package network.proxyagent.pantactical.network

import io.ktor.client.plugins.websocket.*
import io.ktor.websocket.*
import io.ktor.client.*
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
import network.proxyagent.pantactical.security.StrongBoxManager
import android.util.Base64
import android.content.Context

// --- DATA MODELS ---
// These classes define the exact JSON structure the PAN Gateway expects.
@Serializable
data class StatusUpdateRequest(
    val agentId: String,
    val status: String, // "ONLINE" or "OFFLINE"
    val latitude: Double,
    val longitude: Double,
    val radius: Double,
    val loadout: List<String>,
    val signature: String // The TPM hardware signature
)

class PanApiClient {

    // Initialize the Ktor HTTP Client with JSON serialization
    private val client = HttpClient(OkHttp) {
        install(ContentNegotiation) {
            json(Json {
                ignoreUnknownKeys = true
                prettyPrint = true
            })
        }
        install(WebSockets)
    }

    // In production, this will point to our live Mesa load balancers.
    // For now, we use a standard development URL.
    private val BASE_URL = "http://192.168.0.108:8000/v1"
    private val strongBox = StrongBoxManager()

    /**
     * Broadcasts the Agent's tactical status to the PAN Gateway.
     * This is a suspend function, meaning it safely runs on a background thread.
     */
    suspend fun updateAgentStatus(context: Context, isOnline: Boolean, lat: Double, lon: Double, radius: Double, loadout: List<String>): Boolean {
        return kotlinx.coroutines.withContext(kotlinx.coroutines.Dispatchers.IO) {
            try {
                val statusString = if (isOnline) "ONLINE" else "OFFLINE"
                val payloadToSign = "${statusString}_${lat}_${lon}_${radius}"

                // 2. Convert our payload into a URL-safe Base64 "Nonce"
                // Google requires the nonce to be formatted exactly like this.
                val nonce = android.util.Base64.encodeToString(
                    payloadToSign.toByteArray(),
                    android.util.Base64.URL_SAFE or android.util.Base64.NO_WRAP or android.util.Base64.NO_PADDING
                )

                // 3. SECURE HARDWARE PING: Ask Google Play to attest this payload
                println("🛡️ Requesting Google Play Integrity Attestation...")
                val engine = network.proxyagent.pantactical.security.AttestationEngine()
                val hardwareToken = engine.generateHardwareToken(context, nonce)

                // 4. Build the JSON request using the real hardware token
                val requestBody = StatusUpdateRequest(
                    agentId = "VANGUARD-01",
                    status = statusString,
                    latitude = lat,
                    longitude = lon,
                    radius = radius,
                    loadout = loadout, // <-- INJECT THE LIST HERE
                    signature = hardwareToken
                )

                val response: HttpResponse = client.post("$BASE_URL/agent/status") {
                    contentType(ContentType.Application.Json)
                    setBody(requestBody)
                }

                response.status.isSuccess()

            } catch (e: Exception) {
                println("NETWORK ERROR: Failed to broadcast status. ${e.localizedMessage}")
                false
            }
        }
    }
    /**
     * Opens a live, two-way WebSocket connection with the PAN Gateway.
     */
    suspend fun openLiveDispatchLine(
        agentId: String,
        onMissionReceived: (lat: Double, lon: Double, errorCode: String, bounty: String, intersection: String) -> Unit
    ) {
        val wsUrl = BASE_URL.replace("http://", "ws://").replace("/v1", "/ws/v1/dispatch/$agentId")

        try {
            client.webSocket(wsUrl) {
                println("🟢 DISPATCH LINE OPEN: Listening for missions...")

                for (frame in incoming) {
                    frame as? Frame.Text ?: continue
                    val text = frame.readText()
                    println("🚨 INCOMING UDS PAYLOAD: $text")

                    try {
                        val json = org.json.JSONObject(text)
                        if (json.getString("type") == "MISSION") {
                            val lat = json.getDouble("lat")
                            val lon = json.getDouble("lon")
                            // Safely extract the new variables (with fallbacks just in case)
                            val errorCode = json.optString("errorCode", "UNKNOWN ERROR")
                            val bounty = json.optString("bounty", "$0.00")
                            val intersection = json.optString("intersection", "Unknown Coordinates")

                            // Fire the rich payload back to the UI!
                            onMissionReceived(lat, lon, errorCode, bounty, intersection)
                        }
                    } catch (e: Exception) {
                        println("⚠️ Failed to decode tactical payload: ${e.message}")
                    }
                }
            }
        } catch (e: Exception) {
            println("🔴 DISPATCH LINE CLOSED: ${e.localizedMessage}")
        }
    }
}