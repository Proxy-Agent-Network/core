package com.pan.tactical.network

import android.graphics.Bitmap
import android.util.Base64
import android.util.Log
import com.google.firebase.auth.FirebaseAuth
import io.ktor.client.*
import io.ktor.client.engine.okhttp.*
import io.ktor.client.plugins.contentnegotiation.*
import io.ktor.client.request.*
import io.ktor.client.statement.*
import io.ktor.http.*
import io.ktor.serialization.kotlinx.json.*
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.isActive
import kotlinx.coroutines.withContext
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json
import com.google.android.gms.maps.model.LatLng
import java.io.ByteArrayOutputStream
import java.util.concurrent.TimeUnit
import kotlinx.coroutines.delay

import com.pan.tactical.ui.WalletNetworkClient
import com.pan.tactical.ui.WalletResponse
import com.pan.tactical.ui.TransactionLog
import com.pan.tactical.BuildConfig // 🛠️ THE FIX 1: Import generated BuildConfig

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

class PanApiClient : WalletNetworkClient {

    companion object {
        private const val TAG = "PanApiClient"
    }

    private val client = HttpClient(OkHttp) {
        engine {
            config {
                readTimeout(0, TimeUnit.MILLISECONDS)
            }
        }
        install(ContentNegotiation) {
            json(Json { ignoreUnknownKeys = true; prettyPrint = true })
        }
    }

    // 🛠️ THE FIX 2: Correctly reference BuildConfig variables
    private val FIREBASE_URL = BuildConfig.FIREBASE_RTDB_URL
    private val PAN_API_URL = "${BuildConfig.PAN_API_BASE_URL}/api/v1"

    // 🛠️ THE FIX 3: Keep identity internal so we don't violate the interface or UI contracts
    private val agentId: String
        get() = FirebaseAuth.getInstance().currentUser?.uid ?: "VANGUARD-01"

    override suspend fun triggerBackendDispatch(lat: Double, lon: Double, faultCode: String): Boolean {
        return withContext(Dispatchers.IO) {
            try {
                Log.i(TAG, "🚀 Injecting V2X Distress Signal to Python Backend...")
                val response: HttpResponse = client.post("$PAN_API_URL/v2x/distress") {
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
                Log.i(TAG, "🔑 [IDENTITY] Active Node UID: $agentId")

                val statusString = if (isOnline) "ONLINE" else "OFFLINE"
                val payloadToSign = "${statusString}_${lat}_${lon}_${radiusMiles}"
                val nonce = Base64.encodeToString(
                    payloadToSign.toByteArray(),
                    Base64.URL_SAFE or Base64.NO_WRAP
                )

                val engine = com.pan.tactical.security.AttestationEngine()
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

                val response: HttpResponse =
                    client.put("$FIREBASE_URL/agents/$agentId/status.json") {
                        contentType(ContentType.Application.Json)
                        setBody(requestBody)
                    }

                response.status.isSuccess()
            } catch (e: Exception) {
                Log.e(TAG, "Failed to update agent status: ${e.message}", e)
                false
            }
        }
    }

    suspend fun updateLocationTelemetry(lat: Double, lon: Double): Boolean {
        return withContext(Dispatchers.IO) {
            try {
                val payload = """
                    {
                        "latitude": $lat, 
                        "longitude": $lon, 
                        "timestamp": ${System.currentTimeMillis()}
                    }
                """.trimIndent()

                val response: HttpResponse = client.patch("$FIREBASE_URL/agents/$agentId/status.json") {
                    contentType(ContentType.Application.Json)
                    setBody(payload)
                }
                response.status.isSuccess()
            } catch (e: Exception) {
                Log.e(TAG, "Failed to update location telemetry: ${e.message}", e)
                false
            }
        }
    }

    suspend fun openLiveDispatchLine(
        onMissionReceived: (lat: Double, lon: Double, errorCode: String, bounty: String, intersection: String) -> Unit
    ) {
        withContext(Dispatchers.IO) {
            Log.i(TAG, "🟢 DISPATCH LINE OPEN: Listening on Node $agentId...")

            while (isActive) {
                try {
                    val response: HttpResponse = client.get("$FIREBASE_URL/dispatch/$agentId.json") {
                        header(HttpHeaders.CacheControl, "no-cache")
                    }

                    val jsonString = response.bodyAsText()

                    if (jsonString != "null" && jsonString.isNotBlank()) {
                        try {
                            val json = org.json.JSONObject(jsonString)
                            if (json.optString("type") == "MISSION") {
                                val lat = json.getDouble("lat")
                                val lon = json.getDouble("lon")
                                val errorCode = json.optString("errorCode", "UNKNOWN ERROR")
                                val bounty = json.optString("bounty", "$0.00")
                                val intersection = json.optString("intersection", "Unknown Coordinates")

                                withContext(Dispatchers.Main) {
                                    onMissionReceived(lat, lon, errorCode, bounty, intersection)
                                }

                                client.delete("$FIREBASE_URL/dispatch/$agentId.json")
                            }
                        } catch (e: Exception) {
                            Log.e(TAG, "Malformed dispatch JSON payload: ${e.message}", e)
                        }
                    }
                } catch (e: Exception) {
                    Log.e(TAG, "Dispatch line polling failed: ${e.message}", e)
                }
                delay(2000)
            }
        }
    }

    suspend fun acceptMission(): Boolean {
        return withContext(Dispatchers.IO) {
            try {
                val response: HttpResponse =
                    client.put("$FIREBASE_URL/agents/$agentId/mission_state.json") {
                        contentType(ContentType.Application.Json)
                        setBody("\"ACCEPTED\"")
                    }
                response.status.isSuccess()
            } catch (e: Exception) {
                Log.e(TAG, "Failed to accept mission: ${e.message}", e)
                false
            }
        }
    }

    suspend fun getTacticalRoute(
        startLat: Double,
        startLon: Double,
        endLat: Double,
        endLon: Double,
        mode: String = "driving"
    ): Pair<List<LatLng>, List<Triple<String, Double, Double>>> {
        return withContext(Dispatchers.IO) {
            try {
                val urlString = "https://router.project-osrm.org/route/v1/$mode/$startLon,$startLat;$endLon,$endLat?overview=full&geometries=geojson&steps=true"
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
                Log.e(TAG, "Failed to retrieve tactical route: ${e.message}", e)
                Pair(emptyList(), emptyList())
            }
        }
    }

    suspend fun uploadEvidenceArray(bitmaps: List<Bitmap>): List<String> {
        return withContext(Dispatchers.IO) {
            val uploadedUrls = mutableListOf<String>()
            val relayApiKey = BuildConfig.IMGBB_API_KEY
            
            if (relayApiKey.isEmpty()) {
                Log.e(TAG, "IMGBB_API_KEY not configured. Evidence upload skipped.")
                return@withContext uploadedUrls
            }

            // 🛠️ THE FIX 4: Replaced the unused index parameter cleanly
            bitmaps.forEachIndexed { _, bitmap ->
                try {
                    val stream = ByteArrayOutputStream()
                    bitmap.compress(Bitmap.CompressFormat.JPEG, 70, stream)
                    val byteArray = stream.toByteArray()
                    val base64Image = Base64.encodeToString(byteArray, Base64.DEFAULT)

                    val response: HttpResponse = client.post("https://api.imgbb.com/1/upload?key=$relayApiKey") {
                        contentType(ContentType.Application.FormUrlEncoded)
                        setBody("image=${java.net.URLEncoder.encode(base64Image, "UTF-8")}")
                    }

                    if (response.status.isSuccess()) {
                        val json = org.json.JSONObject(response.bodyAsText())
                        val downloadUrl = json.optJSONObject("data")?.optString("url", "") ?: ""
                        if (downloadUrl.isNotEmpty()) uploadedUrls.add(downloadUrl)
                    }
                } catch (e: Exception) {
                    Log.e(TAG, "Failed to upload evidence bitmap: ${e.message}", e)
                }
            }
            uploadedUrls
        }
    }

    suspend fun claimEscrowFunds(netPayout: Double, evidenceUrls: List<String> = emptyList()): Boolean {
        return withContext(Dispatchers.IO) {
            try {
                val currentWallet = getWalletData()
                val newBalance = (currentWallet?.balance ?: 0.0) + netPayout

                client.put("$FIREBASE_URL/agents/$agentId/wallet/balance.json") {
                    contentType(ContentType.Application.Json)
                    setBody(newBalance.toString())
                }

                val txId = "tx_${System.currentTimeMillis()}"

                val tx = TransactionLog(
                    id = txId,
                    date = "Today",
                    amount = String.format("+$%.2f", netPayout),
                    description = "Smart Contract Payout",
                    evidenceUrls = evidenceUrls
                )

                val txJson = org.json.JSONObject().apply {
                    put("id", tx.id)
                    put("date", tx.date)
                    put("amount", tx.amount)
                    put("description", tx.description)
                    if (evidenceUrls.isEmpty()) {
                        put("evidenceUrls", org.json.JSONObject.NULL)
                    } else {
                        val array = org.json.JSONArray()
                        evidenceUrls.forEach { array.put(it) }
                        put("evidenceUrls", array)
                    }
                }.toString()

                client.put("$FIREBASE_URL/agents/$agentId/wallet/history/$txId.json") {
                    contentType(ContentType.Application.Json)
                    setBody(txJson)
                }
                true
            } catch (e: Exception) {
                Log.e(TAG, "Failed to claim escrow funds: ${e.message}", e)
                false
            }
        }
    }

    override suspend fun getWalletData(): WalletResponse? {
        return withContext(Dispatchers.IO) {
            try {
                val response: HttpResponse = client.get("$FIREBASE_URL/agents/$agentId/wallet.json") {
                    header(HttpHeaders.CacheControl, "no-cache")
                }

                val jsonString = response.bodyAsText()
                if (jsonString == "null" || jsonString.isBlank()) {
                    return@withContext WalletResponse(0.0, null, emptyList())
                }

                val json = org.json.JSONObject(jsonString)
                val balance = json.optDouble("balance", 0.0)
                val linkedCard = if (json.isNull("linkedCard")) null else json.optString("linkedCard")

                val historyList = mutableListOf<TransactionLog>()
                val historyObj = json.optJSONObject("history")

                if (historyObj != null) {
                    val keys = historyObj.keys()
                    while (keys.hasNext()) {
                        val key = keys.next()
                        val tx = historyObj.getJSONObject(key)

                        val urls = mutableListOf<String>()
                        val urlArray = tx.optJSONArray("evidenceUrls")
                        if (urlArray != null) {
                            for (i in 0 until urlArray.length()) {
                                urls.add(urlArray.getString(i))
                            }
                        }

                        historyList.add(
                            TransactionLog(
                                id = tx.optString("id", key),
                                date = tx.optString("date", "Unknown"),
                                amount = tx.optString("amount", "$0.00"),
                                description = tx.optString("description", "Ledger Entry"),
                                evidenceUrls = if (urls.isEmpty()) null else urls
                            )
                        )
                    }
                }

                historyList.sortByDescending { it.id }

                WalletResponse(balance, linkedCard, historyList)
            } catch (e: Exception) {
                Log.e(TAG, "Failed to retrieve wallet data: ${e.message}", e)
                null
            }
        }
    }

    override suspend fun linkDebitCard(cardNumber: String): Boolean {
        return withContext(Dispatchers.IO) {
            try {
                val response: HttpResponse =
                    client.put("$FIREBASE_URL/agents/$agentId/wallet/linkedCard.json") {
                        contentType(ContentType.Application.Json)
                        setBody("\"$cardNumber\"")
                    }
                response.status.isSuccess()
            } catch (e: Exception) {
                Log.e(TAG, "Failed to link debit card: ${e.message}", e)
                false
            }
        }
    }

    override suspend fun withdrawFunds(amount: Double): Boolean {
        return withContext(Dispatchers.IO) {
            try {
                client.put("$FIREBASE_URL/agents/$agentId/wallet/balance.json") {
                    contentType(ContentType.Application.Json)
                    setBody("0.0")
                }

                val txId = "wd_${System.currentTimeMillis()}"

                val txJson = org.json.JSONObject().apply {
                    put("id", txId)
                    put("date", "Today")
                    put("amount", "-$${String.format("%.2f", amount)}")
                    put("description", "ACH Bank Transfer")
                    put("evidenceUrls", org.json.JSONObject.NULL)
                }.toString()

                client.put("$FIREBASE_URL/agents/$agentId/wallet/history/$txId.json") {
                    contentType(ContentType.Application.Json)
                    setBody(txJson)
                }
                true
            } catch (e: Exception) {
                Log.e(TAG, "Failed to withdraw funds: ${e.message}", e)
                false
            }
        }
    }
}