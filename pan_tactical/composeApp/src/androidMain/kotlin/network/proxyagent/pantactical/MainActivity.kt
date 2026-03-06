package network.proxyagent.pantactical

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import network.proxyagent.pantactical.ui.screens.AgentDashboardScreen
import network.proxyagent.pantactical.ui.screens.KeyCeremonyScreen

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        setContent {
            // Our Simple Navigation Router
            // "KeyCeremony" is the default starting point.
            var currentScreen by remember { mutableStateOf("KeyCeremony") }

            when (currentScreen) {
                "KeyCeremony" -> {
                    KeyCeremonyScreen(
                        onCeremonyComplete = {
                            println("SYSTEM: Hardware Attestation Complete. Routing to Dashboard.")
                            // This instantly triggers Compose to redraw the screen with the Dashboard
                            currentScreen = "Dashboard"
                        }
                    )
                }
                "Dashboard" -> {
                    AgentDashboardScreen()
                }
            }
        }
    }
}