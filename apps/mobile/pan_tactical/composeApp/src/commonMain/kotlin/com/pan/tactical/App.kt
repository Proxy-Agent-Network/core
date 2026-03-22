package com.pan.tactical

import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import com.pan.tactical.ui.LoginScreen

import androidx.compose.foundation.background
import androidx.compose.ui.Alignment

@Composable
fun App() {
    MaterialTheme {
        var currentScreen by remember { mutableStateOf("LOGIN") }
        var isLoading by remember { mutableStateOf(false) }
        var errorMsg by remember { mutableStateOf<String?>(null) }

        when (currentScreen) {
            "LOGIN" -> {
                LoginScreen(
                    isLoading = isLoading,
                    errorMessage = errorMsg,
                    onLoginClick = { email, password ->
                        isLoading = true
                        errorMsg = null
                        if (email == "agent@pan.com" && password == "password") {
                            isLoading = false

                            // --- INITIALIZE THE NATIVE AUDIO ENGINE ---
                            val audio = AudioEngine()
                            audio.playAlertBeep(100)
                            audio.speak("Uplink secured. Welcome to PAN Command.", 1.0f)
                            // ------------------------------------------

                            currentScreen = "DASHBOARD"
                        } else {
                            isLoading = false
                            errorMsg = "INVALID CREDENTIALS (try agent@pan.com / password)"
                        }
                    }
                )
            }
            "DASHBOARD" -> {
                // Call your full tactical dashboard!
                com.pan.tactical.ui.AgentDashboardScreen()
            }
        }
    }
}