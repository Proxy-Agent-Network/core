package com.pan.tactical

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import com.pan.tactical.network.PanWalletClient
import com.pan.tactical.ui.permissions.HardwarePermissionsGuard

class MainActivity : ComponentActivity() {

    // 🛠️ THE FIX 2: Lazy instantiation to prevent duplicate creations on screen rotation
    private val walletClient by lazy { PanWalletClient() }

    override fun onCreate(savedInstanceState: Bundle?) {
        enableEdgeToEdge()
        super.onCreate(savedInstanceState)

        // 🛠️ THE FIX 1: Removed the unsafe companion object Context.
        // Consumers will now use PanApplication.instance

        setContent {
            // 🟢 NEW: Wrapped the root entry point in the Hardware Permissions Guard.
            // This ensures GPS, BLE, and UWB access is granted before the shared KMP app boots.
            HardwarePermissionsGuard {
                // 🛠️ MINOR FIX: Corrected the comment to reflect our actual flow
                // Launching the shared KMP App (which starts at HardwareAttestationBoot)
                App(apiClient = walletClient)
            }
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        // 🛠️ THE FIX 3: Safe cleanup guard.
        // Only close clients if the app is actually exiting, not just rotating.
        if (isFinishing) {
            // If you implement a close() method on a NON-SINGLETON client, call it here:
            // walletClient.close()
        }
    }
}