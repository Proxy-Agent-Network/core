package com.pan.tactical

import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect

// BootSequence.ios.kt — iosMain actual stub
//
// iOS Secure Enclave attestation is not yet implemented (Q3 2026).
// This stub passes through to onBootComplete() immediately so that
// the shared App.kt routing and AgentDashboardScreen work correctly
// during iOS development without a real attestation gate.
//
// TODO(ios-Q3-2026): Replace LaunchedEffect pass-through with a real
// iOS boot sequence that performs Secure Enclave key generation and
// server-side attestation — matching the Android flow in PanBootSequence.kt.

@Composable
actual fun BootSequence(onBootComplete: () -> Unit) {
    LaunchedEffect(Unit) {
        onBootComplete()
    }
}