package com.pan.tactical.ui.mission

import com.pan.tactical.getCurrentTimeMs
import com.pan.tactical.models.MissionData
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
    private val apiClient: WalletNetworkClient,
    private val walletClient: WalletNetworkClient,
    private val scope: CoroutineScope
) {
    private val _uiState = MutableStateFlow(MissionUiState())
    val uiState: StateFlow<MissionUiState> = _uiState.asStateFlow()

    private var currentRank: AgentRank? = null
    private var socketJob: Job? = null

    private var agentPayoutMultiplier: Double = 0.80

    // ─── BOOT ─────────────────────────────────────────────────────────────────

    fun initialize() {
        scope.launch {
            val data = walletClient.getWalletData()
            if (data != null) {
                val missions = data.missionsCompleted
                currentRank = rankForMissions(missions)
                agentPayoutMultiplier = 0.90
                _uiState.update { it.copy(missionsCompleted = missions) }
            }

            try {
                val activeMissions = apiClient.fetchActiveMissions()
                if (activeMissions.isNotEmpty()) {
                    val mission = activeMissions.first()

                    val safeLat = if (mission.lat == 0.0) 33.3061 else mission.lat
                    val safeLon = if (mission.lon == 0.0) -111.6601 else mission.lon
                    val safeMission = mission.copy(lat = safeLat, lon = safeLon)

                    _uiState.update {
                        it.copy(
                            isOnline = true,
                            activeMission = safeMission,
                            missionPhase = MissionPhase.ACTIVE,
                            missionAcceptTime = getCurrentTimeMs()
                        )
                    }
                    apiClient.updatePresence(true)
                    startSocketListener()
                }
            } catch (e: Exception) {
                println("[MISSION_VM] Polling error during boot restore: ${e.message}")
            }
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
                println("[MISSION_VM] Telemetry push failed: ${e.message}")
            } finally {
                apiClient.updatePresence(true)
                _uiState.update { it.copy(isOnline = true, isProcessing = false) }
                startSocketListener()
            }
        }
    }

    fun goOffline() {
        _uiState.update { it.copy(isProcessing = true) }
        scope.launch {
            delay(800)
            stopSocketListener()
            try {
                apiClient.updatePresence(false)
            } catch (e: Exception) {
                println("[MISSION_VM] Presence update failed: ${e.message}")
            } finally {
                _uiState.update { it.copy(isOnline = false, isProcessing = false) }
            }
        }
    }

    // ─── MISSION SOCKET STREAM ────────────────────────────────────────────────

    private fun startSocketListener() {
        socketJob?.cancel()
        socketJob = scope.launch {
            try {
                walletClient.listenForMissions(
                    onMissionAssigned = { mission ->
                        if (_uiState.value.missionPhase == MissionPhase.IDLE) {
                            val safeLat = if (mission.lat == 0.0) 33.3061 else mission.lat
                            val safeLon = if (mission.lon == 0.0) -111.6601 else mission.lon
                            val safeMission = mission.copy(lat = safeLat, lon = safeLon)

                            _uiState.update { it.copy(activeMission = safeMission, missionPhase = MissionPhase.PENDING) }
                        }
                    },
                    onMissionCleared = {
                        // 🟢 FIX: Prevent race conditions. Never destroy the mission state if the UI
                        // is currently transitioning, on the final debrief screen, or filling out feedback.
                        val currentPhase = _uiState.value.missionPhase
                        if (currentPhase != MissionPhase.COMPLETED &&
                            currentPhase != MissionPhase.ON_SCENE &&
                            !_uiState.value.showFeedbackScreen) {

                            _uiState.update { it.copy(missionPhase = MissionPhase.IDLE, activeMission = null) }
                        }
                    }
                )
            } catch (e: Exception) {
                println("[MISSION_VM] Socket listener crashed: ${e.message}")
            }
        }
    }

    private fun stopSocketListener() {
        socketJob?.cancel()
        socketJob = null
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
                try {
                    apiClient.acknowledgeMission(taskId)
                } catch (e: Exception) {
                    println("[MISSION_VM] ACK failed for $taskId: ${e.message}")
                }
            }
        }
    }

    fun onMissionDeclined() {
        val taskId = _uiState.value.activeMission?.taskId
        scope.launch {
            if (!taskId.isNullOrBlank()) {
                try {
                    apiClient.declineMission(taskId, null)
                } catch (e: Exception) {
                    println("[MISSION_VM] Decline API call failed for $taskId: ${e.message}")
                }
            }
        }

        _uiState.update {
            it.copy(missionPhase = MissionPhase.IDLE, activeMission = null)
        }
    }

    fun onMissionAborted(reason: String) {
        val taskId = _uiState.value.activeMission?.taskId
            ?: _uiState.value.queuedMission?.taskId

        scope.launch {
            if (!taskId.isNullOrBlank()) {
                try {
                    apiClient.declineMission(taskId, reason)
                } catch (e: Exception) {
                    println("[MISSION_VM] Abort API call failed for $taskId: ${e.message}")
                }
            }
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
    }

    fun onArrivedAtScene() {
        _uiState.update {
            it.copy(
                missionPhase = MissionPhase.ON_SCENE,
                sceneArrivalTime = getCurrentTimeMs()
            )
        }
    }

    fun onMissionSuccess() {
        val state = _uiState.value
        val rawBounty = state.activeMission?.bountyUsd ?: 0.0

        val finalPayout = rawBounty * agentPayoutMultiplier
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
            val updated = walletClient.getWalletData()
            if (updated != null) {
                val newCount = updated.missionsCompleted
                checkForRankUp(newCount)
                _uiState.update { it.copy(missionsCompleted = newCount) }
            }
        }
    }

    fun onMissionFailed() {
        // No-op for Q3 bypass
    }

    // ─── POST-MISSION FLOW ────────────────────────────────────────────────────

    fun onReturnToPatrol() {
        _uiState.update {
            it.copy(
                showFeedbackScreen = true,
                feedbackTaskId = it.activeMission?.taskId ?: "",
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
        stopSocketListener()
    }
}