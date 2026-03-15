package com.pan.tactical

actual fun getNativeMapUrl(lat: Double, lon: Double): String {
    // We break the URL into pieces so link-rewriters don't ruin it
    val secureProtocol = "https://"
    val domain = "www." + "google.com"
    val endpoint = "/maps/dir/?api=1"

    return "$secureProtocol$domain$endpoint&destination=$lat,$lon"
}