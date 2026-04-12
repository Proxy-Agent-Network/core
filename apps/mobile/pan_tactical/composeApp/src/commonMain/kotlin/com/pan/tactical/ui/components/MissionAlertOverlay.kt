package com.pan.tactical.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.pan.tactical.models.MissionData
import com.pan.tactical.ui.theme.PanColors

@Composable
fun MissionAlertOverlay(
    activeMission: MissionData?,
    countdownProgress: Float,
    flashAlpha: Float,
    onAccept: () -> Unit,
    onDecline: () -> Unit
) {
    // 🟢 FIX: Safely convert the role (which is likely an Enum) into a String first
    val isSentry = activeMission?.role.toString().uppercase() == "SENTRY"

    val alertTitle = if (isSentry) "SENTRY DISPATCH" else "RESCUE DISPATCH"
    val titleColor = if (isSentry) PanColors.WarningOrange else Color(0xFFF44336)
    val flashColor = if (isSentry) PanColors.WarningOrange else PanColors.QualifiedGreen

    Box(
        modifier = Modifier.fillMaxSize().background(Color(0xEE121212)).padding(24.dp),
        contentAlignment = Alignment.Center
    ) {
        Box(modifier = Modifier.fillMaxSize().background(flashColor.copy(alpha = flashAlpha)))

        Column(
            modifier = Modifier.fillMaxWidth().verticalScroll(rememberScrollState()),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(10.dp)
        ) {

            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.Center
            ) {
                Box(modifier = Modifier.size(32.dp).background(titleColor, CircleShape), contentAlignment = Alignment.Center) {
                    Text("!", color = Color.White, fontWeight = FontWeight.Black, fontSize = 20.sp)
                }
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    text = alertTitle,
                    color = titleColor,
                    fontSize = 24.sp,
                    fontWeight = FontWeight.Black,
                    letterSpacing = 1.sp,
                    textAlign = TextAlign.Center
                )
                Spacer(modifier = Modifier.width(8.dp))
                Box(modifier = Modifier.size(32.dp).background(titleColor, CircleShape), contentAlignment = Alignment.Center) {
                    Text("!", color = Color.White, fontWeight = FontWeight.Black, fontSize = 20.sp)
                }
            }

            Box(
                modifier = Modifier.fillMaxWidth().height(12.dp).background(PanColors.SurfaceMid, shape = RoundedCornerShape(8.dp)),
                contentAlignment = Alignment.CenterStart
            ) {
                Box(modifier = Modifier.fillMaxHeight().fillMaxWidth(countdownProgress).background(flashColor, shape = RoundedCornerShape(8.dp)))
            }

            val rawBounty = activeMission?.bountyUsd ?: 0.0
            val netPayout = rawBounty * 0.90
            val wholePart = netPayout.toInt()
            val fractionalPart = ((netPayout - wholePart) * 100).toInt()
            val formattedBounty = "$$wholePart.${fractionalPart.toString().padStart(2, '0')}"

            Text("GUARANTEED NET PAYOUT", color = Color.LightGray, fontSize = 12.sp, fontWeight = FontWeight.Bold, letterSpacing = 1.sp)
            Text(formattedBounty, color = PanColors.QualifiedGreen, fontSize = 48.sp, fontWeight = FontWeight.Black)

            Text(activeMission?.intersection ?: "Broadway / Dobson", color = PanColors.WarningOrange, fontSize = 20.sp, fontWeight = FontWeight.Medium, textAlign = TextAlign.Center)

            val displayFault = activeMission?.errorCode?.replace("_", " ")?.uppercase() ?: "UNKNOWN FAULT"
            Text(displayFault, color = Color.Red, fontSize = 18.sp, fontWeight = FontWeight.Bold, textAlign = TextAlign.Center)

            Spacer(modifier = Modifier.height(8.dp))
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .background(PanColors.SurfaceMid, shape = RoundedCornerShape(8.dp))
                    .border(2.dp, PanColors.CyanAccent, shape = RoundedCornerShape(8.dp))
                    .padding(vertical = 16.dp),
                contentAlignment = Alignment.Center
            ) {
                Text(
                    text = "DISTANCE: 2.5 MILES",
                    color = PanColors.CyanAccent,
                    fontSize = 22.sp,
                    fontWeight = FontWeight.ExtraBold,
                    letterSpacing = 1.sp
                )
            }
            Spacer(modifier = Modifier.height(8.dp))

            Row(horizontalArrangement = Arrangement.spacedBy(16.dp), modifier = Modifier.fillMaxWidth()) {
                Button(
                    onClick = onDecline,
                    colors = ButtonDefaults.buttonColors(containerColor = PanColors.SurfaceLight),
                    modifier = Modifier.weight(1f).height(64.dp),
                    shape = RoundedCornerShape(12.dp)
                ) {
                    Text("DECLINE", color = Color.White)
                }

                Button(
                    onClick = onAccept,
                    colors = ButtonDefaults.buttonColors(containerColor = PanColors.QualifiedGreen),
                    modifier = Modifier.weight(1f).height(64.dp),
                    shape = RoundedCornerShape(12.dp)
                ) {
                    Text("ACCEPT", color = Color.White, fontWeight = FontWeight.Black)
                }
            }
        }
    }
}