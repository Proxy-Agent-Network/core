package com.pan.tactical

import android.os.Bundle
import androidx.fragment.app.FragmentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import com.pan.tactical.network.PanApiClient 
import com.pan.tactical.ui.permissions.HardwarePermissionsGuard

class MainActivity : FragmentActivity() {

    private val tacticalClient by lazy { PanApiClient() }

    override fun onCreate(savedInstanceState: Bundle?) {
        enableEdgeToEdge()
        super.onCreate(savedInstanceState)


        setContent {
            // 🟢 NEW: Wrapped the root entry point in the Hardware Permissions Guard.
            // This ensures GPS, BLE, and UWB access is granted before the shared KMP app boots.
            HardwarePermissionsGuard {
                App(apiClient = tacticalClient)
            }
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        // Only close clients if the app is actually exiting, not just rotating.
        if (isFinishing) {
            tacticalClient.close()
        }
    }
}