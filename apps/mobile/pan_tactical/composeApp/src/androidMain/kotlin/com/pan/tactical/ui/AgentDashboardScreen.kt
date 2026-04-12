package com.pan.tactical.ui

import android.graphics.BitmapFactory
import androidx.fragment.app.FragmentActivity
import androidx.compose.ui.platform.LocalContext
import androidx.compose.animation.*
import androidx.compose.animation.core.*
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
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
import kotlin.math.*
import com.pan.tactical.ui.components.OfflineLoadoutMenu
import com.pan.tactical.ui.components.OnSceneTerminal
import com.pan.tactical.ui.components.PostMissionOverlays
import com.pan.tactical.ui.components.MissionAlertOverlay
import com.pan.tactical.ui.components.SwipeActionSlider
import com.pan.tactical.ui.components.UwbHomingCompass
import com.pan.tactical.ui.components.FeedbackScreen
import com.pan.tactical.ui.components.FeedbackIssueChip
import com.pan.tactical.ui.components.RankUpOverlay
import com.pan.tactical.ui.components.TacticalStatusBar
import com.pan.tactical.ui.components.MissionControlsPanel
import com.pan.tactical.models.AgentCapability
import com.pan.tactical.models.AgentCapabilityUiModel
import com.pan.tactical.AudioEngine
import com.pan.tactical.getCurrentTimeMs
import com.pan.tactical.getNativeMapUrl
import com.pan.tactical.rememberSharedCameraManager
import com.pan.tactical.rememberSharedLocationManager
import com.pan.tactical.security.BiometricAuthHelper
import com.pan.tactical.security.AndroidBiometricAuthHelper
import com.pan.tactical.network.PanApiClient
import com.pan.tactical.network.PanWalletClient
import com.pan.tactical.ui.mission.MissionViewModel
import com.pan.tactical.ui.mission.MissionPhase
import com.pan.tactical.ui.theme.PanColors
import pantactical.composeapp.generated.resources.Res
import pantactical.composeapp.generated.resources.pan_logo

@Composable
actual fun AgentDashboardScreen(
    apiClient: WalletNetworkClient
) {
    val panClient = apiClient as? PanApiClient
    if (panClient == null) {
        Box(modifier = Modifier.fillMaxSize().background(Color.Black), contentAlignment = Alignment.Center) {
            Text(
                text = "CRITICAL ARCHITECTURE ERROR:\nPanApiClient required for Tactical Dashboard.\nCurrent client is incompatible.",
                color = PanColors.AlertRed,
                fontWeight = FontWeight.Bold,
                textAlign = androidx.compose.ui.text.style.TextAlign.Center
            )
        }
        return
    }

    val context = LocalContext.current
    val fragmentActivity = context as? FragmentActivity
        ?: throw IllegalStateException("Dashboard requires FragmentActivity for biometrics")
    val biometricHelper = remember { AndroidBiometricAuthHelper(fragmentActivity) }

    val coroutineScope = rememberCoroutineScope()
    val trueWalletClient = remember { PanWalletClient() }

    val missionViewModel = remember {
        MissionViewModel(
            apiClient = trueWalletClient,
            walletClient = trueWalletClient,
            scope = coroutineScope
        )
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
                        missionViewModel.initialize()
                        currentScreen = "DASHBOARD"
                        delay(500)
                        appState = "RUNNING"
                    }
                }
                "RUNNING" -> MainDashboardContent(
                    apiClient = panClient,
                    rawWalletClient = trueWalletClient,
                    missionViewModel = missionViewModel,
                    biometricHelper = biometricHelper,
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

@Composable
fun MainDashboardContent(
    apiClient: PanApiClient,
    rawWalletClient: WalletNetworkClient,
    missionViewModel: MissionViewModel,
    biometricHelper: BiometricAuthHelper,
    currentScreen: String,
    onNavigate: (String) -> Unit
) {
    val coroutineScope = rememberCoroutineScope()
    val snackbarHostState = remember { SnackbarHostState() }
    val audio = remember { AudioEngine() }
    val uriHandler = LocalUriHandler.current

    val uiState by missionViewModel.uiState.collectAsState()

    val homingState = object {
        val isResolving = false
        val terminalLogs = emptyList<String>()
        val extensionRequest: com.pan.tactical.managers.SentryExtensionRequest? = null
    }

    DisposableEffect(Unit) {
        onDispose {
            audio.shutdown()
            missionViewModel.close()
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
    var showAbortDialog by rememberSaveable { mutableStateOf(false) }
    var showDevMenu by rememberSaveable { mutableStateOf(false) }
    var abortSliderResetKey by rememberSaveable { mutableIntStateOf(0) }

    var storeBalance by rememberSaveable { mutableDoubleStateOf(0.0) }
    var storeMissions by rememberSaveable { mutableIntStateOf(0) }

    var isMissionControlsExpanded by rememberSaveable { mutableStateOf(false) }

    var agentCapabilities by remember {
        mutableStateOf(
            listOf(
                AgentCapabilityUiModel(capability = AgentCapability("door_securing", "Door Securing", "Push door completely shut.", null, 1, isQualified = true), isEnabled = true),
                AgentCapabilityUiModel(capability = AgentCapability("cabin_sweep", "Cabin Sweep & Trash", "Bag and dispose of trash.", null, 1, isQualified = true), isEnabled = true),
                AgentCapabilityUiModel(capability = AgentCapability("lost_item", "Lost Item Recovery", "Retrieve and secure item.", null, 1, isQualified = true), isEnabled = false),
                AgentCapabilityUiModel(capability = AgentCapability("path_clearing", "Path Clearing", "Remove debris/cones from path.", null, 1, isQualified = true), isEnabled = true),

                AgentCapabilityUiModel(capability = AgentCapability("spill_remediation", "Bio/Liquid Remediation", "Sanitize interior spills.", "Requires wet-vac/bio-kit", 2, isQualified = true), isEnabled = false),
                AgentCapabilityUiModel(capability = AgentCapability("tire_pressure", "Tire Pressure", "Refill low tire.", "Requires air compressor", 2, isQualified = true), isEnabled = false),
                AgentCapabilityUiModel(capability = AgentCapability("battery_jump", "12V System Jump", "Wake AV with jump-box.", "Requires jump kit", 2, isQualified = true), isEnabled = false),
                AgentCapabilityUiModel(capability = AgentCapability("passenger_escort", "Passenger Escort", "Calm and escort passenger.", "High-vis vest required", 2, isQualified = true), isEnabled = false),

                AgentCapabilityUiModel(capability = AgentCapability("sensor_cleaning", "Sensor Cleaning", "Microfiber clean LIDAR dome.", "Certified cleaning kit", 3, isQualified = true), isEnabled = true),
                AgentCapabilityUiModel(capability = AgentCapability("scene_securement", "First Responder Liaison", "Interact with police/flares.", "Requires safety flares", 3, isQualified = true), isEnabled = true),
                AgentCapabilityUiModel(capability = AgentCapability("tire_replacement", "Tire Replacement", "Swap spare or plug blowout.", "Requires jack/plug kit", 3, isQualified = true), isEnabled = true),
                AgentCapabilityUiModel(capability = AgentCapability("manual_override", "Manual Drive Takeover", "Manually extract AV.", "Special ops clearance", 3, isQualified = true), isEnabled = true)
            )
        )
    }

    var agentLocation by remember { mutableStateOf(Pair(33.3061, -111.6601)) }
    var lastTelemetryTime by remember { mutableLongStateOf(0L) }

    val distanceMiles = remember(agentLocation, uiState.activeMission) {
        if (uiState.activeMission == null) return@remember 0.0
        val lat1 = agentLocation.first * PI / 180.0
        val lon1 = agentLocation.second * PI / 180.0
        val lat2 = uiState.activeMission!!.lat * PI / 180.0
        val lon2 = uiState.activeMission!!.lon * PI / 180.0
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

    LaunchedEffect(uiState.missionPhase) {
        when (uiState.missionPhase) {
            MissionPhase.IDLE -> {
                isFlashing = false
                isMissionControlsExpanded = false
            }
            MissionPhase.PENDING -> {
                launch {
                    while (true) {
                        isFlashing = !isFlashing
                        delay(500)
                    }
                }

                val rawBounty = uiState.activeMission?.bountyUsd ?: 0.0
                val netPayout = rawBounty * 0.90
                val cleanBounty = if (netPayout % 1.0 == 0.0) netPayout.toInt().toString() else netPayout.toString()
                val cleanCategory = uiState.activeMission?.errorCode?.substringAfter(": ") ?: uiState.activeMission?.errorCode ?: "Unknown"
                val cleanDistance = ((distanceMiles * 10.0).roundToInt() / 10.0).toString()

                audio.speak("Agent, Mission: $cleanCategory. $cleanDistance Miles Away. Payout, $cleanBounty dollars.", voiceVolume)

                countdownProgress.snapTo(1f)

                countdownProgress.animateTo(
                    targetValue = 0f,
                    animationSpec = tween(durationMillis = 60000, easing = LinearEasing)
                )

                if (missionViewModel.uiState.value.missionPhase == MissionPhase.PENDING) {
                    missionViewModel.onMissionDeclined()
                }
            }
            MissionPhase.ACTIVE -> {
                isFlashing = false
                isMissionControlsExpanded = false
            }
            MissionPhase.ON_SCENE, MissionPhase.COMPLETED -> {
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
        agentLocation = Pair(lat, lon)

        val now = getCurrentTimeMs()
        if (uiState.isOnline && now - lastTelemetryTime > 3000) {
            lastTelemetryTime = now
            coroutineScope.launch {
                try {
                    rawWalletClient.updateLocationTelemetry(lat, lon)
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
        val bytes = imageData as? ByteArray ?: return@rememberSharedCameraManager
        val newList = capturedEvidence.toMutableList()
        newList.add(bytes)
        capturedEvidence = newList.toList()
    }

    val bearingDegrees = remember(agentLocation, uiState.activeMission) {
        if (uiState.activeMission == null) return@remember 0f
        val lat1 = agentLocation.first * PI / 180.0
        val lon1 = agentLocation.second * PI / 180.0
        val lat2 = uiState.activeMission!!.lat * PI / 180.0
        val lon2 = uiState.activeMission!!.lon * PI / 180.0

        val dLon = lon2 - lon1
        val y = sin(dLon) * cos(lat2)
        val x = cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(dLon)
        var brng = atan2(y, x) * 180.0 / PI
        brng = (brng + 360.0) % 360.0
        brng.toFloat()
    }

    val isUwbEngaged = (uiState.missionPhase == MissionPhase.ACTIVE || uiState.missionPhase == MissionPhase.ON_SCENE) && distanceMeters <= 15f

    LaunchedEffect(distanceMiles) {
        if (uiState.missionPhase == MissionPhase.ACTIVE && distanceMiles <= 0.1) {
            isMissionControlsExpanded = true
        }
    }

    val tacticalMapStyle = """[{"elementType":"geometry","stylers":[{"color":"#121212"}]},{"elementType":"labels.icon","stylers":[{"visibility":"off"}]},{"elementType":"labels.text.fill","stylers":[{"color":"#EEEEEE"}]},{"elementType":"labels.text.stroke","stylers":[{"color":"#000000"},{"weight":3}]},{"featureType":"road","elementType":"geometry","stylers":[{"color":"#555555"}]}]"""

    Box(modifier = Modifier.fillMaxSize()) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .background(PanColors.SurfaceDark)
        ) {
            TacticalStatusBar(
                isOnline = uiState.isOnline,
                onNavigateToWallet = { onNavigate("WALLET") },
                onDevMenuLongPress = { showDevMenu = true }
            )

            Box(modifier = Modifier.fillMaxWidth().weight(1f).background(PanColors.SurfaceMid), contentAlignment = Alignment.Center) {

                AnimatedContent(
                    targetState = isUwbEngaged,
                    transitionSpec = {
                        fadeIn(animationSpec = tween(500)) togetherWith fadeOut(animationSpec = tween(500))
                    },
                    label = "map_to_uwb_transition"
                ) { showUwb ->
                    if (showUwb) {
                        UwbHomingCompass(
                            distanceMeters = distanceMeters,
                            bearingDegrees = bearingDegrees,
                            isRanging = true
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

                androidx.compose.animation.AnimatedVisibility(
                    visible = uiState.missionPhase == MissionPhase.PENDING && uiState.activeMission != null,
                    enter = slideInVertically(initialOffsetY = { it }) + fadeIn(),
                    exit = slideOutVertically(targetOffsetY = { it }) + fadeOut(),
                    modifier = Modifier.fillMaxSize()
                ) {
                    MissionAlertOverlay(
                        activeMission = uiState.activeMission,
                        countdownProgress = countdownProgress.value,
                        flashAlpha = flashAlpha,
                        onAccept = {
                            val targetLat = uiState.activeMission?.lat ?: 0.0
                            val targetLon = uiState.activeMission?.lon ?: 0.0

                            // 🟢 FIX: Fetch actual road polyline from OSRM
                            coroutineScope.launch {
                                val realRoute = (rawWalletClient as? PanWalletClient)?.getTacticalRoute(
                                    agentLocation.first, agentLocation.second,
                                    targetLat, targetLon
                                )
                                if (realRoute != null && realRoute.isNotEmpty()) {
                                    tacticalRoute = realRoute
                                } else {
                                    tacticalRoute = listOf(agentLocation, Pair(targetLat, targetLon))
                                }
                            }

                            missionViewModel.onMissionAccepted()

                            try {
                                uriHandler.openUri(getNativeMapUrl(targetLat, targetLon))
                            } catch (e: Exception) {
                                println("[NAVIGATION_ERROR] Failed to open native map: ${e.message}")
                            }
                        },
                        onDecline = {
                            missionViewModel.onMissionDeclined()
                            tacticalRoute = emptyList()
                        }
                    )
                }

                PostMissionOverlays(
                    isUploadingProof = homingState.isResolving,
                    capturedEvidence = capturedEvidence,
                    missionState = uiState.missionPhase.name,
                    lastPayoutAmount = uiState.lastPayoutAmount,
                    timeOnSceneMs = uiState.timeOnSceneMs,
                    totalResponseTimeMs = uiState.totalResponseTimeMs,
                    lastTxHash = uiState.lastTxHash,
                    onReturnToPatrol = {
                        missionViewModel.onReturnToPatrol()
                    }
                )
            }

            Column(modifier = Modifier.fillMaxWidth().background(PanColors.CardBackground), horizontalAlignment = Alignment.CenterHorizontally) {

                AnimatedVisibility(visible = uiState.missionPhase == MissionPhase.ACTIVE, enter = expandVertically() + fadeIn(), exit = shrinkVertically() + fadeOut()) {
                    MissionControlsPanel(
                        activeMission = uiState.activeMission,
                        isExpanded = isMissionControlsExpanded,
                        onToggleExpand = { isMissionControlsExpanded = !isMissionControlsExpanded },
                        onArrivedAtScene = { missionViewModel.onArrivedAtScene() },
                        onAbortRequested = { showAbortDialog = true },
                        abortSliderKey = abortSliderResetKey
                    )
                }

                AnimatedVisibility(visible = uiState.missionPhase == MissionPhase.ON_SCENE, enter = expandVertically() + fadeIn(), exit = shrinkVertically() + fadeOut()) {
                    OnSceneTerminal(
                        activeMission = uiState.activeMission,
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
                                capturedEvidence = mutableList.toList()
                            }
                        },
                        onSubmitEvidence = {
                            val taskId = uiState.activeMission?.taskId
                            if (!taskId.isNullOrBlank()) {
                                coroutineScope.launch {
                                    val success = rawWalletClient.completeMission(
                                        taskId = taskId,
                                        evidenceUrls = listOf("mock_evidence_bypass.jpg")
                                    )

                                    if (success) {
                                        missionViewModel.onMissionSuccess()
                                        audio.speak("Mission accomplished. Escrow funds secured.", voiceVolume)
                                        capturedEvidence = emptyList()
                                    } else {
                                        snackbarHostState.showSnackbar("ERROR: Backend rejected mission completion.")
                                    }
                                }
                            }
                        },
                        onAcceptExtension = { _, _, _ -> },
                        onDeclineExtension = { },
                        onVerifyIdentity = { onResult ->
                            coroutineScope.launch {
                                onResult(
                                    biometricHelper.authenticate(
                                        promptTitle = "Agent Attestation Required",
                                        promptSubtitle = "Authenticate to cryptographically sign mission evidence"
                                    )
                                )
                            }
                        },
                        onLogEntry = { }
                    )
                }

                AnimatedVisibility(visible = uiState.missionPhase == MissionPhase.IDLE) {
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

                AnimatedVisibility(visible = uiState.missionPhase == MissionPhase.IDLE) {
                    Box(modifier = Modifier.padding(start = 16.dp, end = 16.dp, bottom = 16.dp)) {
                        if (uiState.isOnline) {
                            SwipeActionSlider(
                                text = "SWIPE TO GO OFFLINE >>",
                                trackColor = PanColors.ButtonSecondary,
                                thumbColor = PanColors.AlertRed,
                                onSwipeComplete = {
                                    missionViewModel.goOffline()
                                }
                            )
                        } else {
                            Button(
                                enabled = !uiState.isProcessing,
                                onClick = { missionViewModel.goOnline(agentLocation.first, agentLocation.second) },
                                modifier = Modifier.fillMaxWidth().height(56.dp),
                                colors = ButtonDefaults.buttonColors(
                                    containerColor = PanColors.OnlineGreen,
                                    disabledContainerColor = PanColors.Disabled
                                )
                            ) {
                                if (uiState.isProcessing) {
                                    CircularProgressIndicator(color = Color.White)
                                } else {
                                    Text("GO ONLINE", color = Color.White, fontWeight = FontWeight.Bold, letterSpacing = 1.sp)
                                }
                            }
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
                apiClient = rawWalletClient,
                onBack = { onNavigate("DASHBOARD") },
                onNavigateToStore = { bal, miss ->
                    storeBalance = bal
                    storeMissions = miss
                    onNavigate("STORE")
                },
                navPreference = navPreference,
                onNavPrefChange = { navPreference = it },
                audioEngine = audio,
                voiceVolume = voiceVolume,
                onVoiceVolumeChange = { voiceVolume = it },
                alertVolume = alertVolume,
                onAlertVolumeChange = { alertVolume = it }
            )
        }

        AnimatedVisibility(
            visible = currentScreen == "STORE",
            enter = slideInHorizontally(initialOffsetX = { it }) + fadeIn(),
            exit = slideOutHorizontally(targetOffsetX = { it }) + fadeOut(),
            modifier = Modifier.fillMaxSize().zIndex(15f)
        ) {
            StoreScreen(
                currentBalance = storeBalance,
                missionsCompleted = storeMissions,
                onBack = { onNavigate("WALLET") },
                onJoinWaitlist = { itemId, email ->
                    (rawWalletClient as? PanWalletClient)?.joinWaitlist(itemId, email) ?: false
                }
            )
        }

        if (showDevMenu) {
            AlertDialog(onDismissRequest = { showDevMenu = false }, containerColor = PanColors.CardBackground, title = { Text("DEV: INJECT MISSION", color = Color.White, fontWeight = FontWeight.Black) },
                text = { Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {

                    // 🟢 FIX: Moved mock locations to snap directly to actual road networks near the Agent
                    Button(onClick = {
                        coroutineScope.launch { rawWalletClient.triggerBackendDispatch(33.3161, -111.6601, "scene_securement") }
                        showDevMenu = false
                    }, colors = ButtonDefaults.buttonColors(containerColor = PanColors.ButtonSecondary), modifier = Modifier.fillMaxWidth()) { Text("LOC 1: Police Liaison (Tier 3)", color = Color.White) }

                    Button(onClick = {
                        coroutineScope.launch { rawWalletClient.triggerBackendDispatch(33.3061, -111.6451, "spill_remediation") }
                        showDevMenu = false
                    }, colors = ButtonDefaults.buttonColors(containerColor = PanColors.ButtonSecondary), modifier = Modifier.fillMaxWidth()) { Text("LOC 2: Bio/Liquid Remediation (Tier 2)", color = Color.White) }

                    Button(onClick = {
                        coroutineScope.launch { rawWalletClient.triggerBackendDispatch(33.2961, -111.6601, "latch_fault") }
                        showDevMenu = false
                    }, colors = ButtonDefaults.buttonColors(containerColor = PanColors.ButtonSecondary), modifier = Modifier.fillMaxWidth()) { Text("LOC 3: Door Securing (Tier 1)", color = Color.White) }

                    Button(onClick = {
                        val newList = capturedEvidence.toMutableList()
                        newList.add(byteArrayOf(0x00))
                        capturedEvidence = newList.toList()
                        showDevMenu = false
                        coroutineScope.launch {
                            snackbarHostState.showSnackbar("Mock Evidence Injected!")
                        }
                    }, colors = ButtonDefaults.buttonColors(containerColor = PanColors.WarningOrange), modifier = Modifier.fillMaxWidth()) { Text("DEV: INJECT MOCK EVIDENCE", color = Color.Black, fontWeight = FontWeight.Bold) }
                } }, confirmButton = {}, dismissButton = { TextButton(onClick = { showDevMenu = false }) { Text("CLOSE", color = Color.Gray) } }
            )
        }

        if (showAbortDialog) {
            AlertDialog(onDismissRequest = { showAbortDialog = false; abortSliderResetKey++ }, containerColor = PanColors.CardBackground, title = { Text("ABORT MISSION", color = Color.White, fontWeight = FontWeight.Black) },
                text = { Column { listOf("Too Dangerous", "Changed Mind", "Can't Find AV", "AV Leaving Scene", "Other").forEach { reason ->
                    Button(onClick = {
                        missionViewModel.onMissionAborted(reason)
                        showAbortDialog = false; abortSliderResetKey++
                        tacticalRoute = emptyList()
                        capturedEvidence = emptyList()
                    }, colors = ButtonDefaults.buttonColors(containerColor = PanColors.ButtonSecondary), modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp), shape = RoundedCornerShape(8.dp)) { Text(reason, color = Color.White, fontWeight = FontWeight.Bold) }
                } } }, confirmButton = {}, dismissButton = { TextButton(onClick = { showAbortDialog = false; abortSliderResetKey++ }) { Text("CANCEL", color = Color.Gray) } }
            )
        }

        AnimatedVisibility(
            visible = uiState.showFeedbackScreen,
            enter = fadeIn(),
            exit = fadeOut(),
            modifier = Modifier.fillMaxSize().zIndex(20f)
        ) {
            FeedbackScreen(
                taskId = uiState.feedbackTaskId,
                fleetId = uiState.feedbackFleetId,
                payoutAmount = uiState.lastPayoutAmount,
                issueChips = listOf(
                    FeedbackIssueChip("Biohazard Unreported", "SAFETY"),
                    FeedbackIssueChip("Hardware Defect", "SAFETY"),
                    FeedbackIssueChip("Incorrect Fault Code", "COMPLIANCE"),
                    FeedbackIssueChip("Bounty Dispute", "CONDUCT"),
                    FeedbackIssueChip("API Timeout", "LOGISTICS"),
                    FeedbackIssueChip("Vehicle Not at Pin", "LOGISTICS")
                ),
                onSubmit = { isPositive, category, label, ventText ->
                    (rawWalletClient as? PanWalletClient)?.submitMissionFeedback(
                        taskId = uiState.feedbackTaskId,
                        isPositive = isPositive,
                        category = category,
                        label = label,
                        ventText = ventText
                    ) ?: false
                },
                onDismiss = {
                    missionViewModel.onFeedbackDismissed()
                    tacticalRoute = emptyList()
                }
            )
        }

        AnimatedVisibility(
            visible = uiState.showRankUp,
            enter = fadeIn(),
            exit = fadeOut(),
            modifier = Modifier.fillMaxSize().zIndex(25f)
        ) {
            RankUpOverlay(
                newRank = uiState.rankUpTo,
                ownsHapHat = false,
                ownsGauntlets = false,
                onDismiss = { missionViewModel.onRankUpDismissed() }
            )
        }

        SnackbarHost(
            hostState = snackbarHostState,
            modifier = Modifier.align(Alignment.BottomCenter).padding(bottom = 16.dp),
            snackbar = { data ->
                Snackbar(
                    containerColor = PanColors.QualifiedGreen,
                    contentColor = Color.White,
                    shape = RoundedCornerShape(8.dp)
                ) {
                    Text(text = data.visuals.message, fontWeight = FontWeight.Bold)
                }
            }
        )
    }
}