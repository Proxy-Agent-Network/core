package com.pan.tactical.ui.mission

import com.pan.tactical.getCurrentTimeMs
import com.pan.tactical.models.MissionData
import com.pan.tactical.ui.WalletNetworkClient
import com.pan.tactical.ui.components.AgentRank
import com.pan.tactical.ui.components.rankForMissions
import com.pan.tactical.hardware.BleWingmanService
import com.pan.tactical.hardware.HardwareCommandBridge
import com.pan.tactical.hardware.TapPattern
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import kotlin.math.*

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
    private val scope: CoroutineScope,
    // 🟢 NEW: Inject the hardware bridge and Wingman service (defaults to null for safe compilation)
    private val hardwareBridge: HardwareCommandBridge? = null,
    private val wingmanService: BleWingmanService? = null
) {
    private val _uiState = MutableStateFlow(MissionUiState())
    val uiState: StateFlow<MissionUiState> = _uiState.asStateFlow()

    private var currentRank: AgentRank? = null
    private var socketJob: Job? = null
    
    // 🟢 NEW: Wingman Navigation State
    private var directionalTimerJob: Job? = null
    private var currentAgentLat: Double = 0.0
    private var currentAgentLon: Double = 0.0

    // ─── BOOT ─────────────────────────────────────────────────────────────────

    fun initialize() {
        // 🟢 Start listening for physical taps on the Wingman
        observeWingmanGestures()
        
        scope.launch {
            val data = walletClient.getWalletData()
            if (data != null) {
                val missions = data.missionsCompleted
                currentRank = rankForMissions(missions)
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
                    startDirectionalTimer() // Resume compass if recovering state
                }
            } catch (e: Exception) {
                println("[MISSION_VM] Polling error during boot restore: ${e.message}")
            }
        }
    }

    // ─── HARDWARE ORCHESTRATION ───────────────────────────────────────────────

    /**
     * Call this from your SharedLocationManager callback in the UI layer
     * so the ViewModel always knows the agent's live coordinates.
     */
    fun updateAgentLocation(lat: Double, lon: Double) {
        currentAgentLat = lat
        currentAgentLon = lon
    }

    private fun calculateClockPositionToTarget(): Byte {
        val target = _uiState.value.activeMission ?: return 0.toByte()
        
        val lat1 = currentAgentLat * PI / 180.0
        val lon1 = currentAgentLon * PI / 180.0
        val lat2 = target.lat * PI / 180.0
        val lon2 = target.lon * PI / 180.0

        val dLon = lon2 - lon1
        val y = sin(dLon) * cos(lat2)
        val x = cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(dLon)
        
        var brng = atan2(y, x) * 180.0 / PI
        brng = (brng + 360.0) % 360.0
        
        // Map 0-360 degrees to 0-11 clock index (where 0 is 12 o'clock straight ahead)
        val clockIndex = Math.round(brng / 30.0).toInt() % 12
        return clockIndex.toByte()
    }

    private fun startDirectionalTimer() {
        directionalTimerJob?.cancel()
        directionalTimerJob = scope.launch {
            while (true) {
                delay(60_000) // Trigger the 7-second firmware macro every 60 seconds
                val clockPos = calculateClockPositionToTarget()
                hardwareBridge?.onDirectionalTick(clockPos)
            }
        }
    }

    private fun stopDirectionalTimer() {
        directionalTimerJob?.cancel()
        directionalTimerJob = null
    }

    private fun observeWingmanGestures() {
        if (wingmanService == null) return
        scope.launch {
            wingmanService.tapEvents.collect { event ->
                when (event.tapPattern) {
                    TapPattern.DOUBLE -> {
                        // 🟢 MANUAL RE-TRIGGER: If active, fire the 7-second sweep on demand
                        if (_uiState.value.missionPhase == MissionPhase.ACTIVE || 
                            _uiState.value.missionPhase == MissionPhase.ON_SCENE) {
                            
                            val currentBearingClock = calculateClockPositionToTarget()
                            println("[MISSION_VM] Agent double-tapped Wingman. Replaying 7-second sweep for $currentBearingClock o'clock.")
                            
                            hardwareBridge?.onDirectionalTick(currentBearingClock)
                        }
                    }
                    TapPattern.SINGLE -> {
                        println("[MISSION_VM] Voice log stop / Acknowledge gesture detected.")
                        // TODO: Implement voice log stop
                    }
                    TapPattern.LONG_PRESS -> {
                        println("[MISSION_VM] Companion Mode activated.")
                        // TODO: Open voice session
                    }
                    else -> { /* Handle other gestures */ }
                }
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
                            
                            // Fire Purple Incoming Hardware Alert
                            scope.launch { hardwareBridge?.onMissionIncoming() }
                        }
                    },
                    onMissionCleared = {
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
            hardwareBridge?.onMissionAccepted()
            startDirectionalTimer() // 🟢 Begin the 60-second compass sweeps

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
        
        stopDirectionalTimer() // 🟢 Stop compass sweeps
        
        scope.launch {
            hardwareBridge?.onMissionDeclined()
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

        stopDirectionalTimer() // 🟢 Stop compass sweeps
        
        scope.launch {
            hardwareBridge?.onMissionAborted()
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
        
        // 🟢 Note: We do NOT stop the directional timer here.
        // Keeping it running helps the agent locate the exact vehicle in a crowded lot.
        scope.launch { hardwareBridge?.onArrivedAtScene() }
    }

    fun onMissionSuccess() {
        val state = _uiState.value
        val rawBounty = state.activeMission?.bountyUsd ?: 0.0
        val now = getCurrentTimeMs()

        stopDirectionalTimer() // 🟢 Stop compass sweeps

        _uiState.update {
            it.copy(
                missionPhase = MissionPhase.COMPLETED,
                lastPayoutAmount = rawBounty,
                lastTxHash = "tx_$now",
                timeOnSceneMs = if (it.sceneArrivalTime > 0) now - it.sceneArrivalTime else 252000L,
                totalResponseTimeMs = if (it.missionAcceptTime > 0) now - it.missionAcceptTime else 252000L + 300000L
            )
        }

        scope.launch {
            hardwareBridge?.onMissionSuccess()
            
            val updated = walletClient.getWalletData()
            if (updated != null) {
                val newCount = updated.missionsCompleted
                checkForRankUp(newCount)
                _uiState.update { it.copy(missionsCompleted = newCount) }
            }
        }
    }

    fun onMissionFailed() {
        stopDirectionalTimer()
        scope.launch { hardwareBridge?.onMissionFailed() }
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
            startDirectionalTimer() // Resume if chaining missions
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
        stopDirectionalTimer()
    }
}