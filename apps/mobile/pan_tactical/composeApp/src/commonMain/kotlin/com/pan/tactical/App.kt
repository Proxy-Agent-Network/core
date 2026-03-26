package com.pan.tactical

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlinx.coroutines.delay

import com.pan.tactical.ui.WalletNetworkClient

@Composable
fun App(apiClient: WalletNetworkClient) {
    MaterialTheme {
        var currentScreen by remember { mutableStateOf("ATTESTATION") }

        when (currentScreen) {
            "ATTESTATION" -> {
                HardwareAttestationBoot(
                    onUplinkSecured = {
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

@Composable
fun HardwareAttestationBoot(onUplinkSecured: () -> Unit) {
    var bootLog by remember { mutableStateOf("INITIALIZING SECURE ENCLAVE...") }

    // Simulate the Zero-Trust Hardware Handshake
    LaunchedEffect(Unit) {
        delay(800)
        bootLog = "READING TPM 2.0 FINGERPRINT..."
        delay(1200)
        bootLog = "GENERATING CRYPTOGRAPHIC SIGNATURE..."
        delay(1000)
        bootLog = "AUTHENTICATING WITH PAN COMMAND..."
        delay(1500)
        onUplinkSecured()
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color(0xFF050505))
            .padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text(
            text = "PAN TACTICAL",
            color = Color.White,
            fontSize = 32.sp,
            fontWeight = FontWeight.Black,
            letterSpacing = 2.sp
        )
        Spacer(modifier = Modifier.height(32.dp))

        CircularProgressIndicator(
            color = Color(0xFF00BCD4),
            strokeWidth = 3.dp,
            modifier = Modifier.size(48.dp)
        )

        Spacer(modifier = Modifier.height(32.dp))

        Text(
            text = bootLog,
            color = Color(0xFF00BCD4),
            fontSize = 12.sp,
            fontFamily = FontFamily.Monospace,
            letterSpacing = 1.sp
        )
    }
}