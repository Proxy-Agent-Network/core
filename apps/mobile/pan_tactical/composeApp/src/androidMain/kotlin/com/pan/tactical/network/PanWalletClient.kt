package com.pan.tactical.network

import android.util.Log
import com.pan.tactical.BuildConfig
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
data class LinkCardPayload(val card_number: String)

@Serializable
data class WithdrawPayload(val amount: Double)

@Serializable
data class V2XDistressPayload(
    val vin: String,
    val fault_code: String,
    val latitude: Double,
    val longitude: Double,
    val bounty_usd: Double,
    val timestamp: Long
)

@Serializable
data class TelemetryPayload(
    val agent_id: String,
    val latitude: Double,
    val longitude: Double,
    val status: String
)

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

    private val hostUrl = BuildConfig.PAN_API_BASE_URL
    private val baseUrl = "$hostUrl/api/v1/wallet"

    private fun HttpRequestBuilder.attachAgentSignature() {
        header("Authorization", "Bearer dev-token-777")
        header("X-Agent-ID", "VANGUARD-01")
    }

    override suspend fun getWalletData(): WalletResponse? {
        return withContext(Dispatchers.IO) {
            try {
                Log.d(TAG, "Fetching wallet from: $baseUrl/")
                // 7. Added the trailing slash to bypass FastAPI 307 redirects
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

    override suspend fun linkDebitCard(cardNumber: String): Boolean {
        return withContext(Dispatchers.IO) {
            try {
                val response = client.post("$baseUrl/link-card") {
                    contentType(ContentType.Application.Json)
                    attachAgentSignature()
                    setBody(LinkCardPayload(card_number = cardNumber))
                }

                if (!response.status.isSuccess()) {
                    Log.w(TAG, "Card linking rejected: HTTP ${response.status.value}")
                }

                response.status.isSuccess()
            } catch (e: Exception) {
                Log.e(TAG, "Card linking failed: ${e.message}", e)
                false
            }
        }
    }

    override suspend fun withdrawFunds(amount: Double): Boolean {
        return withContext(Dispatchers.IO) {
            try {
                val response = client.post("$baseUrl/withdraw") {
                    contentType(ContentType.Application.Json)
                    attachAgentSignature()
                    setBody(WithdrawPayload(amount = amount))
                }

                if (!response.status.isSuccess()) {
                    Log.w(TAG, "Withdrawal rejected: HTTP ${response.status.value}")
                }

                response.status.isSuccess()
            } catch (e: Exception) {
                Log.e(TAG, "Withdrawal failed: ${e.message}", e)
                false
            }
        }
    }

    override suspend fun triggerBackendDispatch(lat: Double, lon: Double, errorCode: String): Boolean {
        return withContext(Dispatchers.IO) {
            try {
                Log.i(TAG, "🚀 Injecting V2X Distress Signal via WalletClient to Python Backend...")
                val response: HttpResponse = client.post("$hostUrl/api/v1/v2x/distress") {
                    attachAgentSignature() // 8. Standardized auth
                    header("X-Fleet-Id", "DEV-FLEET-01")
                    contentType(ContentType.Application.Json)
                    
                    // 1 & 2. Fixed string template bug by using the strongly typed DTO
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
                    attachAgentSignature() // 8. Standardized auth
                    
                    // 3. Removed raw string interpolation for the typed DTO
                    setBody(TelemetryPayload(
                        agent_id = "VANGUARD-01",
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
        return kotlinx.coroutines.withContext(kotlinx.coroutines.Dispatchers.IO) {
            try {
                val response = client.get("$hostUrl/api/v1/agent/missions") {
                    header("Authorization", "Bearer dev-token-777")
                }

                if (response.status.isSuccess()) {
                    val jsonString = response.bodyAsText()
                    val jsonArray = kotlinx.serialization.json.Json.parseToJsonElement(jsonString).jsonArray

                    jsonArray.map { element ->
                        val obj = element.jsonObject

                        // 🪤 TRAP 1: Did the phone actually catch the ID from the JSON?
                        val parsedId = obj["taskId"]?.jsonPrimitive?.content ?: ""
                        android.util.Log.w("PanNetwork", "🔍 Parsed Mission from Server! Task ID: '$parsedId'")

                        com.pan.tactical.models.MissionData(
                            taskId = parsedId, // Ensure your MissionData.kt model has this variable!
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
                android.util.Log.e("PanNetwork", "Failed to parse missions: ${e.message}")
                emptyList()
            }
        }
    }

    override suspend fun declineMission(taskId: String): Boolean {
        return kotlinx.coroutines.withContext(kotlinx.coroutines.Dispatchers.IO) {
            // 🪤 TRAP 2: Did the UI button pass the ID to the network client?
            android.util.Log.w("PanNetwork", "🔴 UI CLICKED DECLINE! Sending Task ID: '$taskId' to backend...")

            if (taskId.isBlank()) {
                android.util.Log.e("PanNetwork", "❌ STOPPING NETWORK CALL: taskId is blank! The UI forgot to pass it.")
                return@withContext false
            }

            try {
                val response = client.post("$hostUrl/api/v1/agent/missions/$taskId/decline") {
                    header("Authorization", "Bearer dev-token-777")
                }
                response.status.isSuccess()
            } catch (e: Exception) {
                android.util.Log.e("PanNetwork", "Failed to decline mission: ${e.message}", e)
                false
            }
        }
    }

    fun close() = client.close()
}