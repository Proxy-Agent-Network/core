package com.pan.tactical

import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.platform.LocalContext
import com.pan.tactical.hardware.AndroidUwbClient
import com.pan.tactical.hardware.UwbClient

@Composable
actual fun rememberUwbClient(): UwbClient {
    val context = LocalContext.current
    return remember { AndroidUwbClient(context) }
}