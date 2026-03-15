package com.pan.tactical.ui.components

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.foundation.ExperimentalFoundationApi
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.combinedClickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Slider
import androidx.compose.material3.SliderDefaults
import androidx.compose.material3.Switch
import androidx.compose.material3.SwitchDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.rotate
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.pan.tactical.models.AgentCapability
import kotlin.math.roundToInt

@OptIn(ExperimentalFoundationApi::class)
@Composable
fun CapabilityCard(
    cap: AgentCapability,
    agentCapabilities: List<AgentCapability>,
    onUpdate: (List<AgentCapability>) -> Unit
) {
    val originalIndex = agentCapabilities.indexOfFirst { it.id == cap.id }
    var isDetailsExpanded by remember { mutableStateOf(false) }

    val rotationAngle by animateFloatAsState(
        targetValue = if (isDetailsExpanded) 180f else 0f,
        label = "arrow_rotation"
    )

    Column(
        modifier = Modifier
            .fillMaxWidth()
            .background(if (!cap.isQualified) Color(0xFF121212) else if (cap.isEnabled) Color(0xFF4CAF50).copy(alpha = 0.1f) else Color(0xFF2A2A2A), RoundedCornerShape(8.dp))
            .border(1.dp, if (!cap.isQualified) Color(0xFF2A2A2A) else if (cap.isEnabled) Color(0xFF4CAF50) else Color(0xFF444444), RoundedCornerShape(8.dp))
            .clip(RoundedCornerShape(8.dp))
            .combinedClickable(
                onLongClick = {
                    val n = agentCapabilities.toMutableList()
                    n[originalIndex] = cap.copy(isPinned = !cap.isPinned)
                    onUpdate(n)
                },
                onClick = { isDetailsExpanded = !isDetailsExpanded }
            )
            .padding(12.dp)
    ) {
        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.CenterVertically) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                if (cap.isPinned) Text("📌 ", fontSize = 14.sp)
                if (!cap.isQualified) Text("🔒 ", fontSize = 14.sp)
                Text(cap.title, color = if (!cap.isQualified) Color.DarkGray else Color.White, fontSize = 14.sp, fontWeight = FontWeight.Bold)

                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    text = "▼",
                    color = Color.Gray,
                    fontSize = 12.sp,
                    modifier = Modifier.rotate(rotationAngle)
                )
            }
            if (cap.isQualified) {
                Switch(checked = cap.isEnabled, onCheckedChange = { val n = agentCapabilities.toMutableList(); n[originalIndex] = cap.copy(isEnabled = it); onUpdate(n) }, colors = SwitchDefaults.colors(checkedTrackColor = Color(0xFF4CAF50)))
            }
        }

        AnimatedVisibility(visible = isDetailsExpanded) {
            Column(modifier = Modifier.padding(top = 8.dp)) {
                Text(cap.description, color = Color.LightGray, fontSize = 12.sp, lineHeight = 16.sp)
                if (!cap.isQualified && cap.requiredTraining != null) {
                    Spacer(modifier = Modifier.height(4.dp))
                    Text("⚠️ ${cap.requiredTraining}", color = Color(0xFFFF9800), fontSize = 10.sp, fontWeight = FontWeight.Bold)
                } else if (cap.isQualified && cap.requiredTraining != null) {
                    Spacer(modifier = Modifier.height(4.dp))
                    Text("🛡️ Authorized: ${cap.requiredTraining}", color = Color(0xFF4CAF50), fontSize = 10.sp, fontWeight = FontWeight.Bold)
                }
            }
        }

        AnimatedVisibility(visible = cap.isEnabled && cap.isQualified) {
            Column(modifier = Modifier.fillMaxWidth().padding(top = 12.dp)) {
                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                    Text("YOUR MINIMUM BID", color = Color(0xFF00BCD4), fontSize = 10.sp, fontWeight = FontWeight.Bold, letterSpacing = 1.sp)
                    Text("$${cap.currentBid.toInt()}", color = Color.White, fontSize = 14.sp, fontWeight = FontWeight.Black)
                }
                val stepsCount = ((cap.maxPrice - cap.minPrice) / cap.step).roundToInt() - 1
                Slider(
                    value = cap.currentBid,
                    onValueChange = { newBid ->
                        // --- SWAPPED JAVA Math.round FOR PURE KOTLIN .roundToInt() ---
                        val snapped = (((newBid - cap.minPrice) / cap.step).roundToInt() * cap.step) + cap.minPrice
                        val n = agentCapabilities.toMutableList()
                        n[originalIndex] = cap.copy(currentBid = snapped.coerceIn(cap.minPrice, cap.maxPrice))
                        onUpdate(n)
                    },
                    valueRange = cap.minPrice..cap.maxPrice,
                    steps = if (stepsCount > 0) stepsCount else 0,
                    colors = SliderDefaults.colors(thumbColor = Color(0xFF00BCD4), activeTrackColor = Color(0xFF00BCD4), inactiveTrackColor = Color.DarkGray)
                )
                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                    Text("$${cap.minPrice.toInt()}", color = Color.Gray, fontSize = 10.sp)
                    Text("$${cap.maxPrice.toInt()}", color = Color.Gray, fontSize = 10.sp)
                }
            }
        }
    }
}