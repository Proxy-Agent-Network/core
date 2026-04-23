package com.pan.tactical.hardware

/**
 * Platform-agnostic bridge for tactical hardware feedback.
 * - Orchestrates both HapHat and Wingman peripherals.
 * - iOS: Implements CoreHaptics or silent no-ops.
 * * Note: connect() returns false if hardware is unavailable on this platform.
 * This is not an error; it tells the UI to run in software-only mode.
 */
interface HardwareCommandBridge {
    suspend fun connect(): Boolean
    suspend fun close()

    // ─── MISSION LIFECYCLE ─────────────────────────────────────────
    suspend fun onMissionIncoming()       // Purple pulse (Hat & Wingman)
    suspend fun onMissionAccepted()       // En route (Orange sweep)
    suspend fun onMissionDeclined()       // Off
    suspend fun onArrivedAtScene()        // Yellow solid
    suspend fun onMissionSuccess()        // Green strobe / Cascade Up
    suspend fun onMissionFailed()         // Red strobe
    suspend fun onMissionAborted()        // Off
    suspend fun onChainedMission()        // Orange solid
    
    // ─── NETWORK & SENSORS ─────────────────────────────────────────
    suspend fun onBleHandshakeSuccess()   // UWB credentials secured — cyan solid
    suspend fun onBleHandshakeFailed()    // Handshake failed

    // ─── NAVIGATION (HapHat & Wingman Sync) ────────────────────────
    /** * Fires the synchronized 60-second directional pulse.
     * Hat vibrates the forehead; Wingman lights the corresponding clock position.
     * @param clockPosition 0-11 representing the bearing to target.
     */
    suspend fun onDirectionalTick(clockPosition: Byte)
}