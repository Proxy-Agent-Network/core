package com.pan.tactical.ui.components

// --- QUARANTINED ANDROID NAVIGATION SDK IMPORTS ---
// import android.app.Activity
// import android.util.Log
// import androidx.compose.ui.platform.LocalContext
// import androidx.compose.ui.platform.LocalLifecycleOwner
// import androidx.compose.ui.viewinterop.AndroidView
// import androidx.lifecycle.Lifecycle
// import androidx.lifecycle.LifecycleEventObserver
// import com.google.android.gms.maps.model.LatLng
// import com.google.android.gms.maps.model.MapStyleOptions
// import com.google.android.libraries.navigation.NavigationApi
// import com.google.android.libraries.navigation.Navigator
// import com.google.android.libraries.navigation.NavigationView
// import com.google.android.libraries.navigation.RoutingOptions
// import com.google.android.libraries.navigation.Waypoint
// --------------------------------------------------

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign

@Composable
fun TacticalNavEngine(
    modifier: Modifier = Modifier,
    targetLocation: Pair<Double, Double>? = null, // SWAPPED LatLng for KMP Pair
    mapStyleJson: String, // NEW: Accepts our custom dark mode JSON
    onRouteCalculated: (distance: Double, etaSeconds: Int) -> Unit = { _, _ -> }
) {
    // --- QUARANTINED ANDROID NAVIGATION LOGIC ---
    /*
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
                .setLatLng(targetLocation.first, targetLocation.second) // Using Pair
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
    */
    // ---------------------------------------------

    // --- KMP PLACEHOLDER UI ---
    Box(
        modifier = modifier.fillMaxSize().background(Color.Black),
        contentAlignment = Alignment.Center
    ) {
        Text(
            text = "TACTICAL NAV ENGINE OFFLINE\n(Awaiting KMP Bridge)",
            color = Color.Yellow,
            textAlign = TextAlign.Center,
            fontWeight = FontWeight.Bold
        )
    }

    // --- QUARANTINED LIFECYCLE LISTENER ---
    /*
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
    */
}