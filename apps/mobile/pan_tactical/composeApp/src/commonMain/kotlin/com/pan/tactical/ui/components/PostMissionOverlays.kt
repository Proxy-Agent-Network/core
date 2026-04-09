package com.pan.tactical.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

@Composable
fun PostMissionOverlays(
    isUploadingProof: Boolean,
    capturedEvidence: List<ByteArray>, // 🟢 Updated to ByteArray
    missionState: String,
    lastPayoutAmount: Double,
    timeOnSceneMs: Long,
    totalResponseTimeMs: Long,
    lastTxHash: String,
    onReturnToPatrol: () -> Unit
) {
    if (isUploadingProof) {
        Box(
            modifier = Modifier.fillMaxSize().background(Color(0xCC000000)),
            contentAlignment = Alignment.Center
        ) {
            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                CircularProgressIndicator(color = Color(0xFF00BCD4))
                Spacer(modifier = Modifier.height(16.dp))
                Text("UPLOADING SECURE LEDGER PROOF...", color = Color(0xFF00BCD4), fontWeight = FontWeight.Bold)
            }
        }
    } else if (missionState == "COMPLETED") {
        Box(
            modifier = Modifier.fillMaxSize().background(Color(0xEE121212)).padding(24.dp),
            contentAlignment = Alignment.Center
        ) {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .background(Color(0xFF1E1E1E), RoundedCornerShape(12.dp))
                    .padding(24.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Text("MISSION ACCOMPLISHED", color = Color(0xFF4CAF50), fontSize = 24.sp, fontWeight = FontWeight.Black)
                Spacer(modifier = Modifier.height(16.dp))
                Text("ESCROW RELEASED:", color = Color.Gray, fontSize = 12.sp)

                // Format the double so it looks like cash
                val formattedPayout = lastPayoutAmount.toCurrency()
                Text(formattedPayout, color = Color.White, fontSize = 48.sp, fontWeight = FontWeight.Bold)

                Spacer(modifier = Modifier.height(24.dp))
                Button(
                    onClick = onReturnToPatrol,
                    colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF00BCD4)),
                    modifier = Modifier.fillMaxWidth().height(56.dp),
                    shape = RoundedCornerShape(8.dp)
                ) {
                    Text("RETURN TO PATROL", color = Color.Black, fontWeight = FontWeight.Black)
                }
            }
        }
    }
}