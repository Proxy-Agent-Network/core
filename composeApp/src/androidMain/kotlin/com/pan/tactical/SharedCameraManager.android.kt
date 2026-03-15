package com.pan.tactical

import android.graphics.Bitmap
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.activity.result.launch
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import java.io.ByteArrayOutputStream

actual class SharedCameraManager {
    // A hidden variable to hold the trigger action
    internal var onLaunch: (() -> Unit)? = null

    actual fun launchCamera() {
        onLaunch?.invoke()
    }
}

@Composable
actual fun rememberSharedCameraManager(onResult: (ByteArray?) -> Unit): SharedCameraManager {
    // 1. We ask Android for a Camera launcher
    val launcher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.TakePicturePreview()
    ) { bitmap: Bitmap? ->
        // 2. When the picture comes back, we compress it into a ByteArray
        if (bitmap != null) {
            val stream = ByteArrayOutputStream()
            bitmap.compress(Bitmap.CompressFormat.JPEG, 90, stream)
            onResult(stream.toByteArray())
        } else {
            onResult(null)
        }
    }

    // 3. We return our Manager, wired up to pull the trigger
    return remember {
        SharedCameraManager().apply {
            onLaunch = { launcher.launch() }
        }
    }
}