package com.pan.tactical.ui.homing

import android.util.Log
import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewModelScope
import com.pan.tactical.hardware.BleHomingClient
import com.pan.tactical.hardware.UwbClient
import kotlinx.coroutines.Job
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch

// --- STATE MACHINE ---
enum class HomingPhase {
    MACRO_GPS,          // > 50m: Standard Maps/OSRM routing
    BLE_HANDSHAKE,      // < 50m: Initiating Bluetooth GATT
    MICRO_UWB,          // Active Ultra-Wideband ranging
    ON_SCENE,           // < 2m: Agent has arrived
    FAILED              // Hardware/Auth Failure
}

data class HomingUiState(
    val phase: HomingPhase = HomingPhase.MACRO_GPS,
    val gpsDistanceMeters: Double? = null,
    val uwbDistanceMeters: Float? = null,
    val uwbAzimuth: Float? = null,
    val errorMessage: String? = null
)

class HomingViewModel(
    private val bleClient: BleHomingClient,
    private val uwbClient: UwbClient
) : ViewModel() {

    private val _uiState = MutableStateFlow(HomingUiState())
    val uiState: StateFlow<HomingUiState> = _uiState.asStateFlow()

    private var missionId: String = ""
    private var isHandshakeTriggered = false
    
    // Track the collector job to prevent memory leaks
    private var uwbCollectorJob: Job? = null

    init {
        // Observe the UWB hardware stream and push it directly to the UI
        uwbCollectorJob = viewModelScope.launch {
            uwbClient.rangingState
                .filter { it.isRanging }
                .collect { uwbResult ->
                    _uiState.update { it.copy(
                        uwbDistanceMeters = uwbResult.distanceMeters,
                        uwbAzimuth = uwbResult.azimuthDegrees
                    )}
                    
                    // Auto-Arrival Trigger
                    if (uwbResult.distanceMeters != null && uwbResult.distanceMeters < 2.0f) {
                        markOnScene()
                    }
                }
        }
    }

    fun initializeMission(id: String) {
        missionId = id
        _uiState.update { HomingUiState(phase = HomingPhase.MACRO_GPS) }
        isHandshakeTriggered = false
    }

    /**
     * Called by the Location Service when standard GPS updates arrive.
     */
    fun updateGpsDistance(distanceMeters: Double) {
        if (_uiState.value.phase == HomingPhase.MACRO_GPS) {
            _uiState.update { it.copy(gpsDistanceMeters = distanceMeters) }

            // 50 Meters triggers the hardware transition
            if (distanceMeters <= 50.0 && !isHandshakeTriggered) {
                isHandshakeTriggered = true
                executeHandoffSequence()
            }
        }
    }

    /**
     * The core hardware choreography: BLE -> Auth -> UWB
     */
    private fun executeHandoffSequence() {
        viewModelScope.launch {
            _uiState.update { it.copy(phase = HomingPhase.BLE_HANDSHAKE) }
            Log.i("PAN_Homing", "50m Geofence breached. Initiating BLE Handshake...")

            // 1. Execute the Bluetooth Out-Of-Band Handshake
            val oobResult = bleClient.executeOobHandshake(missionId)

            if (oobResult.success && oobResult.uwbMacAddress != null && oobResult.secureSessionKey != null) {
                Log.i("PAN_Homing", "BLE Auth Success. Igniting UWB Engine...")
                
                _uiState.update { it.copy(phase = HomingPhase.MICRO_UWB) }

                // 2. Pass the secure payload directly to the UWB chip
                val uwbStarted = uwbClient.startRanging(
                    avMacAddress = oobResult.uwbMacAddress,
                    secureSessionKey = oobResult.secureSessionKey
                )

                if (!uwbStarted) {
                    _uiState.update { it.copy(
                        phase = HomingPhase.FAILED,
                        errorMessage = "UWB Chip failed to initialize session."
                    )}
                }
            } else {
                Log.e("PAN_Homing", "BLE Handshake Failed: ${oobResult.errorMessage}")
                _uiState.update { it.copy(
                    phase = HomingPhase.FAILED,
                    errorMessage = oobResult.errorMessage ?: "Cryptographic Handshake Failed"
                )}
                
                // Allow the agent to walk closer and try again
                isHandshakeTriggered = false 
            }
        }
    }

    private fun markOnScene() {
        if (_uiState.value.phase != HomingPhase.ON_SCENE) {
            Log.i("PAN_Homing", "Agent has arrived at the physical asset.")
            _uiState.update { it.copy(phase = HomingPhase.ON_SCENE) }
            
            // Clean up hardware to save agent's battery
            uwbClient.stopRanging()
            
            // Kill the collector loop
            uwbCollectorJob?.cancel()
        }
    }

    // 🟢 THE FIX: Allow manual retry from both GPS mode and FAILED mode
    fun forceBleHandshake() {
        val currentPhase = _uiState.value.phase
        if (currentPhase == HomingPhase.MACRO_GPS || currentPhase == HomingPhase.FAILED) {
            isHandshakeTriggered = true
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

// Factory to safely instantiate the ViewModel with its dependencies
class HomingViewModelFactory(
    private val bleClient: BleHomingClient,
    private val uwbClient: UwbClient
) : ViewModelProvider.Factory {
    override fun <T : ViewModel> create(modelClass: Class<T>): T {
        if (modelClass.isAssignableFrom(HomingViewModel::class.java)) {
            @Suppress("UNCHECKED_CAST")
            return HomingViewModel(bleClient, uwbClient) as T
        }
        throw IllegalArgumentException("Unknown ViewModel class")
    }
}