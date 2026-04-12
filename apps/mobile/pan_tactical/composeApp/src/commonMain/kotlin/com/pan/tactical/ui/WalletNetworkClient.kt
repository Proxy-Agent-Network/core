package com.pan.tactical.ui

import com.pan.tactical.models.MissionData

interface WalletNetworkClient {
    // --- Wallet & Profile Operations ---
    suspend fun getWalletData(): WalletResponse?
    suspend fun linkDebitCard(cardNumber: String): Result<String>
    suspend fun withdrawFunds(amount: Double): Result<String>

    // --- Telemetry & Presence ---
    suspend fun updatePresence(isOnline: Boolean): Boolean
    suspend fun updateLocationTelemetry(lat: Double, lon: Double): Boolean
    
    // --- Mission Orchestration ---
    suspend fun fetchActiveMissions(): List<MissionData>
    suspend fun acknowledgeMission(taskId: String): Boolean
    suspend fun completeMission(taskId: String, evidenceUrls: List<String>): Boolean
    
    // 🟢 ADDED: Optional reason parameter for aborts
    suspend fun declineMission(taskId: String, reason: String? = null): Boolean
    
    // --- Developer & Hardware Ops ---
    suspend fun triggerBackendDispatch(lat: Double, lon: Double, errorCode: String): Boolean
    suspend fun registerHardwareKey(agentId: String, publicKeyB64: String, playIntegrityToken: String): Result<String>
}