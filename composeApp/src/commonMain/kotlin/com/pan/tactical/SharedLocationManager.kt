package com.pan.tactical

import androidx.compose.runtime.Composable

// The object that talks to the native OS GPS chips
expect class SharedLocationManager {
    fun startTracking()
    fun stopTracking()
}

// The Composable hook so our Dashboard can listen to the GPS stream
@Composable
expect fun rememberSharedLocationManager(onLocationUpdate: (lat: Double, lon: Double) -> Unit): SharedLocationManager