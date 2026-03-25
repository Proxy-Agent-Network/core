package com.pan.tactical.ui.components

import androidx.compose.animation.core.*
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.drawscope.rotate
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

@Composable
fun UwbHomingCompass(
    distanceMeters: Float?,
    bearingDegrees: Float?,
    isRanging: Boolean
) {
    // Default 0f is safe — arrow is only rendered when bearingDegrees != null
    val animatedBearing by animateFloatAsState(
        targetValue = bearingDegrees ?: 0f,
        animationSpec = tween(durationMillis = 300, easing = LinearOutSlowInEasing),
        label = "bearing_anim"
    )

    val animatedDistance by animateFloatAsState(
        targetValue = distanceMeters ?: 15f,
        animationSpec = tween(durationMillis = 300, easing = FastOutSlowInEasing),
        label = "distance_anim"
    )

    // A pulsing animation for the outer radar ring
    val infiniteTransition = rememberInfiniteTransition(label = "radar_pulse")
    val pulseScale by infiniteTransition.animateFloat(
        initialValue = 0.8f,
        targetValue = 1.2f,
        animationSpec = infiniteRepeatable(
            animation = tween(1500, easing = LinearOutSlowInEasing),
            repeatMode = RepeatMode.Restart
        ),
        label = "scale_anim"
    )
    val pulseAlpha by infiniteTransition.animateFloat(
        initialValue = 0.5f,
        targetValue = 0f,
        animationSpec = infiniteRepeatable(
            animation = tween(1500, easing = LinearOutSlowInEasing),
            repeatMode = RepeatMode.Restart
        ),
        label = "alpha_anim"
    )

    // Tactical Color Logic: Turn green when within 1 meter (The Strike Zone)
    val isStrikeZone = (distanceMeters != null && !distanceMeters.isNaN() && distanceMeters <= 1.0f)
    val tacticalColor = if (isStrikeZone) Color(0xFF4CAF50) else Color(0xFF00BCD4)

    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp)
            .clip(RoundedCornerShape(16.dp))
            .background(Color(0xFF1E1E1E))
            .padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(
            text = if (isRanging) "UWB MICRO-HOMING ENGAGED" else "SEARCHING FOR AV SIGNAL...",
            color = if (isRanging) tacticalColor else Color.Gray,
            fontSize = 12.sp,
            fontWeight = FontWeight.Black,
            letterSpacing = 1.5.sp
        )

        Spacer(modifier = Modifier.height(32.dp))

        Box(
            modifier = Modifier.size(250.dp),
            contentAlignment = Alignment.Center
        ) {
            // THE RADAR CANVAS
            Canvas(modifier = Modifier.fillMaxSize()) {
                val center = Offset(size.width / 2, size.height / 2)
                val maxRadius = size.width / 2

                // Draw the static tactical grid rings
                drawCircle(color = Color(0xFF333333), radius = maxRadius, style = Stroke(width = 2f))
                drawCircle(color = Color(0xFF333333), radius = maxRadius * 0.66f, style = Stroke(width = 2f))
                drawCircle(color = Color(0xFF333333), radius = maxRadius * 0.33f, style = Stroke(width = 2f))

                // Draw crosshairs
                drawLine(color = Color(0xFF333333), start = Offset(center.x, 0f), end = Offset(center.x, size.height), strokeWidth = 2f)
                drawLine(color = Color(0xFF333333), start = Offset(0f, center.y), end = Offset(size.width, center.y), strokeWidth = 2f)

                if (isRanging && distanceMeters != null && !distanceMeters.isNaN() && bearingDegrees != null) {
                    // Ensure animatedDistance is used for smooth visual scaling
                    val safeDistance = if (animatedDistance.isNaN()) 15f else animatedDistance
                    drawCircle(
                        color = tacticalColor.copy(alpha = pulseAlpha),
                        radius = maxRadius * pulseScale * (safeDistance / 15f).coerceIn(0.1f, 1f)
                    )

                    // Draw the directional arrow
                    rotate(degrees = animatedBearing, pivot = center) {
                        // Scaled dynamically relative to the canvas size
                        val arrowWidth = maxRadius * 0.25f
                        val arrowHeight = maxRadius * 0.15f

                        val path = Path().apply {
                            moveTo(center.x, center.y - maxRadius * 0.8f) // Tip
                            lineTo(center.x + arrowWidth, center.y + arrowHeight) // Bottom Right
                            lineTo(center.x, center.y) // Inner notch
                            lineTo(center.x - arrowWidth, center.y + arrowHeight) // Bottom Left
                            close()
                        }
                        drawPath(path = path, color = tacticalColor)
                    }
                }
            }

            // Central Readout Hub
            Box(
                modifier = Modifier
                    .size(90.dp)
                    .clip(CircleShape)
                    .background(Color(0xFF121212))
                    .align(Alignment.Center),
                contentAlignment = Alignment.Center
            ) {
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    if (isRanging && distanceMeters != null) {
                        // 🛠️ THE FIX: Guard against hardware NaN glitches
                        val formattedDistance = if (distanceMeters.isNaN()) {
                            "---"
                        } else {
                            ((distanceMeters * 10).toInt() / 10f).toString()
                        }

                        Text(
                            text = formattedDistance,
                            color = tacticalColor,
                            fontSize = 28.sp,
                            fontWeight = FontWeight.Black
                        )
                        Text(
                            text = "METERS",
                            color = Color.Gray,
                            fontSize = 10.sp,
                            fontWeight = FontWeight.Bold
                        )
                    } else {
                        Text("---", color = Color.DarkGray, fontSize = 28.sp, fontWeight = FontWeight.Black)
                    }
                }
            }
        }
    }
}