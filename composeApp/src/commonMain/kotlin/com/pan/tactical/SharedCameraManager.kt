package com.pan.tactical

import androidx.compose.runtime.Composable

// This is the object that will actually trigger the hardware camera
expect class SharedCameraManager {
    fun launchCamera()
}

// We need a Composable function to "remember" this manager
// so it survives screen rotations and recompositions.
@Composable
expect fun rememberSharedCameraManager(onResult: (ByteArray?) -> Unit): SharedCameraManager