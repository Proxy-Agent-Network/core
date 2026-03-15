package com.pan.tactical

interface Platform {
    val name: String
}

expect fun getPlatform(): Platform