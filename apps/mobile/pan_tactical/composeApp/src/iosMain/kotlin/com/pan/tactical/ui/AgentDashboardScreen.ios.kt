package com.pan.tactical.ui

import androidx.compose.foundation.layout.*
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

// 🛡️ Tells iOS: "Show a compliance warning because iOS lacks the required hardware APIs for this phase."
@Composable
actual fun AgentDashboardScreen(apiClient: WalletNetworkClient) {
    Box(
        modifier = Modifier.fillMaxSize(),
        contentAlignment = Alignment.Center
    ) {
        Column(horizontalAlignment = Alignment.CenterHorizontally) {
            Text(
                text = "⚠️ TACTICAL OPERATIONS RESTRICTED",
                color = Color.Red,
                fontWeight = FontWeight.Black,
                fontSize = 18.sp
            )
            Spacer(modifier = Modifier.height(16.dp))
            Text(
                text = "SB 1417 Compliance requires Android StrongBox and raw UWB access. iOS tactical support is pending MFi fleet integration.",
                color = Color.White,
                modifier = Modifier.padding(32.dp)
            )
        }
    }
}