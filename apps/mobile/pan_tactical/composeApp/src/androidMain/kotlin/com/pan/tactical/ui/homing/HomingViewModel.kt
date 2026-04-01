package com.pan.tactical.ui.homing

import android.graphics.Bitmap
import android.util.Log
import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewModelScope
import com.pan.tactical.hardware.BleHomingClient
import com.pan.tactical.hardware.UwbClient
import com.pan.tactical.managers.MissionEventManager
import com.pan.tactical.managers.SentryExtensionRequest
import com.pan.tactical.network.PanApiClient
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import kotlinx.coroutines.sync.Mutex
import java.util.concurrent.atomic.AtomicBoolean

enum class HomingPhase {
    MACRO_GPS, BLE_HANDSHAKE, MICRO_UWB, ON_SCENE, FAILED
}

enum class MissionResult {
    SUCCESS, FAILED
}

data class HomingUiState(
    val phase: HomingPhase = HomingPhase.MACRO_GPS,
    val gpsDistanceMeters: Double? = null,
    val uwbDistanceMeters: Float? = null,
    val uwbAzimuth: Float? = null,
    val errorMessage: String? = null,
    val isResolving: Boolean = false,
    val terminalLogs: List<String> = listOf("Establishing local connection...", "Connection secured."),
    val extensionRequest: SentryExtensionRequest? = null,
    val missionResult: MissionResult? = null
)

class HomingViewModel(
    private val bleClient: BleHomingClient,
    private val uwbClient: UwbClient,
    private val apiClient: PanApiClient
) : ViewModel() {

    companion object {
        private const val MAX_LOG_LINES = 200
    }

    private val _uiState = MutableStateFlow(HomingUiState())
    val uiState: StateFlow<HomingUiState> = _uiState.asStateFlow()

    private var missionId: String = ""
    private var uwbCollectorJob: Job? = null

    private val isHandshakeTriggered = AtomicBoolean(false)
    private val isOnSceneTriggered = AtomicBoolean(false)
    private val submitMutex = Mutex()

    init {
        MissionEventManager.sentryExtensionEvents
            .onEach { request ->
                _uiState.update { it.copy(extensionRequest = request) }
            }
            .launchIn(viewModelScope)
    }

    fun setMission(id: String) {
        // Cancel any in-flight hardware before accepting a new mission
        uwbCollectorJob?.cancel()
        viewModelScope.launch {
            try {
                uwbClient.stopRanging()
            } catch (e: Exception) {
                Log.e("PAN_Homing", "Best effort UWB teardown on mission reassignment failed", e)
            }
        }

        this.missionId = id
        this.isHandshakeTriggered.set(false)
        this.isOnSceneTriggered.set(false)

        // 🛡️ FIXED: Reset UI to clean initial state for the new mission, preventing compliance bypasses
        _uiState.update { HomingUiState() }

        Log.d("PAN_Homing", "Tracking Mission: $id")
    }

    fun appendLog(message: String) {
        _uiState.update {
            it.copy(terminalLogs = (it.terminalLogs + message).takeLast(MAX_LOG_LINES))
        }
    }

    fun uploadAndSubmit(evidenceBitmaps: List<Bitmap>) {
        if (missionId.isEmpty()) {
            appendLog("ERROR: Mission ID not initialized.")
            return
        }

        viewModelScope.launch {
            if (!submitMutex.tryLock()) return@launch

            try {
                _uiState.update { it.copy(
                    isResolving = true,
                    terminalLogs = (it.terminalLogs + "Uploading evidence...").takeLast(MAX_LOG_LINES)
                )}

                val urls = apiClient.uploadEvidenceArray(evidenceBitmaps)
                submitMissionEvidence(urls)
            } catch (e: Exception) {
                _uiState.update { it.copy(
                    isResolving = false,
                    terminalLogs = (it.terminalLogs + "ERROR: Evidence upload failed.").takeLast(MAX_LOG_LINES),
                    missionResult = MissionResult.FAILED
                )}
            } finally {
                submitMutex.unlock()
            }
        }
    }

    private suspend fun submitMissionEvidence(evidenceUrls: List<String>) {
        _uiState.update { it.copy(
            isResolving = true,
            terminalLogs = (it.terminalLogs + "Pinging AV CAN bus...").takeLast(MAX_LOG_LINES)
        )}

        delay(1000)
        _uiState.update { it.copy(
            terminalLogs = (it.terminalLogs + "Evidence package encrypted.").takeLast(MAX_LOG_LINES)
        )}

        delay(500)
        val success = apiClient.completeMission(missionId, evidenceUrls)

        if (success) {
            _uiState.update { it.copy(
                isResolving = false,
                terminalLogs = (it.terminalLogs + "MISSION COMPLETED.").takeLast(MAX_LOG_LINES),
                missionResult = MissionResult.SUCCESS
            ) }
        } else {
            _uiState.update { it.copy(
                isResolving = false,
                terminalLogs = (it.terminalLogs + "UPLOAD FAILED. RETRY REQUIRED.").takeLast(MAX_LOG_LINES),
                missionResult = MissionResult.FAILED
            ) }
        }
    }

    fun clearMissionResult() {
        _uiState.update { it.copy(missionResult = null) }
    }

    fun acceptExtension(taskId: String, minutes: Int, bountyUsd: Double) {
        viewModelScope.launch {
            val success = apiClient.acceptSentryExtension(taskId, minutes, bountyUsd)
            if (success) {
                _uiState.update { it.copy(
                    extensionRequest = null,
                    terminalLogs = (it.terminalLogs + "Extension Accepted: +${minutes}m").takeLast(MAX_LOG_LINES)
                )}
            } else {
                _uiState.update { it.copy(
                    extensionRequest = null,
                    terminalLogs = (it.terminalLogs + "ERROR: Extension agreement failed to sign.").takeLast(MAX_LOG_LINES)
                )}
            }
        }
    }

    fun declineExtension() {
        _uiState.update { it.copy(extensionRequest = null) }
    }

    fun updateGpsProximity(distanceMeters: Double) {
        _uiState.update { it.copy(gpsDistanceMeters = distanceMeters) }

        if (distanceMeters < 50.0 && isHandshakeTriggered.compareAndSet(false, true)) {
            executeHandoffSequence()
        }
    }

    private fun executeHandoffSequence() {
        if (missionId.isEmpty()) {
            _uiState.update { it.copy(
                phase = HomingPhase.FAILED,
                errorMessage = "Asset Initialization Error: No Mission ID"
            )}
            return
        }

        viewModelScope.launch {
            _uiState.update { it.copy(
                phase = HomingPhase.BLE_HANDSHAKE,
                errorMessage = null
            ) }

            try {
                val result = bleClient.executeOobHandshake(missionId)
                if (result.success && result.uwbMacAddress != null && result.secureSessionKey != null) {
                    startUwbRanging(result.uwbMacAddress, result.secureSessionKey)
                } else {
                    _uiState.update { it.copy(phase = HomingPhase.FAILED, errorMessage = "Asset Authentication Failed") }
                }
            } catch (e: Exception) {
                _uiState.update { it.copy(phase = HomingPhase.FAILED, errorMessage = "Handshake Error: ${e.message}") }
            }
        }
    }

    private fun startUwbRanging(macAddress: String, sessionKey: ByteArray) {
        uwbCollectorJob?.cancel()

        _uiState.update { it.copy(phase = HomingPhase.MICRO_UWB) }

        uwbCollectorJob = viewModelScope.launch {
            try {
                uwbClient.startRanging(macAddress, sessionKey)

                uwbClient.rangingState.collect { state ->
                    _uiState.update { it.copy(
                        uwbDistanceMeters = state.distanceMeters,
                        uwbAzimuth = state.azimuthDegrees
                    ) }

                    if (state.isRanging && state.distanceMeters != null && state.distanceMeters < 2.0f) {
                        markOnScene()
                    }
                }
            } catch (e: Exception) {
                Log.e("PAN_Homing", "UWB ranging failed", e)
                _uiState.update { it.copy(
                    phase = HomingPhase.FAILED,
                    errorMessage = "UWB Error: ${e.message}"
                )}
            }
        }
    }

    private fun markOnScene() {
        if (isOnSceneTriggered.compareAndSet(false, true)) {
            Log.i("PAN_Homing", "Agent has arrived at the physical asset.")
            _uiState.update { it.copy(phase = HomingPhase.ON_SCENE) }

            viewModelScope.launch {
                try {
                    uwbClient.stopRanging()
                } catch (e: Exception) {
                    Log.e("PAN_Homing", "Failed to stop UWB ranging", e)
                }
            }
            uwbCollectorJob?.cancel()
        }
    }

    fun forceBleHandshake() {
        val currentPhase = _uiState.value.phase
        if (currentPhase == HomingPhase.MACRO_GPS || currentPhase == HomingPhase.FAILED) {
            isHandshakeTriggered.set(true)
            isOnSceneTriggered.set(false)
            executeHandoffSequence()
        }
    }

    override fun onCleared() {
        super.onCleared()
        uwbCollectorJob?.cancel()
        bleClient.close()
        uwbClient.close()
    }
}

class HomingViewModelFactory(
    private val bleClient: BleHomingClient,
    private val uwbClient: UwbClient,
    private val apiClient: PanApiClient
) : ViewModelProvider.Factory {
    override fun <T : ViewModel> create(modelClass: Class<T>): T {
        if (modelClass.isAssignableFrom(HomingViewModel::class.java)) {
            @Suppress("UNCHECKED_CAST")
            return HomingViewModel(bleClient, uwbClient, apiClient) as T
        }
        throw IllegalArgumentException("Unknown ViewModel class")
    }
}