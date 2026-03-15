package com.pan.tactical.ui.components

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
    onSwipeComplete: () -> Unit
) {
    var swipeOffset by remember { mutableStateOf(0f) }
    var isDragging by remember { mutableStateOf(false) }
    val thumbSize = 56.dp
    var maxWidthPx by remember { mutableStateOf(0f) }
    val density = LocalDensity.current

    // Smooth snap-back animation if the agent lets go before the end
    val animatedOffset by animateFloatAsState(targetValue = swipeOffset, label = "swipe_snap")

    // Use the active drag offset if touching, otherwise use the snap-back animation value
    val currentOffset = if (isDragging) swipeOffset else animatedOffset

    Box(
        modifier = Modifier
            .fillMaxWidth()
            .height(thumbSize)
            .background(trackColor, RoundedCornerShape(8.dp))
            .onSizeChanged { maxWidthPx = it.width.toFloat() },
        contentAlignment = Alignment.CenterStart
    ) {

        // 1. THE TEXT
        // Drawn first so it sits on the bottom layer. It will be covered up as the fill expands!
        Text(
            text = text,
            color = Color(0xFF999999), // Subdued medium grey
            fontWeight = FontWeight.Bold,
            fontSize = 14.sp,
            letterSpacing = 1.sp,
            modifier = Modifier
                .align(Alignment.Center)
                .padding(start = thumbSize)
        )

        // 2. THE EXPANDING FILL TRACK
        // This box stretches from the left edge to the right edge of the thumb
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
                            // Require a 75% swipe to trigger the action
                            if (swipeOffset > maxSwipe * 0.75f) {
                                swipeOffset = maxSwipe
                                onSwipeComplete()
                            } else {
                                swipeOffset = 0f
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