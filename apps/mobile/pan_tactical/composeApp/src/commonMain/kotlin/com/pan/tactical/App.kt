package com.pan.tactical

import androidx.compose.material3.MaterialTheme
import androidx.compose.runtime.*
import com.pan.tactical.ui.WalletNetworkClient
import com.pan.tactical.ui.AgentDashboardScreen // 🛡️ FIX: Import explicitly here

// App.kt lives in commonMain and is the root of the shared UI tree.
// It routes between the platform-specific boot screen (via expect/actual)
// and the shared AgentDashboardScreen.
//
// Flow: MainActivity → HardwarePermissionsGuard → App → BootSequence (actual) → AgentDashboardScreen

@Composable
fun App(apiClient: WalletNetworkClient) {
    MaterialTheme {
        var currentScreen by remember { mutableStateOf("BOOT") }
        
        // 🛡️ FIX: Hoist the AudioEngine and remember it across recompositions.
        // This gives the OS Text-To-Speech engine time to warm up during the boot sequence
        // and prevents memory leaks from creating disposable TTS instances in lambdas.
        val audioEngine = remember { AudioEngine() }

        when (currentScreen) {
            "BOOT" -> {
                BootSequence(
                    onBootComplete = {
                        audioEngine.playAlertBeep(100)
                        audioEngine.speak("Hardware identity verified. Uplink secured.", 1.0f)
                        currentScreen = "DASHBOARD"
                    }
                )
            }
            "DASHBOARD" -> {
                // 🛡️ FIX: Remove the fully qualified prefix so the KMP compiler 
                // cleanly resolves this to the commonMain `expect` function.
                AgentDashboardScreen(apiClient = apiClient)
            }
        }
    }
}