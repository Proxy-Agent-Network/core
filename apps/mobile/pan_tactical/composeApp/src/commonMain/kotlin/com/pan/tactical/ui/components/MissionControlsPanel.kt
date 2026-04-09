package com.pan.tactical.ui.components

import androidx.compose.animation.animateContentSize
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.key
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.pan.tactical.models.MissionData
import com.pan.tactical.ui.theme.PanColors

/**
 * Renders the expandable "EN ROUTE" tactical panel.
 * Gives the agent the ability to confirm arrival or swipe to abort.
 */
@Composable
fun MissionControlsPanel(
    activeMission: MissionData?,
    isExpanded: Boolean,
    onToggleExpand: () -> Unit,
    onArrivedAtScene: () -> Unit,
    onAbortRequested: () -> Unit,
    abortSliderKey: Int,
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier
            .fillMaxWidth()
            .animateContentSize(),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        // Expand/Collapse Toggle
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .clickable { onToggleExpand() }
                .padding(vertical = 12.dp),
            contentAlignment = Alignment.Center
        ) {
            Text(
                text = if (isExpanded) "▼ HIDE MISSION CONTROLS ▼" else "▲ SHOW MISSION CONTROLS ▲",
                color = PanColors.CyanAccent,
                fontSize = 12.sp,
                fontWeight = FontWeight.Bold,
                letterSpacing = 1.sp
            )
        }

        // Expanded Content
        if (isExpanded) {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(start = 16.dp, end = 16.dp, bottom = 16.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Text(
                    text = "ACTIVE MISSION: EN ROUTE",
                    color = PanColors.CyanAccent,
                    fontSize = 14.sp,
                    fontWeight = FontWeight.Black,
                    letterSpacing = 2.sp
                )

                Spacer(modifier = Modifier.height(8.dp))

                Text(
                    text = activeMission?.intersection ?: "Target Location",
                    color = Color.White,
                    fontSize = 20.sp,
                    fontWeight = FontWeight.Bold
                )

                Text(
                    text = "Diagnostic: ${activeMission?.errorCode}",
                    color = Color.LightGray,
                    fontSize = 14.sp
                )

                Spacer(modifier = Modifier.height(16.dp))

                Button(
                    onClick = onArrivedAtScene,
                    colors = ButtonDefaults.buttonColors(containerColor = PanColors.CyanAccent),
                    shape = RoundedCornerShape(8.dp),
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(64.dp)
                        .padding(bottom = 16.dp)
                ) {
                    Text(
                        text = "ARRIVED AT SCENE",
                        color = Color.Black,
                        fontSize = 20.sp,
                        fontWeight = FontWeight.Black,
                        letterSpacing = 1.sp
                    )
                }

                key(abortSliderKey) {
                    SwipeActionSlider(
                        text = "SWIPE TO ABORT >>",
                        trackColor = Color(0xFF2C2C2C),
                        thumbColor = PanColors.DangerRed,
                        // 🛡️ COMPILER FIX: Explicitly name the parameter instead of using a trailing lambda
                        onSwipeComplete = { onAbortRequested() }
                    )
                }
            }
        }
    }
}