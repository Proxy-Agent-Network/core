package com.pan.tactical

import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import kotlinx.cinterop.ExperimentalForeignApi
import kotlinx.cinterop.addressOf
import kotlinx.cinterop.usePinned
import platform.UIKit.*
import platform.Foundation.*
import platform.darwin.NSObject
import platform.posix.memcpy

actual class SharedCameraManager {
    internal var onLaunch: (() -> Unit)? = null

    actual fun launchCamera() {
        onLaunch?.invoke()
    }
}

@OptIn(ExperimentalForeignApi::class)
@Composable
actual fun rememberSharedCameraManager(onResult: (ByteArray?) -> Unit): SharedCameraManager {
    val cameraManager = remember { SharedCameraManager() }

    // 1. We build the iOS Delegate that waits for the photo to be snapped
    val imagePickerDelegate = remember {
        object : NSObject(), UIImagePickerControllerDelegateProtocol, UINavigationControllerDelegateProtocol {
            override fun imagePickerController(
                picker: UIImagePickerController,
                didFinishPickingMediaWithInfo: Map<Any?, *>
            ) {
                // Grab the picture out of the Apple dictionary
                val image = didFinishPickingMediaWithInfo[UIImagePickerControllerOriginalImage] as? UIImage
                if (image != null) {
                    // Compress it slightly for faster tactical uploads
                    val imageData = UIImageJPEGRepresentation(image, 0.9)
                    if (imageData != null) {
                        val length = imageData.length.toInt()
                        val byteArray = ByteArray(length)
                        if (length > 0) {
                            // Convert Apple NSData into a standard Kotlin ByteArray
                            byteArray.usePinned { pinned ->
                                memcpy(pinned.addressOf(0), imageData.bytes, imageData.length)
                            }
                        }
                        onResult(byteArray)
                    } else {
                        onResult(null)
                    }
                } else {
                    onResult(null)
                }
                // Close the camera screen
                picker.dismissViewControllerAnimated(true, null)
            }

            override fun imagePickerControllerDidCancel(picker: UIImagePickerController) {
                // If the agent hits cancel, just close it
                onResult(null)
                picker.dismissViewControllerAnimated(true, null)
            }
        }
    }

    // 2. We wire up the launch trigger
    cameraManager.onLaunch = {
        val picker = UIImagePickerController()

        // 3. SMART CHECK: Does this device have a real camera? (Simulator = No, Physical iPhone = Yes)
        if (UIImagePickerController.isSourceTypeAvailable(UIImagePickerControllerSourceType.UIImagePickerControllerSourceTypeCamera)) {
            picker.sourceType = UIImagePickerControllerSourceType.UIImagePickerControllerSourceTypeCamera
        } else {
            // Fallback for Mac Simulator testing
            picker.sourceType = UIImagePickerControllerSourceType.UIImagePickerControllerSourceTypePhotoLibrary
        }

        picker.delegate = imagePickerDelegate

        // 4. Grab the active iOS screen and push the camera on top of it
        val window = UIApplication.sharedApplication.keyWindow
        val rootVc = window?.rootViewController

        rootVc?.presentViewController(picker, animated = true, completion = null)
    }

    return cameraManager
}