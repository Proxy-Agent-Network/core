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
    onLogEntry: (String) -> Unit
) {
    // 🟢 FIX: Safely convert the role into a String first
    val isSentry = activeMission?.role.toString().uppercase() == "SENTRY"

    var biometricsPassed by remember { mutableStateOf(true) }
    var isVerifyingBiometrics by remember { mutableStateOf(false) }
    val requiredPhotos = 2

    LaunchedEffect(activeMission) {
        biometricsPassed = activeMission?.requiresAttestation != true
        if (!biometricsPassed) {
            onLogEntry("WARNING: Identity verification required for this asset.")
        }
    }

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
            val titleText = if (isSentry) "🚧 SENTRY TRAFFIC CONTROL" else "📟 AV DIAGNOSTIC TERMINAL"
            val titleColor = if (isSentry) Color(0xFFFF9800) else Color(0xFF00FF00)

            Text(titleText, color = titleColor, fontSize = 16.sp, fontWeight = FontWeight.Black)
            Spacer(modifier = Modifier.height(12.dp))

            if (isSentry) {
                Text(
                    text = "INSTRUCTIONS: Park near the scene. If the primary agent is already there, greet them. Stand 20 feet behind the AV and redirect traffic around the AV while the primary clears the error.",
                    color = Color(0xFFCCCCCC),
                    fontSize = 14.sp,
                    textAlign = TextAlign.Center,
                    modifier = Modifier.padding(horizontal = 8.dp).padding(bottom = 12.dp)
                )
            }

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
                                onLogEntry("Identity verified via StrongBox.")
                            } else {
                                onLogEntry("ERROR: Verification failed.")
                            }
                        }
                    }
                )
            } else {
                if (capturedEvidence.isNotEmpty()) {
                    Row(modifier = Modifier.fillMaxWidth().horizontalScroll(rememberScrollState()).padding(bottom = 16.dp), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        capturedEvidence.forEachIndexed { index, imgBytes ->
                            EvidenceThumbnail(index, imgBytes, isSentry, onRemovePhoto)
                        }
                    }
                }

                ActionButtons(
                    evidenceCount = capturedEvidence.size,
                    requiredPhotos = requiredPhotos,
                    isProcessingRedaction = isProcessingRedaction,
                    isResolving = isResolving,
                    hasCameraPermission = hasCameraPermission,
                    isSentry = isSentry,
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
fun EvidenceThumbnail(index: Int, imgBytes: ByteArray, isSentry: Boolean, onRemove: (Int) -> Unit) {
    val labelText = if (isSentry) {
        if (index == 0) "SETUP" else "TRAFFIC"
    } else {
        if (index == 0) "BEFORE" else "AFTER"
    }

    Box(modifier = Modifier.size(80.dp).border(2.dp, Color(0xFF00BCD4), RoundedCornerShape(8.dp)).clip(RoundedCornerShape(8.dp))) {
        AsyncImage(model = imgBytes, contentDescription = "Evidence", modifier = Modifier.fillMaxSize(), contentScale = ContentScale.Crop)
        Box(modifier = Modifier.align(Alignment.BottomStart).background(Color(0xAA000000)).padding(4.dp)) {
            Text(labelText, color = Color.White, fontSize = 8.sp, fontWeight = FontWeight.Bold)
        }
        Box(modifier = Modifier.align(Alignment.TopEnd).padding(4.dp).size(22.dp).background(Color(0xAA000000), RoundedCornerShape(11.dp)).clickable { onRemove(index) }, contentAlignment = Alignment.Center) {
            Text("✕", color = Color.Red, fontSize = 12.sp, fontWeight = FontWeight.Bold)
        }
    }
}

@Composable
fun ActionButtons(
    evidenceCount: Int,
    requiredPhotos: Int,
    isProcessingRedaction: Boolean,
    isResolving: Boolean,
    hasCameraPermission: Boolean,
    isSentry: Boolean,
    onCapturePhoto: () -> Unit,
    onRequestCameraPermission: () -> Unit,
    onSubmit: () -> Unit
) {
    val btnTextCapture = if (isSentry) "CAPTURE SCENE (${evidenceCount}/$requiredPhotos)" else "CAPTURE PHOTO (${evidenceCount}/$requiredPhotos)"
    val btnTextSubmit = if (isSentry) "SECURE SCENE & SUBMIT" else "RE-RUN DIAGNOSTICS & SUBMIT"

    if (evidenceCount < requiredPhotos) {
        Button(enabled = !isProcessingRedaction, onClick = { if (hasCameraPermission) onCapturePhoto() else onRequestCameraPermission() }, colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF4CAF50), disabledContainerColor = Color(0xFF1B3D20)), modifier = Modifier.fillMaxWidth().height(64.dp), shape = RoundedCornerShape(8.dp)) {
            if (isProcessingRedaction) CircularProgressIndicator(modifier = Modifier.size(20.dp), color = Color.White)
            else Text(btnTextCapture, color = Color.White, fontWeight = FontWeight.Black)
        }
    } else {
        Button(enabled = !isResolving && !isProcessingRedaction, onClick = onSubmit, colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF00BCD4), disabledContainerColor = Color(0xFF1E3538)), modifier = Modifier.fillMaxWidth().height(64.dp), shape = RoundedCornerShape(8.dp)) {
            if (isResolving) CircularProgressIndicator(modifier = Modifier.size(24.dp), color = Color.Black)
            else Text(btnTextSubmit, color = Color.Black, fontWeight = FontWeight.Black)
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