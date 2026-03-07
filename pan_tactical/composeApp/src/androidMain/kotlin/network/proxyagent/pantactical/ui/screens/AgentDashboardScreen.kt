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
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.gestures.detectHorizontalDragGestures
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
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.zIndex
import androidx.core.content.ContextCompat
import kotlinx.coroutines.delay
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch

import kotlinx.serialization.Serializable
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json

import network.proxyagent.pantactical.network.PanApiClient
import java.util.Locale
import kotlin.math.log2
import kotlin.math.roundToInt

import com.google.android.gms.location.*
import com.google.android.gms.maps.model.CameraPosition
import com.google.android.gms.maps.model.LatLng
import com.google.android.gms.maps.model.MapStyleOptions
import com.google.maps.android.compose.*

data class MissionData(
    val lat: Double,
    val lon: Double,
    val errorCode: String,
    val bounty: String,
    val intersection: String
)

@Serializable
data class AgentCapability(
    val id: String,
    val title: String,
    val description: String?,
    val isQualified: Boolean,
    var isEnabled: Boolean,
    val minPrice: Float,
    val maxPrice: Float,
    val step: Float,
    var currentBid: Float
)

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

@Composable
fun MainDashboardContent() {
    val context = LocalContext.current
    val coroutineScope = rememberCoroutineScope()
    val apiClient = remember { PanApiClient() }

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
                    }?.distinctBy { it.name.substringBeforeLast("-") }?.sortedBy { it.name }?.take(6) ?: emptyList()

                    availableVoices = voices
                    if (voices.isNotEmpty()) {
                        selectedVoice = voices.first()
                        ttsInstance?.voice = voices.first()
                    }
                } catch (e: Exception) { }
            }
        }
        tts = ttsInstance
        onDispose { ttsInstance?.shutdown() }
    }

    var currentScreen by remember { mutableStateOf("DASHBOARD") }
    var navPreference by remember { mutableStateOf("GOOGLE") }
    var serviceRadiusMiles by remember { mutableStateOf(5f) }
    var isLoadoutExpanded by remember { mutableStateOf(false) }

    var agentCapabilities by remember {
        mutableStateOf(listOf(
            AgentCapability("accident", "Accident Reporting", null, true, false, 50f, 100f, 5f, 50f),
            AgentCapability("doors", "Close Doors", null, true, true, 8f, 20f, 1f, 8f),
            AgentCapability("drive", "Drive Takeover", null, false, false, 20f, 50f, 5f, 20f),
            AgentCapability("jump", "EV Charge / Jump Start", null, true, true, 20f, 50f, 5f, 20f),
            AgentCapability("clean", "Interior Cleaning (Trash)", null, true, true, 8f, 20f, 1f, 8f),
            AgentCapability("clean_hazmat", "Interior Cleaning (Hazardous)", null, true, false, 50f, 100f, 5f, 50f),
            AgentCapability("air", "Tire Pressure", null, true, true, 20f, 50f, 5f, 20f),
            AgentCapability("tire_repair", "Tire Repair", null, true, false, 50f, 100f, 5f, 50f)
        ))
    }

    var isDataLoaded by remember { mutableStateOf(false) }
    val sharedPrefs = context.getSharedPreferences("PanAgentSettings", Context.MODE_PRIVATE)

    LaunchedEffect(Unit) {
        serviceRadiusMiles = sharedPrefs.getFloat("radius", 5f)
        navPreference = sharedPrefs.getString("nav_pref", "GOOGLE") ?: "GOOGLE"
        val savedCapsJson = sharedPrefs.getString("capabilities", null)
        if (savedCapsJson != null) {
            try { agentCapabilities = Json.decodeFromString(savedCapsJson) } catch (e: Exception) { }
        }
        isDataLoaded = true
    }

    LaunchedEffect(serviceRadiusMiles, navPreference, agentCapabilities) {
        if (isDataLoaded) {
            sharedPrefs.edit().apply {
                putFloat("radius", serviceRadiusMiles)
                putString("nav_pref", navPreference)
                putString("capabilities", Json.encodeToString(agentCapabilities))
                apply()
            }
        }
    }

    var isOnline by remember { mutableStateOf(false) }
    var isProcessing by remember { mutableStateOf(false) }
    var missionState by remember { mutableStateOf("IDLE") }
    var showAbortDialog by remember { mutableStateOf(false) }
    var abortSliderResetKey by remember { mutableIntStateOf(0) }

    var activeMission by remember { mutableStateOf<MissionData?>(null) }
    var queuedMission by remember { mutableStateOf<MissionData?>(null) }
    var previousQueuedMission by remember { mutableStateOf<MissionData?>(null) }

    LaunchedEffect(queuedMission) {
        if (previousQueuedMission != null && queuedMission == null && missionState == "ACTIVE") {
            val toneGen = ToneGenerator(AudioManager.STREAM_ALARM, 100)
            try {
                toneGen.startTone(ToneGenerator.TONE_CDMA_ABBR_INTERCEPT, 400)
                android.widget.Toast.makeText(context, "Queued Mission Cancelled by Command.", android.widget.Toast.LENGTH_LONG).show()
                delay(400)
            } finally { toneGen.release() }
        }
        previousQueuedMission = queuedMission
    }

    var tacticalRoute by remember { mutableStateOf<List<LatLng>>(emptyList()) }
    var tacticalSteps by remember { mutableStateOf<List<Triple<String, Double, Double>>>(emptyList()) }
    var currentStepIndex by remember { mutableIntStateOf(0) }
    var viewStepIndex by remember { mutableIntStateOf(0) }
    var hasEnteredManeuverZone by remember { mutableStateOf(false) }

    var agentLocation by remember { mutableStateOf(LatLng(33.3061, -111.6601)) }
    var locationPermissionGranted by remember { mutableStateOf(false) }

    // --- CAMERA PERMISSIONS & STATE ---
    var hasCameraPermission by remember { mutableStateOf(ContextCompat.checkSelfPermission(context, Manifest.permission.CAMERA) == PackageManager.PERMISSION_GRANTED) }
    var capturedProofImage by remember { mutableStateOf<Bitmap?>(null) }
    var isUploadingProof by remember { mutableStateOf(false) }
    var isSanitizing by remember { mutableStateOf(false) }

    val cameraPermissionLauncher = rememberLauncherForActivityResult(ActivityResultContracts.RequestPermission()) { isGranted ->
        hasCameraPermission = isGranted
    }

    val takePictureLauncher = rememberLauncherForActivityResult(ActivityResultContracts.TakePicturePreview()) { bitmap ->
        if (bitmap != null) {
            isSanitizing = true
            isUploadingProof = true

            // Pass the image through our local ML filter before displaying or uploading
            coroutineScope.launch {
                val safeImage = network.proxyagent.pantactical.security.PrivacyFilter.sanitizeImage(bitmap)
                capturedProofImage = safeImage
                isSanitizing = false
            }
        }
    }

    val countdownProgress = remember { Animatable(1f) }
    var isFlashing by remember { mutableStateOf(false) }
    val flashAlpha by animateFloatAsState(targetValue = if (isFlashing) 0.2f else 0f, animationSpec = tween(durationMillis = 150), label = "flash")

    val diagnosticProtocols = mapOf(
        "ERR-702: Sensor Occlusion" to "Wipe down roof-mounted LIDAR and side camera housings with approved microfiber cloth. Ensure no streaks remain.",
        "ERR-TIRE: Low Pressure" to "Inflate affected tire to 36 PSI using on-board air compressor. Perform visual inspection for punctures or debris.",
        "ERR-BATT: 12V Depleted" to "Remove front access panel. Connect portable jump starter to the 12V auxiliary terminals until relay clicks.",
        "ERR-CABIN: Biohazard" to "Equip Level 1 PPE. Utilize solvent and absorbent pads to clear passenger cabin debris. Deposit in hazmat bag."
    )

    var hasInitializedAudio by remember { mutableStateOf(false) }
    LaunchedEffect(isOnline) {
        if (!hasInitializedAudio) { hasInitializedAudio = true; return@LaunchedEffect }
        val statusToneGen = ToneGenerator(AudioManager.STREAM_ALARM, 100)
        try {
            if (isOnline) { statusToneGen.startTone(ToneGenerator.TONE_PROP_ACK, 100); delay(150); statusToneGen.startTone(ToneGenerator.TONE_PROP_ACK, 100) }
            else { statusToneGen.startTone(ToneGenerator.TONE_PROP_NACK, 250) }
            delay(300)
        } finally { statusToneGen.release() }
    }

    LaunchedEffect(missionState) {
        if (missionState == "PENDING") {
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
                val toneGen = ToneGenerator(AudioManager.STREAM_ALARM, 100)
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
                for (location in locationResult.locations) agentLocation = LatLng(location.latitude, location.longitude)
            }
        }
    }

    val permissionLauncher = rememberLauncherForActivityResult(ActivityResultContracts.RequestMultiplePermissions()) { perms ->
        locationPermissionGranted = perms[Manifest.permission.ACCESS_FINE_LOCATION] == true || perms[Manifest.permission.ACCESS_COARSE_LOCATION] == true
    }

    LaunchedEffect(Unit) {
        val permissionsToRequest = mutableListOf(
            Manifest.permission.ACCESS_FINE_LOCATION,
            Manifest.permission.ACCESS_COARSE_LOCATION
        )
        if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.TIRAMISU) {
            permissionsToRequest.add(Manifest.permission.POST_NOTIFICATIONS)
        }
        permissionLauncher.launch(permissionsToRequest.toTypedArray())

        hasCameraPermission = ContextCompat.checkSelfPermission(context, Manifest.permission.CAMERA) == PackageManager.PERMISSION_GRANTED
    }

    LaunchedEffect(locationPermissionGranted) {
        if (locationPermissionGranted) {
            val locationRequest = LocationRequest.Builder(Priority.PRIORITY_HIGH_ACCURACY, 5000).setMinUpdateDistanceMeters(2f).build()
            try { fusedLocationClient.requestLocationUpdates(locationRequest, locationCallback, Looper.getMainLooper()) } catch (e: SecurityException) { }
        }
    }

    LaunchedEffect(activeMission) {
        if (activeMission != null) {
            val routeData = apiClient.getTacticalRoute(agentLocation.latitude, agentLocation.longitude, activeMission!!.lat, activeMission!!.lon)
            tacticalRoute = routeData.first; tacticalSteps = routeData.second; currentStepIndex = 0; viewStepIndex = 0; hasEnteredManeuverZone = false
        } else {
            tacticalRoute = emptyList(); tacticalSteps = emptyList(); currentStepIndex = 0; viewStepIndex = 0
        }
    }

    val distanceMiles = remember(agentLocation, activeMission) {
        if (activeMission == null) return@remember 0.0
        val results = FloatArray(1)
        android.location.Location.distanceBetween(agentLocation.latitude, agentLocation.longitude, activeMission!!.lat, activeMission!!.lon, results)
        (results[0] / 1609.34)
    }

    val liveStep = tacticalSteps.getOrNull(currentStepIndex)
    if (liveStep != null && missionState == "ACTIVE") {
        val results = FloatArray(1)
        android.location.Location.distanceBetween(agentLocation.latitude, agentLocation.longitude, liveStep.second, liveStep.third, results)
        val distToManeuverMeters = results[0]

        LaunchedEffect(currentStepIndex) {
            viewStepIndex = currentStepIndex
            delay(250)
            val announcement = if (distToManeuverMeters < 160.9f) "In ${((distToManeuverMeters * 3.28084) / 25.0).roundToInt() * 25} feet, ${liveStep.first}" else "In ${String.format("%.1f", distToManeuverMeters / 1609.34f)} miles, ${liveStep.first}"
            if (navPreference == "TACTICAL") tts?.speak(announcement, TextToSpeech.QUEUE_FLUSH, null, "NavStep_$currentStepIndex")
        }

        LaunchedEffect(distToManeuverMeters) {
            if (distToManeuverMeters < 15f) hasEnteredManeuverZone = true
            else if (hasEnteredManeuverZone && distToManeuverMeters > 30f) {
                if (currentStepIndex < tacticalSteps.size - 1) { currentStepIndex++; hasEnteredManeuverZone = false }
            }
        }
    }

    val dynamicZoom = remember(serviceRadiusMiles) { 14.2f - log2(serviceRadiusMiles) }
    val cameraPositionState = rememberCameraPositionState { position = CameraPosition.fromLatLngZoom(agentLocation, dynamicZoom) }

    LaunchedEffect(agentLocation, serviceRadiusMiles) {
        if (!cameraPositionState.isMoving) cameraPositionState.position = CameraPosition.fromLatLngZoom(agentLocation, dynamicZoom)
    }

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

            Row(modifier = Modifier.fillMaxWidth().background(Color(0xFF1E1E1E)).padding(16.dp), horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.CenterVertically) {
                Text("PAN COMMAND", color = Color.White, fontSize = 20.sp, fontWeight = FontWeight.Bold, letterSpacing = 1.sp)
                Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(16.dp)) {
                    Text(text = if (isOnline) "🟢 ONLINE" else "🔴 OFFLINE", color = if (isOnline) Color(0xFF4CAF50) else Color(0xFFF44336), fontSize = 14.sp, fontWeight = FontWeight.Bold)
                    Box(modifier = Modifier.size(36.dp).background(Color(0xFF333333), RoundedCornerShape(18.dp)).clickable { currentScreen = "WALLET" }, contentAlignment = Alignment.Center) {
                        Text("👤", fontSize = 16.sp)
                    }
                }
            }

            AnimatedVisibility(visible = missionState == "ACTIVE" && tacticalSteps.isNotEmpty()) {
                var dragOffset by remember { mutableFloatStateOf(0f) }
                Box(
                    modifier = Modifier.fillMaxWidth().pointerInput(Unit) {
                        detectHorizontalDragGestures(
                            onDragEnd = {
                                if (dragOffset < -40f && viewStepIndex < tacticalSteps.size - 1) viewStepIndex++
                                else if (dragOffset > 40f && viewStepIndex > currentStepIndex) viewStepIndex--
                                dragOffset = 0f
                            }
                        ) { change, dragAmount -> change.consume(); dragOffset += dragAmount }
                    }
                ) {
                    AnimatedContent(targetState = viewStepIndex, transitionSpec = {
                        if (targetState > initialState) (slideInHorizontally { width -> width } + fadeIn()).togetherWith(slideOutHorizontally { width -> -width } + fadeOut())
                        else (slideInHorizontally { width -> -width } + fadeIn()).togetherWith(slideOutHorizontally { width -> width } + fadeOut())
                    }, label = "step_transition") { targetIndex ->
                        val displayStep = tacticalSteps.getOrNull(targetIndex)
                        if (displayStep != null) {
                            val stepResults = FloatArray(1)
                            android.location.Location.distanceBetween(agentLocation.latitude, agentLocation.longitude, displayStep.second, displayStep.third, stepResults)
                            val distToDisplayMeters = stepResults[0]
                            val distDisplay = if (distToDisplayMeters < 160.9f) {
                                val roundedFeet = ((distToDisplayMeters * 3.28084) / 25.0).roundToInt() * 25
                                if (roundedFeet <= 0) "ARRIVING" else "$roundedFeet FT"
                            } else String.format("%.1f MI", distToDisplayMeters / 1609.34f)

                            val isLive = targetIndex == currentStepIndex
                            Column(modifier = Modifier.fillMaxWidth().background(if (isLive) Color(0xFF005662) else Color(0xFF333333)).padding(horizontal = 20.dp, vertical = 16.dp)) {
                                Text(text = if (isLive) "NEXT MANEUVER" else "PREVIEW: TURN ${targetIndex + 1}", color = if (isLive) Color(0xFF80DEEA) else Color.LightGray, fontSize = 12.sp, fontWeight = FontWeight.Bold, letterSpacing = 2.sp)
                                Spacer(modifier = Modifier.height(6.dp))
                                Text(displayStep.first, color = Color.White, fontSize = 26.sp, fontWeight = FontWeight.Black, lineHeight = 30.sp)
                                Spacer(modifier = Modifier.height(4.dp))
                                if (isLive) Text("In $distDisplay", color = Color(0xFFB2EBF2), fontSize = 18.sp, fontWeight = FontWeight.Bold)
                                else Row { Text("Swipe Right to Return", color = Color(0xFFFF9800), fontSize = 14.sp, fontWeight = FontWeight.Bold); Spacer(Modifier.weight(1f)); Text(distDisplay, color = Color.Gray, fontSize = 14.sp) }
                            }
                        }
                    }
                }
            }

            AnimatedVisibility(visible = missionState == "ACTIVE" && tacticalSteps.isNotEmpty()) {
                var directionsExpanded by remember { mutableStateOf(false) }

                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .background(Color(0xFF2A2A2A))
                        .clickable { directionsExpanded = !directionsExpanded }
                ) {
                    Row(
                        modifier = Modifier.fillMaxWidth().padding(12.dp),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Text("📍 FULL ROUTE MANIFEST", color = Color(0xFFFF9800), fontWeight = FontWeight.Bold, fontSize = 12.sp, letterSpacing = 1.sp)
                        Text(if (directionsExpanded) "HIDE ▲" else "SHOW ▼", color = Color.Gray, fontSize = 12.sp, fontWeight = FontWeight.Bold)
                    }

                    if (directionsExpanded) {
                        Column(
                            modifier = Modifier
                                .fillMaxWidth()
                                .heightIn(max = 250.dp)
                                .background(Color(0xFF1E1E1E))
                                .padding(12.dp)
                                .verticalScroll(rememberScrollState())
                        ) {
                            tacticalSteps.forEachIndexed { index, step ->
                                val isCurrent = index == currentStepIndex
                                val color = if (isCurrent) Color(0xFF00BCD4) else Color.LightGray
                                val weight = if (isCurrent) FontWeight.Black else FontWeight.Normal

                                Text("${index + 1}. ${step.first}", color = color, fontSize = 14.sp, fontWeight = weight, modifier = Modifier.padding(vertical = 6.dp))
                                HorizontalDivider(color = Color(0xFF333333), thickness = 1.dp)
                            }
                        }
                    }
                }
            }

            Box(modifier = Modifier.fillMaxWidth().weight(1f).background(Color(0xFF2A2A2A)), contentAlignment = Alignment.Center) {
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

                Column(
                    modifier = Modifier.fillMaxSize(),
                    verticalArrangement = Arrangement.Center,
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    AnimatedVisibility(
                        visible = missionState == "PENDING" && activeMission != null,
                        enter = slideInVertically(initialOffsetY = { it }) + fadeIn(),
                        exit = slideOutVertically(targetOffsetY = { it }) + fadeOut(),
                        modifier = Modifier.fillMaxSize()
                    ) {
                        Box(modifier = Modifier.fillMaxSize().background(Color(0xEE121212)).padding(24.dp), contentAlignment = Alignment.Center) {
                            Box(modifier = Modifier.fillMaxSize().background(Color(0xFF4CAF50).copy(alpha = flashAlpha)))
                            Column(modifier = Modifier.fillMaxWidth().verticalScroll(rememberScrollState()), horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.spacedBy(10.dp)) {
                                Text("🚨 RESCUE DISPATCH 🚨", color = Color(0xFFF44336), fontSize = 24.sp, fontWeight = FontWeight.Black, letterSpacing = 1.sp, textAlign = TextAlign.Center)
                                Box(modifier = Modifier.fillMaxWidth().height(12.dp).background(Color(0xFF1E1E1E), shape = RoundedCornerShape(8.dp)), contentAlignment = Alignment.CenterStart) {
                                    Box(modifier = Modifier.fillMaxHeight().fillMaxWidth(countdownProgress.value.coerceIn(0f, 1f)).background(Color(0xFF4CAF50), shape = RoundedCornerShape(8.dp)))
                                }
                                val rawBounty = activeMission?.bounty?.replace("$", "")?.toFloatOrNull() ?: 0f
                                Text("GUARANTEED NET PAYOUT", color = Color.LightGray, fontSize = 12.sp, fontWeight = FontWeight.Bold, letterSpacing = 1.sp)
                                Text(String.format("$%.2f", rawBounty * 0.90f), color = Color(0xFF4CAF50), fontSize = 48.sp, fontWeight = FontWeight.Black)
                                Text(activeMission?.intersection ?: "Unknown", color = Color(0xFFFF9800), fontSize = 20.sp, fontWeight = FontWeight.Medium, textAlign = TextAlign.Center)
                                Text(activeMission?.errorCode ?: "Unknown Error", color = Color.Red, fontSize = 18.sp, fontWeight = FontWeight.Bold, textAlign = TextAlign.Center)
                                Row(horizontalArrangement = Arrangement.spacedBy(16.dp), modifier = Modifier.fillMaxWidth()) {
                                    Button(onClick = { missionState = "IDLE"; activeMission = null }, colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF333333)), modifier = Modifier.weight(1f).height(64.dp), shape = RoundedCornerShape(12.dp)) { Text("DECLINE", color = Color.White) }
                                    Button(
                                        onClick = {
                                            coroutineScope.launch {
                                                if (apiClient.acceptMission()) {
                                                    missionState = "ACTIVE"
                                                    if (navPreference == "GOOGLE") {
                                                        val mapIntent = Intent(Intent.ACTION_VIEW, Uri.parse("google.navigation:q=${activeMission!!.lat},${activeMission!!.lon}&mode=d"))
                                                        mapIntent.setPackage("com.google.android.apps.maps")
                                                        try { context.startActivity(mapIntent) } catch (e: Exception) { }
                                                    }
                                                }
                                            }
                                        },
                                        colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF4CAF50)), modifier = Modifier.weight(1f).height(64.dp), shape = RoundedCornerShape(12.dp)
                                    ) { Text("ACCEPT", color = Color.White, fontWeight = FontWeight.Black) }
                                }
                            }
                        }
                    }
                }

                // CAMERA CAPTURE OVERLAY
                Column(
                    modifier = Modifier.fillMaxSize(),
                    verticalArrangement = Arrangement.Center,
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    AnimatedVisibility(
                        visible = capturedProofImage != null && isUploadingProof,
                        enter = fadeIn(), exit = fadeOut(),
                        modifier = Modifier.fillMaxSize()
                    ) {
                        Box(modifier = Modifier.fillMaxSize().background(Color(0xEE000000)).padding(24.dp), contentAlignment = Alignment.Center) {
                            Column(horizontalAlignment = Alignment.CenterHorizontally) {

                                Box(modifier = Modifier.size(300.dp).border(2.dp, Color(0xFF00BCD4), RoundedCornerShape(8.dp)).clip(RoundedCornerShape(8.dp))) {
                                    capturedProofImage?.let { bmp ->
                                        Image(bitmap = bmp.asImageBitmap(), contentDescription = "Proof", modifier = Modifier.fillMaxSize(), contentScale = ContentScale.Crop)
                                    }
                                    Column(modifier = Modifier.align(Alignment.BottomStart).background(Color(0x80000000)).padding(8.dp)) {
                                        Text("GPS: ${agentLocation.latitude}, ${agentLocation.longitude}", color = Color(0xFF00FF00), fontSize = 10.sp, fontFamily = FontFamily.Monospace)
                                        Text("TIMESTAMP: ${System.currentTimeMillis()}", color = Color(0xFF00FF00), fontSize = 10.sp, fontFamily = FontFamily.Monospace)
                                    }
                                }

                                Spacer(modifier = Modifier.height(24.dp))
                                CircularProgressIndicator(color = Color(0xFF00BCD4))
                                Spacer(modifier = Modifier.height(16.dp))

                                if (isSanitizing) {
                                    Text("SANITIZING PII...", color = Color.Red, fontWeight = FontWeight.Black, letterSpacing = 2.sp)
                                    Text("REDACTING FACES & LICENSE PLATES", color = Color.Gray, fontSize = 12.sp)
                                } else {
                                    Text("CRYPTOGRAPHIC WATERMARKING...", color = Color(0xFF00BCD4), fontWeight = FontWeight.Black, letterSpacing = 2.sp)
                                    Text("UPLOADING SECURE PROOF OF WORK", color = Color.Gray, fontSize = 12.sp)
                                }

                                LaunchedEffect(capturedProofImage) {
                                    delay(2000)
                                    val rawBounty = activeMission?.bounty?.replace("$", "")?.toFloatOrNull() ?: 0f
                                    val finalPayout = (rawBounty * 0.90f).toDouble()

                                    if (apiClient.claimEscrowFunds(netPayout = finalPayout)) {
                                        android.widget.Toast.makeText(context, String.format("Proof Accepted. +$%.2f", finalPayout), android.widget.Toast.LENGTH_LONG).show()
                                        if (queuedMission != null) {
                                            activeMission = queuedMission; queuedMission = null; missionState = "ACTIVE"
                                        } else { missionState = "IDLE"; activeMission = null }
                                    } else {
                                        android.widget.Toast.makeText(context, "Network Error: Upload Failed.", android.widget.Toast.LENGTH_LONG).show()
                                    }

                                    isUploadingProof = false
                                    capturedProofImage = null
                                }
                            }
                        }
                    }
                }
            }

            // --- BOTTOM CONTROL PANEL ---
            Column(modifier = Modifier.fillMaxWidth().background(Color(0xFF1E1E1E)).padding(24.dp), horizontalAlignment = Alignment.CenterHorizontally) {

                AnimatedVisibility(visible = missionState == "ACTIVE", enter = expandVertically() + fadeIn(), exit = shrinkVertically() + fadeOut()) {
                    Column(modifier = Modifier.fillMaxWidth(), horizontalAlignment = Alignment.CenterHorizontally) {
                        Text("ACTIVE MISSION: EN ROUTE", color = Color(0xFF00BCD4), fontSize = 14.sp, fontWeight = FontWeight.Black, letterSpacing = 2.sp)
                        Spacer(modifier = Modifier.height(8.dp))
                        Text(activeMission?.intersection ?: "Target Location", color = Color.White, fontSize = 20.sp, fontWeight = FontWeight.Bold)
                        Text("Diagnostic: ${activeMission?.errorCode}", color = Color.LightGray, fontSize = 14.sp)
                        Spacer(modifier = Modifier.height(16.dp))

                        Row(modifier = Modifier.fillMaxWidth().padding(bottom = 12.dp), horizontalArrangement = Arrangement.SpaceEvenly) {
                            if (queuedMission == null) {
                                Button(onClick = { queuedMission = MissionData(33.31, -111.65, "ERR-CLEAN: Interior Debris", "$15.00", "Main St & 1st Ave") }, colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF555555))) { Text("DEV: Inject Queue", fontSize = 10.sp) }
                            } else {
                                Button(onClick = { queuedMission = null }, colors = ButtonDefaults.buttonColors(containerColor = Color(0xFFD32F2F))) { Text("DEV: Sim Queue Stolen", fontSize = 10.sp) }
                            }
                        }

                        val isAtScene = distanceMiles <= 0.1
                        Button(
                            enabled = isAtScene,
                            onClick = { missionState = "ON_SCENE" },
                            colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF00BCD4), disabledContainerColor = Color(0xFF333333)),
                            shape = RoundedCornerShape(8.dp), modifier = Modifier.fillMaxWidth().height(64.dp)
                        ) {
                            if (isAtScene) Text("ARRIVED AT SCENE", color = Color.Black, fontSize = 20.sp, fontWeight = FontWeight.Black, letterSpacing = 1.sp)
                            else Text("APPROACHING SCENE (${String.format("%.1f", distanceMiles)} MI)", color = Color.Gray, fontSize = 16.sp, fontWeight = FontWeight.Bold, letterSpacing = 1.sp)
                        }

                        AnimatedVisibility(visible = queuedMission != null) {
                            Column(modifier = Modifier.fillMaxWidth().padding(top = 12.dp).background(Color(0xFF2A2A2A), RoundedCornerShape(8.dp)).border(1.dp, Color(0xFF4CAF50), RoundedCornerShape(8.dp)).padding(12.dp)) {
                                Row(verticalAlignment = Alignment.CenterVertically) {
                                    Text("🔒 NEXT IN QUEUE (LEVEL 3)", color = Color(0xFF4CAF50), fontSize = 10.sp, fontWeight = FontWeight.Black, letterSpacing = 1.sp)
                                    Spacer(modifier = Modifier.weight(1f))
                                    Text(queuedMission?.bounty ?: "", color = Color.White, fontSize = 12.sp, fontWeight = FontWeight.Bold)
                                }
                                Spacer(modifier = Modifier.height(4.dp))
                                Text(queuedMission?.errorCode ?: "", color = Color.LightGray, fontSize = 14.sp)
                            }
                        }

                        Spacer(modifier = Modifier.height(16.dp))
                        key(abortSliderResetKey) {
                            SwipeActionSlider(text = "SWIPE TO ABORT >>", trackColor = Color(0xFF2C2C2C), thumbColor = Color(0xFFD32F2F)) { showAbortDialog = true }
                        }
                    }
                }

                AnimatedVisibility(visible = missionState == "ON_SCENE", enter = expandVertically() + fadeIn(), exit = shrinkVertically() + fadeOut()) {
                    var terminalLogs by remember { mutableStateOf(listOf("Establishing local UWB connection to AV...", "Connection secured.", "Awaiting physical repair and diagnostic re-run...")) }
                    var isResolving by remember { mutableStateOf(false) }
                    var isResolved by remember { mutableStateOf(false) }
                    val activeCode = activeMission?.errorCode ?: "UNKNOWN"

                    LaunchedEffect(activeMission) { terminalLogs = listOf("Connection secured.", "Awaiting repair..."); isResolving = false; isResolved = false }

                    Column(modifier = Modifier.fillMaxWidth().background(Color(0xFF0D1117)).padding(16.dp), horizontalAlignment = Alignment.CenterHorizontally) {
                        Text("📟 AV DIAGNOSTIC TERMINAL", color = Color(0xFF00FF00), fontSize = 16.sp, fontWeight = FontWeight.Black, letterSpacing = 1.sp)
                        Spacer(modifier = Modifier.height(12.dp))

                        Box(modifier = Modifier.fillMaxWidth().height(140.dp).background(Color.Black, RoundedCornerShape(8.dp)).border(1.dp, Color(0xFF333333), RoundedCornerShape(8.dp)).padding(12.dp)) {
                            Column(modifier = Modifier.verticalScroll(rememberScrollState())) {
                                terminalLogs.forEach { log -> Text("> $log", color = Color(0xFF00FF00), fontFamily = FontFamily.Monospace, fontSize = 12.sp); Spacer(modifier = Modifier.height(4.dp)) }
                            }
                        }
                        Spacer(modifier = Modifier.height(16.dp))

                        if (!isResolved) {
                            Button(
                                enabled = !isResolving,
                                onClick = {
                                    isResolving = true
                                    coroutineScope.launch {
                                        terminalLogs = terminalLogs + "Pinging AV CAN bus..."; delay(1000)
                                        terminalLogs = terminalLogs + "Diagnostic Trouble Codes (DTC) cleared."; delay(800)
                                        isResolving = false; isResolved = true
                                    }
                                },
                                colors = ButtonDefaults.buttonColors(containerColor = Color(0xFFD32F2F), disabledContainerColor = Color(0xFF555555)),
                                modifier = Modifier.fillMaxWidth().height(64.dp), shape = RoundedCornerShape(8.dp)
                            ) { if (isResolving) CircularProgressIndicator(modifier = Modifier.size(24.dp), color = Color.White) else Text("RE-RUN AV DIAGNOSTICS", color = Color.White, fontWeight = FontWeight.Black) }
                        } else {

                            Button(
                                onClick = {
                                    if (hasCameraPermission) {
                                        takePictureLauncher.launch(null)
                                    } else {
                                        cameraPermissionLauncher.launch(Manifest.permission.CAMERA)
                                    }
                                },
                                colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF4CAF50), disabledContainerColor = Color(0xFF555555)),
                                modifier = Modifier.fillMaxWidth().height(64.dp), shape = RoundedCornerShape(8.dp)
                            ) {
                                Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                                    Text("📷", fontSize = 18.sp)
                                    Text("CAPTURE PROOF OF WORK", color = Color.White, fontSize = 13.sp, fontWeight = FontWeight.Black)
                                }
                            }
                        }
                    }
                }

                AnimatedVisibility(visible = !isOnline && missionState != "ACTIVE" && missionState != "ON_SCENE") {
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Row(
                            modifier = Modifier.fillMaxWidth().background(Color(0xFF2A2A2A), RoundedCornerShape(8.dp)).clip(RoundedCornerShape(8.dp)).clickable { isLoadoutExpanded = !isLoadoutExpanded }.padding(16.dp),
                            horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.CenterVertically
                        ) {
                            Text("🛠 MARKET BIDS & LOADOUT", color = Color.White, fontSize = 12.sp, fontWeight = FontWeight.Black, letterSpacing = 1.sp)
                            Text(if (isLoadoutExpanded) "HIDE ▲" else "EXPAND ▼", color = Color(0xFF00BCD4), fontSize = 12.sp, fontWeight = FontWeight.Bold)
                        }

                        AnimatedVisibility(visible = isLoadoutExpanded) {
                            Column(modifier = Modifier.fillMaxWidth().padding(top = 16.dp)) {
                                Text("SERVICE RADIUS: ${serviceRadiusMiles.toInt()} MILES", color = Color.LightGray, fontSize = 12.sp, fontWeight = FontWeight.Bold)
                                Slider(value = serviceRadiusMiles, onValueChange = { serviceRadiusMiles = it }, valueRange = 1f..8f, steps = 6, colors = SliderDefaults.colors(thumbColor = Color(0xFFF44336), activeTrackColor = Color(0xFFF44336)), modifier = Modifier.padding(bottom = 12.dp))
                                Column(modifier = Modifier.fillMaxWidth().heightIn(max = 240.dp).verticalScroll(rememberScrollState()).padding(bottom = 16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                                    agentCapabilities.forEachIndexed { index, cap ->
                                        Column(modifier = Modifier.fillMaxWidth().background(if (!cap.isQualified) Color(0xFF121212) else if (cap.isEnabled) Color(0xFF4CAF50).copy(alpha = 0.1f) else Color(0xFF2A2A2A), RoundedCornerShape(8.dp)).border(1.dp, if (!cap.isQualified) Color(0xFF2A2A2A) else if (cap.isEnabled) Color(0xFF4CAF50) else Color(0xFF444444), RoundedCornerShape(8.dp)).padding(12.dp)) {
                                            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.CenterVertically) {
                                                Text(if (!cap.isQualified) "🔒 ${cap.title}" else cap.title, color = if (!cap.isQualified) Color.DarkGray else Color.White, fontSize = 14.sp, fontWeight = FontWeight.Bold)
                                                if (cap.isQualified) Switch(checked = cap.isEnabled, onCheckedChange = { val n = agentCapabilities.toMutableList(); n[index] = cap.copy(isEnabled = it); agentCapabilities = n }, colors = SwitchDefaults.colors(checkedTrackColor = Color(0xFF4CAF50)))
                                            }
                                        }
                                    }
                                }
                            }
                        }

                        Spacer(modifier = Modifier.height(16.dp))
                    }
                }

                AnimatedVisibility(visible = missionState != "ACTIVE" && missionState != "ON_SCENE") {
                    if (isOnline) {
                        SwipeActionSlider(text = "SWIPE TO GO OFFLINE >>", trackColor = Color(0xFF333333), thumbColor = Color(0xFFF44336)) {
                            isProcessing = true
                            coroutineScope.launch {
                                apiClient.updateAgentStatus(context, false, agentLocation.latitude, agentLocation.longitude, serviceRadiusMiles.toDouble(), emptyMap())

                                // --- THIS KILLS THE BACKGROUND GPS TRACKER ---
                                val serviceIntent = Intent(context, network.proxyagent.pantactical.services.PanLocationService::class.java)
                                context.stopService(serviceIntent)

                                isOnline = false
                                missionState = "IDLE"
                                isProcessing = false
                            }
                        }
                    } else {
                        Button(
                            enabled = !isProcessing,
                            onClick = {
                                isProcessing = true
                                coroutineScope.launch {
                                    val activeLoadout = agentCapabilities.filter { it.isQualified && it.isEnabled }.associate { it.id to it.currentBid }
                                    if (apiClient.updateAgentStatus(context, true, agentLocation.latitude, agentLocation.longitude, serviceRadiusMiles.toDouble(), activeLoadout)) {

                                        // --- THIS STARTS THE BACKGROUND GPS TRACKER ---
                                        val serviceIntent = Intent(context, network.proxyagent.pantactical.services.PanLocationService::class.java)
                                        ContextCompat.startForegroundService(context, serviceIntent)

                                        isOnline = true
                                        coroutineScope.launch(kotlinx.coroutines.Dispatchers.IO) {
                                            apiClient.openLiveDispatchLine("VANGUARD-01") { lat, lon, err, bounty, inter -> activeMission = MissionData(lat, lon, err, bounty, inter); missionState = "PENDING" }
                                        }
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

        AnimatedVisibility(
            visible = currentScreen == "WALLET",
            enter = slideInHorizontally(initialOffsetX = { it }) + fadeIn(), exit = slideOutHorizontally(targetOffsetX = { it }) + fadeOut(),
            modifier = Modifier.fillMaxSize().zIndex(10f)
        ) {
            WalletAndProfileScreen(
                apiClient = apiClient,
                onBack = { currentScreen = "DASHBOARD" },
                navPreference = navPreference,
                onNavPrefChange = { navPreference = it },
                tts = tts,
                availableVoices = availableVoices,
                selectedVoice = selectedVoice,
                onVoiceSelect = { selectedVoice = it }
            )
        }

        if (showAbortDialog) {
            AlertDialog(
                onDismissRequest = { showAbortDialog = false; abortSliderResetKey++ },
                containerColor = Color(0xFF1E1E1E),
                title = { Text("ABORT MISSION", color = Color.White, fontWeight = FontWeight.Black) },
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