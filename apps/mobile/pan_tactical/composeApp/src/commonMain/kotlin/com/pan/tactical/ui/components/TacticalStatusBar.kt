package com.pan.tactical.ui.components

import androidx.compose.foundation.ExperimentalFoundationApi
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.combinedClickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.zIndex
import com.pan.tactical.ui.theme.PanColors

/**
 * TacticalStatusBar
 *
 * The persistent top bar of the agent dashboard. Always visible regardless of mission state.
 *
 * Contains:
 * - A transparent logo-sized hit target on the left (long-press triggers dev menu in debug builds)
 * - Online/offline status dot + label on the right
 * - ID button on the right (navigates to WalletAndProfileScreen)
 *
 * The logo itself is NOT rendered here — it is overlaid at the BoxWithConstraints level
 * with zIndex(100f) so it floats above all screens during the boot animation.
 * This Box is sized to match the logo's resting position (200x70dp) to prevent
 * accidental taps on the map underneath.
 *
 * @param isOnline           Current patrol status from MissionViewModel.
 * @param onNavigateToWallet Called when the agent taps the ID badge.
 * @param modifier           Optional Compose modifier for the root layout.
 * @param onDevMenuLongPress If non-null, a long-press on the logo region triggers this callback.
 * Pass null in production builds. Pass `{ showDevMenu = true }` in debug.
 */
@OptIn(ExperimentalFoundationApi::class)
@Composable
fun TacticalStatusBar(
    isOnline: Boolean,
    onNavigateToWallet: () -> Unit,
    modifier: Modifier = Modifier,
    onDevMenuLongPress: (() -> Unit)? = null
) {
    Row(
        modifier = modifier
            .fillMaxWidth()
            .background(Color.Black)
            .padding(end = 16.dp)
            .zIndex(10f),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        // Transparent hit target — logo floats above this at zIndex(100f)
        Box(
            modifier = Modifier
                .width(200.dp)
                .height(70.dp)
                .let {
                    if (onDevMenuLongPress != null) {
                        it.combinedClickable(
                            onClick = {},
                            onLongClick = onDevMenuLongPress
                        )
                    } else {
                        it.clickable(enabled = false) {}
                    }
                }
        )

        Row(
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // Online / Offline indicator
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(6.dp)
            ) {
                Box(
                    modifier = Modifier
                        .size(10.dp)
                        .background(
                            color = if (isOnline) PanColors.QualifiedGreen else Color(0xFFF44336),
                            shape = CircleShape
                        )
                )
                Text(
                    text = if (isOnline) "ONLINE" else "OFFLINE",
                    color = if (isOnline) PanColors.QualifiedGreen else Color(0xFFF44336),
                    fontSize = 14.sp,
                    fontWeight = FontWeight.Bold
                )
            }

            // ID badge — navigates to WalletAndProfileScreen
            Box(
                modifier = Modifier
                    .size(36.dp)
                    .background(PanColors.ButtonSecondary, RoundedCornerShape(18.dp))
                    .clickable { onNavigateToWallet() },
                contentAlignment = Alignment.Center
            ) {
                Text(
                    text = "ID",
                    color = Color.White,
                    fontSize = 12.sp,
                    fontWeight = FontWeight.Bold
                )
            }
        }
    }
}