package com.pan.tactical.ui.theme

import androidx.compose.ui.graphics.Color

// 🛡️ [PHASE 5] Standardized Color Palette for Mesa Sector Operations
object PanColors {
    // --- Tactical UI Colors (New) ---
    val QualifiedGreen = Color(0xFF4CAF50)
    val CyanAccent = Color(0xFF00BCD4)
    val SurfaceDark = Color(0xFF121212)
    val SurfaceMid = Color(0xFF2A2A2A)
    val SurfaceLight = Color(0xFF444444)
    val WarningOrange = Color(0xFFFF9800)

    // 🛡️ REFACTOR: Standardized hex codes into the design system
    val AlertRed = Color(0xFFF44336)      // For offline status, alerts, and standard errors
    val DangerRed = Color(0xFFD32F2F)     // For destructive actions (e.g., abort mission slider)
    val OnlineGreen = Color(0xFF2E7D32)   // For the primary Go Online action
    val Disabled = Color(0xFF555555)      // For disabled UI element backgrounds
    val SliderTrack = Color(0xFF2C2C2C)   // For slider background tracks

    // --- General/Legacy UI Colors (Merged from Color.kt) ---
    val Green = Color(0xFF4CAF50)
    val Cyan = Color(0xFF00BCD4)
    val CardBackground = Color(0xFF1E1E1E)
    val CardBackgroundTransparent = Color(0xEE1E1E1E) // For the sticky banner overlay
    val ButtonSecondary = Color(0xFF333333)
}