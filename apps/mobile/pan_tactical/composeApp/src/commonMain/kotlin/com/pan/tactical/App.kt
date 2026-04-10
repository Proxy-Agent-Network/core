package com.pan.tactical

import androidx.compose.material3.MaterialTheme
import androidx.compose.runtime.*
import com.pan.tactical.ui.WalletNetworkClient

// App.kt lives in commonMain and is the root of the shared UI tree.
// It routes between the platform-specific boot screen (via expect/actual)
// and the shared AgentDashboardScreen.
//
// Flow: MainActivity → HardwarePermissionsGuard → App → BootSequence (actual) → AgentDashboardScreen

@Composable
fun App(apiClient: WalletNetworkClient) {
    MaterialTheme {
        var currentScreen by remember { mutableStateOf("BOOT") }

        when (currentScreen) {
            "BOOT" -> {
                BootSequence(
                    onBootComplete = {
                        val audio = AudioEngine()
                        audio.playAlertBeep(100)
                        audio.speak("Hardware identity verified. Uplink secured.", 1.0f)
                        currentScreen = "DASHBOARD"
                    }
                )
            }
            "DASHBOARD" -> {
                com.pan.tactical.ui.AgentDashboardScreen(apiClient = apiClient)
            }
        }
    }
}