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
import kotlinx.serialization.json.Json
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

// 🛡️ GAP 1 FIXED: Explicit SerialName mapping to protect against Python snake_case
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
    val category: String,
    val label: String,
    val vent_text: String
)

@Serializable
data class WaitlistPayload(
    val item_id: String,
    val email: String
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

    // 🟢 PILOT BYPASS: Hardcode hostUrl to the PC's local IP Address
    // private val hostUrl = BuildConfig.PAN_API_BASE_URL
    private val hostUrl = "http://192.168.0.84:5001"
    private val baseUrl = "$hostUrl/api/v1/wallet"

    private val secureUid: String
        get() = "VNG-50-PILOT"
    //get() = FirebaseAuth.getInstance().currentUser?.uid
    //    ?: throw IllegalStateException("Agent identity missing. Cannot execute network operations.")

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
                    // 🛡️ Ensure mapped fields are passed up to the UI contract
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
                Log.i(TAG, "Transmitting feedback for $taskId (Positive: $isPositive) to $targetUrl")

                val response = client.post(targetUrl) {
                    contentType(ContentType.Application.Json)
                    attachAgentSignature()
                    setBody(FeedbackPayload(
                        is_positive = isPositive,
                        category = category,
                        label = label,
                        vent_text = ventText
                    ))
                }

                if (response.status.isSuccess()) {
                    Log.i(TAG, "Feedback for $taskId successfully logged on PAN Network.")
                    true
                } else {
                    Log.e(TAG, "Feedback rejected by server. HTTP Status: ${response.status.value}")
                    false
                }
            } catch (e: Exception) {
                Log.e(TAG, "Network connection lost during feedback submission: ${e.message}", e)
                false
            }
        }
    }

    suspend fun joinWaitlist(itemId: String, email: String): Boolean {
        return withContext(Dispatchers.IO) {
            try {
                val targetUrl = "$hostUrl/api/v1/store/waitlist"
                Log.i(TAG, "Joining waitlist for hardware $itemId")

                val response = client.post(targetUrl) {
                    contentType(ContentType.Application.Json)
                    attachAgentSignature()
                    setBody(WaitlistPayload(
                        item_id = itemId,
                        email = email
                    ))
                }

                if (response.status.isSuccess()) {
                    Log.i(TAG, "Successfully secured waitlist position for $itemId.")
                    true
                } else {
                    Log.e(TAG, "Waitlist API rejected request. HTTP Status: ${response.status.value}")
                    false
                }
            } catch (e: Exception) {
                Log.e(TAG, "Network connection lost during waitlist submission: ${e.message}", e)
                false
            }
        }
    }

    override suspend fun triggerBackendDispatch(lat: Double, lon: Double, errorCode: String): Boolean {
        return false
    }

    override suspend fun updateLocationTelemetry(lat: Double, lon: Double): Boolean = false

    // 🛡️ FIX: Added updatePresence to satisfy the interface
    override suspend fun updatePresence(isOnline: Boolean): Boolean = false

    override suspend fun fetchActiveMissions(): List<com.pan.tactical.models.MissionData> = emptyList()
    override suspend fun acknowledgeMission(taskId: String): Boolean = false

    // 🛡️ FIX: Added the reason parameter to satisfy the interface
    override suspend fun declineMission(taskId: String, reason: String?): Boolean = false

    override suspend fun completeMission(taskId: String, evidenceUrls: List<String>): Boolean = false

    fun close() = client.close()
}