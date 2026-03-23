package com.pan.tactical

import platform.UIKit.UIView

fun getSecureMapsKey(): String {
    // 🟢 Changed to pull the iOS-specific key!
    return BuildConfig.IOS_MAPS_API_KEY
}

var iosMapViewFactory: (() -> UIView)? = null

// --- THE FIX: Added 'route' to the remote control bridge! ---
var iosMapUpdater: ((lat: Double, lon: Double, styleJson: String?, route: List<Pair<Double, Double>>) -> Unit)? = null