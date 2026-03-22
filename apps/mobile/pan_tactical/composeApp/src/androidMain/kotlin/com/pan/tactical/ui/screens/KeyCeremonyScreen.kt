package com.pan.tactical.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlinx.coroutines.launch
import com.pan.tactical.security.PlayIntegrityManager
import com.pan.tactical.security.StrongBoxManager

@Composable
fun KeyCeremonyScreen(
    onCeremonyComplete: () -> Unit // A callback to tell the app to move to the Dashboard
) {
    // --- STATE MANAGEMENT ---
    // These variables dictate what the UI looks like. When they change, Compose redraws the screen.
    var isProcessing by remember { mutableStateOf(false) }
    var statusText by remember { mutableStateOf("INITIALIZE NODE") }
    var errorMessage by remember { mutableStateOf<String?>(null) }

    // We need a coroutine scope to run our heavy security checks in the background
    val coroutineScope = rememberCoroutineScope()
    // We need the Context to pass to PlayIntegrityManager
    val context = LocalContext.current

    // --- UI LAYOUT ---
    // A Column stacks items vertically. We give it a tactical dark background.
    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color(0xFF121212))
            .systemBarsPadding()
            .padding(32.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {

        // 1. The Branding (We will replace this text with Final_PAN_Logo.png later)
        Text(
            text = "PAN TACTICAL",
            color = Color.White,
            fontSize = 32.sp,
            fontWeight = FontWeight.Black,
            letterSpacing = 2.sp
        )
        Text(
            text = "VANGUARD SECURE UPLINK",
            color = Color.Gray,
            fontSize = 12.sp,
            letterSpacing = 1.sp,
            modifier = Modifier.padding(bottom = 64.dp)
        )

        // 2. The Action Area
        if (isProcessing) {
            // Show a loading spinner while the hardware generates the key
            CircularProgressIndicator(color = Color(0xFFFF9800)) // Warning Orange
            Spacer(modifier = Modifier.height(16.dp))
            Text(text = "ATTESTING HARDWARE...", color = Color.Gray, fontSize = 14.sp)
        } else {
            // Show the main action button
            Button(
                onClick = {
                    // Start the loading state
                    isProcessing = true
                    errorMessage = null

                    // Launch background coroutine
                    coroutineScope.launch {
                        try {
                            // Step A: Generate the TPM 2.0 Key
                            val strongBox = StrongBoxManager()
                            strongBox.generateHardwareKey()

                            // Step B: Verify device integrity with Google
                            val playIntegrity = PlayIntegrityManager(context)
                            // Note: In local dev, this might fail if the emulator isn't configured for Play Services.
                            // We wrap it in a try/catch so you can see how the UI handles the error.
                            val token = playIntegrity.fetchAttestationToken()

                            // If we make it here without throwing an exception, the ceremony is successful!
                            isProcessing = false
                            onCeremonyComplete()

                        } catch (e: Exception) {
                            // If anything fails (no TPM, rooted phone, etc.), catch it and show the error.
                            isProcessing = false
                            errorMessage = e.localizedMessage ?: "Hardware Attestation Failed."
                        }
                    }
                },
                modifier = Modifier
                    .fillMaxWidth()
                    .height(56.dp),
                colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF2E7D32)) // Tactical Green
            ) {
                Text(
                    text = statusText,
                    color = Color.White,
                    fontWeight = FontWeight.Bold,
                    letterSpacing = 1.sp
                )
            }
        }

        // 3. Error Display
        errorMessage?.let { error ->
            Spacer(modifier = Modifier.height(24.dp))
            Text(
                text = "ERROR: $error",
                color = Color.Red,
                fontSize = 14.sp,
                textAlign = TextAlign.Center,
                fontWeight = FontWeight.Medium
            )
        }
    }
}