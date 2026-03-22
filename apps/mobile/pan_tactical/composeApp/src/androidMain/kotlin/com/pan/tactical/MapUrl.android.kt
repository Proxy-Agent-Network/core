package com.pan.tactical

// Android uses the "google.navigation" intent scheme
actual fun getNativeMapUrl(lat: Double, lon: Double): String {
    return "google.navigation:q=$lat,$lon"
}