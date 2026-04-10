package com.pan.tactical

import androidx.compose.runtime.Composable

// BootSequence.kt — commonMain expect declaration
//
// This expect function is the KMP bridge that allows App.kt (commonMain) to
// call a platform-specific boot screen without importing any Android or iOS
// libraries directly.
//
// Android actual: delegates to PanBootSequence (Firebase + Play Integrity)
// iOS actual:     stub pass-through until Secure Enclave logic is built (Q3 2026)

@Composable
expect fun BootSequence(onBootComplete: () -> Unit)