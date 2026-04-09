package com.pan.tactical.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import com.pan.tactical.ui.theme.PanColors

@Composable
fun RankUpOverlay(
    newRank: AgentRank,
    ownsHapHat: Boolean,
    ownsGauntlets: Boolean,
    onDismiss: () -> Unit
) {
    // 🛡️ BUG 4 FIXED: Phantom rank-up enforces strict radio silence
    if (newRank == AgentRank.PHANTOM) {
        LaunchedEffect(Unit) { onDismiss() }
        return
    }

    Dialog(
        onDismissRequest = onDismiss,
        properties = DialogProperties(
            usePlatformDefaultWidth = false,
            dismissOnBackPress = false,
            dismissOnClickOutside = false
        )
    ) {
        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(Color.Black.copy(alpha = 0.9f)),
            contentAlignment = Alignment.Center
        ) {
            Column(
                modifier = Modifier
                    .fillMaxWidth(0.9f)
                    .clip(RoundedCornerShape(16.dp))
                    .background(Color(0xFF1E1E1E))
                    .border(2.dp, PanColors.CyanAccent, RoundedCornerShape(16.dp))
                    .padding(24.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Text(
                    text = "PROMOTION AUTHORIZED",
                    color = PanColors.CyanAccent,
                    fontSize = 14.sp,
                    fontWeight = FontWeight.Black,
                    letterSpacing = 2.sp,
                    modifier = Modifier.padding(bottom = 16.dp)
                )

                // Big Rank Badge
                // 🛡️ BUG 1 FIXED: CircleShape correctly imported
                Box(
                    modifier = Modifier
                        .size(100.dp)
                        .background(Color.Black, CircleShape)
                        .border(2.dp, PanColors.CyanAccent, CircleShape),
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        text = newRank.icon,
                        fontSize = 48.sp
                    )
                }

                Spacer(modifier = Modifier.height(16.dp))

                // 🛡️ BUG 2 FIXED: Using valid enum property 'displayName'
                Text(
                    text = newRank.displayName.uppercase(),
                    color = Color.White,
                    fontSize = 28.sp,
                    fontWeight = FontWeight.Black,
                    letterSpacing = 1.sp
                )

                Text(
                    text = "Vanguard Network access level upgraded.",
                    color = Color.LightGray,
                    fontSize = 14.sp,
                    textAlign = TextAlign.Center,
                    modifier = Modifier.padding(top = 8.dp, bottom = 24.dp)
                )

                // 🛡️ BUG 3 FIXED: Restored spec-compliant encrypted lore hints
                val hint = resolveEasterEggHint(newRank, ownsHapHat, ownsGauntlets)
                if (hint != null) {
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .background(Color.Black, RoundedCornerShape(8.dp))
                            .padding(16.dp)
                    ) {
                        Text(
                            text = "DECRYPTED NETWORK CHATTER",
                            color = Color.Gray,
                            fontSize = 10.sp,
                            fontWeight = FontWeight.Bold,
                            modifier = Modifier.padding(bottom = 8.dp)
                        )

                        Text(
                            text = "▶ $hint",
                            color = PanColors.CyanAccent,
                            fontSize = 12.sp,
                            fontWeight = FontWeight.Medium,
                            lineHeight = 16.sp
                        )
                    }
                }

                Spacer(modifier = Modifier.height(24.dp))

                Button(
                    onClick = onDismiss,
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(56.dp),
                    colors = ButtonDefaults.buttonColors(containerColor = PanColors.CyanAccent),
                    shape = RoundedCornerShape(8.dp)
                ) {
                    Text(
                        text = "ACKNOWLEDGE",
                        color = Color.Black,
                        fontSize = 16.sp,
                        fontWeight = FontWeight.Black,
                        letterSpacing = 1.sp
                    )
                }
            }
        }
    }
}