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
    val taskId: String = "",
    
    @SerialName("incident_id") 
    val incidentId: String = "",
    
    val lat: Double = 0.0, 
    val lon: Double = 0.0, 
    
    @SerialName("error_code") 
    val errorCode: String = "", 
    
    @SerialName("bounty_usd") 
    val bountyUsd: Double = 0.0, 
    
    val intersection: String = "",
    val role: TaskRole = TaskRole.PRIMARY,
    val status: TaskStatus = TaskStatus.OPEN
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
    val isQualified: Boolean,
    
    @SerialName("is_enabled") 
    val isEnabled: Boolean,       
    
    @SerialName("min_price") 
    val minPrice: Float,
    
    @SerialName("max_price") 
    val maxPrice: Float,
    
    val step: Float,
    
    @SerialName("current_bid") 
    val currentBid: Float,        
    
    @SerialName("is_pinned") 
    val isPinned: Boolean = false 
)