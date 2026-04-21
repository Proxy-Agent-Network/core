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

import com.google.firebase.auth.FirebaseAuth
import com.pan.tactical.BuildConfig // 🛡️ Added BuildConfig
import com.pan.tactical.security.PlayIntegrityManager
import com.pan.tactical.security.StrongBoxManager
import com.pan.tactical.ui.WalletNetworkClient

@Composable
fun KeyCeremonyScreen(
    apiClient: WalletNetworkClient,
    onCeremonyComplete: () -> Unit
) {
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
                            // 🛡️ COMPILER-ENFORCED DEV BYPASS
                            val agentId = FirebaseAuth.getInstance().currentUser?.uid ?: run {
                                if (BuildConfig.IS_DEBUG) "DEV_AGENT_01" else throw Exception("Agent identity missing. Please log in.")
                            }

                            val strongBox = StrongBoxManager()
                            strongBox.generateHardwareKey()
                            val publicKeyB64 = strongBox.getPublicKeyBase64()

                            // 🛡️ COMPILER-ENFORCED DEV BYPASS: Skip calling the Play Store entirely in dev mode
                            val token = if (BuildConfig.IS_DEBUG) {
                                "DEV_MOCK_TOKEN_${System.currentTimeMillis()}"
                            } else {
                                val playIntegrity = PlayIntegrityManager(context)
                                playIntegrity.fetchAttestationToken(agentId, publicKeyB64)
                            }

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

                            errorMessage = when (e) {
                                is IllegalStateException -> "This device does not meet hardware security requirements for Vanguard operations."
                                else -> "Initialization failed. Please check your connection and try again."
                            }
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