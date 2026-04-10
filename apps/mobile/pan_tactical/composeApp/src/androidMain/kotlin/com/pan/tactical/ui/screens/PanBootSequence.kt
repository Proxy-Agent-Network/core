package com.pan.tactical.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

import com.google.firebase.auth.FirebaseAuth
import com.pan.tactical.network.PanWalletClient
import com.pan.tactical.security.PlayIntegrityManager
import com.pan.tactical.security.StrongBoxManager

// PanBootSequence.kt — androidMain
//
// The real Android boot gate. Three things must all succeed before onBootComplete()
// is ever called:
//   1. StrongBox key generation (TPM 2.0 hardware enclave)
//   2. Google Play Integrity attestation token acquisition
//   3. Server-side verification of that token via /api/v1/register-key
//
// If any step fails, the boot halts. The agent sees a RETRY UPLINK button.
// The app never reaches the dashboard on an unverified or rooted device.

@Composable
fun PanBootSequence(onBootComplete: () -> Unit) {
    val context = LocalContext.current
    val coroutineScope = rememberCoroutineScope()

    var isInitializing by remember { mutableStateOf(false) }
    var hasError by remember { mutableStateOf(false) }

    // 🛡️ FIX (Issue 2): mutableStateListOf is the idiomatic Compose pattern for
    // observable lists. Avoids creating a new list object on every append, which
    // was the previous `terminalLogs = terminalLogs + "..."` pattern.
    val terminalLogs = remember { mutableStateListOf<String>() }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color(0xFF000000))
            .padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Button(
            onClick = {
                isInitializing = true
                hasError = false
                terminalLogs.clear()
                terminalLogs.add("[SYSTEM] Booting PAN OS v2026.1.0...")

                coroutineScope.launch {
                    try {
                        // ── Step 1: StrongBox key generation ──────────────────────────────
                        delay(400)
                        terminalLogs.add("[HW_LINK] Securing TPM Enclave...")
                        val strongBox = StrongBoxManager()

                        // 🛡️ FIX (Issue 1 pre-req): generateHardwareKey() must run before
                        // getPublicKeyBase64(). On a fresh install the key alias doesn't exist
                        // yet — getPublicKeyBase64() throws SecurityException without this call.
                        // generateHardwareKey() is idempotent: no-ops if key already exists.
                        strongBox.generateHardwareKey()
                        val publicKeyB64 = strongBox.getPublicKeyBase64()

                        val agentId = FirebaseAuth.getInstance().currentUser?.uid
                            ?: throw Exception("Agent identity missing. Firebase authentication required.")

                        // ── Step 2: Play Integrity token acquisition ───────────────────────
                        delay(500)
                        terminalLogs.add("[ATTEST] Requesting Google Play Integrity Token...")
                        val playIntegrity = PlayIntegrityManager(context)
                        val token = playIntegrity.fetchAttestationToken(agentId, publicKeyB64)

                        delay(600)
                        terminalLogs.add("[ATTEST] Token acquired. Submitting for backend verification...")

                        // ── Step 3: Server-side verification ──────────────────────────────
                        // 🛡️ FIX (Issue 1): This is the critical gate. We send the token to
                        // /api/v1/register-key where the PAN backend verifies it against
                        // Google's Play Integrity API servers. onBootComplete() is ONLY called
                        // if the backend returns a success response. A rooted device, emulator,
                        // or tampered APK will fail Play Integrity — the backend rejects the
                        // token — and the boot halts here with an error. The agent cannot
                        // proceed to the dashboard on an unverified device.
                        //
                        // PanWalletClient is used here (not PanApiClient) because
                        // PanApiClient.registerHardwareKey() is a stub that always returns
                        // UnsupportedOperationException by design (split-brain guardrail).
                        delay(400)
                        terminalLogs.add("[NETWORK] Establishing encrypted Vanguard uplink...")
                        val walletClient = PanWalletClient()
                        val result = walletClient.registerHardwareKey(
                            agentId = agentId,
                            publicKeyB64 = publicKeyB64,
                            playIntegrityToken = token
                        )

                        // ── Gate: only proceed on verified success ─────────────────────────
                        result.fold(
                            onSuccess = { message ->
                                delay(500)
                                terminalLogs.add("✅ SYSTEM ONLINE. $message")
                                delay(400)
                                isInitializing = false
                                onBootComplete()
                            },
                            onFailure = { error ->
                                // Backend rejected the device. Halt. Do not boot.
                                throw Exception("Backend verification failed: ${error.message}")
                            }
                        )

                    } catch (e: Exception) {
                        isInitializing = false
                        hasError = true
                        terminalLogs.add("[ERROR] ${e.message}")
                        terminalLogs.add("🛑 BOOT SEQUENCE TERMINATED.")
                    }
                }
            },
            enabled = !isInitializing,
            colors = ButtonDefaults.buttonColors(
                containerColor = Color(0xFF00BCD4),
                disabledContainerColor = Color(0xFF333333)
            ),
            shape = RoundedCornerShape(8.dp),
            modifier = Modifier
                .fillMaxWidth(0.85f)
                .height(64.dp)
        ) {
            when {
                isInitializing -> Text(
                    text = "ATTESTING HARDWARE...",
                    color = Color.LightGray,
                    fontWeight = FontWeight.Bold,
                    letterSpacing = 1.sp
                )
                hasError -> Text(
                    text = "RETRY UPLINK",
                    color = Color.Black,
                    fontWeight = FontWeight.Black,
                    fontSize = 16.sp,
                    letterSpacing = 2.sp
                )
                else -> Text(
                    text = "INITIALIZE NODE",
                    color = Color.Black,
                    fontWeight = FontWeight.Black,
                    fontSize = 16.sp,
                    letterSpacing = 2.sp
                )
            }
        }

        Column(
            modifier = Modifier
                .fillMaxWidth()
                .height(200.dp)
                .padding(top = 20.dp),
            verticalArrangement = Arrangement.Top,
            horizontalAlignment = Alignment.Start
        ) {
            terminalLogs.forEach { log ->
                val textColor = when {
                    log.contains("[ERROR]") || log.contains("TERMINATED") -> Color.Red
                    log.contains("✅") -> Color(0xFF00FF00)
                    else -> Color(0xFF00FF00)
                }
                Text(
                    text = log,
                    color = textColor,
                    fontFamily = FontFamily.Monospace,
                    fontSize = 13.sp,
                    lineHeight = 18.sp
                )
                Spacer(modifier = Modifier.height(4.dp))
            }
        }
    }
}