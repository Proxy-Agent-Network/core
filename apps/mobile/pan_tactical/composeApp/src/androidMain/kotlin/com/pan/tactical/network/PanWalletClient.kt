// TODO: Remove suppression once KMP BuildConfig visibility is confirmed PUBLIC via gmazzo plugin.
// Track against build.gradle.kts visibility(BuildConfigVisibility.PUBLIC) fix.
@file:Suppress("INVISIBLE_REFERENCE", "INVISIBLE_MEMBER")
package com.pan.tactical.network

import android.util.Log
import com.google.firebase.auth.FirebaseAuth
import com.pan.tactical.BuildConfig
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
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json
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
    val balance: Double = 0.0,
    val linkedCard: String? = null,
    val history: List<NetworkTransactionLog> = emptyList()
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

    // 🟢 THE FIX: Wired securely and directly back to the public BuildConfig
    private val hostUrl = BuildConfig.PAN_API_BASE_URL
    private val baseUrl = "$hostUrl/api/v1/wallet"

    private val secureUid: String
        get() = FirebaseAuth.getInstance().currentUser?.uid
            ?: throw IllegalStateException("Agent identity missing. Cannot execute network operations.")

    private var cachedJwt: String? = null
    private var jwtExpiresAt: Long = 0L

    private fun getFreshJwt(): String {
        val now = System.currentTimeMillis() / 1000
        if (cachedJwt == null || now >= jwtExpiresAt - 30) {
            cachedJwt = StrongBoxManager().generateJwt(secureUid)
            jwtExpiresAt = now + 300 
        }
        return cachedJwt!!
    }

    private fun HttpRequestBuilder.attachAgentSignature() {
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
                Log.d(TAG, "Fetching wallet from: $baseUrl/")
                val response = client.get("$baseUrl/") {
                    attachAgentSignature()
                }

                if (!response.status.isSuccess()) {
                    Log.w(TAG, "Wallet GET rejected: HTTP ${response.status.value}")
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
                    }
                )
            } catch (e: Exception) {
                Log.e(TAG, "Wallet GET failed: ${e.message}", e)
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
                    val errorDetail = try {
                        response.body<ErrorPayload>().detail
                    } catch (e: Exception) {
                        "Network rejected card linking (HTTP ${response.status.value})"
                    }
                    Log.w(TAG, "Card linking rejected: $errorDetail")
                    Result.failure(Exception(errorDetail))
                }
            } catch (e: Exception) {
                Log.e(TAG, "Card linking failed: ${e.message}", e)
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
                    val errorDetail = try {
                        response.body<ErrorPayload>().detail
                    } catch (e: Exception) {
                        "Withdrawal rejected by network (HTTP ${response.status.value})"
                    }
                    Log.w(TAG, "Withdrawal rejected: $errorDetail")
                    Result.failure(Exception(errorDetail))
                }
            } catch (e: Exception) {
                Log.e(TAG, "Withdrawal failed: ${e.message}", e)
                Result.failure(Exception("Connection to PAN Network lost."))
            }
        }
    }

    override suspend fun triggerBackendDispatch(lat: Double, lon: Double, errorCode: String): Boolean {
        return withContext(Dispatchers.IO) {
            try {
                Log.i(TAG, "🚀 Injecting V2X Distress Signal via WalletClient to Python Backend...")
                val response: HttpResponse = client.post("$hostUrl/api/v1/v2x/distress") {
                    attachAgentSignature()
                    header("X-Fleet-Id", "DEV-FLEET-01")
                    contentType(ContentType.Application.Json)

                    setBody(V2XDistressPayload(
                        vin = "DEV-VIN-777",
                        fault_code = errorCode,
                        latitude = lat,
                        longitude = lon,
                        bounty_usd = 25.00,
                        timestamp = System.currentTimeMillis() / 1000
                    ))
                }
                response.status.isSuccess()
            } catch (e: Exception) {
                Log.e(TAG, "Backend V2X injection failed: ${e.message}", e)
                false
            }
        }
    }

    override suspend fun updateLocationTelemetry(lat: Double, lon: Double): Boolean {
        return withContext(Dispatchers.IO) {
            try {
                val response: HttpResponse = client.post("$hostUrl/api/v1/telemetry/ingest") {
                    contentType(ContentType.Application.Json)
                    attachAgentSignature()

                    setBody(TelemetryPayload(
                        agent_id = secureUid,
                        latitude = lat,
                        longitude = lon,
                        status = "ONLINE"
                    ))
                }
                response.status.isSuccess()
            } catch (e: Exception) {
                Log.e(TAG, "Telemetry update failed: ${e.message}", e)
                false
            }
        }
    }

    override suspend fun fetchActiveMissions(): List<com.pan.tactical.models.MissionData> {
        return withContext(Dispatchers.IO) {
            try {
                val response = client.get("$hostUrl/api/v1/agent/missions") {
                    attachAgentSignature()
                }

                if (response.status.isSuccess()) {
                    val jsonString = response.bodyAsText()
                    val jsonArray = Json.parseToJsonElement(jsonString).jsonArray

                    jsonArray.map { element ->
                        val obj = element.jsonObject

                        val parsedId = (obj["taskId"] ?: obj["task_id"])?.jsonPrimitive?.content ?: ""
                        Log.w(TAG, "🔍 Parsed Mission from Server! Task ID: '$parsedId'")

                        com.pan.tactical.models.MissionData(
                            taskId = parsedId,
                            lat = obj["lat"]?.jsonPrimitive?.double ?: 0.0,
                            lon = obj["lon"]?.jsonPrimitive?.double ?: 0.0,
                            errorCode = obj["errorCode"]?.jsonPrimitive?.content ?: "Unknown",
                            bounty = obj["bounty"]?.jsonPrimitive?.content ?: "$0.00",
                            intersection = obj["intersection"]?.jsonPrimitive?.content ?: ""
                        )
                    }
                } else {
                    emptyList()
                }
            } catch (e: Exception) {
                Log.e(TAG, "Failed to parse missions: ${e.message}", e)
                emptyList()
            }
        }
    }

    override suspend fun acknowledgeMission(taskId: String): Boolean {
        return withContext(Dispatchers.IO) {
            try {
                val response = client.post("$hostUrl/api/v1/agent/missions/$taskId/ack") {
                    attachAgentSignature()
                }
                response.status.isSuccess()
            } catch (e: Exception) {
                Log.e(TAG, "Failed to acknowledge mission: ${e.message}", e)
                false
            }
        }
    }

    override suspend fun declineMission(taskId: String): Boolean {
        return withContext(Dispatchers.IO) {
            Log.w(TAG, "🔴 UI CLICKED DECLINE! Sending Task ID: '$taskId' to backend...")

            if (taskId.isBlank()) {
                Log.e(TAG, "❌ STOPPING NETWORK CALL: taskId is blank! The UI forgot to pass it.")
                return@withContext false
            }

            try {
                val response = client.post("$hostUrl/api/v1/agent/missions/$taskId/decline") {
                    attachAgentSignature()
                }
                response.status.isSuccess()
            } catch (e: Exception) {
                Log.e(TAG, "Failed to decline mission: ${e.message}", e)
                false
            }
        }
    }

    override suspend fun completeMission(taskId: String): Boolean {
        return withContext(Dispatchers.IO) {
            try {
                val response = client.post("$hostUrl/api/v1/agent/missions/$taskId/complete") {
                    attachAgentSignature()
                    contentType(ContentType.Application.Json)

                    setBody(
                        MissionCompletePayload(
                            agent_id = secureUid,
                            netPayout = 0.0, 
                            evidence_urls = emptyList(),
                            // 🟢 THE FIX: Cryptographically bound to the hardware TPM
                            hardware_attestation_token = StrongBoxManager().generateJwt(secureUid)
                        )
                    )
                }
                response.status.isSuccess()
            } catch (e: Exception) {
                Log.e(TAG, "Failed to complete mission: ${e.message}", e)
                false
            }
        }
    }

    fun close() = client.close()
}