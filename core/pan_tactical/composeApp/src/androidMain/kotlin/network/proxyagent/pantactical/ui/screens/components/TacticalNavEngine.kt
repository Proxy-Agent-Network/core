package network.proxyagent.pantactical.ui.components

import android.app.Activity
import android.util.Log
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalLifecycleOwner
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.viewinterop.AndroidView
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.LifecycleEventObserver
import com.google.android.gms.maps.model.LatLng
import com.google.android.gms.maps.model.MapStyleOptions
import com.google.android.libraries.navigation.NavigationApi
import com.google.android.libraries.navigation.Navigator
import com.google.android.libraries.navigation.NavigationView
import com.google.android.libraries.navigation.RoutingOptions
import com.google.android.libraries.navigation.Waypoint
import android.view.ContextThemeWrapper
import network.proxyagent.pantactical.R

@Composable
fun TacticalNavEngine(
    modifier: Modifier = Modifier,
    targetLocation: LatLng? = null,
    mapStyleJson: String, // NEW: Accepts our custom dark mode JSON
    onRouteCalculated: (distance: Double, etaSeconds: Int) -> Unit = { _, _ -> }
) {
    val context = LocalContext.current
    val activity = context as? Activity
    val lifecycleOwner = LocalLifecycleOwner.current

    var isTosAccepted by remember { mutableStateOf(false) }
    var navigator by remember { mutableStateOf<Navigator?>(null) }
    var navView by remember { mutableStateOf<NavigationView?>(null) }
    var initializationError by remember { mutableStateOf<String?>(null) }

    // STEP 1: Google's Mandatory Terms and Conditions
    LaunchedEffect(Unit) {
        if (activity != null) {
            // --- NEW: INSTANT BYPASS IF ALREADY ACCEPTED ---
            if (NavigationApi.areTermsAccepted(activity.application)) {
                isTosAccepted = true
            } else {
                NavigationApi.showTermsAndConditionsDialog(
                    activity,
                    "PAN Tactical",
                    object : NavigationApi.OnTermsResponseListener {
                        override fun onTermsResponse(isAccepted: Boolean) {
                            if (isAccepted) {
                                isTosAccepted = true
                            } else {
                                initializationError = "TOS Rejected. Navigation offline."
                            }
                        }
                    }
                )
            }
        } else {
            initializationError = "Error: Activity context missing."
        }
    }

    // STEP 2: Initialize the Engine
    LaunchedEffect(isTosAccepted) {
        if (isTosAccepted && activity != null) {
            NavigationApi.getNavigator(
                activity,
                object : NavigationApi.NavigatorListener {
                    override fun onNavigatorReady(nav: Navigator) {
                        navigator = nav
                    }
                    override fun onError(@NavigationApi.ErrorCode errorCode: Int) {
                        initializationError = "Nav SDK Error Code: $errorCode"
                    }
                }
            )
        }
    }

    // STEP 3: Route calculation
    LaunchedEffect(targetLocation, navigator) {
        if (targetLocation != null && navigator != null) {
            val destination = Waypoint.builder()
                .setLatLng(targetLocation.latitude, targetLocation.longitude)
                .build()

            val pendingRoute = navigator?.setDestination(destination, RoutingOptions())

            pendingRoute?.setOnResultListener { routeStatus ->
                if (routeStatus == Navigator.RouteStatus.OK) {
                    navigator?.startGuidance()

                    val timeAndDistance = navigator?.currentTimeAndDistance
                    if (timeAndDistance != null) {
                        onRouteCalculated(
                            timeAndDistance.meters.toDouble() / 1609.34,
                            timeAndDistance.seconds
                        )
                    }
                } else {
                    Log.e("PAN_NAV", "Routing Error: $routeStatus")
                }
            }
        } else if (targetLocation == null) {
            navigator?.stopGuidance()
            navigator?.clearDestinations()
        }
    }

    Box(modifier = modifier.background(Color(0xFF121212)), contentAlignment = Alignment.Center) {
        if (initializationError != null) {
            Text(initializationError!!, color = Color.Red, fontWeight = FontWeight.Bold)
        } else if (navigator == null) {
            CircularProgressIndicator(color = Color(0xFF00BCD4))
        } else {
            // STEP 4: AndroidView Wrapper with Custom Map Styling
            AndroidView(
                factory = { ctx ->
                    val view = NavigationView(ctx).apply {
                        onCreate(null)
                        onStart()
                        onResume()
                    }
                    navView = view

                    view.getMapAsync { googleMap ->
                        googleMap.isMyLocationEnabled = true
                        googleMap.uiSettings.isZoomControlsEnabled = false
                        googleMap.uiSettings.isCompassEnabled = true
                        // Inject PAN Tactical Dark Mode for the map tiles
                        googleMap.setMapStyle(MapStyleOptions(mapStyleJson))
                    }
                    view
                },
                modifier = Modifier.fillMaxSize()
            )
        }
    }

    DisposableEffect(lifecycleOwner) {
        val observer = LifecycleEventObserver { _, event ->
            when (event) {
                Lifecycle.Event.ON_RESUME -> navView?.onResume()
                Lifecycle.Event.ON_PAUSE -> navView?.onPause()
                Lifecycle.Event.ON_STOP -> navView?.onStop()
                Lifecycle.Event.ON_DESTROY -> navView?.onDestroy()
                else -> {}
            }
        }
        lifecycleOwner.lifecycle.addObserver(observer)
        onDispose { lifecycleOwner.lifecycle.removeObserver(observer) }
    }
}