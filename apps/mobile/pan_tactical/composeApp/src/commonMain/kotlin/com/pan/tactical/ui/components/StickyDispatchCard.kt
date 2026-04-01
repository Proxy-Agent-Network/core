package com.pan.tactical.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.pan.tactical.models.MissionData
import com.pan.tactical.models.TaskRole
import com.pan.tactical.ui.theme.PanColors

@Composable
fun StickyDispatchCard(
    queuedMission: MissionData,
    modifier: Modifier = Modifier
) {
    // 🛡️ FIXED: Cross-platform safe currency formatting (Replaces JVM-only .format)
    val wholePart = queuedMission.bountyUsd.toInt()
    val fractionalPart = ((queuedMission.bountyUsd - wholePart) * 100).toInt()
    val formattedBounty = "$$wholePart.${fractionalPart.toString().padStart(2, '0')}"

    Box(
        modifier = modifier
            .fillMaxWidth()
            .padding(16.dp)
            .background(PanColors.CardBackgroundTransparent, shape = RoundedCornerShape(12.dp))
            .border(1.dp, PanColors.Green, shape = RoundedCornerShape(12.dp))
            .padding(16.dp)
    ) {
        Column {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Box(
                    modifier = Modifier
                        .background(PanColors.Green.copy(alpha = 0.2f), RoundedCornerShape(4.dp))
                        .padding(horizontal = 8.dp, vertical = 4.dp)
                ) {
                    Text(
                        text = "NEXT UP • ${queuedMission.role.name}",
                        color = PanColors.Green,
                        fontSize = 10.sp,
                        fontWeight = FontWeight.Black,
                        letterSpacing = 1.sp
                    )
                }

                Text(
                    text = formattedBounty,
                    color = Color.White,
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Bold
                )
            }

            Spacer(modifier = Modifier.height(8.dp))

            Text(
                text = queuedMission.intersection,
                color = Color.LightGray,
                fontSize = 14.sp,
                fontWeight = FontWeight.Medium
            )

            Text(
                // 🛡️ FIXED: Handle the new nullable errorCode from our API contract
                text = queuedMission.errorCode ?: "UNKNOWN FAULT",
                color = PanColors.WarningOrange,
                fontSize = 12.sp,
                fontWeight = FontWeight.Bold
            )
        }
    }
}

@Preview(showBackground = true, backgroundColor = 0xFF121212)
@Composable
fun StickyDispatchCardPreview() {
    StickyDispatchCard(
        queuedMission = MissionData(
            incidentId = "INC-999",
            taskId = "TSK-1024",
            // 🛡️ FIXED: Added required coordinates (No longer defaults to 0.0)
            lat = 33.415,
            lon = -111.831,
            intersection = "Mesa Dr & University",
            errorCode = "LIDAR_CRITICAL_FAULT",
            bountyUsd = 47.50,
            role = TaskRole.PRIMARY
        )
    )
}