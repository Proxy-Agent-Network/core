package com.pan.tactical

import androidx.compose.runtime.*
import kotlinx.cinterop.ExperimentalForeignApi
import kotlinx.cinterop.useContents
import platform.CoreLocation.*
import platform.Foundation.*
import platform.darwin.NSObject

@OptIn(ExperimentalForeignApi::class)
actual class SharedLocationManager {
    internal var onLocationUpdate: ((Double, Double) -> Unit)? = null

    private val locationManager = CLLocationManager()

    private val locationDelegate = object : NSObject(), CLLocationManagerDelegateProtocol {
        override fun locationManager(manager: CLLocationManager, didUpdateLocations: List<*>) {
            val location = didUpdateLocations.lastOrNull() as? CLLocation
            if (location != null) {
                location.coordinate.useContents {
                    onLocationUpdate?.invoke(latitude, longitude)
                }
            }
        }

        override fun locationManager(manager: CLLocationManager, didChangeAuthorizationStatus: Int) {
            if (didChangeAuthorizationStatus == kCLAuthorizationStatusAuthorizedWhenInUse ||
                didChangeAuthorizationStatus == kCLAuthorizationStatusAuthorizedAlways) {
                println("TACTICAL GPS: Permission Confirmed. Starting engine...")
                manager.startUpdatingLocation()
            } else {
                println("TACTICAL GPS: Blocked by Apple. Status Code: $didChangeAuthorizationStatus")
            }
        }

        // --- THE ERROR CATCHER ---
        override fun locationManager(manager: CLLocationManager, didFailWithError: NSError) {
            println("TACTICAL GPS HARDWARE ERROR: ${didFailWithError.localizedDescription} (Code: ${didFailWithError.code})")
        }
    }

    init {
        locationManager.delegate = locationDelegate
        locationManager.desiredAccuracy = kCLLocationAccuracyBest
    }

    actual fun startTracking() {
        println("TACTICAL GPS: Requesting iOS Hardware...")
        locationManager.requestWhenInUseAuthorization()
        locationManager.startUpdatingLocation()
    }

    actual fun stopTracking() {
        locationManager.stopUpdatingLocation()
    }
}

@Composable
actual fun rememberSharedLocationManager(onLocationUpdate: (lat: Double, lon: Double) -> Unit): SharedLocationManager {
    val locationManager = remember {
        SharedLocationManager().apply {
            this.onLocationUpdate = onLocationUpdate
        }
    }

    DisposableEffect(Unit) {
        locationManager.startTracking()
        onDispose {
            locationManager.stopTracking()
        }
    }

    return locationManager
}