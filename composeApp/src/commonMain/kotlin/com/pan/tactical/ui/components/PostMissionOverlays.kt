package com.pan.tactical.ui.components

import androidx.compose.animation.*
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
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

@Composable
fun PostMissionOverlays(
    isUploadingProof: Boolean,
    capturedEvidence: List<Any>,
    missionState: String,
    lastPayoutAmount: Double,
    timeOnSceneMs: Long,
    totalResponseTimeMs: Long,
    lastTxHash: String,
    onReturnToPatrol: () -> Unit
) {
    AnimatedVisibility(visible = isUploadingProof, enter = fadeIn(), exit = fadeOut(), modifier = Modifier.fillMaxSize()) {
        Box(modifier = Modifier.fillMaxSize().background(Color(0xEE000000)).padding(24.dp), contentAlignment = Alignment.Center) {
            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.horizontalScroll(rememberScrollState())) {
                    capturedEvidence.forEach { bmp ->
                        Box(modifier = Modifier.size(120.dp).border(2.dp, Color(0xFF00BCD4), RoundedCornerShape(8.dp)).clip(RoundedCornerShape(8.dp))) {
                            //Image(bitmap = bmp.asImageBitmap(), contentDescription = "Proof", modifier = Modifier.fillMaxSize(), contentScale = ContentScale.Crop)
                        }
                    }
                }
                Spacer(modifier = Modifier.height(24.dp))
                CircularProgressIndicator(color = Color(0xFF00BCD4))
                Spacer(modifier = Modifier.height(16.dp))
                Text("CRYPTOGRAPHIC WATERMARKING...", color = Color(0xFF00BCD4), fontWeight = FontWeight.Black, letterSpacing = 2.sp)
                Text("UPLOADING ${capturedEvidence.size}-PART EVIDENCE ARRAY", color = Color.Gray, fontSize = 12.sp)
            }
        }
    }

    AnimatedVisibility(visible = missionState == "COMPLETED", enter = slideInVertically(initialOffsetY = { it }) + fadeIn(), exit = slideOutVertically(targetOffsetY = { it }) + fadeOut(), modifier = Modifier.fillMaxSize()) {
        Box(modifier = Modifier.fillMaxSize().background(Color(0xEE121212)).padding(24.dp), contentAlignment = Alignment.Center) {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .background(Color(0xFF1E1E1E), RoundedCornerShape(12.dp))
                    .border(2.dp, Color(0xFF4CAF50), RoundedCornerShape(12.dp))
                    .padding(24.dp)
                    .verticalScroll(rememberScrollState()),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {

                // --- THE FIX: Swapped emojis for safe text characters and added CircleShape ---
                Box(modifier = Modifier.fillMaxWidth()) {
                    Box(modifier = Modifier.size(64.dp).background(Color(0xFF4CAF50).copy(alpha = 0.2f), CircleShape).align(Alignment.Center), contentAlignment = Alignment.Center) {
                        Text("✓", color = Color(0xFF4CAF50), fontSize = 32.sp, fontWeight = FontWeight.Black)
                    }

                    Box(
                        modifier = Modifier
                            .size(32.dp)
                            .background(Color(0xFF333333), CircleShape)
                            .align(Alignment.TopEnd)
                            .clickable { onReturnToPatrol() },
                        contentAlignment = Alignment.Center
                    ) {
                        Text("X", color = Color.White, fontSize = 14.sp, fontWeight = FontWeight.Bold)
                    }
                }

                Text("AV RE-ENGAGED", color = Color.White, fontSize = 24.sp, fontWeight = FontWeight.Black, letterSpacing = 2.sp)
                Text("Autonomous systems online. Incident resolved.", color = Color.Gray, fontSize = 12.sp, textAlign = TextAlign.Center)

                Text("FUNDS SECURED", color = Color(0xFF4CAF50), fontSize = 10.sp, fontWeight = FontWeight.Bold, letterSpacing = 2.sp)
                val dollars = lastPayoutAmount.toInt()
                val cents = ((lastPayoutAmount * 100).toInt() % 100).toString().padStart(2, '0')
                Text("+$${dollars}.${cents}", color = Color(0xFF4CAF50), fontSize = 48.sp, fontWeight = FontWeight.Black)

                Spacer(modifier = Modifier.height(8.dp))

                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                    Text("TOTAL RESPONSE TIME", color = Color.Gray, fontSize = 10.sp, fontWeight = FontWeight.Bold)
                    val trtMinutes = (totalResponseTimeMs / 1000) / 60
                    val trtSeconds = (totalResponseTimeMs / 1000) % 60
                    val trtStr = "${trtMinutes.toString().padStart(2, '0')}m ${trtSeconds.toString().padStart(2, '0')}s"
                    Text(trtStr, color = Color.White, fontSize = 14.sp, fontFamily = FontFamily.Monospace)
                }

                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                    Text("TIME ON SCENE", color = Color.Gray, fontSize = 10.sp, fontWeight = FontWeight.Bold)
                    val minutes = (timeOnSceneMs / 1000) / 60
                    val seconds = (timeOnSceneMs / 1000) % 60
                    val timeStr = "${minutes.toString().padStart(2, '0')}m ${seconds.toString().padStart(2, '0')}s"
                    Text(timeStr, color = Color.White, fontSize = 14.sp, fontFamily = FontFamily.Monospace)
                }

                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                    Text("CRYPTOGRAPHIC HASH", color = Color.Gray, fontSize = 10.sp, fontWeight = FontWeight.Bold)
                    Text(lastTxHash, color = Color(0xFF00BCD4), fontSize = 10.sp, fontFamily = FontFamily.Monospace)
                }

                Spacer(modifier = Modifier.height(16.dp))

                Button(
                    onClick = onReturnToPatrol,
                    colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF4CAF50)),
                    modifier = Modifier.fillMaxWidth().height(56.dp), shape = RoundedCornerShape(8.dp)
                ) { Text("RETURN TO PATROL", color = Color.White, fontWeight = FontWeight.Black, letterSpacing = 1.sp) }
            }
        }
    }
}