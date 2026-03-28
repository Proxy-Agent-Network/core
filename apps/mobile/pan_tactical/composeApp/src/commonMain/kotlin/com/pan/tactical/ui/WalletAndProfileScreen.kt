package com.pan.tactical.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.foundation.clickable
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.Dialog
import kotlinx.coroutines.launch

import com.pan.tactical.AudioEngine

// 1. DATA MODELS (Now in commonMain so the UI can see them)
data class TransactionLog(
    val id: String,
    val date: String,
    val amount: String,
    val description: String,
    val evidenceUrls: List<String>? = null
)

data class WalletResponse(val balance: Double, val linkedCard: String? = null, val history: List<TransactionLog>)

// 2. THE INTERFACE (The contract the UI relies on)
interface WalletNetworkClient {
    suspend fun getWalletData(): WalletResponse?
    suspend fun linkDebitCard(cardNumber: String): Boolean
    suspend fun withdrawFunds(amount: Double): Boolean
    suspend fun triggerBackendDispatch(lat: Double, lon: Double, errorCode: String): Boolean
    suspend fun updateLocationTelemetry(lat: Double, lon: Double): Boolean
    suspend fun declineMission(taskId: String): Boolean

    suspend fun fetchActiveMissions(): List<com.pan.tactical.models.MissionData>
}

// --- KMP-FRIENDLY CURRENCY FORMATTER ---
fun Double.toCurrency(): String {
    val parts = this.toString().split(".")
    val whole = parts[0]
    val frac = if (parts.size > 1) parts[1].padEnd(2, '0').take(2) else "00"
    return "$$whole.$frac"
}

@Composable
fun WalletAndProfileScreen(
    apiClient: WalletNetworkClient, // 3. 🛠️ THE FIX: Require the interface, not the Android class
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

    // 🛠️ THE FIX: Dynamic Voice Initialization
    val osVoices = remember { audioEngine.getAvailableVoices() }
    var selectedVoice by remember { mutableStateOf(osVoices.firstOrNull()?.id ?: "") }

    // --- LIVE NETWORK STATE ---
    var isLoading by remember { mutableStateOf(true) }
    var balance by remember { mutableDoubleStateOf(0.00) }
    var linkedCard by remember { mutableStateOf<String?>(null) }
    var history by remember { mutableStateOf<List<TransactionLog>>(emptyList()) }

    var showLinkCardDialog by remember { mutableStateOf(false) }
    var cardNumber by remember { mutableStateOf("") }
    var isLinkingCard by remember { mutableStateOf(false) }
    var isWithdrawing by remember { mutableStateOf(false) }

    // --- FETCH WALLET DATA ON LOAD ---
    LaunchedEffect(Unit) {
        val walletData = apiClient.getWalletData()
        if (walletData != null) {
            balance = walletData.balance
            linkedCard = walletData.linkedCard
            history = walletData.history
        }
        isLoading = false
    }

    // --- LINK CARD DIALOG UI ---
    if (showLinkCardDialog) {
        Dialog(onDismissRequest = { if (!isLinkingCard) showLinkCardDialog = false }) {
            Surface(
                shape = RoundedCornerShape(12.dp),
                color = Color(0xFF1E1E1E),
                modifier = Modifier.fillMaxWidth().padding(16.dp)
            ) {
                Column(modifier = Modifier.padding(24.dp)) {
                    Text("LINK PAYOUT METHOD", color = Color.White, fontSize = 16.sp, fontWeight = FontWeight.Bold)
                    Text("Connect a debit card for instant USD transfers.", color = Color.Gray, fontSize = 12.sp, modifier = Modifier.padding(top = 8.dp, bottom = 16.dp))

                    OutlinedTextField(
                        value = cardNumber,
                        // 🛠️ THE FIX: Prevent invalid input lengths mechanically
                        onValueChange = { if (it.length <= 4 && it.all { c -> c.isDigit() }) cardNumber = it },
                        label = { Text("Card Number (Last 4)", color = Color.Gray, fontSize = 12.sp) },
                        // 🛠️ THE FIX: Prevent OS Keyboard Caching
                        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.NumberPassword),
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedBorderColor = Color(0xFF1976D2), unfocusedBorderColor = Color(0xFF333333),
                            focusedTextColor = Color.White, unfocusedTextColor = Color.White
                        ),
                        modifier = Modifier.fillMaxWidth(), singleLine = true
                    )

                    Spacer(modifier = Modifier.height(24.dp))

                    Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.End) {
                        TextButton(onClick = { showLinkCardDialog = false }, enabled = !isLinkingCard) {
                            Text("CANCEL", color = Color.Gray, fontWeight = FontWeight.Bold)
                        }
                        Button(
                            onClick = {
                                if (cardNumber.isNotBlank() && cardNumber.length == 4) {
                                    isLinkingCard = true
                                    coroutineScope.launch {
                                        val maskedCard = "Visa ending in $cardNumber"
                                        val success = apiClient.linkDebitCard(cardNumber = maskedCard)
                                        if (success) {
                                            linkedCard = maskedCard
                                            audioEngine.speak("Payout method secured.", voiceVolume)
                                        } else {
                                            audioEngine.speak("Network connection failed.", voiceVolume)
                                        }
                                        isLinkingCard = false
                                        showLinkCardDialog = false
                                    }
                                }
                            },
                            enabled = !isLinkingCard && cardNumber.length == 4,
                            colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF1976D2))
                        ) {
                            if (isLinkingCard) CircularProgressIndicator(modifier = Modifier.size(16.dp), color = Color.White, strokeWidth = 2.dp)
                            else Text("SAVE", color = Color.White, fontWeight = FontWeight.Bold)
                        }
                    }
                }
            }
        }
    }

    Column(modifier = Modifier.fillMaxSize().background(Color(0xFF121212))) {

        // 🛠️ THE FIX: Dynamic edge-to-edge support instead of hardcoded 70.dp
        Spacer(
            modifier = Modifier
                .windowInsetsTopHeight(WindowInsets.statusBars)
                .fillMaxWidth()
                .background(Color.Black)
        )

        Column(modifier = Modifier.fillMaxWidth().weight(1f).verticalScroll(rememberScrollState())) {

            Row(modifier = Modifier.fillMaxWidth().background(Color(0xFF1A1A1A)).padding(16.dp), verticalAlignment = Alignment.CenterVertically) {
                Box(
                    modifier = Modifier.size(40.dp).background(Color(0xFF333333), RoundedCornerShape(20.dp)).clip(RoundedCornerShape(20.dp)).clickable { onBack() },
                    contentAlignment = Alignment.Center
                ) { Text("◀", color = Color.White, fontSize = 18.sp) }

                Spacer(modifier = Modifier.width(16.dp))
                Text("AGENT LEDGER & PROFILE", color = Color.White, fontSize = 16.sp, fontWeight = FontWeight.Bold, letterSpacing = 1.sp)
            }

            Column(modifier = Modifier.fillMaxWidth().padding(24.dp), horizontalAlignment = Alignment.CenterHorizontally) {
                Text("AVAILABLE FIAT BALANCE", color = Color.Gray, fontSize = 12.sp, fontWeight = FontWeight.Bold, letterSpacing = 1.sp)

                if (isLoading) {
                    CircularProgressIndicator(color = Color(0xFF4CAF50), modifier = Modifier.padding(16.dp))
                } else {
                    Text(text = balance.toCurrency(), color = Color(0xFF4CAF50), fontSize = 64.sp, fontWeight = FontWeight.Black)
                }

                Spacer(modifier = Modifier.height(24.dp))

                if (linkedCard == null && !isLoading) {
                    Button(
                        onClick = { showLinkCardDialog = true },
                        colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF1976D2)),
                        modifier = Modifier.fillMaxWidth().height(56.dp), shape = RoundedCornerShape(8.dp)
                    ) { Text("LINK BANK DEBIT CARD", color = Color.White, fontWeight = FontWeight.Black, fontSize = 14.sp) }
                } else if (!isLoading) {
                    Button(
                        onClick = {
                            if (balance > 0) {
                                isWithdrawing = true
                                coroutineScope.launch {
                                    // 🛠️ THE FIX: Proper Idempotency/Refresh Flow
                                    val success = apiClient.withdrawFunds(amount = balance)
                                    if (success) {
                                        audioEngine.speak("Funds withdrawn to your bank.", voiceVolume)
                                    } else {
                                        audioEngine.speak("Withdrawal failed.", voiceVolume)
                                    }

                                    // Always re-sync with the server rather than trusting the local mutation
                                    apiClient.getWalletData()?.let {
                                        balance = it.balance
                                        history = it.history
                                    }
                                    isWithdrawing = false
                                }
                            }
                        },
                        colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF2E7D32)),
                        modifier = Modifier.fillMaxWidth().height(56.dp), shape = RoundedCornerShape(8.dp),
                        enabled = !isWithdrawing && balance > 0 // 🛠️ THE FIX: UI Guard
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
                        onValueChangeFinished = { audioEngine.speak("Level set.", voiceVolume) },
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
                        onValueChangeFinished = { audioEngine.speak("Beep.", alertVolume / 100f) },
                        valueRange = 0f..100f,
                        colors = SliderDefaults.colors(thumbColor = Color(0xFFF44336), activeTrackColor = Color(0xFFF44336))
                    )
                }

                Column(modifier = Modifier.fillMaxWidth().padding(top = 24.dp)) {
                    Text("TACTICAL VOICE PROFILE", color = Color.Gray, fontSize = 10.sp, fontWeight = FontWeight.Bold, modifier = Modifier.padding(horizontal = 24.dp, vertical = 8.dp))
                    Row(
                        modifier = Modifier.fillMaxWidth().horizontalScroll(rememberScrollState()).padding(horizontal = 24.dp),
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        osVoices.forEach { voiceProfile ->
                            val isSelected = selectedVoice == voiceProfile.id
                            Surface(
                                shape = RoundedCornerShape(4.dp),
                                color = if (isSelected) Color(0xFF00BCD4) else Color(0xFF333333),
                                modifier = Modifier.clickable {
                                    selectedVoice = voiceProfile.id
                                    audioEngine.setVoice(voiceProfile.id)
                                    audioEngine.speak("Voice profile ${voiceProfile.name} engaged.", voiceVolume)
                                }
                            ) {
                                Text(
                                    text = voiceProfile.name,
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
                Text("FIAT SETTLEMENT LEDGER", color = Color.LightGray, fontSize = 12.sp, fontWeight = FontWeight.Bold, modifier = Modifier.padding(horizontal = 24.dp, vertical = 8.dp))
                Column(modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 8.dp)) {
                    if (history.isEmpty() && !isLoading) {
                        Text("No transaction history available.", color = Color.Gray, fontSize = 14.sp, modifier = Modifier.padding(8.dp))
                    } else {
                        history.forEach { tx ->
                            // 🛠️ THE FIX: Removed dead click handler on transaction rows
                            Row(modifier = Modifier.fillMaxWidth().padding(vertical = 12.dp, horizontal = 8.dp), horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.CenterVertically) {
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
            }
            Spacer(modifier = Modifier.height(32.dp))
        }
    }
}