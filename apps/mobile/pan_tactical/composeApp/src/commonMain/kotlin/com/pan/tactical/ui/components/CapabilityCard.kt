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
import com.pan.tactical.models.AgentCapabilityUiModel
import com.pan.tactical.ui.theme.PanColors
import kotlin.math.roundToInt

@OptIn(ExperimentalFoundationApi::class)
@Composable
fun CapabilityCard(
    capUi: AgentCapabilityUiModel,
    agentCapabilities: List<AgentCapabilityUiModel>,
    onUpdate: (List<AgentCapabilityUiModel>) -> Unit
) {
    var isDetailsExpanded by remember(capUi.id) { mutableStateOf(false) }

    val rotationAngle by animateFloatAsState(
        targetValue = if (isDetailsExpanded) 180f else 0f,
        label = "arrow_rotation"
    )

    val safeMin = capUi.minPrice
    val safeMax = capUi.maxPrice
    val safeStep = capUi.step

    // 🛡️ [PHASE 5] Guard validates range and step to prevent Slider math crashes
    if (safeMin >= safeMax || safeStep <= 0f) return

    Column(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(8.dp))
            .background(
                when {
                    !capUi.isQualified -> PanColors.SurfaceDark // 🛡️ FIXED: Added PanColors prefix
                    capUi.isEnabled -> PanColors.QualifiedGreen.copy(alpha = 0.1f)
                    else -> PanColors.SurfaceMid // 🛡️ FIXED
                }
            )
            .border(
                width = 1.dp,
                color = when {
                    !capUi.isQualified -> PanColors.SurfaceMid // 🛡️ FIXED
                    capUi.isEnabled -> PanColors.QualifiedGreen
                    else -> PanColors.SurfaceLight // 🛡️ FIXED
                },
                shape = RoundedCornerShape(8.dp)
            )
            .combinedClickable(
                onLongClick = {
                    val idx = agentCapabilities.indexOfFirst { it.id == capUi.id }
                    if (idx != -1) {
                        val n = agentCapabilities.toMutableList()
                        n[idx] = capUi.copy(isPinned = !capUi.isPinned)
                        onUpdate(n)
                    }
                },
                onClick = { isDetailsExpanded = !isDetailsExpanded }
            )
            .padding(12.dp)
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                if (capUi.isPinned) Text("📌 ", fontSize = 14.sp)
                if (!capUi.isQualified) Text("🔒 ", fontSize = 14.sp)
                Text(
                    text = capUi.title,
                    color = if (!capUi.isQualified) Color.DarkGray else Color.White,
                    fontSize = 14.sp,
                    fontWeight = FontWeight.Bold
                )

                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    text = "▼",
                    color = Color.Gray,
                    fontSize = 12.sp,
                    modifier = Modifier.rotate(rotationAngle)
                )
            }
            if (capUi.isQualified) {
                Switch(
                    checked = capUi.isEnabled,
                    onCheckedChange = { isChecked ->
                        val idx = agentCapabilities.indexOfFirst { it.id == capUi.id }
                        if (idx != -1) {
                            val n = agentCapabilities.toMutableList()
                            n[idx] = capUi.copy(isEnabled = isChecked)
                            onUpdate(n)
                        }
                    },
                    colors = SwitchDefaults.colors(checkedTrackColor = PanColors.QualifiedGreen)
                )
            }
        }

        AnimatedVisibility(visible = isDetailsExpanded) {
            Column(modifier = Modifier.padding(top = 8.dp)) {
                Text(capUi.description, color = Color.LightGray, fontSize = 12.sp, lineHeight = 16.sp)
                if (!capUi.isQualified && capUi.requiredTraining != null) {
                    Spacer(modifier = Modifier.height(4.dp))
                    Text("⚠️ ${capUi.requiredTraining}", color = PanColors.WarningOrange, fontSize = 10.sp, fontWeight = FontWeight.Bold)
                } else if (capUi.isQualified && capUi.requiredTraining != null) {
                    Spacer(modifier = Modifier.height(4.dp))
                    Text("🛡️ Authorized: ${capUi.requiredTraining}", color = PanColors.QualifiedGreen, fontSize = 10.sp, fontWeight = FontWeight.Bold)
                }
            }
        }

        AnimatedVisibility(visible = capUi.isEnabled && capUi.isQualified) {
            Column(modifier = Modifier.fillMaxWidth().padding(top = 12.dp)) {
                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                    Text("YOUR MINIMUM BID", color = PanColors.CyanAccent, fontSize = 10.sp, fontWeight = FontWeight.Bold, letterSpacing = 1.sp)
                    Text("$${capUi.currentBid.roundToInt()}", color = Color.White, fontSize = 14.sp, fontWeight = FontWeight.Black)
                }

                val safeBid = capUi.currentBid.coerceIn(safeMin, safeMax)
                val stepsCount = ((safeMax - safeMin) / safeStep).roundToInt() - 1

                Slider(
                    value = safeBid,
                    onValueChange = { newBid ->
                        val idx = agentCapabilities.indexOfFirst { it.id == capUi.id }
                        if (idx != -1) {
                            val snapped = (((newBid - safeMin) / safeStep).roundToInt() * safeStep) + safeMin
                            val n = agentCapabilities.toMutableList()
                            n[idx] = capUi.copy(currentBid = snapped.coerceIn(safeMin, safeMax))
                            onUpdate(n)
                        }
                    },
                    valueRange = safeMin..safeMax,
                    steps = if (stepsCount > 0) stepsCount else 0,
                    colors = SliderDefaults.colors(
                        thumbColor = PanColors.CyanAccent,
                        activeTrackColor = PanColors.CyanAccent,
                        inactiveTrackColor = Color.DarkGray
                    )
                )
                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                    Text("$${safeMin.toInt()}", color = Color.Gray, fontSize = 10.sp)
                    Text("$${safeMax.toInt()}", color = Color.Gray, fontSize = 10.sp)
                }
            }
        }
    }
}