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

    @SerialName("fleet_id")
    val fleetId: String = "Vanguard Network Partner",

    val lat: Double,
    val lon: Double,

    @SerialName("fault_code")
    val errorCode: String? = null,

    @SerialName("bounty_usd")
    val bountyUsd: Double,

    // 🟢 THE FIX: Parsing the backend's explicit net payout math!
    @SerialName("net_payout")
    val netPayout: Double = 0.0,

    val intersection: String = "Target Location",

    val role: TaskRole = TaskRole.PRIMARY,
    val status: TaskStatus = TaskStatus.OPEN,

    @SerialName("requires_attestation")
    val requiresAttestation: Boolean = false,

    @SerialName("extension_minutes")
    val extensionMinutes: Int = 0,

    @SerialName("extension_bounty_usd")
    val extensionBountyUsd: Double = 0.0,

    val diagnostic: String? = null
)