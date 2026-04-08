package com.pan.tactical.ui

import android.graphics.BitmapFactory
import androidx.biometric.BiometricManager
import androidx.biometric.BiometricPrompt
import androidx.core.content.ContextCompat
import androidx.fragment.app.FragmentActivity
import androidx.compose.ui.platform.LocalContext
import androidx.compose.animation.*
import androidx.compose.animation.core.*
import androidx.compose.foundation.ExperimentalFoundationApi
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.combinedClickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.runtime.saveable.Saver
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalUriHandler
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.zIndex
import androidx.lifecycle.viewmodel.compose.viewModel
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.jetbrains.compose.resources.painterResource
import kotlin.math.*
import kotlin.math.roundToInt // 🛡️ FIXED: Explicit import for KMP
import com.pan.tactical.BuildConfig // 🛡️ FIXED: Required for environment check
import com.pan.tactical.ui.components.OfflineLoadoutMenu
import com.pan.tactical.ui.components.OnSceneTerminal
import com.pan.tactical.ui.components.PostMissionOverlays
import com.pan.tactical.ui.components.MissionAlertOverlay
import com.pan.tactical.ui.components.SwipeActionSlider
import com.pan.tactical.ui.components.UwbHomingCompass
import com.pan.tactical.ui.components.FeedbackScreen
import com.pan.tactical.ui.components.FeedbackIssueChip
import com.pan.tactical.ui.components.AgentRank
import com.pan.tactical.ui.components.RankUpOverlay
import com.pan.tactical.ui.components.rankForMissions
import com.pan.tactical.models.AgentCapability
import com.pan.tactical.models.AgentCapabilityUiModel
import com.pan.tactical.models.MissionData
import com.pan.tactical.AudioEngine
import com.pan.tactical.getCurrentTimeMs
import com.pan.tactical.getNativeMapUrl
import com.pan.tactical.rememberSharedCameraManager
import com.pan.tactical.rememberSharedLocationManager
import com.pan.tactical.rememberUwbClient
import com.pan.tactical.rememberBleHomingClient
import com.pan.tactical.hardware.rememberBleHapHatService
import com.pan.tactical.hardware.HapHatCommand           
import com.pan.tactical.hardware.LedColor                
import com.pan.tactical.hardware.LedMode                 
import com.pan.tactical.hardware.MotorId                 
import com.pan.tactical.network.PanApiClient
import com.pan.tactical.network.PanWalletClient
import com.pan.tactical.ui.homing.HomingViewModel
import com.pan.tactical.ui.homing.HomingViewModelFactory
import com.pan.tactical.ui.homing.MissionResult
import pantactical.composeapp.generated.resources.Res
import pantactical.composeapp.generated.resources.pan_logo

// 🛡️ FIXED: Wired directly to build environment to prevent production sandbox leaks
private val IS_DEBUG_MODE = BuildConfig.DEBUG

@Composable
actual fun AgentDashboardScreen(
    apiClient: WalletNetworkClient
) {
    val panClient = apiClient as? PanApiClient
    if (panClient == null) {
        Box(modifier = Modifier.fillMaxSize().background(Color.Black), contentAlignment = Alignment.Center) {
            Text(
                text = "CRITICAL ARCHITECTURE ERROR:\nPanApiClient required for Tactical Dashboard.\nCurrent client is incompatible.",
                color = Color.Red,
                fontWeight = FontWeight.Bold,
                textAlign = androidx.compose.ui.text.style.TextAlign.Center
            )
        }
        return
    }

    var appState by rememberSaveable { mutableStateOf("BOOT") }
    var currentScreen by rememberSaveable { mutableStateOf("DASHBOARD") }

    BoxWithConstraints(
        modifier = Modifier
            .fillMaxSize()
            .background(Color.Black)
            .systemBarsPadding()
    ) {
        val isBoot = appState == "BOOT"

        Crossfade(targetState = appState, animationSpec = tween(durationMillis = 2000), label = "app_boot") { state ->
            when (state) {
                "BOOT" -> {
                    LaunchedEffect(Unit) {
                        currentScreen = "DASHBOARD"
                        delay(500)
                        appState = "RUNNING"
                    }
                }
                "RUNNING" -> MainDashboardContent(
                    apiClient = panClient,
                    rawWalletClient = apiClient,
                    currentScreen = currentScreen,
                    onNavigate = { currentScreen = it }
                )
            }
        }

        val logoWidth by animateDpAsState(
            targetValue = if (isBoot) 280.dp else 200.dp,
            animationSpec = if (!isBoot) keyframes {
                durationMillis = 3000
                280.dp at 0
                350.dp at 1000 using FastOutSlowInEasing
                200.dp at 3000 using LinearOutSlowInEasing
            } else tween(800),
            label = "logo_width"
        )

        val logoHeight by animateDpAsState(
            targetValue = if (isBoot) 120.dp else 70.dp,
            animationSpec = if (!isBoot) keyframes {
                durationMillis = 3000
                120.dp at 0
                150.dp at 1000 using FastOutSlowInEasing
                70.dp at 3000 using LinearOutSlowInEasing
            } else tween(800),
            label = "logo_height"
        )

        val offsetX by animateDpAsState(
            targetValue = if (isBoot) (maxWidth - 280.dp) / 2 else 0.dp,
            animationSpec = if (!isBoot) keyframes {
                durationMillis = 3000
                ((maxWidth - 280.dp) / 2) at 0
                ((maxWidth - 350.dp) / 2) at 1000 using FastOutSlowInEasing
                0.dp at 3000 using LinearOutSlowInEasing
            } else tween(800),
            label = "logo_x"
        )

        val offsetY by animateDpAsState(
            targetValue = if (isBoot) (maxHeight - 120.dp) / 3 else 0.dp,
            animationSpec = if (!isBoot) keyframes {
                durationMillis = 3000
                ((maxHeight - 120.dp) / 3) at 0
                ((maxHeight - 150.dp) / 3) at 1000 using FastOutSlowInEasing
                0.dp at 3000 using LinearOutSlowInEasing
            } else tween(800),
            label = "logo_y"
        )

        if (currentScreen == "DASHBOARD") {
            Image(
                painter = painterResource(Res.drawable.pan_logo),
                contentDescription = "PAN Command",
                modifier = Modifier
                    .offset(x = offsetX, y = offsetY)
                    .width(logoWidth)
                    .height(logoHeight)
                    .zIndex(100f),
                contentScale = ContentScale.Fit
            )
        }
    }
}

@OptIn(ExperimentalFoundationApi::class)
@Composable
fun MainDashboardContent(
    apiClient: PanApiClient,
    rawWalletClient: WalletNetworkClient,
    currentScreen: String,
    onNavigate: (String) -> Unit
) {
    val context = LocalContext.current
    val coroutineScope = rememberCoroutineScope()
    val audio = remember { AudioEngine() }
    val uriHandler = LocalUriHandler.current

    val uwbClient = rememberUwbClient()
    val uwbRangingState by uwbClient.rangingState.collectAsState()

    val bleClient = rememberBleHomingClient()
    val hapHat = rememberBleHapHatService() 

    val homingViewModel: HomingViewModel = viewModel(
        factory = HomingViewModelFactory(bleClient, uwbClient, apiClient)
    )
    val homingState by homingViewModel.uiState.collectAsState()

    DisposableEffect(Unit) {
        coroutineScope.launch { hapHat.connect() }
        onDispose {
            audio.shutdown()
            uwbClient.close()
            bleClient.stopScanning()
            hapHat.close() 
        }
    }

    var navPreference by rememberSaveable { mutableStateOf("GOOGLE") }
    var patrolMode by rememberSaveable { mutableStateOf("VEHICLE") }
    var serviceRadiusMiles by rememberSaveable { mutableStateOf(5f) }
    var isLoadoutExpanded by rememberSaveable { mutableStateOf(false) }
    var isDataLoaded by rememberSaveable { mutableStateOf(true) }
    var voiceVolume by rememberSaveable { mutableFloatStateOf(1f) }
    var alertVolume by rememberSaveable { mutableIntStateOf(100) }

    var hasSpokenWelcome by rememberSaveable { mutableStateOf(false) }
    var isOnline by rememberSaveable { mutableStateOf(false) }
    var isProcessing by rememberSaveable { mutableStateOf(false) }
    var missionState by rememberSaveable { mutableStateOf("IDLE") }
    var showAbortDialog by rememberSaveable { mutableStateOf(false) }
    var showDevMenu by rememberSaveable { mutableStateOf(false) }
    var abortSliderResetKey by rememberSaveable { mutableIntStateOf(0) }
    
    // Feedback State
    var showFeedbackScreen by rememberSaveable { mutableStateOf(false) }
    var feedbackTaskId by rememberSaveable { mutableStateOf("") }
    var feedbackFleetId by rememberSaveable { mutableStateOf("") }

    // 🟢 RANK PROGRESSION STATE
    var missionsCompleted by rememberSaveable { mutableIntStateOf(0) }
    var currentRank by rememberSaveable { mutableStateOf<AgentRank?>(null) }
    var showRankUp by rememberSaveable { mutableStateOf(false) }
    var rankUpTo by rememberSaveable { mutableStateOf(AgentRank.RECRUIT) }

    // Ephemeral security storage
    var avUwbMacAddress by remember { mutableStateOf<String?>(null) }
    var avUwbSessionKey by remember { mutableStateOf<ByteArray?>(null) }
    var isBleHandshakeComplete by remember { mutableStateOf(false) }
    var isBleScanning by remember { mutableStateOf(false) }

    // On boot, fetch initial missions completed so we don't trigger a rank-up
    LaunchedEffect(Unit) {
        val data = rawWalletClient.getWalletData()
        if (data != null) {
            missionsCompleted = data.missionsCompleted
        }
    }

    // Trigger overlay safely when crossing a threshold
    LaunchedEffect(missionsCompleted) {
        val newRank = rankForMissions(missionsCompleted)
        if (currentRank != null && newRank > currentRank!!) {
            rankUpTo = newRank
            showRankUp = true
        }
        currentRank = newRank
    }

    val MissionDataSaver = Saver<MissionData?, String>(
        save = { it?.let { data -> "${data.lat}|${data.lon}|${data.errorCode}|${data.bountyUsd}|${data.intersection}|${data.taskId}|${data.incidentId}" } ?: "" },
        restore = { str ->
            if (str.isEmpty()) null
            else {
                val parts = str.split("|")
                if (parts.size >= 7) MissionData(
                    lat = parts[0].toDoubleOrNull() ?: 0.0,
                    lon = parts[1].toDoubleOrNull() ?: 0.0,
                    errorCode = parts[2],
                    bountyUsd = parts[3].toDoubleOrNull() ?: 0.0,
                    intersection = parts[4],
                    taskId = parts[5],
                    incidentId = parts[6]
                ) else null
            }
        }
    )

    var activeMission by rememberSaveable(stateSaver = MissionDataSaver) { mutableStateOf(null) }
    var queuedMission by rememberSaveable(stateSaver = MissionDataSaver) { mutableStateOf(null) }
    var isMissionControlsExpanded by rememberSaveable { mutableStateOf(false) }

    var lastPayoutAmount by rememberSaveable { mutableDoubleStateOf(0.0) }
    var lastTxHash by rememberSaveable { mutableStateOf("") }
    var timeOnSceneMs by rememberSaveable { mutableLongStateOf(0L) }
    var totalResponseTimeMs by rememberSaveable { mutableLongStateOf(0L) }
    var sceneArrivalTime by rememberSaveable { mutableLongStateOf(0L) }
    var missionAcceptTime by rememberSaveable { mutableLongStateOf(0L) }

    var agentCapabilities by remember {
        mutableStateOf(
            listOf(
                AgentCapabilityUiModel(
                    capability = AgentCapability("door_securing", "Door Securing", "Push door completely shut.", null, 1, true),
                    isEnabled = true
                ),
                AgentCapabilityUiModel(
                    capability = AgentCapability("lost_item", "Lost Item Recovery", "Retrieve and secure item.", null, 1, false)
                ),
                AgentCapabilityUiModel(
                    capability = AgentCapability("scene_securement", "First Responder Liaison", "Interact with police/flares.", "Requires safety flares", 3, false)
                )
            )
        )
    }

    var agentLocation by remember { mutableStateOf(Pair(33.3061, -111.6601)) }
    var lastTelemetryTime by remember { mutableLongStateOf(0L) }

    val distanceMiles = remember(agentLocation, activeMission) {
        if (activeMission == null) return@remember 0.0

        val lat1 = agentLocation.first * PI / 180.0
        val lon1 = agentLocation.second * PI / 180.0
        val lat2 = activeMission!!.lat * PI / 180.0
        val lon2 = activeMission!!.lon * PI / 180.0

        val dlon = lon2 - lon1
        val dlat = lat2 - lat1
        val a = sin(dlat / 2).pow(2.0) + cos(lat1) * cos(lat2) * sin(dlon / 2).pow(2.0)
        val c = 2 * asin(sqrt(a))
        val r = 3956.0
        c * r
    }

    val distanceMeters = (distanceMiles * 1609.34).toFloat()

    val countdownProgress = remember { Animatable(1f) }
    var isFlashing by remember { mutableStateOf(false) }
    val flashAlpha by animateFloatAsState(targetValue = if (isFlashing) 0.2f else 0f, animationSpec = tween(durationMillis = 150), label = "flash")

    LaunchedEffect(missionState, isOnline) {
        when (missionState) {
            "IDLE" -> {
                isFlashing = false
                if (isOnline) {
                    while (isOnline && missionState == "IDLE") {
                        try {
                            val incomingMissions = apiClient.fetchActiveMissions()
                            if (incomingMissions.isNotEmpty()) {
                                println("[TACTICAL_UI] Mission Received! Triggering Alert...")
                                withContext(Dispatchers.Main) {
                                    activeMission = incomingMissions.first()
                                    missionState = "PENDING"
                                    
                                    hapHat.sendCommand(
                                        HapHatCommand(
                                            motorId = MotorId.M3_CENTER,
                                            intensityPwm = 200.toByte(), 
                                            ledMode = LedMode.PULSE,
                                            ledColor = LedColor.PURPLE,
                                            durationMs = 15000 
                                        )
                                    )
                                }
                                break
                            }
                        } catch (e: Exception) {
                            println("[NETWORK_ERROR] Mission polling failed: ${e.message}")
                        }
                        delay(3000)
                    }
                }
            }
            "PENDING" -> {
                launch {
                    while (true) {
                        isFlashing = !isFlashing
                        delay(500)
                    }
                }
                
                val taskId = activeMission?.taskId
                if (!taskId.isNullOrBlank()) {
                    launch { apiClient.acknowledgeMission(taskId) }
                }

                val rawBounty = activeMission?.bountyUsd ?: 0.0
                val netPayout = rawBounty * 0.90
                val cleanBounty = if (netPayout % 1.0 == 0.0) netPayout.toInt().toString() else netPayout.toString()
                val cleanCategory = activeMission?.errorCode?.substringAfter(": ") ?: activeMission?.errorCode ?: "Unknown"

                val cleanDistance = ((distanceMiles * 10.0).roundToInt() / 10.0).toString()
                audio.speak("Agent, Mission: $cleanCategory. $cleanDistance Miles Away. Payout, $cleanBounty dollars.", voiceVolume)

                countdownProgress.snapTo(1f)
                countdownProgress.animateTo(
                    targetValue = 0f,
                    animationSpec = tween(durationMillis = 10000, easing = LinearEasing)
                )
                
                if (missionState == "PENDING") {
                    if (!taskId.isNullOrBlank()) {
                        apiClient.declineMission(taskId)
                    }
                    hapHat.sendCommand(HapHatCommand(ledMode = LedMode.OFF, ledColor = LedColor.OFF))
                    missionState = "IDLE"
                    activeMission = null
                }
            }
            "ACTIVE" -> {
                isFlashing = false
                isMissionControlsExpanded = false
            }
            "ON_SCENE", "COMPLETED" -> {
                isFlashing = false
            }
        }
    }

    LaunchedEffect(isDataLoaded) {
        if (isDataLoaded && !hasSpokenWelcome) {
            delay(500)
            audio.speak("The command is now yours, Agent.", voiceVolume)
            hasSpokenWelcome = true
        }
    }

    val locationManager = rememberSharedLocationManager { lat, lon ->
        println("[TACTICAL_GPS] Agent moving: $lat, $lon")
        agentLocation = Pair(lat, lon)

        homingViewModel.updateGpsProximity(distanceMeters.toDouble())

        val now = getCurrentTimeMs()
        if (isOnline && now - lastTelemetryTime > 3000) {
            lastTelemetryTime = now
            coroutineScope.launch {
                try {
                    apiClient.updateLocationTelemetry(lat, lon)
                } catch (e: Exception) {
                    println("[TELEMETRY_ERROR] Failed to push GPS to Backend: ${e.message}")
                }
            }
        }
    }

    var tacticalRoute by remember { mutableStateOf<List<Pair<Double, Double>>>(emptyList()) }
    var hasCameraPermission by rememberSaveable { mutableStateOf(true) }

    var capturedEvidence by remember { mutableStateOf<List<ByteArray>>(emptyList()) }

    val cameraManager = rememberSharedCameraManager { imageData ->
        if (imageData != null) {
            capturedEvidence = capturedEvidence + (imageData as ByteArray)
        }
    }

    LaunchedEffect(homingState.missionResult) {
        when (homingState.missionResult) {
            MissionResult.SUCCESS -> {
                val rawBounty = activeMission?.bountyUsd ?: 0.0
                val finalPayout = rawBounty * 0.90

                lastTxHash = "tx_${getCurrentTimeMs()}"
                lastPayoutAmount = finalPayout
                timeOnSceneMs = if (sceneArrivalTime > 0) getCurrentTimeMs() - sceneArrivalTime else 252000L
                totalResponseTimeMs = if (missionAcceptTime > 0) getCurrentTimeMs() - missionAcceptTime else timeOnSceneMs + 300000L
                missionState = "COMPLETED"

                hapHat.sendCommand(
                    HapHatCommand(
                        motorId = MotorId.ALL, 
                        intensityPwm = 255.toByte(), 
                        ledMode = LedMode.STROBE,
                        ledColor = LedColor.GREEN,
                        durationMs = 3000 
                    )
                )

                audio.speak("Mission accomplished. Escrow funds secured.", voiceVolume)
                capturedEvidence = emptyList()

                // Refresh wallet data after payout to fetch updated missionsCompleted count
                val updatedWallet = rawWalletClient.getWalletData()
                if (updatedWallet != null) {
                    missionsCompleted = updatedWallet.missionsCompleted
                }

                homingViewModel.clearMissionResult()
            }
            MissionResult.FAILED -> {
                audio.speak("Network submission failed. Please retry.", voiceVolume)
                
                hapHat.sendCommand(
                    HapHatCommand(
                        motorId = MotorId.ALL, 
                        intensityPwm = 255.toByte(),
                        ledMode = LedMode.STROBE,
                        ledColor = LedColor.RED,
                        durationMs = 3000
                    )
                )

                homingViewModel.clearMissionResult()
            }
            null -> {}
        }
    }

    val bearingDegrees = remember(agentLocation, activeMission) {
        if (activeMission == null) return@remember 0f
        val lat1 = agentLocation.first * PI / 180.0
        val lon1 = agentLocation.second * PI / 180.0
        val lat2 = activeMission!!.lat * PI / 180.0
        val lon2 = activeMission!!.lon * PI / 180.0

        val dLon = lon2 - lon1
        val y = sin(dLon) * cos(lat2)
        val x = cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(dLon)
        var brng = atan2(y, x) * 180.0 / PI
        brng = (brng + 360.0) % 360.0
        brng.toFloat()
    }

    val isBleZone = (missionState == "ACTIVE" || missionState == "ON_SCENE") && distanceMeters <= 50f
    val isUwbZone = (missionState == "ACTIVE" || missionState == "ON_SCENE") && distanceMeters <= 15f
    val isUwbEngaged = isUwbZone && isBleHandshakeComplete

    LaunchedEffect(isBleZone, activeMission?.taskId) {
        if (isBleZone && !isBleHandshakeComplete && !isBleScanning) {
            val currentTaskId = activeMission?.taskId
            if (!currentTaskId.isNullOrBlank()) {
                isBleScanning = true
                try {
                    audio.speak("Approaching target. Initiating secure B L E handshake.", voiceVolume)

                    val result = bleClient.executeOobHandshake(missionId = currentTaskId)

                    if (result.success && result.uwbMacAddress != null && result.secureSessionKey != null) {
                        avUwbMacAddress = result.uwbMacAddress
                        avUwbSessionKey = result.secureSessionKey
                        isBleHandshakeComplete = true
                        
                        hapHat.sendCommand(
                            HapHatCommand(
                                ledMode = LedMode.SOLID,
                                ledColor = LedColor.CYAN,
                                durationMs = 0
                            )
                        )
                        
                        audio.speak("Handshake verified. Micro-homing credentials secured.", voiceVolume)
                    } else {
                        audio.speak("Handshake failed. Move closer and re-approach target.", voiceVolume)
                    }
                } catch (e: Exception) {
                    println("[BLE_ERROR] Handshake crashed: ${e.message}")
                } finally {
                    isBleScanning = false
                }
            }
        } else if (!isBleZone && isBleHandshakeComplete) {
            isBleHandshakeComplete = false
            avUwbMacAddress = null
            avUwbSessionKey = null
        }
    }

    LaunchedEffect(isUwbEngaged) {
        val mac = avUwbMacAddress
        val key = avUwbSessionKey

        if (isUwbEngaged && mac != null && key != null) {
            uwbClient.startRanging(avMacAddress = mac, secureSessionKey = key)
        } else {
            uwbClient.stopRanging()
        }
    }

    LaunchedEffect(distanceMiles) { if (missionState == "ACTIVE" && distanceMiles <= 0.1) isMissionControlsExpanded = true }

    val tacticalMapStyle = """[{"elementType":"geometry","stylers":[{"color":"#121212"}]},{"elementType":"labels.icon","stylers":[{"visibility":"off"}]},{"elementType":"labels.text.fill","stylers":[{"color":"#EEEEEE"}]},{"elementType":"labels.text.stroke","stylers":[{"color":"#000000"},{"weight":3}]},{"featureType":"road","elementType":"geometry","stylers":[{"color":"#555555"}]}]"""

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
                        .let {
                            if (IS_DEBUG_MODE) {
                                it.combinedClickable(onClick = {}, onLongClick = { showDevMenu = true })
                            } else {
                                it.clickable(enabled = false) {}
                            }
                        }
                )

                Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(16.dp)) {
                    Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                        Box(
                            modifier = Modifier
                                .size(10.dp)
                                .background(if (isOnline) Color(0xFF4CAF50) else Color(0xFFF44336), CircleShape)
                        )
                        Text(
                            text = if (isOnline) "ONLINE" else "OFFLINE",
                            color = if (isOnline) Color(0xFF4CAF50) else Color(0xFFF44336),
                            fontSize = 14.sp,
                            fontWeight = FontWeight.Bold
                        )
                    }

                    Box(
                        modifier = Modifier
                            .size(36.dp)
                            .background(Color(0xFF333333), RoundedCornerShape(18.dp))
                            .clickable { onNavigate("WALLET") },
                        contentAlignment = Alignment.Center
                    ) {
                        Text("ID", color = Color.White, fontSize = 12.sp, fontWeight = FontWeight.Bold)
                    }
                }
            }

            Box(modifier = Modifier.fillMaxWidth().weight(1f).background(Color(0xFF2A2A2A)), contentAlignment = Alignment.Center) {

                AnimatedContent(
                    targetState = isUwbEngaged,
                    transitionSpec = {
                        fadeIn(animationSpec = tween(500)) togetherWith fadeOut(animationSpec = tween(500))
                    },
                    label = "map_to_uwb_transition"
                ) { showUwb ->
                    if (showUwb) {
                        UwbHomingCompass(
                            distanceMeters = if (uwbRangingState.isRanging) uwbRangingState.distanceMeters else distanceMeters,
                            bearingDegrees = if (uwbRangingState.isRanging) uwbRangingState.azimuthDegrees else bearingDegrees,
                            isRanging = uwbRangingState.isRanging
                        )
                    } else {
                        com.pan.tactical.ui.components.TacticalMap(
                            modifier = Modifier.fillMaxSize(),
                            targetLocation = agentLocation,
                            mapStyleJson = tacticalMapStyle,
                            route = tacticalRoute
                        )
                    }
                }

                androidx.compose.animation.AnimatedVisibility(visible = missionState == "PENDING" && activeMission != null, enter = slideInVertically(initialOffsetY = { it }) + fadeIn(), exit = slideOutVertically(targetOffsetY = { it }) + fadeOut(), modifier = Modifier.fillMaxSize()) {
                    MissionAlertOverlay(
                        activeMission = activeMission,
                        countdownProgress = countdownProgress.value,
                        flashAlpha = flashAlpha,
                        onAccept = {
                            val currentTaskId = activeMission?.taskId
                            if (!currentTaskId.isNullOrBlank()) {
                                homingViewModel.setMission(currentTaskId)
                            }

                            missionState = "ACTIVE"
                            
                            coroutineScope.launch {
                                hapHat.sendCommand(
                                    HapHatCommand(
                                        motorId = MotorId.M3_CENTER, 
                                        intensityPwm = 200.toByte(), 
                                        ledMode = LedMode.SOLID,     
                                        ledColor = LedColor.WHITE,
                                        durationMs = 500             
                                    )
                                )
                                delay(500)
                                hapHat.sendCommand(
                                    HapHatCommand(
                                        ledMode = LedMode.SOLID,
                                        ledColor = LedColor.ORANGE,
                                        durationMs = 0
                                    )
                                )
                            }
                            
                            missionAcceptTime = getCurrentTimeMs()
                            audio.stop()

                            val targetLat = activeMission?.lat ?: 0.0
                            val targetLon = activeMission?.lon ?: 0.0

                            // TODO (Phase 6): Fetch actual OSRM geospatial route from matching_engine
                            tacticalRoute = listOf(
                                agentLocation,
                                Pair(agentLocation.first + 0.015, agentLocation.second - 0.01),
                                Pair(targetLat, targetLon)
                            )

                            try {
                                uriHandler.openUri(getNativeMapUrl(targetLat, targetLon))
                            } catch (e: Exception) {
                                println("[NAVIGATION_ERROR] Failed to open native map: ${e.message}")
                            }
                        },
                        onDecline = {
                            val currentTaskId = activeMission?.taskId
                            if (!currentTaskId.isNullOrBlank()) {
                                coroutineScope.launch { apiClient.declineMission(currentTaskId) }
                            }
                            missionState = "IDLE"
                            
                            coroutineScope.launch {
                                hapHat.sendCommand(HapHatCommand(ledMode = LedMode.OFF, ledColor = LedColor.OFF))
                            }
                            
                            activeMission = null
                            tacticalRoute = emptyList()
                            audio.stop()
                        }
                    )
                }

                PostMissionOverlays(
                    isUploadingProof = homingState.isResolving,
                    capturedEvidence = capturedEvidence,
                    missionState = missionState,
                    lastPayoutAmount = lastPayoutAmount,
                    timeOnSceneMs = timeOnSceneMs,
                    totalResponseTimeMs = totalResponseTimeMs,
                    lastTxHash = lastTxHash,
                    onReturnToPatrol = {
                        // 🛡️ Safely snapshot the mission data BEFORE opening the overlay
                        // This prevents recomposition crashes when activeMission becomes null mid-animation
                        feedbackTaskId = activeMission?.taskId ?: ""
                        feedbackFleetId = "Vanguard Network Partner" // To be pulled from activeMission?.fleetId in next iteration
                        showFeedbackScreen = true
                    }
                )
            }

            Column(modifier = Modifier.fillMaxWidth().background(Color(0xFF1E1E1E)), horizontalAlignment = Alignment.CenterHorizontally) {

                AnimatedVisibility(visible = missionState == "ACTIVE", enter = expandVertically() + fadeIn(), exit = shrinkVertically() + fadeOut()) {
                    Column(modifier = Modifier.fillMaxWidth().animateContentSize(), horizontalAlignment = Alignment.CenterHorizontally) {
                        Box(modifier = Modifier.fillMaxWidth().clickable { isMissionControlsExpanded = !isMissionControlsExpanded }.padding(vertical = 12.dp), contentAlignment = Alignment.Center) { Text(if (isMissionControlsExpanded) "▼ HIDE MISSION CONTROLS ▼" else "▲ SHOW MISSION CONTROLS ▲", color = Color(0xFF00BCD4), fontSize = 12.sp, fontWeight = FontWeight.Bold, letterSpacing = 1.sp) }
                        if (isMissionControlsExpanded) {
                            Column(modifier = Modifier.fillMaxWidth().padding(start = 16.dp, end = 16.dp, bottom = 16.dp), horizontalAlignment = Alignment.CenterHorizontally) {
                                Text("ACTIVE MISSION: EN ROUTE", color = Color(0xFF00BCD4), fontSize = 14.sp, fontWeight = FontWeight.Black, letterSpacing = 2.sp)
                                Spacer(modifier = Modifier.height(8.dp)); Text(activeMission?.intersection ?: "Target Location", color = Color.White, fontSize = 20.sp, fontWeight = FontWeight.Bold); Text("Diagnostic: ${activeMission?.errorCode}", color = Color.LightGray, fontSize = 14.sp); Spacer(modifier = Modifier.height(16.dp))
                                Button(
                                    onClick = {
                                        missionState = "ON_SCENE"
                                        sceneArrivalTime = getCurrentTimeMs()
                                        
                                        coroutineScope.launch {
                                            hapHat.sendCommand(
                                                HapHatCommand(
                                                    motorId = MotorId.ALL,
                                                    intensityPwm = 255.toByte(),
                                                    ledMode = LedMode.SOLID,
                                                    ledColor = LedColor.YELLOW,
                                                    durationMs = 0 
                                                )
                                            )
                                        }
                                    },
                                    colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF00BCD4)), shape = RoundedCornerShape(8.dp), modifier = Modifier.fillMaxWidth().height(64.dp).padding(bottom = 16.dp)
                                ) { Text("ARRIVED AT SCENE", color = Color.Black, fontSize = 20.sp, fontWeight = FontWeight.Black, letterSpacing = 1.sp) }

                                key(abortSliderResetKey) {
                                    SwipeActionSlider(text = "SWIPE TO ABORT >>", trackColor = Color(0xFF2C2C2C), thumbColor = Color(0xFFD32F2F)) {
                                        showAbortDialog = true
                                    }
                                }
                            }
                        }
                    }
                }

                AnimatedVisibility(visible = missionState == "ON_SCENE", enter = expandVertically() + fadeIn(), exit = shrinkVertically() + fadeOut()) {
                    OnSceneTerminal(
                        activeMission = activeMission,
                        capturedEvidence = capturedEvidence,
                        isProcessingRedaction = homingState.isResolving,
                        isResolving = homingState.isResolving,
                        terminalLogs = homingState.terminalLogs,
                        extensionRequest = homingState.extensionRequest,
                        hasCameraPermission = hasCameraPermission,
                        onRequestCameraPermission = {
                            hasCameraPermission = true
                        },
                        onCapturePhoto = {
                            cameraManager.launchCamera()
                        },
                        onRemovePhoto = { index ->
                            val mutableList = capturedEvidence.toMutableList()
                            if (index in mutableList.indices) {
                                mutableList.removeAt(index)
                                capturedEvidence = mutableList
                            }
                        },
                        onSubmitEvidence = {
                            val bitmaps = capturedEvidence.mapNotNull { bytes ->
                                BitmapFactory.decodeByteArray(bytes, 0, bytes.size)
                            }
                            homingViewModel.uploadAndSubmit(bitmaps)
                        },
                        onAcceptExtension = { taskId, mins, bounty ->
                            homingViewModel.acceptExtension(taskId, mins, bounty)
                        },
                        onDeclineExtension = {
                            homingViewModel.declineExtension()
                        },
                        onVerifyIdentity = { onResult ->
                            val fragmentActivity = context as? FragmentActivity
                            if (fragmentActivity != null) {
                                val executor = ContextCompat.getMainExecutor(context)
                                val biometricPrompt = BiometricPrompt(
                                    fragmentActivity,
                                    executor,
                                    object : BiometricPrompt.AuthenticationCallback() {
                                        override fun onAuthenticationError(errorCode: Int, errString: CharSequence) {
                                            super.onAuthenticationError(errorCode, errString)
                                            println("[ATTESTATION] Biometric error: $errString")
                                            onResult(false)
                                        }

                                        override fun onAuthenticationSucceeded(result: BiometricPrompt.AuthenticationResult) {
                                            super.onAuthenticationSucceeded(result)
                                            println("[ATTESTATION] ✅ Agent Verified. StrongBox Signature Authorized.")
                                            onResult(true) 
                                        }

                                        override fun onAuthenticationFailed() {
                                            super.onAuthenticationFailed()
                                            println("[ATTESTATION] ❌ Biometric rejection.")
                                            onResult(false)
                                        }
                                    }
                                )

                                val promptInfo = BiometricPrompt.PromptInfo.Builder()
                                    .setTitle("Agent Attestation Required")
                                    .setSubtitle("Authenticate to cryptographically sign mission evidence")
                                    .setNegativeButtonText("Cancel")
                                    .setAllowedAuthenticators(BiometricManager.Authenticators.BIOMETRIC_STRONG)
                                    .build()

                                biometricPrompt.authenticate(promptInfo)
                            } else {
                                println("[ATTESTATION_ERROR] LocalContext is not a FragmentActivity")
                                onResult(false)
                            }
                        },
                        onLogEntry = { log ->
                            homingViewModel.appendLog(log)
                        }
                    )
                }

                AnimatedVisibility(visible = missionState == "IDLE") {
                    OfflineLoadoutMenu(
                        isLoadoutExpanded = isLoadoutExpanded,
                        onToggleExpand = { isLoadoutExpanded = !isLoadoutExpanded },
                        patrolMode = patrolMode,
                        onPatrolModeChange = { patrolMode = it },
                        serviceRadiusMiles = serviceRadiusMiles,
                        onRadiusChange = { serviceRadiusMiles = it },
                        agentCapabilities = agentCapabilities,
                        onCapabilitiesChange = { agentCapabilities = it }
                    )
                }

                AnimatedVisibility(visible = missionState == "IDLE") {
                    Box(modifier = Modifier.padding(start = 16.dp, end = 16.dp, bottom = 16.dp)) {
                        if (isOnline) {
                            SwipeActionSlider(text = "SWIPE TO GO OFFLINE >>", trackColor = Color(0xFF333333), thumbColor = Color(0xFFF44336)) {
                                isProcessing = true
                                coroutineScope.launch {
                                    delay(800)
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
                                        delay(800)
                                        isOnline = true

                                        try {
                                            apiClient.updateLocationTelemetry(agentLocation.first, agentLocation.second)
                                        } catch (e: Exception) {
                                            println("[TELEMETRY_ERROR] ${e.message}")
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

        AnimatedVisibility(
            visible = currentScreen == "WALLET",
            enter = slideInHorizontally(initialOffsetX = { it }) + fadeIn(),
            exit = slideOutHorizontally(targetOffsetX = { it }) + fadeOut(),
            modifier = Modifier.fillMaxSize().zIndex(10f)
        ) {
            WalletAndProfileScreen(
                apiClient = apiClient,
                onBack = { onNavigate("DASHBOARD") },
                navPreference = navPreference,
                onNavPrefChange = { navPreference = it },
                audioEngine = audio,
                voiceVolume = voiceVolume,
                onVoiceVolumeChange = { voiceVolume = it },
                alertVolume = alertVolume,
                onAlertVolumeChange = { alertVolume = it }
            )
        }

        if (showDevMenu) {
            AlertDialog(onDismissRequest = { showDevMenu = false }, containerColor = Color(0xFF1E1E1E), title = { Text("DEV: INJECT MISSION", color = Color.White, fontWeight = FontWeight.Black) },
                text = { Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    Button(onClick = {
                        coroutineScope.launch { apiClient.triggerBackendDispatch(33.432, -111.865, "scene_securement") }
                        showDevMenu = false
                    }, colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF333333)), modifier = Modifier.fillMaxWidth()) { Text("LOC 1: Police Liaison (Tier 3)", color = Color.White) }

                    Button(onClick = {
                        coroutineScope.launch { apiClient.triggerBackendDispatch(33.385, -111.683, "spill_remediation") }
                        showDevMenu = false
                    }, colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF333333)), modifier = Modifier.fillMaxWidth()) { Text("LOC 2: Bio/Liquid Remediation (Tier 2)", color = Color.White) }

                    Button(onClick = {
                        coroutineScope.launch { apiClient.triggerBackendDispatch(33.415, -111.831, "latch_fault") }
                        showDevMenu = false
                    }, colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF333333)), modifier = Modifier.fillMaxWidth()) { Text("LOC 3: Door Securing (Tier 1)", color = Color.White) }

                    Button(onClick = {
                        coroutineScope.launch { apiClient.triggerBackendDispatch(agentLocation.first + 0.00009, agentLocation.second, "uwb_calibration") }
                        showDevMenu = false
                    }, colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF00BCD4)), modifier = Modifier.fillMaxWidth()) { Text("LOC 4: UWB Proximity Test (10m)", color = Color.Black, fontWeight = FontWeight.Bold) }
                } }, confirmButton = {}, dismissButton = { TextButton(onClick = { showDevMenu = false }) { Text("CLOSE", color = Color.Gray) } }
            )
        }

        if (showAbortDialog) {
            AlertDialog(onDismissRequest = { showAbortDialog = false; abortSliderResetKey++ }, containerColor = Color(0xFF1E1E1E), title = { Text("ABORT MISSION", color = Color.White, fontWeight = FontWeight.Black) },
                text = { Column { listOf("Too Dangerous", "Changed Mind", "Can't Find AV", "AV Leaving Scene", "Other").forEach { reason ->
                    Button(onClick = {
                        val currentTaskId = activeMission?.taskId ?: queuedMission?.taskId
                        if (!currentTaskId.isNullOrBlank()) {
                            coroutineScope.launch { apiClient.declineMission(currentTaskId) }
                        }
                        showAbortDialog = false; missionState = "IDLE"; activeMission = null; queuedMission = null; abortSliderResetKey++
                        missionAcceptTime = 0L; sceneArrivalTime = 0L
                        tacticalRoute = emptyList()

                        // 🛡️ FIXED: Clear captured evidence to prevent cross-mission contamination
                        capturedEvidence = emptyList()

                        // 🟢 SECURITY RESET: Scrub BLE Keys
                        isBleHandshakeComplete = false
                        avUwbMacAddress = null
                        avUwbSessionKey = null

                        coroutineScope.launch {
                            hapHat.sendCommand(HapHatCommand(ledMode = LedMode.OFF, ledColor = LedColor.OFF))
                        }
                        
                    }, colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF333333)), modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp), shape = RoundedCornerShape(8.dp)) { Text(reason, color = Color.White, fontWeight = FontWeight.Bold) }
                } } }, confirmButton = {}, dismissButton = { TextButton(onClick = { showAbortDialog = false; abortSliderResetKey++ }) { Text("CANCEL", color = Color.Gray) } }
            )
        }

        // 🟢 FEEDBACK SCREEN INJECTION
        AnimatedVisibility(
            visible = showFeedbackScreen,
            enter = fadeIn(),
            exit = fadeOut(),
            modifier = Modifier.fillMaxSize().zIndex(20f)
        ) {
            FeedbackScreen(
                taskId = feedbackTaskId,
                fleetId = feedbackFleetId,
                payoutAmount = lastPayoutAmount,
                issueChips = listOf(
                    FeedbackIssueChip("Biohazard Unreported", "SAFETY"),
                    FeedbackIssueChip("Hardware Defect", "SAFETY"),
                    FeedbackIssueChip("Incorrect Fault Code", "COMPLIANCE"),
                    FeedbackIssueChip("Bounty Dispute", "CONDUCT"),
                    FeedbackIssueChip("API Timeout", "LOGISTICS"),
                    FeedbackIssueChip("Vehicle Not at Pin", "LOGISTICS")
                ),
                onSubmit = { isPositive, category, label, ventText ->
                    // Cast safely assuming PanWalletClient implementation is provided
                    (rawWalletClient as? PanWalletClient)?.submitMissionFeedback(
                        taskId = feedbackTaskId,
                        isPositive = isPositive,
                        category = category,
                        label = label,
                        ventText = ventText
                    ) ?: false
                },
                onDismiss = {
                    showFeedbackScreen = false
                    
                    // --- DELEGATED POST-MISSION RESET LOGIC ---
                    lastPayoutAmount = 0.0; timeOnSceneMs = 0L; totalResponseTimeMs = 0L; lastTxHash = ""; sceneArrivalTime = 0L; missionAcceptTime = 0L
                    tacticalRoute = emptyList()

                    isBleHandshakeComplete = false
                    avUwbMacAddress = null
                    avUwbSessionKey = null

                    if (queuedMission != null) {
                        activeMission = queuedMission; queuedMission = null; missionState = "ACTIVE"
                        
                        coroutineScope.launch {
                            hapHat.sendCommand(
                                HapHatCommand(
                                    ledMode = LedMode.SOLID,
                                    ledColor = LedColor.ORANGE
                                )
                            )
                        }
                    } else {
                        missionState = "IDLE"; activeMission = null
                        
                        coroutineScope.launch {
                            hapHat.sendCommand(HapHatCommand(ledMode = LedMode.OFF, ledColor = LedColor.OFF))
                        }
                    }
                }
            )
        }

        // 🟢 RANK UP OVERLAY
        AnimatedVisibility(
            visible = showRankUp,
            enter = fadeIn(),
            exit = fadeOut(),
            modifier = Modifier.fillMaxSize().zIndex(25f)
        ) {
            RankUpOverlay(
                newRank = rankUpTo,
                ownsHapHat = false, // Will wire to real hardware inventory in Q3
                ownsGauntlets = false,
                onDismiss = { showRankUp = false }
            )
        }
    }
}