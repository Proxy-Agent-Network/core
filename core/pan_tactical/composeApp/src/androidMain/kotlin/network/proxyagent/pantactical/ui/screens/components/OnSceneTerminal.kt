package network.proxyagent.pantactical.ui.screens.components

import android.graphics.Bitmap
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.foundation.Image
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
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import network.proxyagent.pantactical.models.MissionData

@Composable
fun OnSceneTerminal(
    activeMission: MissionData?,
    capturedEvidence: List<Bitmap>,
    hasCameraPermission: Boolean,
    onRequestCameraPermission: () -> Unit,
    onCapturePhoto: () -> Unit,
    onRemovePhoto: (Int) -> Unit, // --- NEW: Callback for removing a photo ---
    onSubmitEvidence: () -> Unit
) {
    val coroutineScope = rememberCoroutineScope()
    var terminalLogs by remember { mutableStateOf(listOf("Establishing local UWB connection to AV...", "Connection secured.", "Awaiting physical repair and diagnostic re-run...")) }
    var isResolving by remember { mutableStateOf(false) }
    var isResolved by remember { mutableStateOf(false) }
    val requiredPhotos = 2

    LaunchedEffect(activeMission) {
        terminalLogs = listOf("Connection secured.", "Awaiting repair...")
        isResolving = false; isResolved = false
    }

    Column(modifier = Modifier.fillMaxWidth().padding(16.dp).background(Color(0xFF0D1117)).padding(16.dp), horizontalAlignment = Alignment.CenterHorizontally) {
        Text("📟 AV DIAGNOSTIC TERMINAL", color = Color(0xFF00FF00), fontSize = 16.sp, fontWeight = FontWeight.Black, letterSpacing = 1.sp); Spacer(modifier = Modifier.height(12.dp))
        Box(modifier = Modifier.fillMaxWidth().height(140.dp).background(Color.Black, RoundedCornerShape(8.dp)).border(1.dp, Color(0xFF333333), RoundedCornerShape(8.dp)).padding(12.dp)) {
            Column(modifier = Modifier.verticalScroll(rememberScrollState())) {
                terminalLogs.forEach { log -> Text("> $log", color = Color(0xFF00FF00), fontFamily = FontFamily.Monospace, fontSize = 12.sp); Spacer(modifier = Modifier.height(4.dp)) }
            }
        }
        Spacer(modifier = Modifier.height(16.dp))

        if (!isResolved) {
            Button(enabled = !isResolving, onClick = { isResolving = true; coroutineScope.launch { terminalLogs = terminalLogs + "Pinging AV CAN bus..."; delay(1000); terminalLogs = terminalLogs + "Diagnostic Trouble Codes (DTC) cleared."; delay(800); isResolving = false; isResolved = true } }, colors = ButtonDefaults.buttonColors(containerColor = Color(0xFFD32F2F), disabledContainerColor = Color(0xFF555555)), modifier = Modifier.fillMaxWidth().height(64.dp), shape = RoundedCornerShape(8.dp)) { if (isResolving) CircularProgressIndicator(modifier = Modifier.size(24.dp), color = Color.White) else Text("RE-RUN AV DIAGNOSTICS", color = Color.White, fontWeight = FontWeight.Black) }
        } else {
            if (capturedEvidence.isNotEmpty()) {
                Row(modifier = Modifier.fillMaxWidth().horizontalScroll(rememberScrollState()).padding(bottom = 16.dp), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    capturedEvidence.forEachIndexed { index, bmp ->
                        Box(modifier = Modifier.size(80.dp).border(2.dp, Color(0xFF00BCD4), RoundedCornerShape(8.dp)).clip(RoundedCornerShape(8.dp))) {
                            Image(bitmap = bmp.asImageBitmap(), contentDescription = "Evidence", modifier = Modifier.fillMaxSize(), contentScale = ContentScale.Crop)

                            // Bottom Label (BEFORE/AFTER)
                            Box(modifier = Modifier.align(Alignment.BottomStart).background(Color(0xAA000000)).padding(4.dp)) {
                                Text(if(index == 0) "BEFORE" else "AFTER", color = Color.White, fontSize = 8.sp, fontWeight = FontWeight.Bold)
                            }

                            // --- NEW: Remove Photo Button ---
                            Box(
                                modifier = Modifier
                                    .align(Alignment.TopEnd)
                                    .padding(4.dp)
                                    .size(22.dp)
                                    .background(Color(0xAA000000), RoundedCornerShape(11.dp))
                                    .border(1.dp, Color(0xFFF44336), RoundedCornerShape(11.dp))
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

                Button(
                    onClick = { if (hasCameraPermission) onCapturePhoto() else onRequestCameraPermission() },
                    colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF4CAF50), disabledContainerColor = Color(0xFF555555)),
                    modifier = Modifier.fillMaxWidth().height(64.dp), shape = RoundedCornerShape(8.dp)
                ) {
                    Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        Text("📷", fontSize = 18.sp)
                        Text(if (capturedEvidence.size < requiredPhotos) "CAPTURE '$photoType' PHOTO (${capturedEvidence.size}/$requiredPhotos)" else "CAPTURE $photoType PHOTO", color = Color.White, fontSize = 13.sp, fontWeight = FontWeight.Black)
                    }
                }

                AnimatedVisibility(visible = capturedEvidence.size >= requiredPhotos) {
                    Button(
                        onClick = onSubmitEvidence,
                        colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF00BCD4)),
                        modifier = Modifier.fillMaxWidth().height(64.dp), shape = RoundedCornerShape(8.dp)
                    ) {
                        Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                            Text("📤", fontSize = 18.sp)
                            Text("SUBMIT ${capturedEvidence.size}-PART EVIDENCE ARRAY", color = Color.Black, fontSize = 14.sp, fontWeight = FontWeight.Black)
                        }
                    }
                }
            }
        }
    }
}