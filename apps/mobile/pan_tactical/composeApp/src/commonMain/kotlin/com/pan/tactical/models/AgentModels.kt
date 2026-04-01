package com.pan.tactical.models

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
enum class TaskRole {
    PRIMARY,
    SENTRY
}

@Serializable
enum class TaskStatus {
    OPEN,
    QUEUED,
    ASSIGNED,
    ACTIVE,
    PENDING_VERIFICATION,
    SETTLED,
    CANCELLED
}

@Serializable
data class MissionData(
    @SerialName("task_id")
    val taskId: String,

    @SerialName("incident_id")
    val incidentId: String,

    val lat: Double,
    val lon: Double,

    @SerialName("error_code")
    val errorCode: String? = null,

    @SerialName("bounty_usd")
    val bountyUsd: Double,

    val intersection: String,

    val role: TaskRole = TaskRole.PRIMARY,
    val status: TaskStatus = TaskStatus.OPEN,

    // Phase 5: Security & Compliance
    @SerialName("requires_attestation")
    val requiresAttestation: Boolean = false,

    // 🛡️ Phase 5: Sentry Extension Logic
    // Defaults to 0 (not null) to prevent phantom offer display on incorrect null checks
    @SerialName("extension_minutes")
    val extensionMinutes: Int = 0,

    @SerialName("extension_bounty_usd")
    val extensionBountyUsd: Double = 0.0
)

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