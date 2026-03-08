package network.proxyagent.pantactical.ui.screens.components

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import network.proxyagent.pantactical.models.MissionData

@Composable
fun MissionAlertOverlay(
    activeMission: MissionData?,
    countdownProgress: Float,
    flashAlpha: Float,
    onAccept: () -> Unit,
    onDecline: () -> Unit
) {
    Box(modifier = Modifier.fillMaxSize().background(Color(0xEE121212)).padding(24.dp), contentAlignment = Alignment.Center) {
        Box(modifier = Modifier.fillMaxSize().background(Color(0xFF4CAF50).copy(alpha = flashAlpha)))
        Column(modifier = Modifier.fillMaxWidth().verticalScroll(rememberScrollState()), horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.spacedBy(10.dp)) {
            Text("🚨 RESCUE DISPATCH 🚨", color = Color(0xFFF44336), fontSize = 24.sp, fontWeight = FontWeight.Black, letterSpacing = 1.sp, textAlign = TextAlign.Center)
            Box(modifier = Modifier.fillMaxWidth().height(12.dp).background(Color(0xFF1E1E1E), shape = RoundedCornerShape(8.dp)), contentAlignment = Alignment.CenterStart) {
                Box(modifier = Modifier.fillMaxHeight().fillMaxWidth(countdownProgress).background(Color(0xFF4CAF50), shape = RoundedCornerShape(8.dp)))
            }
            val rawBounty = activeMission?.bounty?.replace("$", "")?.toFloatOrNull() ?: 0f
            Text("GUARANTEED NET PAYOUT", color = Color.LightGray, fontSize = 12.sp, fontWeight = FontWeight.Bold, letterSpacing = 1.sp)
            Text(String.format("$%.2f", rawBounty * 0.90f), color = Color(0xFF4CAF50), fontSize = 48.sp, fontWeight = FontWeight.Black)
            Text(activeMission?.intersection ?: "Unknown", color = Color(0xFFFF9800), fontSize = 20.sp, fontWeight = FontWeight.Medium, textAlign = TextAlign.Center)
            Text(activeMission?.errorCode ?: "Unknown Error", color = Color.Red, fontSize = 18.sp, fontWeight = FontWeight.Bold, textAlign = TextAlign.Center)
            Row(horizontalArrangement = Arrangement.spacedBy(16.dp), modifier = Modifier.fillMaxWidth()) {
                Button(onClick = onDecline, colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF333333)), modifier = Modifier.weight(1f).height(64.dp), shape = RoundedCornerShape(12.dp)) { Text("DECLINE", color = Color.White) }
                Button(
                    onClick = onAccept,
                    colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF4CAF50)),
                    modifier = Modifier.weight(1f).height(64.dp),
                    shape = RoundedCornerShape(12.dp)
                ) {
                    Text("ACCEPT", color = Color.White, fontWeight = FontWeight.Black)
                }
            }
        }
    }
}