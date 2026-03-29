package com.pan.tactical

import androidx.compose.runtime.Composable
import com.pan.tactical.hardware.BleHomingClient

@Composable
expect fun rememberBleHomingClient(): BleHomingClient