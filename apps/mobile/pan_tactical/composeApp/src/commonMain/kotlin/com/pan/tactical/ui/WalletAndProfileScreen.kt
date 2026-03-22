package com.pan.tactical.ui

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import coil3.compose.AsyncImage
import kotlinx.coroutines.launch
import kotlinx.coroutines.delay

import com.pan.tactical.network.PythonNetworkBridge
import com.pan.tactical.AudioEngine

// --- KMP-FRIENDLY DATA MODELS ---
data class TransactionLog(
    val id: String,
    val date: String,
    val amount: String,
    val description: String,
    val evidenceUrls: List<String>? = null
)

// --- KMP-FRIENDLY CURRENCY FORMATTER ---
fun Double.toCurrency(): String {
    val parts = this.toString().split(".")
    val whole = parts[0]
    val frac = if (parts.size > 1) parts[1].padEnd(2, '0').take(2) else "00"
    return "$$whole.$frac"
}

@Composable
fun WalletAndProfileScreen(
    onBack: () -> Unit,
    navPreference: String,
    onNavPrefChange: (String) -> Unit,
    audioEngine: AudioEngine,
    voiceVolume: Float,
    onVoiceVolumeChange: (Float) -> Unit,
    alertVolume: Int,
    onAlertVolumeChange: (Int) -> Unit
) {
    val coroutineScope = rememberCoroutineScope()

    var firstName by remember { mutableStateOf("Proxy") }
    var callsign by remember { mutableStateOf("Vanguard-01") }

    // --- RESTORED: Voice Profile State ---
    var selectedVoice by remember { mutableStateOf("ALPHA") }

    var balance by remember { mutableDoubleStateOf(1450.00) }
    var linkedCard by remember { mutableStateOf<String?>("Visa ending in 4242") }

    var showLinkCardDialog by remember { mutableStateOf(false) }
    var cardNumber by remember { mutableStateOf("") }
    var expMonth by remember { mutableStateOf("") }
    var expYear by remember { mutableStateOf("") }
    var cvv by remember { mutableStateOf("") }
    var zipCode by remember { mutableStateOf("") }
    var monthExpanded by remember { mutableStateOf(false) }
    var yearExpanded by remember { mutableStateOf(false) }
    var isLinkingCard by remember { mutableStateOf(false) }
    var isWithdrawing by remember { mutableStateOf(false) }

    var selectedTransaction by remember { mutableStateOf<TransactionLog?>(null) }
    var enlargedImageUrl by remember { mutableStateOf<String?>(null) }

    val history = remember {
        listOf(
            TransactionLog("tx_001", "Today", "+$75.00", "Smart Contract Payout", null),
            TransactionLog("wd_002", "Yesterday", "-$500.00", "ACH Bank Transfer", null)
        )
    }

    Column(modifier = Modifier.fillMaxSize().background(Color(0xFF121212))) {

        Box(
            modifier = Modifier
                .fillMaxWidth()
                .height(70.dp)
                .background(Color(0xFF000000))
        )

        Column(
            modifier = Modifier
                .fillMaxWidth()
                .weight(1f)
                .verticalScroll(rememberScrollState())
        ) {

            Row(
                modifier = Modifier.fillMaxWidth().background(Color(0xFF1A1A1A)).padding(16.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Box(
                    modifier = Modifier
                        .size(40.dp)
                        .background(Color(0xFF333333), RoundedCornerShape(20.dp))
                        .clip(RoundedCornerShape(20.dp))
                        .clickable { onBack() },
                    contentAlignment = Alignment.Center
                ) { Text("◀", color = Color.White, fontSize = 18.sp) }

                Spacer(modifier = Modifier.width(16.dp))
                Text("AGENT LEDGER & PROFILE", color = Color.White, fontSize = 16.sp, fontWeight = FontWeight.Bold, letterSpacing = 1.sp)
            }

            Column(modifier = Modifier.fillMaxWidth().padding(24.dp), horizontalAlignment = Alignment.CenterHorizontally) {
                Text("AVAILABLE ESCROW BALANCE", color = Color.Gray, fontSize = 12.sp, fontWeight = FontWeight.Bold, letterSpacing = 1.sp)
                Text(text = balance.toCurrency(), color = Color(0xFF4CAF50), fontSize = 64.sp, fontWeight = FontWeight.Black)
                Spacer(modifier = Modifier.height(24.dp))

                if (linkedCard == null) {
                    Button(
                        onClick = { showLinkCardDialog = true },
                        colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF1976D2)),
                        modifier = Modifier.fillMaxWidth().height(56.dp), shape = RoundedCornerShape(8.dp)
                    ) { Text("LINK BANK DEBIT CARD", color = Color.White, fontWeight = FontWeight.Black, fontSize = 14.sp) }
                } else {
                    Button(
                        onClick = {
                            if (balance > 0) {
                                isWithdrawing = true
                                coroutineScope.launch {
                                    delay(1500)
                                    balance = 0.0
                                    audioEngine.speak("Funds withdrawn.", voiceVolume)
                                    isWithdrawing = false
                                }
                            }
                        },
                        colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF2E7D32)),
                        modifier = Modifier.fillMaxWidth().height(56.dp), shape = RoundedCornerShape(8.dp), enabled = !isWithdrawing
                    ) {
                        if (isWithdrawing) CircularProgressIndicator(modifier = Modifier.size(24.dp), color = Color.White, strokeWidth = 2.dp)
                        else Text("WITHDRAW TO ${linkedCard?.uppercase()}", color = Color.White, fontWeight = FontWeight.Black)
                    }
                    Spacer(modifier = Modifier.height(12.dp))
                    TextButton(onClick = { showLinkCardDialog = true }) { Text("UPDATE LINKED CARD", color = Color.Gray, fontSize = 12.sp, fontWeight = FontWeight.Bold) }
                }
            }

            Column(modifier = Modifier.fillMaxWidth().background(Color(0xFF1A1A1A)).padding(vertical = 16.dp)) {
                Text("MISSION PREFERENCES", color = Color.LightGray, fontSize = 12.sp, fontWeight = FontWeight.Bold, letterSpacing = 1.sp, modifier = Modifier.padding(horizontal = 24.dp, vertical = 8.dp))
                Row(modifier = Modifier.fillMaxWidth().padding(horizontal = 24.dp), horizontalArrangement = Arrangement.spacedBy(16.dp)) {
                    Button(
                        onClick = { onNavPrefChange("GOOGLE") },
                        colors = ButtonDefaults.buttonColors(containerColor = if (navPreference == "GOOGLE") Color(0xFF1976D2) else Color(0xFF333333)),
                        modifier = Modifier.weight(1f).height(48.dp), shape = RoundedCornerShape(8.dp)
                    ) { Text("NATIVE MAPS", color = Color.White, fontSize = 12.sp, fontWeight = FontWeight.Bold) }

                    Button(
                        onClick = { onNavPrefChange("TACTICAL") },
                        colors = ButtonDefaults.buttonColors(containerColor = if (navPreference == "TACTICAL") Color(0xFF00BCD4) else Color(0xFF333333)),
                        modifier = Modifier.weight(1f).height(48.dp), shape = RoundedCornerShape(8.dp)
                    ) { Text("PAN TACTICAL", color = if (navPreference == "TACTICAL") Color.Black else Color.White, fontSize = 12.sp, fontWeight = FontWeight.Bold) }
                }

                Spacer(modifier = Modifier.height(24.dp))

                Column(modifier = Modifier.fillMaxWidth().padding(horizontal = 24.dp)) {
                    Text("AGENT IDENTITY ALIAS", color = Color(0xFF00BCD4), fontSize = 12.sp, fontWeight = FontWeight.Black, letterSpacing = 1.sp, modifier = Modifier.padding(bottom = 8.dp))

                    OutlinedTextField(
                        value = firstName,
                        onValueChange = { firstName = it },
                        label = { Text("LEGAL FIRST NAME", color = Color.Gray, fontSize = 10.sp) },
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedBorderColor = Color(0xFF00BCD4), unfocusedBorderColor = Color(0xFF333333),
                            focusedTextColor = Color.White, unfocusedTextColor = Color.White
                        ),
                        modifier = Modifier.fillMaxWidth().padding(bottom = 8.dp), singleLine = true
                    )

                    OutlinedTextField(
                        value = callsign,
                        onValueChange = { callsign = it },
                        label = { Text("TACTICAL CALLSIGN", color = Color.Gray, fontSize = 10.sp) },
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedBorderColor = Color(0xFF00BCD4), unfocusedBorderColor = Color(0xFF333333),
                            focusedTextColor = Color.White, unfocusedTextColor = Color.White
                        ),
                        modifier = Modifier.fillMaxWidth().padding(bottom = 16.dp), singleLine = true
                    )

                    Button(
                        onClick = {
                            val identity = if (callsign.isNotBlank()) callsign else firstName
                            audioEngine.speak("The command is now yours, $identity.", voiceVolume)
                        },
                        colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF333333)),
                        modifier = Modifier.fillMaxWidth().height(48.dp), shape = RoundedCornerShape(8.dp)
                    ) { Text("🔊 TEST AUDIO ALIAS", color = Color.White, fontSize = 12.sp, fontWeight = FontWeight.Bold) }
                }

                Spacer(modifier = Modifier.height(24.dp))

                Text("TACTICAL AUDIO MIXER", color = Color.Gray, fontSize = 10.sp, fontWeight = FontWeight.Bold, modifier = Modifier.padding(start = 24.dp, end = 24.dp, bottom = 8.dp))

                Column(modifier = Modifier.fillMaxWidth().padding(horizontal = 24.dp)) {
                    Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                        Text("J.A.R.V.I.S. Dispatch Voice", color = Color.White, fontSize = 12.sp, fontWeight = FontWeight.Medium)
                        Text("${(voiceVolume * 100).toInt()}%", color = Color(0xFF00BCD4), fontSize = 12.sp, fontWeight = FontWeight.Bold)
                    }
                    Slider(
                        value = voiceVolume,
                        onValueChange = { onVoiceVolumeChange(it) },
                        onValueChangeFinished = {
                            // --- RESTORED: Speaks when slider is released ---
                            audioEngine.speak("Level set.", voiceVolume)
                        },
                        valueRange = 0f..1f,
                        colors = SliderDefaults.colors(thumbColor = Color(0xFF00BCD4), activeTrackColor = Color(0xFF00BCD4))
                    )

                    Spacer(modifier = Modifier.height(8.dp))

                    Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                        Text("Emergency Alarms & Beeps", color = Color.White, fontSize = 12.sp, fontWeight = FontWeight.Medium)
                        Text("${alertVolume}%", color = Color(0xFFF44336), fontSize = 12.sp, fontWeight = FontWeight.Bold)
                    }
                    Slider(
                        value = alertVolume.toFloat(),
                        onValueChange = { onAlertVolumeChange(it.toInt()) },
                        onValueChangeFinished = {
                            // --- RESTORED: Uses audio engine for a beep fallback when slider is released ---
                            audioEngine.speak("Beep.", alertVolume / 100f)
                        },
                        valueRange = 0f..100f,
                        colors = SliderDefaults.colors(thumbColor = Color(0xFFF44336), activeTrackColor = Color(0xFFF44336))
                    )
                }

                // --- UPGRADED: Dynamic OS Voice Profiles ---
                Column(modifier = Modifier.fillMaxWidth().padding(top = 24.dp)) {
                    Text("TACTICAL VOICE PROFILE", color = Color.Gray, fontSize = 10.sp, fontWeight = FontWeight.Bold, modifier = Modifier.padding(horizontal = 24.dp, vertical = 8.dp))
                    Row(
                        modifier = Modifier.fillMaxWidth().horizontalScroll(rememberScrollState()).padding(horizontal = 24.dp),
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        // Ask the native OS what voices it actually has!
                        val osVoices = remember { audioEngine.getAvailableVoices() }

                        osVoices.forEach { voiceProfile ->
                            val isSelected = selectedVoice == voiceProfile.id
                            Surface(
                                shape = RoundedCornerShape(4.dp),
                                color = if (isSelected) Color(0xFF00BCD4) else Color(0xFF333333),
                                modifier = Modifier.clickable {
                                    selectedVoice = voiceProfile.id
                                    audioEngine.setVoice(voiceProfile.id) // Engage the native chip!
                                    audioEngine.speak("Voice profile ${voiceProfile.name} engaged.", voiceVolume)
                                }
                            ) {
                                Text(
                                    text = voiceProfile.name, // Will display "SAMANTHA", "DANIEL", etc. on iOS!
                                    color = if(isSelected) Color.Black else Color.White,
                                    fontSize = 12.sp,
                                    fontWeight = FontWeight.Bold,
                                    modifier = Modifier.padding(horizontal = 16.dp, vertical = 10.dp)
                                )
                            }
                        }
                    }
                }
            }

            Column(modifier = Modifier.fillMaxWidth().background(Color(0xFF1E1E1E)).padding(top = 16.dp)) {
                Text("CRYPTOGRAPHIC TRANSACTION LEDGER", color = Color.LightGray, fontSize = 12.sp, fontWeight = FontWeight.Bold, modifier = Modifier.padding(horizontal = 24.dp, vertical = 8.dp))
                Column(modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 8.dp)) {
                    history.forEach { tx ->
                        Row(modifier = Modifier.fillMaxWidth().clickable { selectedTransaction = tx }.padding(vertical = 12.dp, horizontal = 8.dp), horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.CenterVertically) {
                            Column(modifier = Modifier.weight(1f)) {
                                Text(tx.date, color = Color.Gray, fontSize = 12.sp)
                                Spacer(modifier = Modifier.height(4.dp))
                                Text(tx.description, color = Color.White, fontSize = 14.sp, fontWeight = FontWeight.Medium)
                                Text("TXN ID: ${tx.id}", color = Color.DarkGray, fontSize = 10.sp, fontFamily = FontFamily.Monospace)
                            }
                            Text(tx.amount, color = if (tx.amount.startsWith("-")) Color(0xFFF44336) else Color(0xFF4CAF50), fontSize = 18.sp, fontWeight = FontWeight.Black)
                        }
                        HorizontalDivider(color = Color(0xFF333333), thickness = 1.dp)
                    }
                }
            }
            Spacer(modifier = Modifier.height(32.dp))
        }
    }
}