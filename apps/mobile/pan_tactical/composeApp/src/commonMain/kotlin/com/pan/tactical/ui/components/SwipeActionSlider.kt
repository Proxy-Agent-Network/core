package com.pan.tactical.ui.components

// ============================================================================
// CANONICAL VERSION — com.pan.tactical.ui.components
//
// The duplicate SwipeActionSlider in TacticalComponents.kt
// (com.pan.tactical.ui) must be deleted. This file is the single
// source of truth. It supersedes the old version with:
//   - Smooth snap-back animation (animateFloatAsState)
//   - isDragging flag for real-time feel during drag
//   - modifier parameter for caller-controlled sizing and padding
// ============================================================================

import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.foundation.background
import androidx.compose.foundation.gestures.detectHorizontalDragGestures
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.layout.onSizeChanged
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.IntOffset
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlin.math.roundToInt

@Composable
fun SwipeActionSlider(
    text: String,
    trackColor: Color,
    thumbColor: Color,
    onSwipeComplete: () -> Unit,
    modifier: Modifier = Modifier  // Caller controls outer sizing/padding
) {
    var swipeOffset by remember { mutableStateOf(0f) }
    var isDragging by remember { mutableStateOf(false) }
    val thumbSize = 56.dp
    var maxWidthPx by remember { mutableStateOf(0f) }
    val density = LocalDensity.current

    // Smooth snap-back animation when the agent releases before the threshold.
    // While actively dragging, use the raw offset for real-time feel.
    val animatedOffset by animateFloatAsState(targetValue = swipeOffset, label = "swipe_snap")
    val currentOffset = if (isDragging) swipeOffset else animatedOffset

    Box(
        modifier = modifier
            .fillMaxWidth()
            .height(thumbSize)
            .background(trackColor, RoundedCornerShape(8.dp))
            .onSizeChanged { maxWidthPx = it.width.toFloat() },
        contentAlignment = Alignment.CenterStart
    ) {

        // 1. THE TEXT
        // Drawn first — sits on the bottom layer.
        // Gets covered by the expanding fill track as the agent swipes.
        Text(
            text = text,
            color = Color(0xFF999999),
            fontWeight = FontWeight.Bold,
            fontSize = 14.sp,
            letterSpacing = 1.sp,
            modifier = Modifier
                .align(Alignment.Center)
                .padding(start = thumbSize)
        )

        // 2. THE EXPANDING FILL TRACK
        // Stretches from the left edge to the right edge of the thumb.
        Box(
            modifier = Modifier
                .fillMaxHeight()
                .width(with(density) { currentOffset.toDp() + thumbSize })
                .background(thumbColor, RoundedCornerShape(8.dp))
        )

        // 3. THE DRAGGABLE THUMB
        Box(
            modifier = Modifier
                .offset { IntOffset(currentOffset.roundToInt(), 0) }
                .size(thumbSize)
                .background(thumbColor, RoundedCornerShape(8.dp))
                .pointerInput(Unit) {
                    detectHorizontalDragGestures(
                        onDragStart = { isDragging = true },
                        onDragEnd = {
                            isDragging = false
                            val maxSwipe = maxWidthPx - thumbSize.toPx()
                            // 75% swipe required — deliberate friction to prevent
                            // accidental mission aborts or offline toggling.
                            if (swipeOffset > maxSwipe * 0.75f) {
                                swipeOffset = maxSwipe
                                onSwipeComplete()
                            } else {
                                swipeOffset = 0f  // Snap back
                            }
                        }
                    ) { change, dragAmount ->
                        change.consume()
                        val maxSwipe = maxWidthPx - thumbSize.toPx()
                        swipeOffset = (swipeOffset + dragAmount).coerceIn(0f, maxSwipe)
                    }
                },
            contentAlignment = Alignment.Center
        ) {
            Text(">>", color = Color.White, fontWeight = FontWeight.Bold, fontSize = 18.sp)
        }
    }
}
