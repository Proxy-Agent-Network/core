package com.pan.tactical.ui.components

import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.interop.UIKitView
import kotlinx.cinterop.ExperimentalForeignApi
import platform.UIKit.UIView
import com.pan.tactical.iosMapViewFactory
import com.pan.tactical.iosMapUpdater

@OptIn(ExperimentalForeignApi::class)
@Composable
actual fun TacticalMap(
    modifier: Modifier,
    targetLocation: Pair<Double, Double>,
    mapStyleJson: String?,
    route: List<Pair<Double, Double>> // <-- Added Parameter
) {
    UIKitView(
        factory = {
            iosMapViewFactory?.invoke() ?: UIView()
        },
        modifier = modifier,
        update = {
            // Ping Swift with the NEW route data!
            iosMapUpdater?.invoke(targetLocation.first, targetLocation.second, mapStyleJson, route)
        }
    )
}