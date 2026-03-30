package com.pan.tactical

import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.platform.LocalContext
import com.pan.tactical.hardware.AndroidBleClient
import com.pan.tactical.hardware.BleHomingClient

@Composable
actual fun rememberBleHomingClient(): BleHomingClient {
    val context = LocalContext.current
    return remember { AndroidBleClient(context) }
}