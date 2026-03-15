package com.pan.tactical.ui.screens

import android.content.Context
import android.media.AudioManager
import android.speech.tts.TextToSpeech
import android.speech.tts.Voice
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.foundation.background
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
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.AnnotatedString
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.OffsetMapping
import androidx.compose.ui.text.input.TransformedText
import androidx.compose.ui.text.input.VisualTransformation
import androidx.compose.ui.layout.ContentScale
import androidx.compose.foundation.border
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey
import coil3.compose.AsyncImage
import kotlinx.coroutines.launch
import com.pan.tactical.network.PanApiClient

@Composable
fun WalletAndProfileScreen(
    apiClient: PanApiClient,
    onBack: () -> Unit,
    navPreference: String,
    onNavPrefChange: (String) -> Unit,
    tts: TextToSpeech?,
    availableVoices: List<Voice>,
    selectedVoice: Voice?,
    onVoiceSelect: (Voice) -> Unit,
    voiceVolume: Float,
    onVoiceVolumeChange: (Float) -> Unit,
    alertVolume: Int,
    onAlertVolumeChange: (Int) -> Unit
) {
    val context = LocalContext.current
    val coroutineScope = rememberCoroutineScope()

    val sharedPrefs = remember {
        try {
            val masterKey = MasterKey.Builder(context)
                .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
                .build()

            EncryptedSharedPreferences.create(
                context,
                "PanAgentSecureSettings",
                masterKey,
                EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
                EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
            )
        } catch (e: Exception) {
            context.getSharedPreferences("PanAgentSettings", Context.MODE_PRIVATE)
        }
    }

    var firstName by remember { mutableStateOf(sharedPrefs.getString("agent_first_name", "") ?: "") }
    var callsign by remember { mutableStateOf(sharedPrefs.getString("agent_callsign", "") ?: "") }

    var walletData by remember { mutableStateOf<com.pan.tactical.network.WalletResponse?>(null) }
    var isFetchingWallet by remember { mutableStateOf(true) }
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
    var selectedTransaction by remember { mutableStateOf<com.pan.tactical.network.TransactionLog?>(null) }
    var enlargedImageUrl by remember { mutableStateOf<String?>(null) }

    LaunchedEffect(Unit) {
        walletData = apiClient.getWalletData()
        isFetchingWallet = false
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

                if (isFetchingWallet) {
                    CircularProgressIndicator(color = Color(0xFF4CAF50), modifier = Modifier.padding(16.dp))
                } else {
                    Text(text = String.format("$%.2f", walletData?.balance ?: 0.0), color = Color(0xFF4CAF50), fontSize = 64.sp, fontWeight = FontWeight.Black)
                    Spacer(modifier = Modifier.height(24.dp))

                    if (walletData?.linkedCard == null) {
                        Button(
                            onClick = { showLinkCardDialog = true },
                            colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF1976D2)),
                            modifier = Modifier.fillMaxWidth().height(56.dp), shape = RoundedCornerShape(8.dp)
                        ) { Text("LINK BANK DEBIT CARD", color = Color.White, fontWeight = FontWeight.Black, fontSize = 14.sp) }
                    } else {
                        Button(
                            onClick = {
                                val balanceToWithdraw = walletData?.balance ?: 0.0
                                if (balanceToWithdraw > 0) {
                                    isWithdrawing = true
                                    coroutineScope.launch {
                                        val success = apiClient.withdrawFunds(amount = balanceToWithdraw)
                                        if (success) {
                                            android.widget.Toast.makeText(context, String.format("ACH Transfer Initiated: $%.2f", balanceToWithdraw), android.widget.Toast.LENGTH_LONG).show()
                                            walletData = apiClient.getWalletData()
                                        } else {
                                            android.widget.Toast.makeText(context, "Withdrawal Failed.", android.widget.Toast.LENGTH_LONG).show()
                                        }
                                        isWithdrawing = false
                                    }
                                }
                            },
                            colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF2E7D32)),
                            modifier = Modifier.fillMaxWidth().height(56.dp), shape = RoundedCornerShape(8.dp), enabled = !isWithdrawing
                        ) {
                            if (isWithdrawing) CircularProgressIndicator(modifier = Modifier.size(24.dp), color = Color.White, strokeWidth = 2.dp)
                            else Text("WITHDRAW TO ${walletData!!.linkedCard?.uppercase()}", color = Color.White, fontWeight = FontWeight.Black)
                        }
                        Spacer(modifier = Modifier.height(12.dp))
                        TextButton(onClick = { showLinkCardDialog = true }) { Text("UPDATE LINKED CARD", color = Color.Gray, fontSize = 12.sp, fontWeight = FontWeight.Bold) }
                    }
                }
            }

            Column(modifier = Modifier.fillMaxWidth().background(Color(0xFF1A1A1A)).padding(vertical = 16.dp)) {
                Text("MISSION PREFERENCES", color = Color.LightGray, fontSize = 12.sp, fontWeight = FontWeight.Bold, letterSpacing = 1.sp, modifier = Modifier.padding(horizontal = 24.dp, vertical = 8.dp))
                Row(modifier = Modifier.fillMaxWidth().padding(horizontal = 24.dp), horizontalArrangement = Arrangement.spacedBy(16.dp)) {
                    Button(
                        onClick = { onNavPrefChange("GOOGLE") },
                        colors = ButtonDefaults.buttonColors(containerColor = if (navPreference == "GOOGLE") Color(0xFF1976D2) else Color(0xFF333333)),
                        modifier = Modifier.weight(1f).height(48.dp), shape = RoundedCornerShape(8.dp)
                    ) { Text("GOOGLE MAPS", color = Color.White, fontSize = 12.sp, fontWeight = FontWeight.Bold) }

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
                        onValueChange = {
                            firstName = it
                            sharedPrefs.edit().putString("agent_first_name", it).apply()
                        },
                        label = { Text("LEGAL FIRST NAME", color = Color.Gray, fontSize = 10.sp) },
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedBorderColor = Color(0xFF00BCD4),
                            unfocusedBorderColor = Color(0xFF333333),
                            focusedTextColor = Color.White,
                            unfocusedTextColor = Color.White,
                            cursorColor = Color(0xFF00BCD4)
                        ),
                        modifier = Modifier.fillMaxWidth().padding(bottom = 8.dp),
                        singleLine = true
                    )

                    OutlinedTextField(
                        value = callsign,
                        onValueChange = {
                            callsign = it
                            sharedPrefs.edit().putString("agent_callsign", it).apply()
                        },
                        label = { Text("TACTICAL CALLSIGN (OVERRIDES NAME)", color = Color.Gray, fontSize = 10.sp) },
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedBorderColor = Color(0xFF00BCD4),
                            unfocusedBorderColor = Color(0xFF333333),
                            focusedTextColor = Color.White,
                            unfocusedTextColor = Color.White,
                            cursorColor = Color(0xFF00BCD4)
                        ),
                        modifier = Modifier.fillMaxWidth().padding(bottom = 16.dp),
                        singleLine = true
                    )

                    Button(
                        onClick = {
                            val identity = when {
                                callsign.isNotBlank() -> callsign
                                firstName.isNotBlank() -> firstName
                                else -> "Proxy Agent"
                            }
                            val ttsParams = android.os.Bundle().apply {
                                putFloat(android.speech.tts.TextToSpeech.Engine.KEY_PARAM_VOLUME, voiceVolume)
                            }
                            tts?.speak("The command is now yours, $identity.", TextToSpeech.QUEUE_FLUSH, ttsParams, "TestAudio")
                        },
                        colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF333333)),
                        modifier = Modifier.fillMaxWidth().height(48.dp),
                        shape = RoundedCornerShape(8.dp)
                    ) {
                        Text("🔊 TEST AUDIO ALIAS", color = Color.White, fontSize = 12.sp, fontWeight = FontWeight.Bold)
                    }
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
                        onValueChange = {
                            onVoiceVolumeChange(it)
                            val ttsParams = android.os.Bundle().apply { putFloat(android.speech.tts.TextToSpeech.Engine.KEY_PARAM_VOLUME, it) }
                            tts?.speak("Level set.", TextToSpeech.QUEUE_FLUSH, ttsParams, null)
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
                            try {
                                val audioManager = context.getSystemService(Context.AUDIO_SERVICE) as AudioManager
                                if (audioManager.ringerMode == AudioManager.RINGER_MODE_NORMAL) {
                                    val toneGen = android.media.ToneGenerator(AudioManager.STREAM_ALARM, alertVolume)
                                    toneGen.startTone(android.media.ToneGenerator.TONE_PROP_BEEP, 150)
                                    coroutineScope.launch {
                                        kotlinx.coroutines.delay(200)
                                        toneGen.release()
                                    }
                                }
                            } catch (e: Exception) {
                                println("AUDIO ERROR: Failed to play preview beep - ${e.message}")
                            }
                        },
                        valueRange = 0f..100f,
                        colors = SliderDefaults.colors(thumbColor = Color(0xFFF44336), activeTrackColor = Color(0xFFF44336))
                    )
                }

                // --- FIX 1: ALWAYS SHOW VOICE PROFILE ---
                Column(modifier = Modifier.fillMaxWidth().padding(top = 24.dp)) {
                    Text("TACTICAL VOICE PROFILE", color = Color.Gray, fontSize = 10.sp, fontWeight = FontWeight.Bold, modifier = Modifier.padding(horizontal = 24.dp, vertical = 8.dp))
                    Row(modifier = Modifier.fillMaxWidth().horizontalScroll(rememberScrollState()).padding(horizontal = 24.dp), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        val natoAlphabet = listOf("ALPHA", "BRAVO", "CHARLIE", "DELTA", "ECHO", "FOXTROT")
                        availableVoices.forEachIndexed { index, voice ->
                            val isSelected = selectedVoice?.name == voice.name
                            val label = natoAlphabet.getOrElse(index) { "VOICE ${index + 1}" }
                            Surface(
                                shape = RoundedCornerShape(4.dp),
                                color = if (isSelected) Color(0xFF00BCD4) else Color(0xFF333333),
                                modifier = Modifier.clickable {
                                    onVoiceSelect(voice)
                                    tts?.voice = voice
                                    val ttsParams = android.os.Bundle().apply { putFloat(android.speech.tts.TextToSpeech.Engine.KEY_PARAM_VOLUME, voiceVolume) }
                                    tts?.speak("Voice profile $label engaged.", TextToSpeech.QUEUE_FLUSH, ttsParams, null)
                                }
                            ) { Text(text = label, color = if(isSelected) Color.Black else Color.White, fontSize = 12.sp, fontWeight = FontWeight.Bold, modifier = Modifier.padding(horizontal = 16.dp, vertical = 10.dp)) }
                        }
                    }
                }
            }

            Column(modifier = Modifier.fillMaxWidth().background(Color(0xFF1E1E1E)).padding(top = 16.dp)) {
                Text("CRYPTOGRAPHIC TRANSACTION LEDGER", color = Color.LightGray, fontSize = 12.sp, fontWeight = FontWeight.Bold, modifier = Modifier.padding(horizontal = 24.dp, vertical = 8.dp))
                Column(modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 8.dp)) {
                    if (walletData?.history?.isEmpty() == true) {
                        Text("No transactions found on ledger.", color = Color.DarkGray, fontSize = 14.sp, modifier = Modifier.padding(16.dp))
                    } else {
                        walletData?.history?.forEach { tx ->
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
            }

            Spacer(modifier = Modifier.height(32.dp))
        }
    }

    if (showLinkCardDialog) {
        AlertDialog(
            onDismissRequest = { showLinkCardDialog = false },
            containerColor = Color(0xFF1E1E1E),
            title = { Text("🔒 LINK DEBIT CARD", color = Color.White, fontWeight = FontWeight.Black) },
            text = {
                Column {
                    OutlinedTextField(value = cardNumber, onValueChange = { input -> cardNumber = input.filter { it.isDigit() }.take(16) }, label = { Text("16-Digit Card Number", color = Color.Gray) }, keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number), visualTransformation = WalletCardFormatter(), colors = OutlinedTextFieldDefaults.colors(focusedTextColor = Color.White, unfocusedTextColor = Color.White), singleLine = true, modifier = Modifier.fillMaxWidth())
                    Spacer(modifier = Modifier.height(12.dp))
                    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        Box(modifier = Modifier.weight(1f)) {
                            OutlinedTextField(value = expMonth, onValueChange = {}, readOnly = true, label = { Text("Month", color = Color.Gray) }, colors = OutlinedTextFieldDefaults.colors(disabledTextColor = Color.White), modifier = Modifier.fillMaxWidth())
                            Box(modifier = Modifier.matchParentSize().background(Color.Transparent).clickable { monthExpanded = true })
                            DropdownMenu(expanded = monthExpanded, onDismissRequest = { monthExpanded = false }, modifier = Modifier.background(Color(0xFF2A2A2A))) {
                                (1..12).forEach { m -> DropdownMenuItem(text = { Text(m.toString().padStart(2, '0'), color = Color.White) }, onClick = { expMonth = m.toString().padStart(2, '0'); monthExpanded = false }) }
                            }
                        }
                        Box(modifier = Modifier.weight(1f)) {
                            OutlinedTextField(value = expYear, onValueChange = {}, readOnly = true, label = { Text("Year", color = Color.Gray) }, colors = OutlinedTextFieldDefaults.colors(disabledTextColor = Color.White), modifier = Modifier.fillMaxWidth())
                            Box(modifier = Modifier.matchParentSize().background(Color.Transparent).clickable { yearExpanded = true })
                            DropdownMenu(expanded = yearExpanded, onDismissRequest = { yearExpanded = false }, modifier = Modifier.background(Color(0xFF2A2A2A))) {
                                (2026..2035).forEach { y -> DropdownMenuItem(text = { Text(y.toString(), color = Color.White) }, onClick = { expYear = y.toString(); yearExpanded = false }) }
                            }
                        }
                        OutlinedTextField(value = cvv, onValueChange = { cvv = it.filter { c -> c.isDigit() }.take(4) }, label = { Text("CVV", color = Color.Gray) }, keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number), colors = OutlinedTextFieldDefaults.colors(focusedTextColor = Color.White, unfocusedTextColor = Color.White), modifier = Modifier.weight(1f))
                    }
                    Spacer(modifier = Modifier.height(12.dp))
                    OutlinedTextField(value = zipCode, onValueChange = { zipCode = it.filter { c -> c.isDigit() }.take(5) }, label = { Text("ZIP Code", color = Color.Gray) }, keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number), colors = OutlinedTextFieldDefaults.colors(focusedTextColor = Color.White, unfocusedTextColor = Color.White), modifier = Modifier.fillMaxWidth())
                }
            },
            confirmButton = {
                Button(
                    onClick = {
                        if (cardNumber.length == 16 && cvv.isNotEmpty() && zipCode.isNotEmpty() && expMonth.isNotEmpty() && expYear.isNotEmpty()) {
                            isLinkingCard = true
                            coroutineScope.launch {
                                val maskedCard = "Visa ending in ${cardNumber.takeLast(4)}"
                                val success = apiClient.linkDebitCard(cardNumber = maskedCard)
                                if (success) {
                                    walletData = apiClient.getWalletData()
                                    showLinkCardDialog = false
                                    cardNumber = ""; cvv = ""; zipCode = ""; expMonth = ""; expYear = ""
                                }
                                isLinkingCard = false
                            }
                        }
                    },
                    colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF1976D2))
                ) { if (isLinkingCard) CircularProgressIndicator(modifier = Modifier.size(16.dp), color = Color.White) else Text("SECURE LINK", color = Color.White) }
            },
            dismissButton = { TextButton(onClick = { showLinkCardDialog = false }) { Text("CANCEL", color = Color.Gray) } }
        )
    }

    if (selectedTransaction != null) {
        AlertDialog(
            onDismissRequest = { selectedTransaction = null },
            containerColor = Color(0xFF1E1E1E),
            title = { Text("🧾 SMART CONTRACT RECEIPT", color = Color.White, fontWeight = FontWeight.Black) },
            text = {
                Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                    Text(selectedTransaction!!.amount, color = if (selectedTransaction!!.amount.startsWith("-")) Color(0xFFF44336) else Color(0xFF4CAF50), fontSize = 36.sp, fontWeight = FontWeight.Black)

                    Column {
                        Text("DESCRIPTION", color = Color.Gray, fontSize = 10.sp, fontWeight = FontWeight.Bold)
                        Text(selectedTransaction!!.description, color = Color.White, fontSize = 16.sp)
                    }

                    Column {
                        Text("TIMESTAMP", color = Color.Gray, fontSize = 10.sp, fontWeight = FontWeight.Bold)
                        Text(selectedTransaction!!.date, color = Color.White, fontSize = 14.sp)
                    }

                    Column {
                        Text("CRYPTOGRAPHIC HASH (TXN ID)", color = Color.Gray, fontSize = 10.sp, fontWeight = FontWeight.Bold)
                        Text(selectedTransaction!!.id, color = Color(0xFF00BCD4), fontSize = 12.sp, fontFamily = FontFamily.Monospace)
                    }

                    if (!selectedTransaction!!.evidenceUrls.isNullOrEmpty()) {
                        Column {
                            Text("ATTACHED PROOF OF WORK", color = Color.Gray, fontSize = 10.sp, fontWeight = FontWeight.Bold)
                            Spacer(modifier = Modifier.height(4.dp))
                            Row(
                                modifier = Modifier.fillMaxWidth().horizontalScroll(rememberScrollState()),
                                horizontalArrangement = Arrangement.spacedBy(8.dp)
                            ) {
                                selectedTransaction!!.evidenceUrls!!.forEach { url ->
                                    AsyncImage(
                                        model = url,
                                        contentDescription = "Redacted Evidence",
                                        modifier = Modifier
                                            .size(80.dp)
                                            .clip(RoundedCornerShape(8.dp))
                                            .border(1.dp, Color(0xFF00BCD4), RoundedCornerShape(8.dp))
                                            .clickable {
                                                val safeUrl = url.lowercase()
                                                if ((safeUrl.startsWith("https://i.ibb.co/") || safeUrl.startsWith("https://imgbb.com/")) &&
                                                    (safeUrl.endsWith(".jpg") || safeUrl.endsWith(".png") || safeUrl.endsWith(".jpeg"))) {
                                                    enlargedImageUrl = url
                                                } else {
                                                    android.widget.Toast.makeText(context, "SECURITY BLOCK: Untrusted evidence source.", android.widget.Toast.LENGTH_SHORT).show()
                                                }
                                            },
                                        contentScale = ContentScale.Crop
                                    )
                                }
                            }
                        }
                    }

                    Spacer(modifier = Modifier.height(8.dp))
                    Text("STATUS: SETTLED & VERIFIED", color = Color(0xFF4CAF50), fontSize = 12.sp, fontWeight = FontWeight.Black, letterSpacing = 1.sp)
                    Text("NODE: VANGUARD-01", color = Color.DarkGray, fontSize = 10.sp, fontFamily = FontFamily.Monospace)
                }
            },
            confirmButton = {
                Button(
                    onClick = { selectedTransaction = null },
                    colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF333333))
                ) { Text("CLOSE", color = Color.White) }
            }
        )
    }

    if (enlargedImageUrl != null) {
        Dialog(
            onDismissRequest = { enlargedImageUrl = null },
            properties = DialogProperties(usePlatformDefaultWidth = false)
        ) {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .background(Color(0xEE000000))
                    .clickable(
                        interactionSource = remember { MutableInteractionSource() },
                        indication = null,
                        onClick = { enlargedImageUrl = null }
                    ),
                contentAlignment = Alignment.Center
            ) {
                AsyncImage(
                    model = enlargedImageUrl,
                    contentDescription = "Enlarged Evidence",
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp)
                        .clip(RoundedCornerShape(8.dp))
                        .border(2.dp, Color(0xFF00BCD4), RoundedCornerShape(8.dp)),
                    contentScale = ContentScale.FillWidth
                )

                Text(
                    "✖ TAP ANYWHERE TO CLOSE",
                    color = Color.White,
                    fontSize = 12.sp,
                    fontWeight = FontWeight.Bold,
                    letterSpacing = 1.sp,
                    modifier = Modifier
                        .align(Alignment.BottomCenter)
                        .padding(bottom = 32.dp)
                        .background(Color(0x80000000), RoundedCornerShape(16.dp))
                        .padding(horizontal = 16.dp, vertical = 8.dp)
                )
            }
        }
    }
}

private class WalletCardFormatter : VisualTransformation {
    override fun filter(text: AnnotatedString): TransformedText {
        val trimmed = text.text.take(16)
        var out = ""
        for (i in trimmed.indices) {
            out += trimmed[i]
            if (i % 4 == 3 && i != 15) out += " "
        }
        val offsetMapping = object : OffsetMapping {
            override fun originalToTransformed(offset: Int) = if (offset <= 3) offset else if (offset <= 7) offset + 1 else if (offset <= 11) offset + 2 else if (offset <= 16) offset + 3 else 19
            override fun transformedToOriginal(offset: Int) = if (offset <= 4) offset else if (offset <= 9) offset - 1 else if (offset <= 14) offset - 2 else if (offset <= 19) offset - 3 else 16
        }
        return TransformedText(AnnotatedString(out), offsetMapping)
    }
}