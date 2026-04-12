package com.pan.tactical.ui

import kotlinx.serialization.Serializable

@Serializable
data class TransactionLog(
    val id: String,
    val date: String,
    // 🟢 FIXED: Changed back to String so the UI can render "$25.00" directly
    val amount: String,
    val description: String,
    // 🟢 FIXED: Restored the missing evidenceUrls field
    val evidenceUrls: List<String>? = null
)

@Serializable
data class WalletResponse(
    val balance: Double,
    val linkedCard: String? = null,
    val history: List<TransactionLog> = emptyList(),
    val missionsCompleted: Int = 0,
    val vanguardTrustScore: Double = 100.0,

    // Agent Tier for dynamic payout multipliers
    // 1 = Public, 2 = Veteran, 3 = First Responder
    val agentTier: Int = 1
)