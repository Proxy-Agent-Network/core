package com.pan.tactical.ui.components

import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import com.google.android.gms.maps.CameraUpdateFactory
import com.google.android.gms.maps.model.BitmapDescriptorFactory
import com.google.android.gms.maps.model.CameraPosition
import com.google.android.gms.maps.model.LatLng
import com.google.android.gms.maps.model.MapStyleOptions
import com.google.maps.android.compose.*

@Composable
actual fun TacticalMap(
    modifier: Modifier,
    targetLocation: Pair<Double, Double>,
    mapStyleJson: String?,
    route: List<Pair<Double, Double>>
) {
    // 1. Performance Fix: Prevent GC thrashing by remembering the agent's LatLng
    val currentLatLng = remember(targetLocation) {
        LatLng(targetLocation.first, targetLocation.second)
    }

    // 2. Initial Map State
    val cameraPositionState = rememberCameraPositionState {
        position = CameraPosition.fromLatLngZoom(
            LatLng(targetLocation.first, targetLocation.second),
            16.5f // Restored to 16.5f for tactical street-level visibility
        )
    }

    // 3. Performance Fix: Smooth Camera Tracking
    LaunchedEffect(targetLocation) {
        cameraPositionState.animate(
            // Use the memoized currentLatLng to pan without destroying user's manual zoom
            update = CameraUpdateFactory.newLatLng(currentLatLng),
            // 500ms prevents animation queuing when 1Hz GPS pings arrive
            durationMs = 500
        )
    }

    // 4. Performance Fix: Prevent GC thrashing by remembering the mapped route array
    val polylinePoints = remember(route) {
        route.map { LatLng(it.first, it.second) }
    }

    GoogleMap(
        modifier = modifier,
        cameraPositionState = cameraPositionState,
        properties = MapProperties(mapStyleOptions = mapStyleJson?.let { MapStyleOptions(it) }),
        uiSettings = MapUiSettings(
            zoomControlsEnabled = false,
            myLocationButtonEnabled = false,
            compassEnabled = true
        )
    ) {
        // --- DRAW THE MISSION ROUTE & UWB ZONE ---
        if (polylinePoints.isNotEmpty()) {
            val destination = polylinePoints.last()

            // Draw the GPS Macro-Route
            Polyline(
                points = polylinePoints,
                color = Color(0xFF00BCD4), // Tactical Cyan
                width = 12f,
                zIndex = 1f
            )

            // Draw the Target AV Marker
            Marker(
                state = MarkerState(position = destination),
                title = "Stranded AV",
                snippet = "UWB Homing Target",
                zIndex = 2f
            )

            // Draw the 15-Meter UWB Transition Zone
            Circle(
                center = destination,
                radius = 15.0, // Exactly 15 meters for UWB lock
                fillColor = Color(0x3300BCD4), // 20% opacity cyan
                strokeColor = Color(0xFF00BCD4),
                strokeWidth = 3f,
                zIndex = 0f
            )
        }

        // --- DRAW THE VANGUARD AGENT ---
        Marker(
            state = MarkerState(position = currentLatLng),
            title = "Vanguard-01",
            snippet = "Active Patrol",
            icon = BitmapDescriptorFactory.defaultMarker(BitmapDescriptorFactory.HUE_AZURE),
            flat = true, // Rotates with the map, not the camera
            anchor = Offset(0.5f, 0.5f),
            zIndex = 3f
        )
    }
}