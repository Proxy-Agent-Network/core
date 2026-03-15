package com.pan.tactical.ui.components

import androidx.compose.animation.animateContentSize
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Slider
import androidx.compose.material3.SliderDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.pan.tactical.models.AgentCapability

// Make sure your TacticalComponents.kt file has been moved to this same folder
// so CapabilityCard can be properly resolved!
import com.pan.tactical.ui.components.CapabilityCard

@Composable
fun OfflineLoadoutMenu(
    isLoadoutExpanded: Boolean,
    onToggleExpand: () -> Unit,
    patrolMode: String,
    onPatrolModeChange: (String) -> Unit,
    serviceRadiusMiles: Float,
    onRadiusChange: (Float) -> Unit,
    agentCapabilities: List<AgentCapability>,
    onCapabilitiesChange: (List<AgentCapability>) -> Unit
) {
    Column(modifier = Modifier.padding(16.dp).animateContentSize(), horizontalAlignment = Alignment.CenterHorizontally) {
        Row(
            modifier = Modifier.fillMaxWidth()
                .background(Color(0xFF2A2A2A), RoundedCornerShape(8.dp))
                .clip(RoundedCornerShape(8.dp))
                .clickable { onToggleExpand() }
                .padding(16.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text("🛠 MARKET BIDS & LOADOUT", color = Color.White, fontSize = 12.sp, fontWeight = FontWeight.Black, letterSpacing = 1.sp)
            Text(if (isLoadoutExpanded) "HIDE ▲" else "EXPAND ▼", color = Color(0xFF00BCD4), fontSize = 12.sp, fontWeight = FontWeight.Bold)
        }

        if (isLoadoutExpanded) {
            Column(modifier = Modifier.fillMaxWidth().padding(top = 16.dp)) {
                Row(modifier = Modifier.fillMaxWidth().padding(bottom = 16.dp), horizontalArrangement = Arrangement.spacedBy(16.dp)) {
                    Button(
                        onClick = { onPatrolModeChange("VEHICLE") },
                        colors = ButtonDefaults.buttonColors(containerColor = if (patrolMode == "VEHICLE") Color(0xFF1976D2) else Color(0xFF333333)),
                        modifier = Modifier.weight(1f).height(48.dp), shape = RoundedCornerShape(8.dp)
                    ) { Text("VEHICLE", color = Color.White, fontSize = 12.sp, fontWeight = FontWeight.Bold) }

                    Button(
                        onClick = { onPatrolModeChange("FOOT") },
                        colors = ButtonDefaults.buttonColors(containerColor = if (patrolMode == "FOOT") Color(0xFF00BCD4) else Color(0xFF333333)),
                        modifier = Modifier.weight(1f).height(48.dp), shape = RoundedCornerShape(8.dp)
                    ) { Text("FOOT PATROL", color = if (patrolMode == "FOOT") Color.Black else Color.White, fontSize = 12.sp, fontWeight = FontWeight.Bold) }
                }

                val isFoot = patrolMode == "FOOT"
                // --- SWAPPED JAVA STRING.FORMAT FOR PURE KOTLIN MATH ---
                val displayRadius = if (isFoot) {
                    val whole = serviceRadiusMiles.toInt()
                    val fraction = ((serviceRadiusMiles - whole) * 1000).toInt().toString().padEnd(3, '0').take(3)
                    "$whole.$fraction"
                } else {
                    serviceRadiusMiles.toInt().toString()
                }

                Text("SERVICE RADIUS: $displayRadius MILES", color = Color.LightGray, fontSize = 12.sp, fontWeight = FontWeight.Bold)

                Slider(
                    value = serviceRadiusMiles,
                    onValueChange = onRadiusChange,
                    valueRange = if (isFoot) 0.125f..1f else 1f..8f,
                    steps = 6,
                    colors = SliderDefaults.colors(thumbColor = Color(0xFFF44336), activeTrackColor = Color(0xFFF44336)),
                    modifier = Modifier.padding(bottom = 12.dp)
                )

                Column(modifier = Modifier.fillMaxWidth().heightIn(max = 350.dp).verticalScroll(rememberScrollState()).padding(bottom = 16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    val pinned = agentCapabilities.filter { it.isPinned }
                    val tier1 = agentCapabilities.filter { it.tier == 1 && !it.isPinned }
                    val tier2 = agentCapabilities.filter { it.tier == 2 && !it.isPinned }
                    val tier3 = agentCapabilities.filter { it.tier == 3 && !it.isPinned }

                    if (pinned.isNotEmpty()) {
                        Text("📌 PINNED TASKS", color = Color(0xFFFF9800), fontSize = 12.sp, fontWeight = FontWeight.Black, modifier = Modifier.padding(top = 8.dp, bottom = 4.dp))
                        pinned.forEach { cap -> CapabilityCard(cap, agentCapabilities) { onCapabilitiesChange(it) } }
                    }
                    if (tier1.isNotEmpty()) {
                        Text("TIER 1 - BASIC RESPONDER", color = Color(0xFF00BCD4), fontSize = 12.sp, fontWeight = FontWeight.Black, modifier = Modifier.padding(top = 8.dp, bottom = 4.dp))
                        tier1.forEach { cap -> CapabilityCard(cap, agentCapabilities) { onCapabilitiesChange(it) } }
                    }

                    if (patrolMode == "VEHICLE") {
                        if (tier2.isNotEmpty()) {
                            Text("TIER 2 - EQUIPMENT REQUIRED", color = Color(0xFF00BCD4), fontSize = 12.sp, fontWeight = FontWeight.Black, modifier = Modifier.padding(top = 8.dp, bottom = 4.dp))
                            tier2.forEach { cap -> CapabilityCard(cap, agentCapabilities) { onCapabilitiesChange(it) } }
                        }
                        if (tier3.isNotEmpty()) {
                            Text("TIER 3 - SPECIALIZED TRAINING", color = Color(0xFF00BCD4), fontSize = 12.sp, fontWeight = FontWeight.Black, modifier = Modifier.padding(top = 8.dp, bottom = 4.dp))
                            tier3.forEach { cap -> CapabilityCard(cap, agentCapabilities) { onCapabilitiesChange(it) } }
                        }
                    } else {
                        Text("🚫 TIER 2 & 3 TASKS DISABLED ON FOOT PATROL", color = Color(0xFFF44336), fontSize = 10.sp, fontWeight = FontWeight.Bold, modifier = Modifier.padding(top = 16.dp, bottom = 4.dp).fillMaxWidth(), textAlign = TextAlign.Center)
                    }
                }
            }
        }
    }
}