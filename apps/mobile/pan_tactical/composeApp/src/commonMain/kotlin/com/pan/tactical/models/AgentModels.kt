package com.pan.tactical.models

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class AgentCapability(
    val id: String,
    val title: String,
    val description: String,

    @SerialName("required_training")
    val requiredTraining: String?,

    val tier: Int,

    @SerialName("is_qualified")
    val isQualified: Boolean = false
)

data class AgentCapabilityUiModel(
    val capability: AgentCapability,
    val isEnabled: Boolean = false,
    val isPinned: Boolean = false,
    val currentBid: Float = 5.0f,
    val minPrice: Float = 5.0f,
    val maxPrice: Float = 25.0f,
    val step: Float = 1.0f
) {
    // 🛡️ Convenience accessors for cleaner Compose UI code
    val id get() = capability.id
    val title get() = capability.title
    val description get() = capability.description
    val requiredTraining get() = capability.requiredTraining
    val tier get() = capability.tier
    val isQualified get() = capability.isQualified
}

@Serializable
data class AgentProfile(
    @SerialName("agent_id")
    val agentId: String,

    @SerialName("call_sign")
    val callSign: String,

    val tier: Int,

    @SerialName("reputation_score")
    val reputationScore: Float,

    val capabilities: List<AgentCapability> = emptyList()
)