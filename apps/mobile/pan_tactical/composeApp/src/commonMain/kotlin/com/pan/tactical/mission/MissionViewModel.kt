package com.pan.tactical.ui.mission

import com.pan.tactical.getCurrentTimeMs
import com.pan.tactical.hardware.HardwareCommandBridge
import com.pan.tactical.models.MissionData
// 🛡️ FIX: Removed the illegal import. commonMain cannot import androidMain classes.
import com.pan.tactical.ui.WalletNetworkClient
import com.pan.tactical.ui.components.AgentRank
import com.pan.tactical.ui.components.rankForMissions
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

// ─── STATE ───────────────────────────────────────────────────────────────────

enum class MissionPhase {
    IDLE, PENDING, ACTIVE, ON_SCENE, COMPLETED
}

data class MissionUiState(
    val missionPhase: MissionPhase = MissionPhase.IDLE,
    val activeMission: MissionData? = null,
    val queuedMission: MissionData? = null,
    val isOnline: Boolean = false,
    val isProcessing: Boolean = false,
    val lastPayoutAmount: Double = 0.0,
    val lastTxHash: String = "",
    val timeOnSceneMs: Long = 0L,
    val totalResponseTimeMs: Long = 0L,
    val missionsCompleted: Int = 0,
    val showRankUp: Boolean = false,
    val rankUpTo: AgentRank = AgentRank.RECRUIT,
    val showFeedbackScreen: Boolean = false,
    val feedbackTaskId: String = "",
    val feedbackFleetId: String = "",
    val missionAcceptTime: Long = 0L,
    val sceneArrivalTime: Long = 0L,
)

// ─── VIEW MODEL ──────────────────────────────────────────────────────────────

class MissionViewModel(
    // 🛡️ FIX: Program to the shared interface, not the concrete Android implementation.
    private val apiClient: WalletNetworkClient,
    private val walletClient: WalletNetworkClient,
    private val hardwareBridge: HardwareCommandBridge,
    private val scope: CoroutineScope
) {
    private val _uiState = MutableStateFlow(MissionUiState())
    val uiState: StateFlow<MissionUiState> = _uiState.asStateFlow()

    private var currentRank: AgentRank? = null
    private var pollingJob: Job? = null

    // ─── BOOT ─────────────────────────────────────────────────────────────────

    fun initialize() {
        scope.launch {
            val data = walletClient.getWalletData() ?: return@launch
            val missions = data.missionsCompleted
            currentRank = rankForMissions(missions)
            _uiState.update { it.copy(missionsCompleted = missions) }
        }
    }

    // ─── ONLINE / OFFLINE ─────────────────────────────────────────────────────

    fun goOnline(agentLat: Double, agentLon: Double) {
        _uiState.update { it.copy(isProcessing = true) }
        scope.launch {
            try {
                delay(800)
                apiClient.updateLocationTelemetry(agentLat, agentLon)
            } catch (e: Exception) {
                println("[MISSION_VM] Telemetry push failed on go-online: ${e.message}")
            } finally {
                // Note: Ensure updatePresence() is declared in the WalletNetworkClient interface
                // in commonMain, otherwise you will get an unresolved reference error here.
                apiClient.updatePresence(true)
                _uiState.update { it.copy(isOnline = true, isProcessing = false) }
                startPolling()
            }
        }
    }

    fun goOffline() {
        _uiState.update { it.copy(isProcessing = true) }
        scope.launch {
            delay(800)
            stopPolling()
            try {
                apiClient.updatePresence(false)
            } catch (e: Exception) {
                println("[MISSION_VM] Presence update failed on go-offline: ${e.message}")
            } finally {
                _uiState.update { it.copy(isOnline = false, isProcessing = false) }
            }
        }
    }

    // ─── MISSION POLLING ──────────────────────────────────────────────────────

    private fun startPolling() {
        pollingJob?.cancel()
        pollingJob = scope.launch {
            while (_uiState.value.isOnline && _uiState.value.missionPhase == MissionPhase.IDLE) {
                try {
                    val incoming = apiClient.fetchActiveMissions()
                    if (incoming.isNotEmpty()) {
                        val mission = incoming.first()
                        _uiState.update { it.copy(activeMission = mission, missionPhase = MissionPhase.PENDING) }
                        launch { hardwareBridge.onMissionIncoming() }
                        break
                    }
                } catch (e: Exception) {
                    println("[MISSION_VM] Polling error: ${e.message}")
                }
                delay(3000)
            }
        }
    }

    private fun stopPolling() {
        pollingJob?.cancel()
        pollingJob = null
    }

    // ─── MISSION LIFECYCLE EVENTS ─────────────────────────────────────────────

    fun onMissionAccepted() {
        val mission = _uiState.value.activeMission ?: return
        val taskId = mission.taskId

        _uiState.update {
            it.copy(
                missionPhase = MissionPhase.ACTIVE,
                missionAcceptTime = getCurrentTimeMs()
            )
        }

        scope.launch {
            if (taskId.isNotBlank()) {
                try { apiClient.acknowledgeMission(taskId) } catch (e: Exception) {
                    println("[MISSION_VM] ACK failed for $taskId: ${e.message}")
                }
            }
        }

        scope.launch { hardwareBridge.onMissionAccepted() }
    }

    fun onMissionDeclined() {
        val taskId = _uiState.value.activeMission?.taskId
        scope.launch {
            if (!taskId.isNullOrBlank()) {
                try { apiClient.declineMission(taskId) } catch (e: Exception) {
                    println("[MISSION_VM] Decline API call failed: ${e.message}")
                }
            }
            hardwareBridge.onMissionDeclined()
        }

        _uiState.update {
            it.copy(missionPhase = MissionPhase.IDLE, activeMission = null)
        }
        if (_uiState.value.isOnline) startPolling()
    }

    fun onMissionAborted(reason: String) {
        val taskId = _uiState.value.activeMission?.taskId
            ?: _uiState.value.queuedMission?.taskId

        scope.launch {
            if (!taskId.isNullOrBlank()) {
                try { apiClient.declineMission(taskId, reason) } catch (e: Exception) {
                    println("[MISSION_VM] Abort API call failed: ${e.message}")
                }
            }
            hardwareBridge.onMissionAborted()
        }

        _uiState.update {
            it.copy(
                missionPhase = MissionPhase.IDLE,
                activeMission = null,
                queuedMission = null,
                missionAcceptTime = 0L,
                sceneArrivalTime = 0L
            )
        }
        if (_uiState.value.isOnline) startPolling()
    }

    fun onArrivedAtScene() {
        _uiState.update {
            it.copy(
                missionPhase = MissionPhase.ON_SCENE,
                sceneArrivalTime = getCurrentTimeMs()
            )
        }
        scope.launch { hardwareBridge.onArrivedAtScene() }
    }

    fun onMissionSuccess() {
        val state = _uiState.value
        val rawBounty = state.activeMission?.bountyUsd ?: 0.0
        val finalPayout = rawBounty * 0.90
        val now = getCurrentTimeMs()

        _uiState.update {
            it.copy(
                missionPhase = MissionPhase.COMPLETED,
                lastPayoutAmount = finalPayout,
                lastTxHash = "tx_$now",
                timeOnSceneMs = if (it.sceneArrivalTime > 0) now - it.sceneArrivalTime else 252000L,
                totalResponseTimeMs = if (it.missionAcceptTime > 0) now - it.missionAcceptTime else 252000L + 300000L
            )
        }

        scope.launch {
            hardwareBridge.onMissionSuccess()
            val updated = walletClient.getWalletData()
            if (updated != null) {
                val newCount = updated.missionsCompleted
                checkForRankUp(newCount)
                _uiState.update { it.copy(missionsCompleted = newCount) }
            }
        }
    }

    fun onMissionFailed() {
        scope.launch { hardwareBridge.onMissionFailed() }
    }

    // ─── POST-MISSION FLOW ────────────────────────────────────────────────────

    fun onReturnToPatrol() {
        _uiState.update {
            it.copy(
                showFeedbackScreen = true,
                feedbackTaskId = it.activeMission?.taskId ?: "",
                // 🛡️ ACTION ITEM FIXED: Replaced hardcoded string with dynamic fleetId
                feedbackFleetId = it.activeMission?.fleetId ?: "Vanguard Network Partner"
            )
        }
    }

    fun onFeedbackDismissed() {
        val state = _uiState.value

        if (state.queuedMission != null) {
            _uiState.update {
                it.copy(
                    showFeedbackScreen = false,
                    missionPhase = MissionPhase.ACTIVE,
                    activeMission = it.queuedMission,
                    queuedMission = null,
                    lastPayoutAmount = 0.0,
                    timeOnSceneMs = 0L,
                    totalResponseTimeMs = 0L,
                    lastTxHash = "",
                    missionAcceptTime = getCurrentTimeMs(),
                    sceneArrivalTime = 0L
                )
            }
            scope.launch { hardwareBridge.onChainedMission() }
        } else {
            _uiState.update {
                it.copy(
                    showFeedbackScreen = false,
                    missionPhase = MissionPhase.IDLE,
                    activeMission = null,
                    lastPayoutAmount = 0.0,
                    timeOnSceneMs = 0L,
                    totalResponseTimeMs = 0L,
                    lastTxHash = "",
                    missionAcceptTime = 0L,
                    sceneArrivalTime = 0L
                )
            }
            if (_uiState.value.isOnline) startPolling()
        }
    }

    // ─── RANK PROGRESSION ─────────────────────────────────────────────────────

    private fun checkForRankUp(newCount: Int) {
        val newRank = rankForMissions(newCount)
        val previous = currentRank
        if (previous != null && newRank > previous) {
            _uiState.update { it.copy(showRankUp = true, rankUpTo = newRank) }
        }
        currentRank = newRank
    }

    fun onRankUpDismissed() {
        _uiState.update { it.copy(showRankUp = false) }
    }

    fun close() {
        stopPolling()
        scope.launch { hardwareBridge.close() }
    }
}