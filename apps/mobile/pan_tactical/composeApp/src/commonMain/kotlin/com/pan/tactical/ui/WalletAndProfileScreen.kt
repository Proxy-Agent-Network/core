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
import androidx.compose.runtime.saveable.rememberSaveable
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
import kotlinx.serialization.Serializable

import com.pan.tactical.AudioEngine
import com.pan.tactical.ui.theme.PanColors
import com.pan.tactical.ui.components.AgentRankCard
import kotlin.math.abs
import kotlin.math.roundToInt

// 1. DATA MODELS (Now in commonMain so the UI can see them)
@Serializable
data class TransactionLog(
    val id: String,
    val date: String,
    val amount: String,
    val description: String,
    val evidenceUrls: List<String>? = null
)

@Serializable
data class WalletResponse(
    val balance: Double,
    val linkedCard: String? = null,
    val history: List<TransactionLog>,
    val missionsCompleted: Int = 0,
    val vanguardTrustScore: Double = 100.0
)

// 2. THE INTERFACE (The contract the UI relies on)
interface WalletNetworkClient {
    suspend fun getWalletData(): WalletResponse?

    // 🛡️ FIXED: Renamed parameter to explicitly indicate this is a UI display label, not a secure token
    suspend fun linkDebitCard(maskedCardLabel: String): Result<String>

    suspend fun withdrawFunds(amount: Double): Result<String>
    suspend fun triggerBackendDispatch(lat: Double, lon: Double, errorCode: String): Boolean
    suspend fun updateLocationTelemetry(lat: Double, lon: Double): Boolean
    suspend fun declineMission(taskId: String): Boolean
    suspend fun fetchActiveMissions(): List<com.pan.tactical.models.MissionData>
    suspend fun completeMission(taskId: String, evidenceUrls: List<String> = emptyList()): Boolean
    suspend fun registerHardwareKey(agentId: String, publicKeyB64: String, playIntegrityToken: String): Result<String>
    suspend fun acknowledgeMission(taskId: String): Boolean
}

// --- KMP-FRIENDLY CURRENCY FORMATTER ---
fun Double.toCurrency(): String {
    val isNegative = this < 0
    val absoluteValue = abs(this)
    val parts = absoluteValue.toString().split(".")
    val whole = parts[0]
    val frac = if (parts.size > 1) parts[1].padEnd(2, '0').take(2) else "00"
    return if (isNegative) "-$$whole.$frac" else "$$whole.$frac"
}

@Composable
fun WalletAndProfileScreen(
    apiClient: WalletNetworkClient,
    onBack: () -> Unit,
    onNavigateToStore: (balance: Double, missions: Int) -> Unit,
    navPreference: String,
    onNavPrefChange: (String) -> Unit,
    audioEngine: AudioEngine,
    voiceVolume: Float,
    onVoiceVolumeChange: (Float) -> Unit,
    alertVolume: Int,
    onAlertVolumeChange: (Int) -> Unit
) {
    val coroutineScope = rememberCoroutineScope()
    val snackbarHostState = remember { SnackbarHostState() }

    // 🛡️ FIXED: Use rememberSaveable so text inputs survive configuration changes / process death
    var firstName by rememberSaveable { mutableStateOf("Proxy") }
    var callsign by rememberSaveable { mutableStateOf("Vanguard-01") }

    val osVoices = remember { audioEngine.getAvailableVoices() }
    var selectedVoice by remember { mutableStateOf(osVoices.firstOrNull()?.id ?: "") }

    // --- LIVE NETWORK STATE ---
    var isLoading by remember { mutableStateOf(true) }
    var balance by remember { mutableDoubleStateOf(0.00) }
    var linkedCard by remember { mutableStateOf<String?>(null) }
    var history by remember { mutableStateOf<List<TransactionLog>>(emptyList()) }
    var missionsCompleted by remember { mutableIntStateOf(0) }
    var vtsScore by remember { mutableDoubleStateOf(100.0) }

    var showLinkCardDialog by remember { mutableStateOf(false) }
    var cardNumber by rememberSaveable { mutableStateOf("") } // 🛡️ FIXED: Survive rotation
    var isLinkingCard by remember { mutableStateOf(false) }
    var isWithdrawing by remember { mutableStateOf(false) }

    LaunchedEffect(Unit) {
        isLoading = true
        try {
            val walletData = apiClient.getWalletData()
            if (walletData != null) {
                balance = walletData.balance
                linkedCard = walletData.linkedCard
                history = walletData.history
                missionsCompleted = walletData.missionsCompleted
                vtsScore = walletData.vanguardTrustScore
            }
        } catch (e: Exception) {
            snackbarHostState.showSnackbar("ERROR: Failed to load wallet data.")
        } finally {
            isLoading = false
        }
    }

    if (showLinkCardDialog) {
        Dialog(onDismissRequest = {
            if (!isLinkingCard) {
                showLinkCardDialog = false
                cardNumber = ""
            }
        }) {
            Surface(
                shape = RoundedCornerShape(12.dp),
                color = PanColors.CardBackground,
                modifier = Modifier.fillMaxWidth().padding(16.dp)
            ) {
                Column(modifier = Modifier.padding(24.dp)) {
                    Text("LINK PAYOUT METHOD", color = Color.White, fontSize = 16.sp, fontWeight = FontWeight.Bold)
                    Text("Connect a debit card for instant USD transfers.", color = Color.Gray, fontSize = 12.sp, modifier = Modifier.padding(top = 8.dp, bottom = 16.dp))

                    OutlinedTextField(
                        value = cardNumber,
                        onValueChange = { if (it.length <= 4 && it.all { c -> c.isDigit() }) cardNumber = it },
                        label = { Text("Card Number (Last 4)", color = Color.Gray, fontSize = 12.sp) },
                        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.NumberPassword),
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedBorderColor = PanColors.CyanAccent, unfocusedBorderColor = PanColors.ButtonSecondary,
                            focusedTextColor = Color.White, unfocusedTextColor = Color.White
                        ),
                        modifier = Modifier.fillMaxWidth(), singleLine = true
                    )

                    Spacer(modifier = Modifier.height(24.dp))

                    Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.End) {
                        TextButton(
                            onClick = {
                                showLinkCardDialog = false
                                cardNumber = ""
                            },
                            enabled = !isLinkingCard
                        ) {
                            Text("CANCEL", color = Color.Gray, fontWeight = FontWeight.Bold)
                        }
                        Button(
                            onClick = {
                                if (cardNumber.isNotBlank() && cardNumber.length == 4) {
                                    isLinkingCard = true
                                    coroutineScope.launch {
                                        try {
                                            val maskedCard = "Visa ending in $cardNumber"

                                            val result = apiClient.linkDebitCard(maskedCardLabel = maskedCard)

                                            result.onSuccess {
                                                linkedCard = maskedCard
                                                audioEngine.speak("Payout method secured.", voiceVolume)
                                                showLinkCardDialog = false
                                                cardNumber = ""
                                            }.onFailure { error ->
                                                audioEngine.speak("Network connection failed.", voiceVolume)
                                                snackbarHostState.showSnackbar("ERROR: ${error.message}")
                                            }
                                        } finally {
                                            // 🛡️ FIXED: Ensure loading state is cleared even if network throws exception
                                            isLinkingCard = false
                                        }
                                    }
                                }
                            },
                            enabled = !isLinkingCard && cardNumber.length == 4,
                            colors = ButtonDefaults.buttonColors(containerColor = PanColors.CyanAccent)
                        ) {
                            if (isLinkingCard) CircularProgressIndicator(modifier = Modifier.size(16.dp), color = Color.Black, strokeWidth = 2.dp)
                            else Text("SAVE", color = Color.Black, fontWeight = FontWeight.Bold)
                        }
                    }
                }
            }
        }
    }

    Box(modifier = Modifier.fillMaxSize()) {
        Column(modifier = Modifier.fillMaxSize().background(PanColors.SurfaceDark)) {

            Spacer(
                modifier = Modifier
                    .windowInsetsTopHeight(WindowInsets.statusBars)
                    .fillMaxWidth()
                    .background(Color.Black)
            )

            Column(modifier = Modifier.fillMaxWidth().weight(1f).verticalScroll(rememberScrollState())) {

                Row(modifier = Modifier.fillMaxWidth().background(PanColors.SurfaceMid).padding(16.dp), verticalAlignment = Alignment.CenterVertically) {
                    Box(
                        modifier = Modifier.size(40.dp).background(PanColors.ButtonSecondary, RoundedCornerShape(20.dp)).clip(RoundedCornerShape(20.dp)).clickable { onBack() },
                        contentAlignment = Alignment.Center
                    ) { Text("◀", color = Color.White, fontSize = 18.sp) }

                    Spacer(modifier = Modifier.width(16.dp))
                    Text("AGENT LEDGER & PROFILE", color = Color.White, fontSize = 16.sp, fontWeight = FontWeight.Bold, letterSpacing = 1.sp)
                }

                Column(modifier = Modifier.fillMaxWidth().padding(24.dp), horizontalAlignment = Alignment.CenterHorizontally) {
                    Text("AVAILABLE FIAT BALANCE", color = Color.Gray, fontSize = 12.sp, fontWeight = FontWeight.Bold, letterSpacing = 1.sp)

                    if (isLoading) {
                        CircularProgressIndicator(color = PanColors.QualifiedGreen, modifier = Modifier.padding(16.dp))
                    } else {
                        Text(text = balance.toCurrency(), color = PanColors.QualifiedGreen, fontSize = 64.sp, fontWeight = FontWeight.Black)
                    }

                    Spacer(modifier = Modifier.height(24.dp))

                    if (linkedCard == null && !isLoading) {
                        Button(
                            onClick = { showLinkCardDialog = true },
                            colors = ButtonDefaults.buttonColors(containerColor = PanColors.CyanAccent),
                            modifier = Modifier.fillMaxWidth().height(56.dp), shape = RoundedCornerShape(8.dp)
                        ) { Text("LINK BANK DEBIT CARD", color = Color.Black, fontWeight = FontWeight.Black, fontSize = 14.sp) }
                    } else if (!isLoading) {
                        Button(
                            onClick = {
                                if (balance > 0) {
                                    isWithdrawing = true
                                    coroutineScope.launch {
                                        try {
                                            val result = apiClient.withdrawFunds(amount = balance)

                                            result.onSuccess { message ->
                                                audioEngine.speak("Funds withdrawn to your bank.", voiceVolume)
                                                snackbarHostState.showSnackbar("SUCCESS: $message")
                                            }.onFailure { error ->
                                                audioEngine.speak("Transaction denied.", voiceVolume)
                                                snackbarHostState.showSnackbar("ERROR: ${error.message}")
                                            }

                                            apiClient.getWalletData()?.let {
                                                balance = it.balance
                                                history = it.history
                                                missionsCompleted = it.missionsCompleted
                                                vtsScore = it.vanguardTrustScore
                                            }
                                        } catch (e: Exception) {
                                            snackbarHostState.showSnackbar("ERROR: Network failure refreshing ledger.")
                                        } finally {
                                            // 🛡️ FIXED: Ensure UI is unlocked even if ledger re-sync drops
                                            isWithdrawing = false
                                        }
                                    }
                                }
                            },
                            colors = ButtonDefaults.buttonColors(containerColor = PanColors.QualifiedGreen),
                            modifier = Modifier.fillMaxWidth().height(56.dp), shape = RoundedCornerShape(8.dp),
                            enabled = !isWithdrawing && balance > 0
                        ) {
                            if (isWithdrawing) CircularProgressIndicator(modifier = Modifier.size(24.dp), color = Color.Black, strokeWidth = 2.dp)
                            else Text("WITHDRAW TO ${linkedCard?.uppercase() ?: "LINKED CARD"}", color = Color.Black, fontWeight = FontWeight.Black)
                        }
                        Spacer(modifier = Modifier.height(12.dp))
                        TextButton(onClick = { showLinkCardDialog = true }) { Text("UPDATE LINKED CARD", color = Color.Gray, fontSize = 12.sp, fontWeight = FontWeight.Bold) }
                    }

                    if (!isLoading) {
                        Spacer(modifier = Modifier.height(16.dp))
                        Button(
                            onClick = { onNavigateToStore(balance, missionsCompleted) },
                            colors = ButtonDefaults.buttonColors(containerColor = PanColors.ButtonSecondary),
                            modifier = Modifier.fillMaxWidth().height(56.dp),
                            shape = RoundedCornerShape(8.dp)
                        ) {
                            Text("🛒 OPEN SUPPLY DEPOT", color = Color.White, fontWeight = FontWeight.Black, fontSize = 14.sp, letterSpacing = 1.sp)
                        }
                    }
                }

                // 🟢 NEW: DOSSIER INSERTION POINT
                if (!isLoading) {
                    AgentRankCard(
                        missionsCompleted = missionsCompleted
                    )

                    // 🟢 OBSERVATION FIXED: Display VTS Score
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .background(PanColors.SurfaceMid)
                            .padding(horizontal = 24.dp, vertical = 12.dp),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = "VANGUARD TRUST SCORE (VTS)",
                            color = Color.LightGray,
                            fontSize = 11.sp,
                            fontWeight = FontWeight.Bold,
                            letterSpacing = 1.sp
                        )

                        val vtsDisplay = ((vtsScore * 10.0).roundToInt() / 10.0).toString()
                        val vtsColor = when {
                            vtsScore >= 90.0 -> PanColors.QualifiedGreen
                            vtsScore >= 70.0 -> PanColors.CyanAccent
                            else -> PanColors.WarningOrange
                        }

                        Text(
                            text = vtsDisplay,
                            color = vtsColor,
                            fontSize = 18.sp,
                            fontWeight = FontWeight.Black
                        )
                    }

                    HorizontalDivider(color = PanColors.ButtonSecondary, thickness = 1.dp)
                }

                Column(modifier = Modifier.fillMaxWidth().background(PanColors.SurfaceMid).padding(vertical = 16.dp)) {
                    Text("MISSION PREFERENCES", color = Color.LightGray, fontSize = 12.sp, fontWeight = FontWeight.Bold, letterSpacing = 1.sp, modifier = Modifier.padding(horizontal = 24.dp, vertical = 8.dp))
                    Row(modifier = Modifier.fillMaxWidth().padding(horizontal = 24.dp), horizontalArrangement = Arrangement.spacedBy(16.dp)) {
                        Button(
                            onClick = { onNavPrefChange("GOOGLE") },
                            colors = ButtonDefaults.buttonColors(containerColor = if (navPreference == "GOOGLE") PanColors.CyanAccent else PanColors.ButtonSecondary),
                            modifier = Modifier.weight(1f).height(48.dp), shape = RoundedCornerShape(8.dp)
                        ) { Text("NATIVE MAPS", color = if (navPreference == "GOOGLE") Color.Black else Color.White, fontSize = 12.sp, fontWeight = FontWeight.Bold) }

                        Button(
                            onClick = { onNavPrefChange("TACTICAL") },
                            colors = ButtonDefaults.buttonColors(containerColor = if (navPreference == "TACTICAL") PanColors.CyanAccent else PanColors.ButtonSecondary),
                            modifier = Modifier.weight(1f).height(48.dp), shape = RoundedCornerShape(8.dp)
                        ) { Text("PAN TACTICAL", color = if (navPreference == "TACTICAL") Color.Black else Color.White, fontSize = 12.sp, fontWeight = FontWeight.Bold) }
                    }

                    Spacer(modifier = Modifier.height(24.dp))

                    Column(modifier = Modifier.fillMaxWidth().padding(horizontal = 24.dp)) {
                        Text("AGENT IDENTITY ALIAS", color = PanColors.CyanAccent, fontSize = 12.sp, fontWeight = FontWeight.Black, letterSpacing = 1.sp, modifier = Modifier.padding(bottom = 8.dp))

                        OutlinedTextField(
                            value = firstName,
                            onValueChange = { firstName = it },
                            label = { Text("LEGAL FIRST NAME", color = Color.Gray, fontSize = 10.sp) },
                            colors = OutlinedTextFieldDefaults.colors(
                                focusedBorderColor = PanColors.CyanAccent, unfocusedBorderColor = PanColors.ButtonSecondary,
                                focusedTextColor = Color.White, unfocusedTextColor = Color.White
                            ),
                            modifier = Modifier.fillMaxWidth().padding(bottom = 8.dp), singleLine = true
                        )

                        OutlinedTextField(
                            value = callsign,
                            onValueChange = { callsign = it },
                            label = { Text("TACTICAL CALLSIGN", color = Color.Gray, fontSize = 10.sp) },
                            colors = OutlinedTextFieldDefaults.colors(
                                focusedBorderColor = PanColors.CyanAccent, unfocusedBorderColor = PanColors.ButtonSecondary,
                                focusedTextColor = Color.White, unfocusedTextColor = Color.White
                            ),
                            modifier = Modifier.fillMaxWidth().padding(bottom = 16.dp), singleLine = true
                        )

                        Button(
                            onClick = {
                                val identity = if (callsign.isNotBlank()) callsign else firstName
                                audioEngine.speak("The command is now yours, $identity.", voiceVolume)
                            },
                            colors = ButtonDefaults.buttonColors(containerColor = PanColors.ButtonSecondary),
                            modifier = Modifier.fillMaxWidth().height(48.dp), shape = RoundedCornerShape(8.dp)
                        ) { Text("🔊 TEST AUDIO ALIAS", color = Color.White, fontSize = 12.sp, fontWeight = FontWeight.Bold) }
                    }

                    Spacer(modifier = Modifier.height(24.dp))

                    Text("TACTICAL AUDIO MIXER", color = Color.Gray, fontSize = 10.sp, fontWeight = FontWeight.Bold, modifier = Modifier.padding(start = 24.dp, end = 24.dp, bottom = 8.dp))

                    Column(modifier = Modifier.fillMaxWidth().padding(horizontal = 24.dp)) {
                        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                            Text("J.A.R.V.I.S. Dispatch Voice", color = Color.White, fontSize = 12.sp, fontWeight = FontWeight.Medium)
                            Text("${(voiceVolume * 100).toInt()}%", color = PanColors.CyanAccent, fontSize = 12.sp, fontWeight = FontWeight.Bold)
                        }
                        Slider(
                            value = voiceVolume,
                            onValueChange = { onVoiceVolumeChange(it) },
                            onValueChangeFinished = { audioEngine.speak("Level set.", voiceVolume) },
                            valueRange = 0f..1f,
                            colors = SliderDefaults.colors(thumbColor = PanColors.CyanAccent, activeTrackColor = PanColors.CyanAccent)
                        )

                        Spacer(modifier = Modifier.height(8.dp))

                        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                            Text("Emergency Alarms & Beeps", color = Color.White, fontSize = 12.sp, fontWeight = FontWeight.Medium)
                            Text("${alertVolume}%", color = Color.Red, fontSize = 12.sp, fontWeight = FontWeight.Bold)
                        }
                        Slider(
                            value = alertVolume.toFloat(),
                            onValueChange = { onAlertVolumeChange(it.toInt()) },
                            onValueChangeFinished = { audioEngine.playAlertBeep(alertVolume) },
                            valueRange = 0f..100f,
                            colors = SliderDefaults.colors(thumbColor = Color.Red, activeTrackColor = Color.Red)
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
                                    color = if (isSelected) PanColors.CyanAccent else PanColors.ButtonSecondary,
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

                Column(modifier = Modifier.fillMaxWidth().background(PanColors.CardBackground).padding(top = 16.dp)) {
                    Text("FIAT SETTLEMENT LEDGER", color = Color.LightGray, fontSize = 12.sp, fontWeight = FontWeight.Bold, modifier = Modifier.padding(horizontal = 24.dp, vertical = 8.dp))
                    Column(modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 8.dp)) {
                        if (history.isEmpty() && !isLoading) {
                            Text("No transaction history available.", color = Color.Gray, fontSize = 14.sp, modifier = Modifier.padding(8.dp))
                        } else {
                            history.forEach { tx ->
                                Row(modifier = Modifier.fillMaxWidth().padding(vertical = 12.dp, horizontal = 8.dp), horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.CenterVertically) {
                                    Column(modifier = Modifier.weight(1f)) {
                                        Text(tx.date, color = Color.Gray, fontSize = 12.sp)
                                        Spacer(modifier = Modifier.height(4.dp))
                                        Text(tx.description, color = Color.White, fontSize = 14.sp, fontWeight = FontWeight.Medium)
                                        Text("TXN ID: ${tx.id}", color = Color.DarkGray, fontSize = 10.sp, fontFamily = FontFamily.Monospace)
                                    }
                                    Text(tx.amount, color = if (tx.amount.startsWith("-")) Color.Red else PanColors.QualifiedGreen, fontSize = 18.sp, fontWeight = FontWeight.Black)
                                }
                                HorizontalDivider(color = PanColors.ButtonSecondary, thickness = 1.dp)
                            }
                        }
                    }
                }
                Spacer(modifier = Modifier.height(32.dp))
            }
        }

        SnackbarHost(
            hostState = snackbarHostState,
            modifier = Modifier.align(Alignment.BottomCenter).padding(bottom = 16.dp),
            snackbar = { data ->
                Snackbar(
                    containerColor = if (data.visuals.message.startsWith("ERROR")) Color(0xFFB71C1C) else PanColors.QualifiedGreen,
                    contentColor = Color.White,
                    shape = RoundedCornerShape(8.dp)
                ) {
                    Text(text = data.visuals.message, fontWeight = FontWeight.Bold)
                }
            }
        )
    }
}