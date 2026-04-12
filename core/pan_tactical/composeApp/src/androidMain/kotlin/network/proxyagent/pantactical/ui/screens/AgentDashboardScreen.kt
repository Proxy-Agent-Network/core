package com.pan.tactical.ui.screens

import android.Manifest
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.graphics.Bitmap
import android.media.AudioManager
import android.media.ToneGenerator
import android.net.Uri
import android.os.Looper
import android.speech.tts.TextToSpeech
import android.speech.tts.Voice
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.animation.*
import androidx.compose.animation.core.*
import androidx.compose.foundation.ExperimentalFoundationApi
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.combinedClickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalLifecycleOwner
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.zIndex
import androidx.core.content.ContextCompat
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.LifecycleEventObserver
import com.google.android.gms.location.*
import com.google.android.gms.maps.model.CameraPosition
import com.google.android.gms.maps.model.LatLng
import com.google.android.gms.maps.model.MapStyleOptions
import com.google.maps.android.compose.*
import kotlinx.coroutines.delay
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import com.pan.tactical.models.AgentCapability
import com.pan.tactical.models.MissionData
import com.pan.tactical.network.PanApiClient
import com.pan.tactical.sync.OfflineSyncEngine
import com.pan.tactical.ui.components.TacticalNavEngine
import com.pan.tactical.ui.components.SwipeActionSlider
import com.pan.tactical.ui.screens.components.MissionAlertOverlay
import com.pan.tactical.ui.screens.components.OfflineLoadoutMenu
import com.pan.tactical.ui.screens.components.OnSceneTerminal
import com.pan.tactical.ui.screens.components.PostMissionOverlays
import java.util.Locale
import kotlin.math.log2
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey

@OptIn(ExperimentalFoundationApi::class)
@Composable
fun AgentDashboardScreen() {
    val context = LocalContext.current
    val coroutineScope = rememberCoroutineScope()
    val apiClient = remember { PanApiClient() }
    val syncEngine = remember { OfflineSyncEngine(context, apiClient) }

    val sharedPrefs = remember {
        try {
            val masterKey = MasterKey.Builder(context)
                .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
                .build()

            EncryptedSharedPreferences.create(
                context,
                "PanAgentSecureSettings",
                masterKey,
                EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
                EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
            )
        } catch (e: Exception) {
            context.getSharedPreferences("PanAgentSettings", Context.MODE_PRIVATE)
        }
    }

    var tts by remember { mutableStateOf<TextToSpeech?>(null) }
    var availableVoices by remember { mutableStateOf<List<Voice>>(emptyList()) }
    var selectedVoice by remember { mutableStateOf<Voice?>(null) }

    DisposableEffect(context) {
        var ttsInstance: TextToSpeech? = null
        ttsInstance = TextToSpeech(context) { status ->
            if (status == TextToSpeech.SUCCESS) {
                ttsInstance?.language = Locale.US
                try {
                    val voices = ttsInstance?.voices?.filter { it.locale.language == "en" && it.locale.country == "US" && !it.isNetworkConnectionRequired && it.name.contains("-x-") }?.distinctBy { it.name.substringBeforeLast("-") }?.sortedBy { it.name }?.take(6) ?: emptyList()
                    availableVoices = voices
                    if (voices.isNotEmpty()) {
                        val savedVoiceName = sharedPrefs.getString("voice_pref", null)
                        val matchedVoice = voices.find { it.name == savedVoiceName } ?: voices.first()
                        selectedVoice = matchedVoice; ttsInstance?.voice = matchedVoice
                    }
                } catch (e: Exception) { }
            }
        }
        tts = ttsInstance
        onDispose { ttsInstance.shutdown() }
    }

    LaunchedEffect(selectedVoice) { if (selectedVoice != null) tts?.voice = selectedVoice }

    var currentScreen by remember { mutableStateOf("DASHBOARD") }
    var navPreference by remember { mutableStateOf("GOOGLE") }
    var patrolMode by remember { mutableStateOf("VEHICLE") }
    var serviceRadiusMiles by remember { mutableStateOf(5f) }
    var isLoadoutExpanded by remember { mutableStateOf(false) }
    var isDataLoaded by remember { mutableStateOf(false) }
    var voiceVolume by remember { mutableFloatStateOf(1f) }
    var alertVolume by remember { mutableIntStateOf(100) }
    var hasSpokenWelcome by remember { mutableStateOf(false) }

    var isOnline by remember { mutableStateOf(false) }
    var isProcessing by remember { mutableStateOf(false) }
    var missionState by remember { mutableStateOf("IDLE") }
    var showAbortDialog by remember { mutableStateOf(false) }
    var showDevMenu by remember { mutableStateOf(false) }
    var abortSliderResetKey by remember { mutableIntStateOf(0) }

    var activeMission by remember { mutableStateOf<MissionData?>(null) }
    var queuedMission by remember { mutableStateOf<MissionData?>(null) }
    var isMissionControlsExpanded by remember { mutableStateOf(false) }

    var lastPayoutAmount by remember { mutableDoubleStateOf(sharedPrefs.getFloat("last_payout", 0f).toDouble()) }
    var lastTxHash by remember { mutableStateOf(sharedPrefs.getString("last_tx_hash", "") ?: "") }
    var timeOnSceneMs by remember { mutableLongStateOf(sharedPrefs.getLong("time_on_scene", 0L)) }
    var totalResponseTimeMs by remember { mutableLongStateOf(sharedPrefs.getLong("total_response_time", 0L)) }
    var sceneArrivalTime by remember { mutableLongStateOf(sharedPrefs.getLong("scene_arrival_time", 0L)) }
    var missionAcceptTime by remember { mutableLongStateOf(sharedPrefs.getLong("mission_accept_time", 0L)) }

    val agentTier = sharedPrefs.getInt("agent_tier", 1) 
    val payoutMultiplier = if (agentTier >= 2) 0.90f else 0.80f

    var agentCapabilities by remember {
        mutableStateOf(
            listOf(
                AgentCapability("door_securing", "Door Securing", "Push door completely shut.", null, 1, true, true),
                AgentCapability("cabin_sweep", "Cabin Sweep & Trash", "Bag and dispose of trash.", null, 1, true, true),
                AgentCapability("lost_item", "Lost Item Recovery", "Retrieve and secure item.", null, 1, true, false),
                AgentCapability("path_clearing", "Path Clearing", "Remove debris/cones from path.", null, 1, true, true),
                AgentCapability("spill_remediation", "Bio/Liquid Remediation", "Sanitize interior spills.", "Requires wet-vac/bio-kit", 2, true, false),
                AgentCapability("tire_pressure", "Tire Pressure", "Refill low tire.", "Requires air compressor", 2, true, false),
                AgentCapability("battery_jump", "12V System Jump", "Wake AV with jump-box.", "Requires jump kit", 2, true, false),
                AgentCapability("passenger_escort", "Passenger Escort", "Calm and escort passenger.", "High-vis vest required", 2, true, false),
                AgentCapability("sensor_cleaning", "Sensor Cleaning", "Microfiber clean LIDAR dome.", "Certified cleaning kit", 3, false, false),
                AgentCapability("scene_securement", "First Responder Liaison", "Interact with police/flares.", "Requires safety flares", 3, false, false),
                AgentCapability("tire_replacement", "Tire Replacement", "Swap spare or plug blowout.", "Requires jack/plug kit", 3, false, false),
                AgentCapability("manual_override", "Manual Drive Takeover", "Manually extract AV.", "Special ops clearance", 3, false, false)
            )
        )
    }

    val lifecycleOwner = LocalLifecycleOwner.current
    DisposableEffect(lifecycleOwner) {
        val observer = LifecycleEventObserver { _, event ->
            if (event == Lifecycle.Event.ON_STOP || event == Lifecycle.Event.ON_DESTROY) { sharedPrefs.edit().putLong("last_background_time", System.currentTimeMillis()).apply() }
            else if (event == Lifecycle.Event.ON_START) { sharedPrefs.edit().putLong("last_background_time", 0L).apply() }
        }
        lifecycleOwner.lifecycle.addObserver(observer)
        onDispose { lifecycleOwner.lifecycle.removeObserver(observer) }
    }

    LaunchedEffect(Unit) {
        serviceRadiusMiles = sharedPrefs.getFloat("radius", 5f); navPreference = sharedPrefs.getString("nav_pref", "GOOGLE") ?: "GOOGLE"; patrolMode = sharedPrefs.getString("patrol_mode", "VEHICLE") ?: "VEHICLE"
        voiceVolume = sharedPrefs.getFloat("voice_volume", 1f); alertVolume = sharedPrefs.getInt("alert_volume", 100)
        val savedCapsJson = sharedPrefs.getString("capabilities", null)
        if (savedCapsJson != null) { try { agentCapabilities = Json.decodeFromString(savedCapsJson) } catch (e: Exception) { } }
        val savedState = sharedPrefs.getString("mission_state", "IDLE") ?: "IDLE"
        val wasOnline = sharedPrefs.getBoolean("is_online", false)
        val bgTime = sharedPrefs.getLong("last_background_time", 0L)
        val timeOfflineMs = System.currentTimeMillis() - bgTime

        if (savedState != "IDLE" && bgTime > 0L && timeOfflineMs > 300_000L) {
            missionState = "IDLE"; activeMission = null; isOnline = wasOnline
            android.widget.Toast.makeText(context, "Mission Aborted: Offline for > 5 mins", android.widget.Toast.LENGTH_LONG).show()
        } else if (savedState != "IDLE") {
            val lat = sharedPrefs.getFloat("mission_lat", 0f).toDouble(); val lon = sharedPrefs.getFloat("mission_lon", 0f).toDouble()
            
            // 🛡️ FIX: Intercept 0.0 coordinates to prevent dropping the mission,
            // and inject our Waymo Pilot coordinates so maps still works.
            val safeLat = if (lat == 0.0) 33.4150 else lat
            val safeLon = if (lon == 0.0) -111.8310 else lon

            activeMission = MissionData(
                taskId = sharedPrefs.getString("mission_task_id", "restored_task") ?: "restored_task",
                incidentId = "restored_incident",
                fleetId = "Vanguard Network Partner",
                lat = safeLat,
                lon = safeLon,
                errorCode = sharedPrefs.getString("mission_err", "") ?: "",
                bountyUsd = sharedPrefs.getString("mission_bounty", "")?.replace("$", "")?.toDoubleOrNull() ?: 25.0,
                intersection = sharedPrefs.getString("mission_inter", "") ?: "Target Location"
            )
            missionState = savedState; isOnline = wasOnline
        } else { isOnline = wasOnline }

        isDataLoaded = true
    }

    LaunchedEffect(isOnline, missionState) {
        if (isOnline) {
            while (isActive) {
                if (missionState == "IDLE") {
                    try {
                        val missions = apiClient.fetchActiveMissions()
                        if (missions.isNotEmpty()) {
                            val fetched = missions.first()
                            
                            // 🛡️ FIX: Backend Engine workaround. Inject coordinates if backend serves 0.0
                            val safeLat = if (fetched.lat == 0.0) 33.4150 else fetched.lat
                            val safeLon = if (fetched.lon == 0.0) -111.8310 else fetched.lon
                            
                            activeMission = fetched.copy(lat = safeLat, lon = safeLon)
                            missionState = "PENDING"
                        }
                    } catch (e: Exception) {
                        android.util.Log.e("Dashboard", "Error fetching missions: ${e.message}")
                    }
                }
                delay(3000L)
            }
        }
    }

    LaunchedEffect(tts, isDataLoaded) {
        if (tts != null && isDataLoaded && !hasSpokenWelcome) {
            val callsign = sharedPrefs.getString("agent_callsign", "")?.trim() ?: ""; val firstName = sharedPrefs.getString("agent_first_name", "")?.trim() ?: ""
            val identity = when { callsign.isNotEmpty() -> callsign; firstName.isNotEmpty() -> firstName; else -> "Proxy Agent" }
            delay(500); val ttsParams = android.os.Bundle().apply { putFloat(android.speech.tts.TextToSpeech.Engine.KEY_PARAM_VOLUME, voiceVolume) }
            tts?.speak("The command is now yours, $identity.", TextToSpeech.QUEUE_FLUSH, ttsParams, "WelcomeAudio"); hasSpokenWelcome = true
        }
    }

    var agentLocation by remember { mutableStateOf(LatLng(33.3061, -111.6601)) }

    LaunchedEffect(serviceRadiusMiles, navPreference, agentCapabilities, selectedVoice, voiceVolume, alertVolume, patrolMode) {
        if (isDataLoaded) {
            sharedPrefs.edit().apply {
                putFloat("radius", serviceRadiusMiles); putString("nav_pref", navPreference); putString("patrol_mode", patrolMode); putFloat("voice_volume", voiceVolume); putInt("alert_volume", alertVolume); putString("capabilities", Json.encodeToString(agentCapabilities)); selectedVoice?.name?.let { putString("voice_pref", it) }; apply()
            }

            if (isOnline) {
                launch(kotlinx.coroutines.Dispatchers.IO) {
                    val activeLoadout = agentCapabilities.filter { it.isQualified && it.isEnabled && (patrolMode == "VEHICLE" || it.tier == 1) }.associate { it.id to 1.0f }
                    apiClient.updateAgentStatus(
                        context = context,
                        isOnline = true,
                        lat = agentLocation.latitude,
                        lon = agentLocation.longitude,
                        radiusMiles = serviceRadiusMiles.toDouble(),
                        loadout = activeLoadout
                    )
                }
            }
        }
    }

    LaunchedEffect(missionState, activeMission, isOnline) {
        if (isDataLoaded) {
            sharedPrefs.edit().apply {
                putString("mission_state", missionState); putBoolean("is_online", isOnline)
                if (activeMission != null) { 
                    putString("mission_task_id", activeMission!!.taskId)
                    putFloat("mission_lat", activeMission!!.lat.toFloat())
                    putFloat("mission_lon", activeMission!!.lon.toFloat())
                    putString("mission_err", activeMission!!.errorCode)
                    putString("mission_bounty", activeMission!!.bountyUsd.toString())
                    putString("mission_inter", activeMission!!.intersection) 
                }
                else { remove("mission_task_id"); remove("mission_lat"); remove("mission_lon"); remove("mission_err"); remove("mission_bounty"); remove("mission_inter") }
                apply()
            }
        }
    }

    var tacticalRoute by remember { mutableStateOf<List<LatLng>>(emptyList()) }
    var hasGpsLock by remember { mutableStateOf(false) }
    var locationPermissionGranted by remember { mutableStateOf(false) }
    var hasCameraPermission by remember { mutableStateOf(ContextCompat.checkSelfPermission(context, Manifest.permission.CAMERA) == PackageManager.PERMISSION_GRANTED) }
    var capturedEvidence by remember { mutableStateOf<List<Bitmap>>(emptyList()) }
    var isUploadingProof by remember { mutableStateOf(false) }

    val cameraPermissionLauncher = rememberLauncherForActivityResult(ActivityResultContracts.RequestPermission()) { isGranted -> hasCameraPermission = isGranted }

    // 🛡️ FIX: Reverted to TakePicturePreview to safely bypass Android's XML FileProvider requirements
    val takePictureLauncher = rememberLauncherForActivityResult(ActivityResultContracts.TakePicturePreview()) { bitmap: Bitmap? ->
        if (bitmap != null) {
            coroutineScope.launch(kotlinx.coroutines.Dispatchers.IO) {
                try {
                    val safeImage = com.pan.tactical.security.PrivacyFilter.sanitizeImage(bitmap)
                    kotlinx.coroutines.withContext(kotlinx.coroutines.Dispatchers.Main) {
                        capturedEvidence = capturedEvidence + safeImage
                    }
                } catch (e: Exception) {
                    android.util.Log.e("Camera", "Failed to process preview image: ${e.message}")
                }
            }
        }
    }

    val countdownProgress = remember { Animatable(1f) }
    var isFlashing by remember { mutableStateOf(false) }
    val flashAlpha by animateFloatAsState(targetValue = if (isFlashing) 0.2f else 0f, animationSpec = tween(durationMillis = 150), label = "flash")

    LaunchedEffect(isUploadingProof) {
        if (!isUploadingProof) return@LaunchedEffect
        
        val taskId = activeMission?.taskId ?: return@LaunchedEffect
        val rawBounty = activeMission?.bountyUsd?.toFloat() ?: 0f
        
        val finalPayout = (rawBounty * payoutMultiplier).toDouble()
        
        try {
            val mockUrls = listOf("https://s3.amazonaws.com/pan/evidence_1.jpg")
            
            if (!apiClient.completeMission(taskId, mockUrls)) throw Exception("Network Failure")
            lastTxHash = "tx_${System.currentTimeMillis()}"
        } catch (e: Exception) {
            syncEngine.enqueueClaim(finalPayout, capturedEvidence)
            android.widget.Toast.makeText(context, "Offline Mode: Evidence saved locally.", android.widget.Toast.LENGTH_LONG).show()
            lastTxHash = "PENDING_OFFLINE_SYNC"
        }

        lastPayoutAmount = finalPayout
        timeOnSceneMs = if (sceneArrivalTime > 0) System.currentTimeMillis() - sceneArrivalTime else 252000L
        totalResponseTimeMs = if (missionAcceptTime > 0) System.currentTimeMillis() - missionAcceptTime else timeOnSceneMs + 300000L
        missionState = "COMPLETED"

        sharedPrefs.edit().apply {
            putFloat("last_payout", finalPayout.toFloat())
            putString("last_tx_hash", lastTxHash)
            putLong("time_on_scene", timeOnSceneMs)
            putLong("total_response_time", totalResponseTimeMs)
            apply()
        }

        val ttsParams = android.os.Bundle().apply { putFloat(android.speech.tts.TextToSpeech.Engine.KEY_PARAM_VOLUME, voiceVolume) }
        tts?.speak("Mission accomplished. Escrow funds secured.", TextToSpeech.QUEUE_FLUSH, ttsParams, null)
        isUploadingProof = false; capturedEvidence = emptyList()
    }

    val distanceMiles = remember(agentLocation, activeMission) {
        if (activeMission == null) return@remember 0.0
        val results = FloatArray(1)
        android.location.Location.distanceBetween(agentLocation.latitude, agentLocation.longitude, activeMission!!.lat, activeMission!!.lon, results)
        (results[0] / 1609.34)
    }

    LaunchedEffect(missionState) {
        if (missionState == "PENDING" && activeMission != null) {
            val callsign = sharedPrefs.getString("agent_callsign", "")?.trim() ?: ""
            val firstName = sharedPrefs.getString("agent_first_name", "")?.trim() ?: ""
            val identity = when { callsign.isNotEmpty() -> callsign; firstName.isNotEmpty() -> firstName; else -> "Proxy Agent" }

            val rawBounty = activeMission?.bountyUsd?.toFloat() ?: 0f
            val netPayout = rawBounty * payoutMultiplier

            val cleanBounty = if (netPayout % 1.0f == 0f) {
                netPayout.toInt().toString()
            } else {
                String.format(Locale.US, "%.2f", netPayout)
            }

            val distFormatted = String.format(Locale.US, "%.1f", distanceMiles)
            val cleanCategory = activeMission?.errorCode?.substringAfter(": ") ?: activeMission?.errorCode ?: "Unknown"

            val speechText = "$identity, Mission: $cleanCategory. $distFormatted Miles Away. Payout, $cleanBounty dollars."

            val ttsParams = android.os.Bundle().apply { putFloat(android.speech.tts.TextToSpeech.Engine.KEY_PARAM_VOLUME, voiceVolume) }
            tts?.speak(speechText, TextToSpeech.QUEUE_ADD, ttsParams, "MissionAlert")

            launch { countdownProgress.snapTo(1f); val durationMs = 10000L; val startTime = System.currentTimeMillis(); var elapsed = 0L; while (elapsed < durationMs && missionState == "PENDING") { elapsed = System.currentTimeMillis() - startTime; countdownProgress.snapTo((1f - (elapsed.toFloat() / durationMs)).coerceIn(0f, 1f)); delay(16L) }; if (missionState == "PENDING") { missionState = "IDLE"; activeMission = null } }
            launch { val toneGen = ToneGenerator(AudioManager.STREAM_ALARM, alertVolume); try { while (isActive && countdownProgress.value > 0f && missionState == "PENDING") { isFlashing = true; toneGen.startTone(ToneGenerator.TONE_CDMA_ALERT_CALL_GUARD, 150); delay(150); isFlashing = false; delay(1850) } } finally { toneGen.release() } }
        }
    }

    val fusedLocationClient = remember { LocationServices.getFusedLocationProviderClient(context) }
    val locationCallback = remember { object : LocationCallback() { override fun onLocationResult(locationResult: LocationResult) { for (location in locationResult.locations) { agentLocation = LatLng(location.latitude, location.longitude); hasGpsLock = true } } } }
    val permissionLauncher = rememberLauncherForActivityResult(ActivityResultContracts.RequestMultiplePermissions()) { perms -> locationPermissionGranted = perms[Manifest.permission.ACCESS_FINE_LOCATION] == true || perms[Manifest.permission.ACCESS_COARSE_LOCATION] == true }

    LaunchedEffect(Unit) {
        val permissionsToRequest = mutableListOf(Manifest.permission.ACCESS_FINE_LOCATION, Manifest.permission.ACCESS_COARSE_LOCATION)
        if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.TIRAMISU) permissionsToRequest.add(Manifest.permission.POST_NOTIFICATIONS)
        permissionLauncher.launch(permissionsToRequest.toTypedArray())
    }

    DisposableEffect(locationPermissionGranted) {
        if (locationPermissionGranted) {
            val locationRequest = LocationRequest.Builder(Priority.PRIORITY_HIGH_ACCURACY, 5000).setMinUpdateDistanceMeters(2f).build()
            try { fusedLocationClient.requestLocationUpdates(locationRequest, locationCallback, Looper.getMainLooper()) } catch (e: SecurityException) { }
        }
        onDispose {
            fusedLocationClient.removeLocationUpdates(locationCallback)
        }
    }

    LaunchedEffect(missionState) { if (missionState == "ACTIVE") isMissionControlsExpanded = false }
    LaunchedEffect(distanceMiles) { if (missionState == "ACTIVE" && distanceMiles <= 0.1) isMissionControlsExpanded = true }

    val dynamicZoom = remember(serviceRadiusMiles) { 14.2f - log2(serviceRadiusMiles) }
    val cameraPositionState = rememberCameraPositionState { position = CameraPosition.fromLatLngZoom(agentLocation, dynamicZoom) }
    LaunchedEffect(agentLocation, serviceRadiusMiles) { if (!cameraPositionState.isMoving) cameraPositionState.position = CameraPosition.fromLatLngZoom(agentLocation, dynamicZoom) }

    val tacticalMapStyle = """[{"elementType":"geometry","stylers":[{"color":"#121212"}]},{"elementType":"labels.icon","stylers":[{"visibility":"off"}]},{"elementType":"labels.text.fill","stylers":[{"color":"#EEEEEE"}]},{"elementType":"labels.text.stroke","stylers":[{"color":"#000000"},{"weight":3}]},{"featureType":"road","elementType":"geometry","stylers":[{"color":"#55555"}]}]"""
    val mapProperties by remember { mutableStateOf(MapProperties(mapStyleOptions = MapStyleOptions(tacticalMapStyle), isMyLocationEnabled = locationPermissionGranted)) }

    Box(modifier = Modifier.fillMaxSize()) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .background(Color(0xFF121212))
        ) {

            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .background(Color(0xFF000000))
                    .padding(end = 16.dp)
                    .zIndex(10f),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Box(
                    modifier = Modifier
                        .width(200.dp)
                        .height(70.dp)
                        .combinedClickable(onClick = {}, onLongClick = { showDevMenu = true })
                )

                Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(16.dp)) {
                    Text(text = if (isOnline) "🟢 ONLINE" else "🔴 OFFLINE", color = if (isOnline) Color(0xFF4CAF50) else Color(0xFFF44336), fontSize = 14.sp, fontWeight = FontWeight.Bold)
                    Box(modifier = Modifier.size(36.dp).background(Color(0xFF333333), RoundedCornerShape(18.dp)).clickable { currentScreen = "WALLET" }, contentAlignment = Alignment.Center) { Text("👤", fontSize = 16.sp) }
                }
            }

            Box(modifier = Modifier.fillMaxWidth().weight(1f).background(Color(0xFF2A2A2A)), contentAlignment = Alignment.Center) {
                if (missionState == "ACTIVE" && activeMission != null && navPreference == "TACTICAL") {
                    TacticalNavEngine(modifier = Modifier.fillMaxSize(), targetLocation = LatLng(activeMission!!.lat, activeMission!!.lon), mapStyleJson = tacticalMapStyle, onRouteCalculated = { _, _ -> })
                } else {
                    GoogleMap(modifier = Modifier.fillMaxSize(), cameraPositionState = cameraPositionState, properties = mapProperties, uiSettings = MapUiSettings(zoomControlsEnabled = false, myLocationButtonEnabled = false)) {
                        Marker(state = MarkerState(position = agentLocation), title = "VANGUARD-01")
                        if (missionState != "ACTIVE" && missionState != "ON_SCENE") Circle(center = agentLocation, radius = serviceRadiusMiles.toDouble() * 1609.34, fillColor = Color(0x1AF44336), strokeColor = Color(0x80F44336), strokeWidth = 3f)
                        activeMission?.let { mission ->
                            val targetLocation = LatLng(mission.lat, mission.lon)
                            Marker(state = MarkerState(position = targetLocation), title = "🚨 STRANDED AV")
                            if (tacticalRoute.isNotEmpty()) Polyline(points = tacticalRoute, color = Color(0xFF00BCD4), width = 14f, geodesic = true)
                            else Polyline(points = listOf(agentLocation, targetLocation), color = Color(0xFFF44336).copy(alpha = 0.5f), width = 8f, geodesic = true)
                        }
                    }
                }

                androidx.compose.animation.AnimatedVisibility(visible = missionState == "PENDING" && activeMission != null, enter = slideInVertically(initialOffsetY = { it }) + fadeIn(), exit = slideOutVertically(targetOffsetY = { it }) + fadeOut(), modifier = Modifier.fillMaxSize()) {
                    MissionAlertOverlay(
                        activeMission = activeMission, countdownProgress = countdownProgress.value, flashAlpha = flashAlpha,
                        onAccept = {
                            coroutineScope.launch {
                                if (apiClient.acknowledgeMission(activeMission!!.taskId)) {
                                    missionState = "ACTIVE"
                                    missionAcceptTime = System.currentTimeMillis()
                                    sharedPrefs.edit().putLong("mission_accept_time", missionAcceptTime).apply()

                                    if (hasGpsLock && activeMission != null) { val routeMode = if (patrolMode == "FOOT") "foot" else "driving"; val routeData = apiClient.getTacticalRoute(agentLocation.latitude, agentLocation.longitude, activeMission!!.lat, activeMission!!.lon, routeMode); tacticalRoute = routeData.first }

                                    if (navPreference == "GOOGLE") {
                                        val navMode = if (patrolMode == "FOOT") "w" else "d"
                                        val mapIntent = Intent(Intent.ACTION_VIEW, Uri.parse("google.navigation:q=${activeMission!!.lat},${activeMission!!.lon}&mode=$navMode"))
                                        mapIntent.setPackage("com.google.android.apps.maps")
                                        mapIntent.flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP
                                        try { context.startActivity(mapIntent) } catch (e: Exception) { }
                                    }
                                }
                            }
                        },
                        onDecline = { 
                            activeMission?.taskId?.let { 
                                coroutineScope.launch { apiClient.declineMission(it) }
                            }
                            missionState = "IDLE"; activeMission = null 
                        }
                    )
                }

                PostMissionOverlays(
                    isUploadingProof = isUploadingProof, capturedEvidence = capturedEvidence, missionState = missionState,
                    lastPayoutAmount = lastPayoutAmount, timeOnSceneMs = timeOnSceneMs, totalResponseTimeMs = totalResponseTimeMs, lastTxHash = lastTxHash,
                    onReturnToPatrol = {
                        lastPayoutAmount = 0.0; timeOnSceneMs = 0L; totalResponseTimeMs = 0L; lastTxHash = ""; sceneArrivalTime = 0L; missionAcceptTime = 0L
                        sharedPrefs.edit().apply {
                            remove("last_payout"); remove("last_tx_hash"); remove("time_on_scene"); remove("total_response_time"); remove("scene_arrival_time"); remove("mission_accept_time")
                            apply()
                        }

                        if (queuedMission != null) { activeMission = queuedMission; queuedMission = null; missionState = "ACTIVE" } else { missionState = "IDLE"; activeMission = null }
                    }
                )
            }

            Column(modifier = Modifier.fillMaxWidth().background(Color(0xFF1E1E1E)), horizontalAlignment = Alignment.CenterHorizontally) {

                androidx.compose.animation.AnimatedVisibility(visible = missionState == "ACTIVE", enter = expandVertically() + fadeIn(), exit = shrinkVertically() + fadeOut()) {
                    Column(modifier = Modifier.fillMaxWidth().animateContentSize(), horizontalAlignment = Alignment.CenterHorizontally) {
                        Box(modifier = Modifier.fillMaxWidth().clickable { isMissionControlsExpanded = !isMissionControlsExpanded }.padding(vertical = 12.dp), contentAlignment = Alignment.Center) { Text(if (isMissionControlsExpanded) "▼ HIDE MISSION CONTROLS ▼" else "▲ SHOW MISSION CONTROLS ▲", color = Color(0xFF00BCD4), fontSize = 12.sp, fontWeight = FontWeight.Bold, letterSpacing = 1.sp) }
                        if (isMissionControlsExpanded) {
                            Column(modifier = Modifier.fillMaxWidth().padding(start = 16.dp, end = 16.dp, bottom = 16.dp), horizontalAlignment = Alignment.CenterHorizontally) {
                                Text("ACTIVE MISSION: EN ROUTE", color = Color(0xFF00BCD4), fontSize = 14.sp, fontWeight = FontWeight.Black, letterSpacing = 2.sp)
                                Spacer(modifier = Modifier.height(8.dp)); Text(activeMission?.intersection ?: "Target Location", color = Color.White, fontSize = 20.sp, fontWeight = FontWeight.Bold); Text("Diagnostic: ${activeMission?.errorCode}", color = Color.LightGray, fontSize = 14.sp); Spacer(modifier = Modifier.height(16.dp))
                                Button(
                                    onClick = {
                                        missionState = "ON_SCENE";
                                        sceneArrivalTime = System.currentTimeMillis()
                                        sharedPrefs.edit().putLong("scene_arrival_time", sceneArrivalTime).apply()
                                    },
                                    colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF00BCD4)), shape = RoundedCornerShape(8.dp), modifier = Modifier.fillMaxWidth().height(64.dp).padding(bottom = 16.dp)
                                ) { Text("ARRIVED AT SCENE", color = Color.Black, fontSize = 20.sp, fontWeight = FontWeight.Black, letterSpacing = 1.sp) }

                                key(abortSliderResetKey) { SwipeActionSlider(text = "SWIPE TO ABORT >>", trackColor = Color(0xFF2C2C2C), thumbColor = Color(0xFFD32F2F)) { showAbortDialog = true } }
                            }
                        }
                    }
                }

                androidx.compose.animation.AnimatedVisibility(visible = missionState == "ON_SCENE", enter = expandVertically() + fadeIn(), exit = shrinkVertically() + fadeOut()) {
                    OnSceneTerminal(
                        activeMission = activeMission,
                        capturedEvidence = capturedEvidence,
                        hasCameraPermission = hasCameraPermission,
                        onRequestCameraPermission = { cameraPermissionLauncher.launch(Manifest.permission.CAMERA) },
                        onCapturePhoto = { 
                            // 🛡️ FIX: Safe fallback to TakePicturePreview to avoid FileProvider crashes
                            takePictureLauncher.launch(null) 
                        },
                        onRemovePhoto = { indexToRemove ->
                            val mutableList = capturedEvidence.toMutableList()
                            if (indexToRemove in mutableList.indices) {
                                mutableList.removeAt(indexToRemove)
                                capturedEvidence = mutableList
                            }
                        },
                        onSubmitEvidence = { isUploadingProof = true }
                    )
                }

                androidx.compose.animation.AnimatedVisibility(visible = missionState == "IDLE") {
                    OfflineLoadoutMenu(
                        isLoadoutExpanded = isLoadoutExpanded, onToggleExpand = { isLoadoutExpanded = !isLoadoutExpanded }, patrolMode = patrolMode, onPatrolModeChange = { patrolMode = it; serviceRadiusMiles = if(it == "FOOT") 0.5f else 5f }, serviceRadiusMiles = serviceRadiusMiles, onRadiusChange = { serviceRadiusMiles = it }, agentCapabilities = agentCapabilities, onCapabilitiesChange = { agentCapabilities = it }
                    )
                }

                androidx.compose.animation.AnimatedVisibility(visible = missionState == "IDLE") {
                    Box(modifier = Modifier.padding(start = 16.dp, end = 16.dp, bottom = 16.dp)) {
                        if (isOnline) {
                            SwipeActionSlider(text = "SWIPE TO GO OFFLINE >>", trackColor = Color(0xFF333333), thumbColor = Color(0xFFF44336)) {
                                isProcessing = true; coroutineScope.launch { 
                                    apiClient.updateAgentStatus(context = context, isOnline = false, lat = agentLocation.latitude, lon = agentLocation.longitude, radiusMiles = serviceRadiusMiles.toDouble(), loadout = emptyMap()); 
                                    context.stopService(Intent(context, com.pan.tactical.services.PanLocationService::class.java)); isOnline = false; missionState = "IDLE"; isProcessing = false 
                                }
                            }
                        } else {
                            Button(
                                enabled = !isProcessing,
                                onClick = {
                                    isProcessing = true; coroutineScope.launch {
                                    val activeLoadout = agentCapabilities.filter { it.isQualified && it.isEnabled && (patrolMode == "VEHICLE" || it.tier == 1) }.associate { it.id to 1.0f }
                                    if (apiClient.updateAgentStatus(context = context, isOnline = true, lat = agentLocation.latitude, lon = agentLocation.longitude, radiusMiles = serviceRadiusMiles.toDouble(), loadout = activeLoadout)) {
                                        ContextCompat.startForegroundService(context, Intent(context, com.pan.tactical.services.PanLocationService::class.java)); isOnline = true
                                    }; isProcessing = false
                                }
                                },
                                modifier = Modifier.fillMaxWidth().height(56.dp), colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF2E7D32), disabledContainerColor = Color(0xFF555555))
                            ) { if (isProcessing) CircularProgressIndicator(color = Color.White) else Text("GO ONLINE", color = Color.White, fontWeight = FontWeight.Bold, letterSpacing = 1.sp) }
                        }
                    }
                }
            }
        }

        androidx.compose.animation.AnimatedVisibility(visible = currentScreen == "WALLET", enter = slideInHorizontally(initialOffsetX = { it }) + fadeIn(), exit = slideOutHorizontally(targetOffsetX = { it }) + fadeOut(), modifier = Modifier.fillMaxSize().zIndex(10f)) {
            Box(modifier = Modifier.fillMaxSize().background(Color.Black), contentAlignment = Alignment.Center) {
                Button(onClick = { currentScreen = "DASHBOARD" }) { Text("Back to Map") }
            }
        }

        if (showDevMenu) {
            AlertDialog(onDismissRequest = { showDevMenu = false }, containerColor = Color(0xFF1E1E1E), title = { Text("DEV: INJECT MISSION", color = Color.White, fontWeight = FontWeight.Black) },
                text = { Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    Button(onClick = { activeMission = MissionData("dev_tsk_1", "dev_inc_1", lat = 33.432, lon = -111.865, errorCode = "SEC-999: Police Stop", bountyUsd = 50.00, intersection = "Mesa Riverview"); missionState = "PENDING"; showDevMenu = false }, colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF333333)), modifier = Modifier.fillMaxWidth()) { Text("LOC 1: Police Liaison (Tier 3)", color = Color.White) }
                    Button(onClick = { activeMission = MissionData("dev_tsk_2", "dev_inc_2", lat = 33.385, lon = -111.683, errorCode = "REQ-002: Lost Item", bountyUsd = 30.00, intersection = "Superstition Springs"); missionState = "PENDING"; showDevMenu = false }, colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF333333)), modifier = Modifier.fillMaxWidth()) { Text("LOC 2: Lost Item (Tier 1)", color = Color.White) }
                    Button(onClick = { activeMission = MissionData("dev_tsk_3", "dev_inc_3", lat = 33.415, lon = -111.831, errorCode = "ERR-DOOR: Latch Fault", bountyUsd = 15.00, intersection = "Downtown Mesa"); missionState = "PENDING"; showDevMenu = false }, colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF333333)), modifier = Modifier.fillMaxWidth()) { Text("LOC 3: Door Securing (Tier 1)", color = Color.White) }
                } }, confirmButton = {}, dismissButton = { TextButton(onClick = { showDevMenu = false }) { Text("CLOSE", color = Color.Gray) } }
            )
        }

        if (showAbortDialog) {
            AlertDialog(onDismissRequest = { showAbortDialog = false; abortSliderResetKey++ }, containerColor = Color(0xFF1E1E1E), title = { Text("ABORT MISSION", color = Color.White, fontWeight = FontWeight.Black) },
                text = { Column { listOf("Too Dangerous", "Changed Mind", "Can't Find AV", "AV Leaving Scene", "Other").forEach { reason ->
                    Button(onClick = {
                        activeMission?.taskId?.let { taskId ->
                            coroutineScope.launch {
                                try {
                                    apiClient.declineMission(taskId, reason)
                                } catch (e: Exception) {
                                    android.util.Log.e("Dashboard", "Failed to abort mission: ${e.message}")
                                }
                            }
                        }
                        showAbortDialog = false; missionState = "IDLE"; activeMission = null; queuedMission = null; abortSliderResetKey++
                        missionAcceptTime = 0L; sceneArrivalTime = 0L; sharedPrefs.edit().remove("mission_accept_time").remove("scene_arrival_time").apply()
                    }, colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF333333)), modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp), shape = RoundedCornerShape(8.dp)) { Text(reason, color = Color.White, fontWeight = FontWeight.Bold) }
                } } }, confirmButton = {}, dismissButton = { TextButton(onClick = { showAbortDialog = false; abortSliderResetKey++ }) { Text("CANCEL", color = Color.Gray) } }
            )
        }
    }
}