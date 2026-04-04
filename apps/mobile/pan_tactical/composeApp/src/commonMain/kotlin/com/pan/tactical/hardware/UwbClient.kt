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

// --- INTERFACE ---
interface UwbClient {
    val rangingState: StateFlow<UwbRangingResult>

    suspend fun startRanging(avMacAddress: String, secureSessionKey: ByteArray): Boolean
    
    fun stopRanging()
    
    fun close() 
    
    // TODO (AV Diagnostics): Add WebRTC peer-to-peer initialization. 
    // TODO (Passenger Comms): Add VoIP signaling method.
}