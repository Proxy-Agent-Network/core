package com.pan.tactical

import android.content.Context
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge

class MainActivity : ComponentActivity() {

    // --- NATIVE CONTEXT EXPOSURE ---
    // This allows our shared KMP tools (like AudioEngine) to access Android hardware
    companion object {
        var appContext: Context? = null
            private set
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        enableEdgeToEdge()
        super.onCreate(savedInstanceState)

        // Grab the application context the moment the app boots
        appContext = applicationContext

        setContent {
            // Launching the shared KMP App (which starts at LoginScreen)
            App()
        }
    }
}