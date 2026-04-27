package com.pan.tactical.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlinx.coroutines.launch

@Composable
fun HardwareMismatchScreen(
    onRetryScan: () -> Unit,
    onResetSuccess: () -> Unit, // Callback to restart the Key Ceremony
    onDevResetBinding: suspend () -> Boolean // 🟢 KMP Safe: Pass the function, not the Android client!
) {
    val coroutineScope = rememberCoroutineScope()
    var isResetting by remember { mutableStateOf(false) }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color(0xFF121212))
            .padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        // --- ERROR ICON & TITLE ---
        Text(text = "⚠️", fontSize = 64.sp)
        Spacer(modifier = Modifier.height(16.dp))
        Text(
            text = "HARDWARE MISMATCH",
            color = Color.White,
            fontSize = 20.sp,
            fontWeight = FontWeight.Black,
            letterSpacing = 2.sp
        )

        Spacer(modifier = Modifier.height(64.dp))

        Text(text = "❌", fontSize = 80.sp, color = Color(0xFFF44336))
        Spacer(modifier = Modifier.height(16.dp))

        Text(
            text = "VERIFICATION FAILED",
            color = Color(0xFFF44336),
            fontSize = 18.sp,
            fontWeight = FontWeight.Bold,
            letterSpacing = 1.sp
        )

        Spacer(modifier = Modifier.height(16.dp))

        Text(
            text = "The cryptographic signature did not match the authorized agent on file, or the device TPM is already bound.",
            color = Color.LightGray,
            fontSize = 14.sp,
            textAlign = TextAlign.Center,
            lineHeight = 22.sp,
            modifier = Modifier.padding(horizontal = 16.dp)
        )

        Spacer(modifier = Modifier.height(64.dp))

        // --- RETRY BUTTON ---
        Button(
            onClick = onRetryScan,
            modifier = Modifier.fillMaxWidth().height(56.dp),
            colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF00BCD4)),
            shape = RoundedCornerShape(8.dp)
        ) {
            Text("RETRY SCAN", color = Color.Black, fontWeight = FontWeight.Black)
        }

        Spacer(modifier = Modifier.height(16.dp))

        TextButton(onClick = { /* TODO: Support flow */ }) {
            Text("CONTACT DISPATCH", color = Color.Gray, fontWeight = FontWeight.Bold)
        }

        Spacer(modifier = Modifier.height(32.dp))

        // 🟢 The Dev Trapdoor to clear the 409 Conflict
        Button(
            onClick = {
                isResetting = true
                coroutineScope.launch {
                    val success = onDevResetBinding() // Call the passed-in function
                    isResetting = false
                    if (success) {
                        onResetSuccess()
                    }
                }
            },
            modifier = Modifier.fillMaxWidth().height(48.dp),
            colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF4A1A1A)),
            shape = RoundedCornerShape(8.dp),
            enabled = !isResetting
        ) {
            if (isResetting) {
                CircularProgressIndicator(color = Color.White, modifier = Modifier.size(20.dp))
            } else {
                Text("DEV: RESET BINDING", color = Color(0xFFFF6B6B), fontWeight = FontWeight.Bold)
            }
        }
    }
}