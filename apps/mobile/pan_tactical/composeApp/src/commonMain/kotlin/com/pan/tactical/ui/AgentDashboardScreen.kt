package com.pan.tactical.ui

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
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import org.jetbrains.compose.resources.painterResource

import com.pan.tactical.ui.components.OfflineLoadoutMenu
import com.pan.tactical.ui.components.OnSceneTerminal
import com.pan.tactical.ui.components.PostMissionOverlays
import com.pan.tactical.ui.components.MissionAlertOverlay
import com.pan.tactical.ui.components.SwipeActionSlider
import com.pan.tactical.models.AgentCapability
import com.pan.tactical.models.MissionData
import com.pan.tactical.AudioEngine
import com.pan.tactical.getCurrentTimeMs
import com.pan.tactical.getNativeMapUrl
import com.pan.tactical.rememberSharedCameraManager
import com.pan.tactical.rememberSharedLocationManager
import com.pan.tactical.network.PythonNetworkBridge
import pantactical.composeapp.generated.resources.Res
import pantactical.composeapp.generated.resources.pan_logo

@Composable
fun AgentDashboardScreen() {
    var appState by rememberSaveable { mutableStateOf("BOOT") }

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
                    // Bypassing boot sequence for testing
                    LaunchedEffect(Unit) {
                        delay(500)
                        appState = "RUNNING"
                    }
                }
                "RUNNING" -> MainDashboardContent()
            }
        }

        // --- THE LOGO ANIMATIONS ---
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

        // --- RESTORED KMP LOGO ---
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

@OptIn(ExperimentalFoundationApi::class)
@Composable
fun MainDashboardContent() {
    val coroutineScope = rememberCoroutineScope()
    val audio = remember { AudioEngine() }

    val uriHandler = LocalUriHandler.current

    var currentScreen by remember { mutableStateOf("DASHBOARD") }
    var navPreference by remember { mutableStateOf("GOOGLE") }
    var patrolMode by remember { mutableStateOf("VEHICLE") }
    var serviceRadiusMiles by remember { mutableStateOf(5f) }
    var isLoadoutExpanded by remember { mutableStateOf(false) }
    var isDataLoaded by remember { mutableStateOf(true) }
    var voiceVolume by remember { mutableFloatStateOf(1f) }
    var alertVolume by remember { mutableIntStateOf(100) }

    var hasSpokenWelcome by rememberSaveable { mutableStateOf(false) }
    var isOnline by remember { mutableStateOf(false) }
    var isProcessing by remember { mutableStateOf(false) }
    var missionState by remember { mutableStateOf("IDLE") }
    var showAbortDialog by remember { mutableStateOf(false) }
    var showDevMenu by remember { mutableStateOf(false) }
    var abortSliderResetKey by remember { mutableIntStateOf(0) }

    var activeMission by remember { mutableStateOf<MissionData?>(null) }
    var queuedMission by remember { mutableStateOf<MissionData?>(null) }
    var isMissionControlsExpanded by remember { mutableStateOf(false) }

    var lastPayoutAmount by remember { mutableDoubleStateOf(0.0) }
    var lastTxHash by remember { mutableStateOf("") }
    var timeOnSceneMs by remember { mutableLongStateOf(0L) }
    var totalResponseTimeMs by remember { mutableLongStateOf(0L) }
    var sceneArrivalTime by remember { mutableLongStateOf(0L) }
    var missionAcceptTime by remember { mutableLongStateOf(0L) }

    var agentCapabilities by remember {
        mutableStateOf(
            listOf(
                AgentCapability("door_securing", "Door Securing", "Push door completely shut.", null, 1, true, true, 8f, 20f, 1f, 8f),
                AgentCapability("lost_item", "Lost Item Recovery", "Retrieve and secure item.", null, 1, true, false, 15f, 30f, 5f, 15f),
                AgentCapability("scene_securement", "First Responder Liaison", "Interact with police/flares.", "Requires safety flares", 3, false, false, 50f, 150f, 10f, 50f)
            )
        )
    }

    LaunchedEffect(isOnline, missionState) {
        // Only scan the network if the agent is Online and waiting for a job
        if (isOnline && missionState == "IDLE") {
            while (isOnline && missionState == "IDLE") {
                val incomingMissions = PythonNetworkBridge.fetchActiveMissions()

                if (incomingMissions.isNotEmpty()) {
                    // We got a hit! Assign it and trigger the alert UI
                    activeMission = incomingMissions.first()
                    missionState = "PENDING"
                    break // Stop scanning while they handle the alert
                }

                // Wait 5 seconds before asking the server again
                delay(5000)
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

    // --- TARGET 3: THE LIVE GPS BRIDGE ---
    var agentLocation by remember { mutableStateOf(Pair(33.3061, -111.6601)) } // Defaults to Mesa

    val locationManager = rememberSharedLocationManager { lat, lon ->
        // DIAGNOSTIC PING
        println("TACTICAL GPS: Agent is moving! $lat, $lon")
        agentLocation = Pair(lat, lon)
    }

    var tacticalRoute by remember { mutableStateOf<List<Pair<Double, Double>>>(emptyList()) }
    var hasCameraPermission by remember { mutableStateOf(false) }
    var capturedEvidence by remember { mutableStateOf<List<String>>(emptyList()) }
    var mockEvidenceCounter by remember { mutableIntStateOf(1) }
    var isUploadingProof by remember { mutableStateOf(false) }

    val cameraManager = rememberSharedCameraManager { imageData ->
        if (imageData != null) {
            capturedEvidence = capturedEvidence + "Real_Evidentiary_Photo_0${mockEvidenceCounter}_[${imageData.size} bytes].jpg"
            mockEvidenceCounter++
        }
    }

    val countdownProgress = remember { Animatable(1f) }
    var isFlashing by remember { mutableStateOf(false) }
    val flashAlpha by animateFloatAsState(targetValue = if (isFlashing) 0.2f else 0f, animationSpec = tween(durationMillis = 150), label = "flash")

    // --- MOCKED ESCROW UPLOAD ---
    LaunchedEffect(isUploadingProof) {
        if (!isUploadingProof) return@LaunchedEffect
        val rawBounty = activeMission?.bounty?.replace("$", "")?.toFloatOrNull() ?: 0f
        val finalPayout = (rawBounty * 0.90f).toDouble()

        delay(1500)
        lastTxHash = "tx_${getCurrentTimeMs()}"
        lastPayoutAmount = finalPayout
        timeOnSceneMs = if (sceneArrivalTime > 0) getCurrentTimeMs() - sceneArrivalTime else 252000L
        totalResponseTimeMs = if (missionAcceptTime > 0) getCurrentTimeMs() - missionAcceptTime else timeOnSceneMs + 300000L
        missionState = "COMPLETED"

        audio.speak("Mission accomplished. Escrow funds secured.", voiceVolume)
        isUploadingProof = false
        capturedEvidence = emptyList()
    }

    val distanceMiles = remember(agentLocation, activeMission) {
        if (activeMission == null) return@remember 0.0
        2.5 // You can eventually replace this with a real Haversine formula using the new agentLocation!
    }

    LaunchedEffect(missionState) {
        if (missionState == "PENDING" && activeMission != null) {
            val rawBounty = activeMission?.bounty?.replace("$", "")?.toFloatOrNull() ?: 0f
            val netPayout = rawBounty * 0.90f
            val cleanBounty = if (netPayout % 1.0f == 0f) netPayout.toInt().toString() else netPayout.toString()
            val cleanCategory = activeMission?.errorCode?.substringAfter(": ") ?: activeMission?.errorCode ?: "Unknown"

            audio.speak("Agent, Mission: $cleanCategory. 2.5 Miles Away. Payout, $cleanBounty dollars.", voiceVolume)

            launch {
                countdownProgress.snapTo(1f); val durationMs = 10000L; val startTime = getCurrentTimeMs(); var elapsed = 0L;
                while (elapsed < durationMs && missionState == "PENDING") {
                    elapsed = getCurrentTimeMs() - startTime; countdownProgress.snapTo((1f - (elapsed.toFloat() / durationMs)).coerceIn(0f, 1f)); delay(16L)
                }
                if (missionState == "PENDING") { missionState = "IDLE"; activeMission = null }
            }
        }
    }

    LaunchedEffect(missionState) { if (missionState == "ACTIVE") isMissionControlsExpanded = false }
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
                // Invisible Dev Menu Trigger
                Box(
                    modifier = Modifier
                        .width(200.dp)
                        .height(70.dp)
                        .combinedClickable(onClick = {}, onLongClick = { showDevMenu = true })
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
                            .clickable { currentScreen = "WALLET" },
                        contentAlignment = Alignment.Center
                    ) {
                        Text("ID", color = Color.White, fontSize = 12.sp, fontWeight = FontWeight.Bold)
                    }
                }
            }

            Box(modifier = Modifier.fillMaxWidth().weight(1f).background(Color(0xFF2A2A2A)), contentAlignment = Alignment.Center) {

                com.pan.tactical.ui.components.TacticalMap(
                    modifier = Modifier.fillMaxSize(),
                    targetLocation = agentLocation,
                    mapStyleJson = tacticalMapStyle,
                    route = tacticalRoute
                )

                androidx.compose.animation.AnimatedVisibility(visible = missionState == "PENDING" && activeMission != null, enter = slideInVertically(initialOffsetY = { it }) + fadeIn(), exit = slideOutVertically(targetOffsetY = { it }) + fadeOut(), modifier = Modifier.fillMaxSize()) {
                    MissionAlertOverlay(
                        activeMission = activeMission,
                        countdownProgress = countdownProgress.value,
                        flashAlpha = flashAlpha,
                        onAccept = {
                            missionState = "ACTIVE"
                            missionAcceptTime = getCurrentTimeMs()
                            audio.stop()

                            val targetLat = activeMission?.lat ?: 0.0
                            val targetLon = activeMission?.lon ?: 0.0

                            tacticalRoute = listOf(
                                agentLocation,
                                Pair(agentLocation.first + 0.015, agentLocation.second - 0.01),
                                Pair(targetLat, targetLon)
                            )

                            try {
                                uriHandler.openUri(getNativeMapUrl(targetLat, targetLon))
                            } catch (e: Exception) {
                                println("Failed to open navigation app: ${e.message}")
                            }
                        },
                        onDecline = {
                            missionState = "IDLE"
                            activeMission = null
                            tacticalRoute = emptyList()
                            audio.stop()
                        }
                    )
                }

                PostMissionOverlays(
                    isUploadingProof = isUploadingProof,
                    capturedEvidence = capturedEvidence,
                    missionState = missionState,
                    lastPayoutAmount = lastPayoutAmount,
                    timeOnSceneMs = timeOnSceneMs,
                    totalResponseTimeMs = totalResponseTimeMs,
                    lastTxHash = lastTxHash,
                    onReturnToPatrol = {
                        lastPayoutAmount = 0.0; timeOnSceneMs = 0L; totalResponseTimeMs = 0L; lastTxHash = ""; sceneArrivalTime = 0L; missionAcceptTime = 0L
                        tacticalRoute = emptyList()
                        if (queuedMission != null) { activeMission = queuedMission; queuedMission = null; missionState = "ACTIVE" }
                        else { missionState = "IDLE"; activeMission = null }
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
                                        missionState = "ON_SCENE";
                                        sceneArrivalTime = getCurrentTimeMs()
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
                        hasCameraPermission = hasCameraPermission,
                        onRequestCameraPermission = {
                            hasCameraPermission = true
                        },
                        onCapturePhoto = {
                            cameraManager.launchCamera()
                        },
                        onRemovePhoto = { photo ->
                            capturedEvidence = capturedEvidence - photo.toString()
                        },
                        onSubmitEvidence = { isUploadingProof = true }
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

        // --- RESTORED MULTIPLATFORM WALLET ---
        AnimatedVisibility(
            visible = currentScreen == "WALLET",
            enter = slideInHorizontally(initialOffsetX = { it }) + fadeIn(),
            exit = slideOutHorizontally(targetOffsetX = { it }) + fadeOut(),
            modifier = Modifier.fillMaxSize().zIndex(10f)
        ) {
            WalletAndProfileScreen(
                onBack = { currentScreen = "DASHBOARD" },
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
                    Button(onClick = { activeMission = MissionData(33.432, -111.865, "SEC-999: Police Stop", "$50.00", "Mesa Riverview"); missionState = "PENDING"; showDevMenu = false }, colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF333333)), modifier = Modifier.fillMaxWidth()) { Text("LOC 1: Police Liaison (Tier 3)", color = Color.White) }
                    Button(onClick = { activeMission = MissionData(33.385, -111.683, "REQ-002: Lost Item", "$30.00", "Superstition Springs"); missionState = "PENDING"; showDevMenu = false }, colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF333333)), modifier = Modifier.fillMaxWidth()) { Text("LOC 2: Lost Item (Tier 1)", color = Color.White) }
                    Button(onClick = { activeMission = MissionData(33.415, -111.831, "ERR-DOOR: Latch Fault", "$15.00", "Downtown Mesa"); missionState = "PENDING"; showDevMenu = false }, colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF333333)), modifier = Modifier.fillMaxWidth()) { Text("LOC 3: Door Securing (Tier 1)", color = Color.White) }
                } }, confirmButton = {}, dismissButton = { TextButton(onClick = { showDevMenu = false }) { Text("CLOSE", color = Color.Gray) } }
            )
        }

        if (showAbortDialog) {
            AlertDialog(onDismissRequest = { showAbortDialog = false; abortSliderResetKey++ }, containerColor = Color(0xFF1E1E1E), title = { Text("ABORT MISSION", color = Color.White, fontWeight = FontWeight.Black) },
                text = { Column { listOf("Too Dangerous", "Changed Mind", "Can't Find AV", "AV Leaving Scene", "Other").forEach { reason ->
                    Button(onClick = {
                        showAbortDialog = false; missionState = "IDLE"; activeMission = null; queuedMission = null; abortSliderResetKey++
                        missionAcceptTime = 0L; sceneArrivalTime = 0L
                        tacticalRoute = emptyList()
                    }, colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF333333)), modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp), shape = RoundedCornerShape(8.dp)) { Text(reason, color = Color.White, fontWeight = FontWeight.Bold) }
                } } }, confirmButton = {}, dismissButton = { TextButton(onClick = { showAbortDialog = false; abortSliderResetKey++ }) { Text("CANCEL", color = Color.Gray) } }
            )
        }
    }
}