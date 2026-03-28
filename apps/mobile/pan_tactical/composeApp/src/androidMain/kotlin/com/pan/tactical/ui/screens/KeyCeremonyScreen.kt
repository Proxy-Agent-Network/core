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

import com.google.firebase.auth.FirebaseAuth // 🟢 IMPORT FIREBASE
import com.pan.tactical.security.PlayIntegrityManager
import com.pan.tactical.security.StrongBoxManager
import com.pan.tactical.ui.WalletNetworkClient

@Composable
fun KeyCeremonyScreen(
    apiClient: WalletNetworkClient,
    // 🟢 THE FIX 3: Removed the hardcoded Vanguard-01 default parameter
    onCeremonyComplete: () -> Unit
) {
    // --- STATE MANAGEMENT ---
    var isProcessing by remember { mutableStateOf(false) }
    var statusText by remember { mutableStateOf("INITIALIZE NODE") }
    var errorMessage by remember { mutableStateOf<String?>(null) }

    val coroutineScope = rememberCoroutineScope()
    val context = LocalContext.current

    LaunchedEffect(errorMessage) {
        if (errorMessage != null) {
            statusText = "RETRY INITIALIZATION"
        }
    }

    // --- UI LAYOUT ---
    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color(0xFF121212))
            .systemBarsPadding()
            .padding(32.dp),
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
        Text(
            text = "VANGUARD SECURE UPLINK",
            color = Color.Gray,
            fontSize = 12.sp,
            letterSpacing = 1.sp,
            modifier = Modifier.padding(bottom = 64.dp)
        )

        // 2. The Action Area
        if (isProcessing) {
            CircularProgressIndicator(color = Color(0xFFFF9800))
            Spacer(modifier = Modifier.height(16.dp))
            Text(text = "ATTESTING HARDWARE...", color = Color.Gray, fontSize = 14.sp)
        } else {
            Button(
                onClick = {
                    isProcessing = true
                    errorMessage = null

                    coroutineScope.launch {
                        try {
                            // 🟢 THE FIX 3: Strict Identity Enforcement
                            val agentId = FirebaseAuth.getInstance().currentUser?.uid
                                ?: throw Exception("Agent identity missing. Please log in.")

                            // Step A: Generate the TPM 2.0 Key
                            val strongBox = StrongBoxManager()
                            strongBox.generateHardwareKey()

                            // Step B: Extract the Public Key Certificate
                            val publicKeyB64 = strongBox.getPublicKeyBase64()

                            // Step C: Verify device integrity with Google
                            val playIntegrity = PlayIntegrityManager(context)
                            val token = playIntegrity.fetchAttestationToken()

                            // 🟢 THE FIX 2: Transmit the Google Play token to the PAN Backend
                            val result = apiClient.registerHardwareKey(agentId, publicKeyB64, token)

                            result.onSuccess {
                                isProcessing = false
                                onCeremonyComplete()
                            }.onFailure { error ->
                                isProcessing = false
                                errorMessage = error.message ?: "Failed to bind hardware key to backend."
                            }

                        } catch (e: Exception) {
                            isProcessing = false
                            errorMessage = e.localizedMessage ?: "Hardware Attestation Failed."
                        }
                    }
                },
                modifier = Modifier
                    .fillMaxWidth()
                    .height(56.dp),
                colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF2E7D32))
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