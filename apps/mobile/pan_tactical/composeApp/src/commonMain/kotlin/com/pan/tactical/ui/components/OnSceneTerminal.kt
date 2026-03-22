package com.pan.tactical.ui.components

// --- QUARANTINED ANDROID IMPORTS ---
// import android.graphics.Bitmap
// import androidx.compose.foundation.Image
// import androidx.compose.ui.graphics.asImageBitmap
// -----------------------------------

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import com.pan.tactical.models.MissionData

@Composable
fun OnSceneTerminal(
    activeMission: MissionData?,
    capturedEvidence: List<Any>, 
    hasCameraPermission: Boolean,
    onRequestCameraPermission: () -> Unit,
    onCapturePhoto: () -> Unit,
    onRemovePhoto: (Int) -> Unit, 
    onSubmitEvidence: () -> Unit,
    onVerifyIdentity: () -> Unit = {} // 🟢 NEW: Hook for Android BiometricPrompt
) {
    val coroutineScope = rememberCoroutineScope()
    var terminalLogs by remember { mutableStateOf(listOf("Establishing local UWB connection to AV...", "Connection secured.")) }
    var isResolving by remember { mutableStateOf(false) }
    val requiredPhotos = 2

    // 🟢 NEW: Biometric State Management
    var requiresBiometrics by remember { mutableStateOf(false) }
    var biometricsPassed by remember { mutableStateOf(true) }

    LaunchedEffect(activeMission) {
        terminalLogs = listOf("Connection secured.", "Awaiting visual evidence package...")
        isResolving = false
        
        // Always require biometrics for high-liability faults, 20% chance for others
        val isHighTier = activeMission?.errorCode == "manual_override" || activeMission?.errorCode == "scene_securement"
        requiresBiometrics = Math.random() < 0.20 || isHighTier
        biometricsPassed = !requiresBiometrics
        
        if (requiresBiometrics) {
            terminalLogs = terminalLogs + "WARNING: Identity verification required for this asset."
        }
    }

    Column(modifier = Modifier.fillMaxWidth().padding(16.dp).background(Color(0xFF0D1117)).padding(16.dp), horizontalAlignment = Alignment.CenterHorizontally) {
        Text("📟 AV DIAGNOSTIC TERMINAL", color = Color(0xFF00FF00), fontSize = 16.sp, fontWeight = FontWeight.Black, letterSpacing = 1.sp); Spacer(modifier = Modifier.height(12.dp))
        
        Box(modifier = Modifier.fillMaxWidth().height(140.dp).background(Color.Black, RoundedCornerShape(8.dp)).border(1.dp, Color(0xFF333333), RoundedCornerShape(8.dp)).padding(12.dp)) {
            Column(modifier = Modifier.verticalScroll(rememberScrollState())) {
                terminalLogs.forEach { log -> Text("> $log", color = Color(0xFF00FF00), fontFamily = FontFamily.Monospace, fontSize = 12.sp); Spacer(modifier = Modifier.height(4.dp)) }
            }
        }
        Spacer(modifier = Modifier.height(16.dp))

        // 🟢 1. THE BIOMETRIC GATE
        if (!biometricsPassed) {
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .border(2.dp, Color.Red, RoundedCornerShape(8.dp))
                    .background(Color(0xFF2A0000), RoundedCornerShape(8.dp))
                    .padding(16.dp)
            ) {
                Column(horizontalAlignment = Alignment.CenterHorizontally, modifier = Modifier.fillMaxWidth()) {
                    Text("⚠️ RANDOM SECURITY CHECK ⚠️", color = Color.Red, fontWeight = FontWeight.Bold, fontSize = 16.sp)
                    Spacer(modifier = Modifier.height(4.dp))
                    Text("Identity verification required to proceed.", color = Color.LightGray, fontSize = 12.sp)
                    Spacer(modifier = Modifier.height(12.dp))
                    Button(
                        onClick = {
                            onVerifyIdentity()
                            biometricsPassed = true // For prototype, clicking auto-passes
                            terminalLogs = terminalLogs + "Identity verified via Biometrics."
                        },
                        colors = ButtonDefaults.buttonColors(containerColor = Color.Red)
                    ) {
                        Text("VERIFY IDENTITY", color = Color.White, fontWeight = FontWeight.Black)
                    }
                }
            }
        } 
        // 🟢 2. THE PHOTO & DIAGNOSTIC FLOW (Unlocked after biometrics)
        else {
            if (capturedEvidence.isNotEmpty()) {
                Row(modifier = Modifier.fillMaxWidth().horizontalScroll(rememberScrollState()).padding(bottom = 16.dp), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    capturedEvidence.forEachIndexed { index, bmp ->
                        Box(modifier = Modifier.size(80.dp).border(2.dp, Color(0xFF00BCD4), RoundedCornerShape(8.dp)).clip(RoundedCornerShape(8.dp))) {

                            // --- QUARANTINED ANDROID IMAGE RENDERER ---
                            // Image(bitmap = bmp.asImageBitmap(), contentDescription = "Evidence", modifier = Modifier.fillMaxSize(), contentScale = ContentScale.Crop)

                            Box(modifier = Modifier.align(Alignment.BottomStart).background(Color(0xAA000000)).padding(4.dp)) {
                                Text(if(index == 0) "BEFORE" else "AFTER", color = Color.White, fontSize = 8.sp, fontWeight = FontWeight.Bold)
                            }

                            Box(
                                modifier = Modifier.align(Alignment.TopEnd).padding(4.dp).size(22.dp).background(Color(0xAA000000), RoundedCornerShape(11.dp)).border(1.dp, Color(0xFFF44336), RoundedCornerShape(11.dp))
                                    .clickable { onRemovePhoto(index) },
                                contentAlignment = Alignment.Center
                            ) {
                                Text("✕", color = Color(0xFFF44336), fontSize = 12.sp, fontWeight = FontWeight.Bold)
                            }
                        }
                    }
                }
            }

            Column(verticalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.fillMaxWidth()) {
                val photoType = when (capturedEvidence.size) {
                    0 -> "BEFORE"
                    1 -> "AFTER"
                    else -> "ADDITIONAL"
                }

                // Show Camera Button if we need more photos
                if (capturedEvidence.size < requiredPhotos) {
                    Button(
                        onClick = { if (hasCameraPermission) onCapturePhoto() else onRequestCameraPermission() },
                        colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF4CAF50)),
                        modifier = Modifier.fillMaxWidth().height(64.dp), shape = RoundedCornerShape(8.dp)
                    ) {
                        Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                            Text("📷", fontSize = 18.sp)
                            Text("CAPTURE '$photoType' PHOTO (${capturedEvidence.size}/$requiredPhotos)", color = Color.White, fontSize = 13.sp, fontWeight = FontWeight.Black)
                        }
                    }
                } 
                // Show Diagnostics/Submit button once photos are complete
                else {
                    Button(
                        enabled = !isResolving,
                        onClick = { 
                            isResolving = true 
                            coroutineScope.launch { 
                                terminalLogs = terminalLogs + "Pinging AV CAN bus..."
                                delay(1000)
                                terminalLogs = terminalLogs + "Diagnostic Trouble Codes (DTC) cleared."
                                delay(800)
                                terminalLogs = terminalLogs + "Evidence package encrypted and queued."
                                delay(500)
                                isResolving = false
                                onSubmitEvidence() 
                            } 
                        }, 
                        colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF00BCD4), disabledContainerColor = Color(0xFF333333)), 
                        modifier = Modifier.fillMaxWidth().height(64.dp), 
                        shape = RoundedCornerShape(8.dp)
                    ) { 
                        if (isResolving) {
                            CircularProgressIndicator(modifier = Modifier.size(24.dp), color = Color.Black) 
                        } else {
                            Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                                Text("⚙️", fontSize = 18.sp)
                                Text("RE-RUN DIAGNOSTICS & SUBMIT", color = Color.Black, fontSize = 14.sp, fontWeight = FontWeight.Black)
                            }
                        }
                    }
                }
            }
        }
    }
}