package com.pan.tactical.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.pan.tactical.ui.theme.PanColors

// ─── DATA MODELS & BUSINESS LOGIC ────────────────────────────────────────────

// 🛡️ BUG 1, FINDING 1 & 2 FIXED: Restored semantic icons, original thresholds, and missionsPerStar math
enum class AgentRank(val displayName: String, val icon: String, val missionThreshold: Int, val missionsPerStar: Int) {
    RECRUIT("Recruit", "🔰", 0, 2),
    FIELD_AGENT("Field Agent", "🔦", 10, 8),
    VANGUARD("Vanguard", "⚡", 50, 20),
    SPECIALIST("Specialist", "🛠️", 150, 20),
    OPERATOR("Operator", "🦅", 250, 50),
    PHANTOM("Phantom", "👻", 500, 0)
}

fun rankForMissions(missionsCompleted: Int): AgentRank {
    // 🛡️ FINDING 3 FIXED: Using .entries for zero-allocation access
    return AgentRank.entries.lastOrNull { missionsCompleted >= it.missionThreshold } ?: AgentRank.RECRUIT
}

fun nextRankForMissions(missionsCompleted: Int): AgentRank? {
    return AgentRank.entries.firstOrNull { missionsCompleted < it.missionThreshold }
}

internal fun resolveEasterEggHint(
    rank: AgentRank,
    ownsHapHat: Boolean,
    ownsGauntlets: Boolean
): String? = when (rank) {
    AgentRank.RECRUIT -> null
    AgentRank.FIELD_AGENT -> "Midnight missions carry a different color. Keep working."
    AgentRank.VANGUARD -> "Greet your partner on scene. The network rewards it."
    // 🛡️ BUG 2 FIXED: Strict radio silence for agents without hardware
    AgentRank.SPECIALIST -> if (ownsHapHat) "Double-tap signals something." else null
    AgentRank.OPERATOR -> if (ownsGauntlets) "The handshake isn't finished when you think it is." else null
    AgentRank.PHANTOM -> null
}

// ─── UI COMPONENT ────────────────────────────────────────────────────────────

@Composable
fun AgentRankCard(
    missionsCompleted: Int,
    modifier: Modifier = Modifier
) {
    val currentRank = rankForMissions(missionsCompleted)
    val nextRank = nextRankForMissions(missionsCompleted)

    Column(
        modifier = modifier
            .fillMaxWidth()
            .background(PanColors.SurfaceMid)
            .padding(horizontal = 24.dp, vertical = 16.dp)
    ) {
        Text(
            text = "VANGUARD NETWORK RANK",
            color = Color.LightGray,
            fontSize = 11.sp,
            fontWeight = FontWeight.Bold,
            letterSpacing = 1.sp,
            modifier = Modifier.padding(bottom = 12.dp)
        )

        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically
        ) {
            // Badge
            Box(
                modifier = Modifier
                    .size(48.dp)
                    .background(Color(0xFF121212), CircleShape)
                    .border(1.dp, PanColors.ButtonSecondary, CircleShape),
                contentAlignment = Alignment.Center
            ) {
                Text(
                    text = currentRank.icon,
                    fontSize = 24.sp
                )
            }

            Spacer(modifier = Modifier.width(16.dp))

            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = currentRank.displayName.uppercase(),
                    color = Color.White,
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Black,
                    letterSpacing = 1.sp
                )

                Text(
                    text = "$missionsCompleted Missions Secured",
                    color = PanColors.CyanAccent,
                    fontSize = 12.sp,
                    fontWeight = FontWeight.Medium
                )
            }
        }

        if (nextRank != null) {
            Spacer(modifier = Modifier.height(16.dp))

            // Calculate stepped-linear progress
            val progressInRank = missionsCompleted - currentRank.missionThreshold
            val starsEarned = if (currentRank.missionsPerStar > 0) {
                (progressInRank / currentRank.missionsPerStar).coerceIn(0, 5)
            } else 0

            val missionsRemaining = nextRank.missionThreshold - missionsCompleted

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.Bottom
            ) {
                Text(
                    text = "NEXT: ${nextRank.displayName.uppercase()}",
                    color = Color.Gray,
                    fontSize = 10.sp,
                    fontWeight = FontWeight.Bold
                )
                Text(
                    text = "$missionsRemaining remaining",
                    color = Color.Gray,
                    fontSize = 10.sp,
                    fontWeight = FontWeight.Bold
                )
            }

            Spacer(modifier = Modifier.height(8.dp))

            // 5-Segment Star System
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                for (i in 0 until 5) {
                    val isEarned = i < starsEarned
                    Box(
                        modifier = Modifier
                            .weight(1f)
                            .padding(end = if (i < 4) 4.dp else 0.dp)
                            .height(6.dp)
                            .clip(RoundedCornerShape(3.dp))
                            .background(if (isEarned) PanColors.CyanAccent else Color(0xFF2A2A2A))
                    )
                }
            }
        }
    }
}