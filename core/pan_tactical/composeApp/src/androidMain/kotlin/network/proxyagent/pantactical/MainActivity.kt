package network.proxyagent.pantactical

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.runtime.*
import com.google.firebase.FirebaseApp
import com.google.firebase.auth.FirebaseAuth
import network.proxyagent.pantactical.ui.screens.AgentDashboardScreen
import network.proxyagent.pantactical.ui.screens.LoginScreen

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Initialize Firebase on app boot
        FirebaseApp.initializeApp(this)

        setContent {
            // Pass control to the Security Router
            AppRouter()
        }
    }
}

@Composable
fun AppRouter() {
    val auth = remember { FirebaseAuth.getInstance() }

    // Check if the user is already logged in on this device
    var currentAgentUid by remember { mutableStateOf(auth.currentUser?.uid) }

    if (currentAgentUid == null) {
        // User is NOT logged in. Show the tactical login terminal.
        LoginScreen(
            onLoginSuccess = { secureUid ->
                // When LoginScreen reports a success, update the state to boot the dashboard
                currentAgentUid = secureUid
            }
        )
    } else {
        // User IS logged in! Boot the main terminal.
        // NOTE: Right now, the dashboard still hardcodes "VANGUARD-01".
        // We will pass this UID into it in the next step.
        AgentDashboardScreen()
    }
}