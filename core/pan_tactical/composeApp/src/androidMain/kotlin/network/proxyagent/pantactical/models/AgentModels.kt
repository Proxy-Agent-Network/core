package network.proxyagent.pantactical.models

import kotlinx.serialization.Serializable

data class MissionData(
    val lat: Double,
    val lon: Double,
    val errorCode: String,
    val bounty: String,
    val intersection: String
)

@Serializable
data class AgentCapability(
    val id: String,
    val title: String,
    val description: String,
    val requiredTraining: String?,
    val tier: Int,
    val isQualified: Boolean,
    var isEnabled: Boolean,
    val minPrice: Float,
    val maxPrice: Float,
    val step: Float,
    var currentBid: Float,
    var isPinned: Boolean = false
)