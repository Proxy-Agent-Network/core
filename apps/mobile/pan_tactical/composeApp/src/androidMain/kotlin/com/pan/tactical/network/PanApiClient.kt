// TODO: Remove suppression once KMP BuildConfig visibility is confirmed PUBLIC via gmazzo plugin.
// Track against build.gradle.kts visibility(BuildConfigVisibility.PUBLIC) fix.
@file:Suppress("INVISIBLE_REFERENCE", "INVISIBLE_MEMBER")
package com.pan.tactical.network

import android.graphics.Bitmap
import android.util.Log
import com.google.firebase.auth.FirebaseAuth
import com.pan.tactical.BuildConfig 
import com.pan.tactical.models.MissionData
import com.pan.tactical.security.StrongBoxManager
import com.pan.tactical.ui.WalletNetworkClient
import com.pan.tactical.ui.WalletResponse
import com.pan.tactical.ui.TransactionLog
import io.ktor.client.*
import io.ktor.client.call.*
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
data class MissionCompletePayload(
    val agent_id: String,
    val netPayout: Double,
    val evidence_urls: List<String>,
    val hardware_attestation_token: String
)

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

    private val FIREBASE_URL = BuildConfig.FIREBASE_RTDB_URL
    private val hostUrl = BuildConfig.PAN_API_BASE_URL
    private val PAN_API_URL = "$hostUrl/api/v1"

    private val secureUid: String
        get() = FirebaseAuth.getInstance().currentUser?.uid
            ?: throw IllegalStateException("Agent identity missing")

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

    override suspend fun triggerBackendDispatch(lat: Double, lon: Double, errorCode: String): Boolean {
        return withContext(Dispatchers.IO) {
            try {
                Log.i(TAG, "🚀 Injecting V2X Distress Signal to Python Backend...")
                val response: HttpResponse = client.post("$PAN_API_URL/v2x/distress") {
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
                val nonce = android.util.Base64.encodeToString(
                    payloadToSign.toByteArray(),
                    android.util.Base64.URL_SAFE or android.util.Base64.NO_WRAP
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
                    client.put("$FIREBASE_URL/agents/$secureUid/status.json") {
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

    override suspend fun updateLocationTelemetry(lat: Double, lon: Double): Boolean {
        return withContext(Dispatchers.IO) {
            try {
                val response: HttpResponse = client.post("$PAN_API_URL/telemetry/ingest") {
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
                Log.e(TAG, "Failed to update location telemetry: ${e.message}", e)
                false
            }
        }
    }

    suspend fun openLiveDispatchLine(
        onMissionReceived: (lat: Double, lon: Double, errorCode: String, bounty: String, intersection: String) -> Unit
    ) {
        withContext(Dispatchers.IO) {
            Log.i(TAG, "🟢 DISPATCH LINE OPEN: Listening on Node $secureUid...")

            while (isActive) {
                try {
                    val response: HttpResponse = client.get("$FIREBASE_URL/dispatch/$secureUid.json") {
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

                                // TODO: Implement two-phase ACK to prevent duplicate dispatches on crash
                                client.delete("$FIREBASE_URL/dispatch/$secureUid.json")
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
                    client.put("$FIREBASE_URL/agents/$secureUid/mission_state.json") {
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
                Log.e(TAG, "IMGBB_API_KEY not configured. Evidence upload skipped to prevent false-positive compliance checks.")
                return@withContext uploadedUrls
            }

            bitmaps.forEachIndexed { _, bitmap ->
                try {
                    val stream = ByteArrayOutputStream()
                    bitmap.compress(Bitmap.CompressFormat.JPEG, 70, stream)
                    val byteArray = stream.toByteArray()
                    val base64Image = android.util.Base64.encodeToString(byteArray, android.util.Base64.DEFAULT)

                    val response: HttpResponse = client.post("https://api.imgbb.com/1/upload?key=$relayApiKey") {
                        contentType(ContentType.Application.FormUrlEncoded)
                        setBody("image=${java.net.URLEncoder.encode(base64Image, "UTF-8")}")
                    }

                    val responseBody = response.bodyAsText()

                    if (response.status.isSuccess()) {
                        val json = org.json.JSONObject(responseBody)
                        val dataObj = json.optJSONObject("data")
                        val downloadUrl = dataObj?.optString("url", "") ?: ""
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

                client.put("$FIREBASE_URL/agents/$secureUid/wallet/balance.json") {
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

                client.put("$FIREBASE_URL/agents/$secureUid/wallet/history/$txId.json") {
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
                val response: HttpResponse = client.get("$FIREBASE_URL/agents/$secureUid/wallet.json") {
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

    override suspend fun linkDebitCard(cardNumber: String): Result<String> {
        return withContext(Dispatchers.IO) {
            try {
                val response: HttpResponse =
                    client.put("$FIREBASE_URL/agents/$secureUid/wallet/linkedCard.json") {
                        contentType(ContentType.Application.Json)
                        setBody("\"$cardNumber\"")
                    }
                if (response.status.isSuccess()) {
                    Result.success("Card linked to legacy wallet.")
                } else {
                    Result.failure(Exception("Network rejected card linking (HTTP ${response.status.value})"))
                }
            } catch (e: Exception) {
                Log.e(TAG, "Failed to link debit card: ${e.message}", e)
                Result.failure(Exception("Connection to legacy network lost."))
            }
        }
    }

    override suspend fun withdrawFunds(amount: Double): Result<String> {
        return withContext(Dispatchers.IO) {
            try {
                client.put("$FIREBASE_URL/agents/$secureUid/wallet/balance.json") {
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

                client.put("$FIREBASE_URL/agents/$secureUid/wallet/history/$txId.json") {
                    contentType(ContentType.Application.Json)
                    setBody(txJson)
                }
                Result.success("Transfer recorded in legacy wallet.")
            } catch (e: Exception) {
                Log.e(TAG, "Failed to withdraw funds: ${e.message}", e)
                Result.failure(Exception("Connection to legacy network lost."))
            }
        }
    }

    override suspend fun fetchActiveMissions(): List<MissionData> {
        return withContext(Dispatchers.IO) {
            try {
                val response = client.get("$PAN_API_URL/agent/missions") {
                    attachAgentSignature()
                }
                if (response.status.isSuccess()) {
                    val jsonString = response.bodyAsText()
                    val array = org.json.JSONArray(jsonString)
                    val list = mutableListOf<MissionData>()
                    
                    for (i in 0 until array.length()) {
                        val obj = array.getJSONObject(i)
                        list.add(
                            MissionData(
                                lat = obj.optDouble("lat", obj.optDouble("latitude", 0.0)),
                                lon = obj.optDouble("lon", obj.optDouble("longitude", 0.0)),
                                errorCode = obj.optString("errorCode", obj.optString("error_code", "")),
                                bounty = obj.optString("bounty", obj.optString("bounty_usd", "")),
                                intersection = obj.optString("intersection", ""),
                                taskId = obj.optString("taskId", obj.optString("task_id", ""))
                            )
                        )
                    }
                    list
                } else {
                    emptyList()
                }
            } catch (e: Exception) {
                Log.e(TAG, "Fetch missions failed: ${e.message}")
                emptyList()
            }
        }
    }

    override suspend fun acknowledgeMission(taskId: String): Boolean {
        return withContext(Dispatchers.IO) {
            try {
                val response = client.post("$PAN_API_URL/agent/missions/$taskId/ack") {
                    attachAgentSignature() 
                }
                response.status.isSuccess()
            } catch (e: Exception) {
                Log.e(TAG, "ACK failed: ${e.message}")
                false
            }
        }
    }

    override suspend fun declineMission(taskId: String): Boolean {
        return withContext(Dispatchers.IO) {
            try {
                val response = client.post("$PAN_API_URL/agent/missions/$taskId/decline") {
                    attachAgentSignature() 
                }
                response.status.isSuccess()
            } catch (e: Exception) {
                Log.e(TAG, "Decline failed: ${e.message}")
                false
            }
        }
    }

    override suspend fun completeMission(taskId: String): Boolean {
        return withContext(Dispatchers.IO) {
            try {
                val response = client.post("$PAN_API_URL/agent/missions/$taskId/complete") {
                    attachAgentSignature()
                    contentType(ContentType.Application.Json)
                    setBody(
                        MissionCompletePayload(
                            agent_id = secureUid,
                            netPayout = 0.0,
                            evidence_urls = emptyList(),
                            hardware_attestation_token = "dev-bypass"
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

    override suspend fun registerHardwareKey(agentId: String, publicKeyB64: String, playIntegrityToken: String): Result<String> =
        Result.failure(Exception("Not implemented in PanApiClient"))

    fun close() = client.close()
}