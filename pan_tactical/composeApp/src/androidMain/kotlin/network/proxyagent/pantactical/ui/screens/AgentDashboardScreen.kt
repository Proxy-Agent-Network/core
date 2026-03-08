package network.proxyagent.pantactical.ui.screens

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
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.combinedClickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalLifecycleOwner
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.zIndex
import androidx.core.content.ContextCompat
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.LifecycleEventObserver
import kotlinx.coroutines.delay
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch

import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json

import network.proxyagent.pantactical.network.PanApiClient
import network.proxyagent.pantactical.models.AgentCapability
import network.proxyagent.pantactical.models.MissionData
import network.proxyagent.pantactical.ui.components.CapabilityCard
import network.proxyagent.pantactical.ui.components.TacticalNavEngine

import java.util.Locale
import kotlin.math.log2

import com.google.android.gms.location.*
import com.google.android.gms.maps.model.CameraPosition
import com.google.android.gms.maps.model.LatLng
import com.google.android.gms.maps.model.MapStyleOptions
import com.google.maps.android.compose.*

@Composable
fun AgentDashboardScreen() {
    var appState by remember { mutableStateOf("BOOT") }

    Crossfade(targetState = appState, animationSpec = tween(durationMillis = 800), label = "app_boot") { state ->
        when (state) {
            "BOOT" -> PanBootSequence(onBootComplete = { appState = "RUNNING" })
            "RUNNING" -> MainDashboardContent()
        }
    }
}

@OptIn(ExperimentalFoundationApi::class)
@Composable
fun MainDashboardContent() {
    val context = LocalContext.current
    val coroutineScope = rememberCoroutineScope()
    val apiClient = remember { PanApiClient() }

    val sharedPrefs = remember { context.getSharedPreferences("PanAgentSettings", Context.MODE_PRIVATE) }

    var tts by remember { mutableStateOf<TextToSpeech?>(null) }
    var availableVoices by remember { mutableStateOf<List<Voice>>(emptyList()) }
    var selectedVoice by remember { mutableStateOf<Voice?>(null) }

    DisposableEffect(context) {
        var ttsInstance: TextToSpeech? = null
        ttsInstance = TextToSpeech(context) { status ->
            if (status == TextToSpeech.SUCCESS) {
                ttsInstance?.language = Locale.US
                try {
                    val voices = ttsInstance?.voices?.filter {
                        it.locale.language == "en" &&
                                it.locale.country == "US" &&
                                !it.isNetworkConnectionRequired &&
                                it.name.contains("-x-")
                    }?.distinctBy { it.name.substringBeforeLast("-") }?.sortedBy { it.name }
                        ?.take(6) ?: emptyList()

                    availableVoices = voices
                    if (voices.isNotEmpty()) {
                        val savedVoiceName = sharedPrefs.getString("voice_pref", null)
                        val matchedVoice = voices.find { it.name == savedVoiceName } ?: voices.first()
                        selectedVoice = matchedVoice
                        ttsInstance?.voice = matchedVoice
                    }
                } catch (e: Exception) { }
            }
        }
        tts = ttsInstance
        onDispose { ttsInstance.shutdown() }
    }

    LaunchedEffect(selectedVoice) {
        if (selectedVoice != null) {
            tts?.voice = selectedVoice
        }
    }

    // =========================================================================
    // STATE DECLARATION (Must come BEFORE the rehydration engine)
    // =========================================================================
    var currentScreen by remember { mutableStateOf("DASHBOARD") }
    var navPreference by remember { mutableStateOf("GOOGLE") }
    var serviceRadiusMiles by remember { mutableStateOf(5f) }
    var isLoadoutExpanded by remember { mutableStateOf(false) }
    var isDataLoaded by remember { mutableStateOf(false) }
    var voiceVolume by remember { mutableFloatStateOf(1f) }
    var alertVolume by remember { mutableIntStateOf(100) }

    // --- UPGRADED: TACTICAL VOICE GREETING ---
    var hasSpokenWelcome by remember { mutableStateOf(false) }

    LaunchedEffect(tts, isDataLoaded) {
        if (tts != null && isDataLoaded && !hasSpokenWelcome) {

            // 1. Pull the identity variables from local storage
            val callsign = sharedPrefs.getString("agent_callsign", "")?.trim() ?: ""
            val firstName = sharedPrefs.getString("agent_first_name", "")?.trim() ?: ""

            // 2. Waterfall logic to determine the correct greeting name
            val identity = when {
                callsign.isNotEmpty() -> callsign
                firstName.isNotEmpty() -> firstName
                else -> "Proxy Agent"
            }

            delay(500) // Wait for the visual crossfade to finish
            val ttsParams = android.os.Bundle().apply { putFloat(android.speech.tts.TextToSpeech.Engine.KEY_PARAM_VOLUME, voiceVolume) }
            tts?.speak("The command is now yours, $identity.", TextToSpeech.QUEUE_FLUSH, ttsParams, "WelcomeAudio")
            hasSpokenWelcome = true
        }
    }

    var isOnline by remember { mutableStateOf(false) }
    var isProcessing by remember { mutableStateOf(false) }
    var missionState by remember { mutableStateOf("IDLE") }
    var showAbortDialog by remember { mutableStateOf(false) }
    var showDevMenu by remember { mutableStateOf(false) }
    var abortSliderResetKey by remember { mutableIntStateOf(0) }

    var activeMission by remember { mutableStateOf<MissionData?>(null) }
    var queuedMission by remember { mutableStateOf<MissionData?>(null) }
    var previousQueuedMission by remember { mutableStateOf<MissionData?>(null) }
    var isMissionControlsExpanded by remember { mutableStateOf(false) }

    var agentCapabilities by remember {
        mutableStateOf(
            listOf(
                AgentCapability("close_doors", "Close Doors", "Park behind the AV...", null, 1, true, true, 8f, 20f, 1f, 8f),
                AgentCapability("clean_trash", "Interior Cleaning", "Remove trash...", null, 1, true, true, 8f, 20f, 1f, 8f),
                AgentCapability("search", "Item Search", "Find missing item...", null, 1, true, true, 8f, 20f, 1f, 8f),
                AgentCapability("accident", "Accident Reporting", "Go to scene...", null, 1, true, false, 50f, 100f, 5f, 50f),
                AgentCapability("jump", "EV Charge / Jump Start", "Jump the AV...", "Requires jump kit.", 2, true, false, 20f, 50f, 5f, 20f),
                AgentCapability("clean_spill", "Interior Cleaning (Spill)", "Clean spill...", "Requires supplies.", 2, true, false, 20f, 50f, 5f, 20f),
                AgentCapability("air", "Tire Pressure", "Inflate tire...", "Requires compressor.", 2, true, false, 20f, 50f, 5f, 20f),
                AgentCapability("escort", "Passenger Escort", "Wait with passenger...", "Training required.", 2, true, false, 8f, 20f, 1f, 8f),
                AgentCapability("sensor_clean", "Sensor Cleaning", "Clean sensor...", "Requires cleaning kit.", 3, false, false, 20f, 50f, 1f, 20f),
                AgentCapability("sensor_cal", "Sensor Calibration", "Calibrate...", "Training required.", 3, false, false, 20f, 50f, 1f, 20f),
                AgentCapability("tire_repair", "Tire Repair", "Plug tire...", "Requires plug kit.", 3, false, false, 50f, 100f, 5f, 50f),
                AgentCapability("drive", "Drive Takeover", "Drive AV...", "Special training.", 3, false, false, 20f, 50f, 5f, 20f)
            )
        )
    }

    // =========================================================================
    // REHYDRATION ENGINE & STATE SAVING
    // =========================================================================
    val lifecycleOwner = LocalLifecycleOwner.current
    DisposableEffect(lifecycleOwner) {
        val observer = LifecycleEventObserver { _, event ->
            if (event == Lifecycle.Event.ON_STOP || event == Lifecycle.Event.ON_DESTROY) {
                sharedPrefs.edit().putLong("last_background_time", System.currentTimeMillis()).apply()
            } else if (event == Lifecycle.Event.ON_START) {
                sharedPrefs.edit().putLong("last_background_time", 0L).apply()
            }
        }
        lifecycleOwner.lifecycle.addObserver(observer)
        onDispose { lifecycleOwner.lifecycle.removeObserver(observer) }
    }

    LaunchedEffect(Unit) {
        serviceRadiusMiles = sharedPrefs.getFloat("radius", 5f)
        navPreference = sharedPrefs.getString("nav_pref", "GOOGLE") ?: "GOOGLE"

        // --- NEW: Load Volume Preferences ---
        voiceVolume = sharedPrefs.getFloat("voice_volume", 1f)
        alertVolume = sharedPrefs.getInt("alert_volume", 100)
        val savedCapsJson = sharedPrefs.getString("capabilities", null)
        if (savedCapsJson != null) {
            try { agentCapabilities = Json.decodeFromString(savedCapsJson) } catch (e: Exception) { }
        }

        val savedState = sharedPrefs.getString("mission_state", "IDLE") ?: "IDLE"
        val wasOnline = sharedPrefs.getBoolean("is_online", false)
        val bgTime = sharedPrefs.getLong("last_background_time", 0L)
        val timeOfflineMs = System.currentTimeMillis() - bgTime

        if (savedState != "IDLE" && bgTime > 0L && timeOfflineMs > 300_000L) {
            missionState = "IDLE"
            activeMission = null
            isOnline = wasOnline
            android.widget.Toast.makeText(context, "Mission Aborted: Offline for > 5 mins", android.widget.Toast.LENGTH_LONG).show()
        } else if (savedState != "IDLE") {
            val lat = sharedPrefs.getFloat("mission_lat", 0f).toDouble()
            val lon = sharedPrefs.getFloat("mission_lon", 0f).toDouble()
            if (lat != 0.0 && lon != 0.0) {
                activeMission = MissionData(
                    lat, lon,
                    sharedPrefs.getString("mission_err", "") ?: "",
                    sharedPrefs.getString("mission_bounty", "") ?: "",
                    sharedPrefs.getString("mission_inter", "") ?: ""
                )
                missionState = savedState
                isOnline = wasOnline
            }
        } else {
            isOnline = wasOnline
        }

        if (isOnline) {
            val serviceIntent = Intent(context, network.proxyagent.pantactical.services.PanLocationService::class.java)
            ContextCompat.startForegroundService(context, serviceIntent)
            if (missionState == "IDLE") {
                coroutineScope.launch(kotlinx.coroutines.Dispatchers.IO) {
                    apiClient.openLiveDispatchLine("VANGUARD-01") { lat, lon, err, bounty, inter ->
                        activeMission = MissionData(lat, lon, err, bounty, inter)
                        missionState = "PENDING"
                    }
                }
            }
        }
        isDataLoaded = true
    }

    LaunchedEffect(serviceRadiusMiles, navPreference, agentCapabilities, selectedVoice, voiceVolume, alertVolume) {
        if (isDataLoaded) {
            sharedPrefs.edit().apply {
                putFloat("radius", serviceRadiusMiles)
                putString("nav_pref", navPreference)
                putFloat("voice_volume", voiceVolume)
                putInt("alert_volume", alertVolume)
                putString("capabilities", Json.encodeToString(agentCapabilities))
                selectedVoice?.name?.let { putString("voice_pref", it) }
                apply()
            }
        }
    }

    LaunchedEffect(missionState, activeMission, isOnline) {
        if (isDataLoaded) {
            sharedPrefs.edit().apply {
                putString("mission_state", missionState)
                putBoolean("is_online", isOnline)
                if (activeMission != null) {
                    putFloat("mission_lat", activeMission!!.lat.toFloat())
                    putFloat("mission_lon", activeMission!!.lon.toFloat())
                    putString("mission_err", activeMission!!.errorCode)
                    putString("mission_bounty", activeMission!!.bounty)
                    putString("mission_inter", activeMission!!.intersection)
                } else {
                    remove("mission_lat"); remove("mission_lon"); remove("mission_err"); remove("mission_bounty"); remove("mission_inter")
                }
                apply()
            }
        }
    }

    LaunchedEffect(queuedMission) {
        if (previousQueuedMission != null && queuedMission == null && missionState == "ACTIVE") {
            val toneGen = ToneGenerator(AudioManager.STREAM_ALARM, alertVolume)
            try {
                toneGen.startTone(ToneGenerator.TONE_CDMA_ABBR_INTERCEPT, 400)
                android.widget.Toast.makeText(context, "Queued Mission Cancelled by Command.", android.widget.Toast.LENGTH_LONG).show()
                delay(400)
            } finally { toneGen.release() }
        }
        previousQueuedMission = queuedMission
    }

    var tacticalRoute by remember { mutableStateOf<List<LatLng>>(emptyList()) }
    var agentLocation by remember { mutableStateOf(LatLng(33.3061, -111.6601)) }
    var hasGpsLock by remember { mutableStateOf(false) }
    var locationPermissionGranted by remember { mutableStateOf(false) }

    var hasCameraPermission by remember { mutableStateOf(ContextCompat.checkSelfPermission(context, Manifest.permission.CAMERA) == PackageManager.PERMISSION_GRANTED) }
    var capturedProofImage by remember { mutableStateOf<Bitmap?>(null) }
    var isUploadingProof by remember { mutableStateOf(false) }
    var isSanitizing by remember { mutableStateOf(false) }

    val cameraPermissionLauncher = rememberLauncherForActivityResult(ActivityResultContracts.RequestPermission()) { isGranted -> hasCameraPermission = isGranted }

    val takePictureLauncher = rememberLauncherForActivityResult(ActivityResultContracts.TakePicturePreview()) { bitmap ->
        if (bitmap != null) {
            isSanitizing = true; isUploadingProof = true
            coroutineScope.launch {
                val safeImage = network.proxyagent.pantactical.security.PrivacyFilter.sanitizeImage(bitmap)
                capturedProofImage = safeImage; isSanitizing = false
            }
        }
    }

    val countdownProgress = remember { Animatable(1f) }
    var isFlashing by remember { mutableStateOf(false) }
    val flashAlpha by animateFloatAsState(targetValue = if (isFlashing) 0.2f else 0f, animationSpec = tween(durationMillis = 150), label = "flash")

    var hasInitializedAudio by remember { mutableStateOf(false) }
    LaunchedEffect(isOnline) {
        if (!hasInitializedAudio) { hasInitializedAudio = true; return@LaunchedEffect }
        val statusToneGen = ToneGenerator(AudioManager.STREAM_ALARM, alertVolume)
        try {
            if (isOnline) { statusToneGen.startTone(ToneGenerator.TONE_PROP_ACK, 100); delay(150); statusToneGen.startTone(ToneGenerator.TONE_PROP_ACK, 100) }
            else { statusToneGen.startTone(ToneGenerator.TONE_PROP_NACK, 250) }
            delay(300)
        } finally { statusToneGen.release() }
    }

    LaunchedEffect(missionState) {
        if (missionState == "PENDING" && activeMission != null) {

            // --- NEW: TACTICAL VOICE DISPATCH ANNOUNCEMENT ---
            val speechText = "Priority Dispatch. ${activeMission?.intersection}. Diagnostic: ${activeMission?.errorCode}. Guaranteed payout: ${activeMission?.bounty}."
            val ttsParams = android.os.Bundle().apply { putFloat(android.speech.tts.TextToSpeech.Engine.KEY_PARAM_VOLUME, voiceVolume) }
            tts?.speak(speechText, TextToSpeech.QUEUE_ADD, ttsParams, "MissionAlert")

            launch {
                countdownProgress.snapTo(1f)
                val durationMs = 10000L
                val startTime = System.currentTimeMillis()
                var elapsed = 0L
                while (elapsed < durationMs && missionState == "PENDING") {
                    elapsed = System.currentTimeMillis() - startTime
                    val remainingPercentage = 1f - (elapsed.toFloat() / durationMs.toFloat())
                    countdownProgress.snapTo(remainingPercentage.coerceIn(0f, 1f))
                    delay(16L)
                }
                if (missionState == "PENDING") { missionState = "IDLE"; activeMission = null }
            }
            launch {
                val toneGen = ToneGenerator(AudioManager.STREAM_ALARM, alertVolume)
                try {
                    while (isActive && countdownProgress.value > 0f && missionState == "PENDING") {
                        isFlashing = true; toneGen.startTone(ToneGenerator.TONE_CDMA_ALERT_CALL_GUARD, 150); delay(150); isFlashing = false; delay(1850)
                    }
                } finally { toneGen.release() }
            }
        }
    }

    val fusedLocationClient = remember { LocationServices.getFusedLocationProviderClient(context) }
    val locationCallback = remember {
        object : LocationCallback() {
            override fun onLocationResult(locationResult: LocationResult) {
                for (location in locationResult.locations) {
                    agentLocation = LatLng(location.latitude, location.longitude)
                    hasGpsLock = true // <--- NEW: We officially have a real satellite ping!
                }
            }
        }
    }

    val permissionLauncher = rememberLauncherForActivityResult(ActivityResultContracts.RequestMultiplePermissions()) { perms ->
        locationPermissionGranted = perms[Manifest.permission.ACCESS_FINE_LOCATION] == true || perms[Manifest.permission.ACCESS_COARSE_LOCATION] == true
    }

    LaunchedEffect(Unit) {
        val permissionsToRequest = mutableListOf(Manifest.permission.ACCESS_FINE_LOCATION, Manifest.permission.ACCESS_COARSE_LOCATION)
        if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.TIRAMISU) { permissionsToRequest.add(Manifest.permission.POST_NOTIFICATIONS) }
        permissionLauncher.launch(permissionsToRequest.toTypedArray())
        hasCameraPermission = ContextCompat.checkSelfPermission(context, Manifest.permission.CAMERA) == PackageManager.PERMISSION_GRANTED
    }

    LaunchedEffect(locationPermissionGranted) {
        if (locationPermissionGranted) {
            val locationRequest = LocationRequest.Builder(Priority.PRIORITY_HIGH_ACCURACY, 5000).setMinUpdateDistanceMeters(2f).build()
            try { fusedLocationClient.requestLocationUpdates(locationRequest, locationCallback, Looper.getMainLooper()) } catch (e: SecurityException) { }
        }
    }

    // --- UPDATED: Wait for GPS Lock before drawing the route ---
    LaunchedEffect(activeMission, hasGpsLock) {
        if (activeMission != null && hasGpsLock) {
            val routeData = apiClient.getTacticalRoute(agentLocation.latitude, agentLocation.longitude, activeMission!!.lat, activeMission!!.lon)
            tacticalRoute = routeData.first
        } else if (activeMission == null) {
            tacticalRoute = emptyList()
        }
    }

    val distanceMiles = remember(agentLocation, activeMission) {
        if (activeMission == null) return@remember 0.0
        val results = FloatArray(1)
        android.location.Location.distanceBetween(agentLocation.latitude, agentLocation.longitude, activeMission!!.lat, activeMission!!.lon, results)
        (results[0] / 1609.34)
    }

    LaunchedEffect(missionState) { if (missionState == "ACTIVE") isMissionControlsExpanded = false }
    LaunchedEffect(distanceMiles) { if (missionState == "ACTIVE" && distanceMiles <= 0.1) isMissionControlsExpanded = true }

    val dynamicZoom = remember(serviceRadiusMiles) { 14.2f - log2(serviceRadiusMiles) }
    val cameraPositionState = rememberCameraPositionState { position = CameraPosition.fromLatLngZoom(agentLocation, dynamicZoom) }
    LaunchedEffect(agentLocation, serviceRadiusMiles) { if (!cameraPositionState.isMoving) cameraPositionState.position = CameraPosition.fromLatLngZoom(agentLocation, dynamicZoom) }

    val tacticalMapStyle = """
        [
          { "elementType": "geometry", "stylers": [{ "color": "#121212" }] },
          { "elementType": "labels.icon", "stylers": [{ "visibility": "off" }] },
          { "elementType": "labels.text.fill", "stylers": [{ "color": "#EEEEEE" }] },
          { "elementType": "labels.text.stroke", "stylers": [{ "color": "#000000" }, { "weight": 3 }] },
          { "featureType": "road", "elementType": "geometry", "stylers": [{ "color": "#555555" }] }
        ]
    """.trimIndent()
    val mapProperties by remember { mutableStateOf(MapProperties(mapStyleOptions = MapStyleOptions(tacticalMapStyle), isMyLocationEnabled = locationPermissionGranted)) }
    val mapUiSettings by remember { mutableStateOf(MapUiSettings(zoomControlsEnabled = false, myLocationButtonEnabled = false)) }

    Box(modifier = Modifier.fillMaxSize()) {

        Column(modifier = Modifier.fillMaxSize().background(Color(0xFF121212)).systemBarsPadding()) {

            Row(modifier = Modifier.fillMaxWidth().background(Color(0xFF1E1E1E)).padding(16.dp).zIndex(10f), horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.CenterVertically) {
                Text("PAN COMMAND", color = Color.White, fontSize = 20.sp, fontWeight = FontWeight.Bold, letterSpacing = 1.sp, modifier = Modifier.combinedClickable(onClick = {}, onLongClick = { showDevMenu = true }))
                Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(16.dp)) {
                    Text(text = if (isOnline) "🟢 ONLINE" else "🔴 OFFLINE", color = if (isOnline) Color(0xFF4CAF50) else Color(0xFFF44336), fontSize = 14.sp, fontWeight = FontWeight.Bold)
                    Box(modifier = Modifier.size(36.dp).background(Color(0xFF333333), RoundedCornerShape(18.dp)).clickable { currentScreen = "WALLET" }, contentAlignment = Alignment.Center) { Text("👤", fontSize = 16.sp) }
                }
            }

            Box(modifier = Modifier.fillMaxWidth().weight(1f).background(Color(0xFF2A2A2A)), contentAlignment = Alignment.Center) {

                if (missionState == "ACTIVE" && activeMission != null && navPreference == "TACTICAL") {
                    TacticalNavEngine(modifier = Modifier.fillMaxSize(), targetLocation = LatLng(activeMission!!.lat, activeMission!!.lon), mapStyleJson = tacticalMapStyle, onRouteCalculated = { dist, eta -> })
                } else {
                    GoogleMap(modifier = Modifier.fillMaxSize(), cameraPositionState = cameraPositionState, properties = mapProperties, uiSettings = mapUiSettings) {
                        Marker(state = MarkerState(position = agentLocation), title = "VANGUARD-01")
                        if (missionState != "ACTIVE" && missionState != "ON_SCENE") Circle(center = agentLocation, radius = serviceRadiusMiles.toDouble() * 1609.34, fillColor = Color(0x1AF44336), strokeColor = Color(0x80F44336), strokeWidth = 3f)
                        activeMission?.let { mission ->
                            val targetLocation = LatLng(mission.lat, mission.lon)
                            Marker(state = MarkerState(position = targetLocation), title = "🚨 STRANDED AV")
                            if (tacticalRoute.isNotEmpty()) Polyline(points = tacticalRoute, color = Color(0xFFFF9800), width = 14f, geodesic = true)
                            else Polyline(points = listOf(agentLocation, targetLocation), color = Color(0xFFF44336).copy(alpha = 0.5f), width = 8f, geodesic = true)
                        }
                    }
                }

                Column(modifier = Modifier.fillMaxSize(), verticalArrangement = Arrangement.Center, horizontalAlignment = Alignment.CenterHorizontally) {
                    AnimatedVisibility(visible = missionState == "PENDING" && activeMission != null, enter = slideInVertically(initialOffsetY = { it }) + fadeIn(), exit = slideOutVertically(targetOffsetY = { it }) + fadeOut(), modifier = Modifier.fillMaxSize()) {
                        Box(modifier = Modifier.fillMaxSize().background(Color(0xEE121212)).padding(24.dp), contentAlignment = Alignment.Center) {
                            Box(modifier = Modifier.fillMaxSize().background(Color(0xFF4CAF50).copy(alpha = flashAlpha)))
                            Column(modifier = Modifier.fillMaxWidth().verticalScroll(rememberScrollState()), horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.spacedBy(10.dp)) {
                                Text("🚨 RESCUE DISPATCH 🚨", color = Color(0xFFF44336), fontSize = 24.sp, fontWeight = FontWeight.Black, letterSpacing = 1.sp, textAlign = TextAlign.Center)
                                Box(modifier = Modifier.fillMaxWidth().height(12.dp).background(Color(0xFF1E1E1E), shape = RoundedCornerShape(8.dp)), contentAlignment = Alignment.CenterStart) { Box(modifier = Modifier.fillMaxHeight().fillMaxWidth(countdownProgress.value.coerceIn(0f, 1f)).background(Color(0xFF4CAF50), shape = RoundedCornerShape(8.dp))) }
                                val rawBounty = activeMission?.bounty?.replace("$", "")?.toFloatOrNull() ?: 0f
                                Text("GUARANTEED NET PAYOUT", color = Color.LightGray, fontSize = 12.sp, fontWeight = FontWeight.Bold, letterSpacing = 1.sp)
                                Text(String.format("$%.2f", rawBounty * 0.90f), color = Color(0xFF4CAF50), fontSize = 48.sp, fontWeight = FontWeight.Black)
                                Text(activeMission?.intersection ?: "Unknown", color = Color(0xFFFF9800), fontSize = 20.sp, fontWeight = FontWeight.Medium, textAlign = TextAlign.Center)
                                Text(activeMission?.errorCode ?: "Unknown Error", color = Color.Red, fontSize = 18.sp, fontWeight = FontWeight.Bold, textAlign = TextAlign.Center)
                                Row(horizontalArrangement = Arrangement.spacedBy(16.dp), modifier = Modifier.fillMaxWidth()) {
                                    Button(onClick = { missionState = "IDLE"; activeMission = null }, colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF333333)), modifier = Modifier.weight(1f).height(64.dp), shape = RoundedCornerShape(12.dp)) { Text("DECLINE", color = Color.White) }
                                    Button(onClick = { coroutineScope.launch { if (apiClient.acceptMission()) { missionState = "ACTIVE"; if (navPreference == "GOOGLE") { val mapIntent = Intent(Intent.ACTION_VIEW, Uri.parse("google.navigation:q=${activeMission!!.lat},${activeMission!!.lon}&mode=d")); mapIntent.setPackage("com.google.android.apps.maps"); try { context.startActivity(mapIntent) } catch (e: Exception) { } } } } }, colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF4CAF50)), modifier = Modifier.weight(1f).height(64.dp), shape = RoundedCornerShape(12.dp)) { Text("ACCEPT", color = Color.White, fontWeight = FontWeight.Black) }
                                }
                            }
                        }
                    }
                }

                Column(modifier = Modifier.fillMaxSize(), verticalArrangement = Arrangement.Center, horizontalAlignment = Alignment.CenterHorizontally) {
                    AnimatedVisibility(visible = capturedProofImage != null && isUploadingProof, enter = fadeIn(), exit = fadeOut(), modifier = Modifier.fillMaxSize()) {
                        Box(modifier = Modifier.fillMaxSize().background(Color(0xEE000000)).padding(24.dp), contentAlignment = Alignment.Center) {
                            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                                Box(modifier = Modifier.size(300.dp).border(2.dp, Color(0xFF00BCD4), RoundedCornerShape(8.dp)).clip(RoundedCornerShape(8.dp))) {
                                    capturedProofImage?.let { bmp -> Image(bitmap = bmp.asImageBitmap(), contentDescription = "Proof", modifier = Modifier.fillMaxSize(), contentScale = ContentScale.Crop) }
                                    Column(modifier = Modifier.align(Alignment.BottomStart).background(Color(0x80000000)).padding(8.dp)) { Text("GPS: ${agentLocation.latitude}, ${agentLocation.longitude}", color = Color(0xFF00FF00), fontSize = 10.sp, fontFamily = FontFamily.Monospace); Text("TIMESTAMP: ${System.currentTimeMillis()}", color = Color(0xFF00FF00), fontSize = 10.sp, fontFamily = FontFamily.Monospace) }
                                }
                                Spacer(modifier = Modifier.height(24.dp)); CircularProgressIndicator(color = Color(0xFF00BCD4)); Spacer(modifier = Modifier.height(16.dp))
                                if (isSanitizing) { Text("SANITIZING PII...", color = Color.Red, fontWeight = FontWeight.Black, letterSpacing = 2.sp); Text("REDACTING FACES & LICENSE PLATES", color = Color.Gray, fontSize = 12.sp) } else { Text("CRYPTOGRAPHIC WATERMARKING...", color = Color(0xFF00BCD4), fontWeight = FontWeight.Black, letterSpacing = 2.sp); Text("UPLOADING SECURE PROOF OF WORK", color = Color.Gray, fontSize = 12.sp) }
                                LaunchedEffect(capturedProofImage) {
                                    delay(2000)
                                    val rawBounty = activeMission?.bounty?.replace("$", "")?.toFloatOrNull() ?: 0f
                                    val finalPayout = (rawBounty * 0.90f).toDouble()
                                    if (apiClient.claimEscrowFunds(netPayout = finalPayout)) { android.widget.Toast.makeText(context, String.format("Proof Accepted. +$%.2f", finalPayout), android.widget.Toast.LENGTH_LONG).show(); if (queuedMission != null) { activeMission = queuedMission; queuedMission = null; missionState = "ACTIVE" } else { missionState = "IDLE"; activeMission = null } } else { android.widget.Toast.makeText(context, "Network Error: Upload Failed.", android.widget.Toast.LENGTH_LONG).show() }
                                    isUploadingProof = false; capturedProofImage = null
                                }
                            }
                        }
                    }
                }
            }

            Column(modifier = Modifier.fillMaxWidth().background(Color(0xFF1E1E1E)), horizontalAlignment = Alignment.CenterHorizontally) {
                AnimatedVisibility(visible = missionState == "ACTIVE", enter = expandVertically() + fadeIn(), exit = shrinkVertically() + fadeOut()) {
                    Column(modifier = Modifier.fillMaxWidth(), horizontalAlignment = Alignment.CenterHorizontally) {
                        Box(modifier = Modifier.fillMaxWidth().clickable { isMissionControlsExpanded = !isMissionControlsExpanded }.padding(vertical = 12.dp), contentAlignment = Alignment.Center) { Text(if (isMissionControlsExpanded) "▼ HIDE MISSION CONTROLS ▼" else "▲ SHOW MISSION CONTROLS ▲", color = Color(0xFF00BCD4), fontSize = 12.sp, fontWeight = FontWeight.Bold, letterSpacing = 1.sp) }
                        AnimatedVisibility(visible = isMissionControlsExpanded) {
                            Column(modifier = Modifier.fillMaxWidth().padding(start = 16.dp, end = 16.dp, bottom = 16.dp), horizontalAlignment = Alignment.CenterHorizontally) {
                                Text("ACTIVE MISSION: EN ROUTE", color = Color(0xFF00BCD4), fontSize = 14.sp, fontWeight = FontWeight.Black, letterSpacing = 2.sp)
                                Spacer(modifier = Modifier.height(8.dp)); Text(activeMission?.intersection ?: "Target Location", color = Color.White, fontSize = 20.sp, fontWeight = FontWeight.Bold); Text("Diagnostic: ${activeMission?.errorCode}", color = Color.LightGray, fontSize = 14.sp); Spacer(modifier = Modifier.height(16.dp))
                                val isAtScene = distanceMiles <= 0.1
                                AnimatedVisibility(visible = isAtScene) { Button(onClick = { missionState = "ON_SCENE" }, colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF00BCD4)), shape = RoundedCornerShape(8.dp), modifier = Modifier.fillMaxWidth().height(64.dp).padding(bottom = 16.dp)) { Text("ARRIVED AT SCENE", color = Color.Black, fontSize = 20.sp, fontWeight = FontWeight.Black, letterSpacing = 1.sp) } }
                                key(abortSliderResetKey) { SwipeActionSlider(text = "SWIPE TO ABORT >>", trackColor = Color(0xFF2C2C2C), thumbColor = Color(0xFFD32F2F)) { showAbortDialog = true } }
                            }
                        }
                    }
                }

                AnimatedVisibility(visible = missionState == "ON_SCENE", enter = expandVertically() + fadeIn(), exit = shrinkVertically() + fadeOut()) {
                    var terminalLogs by remember { mutableStateOf(listOf("Establishing local UWB connection to AV...", "Connection secured.", "Awaiting physical repair and diagnostic re-run...")) }
                    var isResolving by remember { mutableStateOf(false) }
                    var isResolved by remember { mutableStateOf(false) }
                    LaunchedEffect(activeMission) { terminalLogs = listOf("Connection secured.", "Awaiting repair..."); isResolving = false; isResolved = false }
                    Column(modifier = Modifier.fillMaxWidth().padding(16.dp).background(Color(0xFF0D1117)).padding(16.dp), horizontalAlignment = Alignment.CenterHorizontally) {
                        Text("📟 AV DIAGNOSTIC TERMINAL", color = Color(0xFF00FF00), fontSize = 16.sp, fontWeight = FontWeight.Black, letterSpacing = 1.sp); Spacer(modifier = Modifier.height(12.dp))
                        Box(modifier = Modifier.fillMaxWidth().height(140.dp).background(Color.Black, RoundedCornerShape(8.dp)).border(1.dp, Color(0xFF333333), RoundedCornerShape(8.dp)).padding(12.dp)) { Column(modifier = Modifier.verticalScroll(rememberScrollState())) { terminalLogs.forEach { log -> Text("> $log", color = Color(0xFF00FF00), fontFamily = FontFamily.Monospace, fontSize = 12.sp); Spacer(modifier = Modifier.height(4.dp)) } } }
                        Spacer(modifier = Modifier.height(16.dp))
                        if (!isResolved) { Button(enabled = !isResolving, onClick = { isResolving = true; coroutineScope.launch { terminalLogs = terminalLogs + "Pinging AV CAN bus..."; delay(1000); terminalLogs = terminalLogs + "Diagnostic Trouble Codes (DTC) cleared."; delay(800); isResolving = false; isResolved = true } }, colors = ButtonDefaults.buttonColors(containerColor = Color(0xFFD32F2F), disabledContainerColor = Color(0xFF555555)), modifier = Modifier.fillMaxWidth().height(64.dp), shape = RoundedCornerShape(8.dp)) { if (isResolving) CircularProgressIndicator(modifier = Modifier.size(24.dp), color = Color.White) else Text("RE-RUN AV DIAGNOSTICS", color = Color.White, fontWeight = FontWeight.Black) } } else { Button(onClick = { if (hasCameraPermission) takePictureLauncher.launch(null) else cameraPermissionLauncher.launch(Manifest.permission.CAMERA) }, colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF4CAF50), disabledContainerColor = Color(0xFF555555)), modifier = Modifier.fillMaxWidth().height(64.dp), shape = RoundedCornerShape(8.dp)) { Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) { Text("📷", fontSize = 18.sp); Text("CAPTURE PROOF OF WORK", color = Color.White, fontSize = 13.sp, fontWeight = FontWeight.Black) } } }
                    }
                }

                AnimatedVisibility(visible = !isOnline && missionState != "ACTIVE" && missionState != "ON_SCENE") {
                    Column(modifier = Modifier.padding(16.dp), horizontalAlignment = Alignment.CenterHorizontally) {
                        Row(modifier = Modifier.fillMaxWidth().background(Color(0xFF2A2A2A), RoundedCornerShape(8.dp)).clip(RoundedCornerShape(8.dp)).clickable { isLoadoutExpanded = !isLoadoutExpanded }.padding(16.dp), horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.CenterVertically) { Text("🛠 MARKET BIDS & LOADOUT", color = Color.White, fontSize = 12.sp, fontWeight = FontWeight.Black, letterSpacing = 1.sp); Text(if (isLoadoutExpanded) "HIDE ▲" else "EXPAND ▼", color = Color(0xFF00BCD4), fontSize = 12.sp, fontWeight = FontWeight.Bold) }
                        AnimatedVisibility(visible = isLoadoutExpanded) {
                            Column(modifier = Modifier.fillMaxWidth().padding(top = 16.dp)) {
                                Text("SERVICE RADIUS: ${serviceRadiusMiles.toInt()} MILES", color = Color.LightGray, fontSize = 12.sp, fontWeight = FontWeight.Bold)
                                Slider(value = serviceRadiusMiles, onValueChange = { serviceRadiusMiles = it }, valueRange = 1f..8f, steps = 6, colors = SliderDefaults.colors(thumbColor = Color(0xFFF44336), activeTrackColor = Color(0xFFF44336)), modifier = Modifier.padding(bottom = 12.dp))
                                Column(modifier = Modifier.fillMaxWidth().heightIn(max = 350.dp).verticalScroll(rememberScrollState()).padding(bottom = 16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                                    val pinned = agentCapabilities.filter { it.isPinned }
                                    val tier1 = agentCapabilities.filter { it.tier == 1 && !it.isPinned }
                                    val tier2 = agentCapabilities.filter { it.tier == 2 && !it.isPinned }
                                    val tier3 = agentCapabilities.filter { it.tier == 3 && !it.isPinned }
                                    if (pinned.isNotEmpty()) { Text("📌 PINNED TASKS", color = Color(0xFFFF9800), fontSize = 12.sp, fontWeight = FontWeight.Black, modifier = Modifier.padding(top = 8.dp, bottom = 4.dp)); pinned.forEach { cap -> CapabilityCard(cap, agentCapabilities) { agentCapabilities = it } } }
                                    if (tier1.isNotEmpty()) { Text("TIER 1 - BASIC RESPONDER", color = Color(0xFF00BCD4), fontSize = 12.sp, fontWeight = FontWeight.Black, modifier = Modifier.padding(top = 8.dp, bottom = 4.dp)); tier1.forEach { cap -> CapabilityCard(cap, agentCapabilities) { agentCapabilities = it } } }
                                    if (tier2.isNotEmpty()) { Text("TIER 2 - EQUIPMENT REQUIRED", color = Color(0xFF00BCD4), fontSize = 12.sp, fontWeight = FontWeight.Black, modifier = Modifier.padding(top = 8.dp, bottom = 4.dp)); tier2.forEach { cap -> CapabilityCard(cap, agentCapabilities) { agentCapabilities = it } } }
                                    if (tier3.isNotEmpty()) { Text("TIER 3 - SPECIALIZED TRAINING", color = Color(0xFF00BCD4), fontSize = 12.sp, fontWeight = FontWeight.Black, modifier = Modifier.padding(top = 8.dp, bottom = 4.dp)); tier3.forEach { cap -> CapabilityCard(cap, agentCapabilities) { agentCapabilities = it } } }
                                }
                            }
                        }
                        Spacer(modifier = Modifier.height(16.dp))
                    }
                }

                AnimatedVisibility(visible = missionState != "ACTIVE" && missionState != "ON_SCENE") {
                    Box(modifier = Modifier.padding(start = 16.dp, end = 16.dp, bottom = 16.dp)) {
                        if (isOnline) {
                            SwipeActionSlider(text = "SWIPE TO GO OFFLINE >>", trackColor = Color(0xFF333333), thumbColor = Color(0xFFF44336)) {
                                isProcessing = true; coroutineScope.launch { apiClient.updateAgentStatus(context, false, agentLocation.latitude, agentLocation.longitude, serviceRadiusMiles.toDouble(), emptyMap()); val serviceIntent = Intent(context, network.proxyagent.pantactical.services.PanLocationService::class.java); context.stopService(serviceIntent); isOnline = false; missionState = "IDLE"; isProcessing = false }
                            }
                        } else {
                            Button(
                                enabled = !isProcessing,
                                onClick = {
                                    isProcessing = true
                                    coroutineScope.launch {
                                        val activeLoadout = agentCapabilities.filter { it.isQualified && it.isEnabled }.associate { it.id to it.currentBid }
                                        if (apiClient.updateAgentStatus(context, true, agentLocation.latitude, agentLocation.longitude, serviceRadiusMiles.toDouble(), activeLoadout)) {
                                            val serviceIntent = Intent(context, network.proxyagent.pantactical.services.PanLocationService::class.java); ContextCompat.startForegroundService(context, serviceIntent); isOnline = true
                                            coroutineScope.launch(kotlinx.coroutines.Dispatchers.IO) { apiClient.openLiveDispatchLine("VANGUARD-01") { lat, lon, err, bounty, inter -> activeMission = MissionData(lat, lon, err, bounty, inter); missionState = "PENDING" } }
                                        }
                                        isProcessing = false
                                    }
                                },
                                modifier = Modifier.fillMaxWidth().height(56.dp), colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF2E7D32), disabledContainerColor = Color(0xFF555555))
                            ) { if (isProcessing) CircularProgressIndicator(color = Color.White) else Text("GO ONLINE", color = Color.White, fontWeight = FontWeight.Bold, letterSpacing = 1.sp) }
                        }
                    }
                }
            }
        }

        AnimatedVisibility(visible = currentScreen == "WALLET", enter = slideInHorizontally(initialOffsetX = { it }) + fadeIn(), exit = slideOutHorizontally(targetOffsetX = { it }) + fadeOut(), modifier = Modifier.fillMaxSize().zIndex(10f)) {
            WalletAndProfileScreen(
                apiClient = apiClient,
                onBack = { currentScreen = "DASHBOARD" },
                navPreference = navPreference,
                onNavPrefChange = { navPreference = it },
                tts = tts,
                availableVoices = availableVoices,
                selectedVoice = selectedVoice,
                onVoiceSelect = { selectedVoice = it },
                // --- NEW PASS-THROUGHS ---
                voiceVolume = voiceVolume,
                onVoiceVolumeChange = { voiceVolume = it },
                alertVolume = alertVolume,
                onAlertVolumeChange = { alertVolume = it }
            )
        }

        if (showDevMenu) {
            AlertDialog(
                onDismissRequest = { showDevMenu = false }, containerColor = Color(0xFF1E1E1E), title = { Text("DEV: INJECT MISSION", color = Color.White, fontWeight = FontWeight.Black) },
                text = {
                    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        Button(onClick = { activeMission = MissionData(33.432, -111.865, "ERR-TRASH: Biohazard", "$45.00", "Mesa Riverview"); missionState = "PENDING"; showDevMenu = false }, colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF333333)), modifier = Modifier.fillMaxWidth()) { Text("LOC 1: Mesa Riverview", color = Color.White) }
                        Button(onClick = { activeMission = MissionData(33.385, -111.683, "ERR-TIRE: Puncture", "$80.00", "Superstition Springs"); missionState = "PENDING"; showDevMenu = false }, colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF333333)), modifier = Modifier.fillMaxWidth()) { Text("LOC 2: Superstition Springs", color = Color.White) }
                        Button(onClick = { activeMission = MissionData(33.415, -111.831, "ERR-DOOR: Latch Fault", "$12.00", "Downtown Mesa"); missionState = "PENDING"; showDevMenu = false }, colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF333333)), modifier = Modifier.fillMaxWidth()) { Text("LOC 3: Downtown Mesa", color = Color.White) }
                    }
                },
                confirmButton = {}, dismissButton = { TextButton(onClick = { showDevMenu = false }) { Text("CLOSE", color = Color.Gray) } }
            )
        }

        if (showAbortDialog) {
            AlertDialog(
                onDismissRequest = { showAbortDialog = false; abortSliderResetKey++ }, containerColor = Color(0xFF1E1E1E), title = { Text("ABORT MISSION", color = Color.White, fontWeight = FontWeight.Black) },
                text = {
                    Column {
                        listOf("Too Dangerous", "Changed Mind", "Can't Find AV", "AV Leaving Scene", "Other").forEach { reason ->
                            Button(onClick = { showAbortDialog = false; missionState = "IDLE"; activeMission = null; queuedMission = null; abortSliderResetKey++ }, colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF333333)), modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp), shape = RoundedCornerShape(8.dp)) { Text(reason, color = Color.White, fontWeight = FontWeight.Bold) }
                        }
                    }
                },
                confirmButton = {}, dismissButton = { TextButton(onClick = { showAbortDialog = false; abortSliderResetKey++ }) { Text("CANCEL", color = Color.Gray) } }
            )
        }
    }
}