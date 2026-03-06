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
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.core.content.ContextCompat
import kotlinx.coroutines.delay
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch
import network.proxyagent.pantactical.network.PanApiClient
import kotlin.math.log2

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

// --- NEW: TACTICAL LOADOUT DATA MODEL ---
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

    // --- NEW: AGENT LOADOUT STATE ---
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
    var agentLocation by remember { mutableStateOf(LatLng(33.3061, -111.6601)) }
    var locationPermissionGranted by remember { mutableStateOf(false) }

    val countdownProgress = remember { Animatable(1f) }
    var isFlashing by remember { mutableStateOf(false) }
    val flashAlpha by animateFloatAsState(
        targetValue = if (isFlashing) 0.2f else 0f,
        animationSpec = tween(durationMillis = 150), label = "flash"
    )

    // --- FIXED: SYSTEM LOGIN/LOGOUT AUDIO ---
    var hasInitializedAudio by remember { mutableStateOf(false) }
    LaunchedEffect(isOnline) {
        if (!hasInitializedAudio) {
            hasInitializedAudio = true
            return@LaunchedEffect
        }

        // UPGRADE: Switched to STREAM_ALARM so it bypasses muted system/notification volumes!
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
                Circle(center = agentLocation, radius = serviceRadiusMiles.toDouble() * 1609.34, fillColor = Color(0x1AF44336), strokeColor = Color(0x80F44336), strokeWidth = 3f)

                activeMission?.let { mission ->
                    val targetLocation = LatLng(mission.lat, mission.lon)
                    Marker(state = MarkerState(position = targetLocation), title = "🚨 STRANDED AV")
                    Polyline(points = listOf(agentLocation, targetLocation), color = Color(0xFFF44336), width = 8f, geodesic = true)
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
                                        missionState = "ACTIVE"
                                        activeMission?.let { target ->
                                            val gmmIntentUri = Uri.parse("google.navigation:q=${target.lat},${target.lon}&mode=d")
                                            val mapIntent = Intent(Intent.ACTION_VIEW, gmmIntentUri)
                                            mapIntent.setPackage("com.google.android.apps.maps")
                                            try { context.startActivity(mapIntent) } catch (e: Exception) { println("NAV ERROR") }
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

        // --- BOTTOM ACTION BAR: SLIDER & LOADOUT ---
        Column(
            modifier = Modifier.fillMaxWidth().background(Color(0xFF1E1E1E)).padding(24.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            AnimatedVisibility(
                visible = !isOnline,
                enter = expandVertically() + fadeIn(),
                exit = shrinkVertically() + fadeOut()
            ) {
                Column(horizontalAlignment = Alignment.CenterHorizontally) {

                    // --- NEW: TACTICAL LOADOUT TOGGLES ---
                    Text("ACTIVE LOADOUT", color = Color.LightGray, fontSize = 12.sp, fontWeight = FontWeight.Bold, letterSpacing = 1.sp)
                    Spacer(modifier = Modifier.height(8.dp))

                    // Horizontally scrolling row of Data Pills
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .horizontalScroll(rememberScrollState())
                            .padding(bottom = 16.dp),
                        horizontalArrangement = Arrangement.spacedBy(12.dp)
                    ) {
                        agentCapabilities.forEachIndexed { index, cap ->

                            // Determine the aesthetic state of the pill
                            val bgColor = when {
                                !cap.isQualified -> Color(0xFF121212) // Pitch black for locked
                                cap.isEnabled -> Color(0xFF4CAF50).copy(alpha = 0.15f) // Glowing Green
                                else -> Color(0xFF333333) // Dimmed Gray
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

                            // The Data Pill UI
                            Surface(
                                shape = RoundedCornerShape(6.dp),
                                color = bgColor,
                                border = BorderStroke(1.dp, borderColor),
                                modifier = Modifier.clickable(enabled = cap.isQualified) {
                                    // Toggle the specific capability ON/OFF
                                    val newList = agentCapabilities.toMutableList()
                                    newList[index] = cap.copy(isEnabled = !cap.isEnabled)
                                    agentCapabilities = newList
                                }
                            ) {
                                Row(
                                    modifier = Modifier.padding(horizontal = 14.dp, vertical = 10.dp),
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    if (!cap.isQualified) {
                                        Text("🔒 ", fontSize = 12.sp)
                                    }
                                    Text(cap.title.uppercase(), color = textColor, fontSize = 12.sp, fontWeight = FontWeight.Bold)
                                }
                            }
                        }
                    }

                    // --- THE RADIUS SLIDER ---
                    Text("SERVICE RADIUS: ${serviceRadiusMiles.toInt()} MILES", color = Color.LightGray, fontSize = 12.sp, fontWeight = FontWeight.Bold, letterSpacing = 1.sp)
                    Slider(
                        value = serviceRadiusMiles, onValueChange = { serviceRadiusMiles = it }, valueRange = 1f..8f, steps = 6,
                        colors = SliderDefaults.colors(thumbColor = Color(0xFFF44336), activeTrackColor = Color(0xFFF44336), inactiveTrackColor = Color.DarkGray),
                        modifier = Modifier.padding(bottom = 16.dp)
                    )
                }
            }

            Button(
                enabled = !isProcessing,
                onClick = {
                    if (missionState == "ACTIVE") {
                        missionState = "IDLE"
                        activeMission = null
                        return@Button
                    }
                    isProcessing = true
                    errorMessage = null

                    coroutineScope.launch {
                        val targetState = !isOnline

                        // --- NEW: EXTRACT THE ACTIVE LOADOUT ---
                        // We filter the list so we ONLY send the IDs of the items that are both Qualified AND Enabled.
                        val activeLoadout = agentCapabilities
                            .filter { it.isQualified && it.isEnabled }
                            .map { it.id }

                        // Pass the activeLoadout into the API call
                        val success = apiClient.updateAgentStatus(
                            context, targetState, agentLocation.latitude, agentLocation.longitude, serviceRadiusMiles.toDouble(), activeLoadout
                        )

                        if (success) {
                            isOnline = targetState
                            if (isOnline) {
                                coroutineScope.launch(kotlinx.coroutines.Dispatchers.IO) {
                                    apiClient.openLiveDispatchLine("VANGUARD-01") { lat, lon, err, bounty, inter ->
                                        activeMission = MissionData(lat, lon, err, bounty, inter)
                                        missionState = "PENDING"
                                    }
                                }
                            } else {
                                activeMission = null
                                missionState = "IDLE"
                            }
                        } else {
                            errorMessage = "Failed to establish secure handshake."
                        }
                        isProcessing = false
                    }
                },
                modifier = Modifier.fillMaxWidth().height(56.dp),
                colors = ButtonDefaults.buttonColors(containerColor = if (isOnline) Color(0xFFF44336) else Color(0xFF2E7D32), disabledContainerColor = Color(0xFF555555))
            ) {
                if (isProcessing) CircularProgressIndicator(modifier = Modifier.size(24.dp), color = Color.White, strokeWidth = 2.dp)
                else Text(
                    when { missionState == "ACTIVE" -> "ABORT MISSION"; isOnline -> "GO OFFLINE"; else -> "GO ONLINE" },
                    color = Color.White, fontWeight = FontWeight.Bold, letterSpacing = 1.sp
                )
            }
        }
    }
}