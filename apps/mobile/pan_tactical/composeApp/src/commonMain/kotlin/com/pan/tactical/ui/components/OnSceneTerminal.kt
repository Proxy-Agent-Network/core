package com.pan.tactical.ui.components

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
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
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import coil3.compose.AsyncImage
import com.pan.tactical.models.MissionData
import com.pan.tactical.managers.SentryExtensionRequest

@Composable
fun OnSceneTerminal(
    activeMission: MissionData?,
    capturedEvidence: List<ByteArray>,
    isProcessingRedaction: Boolean,
    isResolving: Boolean, 
    terminalLogs: List<String>, 
    hasCameraPermission: Boolean,
    extensionRequest: SentryExtensionRequest?, 
    onRequestCameraPermission: () -> Unit,
    onCapturePhoto: () -> Unit,
    onRemovePhoto: (Int) -> Unit,
    onSubmitEvidence: () -> Unit, 
    onAcceptExtension: (String, Int, Double) -> Unit, 
    onDeclineExtension: () -> Unit, 
    onVerifyIdentity: (onResult: (Boolean) -> Unit) -> Unit,
    onLogEntry: (String) -> Unit // 🛡️ FIXED: Callback bridge for UI-driven logs
) {
    var biometricsPassed by remember { mutableStateOf(true) }
    var isVerifyingBiometrics by remember { mutableStateOf(false) }
    val requiredPhotos = 2

    LaunchedEffect(activeMission) {
        biometricsPassed = activeMission?.requiresAttestation != true 
        // 🛡️ HOLE 3 FIXED: Attestation warning restored
        if (!biometricsPassed) {
            onLogEntry("WARNING: Identity verification required for this asset.")
        }
    }

    // 🛡️ HOLE 1 FIXED: PrivacyFilter feedback restored
    LaunchedEffect(isProcessingRedaction) {
        if (isProcessingRedaction) {
            onLogEntry("PrivacyFilter: Redacting PII and scaling to 720p...")
        } else if (capturedEvidence.isNotEmpty()) {
            onLogEntry("Compliance pass complete. Evidence sanitized.")
        }
    }

    Box(modifier = Modifier.fillMaxSize()) {
        Column(
            modifier = Modifier.fillMaxWidth().padding(16.dp).background(Color(0xFF0D1117)).padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text("📟 AV DIAGNOSTIC TERMINAL", color = Color(0xFF00FF00), fontSize = 16.sp, fontWeight = FontWeight.Black)
            Spacer(modifier = Modifier.height(12.dp))

            Box(modifier = Modifier.fillMaxWidth().height(140.dp).background(Color.Black, RoundedCornerShape(8.dp)).border(1.dp, Color(0xFF333333), RoundedCornerShape(8.dp)).padding(12.dp)) {
                Column(modifier = Modifier.verticalScroll(rememberScrollState())) {
                    terminalLogs.forEach { log ->
                        Text("> $log", color = Color(0xFF00FF00), fontFamily = FontFamily.Monospace, fontSize = 12.sp)
                        Spacer(modifier = Modifier.height(4.dp))
                    }
                }
            }
            Spacer(modifier = Modifier.height(16.dp))

            if (!biometricsPassed) {
                SecurityCheckUI(
                    isVerifying = isVerifyingBiometrics,
                    onVerify = {
                        isVerifyingBiometrics = true
                        onVerifyIdentity { success ->
                            isVerifyingBiometrics = false
                            if (success) {
                                biometricsPassed = true
                                // 🛡️ HOLE 2 FIXED: Biometric success feedback restored
                                onLogEntry("Identity verified via StrongBox.")
                            } else {
                                // 🛡️ HOLE 2 FIXED: Biometric failure feedback restored
                                onLogEntry("ERROR: Verification failed.")
                            }
                        }
                    }
                )
            } else {
                if (capturedEvidence.isNotEmpty()) {
                    Row(modifier = Modifier.fillMaxWidth().horizontalScroll(rememberScrollState()).padding(bottom = 16.dp), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        capturedEvidence.forEachIndexed { index, imgBytes ->
                            EvidenceThumbnail(index, imgBytes, onRemovePhoto)
                        }
                    }
                }

                ActionButtons(
                    evidenceCount = capturedEvidence.size,
                    requiredPhotos = requiredPhotos,
                    isProcessingRedaction = isProcessingRedaction,
                    isResolving = isResolving,
                    hasCameraPermission = hasCameraPermission,
                    onCapturePhoto = onCapturePhoto,
                    onRequestCameraPermission = onRequestCameraPermission,
                    onSubmit = onSubmitEvidence
                )
            }
        }

        AnimatedVisibility(
            visible = extensionRequest != null,
            enter = fadeIn(),
            exit = fadeOut()
        ) {
            val stableRequest = remember { extensionRequest } ?: return@AnimatedVisibility
            SentryExtensionOverlay(
                request = stableRequest,
                onAccept = { onAcceptExtension(stableRequest.taskId, stableRequest.extensionMinutes, stableRequest.offeredBountyUsd) },
                onDecline = onDeclineExtension
            )
        }
    }
}

@Composable
fun SentryExtensionOverlay(request: SentryExtensionRequest, onAccept: () -> Unit, onDecline: () -> Unit) {
    Box(modifier = Modifier.fillMaxSize().background(Color(0xEE000000)).padding(24.dp), contentAlignment = Alignment.Center) {
        Column(
            modifier = Modifier.background(Color(0xFF1E1E1E), RoundedCornerShape(16.dp)).border(2.dp, Color(0xFF4CAF50), RoundedCornerShape(16.dp)).padding(24.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text("🛡️ SENTRY EXTENSION", color = Color(0xFF4CAF50), fontSize = 20.sp, fontWeight = FontWeight.Black)
            Spacer(modifier = Modifier.height(12.dp))
            Text(text = "The fleet requires an additional ${request.extensionMinutes}m of scene securement.", color = Color.White, textAlign = TextAlign.Center)
            Spacer(modifier = Modifier.height(16.dp))
            Text(text = "+$${"%.2f".format(request.offeredBountyUsd)} BOUNTY", color = Color(0xFF4CAF50), fontSize = 28.sp, fontWeight = FontWeight.Black)
            Spacer(modifier = Modifier.height(24.dp))
            Button(onClick = onAccept, modifier = Modifier.fillMaxWidth().height(56.dp), colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF4CAF50))) {
                Text("ACCEPT & EXTEND", fontWeight = FontWeight.ExtraBold, color = Color.White)
            }
            Spacer(modifier = Modifier.height(8.dp))
            TextButton(onClick = onDecline, modifier = Modifier.fillMaxWidth().height(48.dp)) {
                Text("DECLINE", color = Color.Gray, fontWeight = FontWeight.Bold)
            }
        }
    }
}

@Composable
fun EvidenceThumbnail(index: Int, imgBytes: ByteArray, onRemove: (Int) -> Unit) {
    Box(modifier = Modifier.size(80.dp).border(2.dp, Color(0xFF00BCD4), RoundedCornerShape(8.dp)).clip(RoundedCornerShape(8.dp))) {
        AsyncImage(model = imgBytes, contentDescription = "Evidence", modifier = Modifier.fillMaxSize(), contentScale = ContentScale.Crop)
        Box(modifier = Modifier.align(Alignment.BottomStart).background(Color(0xAA000000)).padding(4.dp)) {
            Text(if (index == 0) "BEFORE" else "AFTER", color = Color.White, fontSize = 8.sp, fontWeight = FontWeight.Bold)
        }
        Box(modifier = Modifier.align(Alignment.TopEnd).padding(4.dp).size(22.dp).background(Color(0xAA000000), RoundedCornerShape(11.dp)).clickable { onRemove(index) }, contentAlignment = Alignment.Center) {
            Text("✕", color = Color.Red, fontSize = 12.sp, fontWeight = FontWeight.Bold)
        }
    }
}

@Composable
fun ActionButtons(evidenceCount: Int, requiredPhotos: Int, isProcessingRedaction: Boolean, isResolving: Boolean, hasCameraPermission: Boolean, onCapturePhoto: () -> Unit, onRequestCameraPermission: () -> Unit, onSubmit: () -> Unit) {
    if (evidenceCount < requiredPhotos) {
        Button(enabled = !isProcessingRedaction, onClick = { if (hasCameraPermission) onCapturePhoto() else onRequestCameraPermission() }, colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF4CAF50), disabledContainerColor = Color(0xFF1B3D20)), modifier = Modifier.fillMaxWidth().height(64.dp), shape = RoundedCornerShape(8.dp)) {
            if (isProcessingRedaction) CircularProgressIndicator(modifier = Modifier.size(20.dp), color = Color.White)
            else Text("CAPTURE PHOTO (${evidenceCount}/$requiredPhotos)", color = Color.White, fontWeight = FontWeight.Black)
        }
    } else {
        Button(enabled = !isResolving && !isProcessingRedaction, onClick = onSubmit, colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF00BCD4), disabledContainerColor = Color(0xFF1E3538)), modifier = Modifier.fillMaxWidth().height(64.dp), shape = RoundedCornerShape(8.dp)) {
            if (isResolving) CircularProgressIndicator(modifier = Modifier.size(24.dp), color = Color.Black)
            else Text("RE-RUN DIAGNOSTICS & SUBMIT", color = Color.Black, fontWeight = FontWeight.Black)
        }
    }
}

@Composable
fun SecurityCheckUI(isVerifying: Boolean, onVerify: () -> Unit) {
    Box(modifier = Modifier.fillMaxWidth().border(2.dp, Color.Red, RoundedCornerShape(8.dp)).background(Color(0xFF2A0000), RoundedCornerShape(8.dp)).padding(16.dp)) {
        Column(horizontalAlignment = Alignment.CenterHorizontally, modifier = Modifier.fillMaxWidth()) {
            Text("⚠️ IDENTITY ATTESTATION REQUIRED ⚠️", color = Color.Red, fontWeight = FontWeight.Bold, fontSize = 14.sp)
            Spacer(modifier = Modifier.height(12.dp))
            Button(onClick = onVerify, enabled = !isVerifying, colors = ButtonDefaults.buttonColors(containerColor = Color.Red)) {
                if (isVerifying) CircularProgressIndicator(modifier = Modifier.size(20.dp), color = Color.White)
                else Text("VERIFY IDENTITY", color = Color.White, fontWeight = FontWeight.Black)
            }
        }
    }
}