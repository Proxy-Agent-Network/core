package com.pan.tactical.hardware

/**
 * Platform-agnostic bridge for tactical hardware feedback.
 * - Android: Implements BLE HapHat commands.
 * - iOS: Implements CoreHaptics or silent no-ops.
 * * Note: connect() returns false if hardware is unavailable on this platform.
 * This is not an error; it tells the UI to run in software-only mode.
 */
interface HardwareCommandBridge {
    suspend fun connect(): Boolean
    suspend fun close()

    suspend fun onMissionIncoming()       // Pending alert — purple pulse
    suspend fun onMissionAccepted()       // En route — white → orange
    suspend fun onMissionDeclined()       // Declined or timed out — off
    suspend fun onArrivedAtScene()        // On scene — yellow solid
    suspend fun onBleHandshakeSuccess()   // UWB credentials secured — cyan solid
    suspend fun onBleHandshakeFailed()    // Handshake failed — reserved for future haptic
    suspend fun onMissionSuccess()        // Completed — green strobe
    suspend fun onMissionFailed()         // Submission failed — red strobe
    suspend fun onMissionAborted()        // Mid-mission abort — off
    suspend fun onChainedMission()        // Queued mission loaded — orange solid
}