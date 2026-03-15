package com.pan.tactical.ui.components

import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier

@Composable
expect fun TacticalMap(
    modifier: Modifier,
    targetLocation: Pair<Double, Double>,
    mapStyleJson: String? = null,
    route: List<Pair<Double, Double>> = emptyList() // <-- New Parameter
)