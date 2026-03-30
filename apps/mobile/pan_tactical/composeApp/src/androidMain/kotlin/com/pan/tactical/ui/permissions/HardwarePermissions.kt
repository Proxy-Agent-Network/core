package com.pan.tactical.ui.permissions

import android.Manifest
import android.content.pm.PackageManager
import android.os.Build
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.core.content.ContextCompat

@Composable
fun HardwarePermissionsGuard(
    onPermissionsGranted: @Composable () -> Unit
) {
    val context = LocalContext.current

    // Determine the exact permissions needed based on Android version
    val requiredPermissions = mutableListOf(
        Manifest.permission.ACCESS_FINE_LOCATION,
        Manifest.permission.ACCESS_COARSE_LOCATION
    ).apply {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            add(Manifest.permission.BLUETOOTH_SCAN)
            add(Manifest.permission.BLUETOOTH_CONNECT)
            add("android.permission.UWB_RANGING") // Hardcoded string for broader API compatibility
        }
    }.toTypedArray()

    // 🟢 THE FIX: Synchronously check system state to prevent UI flicker
    var permissionsGranted by remember {
        mutableStateOf(
            requiredPermissions.all {
                ContextCompat.checkSelfPermission(context, it) == PackageManager.PERMISSION_GRANTED
            }
        )
    }

    val permissionLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestMultiplePermissions()
    ) { permissionsMap ->
        // Check if every requested permission was granted
        permissionsGranted = permissionsMap.values.all { it }
    }

    if (permissionsGranted) {
        onPermissionsGranted()
    } else {
        // Tactical dark-mode permission prompt
        Column(
            modifier = Modifier
                .fillMaxSize()
                .background(Color(0xFF121212))
                .padding(24.dp),
            verticalArrangement = Arrangement.Center,
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(
                text = "HARDWARE ACCESS REQUIRED",
                color = Color(0xFF00BCD4), // Cyan
                style = MaterialTheme.typography.titleLarge,
                fontWeight = FontWeight.Black
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            Text(
                text = "PAN Tactical requires precise GPS, Bluetooth Low Energy (BLE), and Ultra-Wideband (UWB) access to securely authenticate with and locate stranded autonomous vehicles.",
                color = Color.LightGray,
                style = MaterialTheme.typography.bodyMedium,
                textAlign = androidx.compose.ui.text.style.TextAlign.Center
            )
            
            Spacer(modifier = Modifier.height(32.dp))
            
            Button(
                onClick = { permissionLauncher.launch(requiredPermissions) },
                colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF4CAF50)) // Green
            ) {
                Text("AUTHORIZE HARDWARE", color = Color.Black, fontWeight = FontWeight.Bold)
            }
        }
    }
}