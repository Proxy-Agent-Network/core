@file:Suppress("INVISIBLE_REFERENCE", "INVISIBLE_MEMBER", "CANNOT_OVERRIDE_INVISIBLE_MEMBER")
package com.pan.tactical.network

import android.util.Log
import com.pan.tactical.security.StrongBoxManager
import com.pan.tactical.ui.TransactionLog
import com.pan.tactical.ui.WalletNetworkClient
import com.pan.tactical.ui.WalletResponse
import io.ktor.client.*
import io.ktor.client.call.*
import io.ktor.client.engine.okhttp.*
import io.ktor.client.plugins.contentnegotiation.*
import io.ktor.client.request.*
import io.ktor.client.statement.*
import io.ktor.http.*
import io.ktor.serialization.kotlinx.json.*
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import kotlinx.serialization.Serializable
import kotlinx.serialization.SerialName
import kotlinx.serialization.json.*
import java.util.concurrent.TimeUnit

// --- NETWORK DTOs ---

@Serializable
data class KeyRegistrationPayload(val agent_id: String, val public_key_b64: String, val play_integrity_token: String)

@Serializable
data class ErrorPayload(val detail: String)

@Serializable
data class LinkCardPayload(val card_number: String)

@Serializable
data class WithdrawPayload(val amount: Double)

@Serializable
data class NetworkTransactionLog(
    val id: String,
    val date: String,
    val amount: String,
    val description: String,
    val evidenceUrls: List<String>? = null
)

@Serializable
data class NetworkWalletResponse(
    @SerialName("balance") val balance: Double = 0.0,
    @SerialName("linkedCard") val linkedCard: String? = null,
    @SerialName("history") val history: List<NetworkTransactionLog> = emptyList(),
    @SerialName("missions_completed") val missionsCompleted: Int = 0,
    @SerialName("vanguard_trust_score") val vanguardTrustScore: Double = 100.0
)

@Serializable
data class FeedbackPayload(
    val is_positive: Boolean,
    val category: String? = null,
    val label: String? = null,
    val vent_text: String? = null
)

@Serializable
data class WaitlistPayload(
    val item_id: String,
    val email: String
)

@Serializable
data class TelemetryPayload(val lat: Double, val lon: Double)

@Serializable
data class PresencePayload(
    @SerialName("is_online") val isOnline: Boolean
)

@Serializable
data class DeclinePayload(val reason: String)

@Serializable
data class DistressPayload(
    val vin: String,
    val fault_code: String,
    val latitude: Double,
    val longitude: Double,
    val bounty_usd: Double,
    val timestamp: Int
)

@Serializable
data class MissionCompletePayload(
    @SerialName("agent_id") val agentId: String,
    @SerialName("net_payout") val netPayout: Double,
    @SerialName("evidence_urls") val evidenceUrls: List<String>,
    @SerialName("hardware_attestation_token") val hardwareAttestationToken: String
)


class PanWalletClient : WalletNetworkClient {

    companion object {
        private const val TAG = "PanWalletClient"
    }

    private val client = HttpClient(OkHttp) {
        install(ContentNegotiation) {
            json(Json { ignoreUnknownKeys = true })
        }
        engine {
            config {
                connectTimeout(3, TimeUnit.SECONDS)
                readTimeout(3, TimeUnit.SECONDS)
            }
        }
    }

    private val hostUrl = "http://192.168.0.84:5001"
    private val baseUrl = "$hostUrl/api/v1/wallet"

    private val secureUid: String
        get() = "VNG-50-PILOT"

    private val jwtMutex = Mutex()
    private var cachedJwt: String? = null
    private var jwtExpiresAt: Long = 0L

    private suspend fun getFreshJwt(): String = jwtMutex.withLock {
        val now = System.currentTimeMillis() / 1000
        if (cachedJwt == null || now >= jwtExpiresAt - 30) {
            cachedJwt = StrongBoxManager().generateJwt(secureUid)
            jwtExpiresAt = now + 300
        }
        return cachedJwt!!
    }

    private suspend fun HttpRequestBuilder.attachAgentSignature() {
        header("Authorization", "Bearer ${getFreshJwt()}")
    }

    override suspend fun registerHardwareKey(agentId: String, publicKeyB64: String, playIntegrityToken: String): Result<String> {
        return withContext(Dispatchers.IO) {
            try {
                val response = client.post("$hostUrl/api/v1/register-key") {
                    contentType(ContentType.Application.Json)
                    setBody(KeyRegistrationPayload(
                        agent_id = agentId,
                        public_key_b64 = publicKeyB64,
                        play_integrity_token = playIntegrityToken
                    ))
                }

                if (response.status.isSuccess()) {
                    Result.success("Hardware bound to identity.")
                } else {
                    val errorDetail = try {
                        response.body<ErrorPayload>().detail
                    } catch(e: Exception) {
                        "Registry rejected key (HTTP ${response.status.value})"
                    }
                    Log.w(TAG, "Key Ceremony rejected: $errorDetail")
                    Result.failure(Exception(errorDetail))
                }
            } catch (e: Exception) {
                Log.e(TAG, "Key Ceremony failed: ${e.message}", e)
                Result.failure(Exception("Network connection lost during Key Ceremony."))
            }
        }
    }

    override suspend fun getWalletData(): WalletResponse? {
        return withContext(Dispatchers.IO) {
            try {
                val response = client.get("$baseUrl/") {
                    attachAgentSignature()
                }

                if (!response.status.isSuccess()) {
                    return@withContext null
                }

                val data = response.body<NetworkWalletResponse>()

                WalletResponse(
                    balance = data.balance,
                    linkedCard = data.linkedCard,
                    history = data.history.map {
                        TransactionLog(
                            id = it.id,
                            date = it.date,
                            amount = it.amount,
                            description = it.description,
                            evidenceUrls = it.evidenceUrls
                        )
                    },
                    missionsCompleted = data.missionsCompleted,
                    vanguardTrustScore = data.vanguardTrustScore
                )
            } catch (e: Exception) {
                Log.e(TAG, "getWalletData failed: ${e.message}", e)
                null
            }
        }
    }

    override suspend fun linkDebitCard(cardNumber: String): Result<String> {
        return withContext(Dispatchers.IO) {
            try {
                val response = client.post("$baseUrl/link-card") {
                    contentType(ContentType.Application.Json)
                    attachAgentSignature()
                    setBody(LinkCardPayload(card_number = cardNumber))
                }

                if (response.status.isSuccess()) {
                    Result.success("Card linked successfully.")
                } else {
                    Result.failure(Exception("Network rejected card linking"))
                }
            } catch (e: Exception) {
                Result.failure(Exception("Connection to PAN Network lost."))
            }
        }
    }

    override suspend fun withdrawFunds(amount: Double): Result<String> {
        return withContext(Dispatchers.IO) {
            try {
                val response = client.post("$baseUrl/withdraw") {
                    contentType(ContentType.Application.Json)
                    attachAgentSignature()
                    setBody(WithdrawPayload(amount = amount))
                }

                if (response.status.isSuccess()) {
                    Result.success("Transfer initiated.")
                } else {
                    Result.failure(Exception("Withdrawal rejected"))
                }
            } catch (e: Exception) {
                Result.failure(Exception("Connection to PAN Network lost."))
            }
        }
    }

    suspend fun submitMissionFeedback(taskId: String, isPositive: Boolean, category: String, label: String, ventText: String): Boolean {
        return withContext(Dispatchers.IO) {
            try {
                val targetUrl = "$hostUrl/api/v1/agent/missions/$taskId/feedback"
                val response = client.post(targetUrl) {
                    contentType(ContentType.Application.Json)
                    attachAgentSignature()
                    setBody(FeedbackPayload(
                        is_positive = isPositive,
                        category = category.ifBlank { null },
                        label = label.ifBlank { null },
                        vent_text = ventText.ifBlank { null }
                    ))
                }
                response.status.isSuccess()
            } catch (e: Exception) { false }
        }
    }

    suspend fun joinWaitlist(itemId: String, email: String): Boolean {
        return withContext(Dispatchers.IO) {
            try {
                val targetUrl = "$hostUrl/api/v1/store/waitlist"
                val response = client.post(targetUrl) {
                    contentType(ContentType.Application.Json)
                    attachAgentSignature()
                    setBody(WaitlistPayload(
                        item_id = itemId,
                        email = email
                    ))
                }
                response.status.isSuccess()
            } catch (e: Exception) { false }
        }
    }

    // 🟢 NEW: Safely fetches the turn-by-turn road polyline from OSRM
    suspend fun getTacticalRoute(startLat: Double, startLon: Double, endLat: Double, endLon: Double): List<Pair<Double, Double>> {
        return withContext(Dispatchers.IO) {
            try {
                val response = client.get("https://router.project-osrm.org/route/v1/driving/$startLon,$startLat;$endLon,$endLat?overview=full&geometries=geojson")
                val jsonString = response.bodyAsText()
                val element = Json.parseToJsonElement(jsonString)
                val routes = element.jsonObject["routes"]?.jsonArray
                if (routes != null && routes.isNotEmpty()) {
                    val geometry = routes[0].jsonObject["geometry"]?.jsonObject
                    val coordinates = geometry?.get("coordinates")?.jsonArray
                    if (coordinates != null) {
                        return@withContext coordinates.map {
                            val point = it.jsonArray
                            Pair(point[1].jsonPrimitive.double, point[0].jsonPrimitive.double)
                        }
                    }
                }
                emptyList()
            } catch (e: Exception) {
                Log.e(TAG, "Failed to get tactical route", e)
                emptyList()
            }
        }
    }

    override suspend fun triggerBackendDispatch(lat: Double, lon: Double, errorCode: String): Boolean {
        return withContext(Dispatchers.IO) {
            try {
                val response = client.post("$hostUrl/api/v1/v2x/distress") {
                    contentType(ContentType.Application.Json)
                    header("X-Fleet-Id", "DEV-FLEET-01")
                    header("Authorization", "Bearer sk_test_mock_waymo_token_123")
                    setBody(DistressPayload(
                        vin = "DEV-VIN-${(Math.random() * 1000).toInt()}",
                        fault_code = errorCode,
                        latitude = lat,
                        longitude = lon,
                        bounty_usd = 50.0,
                        timestamp = (System.currentTimeMillis() / 1000).toInt()
                    ))
                }
                response.status.isSuccess()
            } catch (e: Exception) { false }
        }
    }

    override suspend fun updateLocationTelemetry(lat: Double, lon: Double): Boolean {
        return withContext(Dispatchers.IO) {
            try {
                val response = client.post("$hostUrl/api/v1/telemetry/ingest") {
                    contentType(ContentType.Application.Json)
                    attachAgentSignature()
                    setBody(TelemetryPayload(lat, lon))
                }
                response.status.isSuccess()
            } catch (e: Exception) { false }
        }
    }

    override suspend fun updatePresence(isOnline: Boolean): Boolean {
        return withContext(Dispatchers.IO) {
            try {
                val response = client.post("$hostUrl/api/v1/agent/presence") {
                    contentType(ContentType.Application.Json)
                    attachAgentSignature()
                    setBody(PresencePayload(isOnline = isOnline))
                }
                response.status.isSuccess()
            } catch (e: Exception) { false }
        }
    }

    override suspend fun fetchActiveMissions(): List<com.pan.tactical.models.MissionData> {
        return withContext(Dispatchers.IO) {
            try {
                val response = client.get("$hostUrl/api/v1/agent/missions") {
                    attachAgentSignature()
                }
                if (response.status.isSuccess()) {
                    response.body<List<com.pan.tactical.models.MissionData>>()
                } else emptyList()
            } catch (e: Exception) { emptyList() }
        }
    }

    override suspend fun acknowledgeMission(taskId: String): Boolean {
        return withContext(Dispatchers.IO) {
            try {
                val response = client.post("$hostUrl/api/v1/agent/missions/$taskId/ack") {
                    attachAgentSignature()
                }
                response.status.isSuccess()
            } catch (e: Exception) { false }
        }
    }

    override suspend fun declineMission(taskId: String, reason: String?): Boolean {
        return withContext(Dispatchers.IO) {
            try {
                val response = client.post("$hostUrl/api/v1/agent/missions/$taskId/decline") {
                    contentType(ContentType.Application.Json)
                    attachAgentSignature()
                    setBody(DeclinePayload(reason ?: "Agent aborted"))
                }
                response.status.isSuccess()
            } catch (e: Exception) { false }
        }
    }

    override suspend fun completeMission(taskId: String, evidenceUrls: List<String>): Boolean {
        return withContext(Dispatchers.IO) {
            try {
                val jwt = getFreshJwt()
                val safeToken = if (jwt.length < 100) jwt.padEnd(105, 'x') else jwt

                val response = client.post("$hostUrl/api/v1/agent/missions/$taskId/complete") {
                    contentType(ContentType.Application.Json)
                    attachAgentSignature()
                    setBody(
                        MissionCompletePayload(
                            agentId = secureUid,
                            netPayout = 0.0,
                            evidenceUrls = evidenceUrls,
                            hardwareAttestationToken = safeToken
                        )
                    )
                }
                response.status.isSuccess()
            } catch (e: Exception) { false }
        }
    }

    fun close() = client.close()
}