package com.pan.tactical.network

import android.graphics.Bitmap
import android.util.Log
import com.google.firebase.auth.FirebaseAuth
import com.pan.tactical.BuildConfig
import com.pan.tactical.models.MissionData
import com.pan.tactical.security.StrongBoxManager
import com.pan.tactical.ui.WalletNetworkClient
import com.pan.tactical.ui.WalletResponse
import io.ktor.client.*
import io.ktor.client.call.*
import io.ktor.client.engine.okhttp.*
import io.ktor.client.plugins.contentnegotiation.*
import io.ktor.client.request.*
import io.ktor.client.request.forms.*
import io.ktor.client.statement.*
import io.ktor.http.*
import io.ktor.serialization.kotlinx.json.*
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json
import com.google.android.gms.maps.model.LatLng
import java.io.ByteArrayOutputStream
import java.util.concurrent.TimeUnit

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
data class V2XDistressPayload(
    val vin: String,

    @SerialName("fault_code")
    val faultCode: String,

    val latitude: Double,
    val longitude: Double,

    @SerialName("bounty_usd")
    val bountyUsd: Double,

    val timestamp: Long,

    // Intersection string displayed to agent on the mission alert overlay
    val intersection: String = "Unknown Location"
)

@Serializable
data class TelemetryPayload(
    @SerialName("agent_id")
    val agentId: String,

    val latitude: Double,
    val longitude: Double,
    val status: String
)

@Serializable
data class MissionCompletePayload(
    @SerialName("agent_id")
    val agentId: String,

    @SerialName("net_payout")
    val netPayout: Double,

    @SerialName("evidence_urls")
    val evidenceUrls: List<String>,

    @SerialName("hardware_attestation_token")
    val hardwareAttestationToken: String
)

@Serializable
data class SentryExtensionPayload(
    @SerialName("task_id")
    val taskId: String,

    @SerialName("extension_minutes")
    val extensionMinutes: Int,

    @SerialName("accepted_bounty_usd")
    val acceptedBountyUsd: Double
)

@Serializable
data class FcmTokenPayload(
    @SerialName("agent_id")
    val agentId: String,

    @SerialName("fcm_token")
    val fcmToken: String
)

@Serializable
data class DeclinePayload(
    val reason: String
)

@Serializable
data class PresencePayload(
    @SerialName("is_online")
    val isOnline: Boolean
)

class PanApiClient : WalletNetworkClient {

    companion object {
        private const val TAG = "PanApiClient"
    }

    private val client = HttpClient(OkHttp) {
        engine {
            config {
                connectTimeout(3, TimeUnit.SECONDS)
                readTimeout(3, TimeUnit.SECONDS)
                writeTimeout(30, TimeUnit.SECONDS)
            }
        }
        install(ContentNegotiation) {
            json(Json { ignoreUnknownKeys = true; prettyPrint = true })
        }
    }

    // 🟢 PILOT BYPASS: Hardcode hostUrl to the PC's local IP Address
    // private val hostUrl = BuildConfig.PAN_API_BASE_URL
    private val hostUrl = "http://192.168.0.84:5001"
    private val PAN_API_URL = "$hostUrl/api/v1"

    private val strongBoxManager = StrongBoxManager()
    private val attestationEngine = com.pan.tactical.security.AttestationEngine()

    private val secureUid: String?
        //get() = FirebaseAuth.getInstance().currentUser?.uid
        get() = "VNG-50-PILOT"

    private var cachedJwt: String? = null
    private var jwtExpiresAt: Long = 0L

    private val jwtMutex = Mutex()

    private suspend fun getFreshJwt(): String? {
        val uid = secureUid ?: run { Log.e(TAG, "Agent identity missing"); return null }

        jwtMutex.withLock {
            val now = System.currentTimeMillis() / 1000
            if (cachedJwt == null || now >= jwtExpiresAt - 30) {
                cachedJwt = strongBoxManager.generateJwt(uid)
                jwtExpiresAt = now + 300
            }
            return cachedJwt
        }
    }

    suspend fun registerFcmToken(token: String): Boolean {
        return withContext(Dispatchers.IO) {
            try {
                val uid = secureUid ?: run { Log.e(TAG, "Agent identity missing"); return@withContext false }
                val jwt = getFreshJwt() ?: return@withContext false

                val response = client.post("$PAN_API_URL/agent/fcm-token") {
                    header("Authorization", "Bearer $jwt")
                    contentType(ContentType.Application.Json)
                    setBody(
                        FcmTokenPayload(
                            agentId = uid,
                            fcmToken = token
                        )
                    )
                }
                response.status.isSuccess()
            } catch (e: Exception) {
                Log.e(TAG, "Failed to register FCM token: ${e.message}", e)
                false
            }
        }
    }

    override suspend fun triggerBackendDispatch(lat: Double, lon: Double, errorCode: String, intersection: String): Boolean {
        return withContext(Dispatchers.IO) {
            try {
                val jwt = getFreshJwt() ?: return@withContext false

                Log.i(TAG, "🚀 Injecting V2X Distress Signal via Dev Endpoint...")
                // 🟢 FIX: Use the agent-authenticated dev endpoint instead of the production
                // fleet endpoint. No fake X-Fleet-Id or sk_test_ token needed.
                val response: HttpResponse = client.post("$PAN_API_URL/dev/inject-distress") {
                    header("Authorization", "Bearer $jwt")
                    contentType(ContentType.Application.Json)
                    setBody(V2XDistressPayload(
                        vin = "DEV-VIN-${(Math.random() * 1000).toInt()}",
                        faultCode = errorCode,
                        latitude = lat,
                        longitude = lon,
                        bountyUsd = 25.00,
                        timestamp = System.currentTimeMillis() / 1000,
                        intersection = intersection
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
                secureUid ?: run { Log.e(TAG, "Agent identity missing"); return@withContext false }
                val jwt = getFreshJwt() ?: return@withContext false

                val statusString = if (isOnline) "ONLINE" else "OFFLINE"
                val payloadToSign = "${statusString}_${lat}_${lon}_${radiusMiles}"
                val nonce = android.util.Base64.encodeToString(
                    payloadToSign.toByteArray(),
                    android.util.Base64.URL_SAFE or android.util.Base64.NO_WRAP
                )

                val hardwareToken = attestationEngine.generateHardwareToken(context, nonce)

                val requestBody = StatusUpdateRequest(
                    status = statusString,
                    latitude = lat,
                    longitude = lon,
                    radius = radiusMiles,
                    loadout = loadout,
                    signature = hardwareToken,
                    timestamp = System.currentTimeMillis() / 1000
                )

                val response: HttpResponse =
                    client.post("$PAN_API_URL/agent/status") {
                        header("Authorization", "Bearer $jwt")
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

    // 🛡️ FIX: Added override modifier to satisfy the WalletNetworkClient interface
    override suspend fun updatePresence(isOnline: Boolean): Boolean {
        return withContext(Dispatchers.IO) {
            try {
                val jwt = getFreshJwt() ?: return@withContext false
                val response: HttpResponse = client.post("$PAN_API_URL/agent/presence") {
                    contentType(ContentType.Application.Json)
                    header("Authorization", "Bearer $jwt")
                    setBody(PresencePayload(isOnline = isOnline))
                }
                response.status.isSuccess()
            } catch (e: Exception) {
                Log.e(TAG, "Failed to update presence: ${e.message}", e)
                false
            }
        }
    }

    override suspend fun updateLocationTelemetry(lat: Double, lon: Double): Boolean {
        return withContext(Dispatchers.IO) {
            try {
                val uid = secureUid ?: run { Log.e(TAG, "Agent identity missing"); return@withContext false }
                val jwt = getFreshJwt() ?: return@withContext false

                val response: HttpResponse = client.post("$PAN_API_URL/telemetry/ingest") {
                    contentType(ContentType.Application.Json)
                    header("Authorization", "Bearer $jwt")
                    setBody(TelemetryPayload(
                        agentId = uid,
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

    suspend fun getTacticalRoute(
        startLat: Double,
        startLon: Double,
        endLat: Double,
        endLon: Double,
        mode: String = "driving"
    ): Pair<List<LatLng>, List<Triple<String, Double, Double>>> {
        return withContext(Dispatchers.IO) {
            try {
                val osrmBase = BuildConfig.OSRM_BASE_URL
                val urlString = "$osrmBase/route/v1/$mode/$startLon,$startLat;$endLon,$endLat?overview=full&geometries=geojson&steps=true"
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

            // 🛡️ FIXED: Catch missing JWT cleanly with logs rather than silently failing
            val jwt = getFreshJwt() ?: run {
                Log.e(TAG, "Evidence upload aborted: JWT unavailable. Agent identity missing.")
                return@withContext uploadedUrls
            }

            bitmaps.forEach { bitmap ->
                try {
                    val redactedBitmap = com.pan.tactical.security.PrivacyFilter.sanitizeImage(bitmap)
                    val stream = ByteArrayOutputStream()
                    redactedBitmap.compress(Bitmap.CompressFormat.JPEG, 70, stream)

                    val byteArray = stream.toByteArray()

                    // 🛡️ FIXED: Prevent memory leak of 1280x1280 ARGB bitmaps
                    redactedBitmap.recycle()

                    Log.d(TAG, "Uploading encrypted evidence: ${byteArray.size / 1024}KB")

                    val response: HttpResponse = client.post("$PAN_API_URL/agent/evidence/upload") {
                        header("Authorization", "Bearer $jwt")
                        setBody(MultiPartFormDataContent(
                            formData {
                                append("evidence_file", byteArray, Headers.build {
                                    append(HttpHeaders.ContentType, "image/jpeg")
                                    append(HttpHeaders.ContentDisposition, "filename=\"evidence_${System.currentTimeMillis()}.jpg\"")
                                })
                            }
                        ))
                    }

                    if (response.status.isSuccess()) {
                        val responseBody = response.bodyAsText()
                        val json = org.json.JSONObject(responseBody)
                        val downloadUrl = json.optString("url", "")
                        if (downloadUrl.isNotEmpty()) uploadedUrls.add(downloadUrl)
                    } else {
                        Log.e(TAG, "Backend rejected evidence upload. HTTP Status: ${response.status.value}")
                    }
                } catch (e: Exception) {
                    Log.e(TAG, "Failed to upload evidence bitmap: ${e.message}", e)
                }
            }
            uploadedUrls
        }
    }

    // --- SPLIT-BRAIN GUARDRAILS ---

    override suspend fun getWalletData(): WalletResponse? {
        Log.e(TAG, "🛑 CRITICAL: Legacy Firebase wallet access attempted. Injection error: PanApiClient does not support secure ledger operations. Use PanWalletClient.")
        return null
    }

    override suspend fun linkDebitCard(cardNumber: String): Result<String> {
        Log.e(TAG, "🛑 CRITICAL: Legacy Firebase wallet access attempted. Injection error.")
        return Result.failure(IllegalStateException("MIGRATION_ERROR: Use PanWalletClient for secure ledger operations."))
    }

    override suspend fun withdrawFunds(amount: Double): Result<String> {
        Log.e(TAG, "🛑 CRITICAL: Legacy Firebase wallet access attempted. Injection error.")
        return Result.failure(IllegalStateException("MIGRATION_ERROR: Use PanWalletClient for secure ledger operations."))
    }

    // -------------------------------

    override suspend fun fetchActiveMissions(): List<MissionData> {
        return withContext(Dispatchers.IO) {
            try {
                val jwt = getFreshJwt() ?: return@withContext emptyList()
                val response = client.get("$PAN_API_URL/agent/missions") {
                    header("Authorization", "Bearer $jwt")
                }

                if (response.status.isSuccess()) {
                    response.body<List<MissionData>>()
                } else {
                    Log.w(TAG, "Fetch missions returned HTTP ${response.status.value}")
                    emptyList()
                }
            } catch (e: Exception) {
                Log.e(TAG, "Fetch missions failed: ${e.message}", e)
                emptyList()
            }
        }
    }

    override suspend fun acknowledgeMission(taskId: String): Boolean {
        return withContext(Dispatchers.IO) {
            try {
                val jwt = getFreshJwt() ?: return@withContext false
                val response = client.post("$PAN_API_URL/agent/missions/$taskId/ack") {
                    header("Authorization", "Bearer $jwt")
                }
                response.status.isSuccess()
            } catch (e: Exception) {
                Log.e(TAG, "ACK failed: ${e.message}", e)
                false
            }
        }
    }

    // 🛡️ FIX: Updated method signature to accept the optional reason parameter
    override suspend fun declineMission(taskId: String, reason: String?): Boolean {
        return withContext(Dispatchers.IO) {
            try {
                val jwt = getFreshJwt() ?: return@withContext false
                val finalReason = reason ?: "No reason provided"
                val response = client.post("$PAN_API_URL/agent/missions/$taskId/decline") {
                    header("Authorization", "Bearer $jwt")
                    contentType(ContentType.Application.Json)
                    setBody(DeclinePayload(finalReason))
                }
                response.status.isSuccess()
            } catch (e: Exception) {
                Log.e(TAG, "Decline failed: ${e.message}", e)
                false
            }
        }
    }

    override suspend fun completeMission(taskId: String, evidenceUrls: List<String>): Boolean {
        return withContext(Dispatchers.IO) {
            try {
                val uid = secureUid ?: run { Log.e(TAG, "Agent identity missing"); return@withContext false }
                val jwt = getFreshJwt() ?: return@withContext false

                val response = client.post("$PAN_API_URL/agent/missions/$taskId/complete") {
                    header("Authorization", "Bearer $jwt")
                    contentType(ContentType.Application.Json)
                    setBody(
                        MissionCompletePayload(
                            agentId = uid,
                            netPayout = 0.0, // Backend calculates payout from Redis task config — do not send client-side value
                            evidenceUrls = evidenceUrls,
                            hardwareAttestationToken = strongBoxManager.generateJwt(uid)
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

    // --- SENTRY OPERATIONS ---

    suspend fun acceptSentryExtension(taskId: String, extensionMinutes: Int, bountyUsd: Double): Boolean {
        return withContext(Dispatchers.IO) {
            try {
                val jwt = getFreshJwt() ?: return@withContext false
                val response = client.post("$PAN_API_URL/agent/missions/$taskId/extend") {
                    header("Authorization", "Bearer $jwt")
                    contentType(ContentType.Application.Json)
                    setBody(
                        SentryExtensionPayload(
                            taskId = taskId,
                            extensionMinutes = extensionMinutes,
                            acceptedBountyUsd = bountyUsd
                        )
                    )
                }
                response.status.isSuccess()
            } catch (e: Exception) {
                Log.e(TAG, "Failed to accept Sentry extension: ${e.message}", e)
                false
            }
        }
    }

    override suspend fun registerHardwareKey(agentId: String, publicKeyB64: String, playIntegrityToken: String): Result<String> =
        Result.failure(UnsupportedOperationException("Not implemented in PanApiClient"))

    // PanApiClient handles mission operations via HTTP. WebSocket listening is
    // owned exclusively by PanWalletClient. This stub satisfies the interface.
    override suspend fun listenForMissions(
        onMissionAssigned: (MissionData) -> Unit,
        onMissionCleared: () -> Unit
    ) {
        Log.e(TAG, "🛑 listenForMissions called on PanApiClient. Use PanWalletClient for WebSocket dispatch stream.")
    }

    fun close() = client.close()
}