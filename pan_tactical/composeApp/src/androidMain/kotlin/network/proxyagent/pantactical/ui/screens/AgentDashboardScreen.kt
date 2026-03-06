package network.proxyagent.pantactical.ui.screens

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.media.AudioManager
import android.media.ToneGenerator
import android.net.Uri
import android.os.Looper
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.animation.*
import androidx.compose.animation.core.*
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.gestures.detectHorizontalDragGestures
import androidx.compose.foundation.horizontalScroll
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
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.layout.onSizeChanged
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.IntOffset
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.core.content.ContextCompat
import kotlinx.coroutines.delay
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch
import network.proxyagent.pantactical.network.PanApiClient
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

data class AgentCapability(
    val id: String,
    val title: String,
    val isQualified: Boolean,
    var isEnabled: Boolean
)

@Composable
fun AgentDashboardScreen() {
    val context = LocalContext.current
    val coroutineScope = rememberCoroutineScope()
    val apiClient = remember { PanApiClient() }

    var isOnline by remember { mutableStateOf(false) }
    var isProcessing by remember { mutableStateOf(false) }
    var errorMessage by remember { mutableStateOf<String?>(null) }
    var missionState by remember { mutableStateOf("IDLE") }
    var serviceRadiusMiles by remember { mutableStateOf(5f) }

    var showAbortDialog by remember { mutableStateOf(false) }
    var abortSliderResetKey by remember { mutableIntStateOf(0) }

    var agentCapabilities by remember {
        mutableStateOf(listOf(
            AgentCapability("clean", "Cabin Cleanup", isQualified = true, isEnabled = true),
            AgentCapability("air", "Tire Pressure", isQualified = true, isEnabled = true),
            AgentCapability("jump", "Jump Start", isQualified = true, isEnabled = true),
            AgentCapability("sensor", "Sensor Reset", isQualified = false, isEnabled = false),
            AgentCapability("drive", "Manual Override", isQualified = false, isEnabled = false)
        ))
    }

    var activeMission by remember { mutableStateOf<MissionData?>(null) }
    var tacticalRoute by remember { mutableStateOf<List<LatLng>>(emptyList()) }

    // --- NEW: HUD TRACKING STATE ---
    var tacticalSteps by remember { mutableStateOf<List<Triple<String, Double, Double>>>(emptyList()) }
    var currentStepIndex by remember { mutableIntStateOf(0) }
    var hasEnteredManeuverZone by remember { mutableStateOf(false) } // NEW: Intersection entry flag

    var agentLocation by remember { mutableStateOf(LatLng(33.3061, -111.6601)) }
    var locationPermissionGranted by remember { mutableStateOf(false) }

    val countdownProgress = remember { Animatable(1f) }
    var isFlashing by remember { mutableStateOf(false) }
    val flashAlpha by animateFloatAsState(
        targetValue = if (isFlashing) 0.2f else 0f,
        animationSpec = tween(durationMillis = 150), label = "flash"
    )

    var hasInitializedAudio by remember { mutableStateOf(false) }
    LaunchedEffect(isOnline) {
        if (!hasInitializedAudio) {
            hasInitializedAudio = true
            return@LaunchedEffect
        }
        val statusToneGen = ToneGenerator(AudioManager.STREAM_ALARM, 100)
        try {
            if (isOnline) {
                statusToneGen.startTone(ToneGenerator.TONE_PROP_ACK, 100)
                delay(150)
                statusToneGen.startTone(ToneGenerator.TONE_PROP_ACK, 100)
            } else {
                statusToneGen.startTone(ToneGenerator.TONE_PROP_NACK, 250)
            }
            delay(300)
        } finally {
            statusToneGen.release()
        }
    }

    LaunchedEffect(missionState) {
        if (missionState == "PENDING") {
            launch {
                val durationMs = 10000L
                val startTime = System.currentTimeMillis()
                var elapsed = 0L

                while (elapsed < durationMs && missionState == "PENDING") {
                    elapsed = System.currentTimeMillis() - startTime
                    val remainingPercentage = 1f - (elapsed.toFloat() / durationMs.toFloat())
                    countdownProgress.snapTo(remainingPercentage.coerceAtLeast(0f))
                    delay(16L)
                }

                if (missionState == "PENDING") {
                    missionState = "IDLE"
                    activeMission = null
                }
            }

            launch {
                val toneGen = ToneGenerator(AudioManager.STREAM_ALARM, 100)
                try {
                    while (isActive && countdownProgress.value > 0f && missionState == "PENDING") {
                        isFlashing = true
                        toneGen.startTone(ToneGenerator.TONE_CDMA_ALERT_CALL_GUARD, 150)
                        delay(150)
                        isFlashing = false
                        delay(1850)
                    }
                } finally {
                    toneGen.release()
                }
            }
        }
    }

    val fusedLocationClient = remember { LocationServices.getFusedLocationProviderClient(context) }
    val locationCallback = remember {
        object : LocationCallback() {
            override fun onLocationResult(locationResult: LocationResult) {
                for (location in locationResult.locations) {
                    agentLocation = LatLng(location.latitude, location.longitude)
                }
            }
        }
    }

    val permissionLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestMultiplePermissions(),
        onResult = { permissions ->
            locationPermissionGranted = permissions[Manifest.permission.ACCESS_FINE_LOCATION] == true || permissions[Manifest.permission.ACCESS_COARSE_LOCATION] == true
        }
    )

    LaunchedEffect(Unit) {
        val fineLocation = ContextCompat.checkSelfPermission(context, Manifest.permission.ACCESS_FINE_LOCATION) == PackageManager.PERMISSION_GRANTED
        if (fineLocation) locationPermissionGranted = true
        else permissionLauncher.launch(arrayOf(Manifest.permission.ACCESS_FINE_LOCATION, Manifest.permission.ACCESS_COARSE_LOCATION))
    }

    LaunchedEffect(locationPermissionGranted) {
        if (locationPermissionGranted) {
            val locationRequest = LocationRequest.Builder(Priority.PRIORITY_HIGH_ACCURACY, 5000).setMinUpdateDistanceMeters(2f).build()
            try { fusedLocationClient.requestLocationUpdates(locationRequest, locationCallback, Looper.getMainLooper()) }
            catch (e: SecurityException) { println("GPS ERROR: Permission denied.") }
        }
    }

    LaunchedEffect(activeMission) {
        if (activeMission != null) {
            val routeData = apiClient.getTacticalRoute(
                startLat = agentLocation.latitude,
                startLon = agentLocation.longitude,
                endLat = activeMission!!.lat,
                endLon = activeMission!!.lon
            )
            tacticalRoute = routeData.first
            tacticalSteps = routeData.second
            currentStepIndex = 0 // Reset the HUD tracker
            hasEnteredManeuverZone = false // Reset the flag for the new route
        } else {
            tacticalRoute = emptyList()
            tacticalSteps = emptyList()
            currentStepIndex = 0
        }
    }

    val distanceMiles = remember(agentLocation, activeMission) {
        if (activeMission == null) return@remember 0.0
        val results = FloatArray(1)
        android.location.Location.distanceBetween(agentLocation.latitude, agentLocation.longitude, activeMission!!.lat, activeMission!!.lon, results)
        (results[0] / 1609.34)
    }

    val dynamicZoom = remember(serviceRadiusMiles) { 14.2f - log2(serviceRadiusMiles) }
    val cameraPositionState = rememberCameraPositionState { position = CameraPosition.fromLatLngZoom(agentLocation, dynamicZoom) }

    LaunchedEffect(agentLocation, serviceRadiusMiles) {
        if (!cameraPositionState.isMoving) {
            cameraPositionState.position = CameraPosition.fromLatLngZoom(agentLocation, dynamicZoom)
        }
    }

    val tacticalMapStyle = """
        [
          { "elementType": "geometry", "stylers": [{ "color": "#121212" }] },
          { "elementType": "labels.icon", "stylers": [{ "visibility": "off" }] },
          { "elementType": "labels.text.fill", "stylers": [{ "color": "#EEEEEE" }] },
          { "elementType": "labels.text.stroke", "stylers": [{ "color": "#000000" }, { "weight": 3 }] },
          { "featureType": "administrative", "elementType": "geometry", "stylers": [{ "color": "#757575" }] },
          { "featureType": "water", "elementType": "geometry", "stylers": [{ "color": "#000000" }] },
          { "featureType": "road", "elementType": "geometry", "stylers": [{ "color": "#555555" }] },
          { "featureType": "road.highway", "elementType": "geometry", "stylers": [{ "color": "#9E9E9E" }] },
          { "featureType": "road.arterial", "elementType": "geometry", "stylers": [{ "color": "#777777" }] },
          { "featureType": "road.local", "elementType": "geometry", "stylers": [{ "color": "#444444" }] }
        ]
    """.trimIndent()
    val mapProperties by remember { mutableStateOf(MapProperties(mapStyleOptions = MapStyleOptions(tacticalMapStyle), isMyLocationEnabled = locationPermissionGranted)) }
    val mapUiSettings by remember { mutableStateOf(MapUiSettings(zoomControlsEnabled = false, myLocationButtonEnabled = false)) }

    Box(modifier = Modifier.fillMaxSize()) {
        Column(modifier = Modifier.fillMaxSize().background(Color(0xFF121212)).systemBarsPadding()) {

            Row(
                modifier = Modifier.fillMaxWidth().background(Color(0xFF1E1E1E)).padding(16.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text("PAN COMMAND", color = Color.White, fontSize = 20.sp, fontWeight = FontWeight.Bold, letterSpacing = 1.sp)
                Text(
                    text = if (isOnline) "🟢 ONLINE" else "🔴 OFFLINE",
                    color = if (isOnline) Color(0xFF4CAF50) else Color(0xFFF44336),
                    fontSize = 14.sp, fontWeight = FontWeight.Bold
                )
            }

            // --- THE NEW TURN-BY-TURN HUD BANNER ---
            AnimatedVisibility(visible = missionState == "ACTIVE" && tacticalSteps.isNotEmpty()) {
                val currentStep = tacticalSteps.getOrNull(currentStepIndex)

                if (currentStep != null) {
                    // Calculate exactly how far away the physical turn is from the agent's GPS
                    val results = FloatArray(1)
                    android.location.Location.distanceBetween(agentLocation.latitude, agentLocation.longitude, currentStep.second, currentStep.third, results)
                    val distToManeuverMeters = results[0]

                    // UPGRADED GEOFENCE: The "Exit Trigger" Logic
                    LaunchedEffect(distToManeuverMeters) {
                        if (distToManeuverMeters < 15f) {
                            // 1. Agent has entered the intersection (within ~50 feet)
                            hasEnteredManeuverZone = true
                        } else if (hasEnteredManeuverZone && distToManeuverMeters > 30f) {
                            // 2. Agent has completed the turn and is driving away (passed ~100 feet)
                            if (currentStepIndex < tacticalSteps.size - 1) {
                                currentStepIndex++
                                hasEnteredManeuverZone = false // Reset for the NEXT turn
                            }
                        }
                    }

                    // Format the display text with 25-foot rounding for clean UX
                    val distDisplay = if (distToManeuverMeters < 160.9f) { // Under 0.1 miles
                        val rawFeet = distToManeuverMeters * 3.28084
                        // Divide by 25, round to nearest whole number, then multiply back by 25
                        val roundedFeet = (rawFeet / 25.0).roundToInt() * 25

                        // Prevent it from saying "0 FT" if they are right on top of it
                        if (roundedFeet <= 0) "ARRIVING" else "$roundedFeet FT"
                    } else {
                        String.format("%.1f MI", distToManeuverMeters / 1609.34f)
                    }

                    Column(
                        modifier = Modifier.fillMaxWidth().background(Color(0xFF005662)).padding(horizontal = 20.dp, vertical = 16.dp)
                    ) {
                        Text("NEXT MANEUVER", color = Color(0xFF80DEEA), fontSize = 12.sp, fontWeight = FontWeight.Bold, letterSpacing = 2.sp)
                        Spacer(modifier = Modifier.height(6.dp))
                        Text(currentStep.first, color = Color.White, fontSize = 26.sp, fontWeight = FontWeight.Black, lineHeight = 30.sp)
                        Spacer(modifier = Modifier.height(4.dp))
                        Text("In $distDisplay", color = Color(0xFFB2EBF2), fontSize = 18.sp, fontWeight = FontWeight.Bold)
                    }
                }
            }

            // --- THE FALLBACK ROUTE MANIFEST DRAWER ---
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
                                // Highlight the currently active step in bright cyan!
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

            Box(
                modifier = Modifier.fillMaxWidth().weight(1f).background(Color(0xFF2A2A2A)),
                contentAlignment = Alignment.Center
            ) {
                GoogleMap(
                    modifier = Modifier.fillMaxSize(),
                    cameraPositionState = cameraPositionState,
                    properties = mapProperties,
                    uiSettings = mapUiSettings
                ) {
                    Marker(state = MarkerState(position = agentLocation), title = "VANGUARD-01")
                    if (missionState != "ACTIVE" && missionState != "ON_SCENE") {
                        Circle(center = agentLocation, radius = serviceRadiusMiles.toDouble() * 1609.34, fillColor = Color(0x1AF44336), strokeColor = Color(0x80F44336), strokeWidth = 3f)
                    }

                    activeMission?.let { mission ->
                        val targetLocation = LatLng(mission.lat, mission.lon)
                        Marker(state = MarkerState(position = targetLocation), title = "🚨 STRANDED AV")

                        if (tacticalRoute.isNotEmpty()) {
                            Polyline(points = tacticalRoute, color = Color(0xFFFF9800), width = 14f, geodesic = true)
                        } else {
                            Polyline(points = listOf(agentLocation, targetLocation), color = Color(0xFFF44336).copy(alpha = 0.5f), width = 8f, geodesic = true)
                        }
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

                            Column(modifier = Modifier.fillMaxWidth(), horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.spacedBy(16.dp)) {

                                Text("🚨 RESCUE DISPATCH 🚨", color = Color(0xFFF44336), fontSize = 24.sp, fontWeight = FontWeight.Black, letterSpacing = 1.sp, textAlign = TextAlign.Center, maxLines = 1)

                                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                                    Text("ESTIMATED PAYOUT", color = Color.LightGray, fontSize = 14.sp, fontWeight = FontWeight.Bold)
                                    Text(activeMission?.bounty ?: "$0.00", color = Color(0xFF4CAF50), fontSize = 56.sp, fontWeight = FontWeight.Black)
                                }

                                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                                    Text("DISTANCE", color = Color.LightGray, fontSize = 14.sp, fontWeight = FontWeight.Bold)
                                    Text(String.format("%.1f Miles Away", distanceMiles), color = Color.White, fontSize = 32.sp, fontWeight = FontWeight.Bold)
                                }

                                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                                    Text("INTERSECTION", color = Color.LightGray, fontSize = 14.sp, fontWeight = FontWeight.Bold)
                                    Text(activeMission?.intersection ?: "Unknown", color = Color(0xFFFF9800), fontSize = 24.sp, fontWeight = FontWeight.Medium, textAlign = TextAlign.Center)
                                }

                                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                                    Text("DIAGNOSTIC CODE", color = Color.LightGray, fontSize = 14.sp, fontWeight = FontWeight.Bold)
                                    Text(activeMission?.errorCode ?: "Unknown Error", color = Color.Red, fontSize = 20.sp, fontWeight = FontWeight.Bold, textAlign = TextAlign.Center)
                                }

                                Spacer(modifier = Modifier.height(8.dp))

                                Row(horizontalArrangement = Arrangement.spacedBy(16.dp), modifier = Modifier.fillMaxWidth()) {
                                    Button(
                                        onClick = { missionState = "IDLE"; activeMission = null },
                                        colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF333333)),
                                        shape = RoundedCornerShape(12.dp),
                                        modifier = Modifier.weight(1f).height(72.dp)
                                    ) { Text("DECLINE", color = Color.White, fontSize = 20.sp, fontWeight = FontWeight.Bold) }

                                    Button(
                                        onClick = {
                                            coroutineScope.launch {
                                                val claimed = apiClient.acceptMission()
                                                if (claimed) {
                                                    missionState = "ACTIVE"
                                                    activeMission?.let { target ->
                                                        val gmmIntentUri = Uri.parse("google.navigation:q=${target.lat},${target.lon}&mode=d")
                                                        val mapIntent = Intent(Intent.ACTION_VIEW, gmmIntentUri)
                                                        mapIntent.setPackage("com.google.android.apps.maps")
                                                        try { context.startActivity(mapIntent) } catch (e: Exception) { println("NAV ERROR") }
                                                    }
                                                } else {
                                                    android.widget.Toast.makeText(context, "Network Error: Server rejected claim.", android.widget.Toast.LENGTH_LONG).show()
                                                }
                                            }
                                        },
                                        colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF4CAF50)),
                                        shape = RoundedCornerShape(12.dp),
                                        modifier = Modifier.weight(1f).height(72.dp)
                                    ) { Text("ACCEPT", color = Color.White, fontSize = 20.sp, fontWeight = FontWeight.Black) }
                                }

                                Box(modifier = Modifier.fillMaxWidth().height(25.dp).background(Color(0xFF1E1E1E), shape = RoundedCornerShape(4.dp)), contentAlignment = Alignment.CenterEnd) {
                                    Box(modifier = Modifier.fillMaxHeight().fillMaxWidth(countdownProgress.value).background(Color(0xFF4CAF50), shape = RoundedCornerShape(4.dp)))
                                }
                            }
                        }
                    }
                }
            }

            // --- BOTTOM ACTION BAR: EN-ROUTE & LOADOUT UI ---
            Column(
                modifier = Modifier.fillMaxWidth().background(Color(0xFF1E1E1E)).padding(24.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {

                AnimatedVisibility(
                    visible = missionState == "ACTIVE",
                    enter = expandVertically() + fadeIn(),
                    exit = shrinkVertically() + fadeOut()
                ) {
                    Column(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        Text("ACTIVE MISSION: EN ROUTE", color = Color(0xFF00BCD4), fontSize = 14.sp, fontWeight = FontWeight.Black, letterSpacing = 2.sp)
                        Spacer(modifier = Modifier.height(8.dp))
                        Text(activeMission?.intersection ?: "Target Location", color = Color.White, fontSize = 20.sp, fontWeight = FontWeight.Bold)
                        Text("Diagnostic: ${activeMission?.errorCode}", color = Color.LightGray, fontSize = 14.sp)
                        Spacer(modifier = Modifier.height(16.dp))

                        val isAtScene = distanceMiles <= 0.1

                        Button(
                            enabled = isAtScene,
                            onClick = { missionState = "ON_SCENE" },
                            colors = ButtonDefaults.buttonColors(
                                containerColor = Color(0xFF00BCD4),
                                disabledContainerColor = Color(0xFF333333)
                            ),
                            shape = RoundedCornerShape(8.dp),
                            modifier = Modifier.fillMaxWidth().height(64.dp)
                        ) {
                            if (isAtScene) {
                                Text("ARRIVED AT SCENE", color = Color.Black, fontSize = 20.sp, fontWeight = FontWeight.Black, letterSpacing = 1.sp)
                            } else {
                                Text("APPROACHING SCENE (${String.format("%.1f", distanceMiles)} MI)", color = Color.Gray, fontSize = 16.sp, fontWeight = FontWeight.Bold, letterSpacing = 1.sp)
                            }
                        }

                        Spacer(modifier = Modifier.height(16.dp))

                        key(abortSliderResetKey) {
                            SwipeActionSlider(
                                text = "SWIPE TO ABORT >>",
                                trackColor = Color(0xFF2C2C2C),
                                thumbColor = Color(0xFFD32F2F),
                                onSwipeComplete = {
                                    showAbortDialog = true
                                }
                            )
                        }
                    }
                }

                AnimatedVisibility(
                    visible = !isOnline && missionState != "ACTIVE",
                    enter = expandVertically() + fadeIn(),
                    exit = shrinkVertically() + fadeOut()
                ) {
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {

                        Text("ACTIVE LOADOUT", color = Color.LightGray, fontSize = 12.sp, fontWeight = FontWeight.Bold, letterSpacing = 1.sp)
                        Spacer(modifier = Modifier.height(8.dp))

                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .horizontalScroll(rememberScrollState())
                                .padding(bottom = 16.dp),
                            horizontalArrangement = Arrangement.spacedBy(12.dp)
                        ) {
                            agentCapabilities.forEachIndexed { index, cap ->
                                val bgColor = when {
                                    !cap.isQualified -> Color(0xFF121212)
                                    cap.isEnabled -> Color(0xFF4CAF50).copy(alpha = 0.15f)
                                    else -> Color(0xFF333333)
                                }
                                val borderColor = when {
                                    !cap.isQualified -> Color(0xFF2A2A2A)
                                    cap.isEnabled -> Color(0xFF4CAF50)
                                    else -> Color(0xFF555555)
                                }
                                val textColor = when {
                                    !cap.isQualified -> Color.DarkGray
                                    cap.isEnabled -> Color(0xFF4CAF50)
                                    else -> Color.LightGray
                                }

                                Surface(
                                    shape = RoundedCornerShape(6.dp),
                                    color = bgColor,
                                    border = BorderStroke(1.dp, borderColor),
                                    modifier = Modifier.clickable(enabled = cap.isQualified) {
                                        val newList = agentCapabilities.toMutableList()
                                        newList[index] = cap.copy(isEnabled = !cap.isEnabled)
                                        agentCapabilities = newList
                                    }
                                ) {
                                    Row(
                                        modifier = Modifier.padding(
                                            horizontal = 14.dp,
                                            vertical = 10.dp
                                        ), verticalAlignment = Alignment.CenterVertically
                                    ) {
                                        if (!cap.isQualified) Text("🔒 ", fontSize = 12.sp)
                                        Text(cap.title.uppercase(), color = textColor, fontSize = 12.sp, fontWeight = FontWeight.Bold)
                                    }
                                }
                            }
                        }

                        Text("SERVICE RADIUS: ${serviceRadiusMiles.toInt()} MILES", color = Color.LightGray, fontSize = 12.sp, fontWeight = FontWeight.Bold, letterSpacing = 1.sp)
                        Slider(
                            value = serviceRadiusMiles,
                            onValueChange = { serviceRadiusMiles = it },
                            valueRange = 1f..8f,
                            steps = 6,
                            colors = SliderDefaults.colors(
                                thumbColor = Color(0xFFF44336),
                                activeTrackColor = Color(0xFFF44336),
                                inactiveTrackColor = Color.DarkGray
                            ),
                            modifier = Modifier.padding(bottom = 16.dp)
                        )
                    }
                }

                AnimatedVisibility(
                    visible = missionState != "ACTIVE",
                    enter = expandVertically() + fadeIn(),
                    exit = shrinkVertically() + fadeOut()
                ) {
                    if (isOnline) {
                        SwipeActionSlider(
                            text = "SWIPE TO GO OFFLINE >>",
                            trackColor = Color(0xFF333333),
                            thumbColor = Color(0xFFF44336),
                            textColor = Color.LightGray.copy(alpha = 0.5f),
                            onSwipeComplete = {
                                isProcessing = true
                                coroutineScope.launch {
                                    val success = apiClient.updateAgentStatus(
                                        context, false, agentLocation.latitude, agentLocation.longitude, serviceRadiusMiles.toDouble(), emptyList()
                                    )
                                    if (success) {
                                        isOnline = false
                                        activeMission = null
                                        missionState = "IDLE"
                                    }
                                    isProcessing = false
                                }
                            }
                        )
                    } else {
                        Button(
                            enabled = !isProcessing,
                            onClick = {
                                isProcessing = true
                                coroutineScope.launch {
                                    val activeLoadout = agentCapabilities.filter { it.isQualified && it.isEnabled }.map { it.id }
                                    val success = apiClient.updateAgentStatus(
                                        context, true, agentLocation.latitude, agentLocation.longitude, serviceRadiusMiles.toDouble(), activeLoadout
                                    )

                                    if (success) {
                                        isOnline = true
                                        coroutineScope.launch(kotlinx.coroutines.Dispatchers.IO) {
                                            apiClient.openLiveDispatchLine("VANGUARD-01") { lat, lon, err, bounty, inter ->
                                                activeMission = MissionData(lat, lon, err, bounty, inter)
                                                missionState = "PENDING"
                                            }
                                        }
                                    }
                                    isProcessing = false
                                }
                            },
                            modifier = Modifier.fillMaxWidth().height(56.dp),
                            colors = ButtonDefaults.buttonColors(
                                containerColor = Color(0xFF2E7D32),
                                disabledContainerColor = Color(0xFF555555)
                            )
                        ) {
                            if (isProcessing) CircularProgressIndicator(modifier = Modifier.size(24.dp), color = Color.White, strokeWidth = 2.dp)
                            else Text("GO ONLINE", color = Color.White, fontWeight = FontWeight.Bold, letterSpacing = 1.sp)
                        }
                    }
                }
            }
        }

        // --- THE ABORT REASON DIALOG ---
        if (showAbortDialog) {
            AlertDialog(
                onDismissRequest = {
                    showAbortDialog = false
                    abortSliderResetKey++
                },
                containerColor = Color(0xFF1E1E1E),
                title = { Text("ABORT MISSION", color = Color.White, fontWeight = FontWeight.Black) },
                text = {
                    Column {
                        Text("Please select a reason for aborting:", color = Color.LightGray, fontSize = 14.sp)
                        Spacer(modifier = Modifier.height(16.dp))

                        val reasons = listOf("Too Dangerous", "Changed Mind", "Can't Find AV", "AV Leaving Scene", "Other")
                        reasons.forEach { reason ->
                            Button(
                                onClick = {
                                    println("🚨 MISSION ABORTED: $reason")
                                    showAbortDialog = false
                                    missionState = "IDLE"
                                    activeMission = null
                                    abortSliderResetKey++
                                },
                                colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF333333)),
                                modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp),
                                shape = RoundedCornerShape(8.dp)
                            ) {
                                Text(reason, color = Color.White, fontWeight = FontWeight.Bold)
                            }
                        }
                    }
                },
                confirmButton = {},
                dismissButton = {
                    TextButton(onClick = {
                        showAbortDialog = false
                        abortSliderResetKey++
                    }) {
                        Text("CANCEL", color = Color.Gray)
                    }
                }
            )
        }
    }
}

@Composable
fun SwipeActionSlider(
    modifier: Modifier = Modifier,
    text: String,
    trackColor: Color = Color(0xFF2C2C2C),
    thumbColor: Color = Color(0xFFD32F2F),
    textColor: Color = Color.Red.copy(alpha = 0.5f),
    onSwipeComplete: () -> Unit
) {
    val thumbSize = 64.dp
    val trackHeight = 64.dp
    val swipeState = remember { Animatable(0f) }
    val coroutineScope = rememberCoroutineScope()
    var trackWidthPx by remember { mutableStateOf(0f) }

    val density = LocalDensity.current
    val thumbSizePx = with(density) { thumbSize.toPx() }

    Box(
        modifier = modifier
            .fillMaxWidth()
            .height(trackHeight)
            .clip(RoundedCornerShape(8.dp))
            .background(trackColor)
            .onSizeChanged { trackWidthPx = it.width.toFloat() },
        contentAlignment = Alignment.CenterStart
    ) {

        Box(
            modifier = Modifier
                .fillMaxHeight()
                .width(with(density) { (swipeState.value + thumbSizePx).toDp() })
                .clip(RoundedCornerShape(8.dp))
                .background(thumbColor.copy(alpha = 0.5f))
        )

        Text(
            text = text,
            color = textColor,
            modifier = Modifier.fillMaxWidth(),
            textAlign = TextAlign.Center,
            fontWeight = FontWeight.Bold,
            letterSpacing = 2.sp
        )

        Box(
            modifier = Modifier
                .offset { IntOffset(swipeState.value.roundToInt(), 0) }
                .size(thumbSize)
                .clip(RoundedCornerShape(8.dp))
                .background(thumbColor)
                .pointerInput(Unit) {
                    detectHorizontalDragGestures(
                        onDragEnd = {
                            val threshold = trackWidthPx - thumbSizePx
                            if (swipeState.value >= threshold * 0.85f) {
                                coroutineScope.launch {
                                    swipeState.snapTo(threshold)
                                    onSwipeComplete()
                                }
                            } else {
                                coroutineScope.launch { swipeState.animateTo(0f) }
                            }
                        }
                    ) { change, dragAmount ->
                        change.consume()
                        coroutineScope.launch {
                            val newOffset = (swipeState.value + dragAmount).coerceIn(0f, trackWidthPx - thumbSizePx)
                            swipeState.snapTo(newOffset)
                        }
                    }
                },
            contentAlignment = Alignment.Center
        ) {
            Text(">>", color = Color.White, fontWeight = FontWeight.Black, fontSize = 20.sp)
        }
    }
}