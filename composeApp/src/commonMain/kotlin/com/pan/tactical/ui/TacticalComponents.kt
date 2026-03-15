package com.pan.tactical.ui

import androidx.compose.animation.core.Animatable
import androidx.compose.foundation.background
import androidx.compose.foundation.gestures.detectHorizontalDragGestures
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.layout.onSizeChanged
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.text.AnnotatedString
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.OffsetMapping
import androidx.compose.ui.text.input.TransformedText
import androidx.compose.ui.text.input.VisualTransformation
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.IntOffset
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlinx.coroutines.launch
import kotlin.math.roundToInt

// --- SECURE CREDIT CARD FORMATTER ---
class CreditCardVisualTransformation : VisualTransformation {
    override fun filter(text: AnnotatedString): TransformedText {
        val trimmed = text.text.take(16)
        var out = ""
        for (i in trimmed.indices) {
            out += trimmed[i]
            if (i % 4 == 3 && i != 15) out += " "
        }

        val offsetMapping = object : OffsetMapping {
            override fun originalToTransformed(offset: Int): Int {
                if (offset <= 3) return offset
                if (offset <= 7) return offset + 1
                if (offset <= 11) return offset + 2
                if (offset <= 16) return offset + 3
                return 19
            }
            override fun transformedToOriginal(offset: Int): Int {
                if (offset <= 4) return offset
                if (offset <= 9) return offset - 1
                if (offset <= 14) return offset - 2
                if (offset <= 19) return offset - 3
                return 16
            }
        }
        return TransformedText(AnnotatedString(out), offsetMapping)
    }
}

// --- CUSTOM TACTICAL SWIPE SLIDER ---
@Composable
fun SwipeActionSlider(
    modifier: Modifier = Modifier,
    text: String,
    trackColor: Color = Color(0xFF2C2C2C),
    thumbColor: Color = Color(0xFFD32F2F),
    textColor: Color = Color.Red.copy(alpha = 0.5f),
    onSwipeComplete: () -> Unit
) {
    val thumbSize = 64.dp
    val trackHeight = 64.dp
    val swipeState = remember { Animatable(0f) }
    val coroutineScope = rememberCoroutineScope()
    var trackWidthPx by remember { mutableFloatStateOf(0f) }

    val density = LocalDensity.current
    val thumbSizePx = with(density) { thumbSize.toPx() }

    Box(
        modifier = modifier
            .fillMaxWidth()
            .height(trackHeight)
            .clip(RoundedCornerShape(8.dp))
            .background(trackColor)
            .onSizeChanged { trackWidthPx = it.width.toFloat() },
        contentAlignment = Alignment.CenterStart
    ) {

        Box(
            modifier = Modifier
                .fillMaxHeight()
                .width(with(density) { (swipeState.value + thumbSizePx).toDp() })
                .clip(RoundedCornerShape(8.dp))
                .background(thumbColor.copy(alpha = 0.5f))
        )

        Text(
            text = text,
            color = textColor,
            modifier = Modifier.fillMaxWidth(),
            textAlign = TextAlign.Center,
            fontWeight = FontWeight.Bold,
            letterSpacing = 2.sp
        )

        Box(
            modifier = Modifier
                .offset { IntOffset(swipeState.value.roundToInt(), 0) }
                .size(thumbSize)
                .clip(RoundedCornerShape(8.dp))
                .background(thumbColor)
                .pointerInput(Unit) {
                    detectHorizontalDragGestures(
                        onDragEnd = {
                            val threshold = trackWidthPx - thumbSizePx
                            if (swipeState.value >= threshold * 0.85f) {
                                coroutineScope.launch {
                                    swipeState.snapTo(threshold)
                                    onSwipeComplete()
                                }
                            } else {
                                coroutineScope.launch { swipeState.animateTo(0f) }
                            }
                        }
                    ) { change, dragAmount ->
                        change.consume()
                        coroutineScope.launch {
                            val newOffset = (swipeState.value + dragAmount).coerceIn(0f, trackWidthPx - thumbSizePx)
                            swipeState.snapTo(newOffset)
                        }
                    }
                },
            contentAlignment = Alignment.Center
        ) {
            Text(">>", color = Color.White, fontWeight = FontWeight.Black, fontSize = 20.sp)
        }
    }
}