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
import kotlin.math.abs
import kotlin.math.roundToInt

// 🟢 THE FIX 1: KMP-safe float formatter.
// Standard String.format is JVM-only and breaks iOS builds.
fun formatDistanceKmp(distance: Float): String {
    if (distance.isNaN()) return "---"
    val isNegative = distance < 0
    val absolute = abs(distance)
    val scaled = (absolute * 10.0).roundToInt()
    val whole = scaled / 10
    val fraction = scaled % 10
    val prefix = if (isNegative) "-" else ""
    return "$prefix$whole.$fraction"
}

@Composable
fun UwbHomingCompass(
    distanceMeters: Float?,
    bearingDegrees: Float?,
    isRanging: Boolean
) {
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

    // 🟢 THE FIX 3: Idle searching animation
    val idleRotation by infiniteTransition.animateFloat(
        initialValue = 0f,
        targetValue = 360f,
        animationSpec = infiniteRepeatable(
            animation = tween(8000, easing = LinearEasing),
            repeatMode = RepeatMode.Restart
        ),
        label = "idle_rotation"
    )

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
            Canvas(modifier = Modifier.fillMaxSize()) {
                val center = Offset(size.width / 2, size.height / 2)
                val maxRadius = size.width / 2

                // Rotate the grid slowly if we are searching, or lock it if we have a signal
                val gridRotation = if (isRanging) 0f else idleRotation

                rotate(degrees = gridRotation, pivot = center) {
                    drawCircle(color = Color(0xFF333333), radius = maxRadius, style = Stroke(width = 2f))
                    drawCircle(color = Color(0xFF333333), radius = maxRadius * 0.66f, style = Stroke(width = 2f))
                    drawCircle(color = Color(0xFF333333), radius = maxRadius * 0.33f, style = Stroke(width = 2f))

                    drawLine(color = Color(0xFF333333), start = Offset(center.x, 0f), end = Offset(center.x, size.height), strokeWidth = 2f)
                    drawLine(color = Color(0xFF333333), start = Offset(0f, center.y), end = Offset(size.width, center.y), strokeWidth = 2f)
                }

                if (isRanging && distanceMeters != null && !distanceMeters.isNaN() && bearingDegrees != null) {
                    val safeDistance = if (animatedDistance.isNaN()) 15f else animatedDistance
                    drawCircle(
                        color = tacticalColor.copy(alpha = pulseAlpha),
                        radius = maxRadius * pulseScale * (safeDistance / 15f).coerceIn(0.1f, 1f)
                    )

                    rotate(degrees = animatedBearing, pivot = center) {
                        val arrowWidth = maxRadius * 0.25f
                        val arrowHeight = maxRadius * 0.15f

                        val path = Path().apply {
                            moveTo(center.x, center.y - maxRadius * 0.8f)
                            lineTo(center.x + arrowWidth, center.y + arrowHeight)
                            lineTo(center.x, center.y)
                            lineTo(center.x - arrowWidth, center.y + arrowHeight)
                            close()
                        }
                        drawPath(path = path, color = tacticalColor)
                    }
                }
            }

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
                        Text(
                            text = formatDistanceKmp(distanceMeters),
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