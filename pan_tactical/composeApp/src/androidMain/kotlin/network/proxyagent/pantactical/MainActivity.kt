package network.proxyagent.pantactical

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import network.proxyagent.pantactical.ui.screens.AgentDashboardScreen

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        setContent {
            // This lives in androidMain, so it is allowed to call the dashboard directly!
            // This instantly launches the new PanBootSequence we just built.
            AgentDashboardScreen()
        }
    }
}