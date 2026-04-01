package com.pan.tactical.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties

// TODO: Extract these to your project's Color.kt / Theme.kt file
val PanGreen = Color(0xFF4CAF50)
val PanCardBackground = Color(0xFF1E1E1E)
val PanCyan = Color(0xFF00BCD4)          // Tactical accent / header color
val PanButtonSecondary = Color(0xFF333333) // Decline / neutral button

@Composable
fun SentryExtensionDialog(
    bountyUsd: Double = 5.00,
    extensionMinutes: Int = 10,
    onAccept: () -> Unit,
    onDecline: () -> Unit
) {
    // Format the double to exactly +$X.XX
    val formattedBounty = "+$%.2f".format(bountyUsd)

    Dialog(
        onDismissRequest = { },
        // Force explicit accept/decline — dismissOnBackPress and dismissOnClickOutside are 
        // both false to prevent accidental earnings loss from an unintended gesture
        properties = DialogProperties(dismissOnBackPress = false, dismissOnClickOutside = false)
    ) {
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .background(PanCardBackground, shape = RoundedCornerShape(16.dp))
                .padding(24.dp)
        ) {
            Column(
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                Text(
                    text = "TIME EXTENSION REQUEST",
                    color = PanCyan, 
                    fontSize = 16.sp,
                    fontWeight = FontWeight.Black,
                    letterSpacing = 1.sp,
                    textAlign = TextAlign.Center
                )
                
                Text(
                    text = "The Primary Agent requires more time to resolve the incident. Fleet Command is offering an additional bounty to maintain the safety perimeter for $extensionMinutes more minutes.",
                    color = Color.LightGray,
                    fontSize = 14.sp,
                    textAlign = TextAlign.Center
                )
                
                Text(
                    text = formattedBounty,
                    color = PanGreen,
                    fontSize = 36.sp,
                    fontWeight = FontWeight.Black
                )
                
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    Button(
                        onClick = onDecline,
                        colors = ButtonDefaults.buttonColors(containerColor = PanButtonSecondary),
                        modifier = Modifier.weight(1f).height(56.dp),
                        shape = RoundedCornerShape(8.dp)
                    ) {
                        Text("DECLINE", color = Color.White)
                    }

                    Button(
                        onClick = onAccept,
                        colors = ButtonDefaults.buttonColors(containerColor = PanGreen),
                        modifier = Modifier.weight(1f).height(56.dp),
                        shape = RoundedCornerShape(8.dp)
                    ) {
                        Text("EXTEND", color = Color.White, fontWeight = FontWeight.Black)
                    }
                }
            }
        }
    }
}

@Preview(showBackground = true, backgroundColor = 0xFF121212)
@Composable
fun SentryExtensionDialogPreview() {
    SentryExtensionDialog(
        bountyUsd = 5.00,
        extensionMinutes = 10,
        onAccept = {},
        onDecline = {}
    )
}