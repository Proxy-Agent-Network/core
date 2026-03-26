package com.pan.tactical.network

import android.util.Log
import com.pan.tactical.ui.TransactionLog
import com.pan.tactical.ui.WalletNetworkClient
import com.pan.tactical.ui.WalletResponse
import com.pan.tactical.BuildConfig // 🛠️ THE FIX 1: Read the physical IP from Gradle
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
import java.util.concurrent.TimeUnit

// --- NETWORK DTOs ---
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
    val balance: Double,
    val linkedCard: String? = null,
    val history: List<NetworkTransactionLog>
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

    // 🛠️ THE FIX 2: Stop falling back to 10.0.2.2. Use the physical IP configured in local.properties
    private val hostUrl = BuildConfig.PAN_API_BASE_URL
    private val baseUrl = "$hostUrl/api/v1/wallet"

    private fun HttpRequestBuilder.attachAgentSignature() {
        header("Authorization", "Bearer dev-token-777")
        header("X-Agent-ID", "VANGUARD-01")
    }

    override suspend fun getWalletData(): WalletResponse? {
        return withContext(Dispatchers.IO) {
            try {
                Log.d(TAG, "Fetching wallet from: $baseUrl")
                val response = client.get(baseUrl) {
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

    // 🛠️ THE FIX 3: Actually fire the V2X Distress Signal since DI bound this class to the UI
    override suspend fun triggerBackendDispatch(lat: Double, lon: Double, faultCode: String): Boolean {
        return withContext(Dispatchers.IO) {
            try {
                Log.i(TAG, "🚀 Injecting V2X Distress Signal via WalletClient to Python Backend...")
                val response: HttpResponse = client.post("$hostUrl/api/v1/v2x/distress") {
                    header("Authorization", "Bearer dev-token-777")
                    header("X-Fleet-Id", "DEV-FLEET-01")
                    contentType(ContentType.Application.Json)
                    setBody("""
                        {
                            "vin": "DEV-VIN-777",
                            "fault_code": "$faultCode",
                            "latitude": $lat,
                            "longitude": $lon,
                            "bounty_usd": 25.00,
                            "timestamp": ${System.currentTimeMillis() / 1000}
                        }
                    """.trimIndent())
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
                    setBody("""
                        {
                            "agent_id": "VANGUARD-01",
                            "latitude": $lat,
                            "longitude": $lon,
                            "status": "ONLINE"
                        }
                    """.trimIndent())
                }
                response.status.isSuccess()
            } catch (e: Exception) {
                Log.e(TAG, "Telemetry update failed: ${e.message}", e)
                false
            }
        }
    }

    fun close() = client.close()
}