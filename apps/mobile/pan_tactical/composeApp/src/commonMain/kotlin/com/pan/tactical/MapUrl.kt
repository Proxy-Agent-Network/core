package com.pan.tactical

// We "expect" each platform to provide its own specific navigation URL
expect fun getNativeMapUrl(lat: Double, lon: Double): String