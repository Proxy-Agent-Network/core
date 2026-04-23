package com.pan.tactical.hardware

import kotlinx.coroutines.flow.SharedFlow

/**
 * 🛡️ PAN Wingman Hardware Contract (v1.1)
 * Defines the GATT payload structure and event streams expected by the Wingman.
 */

// --- BLE GATT UUIDs ---
// Service: E0000001-0000-1000-8000-00805F9B34FB
// Tap Notify: E0000002...
// LED Write: E0000003...
// Audio Stream: E0000004...
// Status Notify: E0000005...
// HapHat Sync: E0000006...

enum class TapPattern {
    SINGLE, DOUBLE, TRIPLE, LONG_PRESS, HOLD_5S,
    LONG_PLUS_DOUBLE,     // Partner ping
    LONG_PLUS_TRIPLE,     // Quiet Room toggle
    TRIPLE_PLUS_HOLD,     // Silent duress
    LONG_DURING_ONSCENE   // Drop map pin
}

data class WingmanTapEvent(
    val wingmanId: String,
    val agentId: String,
    val tapPattern: TapPattern,
    val timestamp: Long,
    val missionId: String? = null,
    val partnerWingmanId: String? = null
)

enum class LedRingMode(val byte: Byte) {
    OFF(0x00),
    SOLID(0x01),
    BREATHING(0x02),
    PULSE(0x03),
    FLASH(0x04),
    CASCADE_UP(0x05),
    CASCADE_DOWN(0x06),
    DIRECTIONAL_HOLD(0x07),
    RAINBOW_CYCLE(0x08),
    SOS_PATTERN(0x09),
    DIRECTIONAL_SWEEP(0x0A) // 🟢 ADDED THIS LINE for the 7-second firmware macro
}

data class WingmanLedCommand(
    val ledMode: LedRingMode,
    val color: LedColor?, // Reusing the LedColor enum from BleHapHatService
    val durationMs: Short = 0,
    val directionClockPosition: Byte? = null // 0-11 for HapHat sync
)

interface BleWingmanService {
    /** Stream of physical tap gestures from the agent */
    val tapEvents: SharedFlow<WingmanTapEvent>

    suspend fun connect(): Boolean
    suspend fun sendLedCommand(command: WingmanLedCommand): Boolean
    
    // Audio streaming capabilities for Push-to-Talk (to be implemented)
    suspend fun startAudioStream(): Boolean
    suspend fun stopAudioStream(): Boolean

    fun close()
}