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
import java.net.URL
import com.google.android.gms.maps.model.LatLng

// --- DATA MODELS ---
@Serializable
data class StatusUpdateRequest(
    val agentId: String,
    val status: String,
    val latitude: Double,
    val longitude: Double,
    val radius: Double,
    val loadout: Map<String, Float>,
    val signature: String
)

@Serializable
data class MissionCompleteRequest(val agentId: String, val netPayout: Double)

@Serializable
data class LinkCardRequest(val agentId: String, val cardNumber: String)

@Serializable
data class WithdrawRequest(val agentId: String, val amount: Double)

@Serializable
data class TransactionLog(
    val id: String,
    val date: String,
    val amount: String,
    val description: String
)

@Serializable
data class WalletResponse(
    val balance: Double,
    val linkedCard: String? = null,
    val history: List<TransactionLog>
)

class PanApiClient {

    private val client = HttpClient(OkHttp) {
        install(ContentNegotiation) {
            json(Json {
                ignoreUnknownKeys = true
                prettyPrint = true
            })
        }
        install(WebSockets)
    }

    private val BASE_URL = "https://collectible-kanisha-altruistically.ngrok-free.dev/v1"
    private val strongBox = StrongBoxManager()

    suspend fun updateAgentStatus(
        context: android.content.Context,
        isOnline: Boolean,
        lat: Double,
        lon: Double,
        radiusMiles: Double, // The parameter is called radiusMiles
        loadout: Map<String, Float>
    ): Boolean {
        return kotlinx.coroutines.withContext(kotlinx.coroutines.Dispatchers.IO) {
            try {
                val statusString = if (isOnline) "ONLINE" else "OFFLINE"
                // --- FIXED: Reference the correct variable name (radiusMiles) ---
                val payloadToSign = "${statusString}_${lat}_${lon}_${radiusMiles}"

                val nonce = android.util.Base64.encodeToString(
                    payloadToSign.toByteArray(),
                    android.util.Base64.URL_SAFE or android.util.Base64.NO_WRAP or android.util.Base64.NO_PADDING
                )

                println("🛡️ Requesting Google Play Integrity Attestation...")
                val engine = network.proxyagent.pantactical.security.AttestationEngine()
                val hardwareToken = engine.generateHardwareToken(context, nonce)

                val requestBody = StatusUpdateRequest(
                    agentId = "VANGUARD-01",
                    status = statusString,
                    latitude = lat,
                    longitude = lon,
                    radius = radiusMiles, // --- FIXED: Pass radiusMiles into the data class ---
                    loadout = loadout,
                    signature = hardwareToken
                )

                val response: HttpResponse = client.post("$BASE_URL/agent/status") {
                    header("ngrok-skip-browser-warning", "69420")
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

    suspend fun openLiveDispatchLine(
        agentId: String,
        onMissionReceived: (lat: Double, lon: Double, errorCode: String, bounty: String, intersection: String) -> Unit
    ) {
        val wsUrl = BASE_URL
            .replace("https://", "wss://")
            .replace("http://", "ws://")
            .replace("/v1", "/ws/v1/dispatch/$agentId")

        try {
            client.webSocket(wsUrl) {
                request { header("ngrok-skip-browser-warning", "69420") }

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
                            val errorCode = json.optString("errorCode", "UNKNOWN ERROR")
                            val bounty = json.optString("bounty", "$0.00")
                            val intersection = json.optString("intersection", "Unknown Coordinates")

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

    suspend fun acceptMission(agentId: String = "VANGUARD-01"): Boolean {
        return kotlinx.coroutines.withContext(kotlinx.coroutines.Dispatchers.IO) {
            try {
                val jsonPayload = """{"agentId": "$agentId"}"""
                val response: HttpResponse = client.post("$BASE_URL/mission/accept") {
                    header("ngrok-skip-browser-warning", "69420")
                    contentType(ContentType.Application.Json)
                    setBody(jsonPayload)
                }
                response.status.value in 200..299
            } catch (e: Exception) {
                println("API ERROR: Failed to accept mission - ${e.message}")
                false
            }
        }
    }

    suspend fun getTacticalRoute(startLat: Double, startLon: Double, endLat: Double, endLon: Double): Pair<List<LatLng>, List<Triple<String, Double, Double>>> {
        return kotlinx.coroutines.withContext(kotlinx.coroutines.Dispatchers.IO) {
            try {
                val urlString = "https://router.project-osrm.org/route/v1/driving/$startLon,$startLat;$endLon,$endLat?overview=full&geometries=geojson&steps=true"

                val response: HttpResponse = client.get(urlString)
                val jsonString = response.bodyAsText()
                val json = org.json.JSONObject(jsonString)
                val routes = json.optJSONArray("routes")

                if (routes != null && routes.length() > 0) {
                    val routeObj = routes.getJSONObject(0)

                    val geometry = routeObj.getJSONObject("geometry")
                    val coordinates = geometry.getJSONArray("coordinates")
                    val path = mutableListOf<LatLng>()
                    for (i in 0 until coordinates.length()) {
                        val point = coordinates.getJSONArray(i)
                        path.add(LatLng(point.getDouble(1), point.getDouble(0)))
                    }

                    val stepsList = mutableListOf<Triple<String, Double, Double>>()
                    val legs = routeObj.optJSONArray("legs")
                    if (legs != null && legs.length() > 0) {
                        val steps = legs.getJSONObject(0).optJSONArray("steps")
                        if (steps != null) {
                            for (j in 0 until steps.length()) {
                                val step = steps.getJSONObject(j)
                                val maneuver = step.optJSONObject("maneuver")
                                val distanceMiles = step.optDouble("distance", 0.0) / 1609.34

                                val location = maneuver?.optJSONArray("location")
                                val stepLon = location?.optDouble(0) ?: 0.0
                                val stepLat = location?.optDouble(1) ?: 0.0

                                val type = maneuver?.optString("type", "") ?: ""
                                val modifier = maneuver?.optString("modifier", "") ?: ""
                                var name = step.optString("name", "")
                                if (name.isEmpty()) name = "unnamed road"

                                val action = if (modifier.isNotEmpty() && modifier != "straight") "$type $modifier" else type
                                val formattedAction = action.replaceFirstChar { if (it.isLowerCase()) it.titlecase() else it.toString() }

                                if (type == "arrive") {
                                    stepsList.add(Triple("Arrive at Destination", stepLat, stepLon))
                                } else if (distanceMiles > 0.0) {
                                    stepsList.add(Triple("$formattedAction onto $name", stepLat, stepLon))
                                }
                            }
                        }
                    }
                    return@withContext Pair(path, stepsList)
                }
                Pair(emptyList(), emptyList())
            } catch (e: Exception) {
                println("🗺️ ROUTING ERROR: ${e.message}")
                Pair(emptyList(), emptyList())
            }
        }
    }

    suspend fun claimEscrowFunds(agentId: String = "VANGUARD-01", netPayout: Double): Boolean {
        return kotlinx.coroutines.withContext(kotlinx.coroutines.Dispatchers.IO) {
            try {
                val requestBody = MissionCompleteRequest(agentId, netPayout)
                val response: HttpResponse = client.post("$BASE_URL/mission/complete") {
                    header("ngrok-skip-browser-warning", "69420")
                    contentType(ContentType.Application.Json)
                    setBody(requestBody)
                }
                response.status.isSuccess()
            } catch (e: Exception) {
                println("💰 ESCROW ERROR: Failed to claim funds - ${e.message}")
                false
            }
        }
    }

    suspend fun getWalletData(agentId: String = "VANGUARD-01"): WalletResponse? {
        return kotlinx.coroutines.withContext(kotlinx.coroutines.Dispatchers.IO) {
            try {
                val response: HttpResponse = client.get("$BASE_URL/agent/$agentId/wallet") {
                    header("ngrok-skip-browser-warning", "69420")
                }
                if (response.status.isSuccess()) {
                    val jsonString = response.bodyAsText()
                    Json { ignoreUnknownKeys = true }.decodeFromString<WalletResponse>(jsonString)
                } else null
            } catch (e: Exception) {
                println("🏦 WALLET ERROR: Failed to fetch ledger - ${e.message}")
                null
            }
        }
    }

    suspend fun linkDebitCard(agentId: String = "VANGUARD-01", cardNumber: String): Boolean {
        return kotlinx.coroutines.withContext(kotlinx.coroutines.Dispatchers.IO) {
            try {
                val requestBody = LinkCardRequest(agentId, cardNumber)
                val response: HttpResponse = client.post("$BASE_URL/wallet/link_card") {
                    header("ngrok-skip-browser-warning", "69420")
                    contentType(ContentType.Application.Json)
                    setBody(requestBody)
                }
                response.status.isSuccess()
            } catch (e: Exception) {
                println("🏦 BANK ERROR: Failed to link card - ${e.message}")
                false
            }
        }
    }

    suspend fun withdrawFunds(agentId: String = "VANGUARD-01", amount: Double): Boolean {
        return kotlinx.coroutines.withContext(kotlinx.coroutines.Dispatchers.IO) {
            try {
                val requestBody = WithdrawRequest(agentId, amount)
                val response: HttpResponse = client.post("$BASE_URL/wallet/withdraw") {
                    header("ngrok-skip-browser-warning", "69420")
                    contentType(ContentType.Application.Json)
                    setBody(requestBody)
                }
                response.status.isSuccess()
            } catch (e: Exception) {
                println("🏦 BANK ERROR: Failed to withdraw funds - ${e.message}")
                false
            }
        }
    }
}