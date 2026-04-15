package com.pan.tactical.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.pan.tactical.models.MissionData

// KMP-safe currency formatter since String.format is platform-specific
private fun formatCurrency(value: Double): String {
    val wholePart = value.toInt()
    val fractionalPart = ((value - wholePart) * 100).toInt()
    return "$wholePart.${fractionalPart.toString().padStart(2, '0')}"
}

@Composable
fun MissionAlertOverlay(
    activeMission: MissionData?,
    countdownProgress: Float,
    flashAlpha: Float, // Retained for compatibility with the view model
    isVeteran: Boolean = false, // 🟢 NEW: Drives the 15% vs 25% math
    distanceMiles: Double = 0.0, // 🟢 NEW: Dynamically render distance
    onAccept: () -> Unit,
    onDecline: () -> Unit
) {
    val isSentry = activeMission?.role.toString().uppercase() == "SENTRY"
    val alertTitle = if (isSentry) "SENTRY DISPATCH" else "MISSION ALERT"

    // Format the fault code to look clean (e.g., "scene_securement" -> "Scene Securement")
    val displayFault = activeMission?.errorCode?.replace("_", " ")?.split(" ")?.joinToString(" ") {
        it.replaceFirstChar { char -> char.uppercase() }
    } ?: "Unknown Alert"

    // --- FEE TRANSPARENCY MATH ---
    val grossBounty = activeMission?.bountyUsd ?: 0.0
    val feePercentage = if (isVeteran) 0.15 else 0.25
    val feeAmount = grossBounty * feePercentage
    val netPayout = grossBounty - feeAmount
    val feePercentText = if (isVeteran) "15%" else "25%"

    // The mockup floats at the bottom over the map
    Box(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        contentAlignment = Alignment.BottomCenter
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .background(Color(0xFA1A1D21), RoundedCornerShape(16.dp)) // Deep dark gray from mockup
                .border(1.dp, Color(0xFF333333), RoundedCornerShape(16.dp))
                .padding(20.dp)
        ) {

            // --- HEADER ---
            Row(verticalAlignment = Alignment.CenterVertically) {
                // Swapped missing Material Icon for a clean native emoji
                Text(
                    text = "⚠️",
                    fontSize = 28.sp
                )
                Spacer(modifier = Modifier.width(12.dp))
                Column {
                    Text(
                        text = alertTitle,
                        color = Color.White,
                        fontSize = 22.sp,
                        fontWeight = FontWeight.Black,
                        letterSpacing = 1.sp
                    )
                    Text(
                        text = displayFault,
                        color = Color(0xFF00BCD4), // Cyan accent
                        fontSize = 16.sp,
                        fontWeight = FontWeight.Medium
                    )
                }
            }

            Spacer(modifier = Modifier.height(20.dp))

            // --- BOUNTY & FEE BREAKDOWN ---
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .background(Color(0xFF121212), RoundedCornerShape(12.dp))
                    .padding(vertical = 20.dp),
                contentAlignment = Alignment.Center
            ) {
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Text(
                        text = "$${formatCurrency(netPayout)}",
                        color = Color(0xFF4CAF50), // Green payout
                        fontSize = 56.sp,
                        fontWeight = FontWeight.Black
                    )
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = "$${formatCurrency(grossBounty)} - $${formatCurrency(feeAmount)} ($feePercentText) fee",
                        color = Color(0xFFAAAAAA),
                        fontSize = 14.sp,
                        fontWeight = FontWeight.Medium
                    )
                }
            }

            Spacer(modifier = Modifier.height(20.dp))

            // --- LOCATION INFO ---
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(
                    text = "📍",
                    fontSize = 20.sp
                )
                Spacer(modifier = Modifier.width(12.dp))
                Column {
                    Text("Target Location", color = Color.Gray, fontSize = 12.sp)
                    Text(
                        text = activeMission?.intersection ?: "Calculating Location...",
                        color = Color.White,
                        fontSize = 15.sp,
                        fontWeight = FontWeight.Bold
                    )
                }
            }

            Spacer(modifier = Modifier.height(16.dp))

            // --- DISTANCE INFO ---
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(
                    text = "🚗",
                    fontSize = 20.sp
                )
                Spacer(modifier = Modifier.width(12.dp))
                val distanceText = if (distanceMiles > 0) "${formatCurrency(distanceMiles)} Miles" else "Calculating..."
                Text(
                    text = distanceText,
                    color = Color.White,
                    fontSize = 15.sp,
                    fontWeight = FontWeight.Bold
                )
            }

            Spacer(modifier = Modifier.height(24.dp))

            // --- SLA PROGRESS BAR ---
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(4.dp)
                    .background(Color(0xFF333333), RoundedCornerShape(2.dp)),
                contentAlignment = Alignment.CenterStart
            ) {
                Box(
                    modifier = Modifier
                        .fillMaxHeight()
                        .fillMaxWidth(countdownProgress)
                        .background(Color(0xFF00BCD4), RoundedCornerShape(2.dp))
                )
            }

            Spacer(modifier = Modifier.height(20.dp))

            // --- ACTION BUTTONS ---
            Row(
                horizontalArrangement = Arrangement.spacedBy(16.dp),
                modifier = Modifier.fillMaxWidth()
            ) {
                Button(
                    onClick = onDecline,
                    colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF4A4A4A)),
                    modifier = Modifier.weight(1f).height(60.dp),
                    shape = RoundedCornerShape(12.dp)
                ) {
                    Text("DECLINE", color = Color.White, fontWeight = FontWeight.Bold, fontSize = 18.sp)
                }

                Button(
                    onClick = onAccept,
                    colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF66BB6A)),
                    modifier = Modifier.weight(1f).height(60.dp),
                    shape = RoundedCornerShape(12.dp)
                ) {
                    Text("ACCEPT", color = Color.Black, fontWeight = FontWeight.Black, fontSize = 18.sp)
                }
            }
        }
    }
}