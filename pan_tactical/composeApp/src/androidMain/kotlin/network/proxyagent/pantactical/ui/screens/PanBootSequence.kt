package network.proxyagent.pantactical.ui.screens

import androidx.compose.foundation.Image
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
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import network.proxyagent.pantactical.R
import network.proxyagent.pantactical.security.PlayIntegrityManager
import network.proxyagent.pantactical.security.StrongBoxManager

@Composable
fun PanBootSequence(onBootComplete: () -> Unit) {
    val context = LocalContext.current
    val coroutineScope = rememberCoroutineScope()

    var isInitializing by remember { mutableStateOf(false) }
    var terminalLogs by remember { mutableStateOf(listOf<String>()) }
    var hasError by remember { mutableStateOf(false) }

    Column(
        modifier = Modifier.fillMaxSize().background(Color(0xFF000000)).padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Spacer(modifier = Modifier.weight(1f))

        Image(
            painter = painterResource(id = R.drawable.pan_logo),
            contentDescription = "PAN Logo",
            modifier = Modifier.fillMaxWidth(0.8f),
            contentScale = ContentScale.Fit
        )

        Spacer(modifier = Modifier.height(64.dp))

        Button(
            onClick = {
                isInitializing = true
                hasError = false
                terminalLogs = emptyList()

                coroutineScope.launch {
                    try {
                        terminalLogs = terminalLogs + "> Initiating secure uplink..."
                        delay(400)

                        terminalLogs = terminalLogs + "> Generating TPM 2.0 Hardware Key..."
                        val strongBox = StrongBoxManager()
                        strongBox.generateHardwareKey()
                        delay(400)

                        terminalLogs = terminalLogs + "> Verifying Google Play Integrity..."
                        val playIntegrity = PlayIntegrityManager(context)
                        val token = playIntegrity.fetchAttestationToken()
                        delay(400)

                        terminalLogs = terminalLogs + "> Handshake secured. Welcome, Agent."
                        delay(800)

                        onBootComplete()

                    } catch (e: Exception) {
                        isInitializing = false
                        hasError = true
                        terminalLogs = terminalLogs + "> [ERROR] ${e.localizedMessage ?: "Hardware Attestation Failed."}"
                        terminalLogs = terminalLogs + "> UPLINK TERMINATED."
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
                Spacer(modifier = Modifier.height(6.dp))
            }
        }

        Spacer(modifier = Modifier.weight(1f))
    }
}