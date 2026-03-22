package com.pan.tactical

import android.Manifest
import android.annotation.SuppressLint
import android.content.Context
import android.location.Location
import android.location.LocationListener
import android.location.LocationManager
import android.os.Bundle
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.runtime.*
import androidx.compose.ui.platform.LocalContext

actual class SharedLocationManager {
    // Hidden variables to hold the Android context and our callback
    internal var context: Context? = null
    internal var onLocationUpdate: ((Double, Double) -> Unit)? = null

    private var locationManager: LocationManager? = null
    private var isTracking = false

    // The native Android listener that catches GPS pings
    private val locationListener = object : LocationListener {
        override fun onLocationChanged(location: Location) {
            // Send the raw coordinates back to our shared KMP Dashboard!
            onLocationUpdate?.invoke(location.latitude, location.longitude)
        }
        override fun onStatusChanged(provider: String?, status: Int, extras: Bundle?) {}
        override fun onProviderEnabled(provider: String) {}
        override fun onProviderDisabled(provider: String) {}
    }

    @SuppressLint("MissingPermission")
    actual fun startTracking() {
        if (isTracking || context == null) return
        locationManager = context?.getSystemService(Context.LOCATION_SERVICE) as? LocationManager

        try {
            // Request updates every 2 seconds (2000ms) or every 1 meter moved
            locationManager?.requestLocationUpdates(LocationManager.GPS_PROVIDER, 2000L, 1f, locationListener)
            locationManager?.requestLocationUpdates(LocationManager.NETWORK_PROVIDER, 2000L, 1f, locationListener)
            isTracking = true
        } catch (e: Exception) {
            println("Tactical Location tracking failed: ${e.message}")
        }
    }

    actual fun stopTracking() {
        locationManager?.removeUpdates(locationListener)
        isTracking = false
    }
}

@Composable
actual fun rememberSharedLocationManager(onLocationUpdate: (lat: Double, lon: Double) -> Unit): SharedLocationManager {
    val context = LocalContext.current

    // 1. Create our Manager and attach the context/callback
    val locationManager = remember {
        SharedLocationManager().apply {
            this.context = context
            this.onLocationUpdate = onLocationUpdate
        }
    }

    var hasPermission by remember { mutableStateOf(false) }

    // 2. The Android permission popup launcher
    val permissionLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestMultiplePermissions()
    ) { permissions ->
        hasPermission = permissions[Manifest.permission.ACCESS_FINE_LOCATION] == true ||
                permissions[Manifest.permission.ACCESS_COARSE_LOCATION] == true

        // If the agent clicks "Allow", instantly start pulling GPS data
        if (hasPermission) {
            locationManager.startTracking()
        }
    }

    // 3. As soon as this Composable hits the screen, ask for permission
    LaunchedEffect(Unit) {
        permissionLauncher.launch(
            arrayOf(
                Manifest.permission.ACCESS_FINE_LOCATION,
                Manifest.permission.ACCESS_COARSE_LOCATION
            )
        )
    }

    // 4. Safety First: If the agent closes the app, stop pinging the GPS to save battery
    DisposableEffect(Unit) {
        onDispose {
            locationManager.stopTracking()
        }
    }

    return locationManager
}