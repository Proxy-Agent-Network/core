package com.pan.tactical.ui

import androidx.compose.ui.text.AnnotatedString
import androidx.compose.ui.text.input.OffsetMapping
import androidx.compose.ui.text.input.TransformedText
import androidx.compose.ui.text.input.VisualTransformation

// ============================================================================
// TacticalComponents.kt
//
// SwipeActionSlider has been removed from this file.
// The canonical implementation lives at:
//   com.pan.tactical.ui.components.SwipeActionSlider
//   (SwipeActionSlider.kt in the ui/components package)
//
// Any file that previously imported SwipeActionSlider from com.pan.tactical.ui
// must update its import to com.pan.tactical.ui.components.
// ============================================================================

// --- SECURE CREDIT CARD FORMATTER ---
// Used by WalletAndProfileScreen for masked card number input.
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
