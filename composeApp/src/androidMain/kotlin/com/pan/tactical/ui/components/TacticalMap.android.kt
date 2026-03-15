package com.pan.tactical.ui.components

import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import com.google.android.gms.maps.model.CameraPosition
import com.google.android.gms.maps.model.LatLng
import com.google.android.gms.maps.model.MapStyleOptions
import com.google.maps.android.compose.GoogleMap
import com.google.maps.android.compose.MapProperties
import com.google.maps.android.compose.MapUiSettings
import com.google.maps.android.compose.rememberCameraPositionState

@Composable
actual fun TacticalMap(
    modifier: Modifier,
    targetLocation: Pair<Double, Double>,
    mapStyleJson: String?,
    route: List<Pair<Double, Double>> // <-- Added Parameter
) {
    val position = LatLng(targetLocation.first, targetLocation.second)
    val cameraPositionState = rememberCameraPositionState {
        this.position = CameraPosition.fromLatLngZoom(position, 14.2f)
    }

    GoogleMap(
        modifier = modifier,
        cameraPositionState = cameraPositionState,
        properties = MapProperties(mapStyleOptions = mapStyleJson?.let { MapStyleOptions(it) }),
        uiSettings = MapUiSettings(zoomControlsEnabled = false, myLocationButtonEnabled = false)
    )
}