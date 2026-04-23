package com.pan.tactical.ui.screens

import androidx.compose.animation.AnimatedContent
import androidx.compose.animation.core.tween
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.togetherWith
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import com.pan.tactical.ui.WalletNetworkClient // 🟢 THE FIX: Use the cross-platform Interface

enum class TransferState {
    EXPLANATION, CAPTURING, VERIFYING, SUCCESS, FAILED
}

@Composable
fun DeviceTransferScreen(
    apiClient: WalletNetworkClient, // 🟢 THE FIX: Accept the interface type
    onTransferComplete: () -> Unit,
    onCancel: () -> Unit
) {
    var currentState by remember { mutableStateOf(TransferState.EXPLANATION) }
    val coroutineScope = rememberCoroutineScope()

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color(0xFF0A0C10))
            .padding(24.dp)
            .systemBarsPadding(),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        // --- HEADER ---
        Spacer(modifier = Modifier.height(24.dp))

        Text(
            text = "⚠️",
            fontSize = 48.sp
        )

        Spacer(modifier = Modifier.height(16.dp))
        Text(
            text = "HARDWARE MISMATCH",
            color = Color.White,
            fontSize = 20.sp,
            fontWeight = FontWeight.Black,
            letterSpacing = 2.sp,
            fontFamily = FontFamily.Monospace
        )
        Spacer(modifier = Modifier.height(32.dp))

        // --- DYNAMIC CONTENT AREA ---
        Box(
            modifier = Modifier
                .weight(1f)
                .fillMaxWidth(),
            contentAlignment = Alignment.Center
        ) {
            AnimatedContent(
                targetState = currentState,
                transitionSpec = {
                    fadeIn(animationSpec = tween(500)) togetherWith fadeOut(animationSpec = tween(500))
                },
                label = "transfer_state_animation"
            ) { state ->
                when (state) {
                    TransferState.EXPLANATION -> ExplanationView()
                    TransferState.CAPTURING -> MockCameraView()
                    TransferState.VERIFYING -> VerifyingView()
                    TransferState.SUCCESS -> SuccessView()
                    TransferState.FAILED -> FailedView()
                }
            }
        }

        // --- BOTTOM CONTROLS ---
        Spacer(modifier = Modifier.height(24.dp))

        when (currentState) {
            TransferState.EXPLANATION -> {
                Button(
                    onClick = { currentState = TransferState.CAPTURING },
                    colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF00BCD4)),
                    modifier = Modifier.fillMaxWidth().height(56.dp),
                    shape = RoundedCornerShape(4.dp)
                ) {
                    Text("START BIOMETRIC SCAN", color = Color.Black, fontWeight = FontWeight.Bold, letterSpacing = 1.sp)
                }
                TextButton(onClick = onCancel, modifier = Modifier.padding(top = 8.dp)) {
                    Text("CANCEL", color = Color.Gray, letterSpacing = 1.sp)
                }
            }
            TransferState.CAPTURING -> {
                Button(
                    onClick = {
                        currentState = TransferState.VERIFYING
                        coroutineScope.launch {
                            // 🟢 THE FIX: The interface now exposes this method!
                            val success = apiClient.overrideHardwareLock()

                            // Small delay so the user sees the "Verifying" state
                            delay(1500)

                            if (success) {
                                currentState = TransferState.SUCCESS
                            } else {
                                currentState = TransferState.FAILED
                            }
                        }
                    },
                    colors = ButtonDefaults.buttonColors(containerColor = Color.White),
                    modifier = Modifier.fillMaxWidth().height(56.dp),
                    shape = RoundedCornerShape(4.dp)
                ) {
                    Text("CAPTURE PHOTO", color = Color.Black, fontWeight = FontWeight.Bold)
                }
            }
            TransferState.VERIFYING -> {
                // No buttons, waiting on API response
            }
            TransferState.SUCCESS -> {
                Button(
                    onClick = onTransferComplete,
                    colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF4CAF50)),
                    modifier = Modifier.fillMaxWidth().height(56.dp),
                    shape = RoundedCornerShape(4.dp)
                ) {
                    Text("REBOOT TERMINAL", color = Color.White, fontWeight = FontWeight.Bold)
                }
            }
            TransferState.FAILED -> {
                Button(
                    onClick = { currentState = TransferState.CAPTURING },
                    colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF00BCD4)),
                    modifier = Modifier.fillMaxWidth().height(56.dp),
                    shape = RoundedCornerShape(4.dp)
                ) {
                    Text("RETRY SCAN", color = Color.Black, fontWeight = FontWeight.Bold)
                }
                TextButton(onClick = onCancel, modifier = Modifier.padding(top = 8.dp)) {
                    Text("CONTACT DISPATCH", color = Color.Gray)
                }
            }
        }
    }
}

@Composable
private fun ExplanationView() {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(
            text = "IDENTITY LOCKED\nDevice Mismatch Detected",
            color = Color.LightGray,
            fontSize = 18.sp,
            textAlign = TextAlign.Center,
            lineHeight = 26.sp,
            fontWeight = FontWeight.Bold
        )
        Spacer(modifier = Modifier.height(24.dp))
        Box(
            modifier = Modifier
                .border(1.dp, Color(0xFF333333), RoundedCornerShape(8.dp))
                .background(Color(0xFF121212))
                .padding(16.dp)
        ) {
            Text(
                text = "Complete a 3D biometric scan to verify your identity and authorize device transfer.\n\nRemove hats & sunglasses.",
                color = Color(0xFF00BCD4),
                fontSize = 16.sp,
                textAlign = TextAlign.Center,
                lineHeight = 24.sp,
                fontWeight = FontWeight.Medium
            )
        }
    }
}

@Composable
private fun MockCameraView() {
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .aspectRatio(3f / 4f)
            .border(2.dp, Color(0xFF00BCD4), RoundedCornerShape(16.dp))
            .background(Color(0xFF1E1E1E)),
        contentAlignment = Alignment.Center
    ) {
        Text("[ CAMERA VIEWFINDER ACTIVE ]", color = Color.Gray, fontFamily = FontFamily.Monospace)

        Box(
            modifier = Modifier
                .fillMaxHeight(0.6f)
                .fillMaxWidth(0.5f)
                .border(2.dp, Color.White.copy(alpha = 0.3f), RoundedCornerShape(100.dp))
        )
    }
}

@Composable
private fun VerifyingView() {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        CircularProgressIndicator(color = Color(0xFF00BCD4), modifier = Modifier.size(64.dp), strokeWidth = 4.dp)
        Spacer(modifier = Modifier.height(24.dp))
        Text(
            text = "ENCRYPTING BIOMETRICS...",
            color = Color.White,
            fontFamily = FontFamily.Monospace,
            letterSpacing = 1.sp
        )
        Spacer(modifier = Modifier.height(8.dp))
        Text(
            text = "Verifying with Vanguard Identity Services",
            color = Color.Gray,
            fontSize = 12.sp
        )
    }
}

@Composable
private fun SuccessView() {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text("✅", fontSize = 64.sp)
        Spacer(modifier = Modifier.height(24.dp))
        Text(
            text = "IDENTITY VERIFIED",
            color = Color(0xFF4CAF50),
            fontSize = 20.sp,
            fontWeight = FontWeight.Black,
            letterSpacing = 1.sp
        )
        Spacer(modifier = Modifier.height(16.dp))
        Text(
            text = "The previous hardware lock has been wiped from the ledger. You may now initialize this terminal.",
            color = Color.LightGray,
            textAlign = TextAlign.Center,
            modifier = Modifier.padding(horizontal = 24.dp)
        )
    }
}

@Composable
private fun FailedView() {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text("❌", fontSize = 64.sp)
        Spacer(modifier = Modifier.height(24.dp))
        Text(
            text = "VERIFICATION FAILED",
            color = Color(0xFFE53935),
            fontSize = 20.sp,
            fontWeight = FontWeight.Black,
            letterSpacing = 1.sp
        )
        Spacer(modifier = Modifier.height(16.dp))
        Text(
            text = "The biometric scan did not match the authorized agent on file, or lighting was too poor to process.",
            color = Color.LightGray,
            textAlign = TextAlign.Center,
            modifier = Modifier.padding(horizontal = 24.dp)
        )
    }
}