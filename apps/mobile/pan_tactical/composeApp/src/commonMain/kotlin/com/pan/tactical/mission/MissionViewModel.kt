package com.pan.tactical.ui.mission

import com.pan.tactical.getCurrentTimeMs
import com.pan.tactical.hardware.HardwareCommandBridge
import com.pan.tactical.models.MissionData
import com.pan.tactical.network.PanApiClient
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

// 🛡️ WARNING 2 FIXED: Upgraded from String literals to a strict enum for type safety
enum class MissionPhase {
    IDLE, PENDING, ACTIVE, ON_SCENE, COMPLETED
}

/**
 * All UI-visible state owned by the Business State Machine.
 * The Compose layer observes this as a single StateFlow and renders accordingly.
 * HomingViewModel state is observed separately by the UI — never merged here.
 */
data class MissionUiState(
    // --- Mission State Machine ---
    val missionPhase: MissionPhase = MissionPhase.IDLE,
    val activeMission: MissionData? = null,
    val queuedMission: MissionData? = null,

    // --- Patrol ---
    val isOnline: Boolean = false,
    val isProcessing: Boolean = false,       // Network in-flight guard

    // --- Financial Settlement ---
    val lastPayoutAmount: Double = 0.0,
    val lastTxHash: String = "",
    val timeOnSceneMs: Long = 0L,
    val totalResponseTimeMs: Long = 0L,

    // --- Rank Progression ---
    val missionsCompleted: Int = 0,
    val showRankUp: Boolean = false,
    val rankUpTo: AgentRank = AgentRank.RECRUIT,

    // --- Post-Mission Flow ---
    val showFeedbackScreen: Boolean = false,
    val feedbackTaskId: String = "",
    val feedbackFleetId: String = "",

    // --- Timing (internal business logic, exposed for HomingViewModel coordination) ---
    val missionAcceptTime: Long = 0L,
    val sceneArrivalTime: Long = 0L,
)

// ─── VIEW MODEL ──────────────────────────────────────────────────────────────

/**
 * MissionViewModel — Business State Machine
 *
 * Owns: API polling, wallet sync, payout calculation, rank progression,
 * hardware event dispatch, mission accept/decline/abort/complete lifecycle.
 *
 * Does NOT own: UWB ranging, BLE handshake, GPS proximity, biometric attestation UI.
 * Those belong to HomingViewModel. The Compose UI coordinates between both.
 *
 * Constructor injection keeps this class in commonMain with zero platform imports.
 */
class MissionViewModel(
    private val apiClient: PanApiClient,
    private val walletClient: WalletNetworkClient,
    private val hardwareBridge: HardwareCommandBridge,
    // 🛡️ BUG 1 FIXED: Removed unused biometricHelper dependency
    private val scope: CoroutineScope
) {
    private val _uiState = MutableStateFlow(MissionUiState())
    val uiState: StateFlow<MissionUiState> = _uiState.asStateFlow()

    // Tracks the current rank so we can detect threshold crossings
    private var currentRank: AgentRank? = null

    // Holds the active polling job so it can be cancelled on going offline
    private var pollingJob: Job? = null

    // ─── BOOT ─────────────────────────────────────────────────────────────────

    /**
     * Call once on app boot to initialize missionsCompleted without triggering
     * a rank-up overlay. Sets the baseline so the first real mission completion
     * produces the correct delta.
     */
    fun initialize() {
        scope.launch {
            val data = walletClient.getWalletData() ?: return@launch
            val missions = data.missionsCompleted
            // Set currentRank silently — no rank-up event on boot
            currentRank = rankForMissions(missions)
            _uiState.update { it.copy(missionsCompleted = missions) }
        }
    }

    // ─── ONLINE / OFFLINE ─────────────────────────────────────────────────────

    fun goOnline(agentLat: Double, agentLon: Double) {
        _uiState.update { it.copy(isProcessing = true) }
        scope.launch {
            try {
                delay(800) // Deliberate UI feedback delay (matches prior dashboard)
                apiClient.updateLocationTelemetry(agentLat, agentLon)
            } catch (e: Exception) {
                println("[MISSION_VM] Telemetry push failed on go-online: ${e.message}")
            } finally {
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

            // TODO: Inform the backend the agent has dropped off the network
            // so the dispatch matching engine removes them from the eligible pool.
            // try { apiClient.updatePresence(isOnline = false) } catch (e: Exception) { ... }

            _uiState.update { it.copy(isOnline = false, isProcessing = false) }
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

    /**
     * Called when the agent taps ACCEPT on the MissionAlertOverlay.
     * Hardware command has a 500ms internal delay — must fire in a separate launch.
     */
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

        // Launched separately — onMissionAccepted contains a 500ms hardware delay
        scope.launch { hardwareBridge.onMissionAccepted() }
    }

    /**
     * Called when agent taps DECLINE or when the 10s countdown expires.
     */
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
        // Re-start polling if still online
        if (_uiState.value.isOnline) startPolling()
    }

    /**
     * Called when agent confirms abort via the reason dialog.
     */
    fun onMissionAborted(reason: String) {
        val taskId = _uiState.value.activeMission?.taskId
            ?: _uiState.value.queuedMission?.taskId

        scope.launch {
            if (!taskId.isNullOrBlank()) {
                // 🛡️ BUG 2 FIXED: Documented missing parameter mapping for fleet analytics
                // TODO: Pass reason to backend when declineMission API supports abort_reason field
                try { apiClient.declineMission(taskId) } catch (e: Exception) {
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

    /**
     * Called when the agent taps ARRIVED AT SCENE.
     * Transitions ACTIVE → ON_SCENE and starts the scene timer.
     */
    fun onArrivedAtScene() {
        _uiState.update {
            it.copy(
                missionPhase = MissionPhase.ON_SCENE,
                sceneArrivalTime = getCurrentTimeMs()
            )
        }
        scope.launch { hardwareBridge.onArrivedAtScene() }
    }

    /**
     * Called by HomingViewModel / the UI when evidence submission succeeds.
     * Triggers financial settlement read, rank check, and feedback flow.
     */
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
            // Sync fresh wallet data — backend has already incremented missions_completed
            val updated = walletClient.getWalletData()
            if (updated != null) {
                val newCount = updated.missionsCompleted
                checkForRankUp(newCount)
                _uiState.update { it.copy(missionsCompleted = newCount) }
            }
        }
    }

    /**
     * Called by HomingViewModel / the UI when evidence submission fails.
     */
    fun onMissionFailed() {
        scope.launch { hardwareBridge.onMissionFailed() }
        // Stay in ON_SCENE so the agent can retry submission
    }

    // ─── POST-MISSION FLOW ────────────────────────────────────────────────────

    /**
     * Called when the agent taps RETURN TO PATROL on the completion screen.
     * Opens the feedback overlay. Reset happens after feedback is dismissed.
     */
    fun onReturnToPatrol() {
        // 🛡️ WARNING 1 FIXED: Removed unused state capture
        _uiState.update {
            it.copy(
                showFeedbackScreen = true,
                feedbackTaskId = it.activeMission?.taskId ?: "",
                // TODO: Replace with activeMission.fleetId when field is added to MissionData
                feedbackFleetId = "Vanguard Network Partner"
            )
        }
    }

    /**
     * Called when the feedback screen is dismissed (after submit or skip).
     * Handles chained mission logic.
     */
    fun onFeedbackDismissed() {
        val state = _uiState.value

        if (state.queuedMission != null) {
            // Chain to queued mission
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
            // Return to patrol
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

    // ─── CLEANUP ──────────────────────────────────────────────────────────────

    /**
     * Call from the platform's onDispose / onCleared equivalent.
     */
    fun close() {
        stopPolling()
        scope.launch { hardwareBridge.close() }
    }
}