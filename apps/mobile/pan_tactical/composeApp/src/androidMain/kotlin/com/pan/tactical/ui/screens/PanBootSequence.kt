package com.pan.tactical.ui.screens

import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalUriHandler
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import org.jetbrains.compose.resources.painterResource
import pantactical.composeapp.generated.resources.Res
import pantactical.composeapp.generated.resources.pan_logo

import com.google.firebase.auth.FirebaseAuth
import com.pan.tactical.BuildConfig
import com.pan.tactical.network.PanWalletClient
import com.pan.tactical.security.PlayIntegrityManager
import com.pan.tactical.security.StrongBoxManager

@Composable
fun PanBootSequence(onBootComplete: () -> Unit) {
    val context = LocalContext.current
    val coroutineScope = rememberCoroutineScope()
    val uriHandler = LocalUriHandler.current

    var isInitializing by remember { mutableStateOf(false) }
    var hasError by remember { mutableStateOf(false) }

    val terminalLogs = remember { mutableStateListOf<String>() }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color(0xFF0A0C10))
            .padding(horizontal = 24.dp, vertical = 48.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.SpaceBetween
    ) {

        Column(horizontalAlignment = Alignment.CenterHorizontally) {
            Image(
                painter = painterResource(Res.drawable.pan_logo),
                contentDescription = "PAN Command",
                modifier = Modifier
                    .width(220.dp)
                    .height(80.dp),
                contentScale = ContentScale.Fit
            )
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = "SECURE AGENT TERMINAL v2.0",
                color = Color(0xFF00BCD4),
                fontSize = 10.sp,
                fontFamily = FontFamily.Monospace,
                letterSpacing = 2.sp,
                fontWeight = FontWeight.Bold
            )
        }

        Box(
            modifier = Modifier
                .fillMaxWidth()
                .weight(1f)
                .padding(vertical = 32.dp)
                .clip(RoundedCornerShape(8.dp))
                .background(Color.Black)
                .border(1.dp, Color(0xFF333333), RoundedCornerShape(8.dp))
                .padding(16.dp)
        ) {
            if (terminalLogs.isEmpty()) {
                Column(
                    modifier = Modifier.fillMaxSize(),
                    verticalArrangement = Arrangement.Center,
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Text(
                        text = "AWAITING INITIALIZATION",
                        color = Color(0xFF333333),
                        fontFamily = FontFamily.Monospace,
                        fontSize = 14.sp,
                        letterSpacing = 1.sp
                    )
                }
            } else {
                Column(
                    modifier = Modifier.fillMaxSize(),
                    verticalArrangement = Arrangement.Bottom,
                    horizontalAlignment = Alignment.Start
                ) {
                    terminalLogs.forEach { log ->
                        val textColor = when {
                            log.contains("[ERROR]") || log.contains("TERMINATED") || log.contains("DEBUG") -> Color.Red
                            log.contains("✅") -> Color(0xFF00FF00)
                            else -> Color(0xFF00FF00)
                        }
                        Text(
                            text = log,
                            color = textColor,
                            fontFamily = FontFamily.Monospace,
                            fontSize = 12.sp,
                            lineHeight = 16.sp
                        )
                        Spacer(modifier = Modifier.height(6.dp))
                    }
                }
            }
        }

        Column(horizontalAlignment = Alignment.CenterHorizontally) {

            Button(
                onClick = {
                    isInitializing = true
                    hasError = false
                    terminalLogs.clear()
                    terminalLogs.add("[SYSTEM] Booting PAN OS v2026.1.0...")

                    coroutineScope.launch {
                        try {
                            delay(400)
                            terminalLogs.add("[HW_LINK] Securing TPM Enclave...")
                            val strongBox = StrongBoxManager()

                            strongBox.generateHardwareKey()
                            val publicKeyB64 = strongBox.getPublicKeyBase64()

                            // 🛡️ COMPILER-ENFORCED DEV BYPASS
                            val agentId = FirebaseAuth.getInstance().currentUser?.uid ?: run {
                                if (BuildConfig.IS_DEBUG) "DEV_AGENT_01" else throw Exception("Agent identity missing. Please log in.")
                            }

                            delay(500)
                            terminalLogs.add("[ATTEST] Requesting Google Play Integrity Token...")

                            // 🛡️ COMPILER-ENFORCED DEV BYPASS: Skip calling the Play Store entirely in dev mode
                            val token = if (BuildConfig.IS_DEBUG) {
                                terminalLogs.add("[WARN] Play Store bypassed. Using Dev Mock Token.")
                                "DEV_MOCK_TOKEN_${System.currentTimeMillis()}"
                            } else {
                                val playIntegrity = PlayIntegrityManager(context)
                                playIntegrity.fetchAttestationToken(agentId, publicKeyB64)
                            }

                            delay(600)
                            terminalLogs.add("[NETWORK] Establishing encrypted Vanguard uplink...")
                            val walletClient = PanWalletClient()
                            val result = walletClient.registerHardwareKey(
                                agentId = agentId,
                                publicKeyB64 = publicKeyB64,
                                playIntegrityToken = token
                            )

                            if (result.isSuccess) {
                                val message = result.getOrNull()
                                delay(500)
                                terminalLogs.add("✅ SYSTEM ONLINE. $message")
                                delay(400)
                                isInitializing = false
                                onBootComplete()
                            } else {
                                val error = result.exceptionOrNull()
                                throw Exception("Backend verification failed: ${error?.message}")
                            }

                        } catch (e: Exception) {
                            isInitializing = false
                            hasError = true

                            // 🛡️ RESTORED: Removed ${e.message} to prevent UI leakage
                            val userMsg = when (e) {
                                is IllegalStateException -> "Device secure element unavailable."
                                else -> "Hardware attestation failed. Contact support."
                            }
                            terminalLogs.add("[ERROR] $userMsg")

                            if (e.toString().contains("ConnectException") ||
                                e.toString().contains("UnresolvedAddressException") ||
                                e.message?.contains("Network") == true) {
                                terminalLogs.add("🔍 DEBUG: Target Host was ${BuildConfig.PAN_API_BASE_URL}")
                            }

                            terminalLogs.add("🛑 BOOT SEQUENCE TERMINATED.")
                        }
                    }
                },
                enabled = !isInitializing,
                colors = ButtonDefaults.buttonColors(
                    containerColor = Color(0xFF00BCD4),
                    disabledContainerColor = Color(0xFF1E3538)
                ),
                shape = RoundedCornerShape(4.dp),
                modifier = Modifier
                    .fillMaxWidth()
                    .height(64.dp)
            ) {
                when {
                    isInitializing -> {
                        CircularProgressIndicator(modifier = Modifier.size(24.dp), color = Color.Black, strokeWidth = 3.dp)
                        Spacer(modifier = Modifier.width(12.dp))
                        Text(
                            text = "ATTESTING HARDWARE...",
                            color = Color.Black,
                            fontWeight = FontWeight.Black,
                            letterSpacing = 1.sp
                        )
                    }
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

            Spacer(modifier = Modifier.height(32.dp))

            Text(
                text = "WE WANT YOU!\nJOIN THE VANGUARD TODAY",
                color = Color(0xFF00BCD4),
                fontSize = 11.sp,
                fontWeight = FontWeight.Bold,
                letterSpacing = 1.sp,
                textAlign = TextAlign.Center,
                lineHeight = 16.sp,
                modifier = Modifier
                    .padding(16.dp)
                    .clickable {
                        uriHandler.openUri("https://www.proxyagent.network/enlist")
                    }
            )
        }
    }
}