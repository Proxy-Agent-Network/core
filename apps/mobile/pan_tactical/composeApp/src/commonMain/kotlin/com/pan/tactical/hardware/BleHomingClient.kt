package com.pan.tactical.hardware

data class OobHandshakeResult(
    val success: Boolean,
    val uwbMacAddress: String? = null,
    // Note: secureSessionKey uses reference equality. Use .contentEquals() for value comparison.
    val secureSessionKey: ByteArray? = null,
    val errorMessage: String? = null
)

interface BleHomingClient {
    suspend fun executeOobHandshake(missionId: String): OobHandshakeResult
    fun stopScanning()
    
    fun close()
}