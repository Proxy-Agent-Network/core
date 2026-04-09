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

    // 🛡️ ACTION ITEM FIXED: Added fleet_id mapping for dynamic feedback routing
    @SerialName("fleet_id")
    val fleetId: String = "Vanguard Network Partner",

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
    @SerialName("extension_minutes")
    val extensionMinutes: Int = 0,

    @SerialName("extension_bounty_usd")
    val extensionBountyUsd: Double = 0.0
)