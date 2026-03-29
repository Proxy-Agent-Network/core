package com.pan.tactical.hardware

import kotlinx.coroutines.flow.StateFlow

// --- STATE MODELS ---
data class UwbRangingResult(
    val isRanging: Boolean = false,
    val distanceMeters: Float? = null,
    val azimuthDegrees: Float? = null,
    val elevationDegrees: Float? = null,
    val vehicleHeadingDegrees: Float? = null 
)

// TODO: BleHapHatService — Add sendHapHatCommand(command: HapHatCommand) to this interface
// data class HapHatCommand(
//     val motorId: Byte,       // FRONT_LEFT, FRONT_RIGHT, BACK_LEFT, BACK_RIGHT, ALL
//     val pulseSpeed: Byte,    // 0-255 maps to 0Hz-10Hz
//     val ledMode: Byte,       // OFF, SOLID, PULSE, STROBE
//     val ledColor: Byte,      // WHITE, CYAN, GREEN, RED, AMBER
//     val durationMs: Int      // 0 = indefinite
// )

// --- INTERFACE ---
interface UwbClient {
    val rangingState: StateFlow<UwbRangingResult>

    suspend fun startRanging(avMacAddress: String, secureSessionKey: ByteArray): Boolean
    
    fun stopRanging()
    
    fun close() 
    
    // TODO (AV Diagnostics): Add WebRTC peer-to-peer initialization. 
    // TODO (Passenger Comms): Add VoIP signaling method.
}