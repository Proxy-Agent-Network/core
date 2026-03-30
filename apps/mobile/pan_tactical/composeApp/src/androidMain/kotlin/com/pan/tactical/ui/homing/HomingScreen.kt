package com.pan.tactical.ui.homing

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

@Composable
fun HomingScreen(
    viewModel: HomingViewModel,
    onMissionComplete: () -> Unit
) {
    val uiState by viewModel.uiState.collectAsState()

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color(0xFF000000))
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        // Header
        Text(
            text = "TACTICAL MICRO-HOMING",
            color = Color(0xFF00BCD4),
            fontFamily = FontFamily.Monospace,
            fontSize = 20.sp,
            fontWeight = FontWeight.Black,
            modifier = Modifier.padding(top = 24.dp, bottom = 32.dp)
        )

        // Main Status Display Area
        Box(
            modifier = Modifier
                .weight(1f)
                .fillMaxWidth()
                .border(2.dp, getBorderColorForPhase(uiState.phase), RoundedCornerShape(8.dp))
                .background(Color(0xFF111111))
                .padding(24.dp),
            contentAlignment = Alignment.Center
        ) {
            when (uiState.phase) {
                HomingPhase.MACRO_GPS -> {
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Text("GPS MACRO-ROUTING", color = Color.Gray, fontFamily = FontFamily.Monospace)
                        Spacer(modifier = Modifier.height(16.dp))
                        Text(
                            text = uiState.gpsDistanceMeters?.let { "%.1f m".format(it) } ?: "CALCULATING...",
                            color = Color.White,
                            fontSize = 48.sp,
                            fontWeight = FontWeight.Bold,
                            fontFamily = FontFamily.Monospace
                        )
                        Spacer(modifier = Modifier.height(16.dp))
                        Text("Awaiting 50m Geofence Breach", color = Color(0xFFFF9800), fontSize = 12.sp)
                    }
                }
                HomingPhase.BLE_HANDSHAKE -> {
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        CircularProgressIndicator(color = Color(0xFF00BCD4))
                        Spacer(modifier = Modifier.height(24.dp))
                        Text("EXECUTING OOB HANDSHAKE...", color = Color(0xFF00BCD4), fontFamily = FontFamily.Monospace)
                        Text("Exchanging Cryptographic Keys via BLE", color = Color.Gray, fontSize = 12.sp, modifier = Modifier.padding(top = 8.dp))
                    }
                }
                HomingPhase.MICRO_UWB -> {
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Text("UWB PRECISION TRACKING", color = Color(0xFFE040FB), fontFamily = FontFamily.Monospace)
                        Spacer(modifier = Modifier.height(16.dp))
                        Text(
                            text = uiState.uwbDistanceMeters?.let { "%.2f m".format(it) } ?: "LINKING...",
                            color = Color.White,
                            fontSize = 64.sp,
                            fontWeight = FontWeight.Black,
                            fontFamily = FontFamily.Monospace
                        )
                        Spacer(modifier = Modifier.height(16.dp))
                        Text(
                            text = uiState.uwbAzimuth?.let { "AZIMUTH: %.1f°".format(it) } ?: "ACQUIRING VECTOR...",
                            color = Color(0xFFE040FB),
                            fontSize = 16.sp,
                            fontFamily = FontFamily.Monospace
                        )
                    }
                }
                HomingPhase.ON_SCENE -> {
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Text("✅ ASSET SECURED", color = Color(0xFF4CAF50), fontSize = 24.sp, fontWeight = FontWeight.Black)
                        Spacer(modifier = Modifier.height(16.dp))
                        Text("Agent is within 2.0 meters.", color = Color.LightGray)
                        Spacer(modifier = Modifier.height(32.dp))
                        Button(
                            onClick = onMissionComplete,
                            colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF4CAF50))
                        ) {
                            Text("PROCEED TO EVIDENCE UPLOAD", color = Color.Black, fontWeight = FontWeight.Bold)
                        }
                    }
                }
                HomingPhase.FAILED -> {
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Text("❌ HARDWARE FAULT", color = Color(0xFFF44336), fontSize = 24.sp, fontWeight = FontWeight.Black)
                        Spacer(modifier = Modifier.height(16.dp))
                        Text(uiState.errorMessage ?: "Unknown hardware error occurred.", color = Color.LightGray, textAlign = androidx.compose.ui.text.style.TextAlign.Center)
                        Spacer(modifier = Modifier.height(32.dp))
                        Button(
                            onClick = { viewModel.forceBleHandshake() },
                            colors = ButtonDefaults.buttonColors(containerColor = Color(0xFFF44336))
                        ) {
                            Text("RETRY HANDSHAKE", color = Color.White, fontWeight = FontWeight.Bold)
                        }
                    }
                }
            }
        }
        
        // Manual Override Button (Only visible in GPS phase)
        if (uiState.phase == HomingPhase.MACRO_GPS) {
            Spacer(modifier = Modifier.height(24.dp))
            OutlinedButton(
                onClick = { viewModel.forceBleHandshake() },
                colors = ButtonDefaults.outlinedButtonColors(contentColor = Color(0xFF888888))
            ) {
                Text("FORCE BLE HANDSHAKE", fontFamily = FontFamily.Monospace, fontSize = 12.sp)
            }
        }
    }
}

// Helper for UI styling
fun getBorderColorForPhase(phase: HomingPhase): Color {
    return when (phase) {
        HomingPhase.MACRO_GPS -> Color(0xFF333333)
        HomingPhase.BLE_HANDSHAKE -> Color(0xFF00BCD4)
        HomingPhase.MICRO_UWB -> Color(0xFFE040FB)
        HomingPhase.ON_SCENE -> Color(0xFF4CAF50)
        HomingPhase.FAILED -> Color(0xFFF44336)
    }
}