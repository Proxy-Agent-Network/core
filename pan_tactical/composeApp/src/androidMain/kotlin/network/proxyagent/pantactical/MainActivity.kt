package network.proxyagent.pantactical

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import com.google.firebase.FirebaseApp
import network.proxyagent.pantactical.ui.screens.AgentDashboardScreen

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        FirebaseApp.initializeApp(this)

        setContent {
            // This lives in androidMain, so it is allowed to call the dashboard directly!
            // This instantly launches the new PanBootSequence we just built.
            AgentDashboardScreen()
        }
    }
}