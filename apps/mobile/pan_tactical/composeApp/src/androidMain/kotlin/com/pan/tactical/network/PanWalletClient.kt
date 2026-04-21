@file:Suppress("INVISIBLE_REFERENCE", "INVISIBLE_MEMBER", "CANNOT_OVERRIDE_INVISIBLE_MEMBER")
package com.pan.tactical.network

import android.util.Log
import com.google.firebase.auth.FirebaseAuth
import com.pan.tactical.BuildConfig
import com.pan.tactical.models.MissionData
import com.pan.tactical.security.StrongBoxManager
import com.pan.tactical.ui.TransactionLog
import com.pan.tactical.ui.WalletNetworkClient
import com.pan.tactical.ui.WalletResponse
import io.ktor.client.*
import io.ktor.client.call.*
import io.ktor.client.engine.okhttp.*
import io.ktor.client.plugins.contentnegotiation.*
import io.ktor.client.plugins.websocket.*
import io.ktor.client.request.*
import io.ktor.client.statement.*
import io.ktor.http.*
import io.ktor.serialization.kotlinx.json.*
import io.ktor.websocket.*
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.withContext
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import kotlinx.serialization.Serializable
import kotlinx.serialization.SerialName
import kotlinx.serialization.json.*
import okhttp3.CertificatePinner // 🛡️ PHASE 4 FIX: Added Pinner Import
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
data class WaitlistPayload(val item_id: String, val email: String)

@Serializable
data class WalletFeedbackPayload(
    val is_positive: Boolean,
    val category: String? = null,
    val label: String? = null,
    val vent_text: String? = null
)

@Serializable
data class WalletTelemetryPayload(val lat: Double, val lon: Double)

@Serializable
data class WalletPresencePayload(
    @SerialName("is_online") val isOnline: Boolean
)

@Serializable
data class WalletDeclinePayload(val reason: String)

@Serializable
data class WalletDistressPayload(
    val vin: String,
    val fault_code: String,
    val latitude: Double,
    val longitude: Double,
    val bounty_usd: Double,
    val timestamp: Int,
    val intersection: String = "Unknown Location"
)

@Serializable
data class WalletMissionCompletePayload(
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
        install(WebSockets) {
            pingInterval = 20_000
        }
        engine {
            config {
                // 🛡️ PHASE 4 FIX: Added Certificate Pinning for financial ledger connections
                val pinner = CertificatePinner.Builder()
                    .add("*.proxyagent.network", "sha256/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=")
                    .build()

                certificatePinner(pinner)
                // 🛑 THE FIX: Increased timeouts to outlast the Google API credential search
                connectTimeout(15, TimeUnit.SECONDS)
                readTimeout(15, TimeUnit.SECONDS)
            }
        }
    }

    private val hostUrl = BuildConfig.PAN_API_BASE_URL
    private val baseUrl = "$hostUrl/api/v1/wallet"

    // 🛡️ PHASE 2 FIX: Real identity enforcement via Firebase Auth
    private val secureUid: String?
        get() = FirebaseAuth.getInstance().currentUser?.uid

    private val jwtMutex = Mutex()
    private var cachedJwt: String? = null
    private var jwtExpiresAt: Long = 0L

    private suspend fun getFreshJwt(): String = jwtMutex.withLock {
        val uid = secureUid ?: throw IllegalStateException("Agent identity missing. Cannot sign JWT.")
        val now = System.currentTimeMillis() / 1000
        if (cachedJwt == null || now >= jwtExpiresAt - 30) {
            cachedJwt = StrongBoxManager().generateJwt(uid)
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
                // 🛑 THE FIX: Removed the explicit /api/v1 prefix to avoid a double-prefix mismatch
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
                    } catch (e: Exception) {
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
                if (!response.status.isSuccess()) return@withContext null

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
                if (response.status.isSuccess()) Result.success("Card linked.")
                else Result.failure(Exception("Failed to link card."))
            } catch (e: Exception) {
                Log.e(TAG, "linkDebitCard failed: ${e.message}", e)
                Result.failure(e)
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
                if (response.status.isSuccess()) Result.success("Withdrawal initiated.")
                else Result.failure(Exception("Withdrawal failed."))
            } catch (e: Exception) {
                Log.e(TAG, "withdrawFunds failed: ${e.message}", e)
                Result.failure(e)
            }
        }
    }

    suspend fun submitMissionFeedback(
        taskId: String,
        isPositive: Boolean,
        category: String,
        label: String,
        ventText: String
    ): Boolean {
        return withContext(Dispatchers.IO) {
            try {
                val response = client.post("$hostUrl/api/v1/agent/missions/$taskId/feedback") {
                    contentType(ContentType.Application.Json)
                    attachAgentSignature()
                    setBody(WalletFeedbackPayload(
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
                val response = client.post("$hostUrl/api/v1/store/waitlist") {
                    contentType(ContentType.Application.Json)
                    attachAgentSignature()
                    setBody(WaitlistPayload(item_id = itemId, email = email))
                }
                response.status.isSuccess()
            } catch (e: Exception) { false }
        }
    }

    suspend fun getTacticalRoute(startLat: Double, startLon: Double, endLat: Double, endLon: Double): List<Pair<Double, Double>> {
        return withContext(Dispatchers.IO) {
            try {
                // 🛡️ PHASE 2 FIX: OSRM Route Engine Hardcode Removed
                val osrmBase = BuildConfig.OSRM_BASE_URL
                val response = client.get("$osrmBase/route/v1/driving/$startLon,$startLat;$endLon,$endLat?overview=full&geometries=geojson")
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
                Log.e(TAG, "Failed to get tactical route: ${e.message}", e)
                emptyList()
            }
        }
    }

    override suspend fun triggerBackendDispatch(lat: Double, lon: Double, errorCode: String, intersection: String): Boolean {
        return withContext(Dispatchers.IO) {
            try {
                val response = client.post("$hostUrl/api/v1/dev/inject-distress") {
                    contentType(ContentType.Application.Json)
                    attachAgentSignature()
                    setBody(WalletDistressPayload(
                        vin = "DEV-VIN-${(Math.random() * 1000).toInt()}",
                        fault_code = errorCode,
                        latitude = lat,
                        longitude = lon,
                        bounty_usd = 50.0,
                        timestamp = (System.currentTimeMillis() / 1000).toInt(),
                        intersection = intersection
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
                    setBody(WalletTelemetryPayload(lat, lon))
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
                    setBody(WalletPresencePayload(isOnline = isOnline))
                }
                response.status.isSuccess()
            } catch (e: Exception) { false }
        }
    }

    override suspend fun fetchActiveMissions(): List<MissionData> {
        return withContext(Dispatchers.IO) {
            try {
                val response = client.get("$hostUrl/api/v1/agent/missions") {
                    attachAgentSignature()
                }
                if (response.status.isSuccess()) response.body<List<MissionData>>()
                else emptyList()
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
                    setBody(WalletDeclinePayload(reason ?: "Agent aborted"))
                }
                response.status.isSuccess()
            } catch (e: Exception) { false }
        }
    }

    override suspend fun completeMission(taskId: String, evidenceUrls: List<String>): Boolean {
        return withContext(Dispatchers.IO) {
            try {
                val uid = secureUid ?: return@withContext false
                val jwt = getFreshJwt() // Fetch once, use twice

                val response = client.post("$hostUrl/api/v1/agent/missions/$taskId/complete") {
                    contentType(ContentType.Application.Json)
                    header("Authorization", "Bearer $jwt")
                    setBody(WalletMissionCompletePayload(
                        agentId = uid,
                        netPayout = 0.0,
                        evidenceUrls = evidenceUrls,
                        hardwareAttestationToken = jwt
                    ))
                }
                response.status.isSuccess()
            } catch (e: Exception) { false }
        }
    }

    override suspend fun listenForMissions(
        onMissionAssigned: (MissionData) -> Unit,
        onMissionCleared: () -> Unit
    ) {
        val wsUrl = hostUrl.replace("https://", "wss://").replace("http://", "ws://")

        while (true) {
            try {
                val jwt = getFreshJwt()
                val uid = secureUid ?: throw IllegalStateException("Agent identity missing")

                client.webSocket(
                    urlString = "$wsUrl/api/v1/agent/stream?agent_id=$uid",
                    request = {
                        header("Authorization", "Bearer $jwt")
                    }
                ) {
                    Log.i(TAG, "🟢 [WEBSOCKET] Connected to real-time dispatch stream.")

                    val activeMissions = fetchActiveMissions()
                    if (activeMissions.isNotEmpty()) {
                        withContext(Dispatchers.Main) { onMissionAssigned(activeMissions.first()) }
                    }

                    for (frame in incoming) {
                        if (frame !is Frame.Text) continue
                        val text = frame.readText()
                        try {
                            val json = Json.parseToJsonElement(text).jsonObject
                            val type = json["type"]?.jsonPrimitive?.content

                            if (type == "NEW_MISSION") {
                                val currentMissions = fetchActiveMissions()
                                if (currentMissions.isNotEmpty()) {
                                    withContext(Dispatchers.Main) { onMissionAssigned(currentMissions.first()) }
                                }
                            } else if (type == "MISSION_CLEARED") {
                                withContext(Dispatchers.Main) { onMissionCleared() }
                            }
                        } catch (e: Exception) {
                            Log.e(TAG, "Error parsing WS frame: ${e.message}")
                        }
                    }
                }
            } catch (e: Exception) {
                Log.w(TAG, "🔴 [WEBSOCKET] Connection dropped. Reconnecting in 3s... (${e.message})")
                delay(3000)
            }
        }
    }

    fun close() = client.close()
}