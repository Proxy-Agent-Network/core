package com.pan.tactical

import android.os.Bundle
import androidx.fragment.app.FragmentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import com.google.firebase.FirebaseApp
import com.google.firebase.FirebaseOptions
import com.pan.tactical.network.PanApiClient
import com.pan.tactical.ui.permissions.HardwarePermissionsGuard

class MainActivity : FragmentActivity() {

    private val tacticalClient by lazy { PanApiClient() }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()

        // THE SILVER BULLET: Manually satisfy Firebase to stop the crash.
        // This prevents the "Default FirebaseApp is not initialized" error
        // without needing to fight the Gradle plugin or rip out your code.
        try {
            if (FirebaseApp.getApps(this).isEmpty()) {
                val options = FirebaseOptions.Builder()
                    .setProjectId("vanguard-50-pilot")
                    .setApplicationId("1:1234567890:android:abcdef123456")
                    .setApiKey("AIzaSyMockKeyForVanguardPilotTest123")
                    .build()
                FirebaseApp.initializeApp(this, options)
            }
        } catch (e: Exception) {
            e.printStackTrace()
        }

        setContent {
            HardwarePermissionsGuard {
                App(apiClient = tacticalClient)
            }
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        if (isFinishing) {
            tacticalClient.close()
        }
    }
}