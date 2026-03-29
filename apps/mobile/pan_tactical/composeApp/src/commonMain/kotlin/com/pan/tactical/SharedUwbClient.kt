package com.pan.tactical

import androidx.compose.runtime.Composable
import com.pan.tactical.hardware.UwbClient

// The Composable hook so our Dashboard can instantiate the platform-specific UWB engine
@Composable
expect fun rememberUwbClient(): UwbClient