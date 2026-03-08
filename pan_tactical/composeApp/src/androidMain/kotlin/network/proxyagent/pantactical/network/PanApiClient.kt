package network.proxyagent.pantactical.network

import io.ktor.client.*
import io.ktor.client.engine.okhttp.*
import io.ktor.client.plugins.contentnegotiation.*
import io.ktor.client.request.*
import io.ktor.client.statement.*
import io.ktor.http.*
import io.ktor.serialization.kotlinx.json.*
import io.ktor.utils.io.*
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.isActive
import kotlinx.coroutines.withContext
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json
import network.proxyagent.pantactical.security.StrongBoxManager
import com.google.android.gms.maps.model.LatLng
import java.util.concurrent.TimeUnit
import kotlinx.coroutines.delay

// --- DATA MODELS ---
@Serializable
data class StatusUpdateRequest(
    val status: String,
    val latitude: Double,
    val longitude: Double,
    val radius: Double,
    val loadout: Map<String, Float>,
    val signature: String,
    val timestamp: Long
)

@Serializable
data class MissionCompleteRequest(val agentId: String, val netPayout: Double)

@Serializable
data class LinkCardRequest(val agentId: String, val cardNumber: String)

@Serializable
data class WithdrawRequest(val agentId: String, val amount: Double)

@Serializable
data class TransactionLog(val id: String, val date: String, val amount: String, val description: String)

@Serializable
data class WalletResponse(val balance: Double, val linkedCard: String? = null, val history: List<TransactionLog>)

class PanApiClient {

    private val client = HttpClient(OkHttp) {
        // --- NEW: Disable the 10-second timeout for infinite SSE streaming ---
        engine {
            config {
                readTimeout(0, TimeUnit.MILLISECONDS)
            }
        }
        install(ContentNegotiation) {
            json(Json { ignoreUnknownKeys = true; prettyPrint = true })
        }
    }

    // --- FIREBASE RTDB PRODUCTION URL ---
    private val BASE_URL = "https://pan-tactical-default-rtdb.firebaseio.com"

    suspend fun updateAgentStatus(
        context: android.content.Context,
        isOnline: Boolean,
        lat: Double,
        lon: Double,
        radiusMiles: Double,
        loadout: Map<String, Float>
    ): Boolean {
        return withContext(Dispatchers.IO) {
            try {
                val statusString = if (isOnline) "ONLINE" else "OFFLINE"
                val payloadToSign = "${statusString}_${lat}_${lon}_${radiusMiles}"
                val nonce = android.util.Base64.encodeToString(payloadToSign.toByteArray(), android.util.Base64.URL_SAFE or android.util.Base64.NO_WRAP)

                println("🛡️ Requesting Google Play Integrity Attestation...")
                val engine = network.proxyagent.pantactical.security.AttestationEngine()
                val hardwareToken = engine.generateHardwareToken(context, nonce)

                val requestBody = StatusUpdateRequest(
                    status = statusString,
                    latitude = lat,
                    longitude = lon,
                    radius = radiusMiles,
                    loadout = loadout,
                    signature = hardwareToken,
                    timestamp = System.currentTimeMillis()
                )

                // FIREBASE REST: PUT request overwrites the agent's current status node
                val response: HttpResponse = client.put("$BASE_URL/agents/VANGUARD-01/status.json") {
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
        withContext(Dispatchers.IO) {
            println("🟢 DISPATCH LINE OPEN: Tactical Short-Polling engaged...")

            // --- NEW: Bypass Samsung Knox with a 2-second GET heartbeat ---
            while (isActive) {
                try {
                    val response: HttpResponse = client.get("$BASE_URL/dispatch/$agentId.json") {
                        header(HttpHeaders.CacheControl, "no-cache")
                    }

                    val jsonString = response.bodyAsText()

                    // Firebase returns the string "null" if the node is empty
                    if (jsonString != "null" && jsonString.isNotBlank()) {
                        try {
                            val json = org.json.JSONObject(jsonString)
                            if (json.optString("type") == "MISSION") {
                                println("🚨 INCOMING FIREBASE PAYLOAD: $jsonString")

                                val lat = json.getDouble("lat")
                                val lon = json.getDouble("lon")
                                val errorCode = json.optString("errorCode", "UNKNOWN ERROR")
                                val bounty = json.optString("bounty", "$0.00")
                                val intersection = json.optString("intersection", "Unknown Coordinates")

                                withContext(Dispatchers.Main) {
                                    onMissionReceived(lat, lon, errorCode, bounty, intersection)
                                }

                                // Auto-delete the payload so we don't trigger it again
                                client.delete("$BASE_URL/dispatch/$agentId.json")
                            }
                        } catch (e: Exception) {
                            println("⚠️ Failed to decode tactical payload: ${e.message}")
                        }
                    }
                } catch (e: Exception) {
                    println("📡 DISPATCH POLL ERROR: ${e.message}")
                }

                // Pause for 2 seconds before checking again to preserve battery
                delay(2000)
            }
        }
    }

    suspend fun acceptMission(agentId: String = "VANGUARD-01"): Boolean {
        return withContext(Dispatchers.IO) {
            try {
                // Update Firebase to show the agent has locked the mission
                val response: HttpResponse = client.put("$BASE_URL/agents/$agentId/mission_state.json") {
                    contentType(ContentType.Application.Json)
                    setBody("\"ACCEPTED\"")
                }
                response.status.isSuccess()
            } catch (e: Exception) {
                println("API ERROR: Failed to accept mission - ${e.message}")
                false
            }
        }
    }

    suspend fun getTacticalRoute(startLat: Double, startLon: Double, endLat: Double, endLon: Double): Pair<List<LatLng>, List<Triple<String, Double, Double>>> {
        return withContext(Dispatchers.IO) {
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

                                if (type == "arrive") stepsList.add(Triple("Arrive at Destination", stepLat, stepLon))
                                else if (distanceMiles > 0.0) stepsList.add(Triple("$formattedAction onto $name", stepLat, stepLon))
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
        return withContext(Dispatchers.IO) {
            try {
                // Mock endpoint pointing to Firebase for successful escrow completion
                val response: HttpResponse = client.post("$BASE_URL/ledger/escrow_claim.json") {
                    contentType(ContentType.Application.Json)
                    setBody(MissionCompleteRequest(agentId, netPayout))
                }
                response.status.isSuccess()
            } catch (e: Exception) {
                println("💰 ESCROW ERROR: Failed to claim funds - ${e.message}")
                false
            }
        }
    }

    suspend fun getWalletData(agentId: String = "VANGUARD-01"): WalletResponse? {
        return withContext(Dispatchers.IO) { null } // Disabled until backend ledger is built
    }

    suspend fun linkDebitCard(agentId: String = "VANGUARD-01", cardNumber: String): Boolean {
        return withContext(Dispatchers.IO) { false } // Disabled until Stripe is integrated
    }

    suspend fun withdrawFunds(agentId: String = "VANGUARD-01", amount: Double): Boolean {
        return withContext(Dispatchers.IO) { false } // Disabled until Stripe is integrated
    }
}