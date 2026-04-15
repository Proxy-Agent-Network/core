package com.pan.tactical.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.pan.tactical.ui.toCurrency
import kotlin.math.round

@Composable
fun PostMissionOverlays(
    isUploadingProof: Boolean,
    capturedEvidence: List<ByteArray>,
    missionState: String,
    lastPayoutAmount: Double,
    timeOnSceneMs: Long,
    totalResponseTimeMs: Long,
    lastTxHash: String,
    isVeteran: Boolean = false, // 🟢 Defaults to false (25%) if not passed from Dashboard!
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

        // --- TIME CALCULATIONS ---
        val totalSecs = (totalResponseTimeMs / 1000).toInt()
        val totalMins = totalSecs / 60
        val remSecs = totalSecs % 60

        val sceneSecs = (timeOnSceneMs / 1000).toInt()
        val sceneMins = sceneSecs / 60
        val remSceneSecs = sceneSecs % 60

        val travelMs = (totalResponseTimeMs - timeOnSceneMs).coerceAtLeast(0)
        val travelSecs = (travelMs / 1000).toInt()
        val travelMins = travelSecs / 60
        val remTravelSecs = travelSecs % 60
        // -------------------------

        // Audit Category Color Shift
        val tacticalColor = when {
            totalSecs < 720 -> Color(0xFF4CAF50) // < 12 mins (Qualified Green)
            totalSecs < 1200 -> Color(0xFFFF9800) // 12 - 20 mins (Warning Orange)
            else -> Color(0xFFF44336) // >= 20 mins (Critical Red)
        }

        // --- FEE TRANSPARENCY MATH (Reverse Calculation with strict rounding) ---
        val feePercentage = if (isVeteran) 0.15 else 0.25
        val feePercentText = if (isVeteran) "15%" else "25%"

        // Reconstruct the gross bounty from the net payout, rounded to 2 decimal places
        val grossBounty = round((lastPayoutAmount / (1.0 - feePercentage)) * 100) / 100.0
        val feeAmount = round((grossBounty - lastPayoutAmount) * 100) / 100.0

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
                Text("MISSION ACCOMPLISHED", color = Color(0xFF4CAF50), fontSize = 22.sp, fontWeight = FontWeight.Black)
                Spacer(modifier = Modifier.height(16.dp))

                Text("TAKE HOME PAYOUT:", color = Color.Gray, fontSize = 12.sp, fontWeight = FontWeight.Bold)

                val formattedPayout = lastPayoutAmount.toCurrency()
                Text(formattedPayout, color = Color.White, fontSize = 56.sp, fontWeight = FontWeight.Bold)

                Spacer(modifier = Modifier.height(4.dp))

                Text(
                    text = "${grossBounty.toCurrency()} - ${feeAmount.toCurrency()} ($feePercentText) network fee",
                    color = Color(0xFFAAAAAA),
                    fontSize = 14.sp,
                    fontWeight = FontWeight.Medium
                )

                Spacer(modifier = Modifier.height(24.dp))

                Column(
                    modifier = Modifier.fillMaxWidth().background(Color(0xFF2A2A2A), RoundedCornerShape(8.dp)).padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                        Text("TRAVEL TIME", color = Color.Gray, fontSize = 12.sp, fontWeight = FontWeight.Bold)
                        Text("${travelMins}m ${remTravelSecs}s", color = Color.White, fontSize = 12.sp, fontWeight = FontWeight.Bold)
                    }
                    Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                        Text("TIME ON SCENE", color = Color.Gray, fontSize = 12.sp, fontWeight = FontWeight.Bold)
                        Text("${sceneMins}m ${remSceneSecs}s", color = Color.White, fontSize = 12.sp, fontWeight = FontWeight.Bold)
                    }
                    HorizontalDivider(color = Color.DarkGray)

                    Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                        Text("TOTAL MISSION TIME", color = tacticalColor, fontSize = 14.sp, fontWeight = FontWeight.Black)
                        Text("${totalMins}m ${remSecs}s", color = tacticalColor, fontSize = 14.sp, fontWeight = FontWeight.Black)
                    }
                }

                Spacer(modifier = Modifier.height(32.dp))

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