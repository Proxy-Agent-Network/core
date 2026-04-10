package com.pan.tactical

import androidx.compose.runtime.Composable
import com.pan.tactical.ui.screens.PanBootSequence

// BootSequence.android.kt — androidMain actual implementation
//
// Delegates entirely to PanBootSequence, which owns the full Android-specific
// boot flow: StrongBox key generation, Firebase Auth identity check,
// Google Play Integrity attestation, and server-side verification.
//
// Keeping this file as a thin wrapper preserves the ability to swap or
// extend the Android boot implementation without touching commonMain.

@Composable
actual fun BootSequence(onBootComplete: () -> Unit) {
    PanBootSequence(onBootComplete = onBootComplete)
}