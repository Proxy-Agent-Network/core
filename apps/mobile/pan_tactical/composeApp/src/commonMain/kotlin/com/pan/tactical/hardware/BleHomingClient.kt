package com.pan.tactical.hardware

data class OobHandshakeResult(
    val success: Boolean,
    val uwbMacAddress: String? = null,
    val secureSessionKey: ByteArray? = null,
    val errorMessage: String? = null
)

interface BleHomingClient {
    suspend fun executeOobHandshake(missionId: String): OobHandshakeResult
    fun stopScanning()
    
    // 🟢 THE FIX: Required for GATT connection and BLE adapter cleanup
    fun close()
}