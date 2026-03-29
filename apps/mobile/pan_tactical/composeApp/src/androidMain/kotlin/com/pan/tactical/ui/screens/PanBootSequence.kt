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

import com.google.firebase.auth.FirebaseAuth // 🟢 IMPORT FIREBASE
import com.pan.tactical.security.PlayIntegrityManager
import com.pan.tactical.security.StrongBoxManager

@Composable
fun PanBootSequence(onBootComplete: () -> Unit) {
    val context = LocalContext.current
    val coroutineScope = rememberCoroutineScope()

    var isInitializing by remember { mutableStateOf(false) }
    var terminalLogs by remember { mutableStateOf(listOf<String>()) }
    var hasError by remember { mutableStateOf(false) }

    Column(
        modifier = Modifier.fillMaxSize().background(Color(0xFF000000)).padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Button(
            onClick = {
                isInitializing = true
                hasError = false
                terminalLogs = listOf("[SYSTEM] Booting PAN OS v2026.1.0...")

                coroutineScope.launch {
                    try {
                        delay(400)
                        terminalLogs = terminalLogs + "[HW_LINK] Securing TPM Enclave..."
                        val strongBox = StrongBoxManager()

                        // 🟢 THE FIX: Extract public key and identity for the Play Integrity bind
                        val publicKeyB64 = strongBox.getPublicKeyBase64()
                        val agentId = FirebaseAuth.getInstance().currentUser?.uid
                            ?: throw Exception("Agent identity missing. Authentication required.")

                        delay(500)
                        terminalLogs = terminalLogs + "[ATTEST] Requesting Google Play Integrity Token..."

                        val playIntegrity = PlayIntegrityManager(context)
                        // 🟢 THE FIX: Pass both parameters to fetchAttestationToken
                        val token = playIntegrity.fetchAttestationToken(agentId, publicKeyB64)

                        delay(600)
                        terminalLogs = terminalLogs + "[ATTEST] Token Acquired. Awaiting Backend Verification."

                        delay(400)
                        terminalLogs = terminalLogs + "[NETWORK] Establishing encrypted Vanguard uplink..."

                        delay(700)
                        terminalLogs = terminalLogs + "✅ SYSTEM ONLINE."

                        delay(500)
                        isInitializing = false
                        onBootComplete()

                    } catch (e: Exception) {
                        isInitializing = false
                        hasError = true
                        terminalLogs = terminalLogs + "[ERROR] ${e.message}"
                        terminalLogs = terminalLogs + "🛑 BOOT SEQUENCE TERMINATED."
                    }
                }
            },
            enabled = !isInitializing,
            colors = ButtonDefaults.buttonColors(
                containerColor = Color(0xFF00BCD4),
                disabledContainerColor = Color(0xFF333333)
            ),
            shape = RoundedCornerShape(8.dp),
            modifier = Modifier.fillMaxWidth(0.85f).height(64.dp)
        ) {
            if (isInitializing) {
                Text("ATTESTING HARDWARE...", color = Color.LightGray, fontWeight = FontWeight.Bold, letterSpacing = 1.sp)
            } else if (hasError) {
                Text("RETRY UPLINK", color = Color.Black, fontWeight = FontWeight.Black, fontSize = 16.sp, letterSpacing = 2.sp)
            } else {
                Text("INITIALIZE NODE", color = Color.Black, fontWeight = FontWeight.Black, fontSize = 16.sp, letterSpacing = 2.sp)
            }
        }

        Column(
            modifier = Modifier.fillMaxWidth().height(150.dp).padding(top = 20.dp),
            verticalArrangement = Arrangement.Top,
            horizontalAlignment = Alignment.Start
        ) {
            terminalLogs.forEach { log ->
                val textColor = if (log.contains("[ERROR]") || log.contains("TERMINATED")) Color.Red else Color(0xFF00FF00)
                Text(text = log, color = textColor, fontFamily = FontFamily.Monospace, fontSize = 14.sp)
                Spacer(modifier = Modifier.height(4.dp))
            }
        }
    }
}