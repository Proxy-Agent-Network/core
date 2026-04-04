package com.pan.tactical.security

import android.graphics.Bitmap
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Paint
import android.util.Log
import com.google.mlkit.vision.common.InputImage
import com.google.mlkit.vision.face.FaceDetection
import com.google.mlkit.vision.face.FaceDetectorOptions
import com.google.mlkit.vision.text.TextRecognition
import com.google.mlkit.vision.text.latin.TextRecognizerOptions
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.async
import kotlinx.coroutines.coroutineScope
import kotlinx.coroutines.tasks.await
import kotlinx.coroutines.withContext
import kotlin.math.min

object PrivacyFilter {

    private const val TAG = "PrivacyFilter"
    private const val MAX_DIMENSION = 1280
    private const val FACE_EXPANSION_PX = 20
    private const val TEXT_EXPANSION_PX = 10

    private val faceOptions = FaceDetectorOptions.Builder()
        .setPerformanceMode(FaceDetectorOptions.PERFORMANCE_MODE_FAST)
        .build()

    private val faceDetector = FaceDetection.getClient(faceOptions)
    private val textRecognizer = TextRecognition.getClient(TextRecognizerOptions.DEFAULT_OPTIONS)

    /**
     * Sanitizes a frame by redacting PII (faces/text).
     * 🛡️ STRICT CONTRACT: This function takes absolute ownership of [originalBitmap].
     * It will ALWAYS be recycled before this function returns. Do not use it after calling.
     */
    suspend fun sanitizeImage(originalBitmap: Bitmap): Bitmap {
        return withContext(Dispatchers.Default) {
            try {
                // 🛡️ FIXED: Moved Paint instantiation inside the function to prevent shared mutable state issues
                // if this is ever called concurrently from multiple coroutines.
                val redactionPaint = Paint().apply {
                    color = Color.BLACK
                    style = Paint.Style.FILL
                }

                val scale = minOf(
                    MAX_DIMENSION.toFloat() / originalBitmap.width,
                    MAX_DIMENSION.toFloat() / originalBitmap.height,
                    1.0f
                )

                // 1. Create a scaled working copy if necessary, or point to original
                val workingBitmap = if (scale < 1.0f) {
                    Bitmap.createScaledBitmap(
                        originalBitmap,
                        (originalBitmap.width * scale).toInt(),
                        (originalBitmap.height * scale).toInt(),
                        true
                    )
                } else {
                    originalBitmap
                }

                // 2. Create the final mutable ARGB_8888 canvas target
                val sanitizedBitmap = workingBitmap.copy(Bitmap.Config.ARGB_8888, true)
                
                // 3. Clean up intermediate references immediately
                if (workingBitmap !== originalBitmap) {
                    workingBitmap.recycle()
                }
                // 🛡️ UNCONDITIONAL RECYCLE: We own the input, we destroy it to prevent leaks.
                if (!originalBitmap.isRecycled) {
                    originalBitmap.recycle()
                }

                val canvas = Canvas(sanitizedBitmap)
                val image = InputImage.fromBitmap(sanitizedBitmap, 0)

                // 4. Concurrent ML Redaction
                val (faces, visionText) = coroutineScope {
                    val facesDeferred = async { faceDetector.process(image).await() }
                    val textDeferred = async { textRecognizer.process(image).await() }
                    Pair(facesDeferred.await(), textDeferred.await())
                }

                for (face in faces) {
                    val rect = face.boundingBox
                    // 🛡️ FIXED: Negative inset intentionally EXPANDS the bounding box outward
                    rect.inset(-FACE_EXPANSION_PX, -FACE_EXPANSION_PX)
                    
                    // 🛡️ FIXED: Clamp to bounds to prevent negative coordinates or exceeding bitmap dimensions
                    rect.left = rect.left.coerceAtLeast(0)
                    rect.top = rect.top.coerceAtLeast(0)
                    rect.right = rect.right.coerceAtMost(sanitizedBitmap.width)
                    rect.bottom = rect.bottom.coerceAtMost(sanitizedBitmap.height)
                    
                    canvas.drawRect(rect, redactionPaint)
                }

                for (block in visionText.textBlocks) {
                    block.boundingBox?.let { rect ->
                        // 🛡️ FIXED: Negative inset intentionally EXPANDS the bounding box outward
                        rect.inset(-TEXT_EXPANSION_PX, -TEXT_EXPANSION_PX)
                        
                        // 🛡️ FIXED: Clamp to bounds to prevent negative coordinates or exceeding bitmap dimensions
                        rect.left = rect.left.coerceAtLeast(0)
                        rect.top = rect.top.coerceAtLeast(0)
                        rect.right = rect.right.coerceAtMost(sanitizedBitmap.width)
                        rect.bottom = rect.bottom.coerceAtMost(sanitizedBitmap.height)
                        
                        canvas.drawRect(rect, redactionPaint)
                    }
                }

                sanitizedBitmap
                
            } catch (e: Throwable) {
                Log.e(TAG, "🛡️ ML REDACTION FATAL: ${e.message}. Returning fail-safe.")
                
                // Ensure cleanup even on crash
                if (!originalBitmap.isRecycled) originalBitmap.recycle()
                
                try {
                    val blackout = Bitmap.createBitmap(MAX_DIMENSION, MAX_DIMENSION, Bitmap.Config.ARGB_8888)
                    Canvas(blackout).drawColor(Color.BLACK)
                    blackout
                } catch (oom: OutOfMemoryError) {
                    val tinyBlackout = Bitmap.createBitmap(1, 1, Bitmap.Config.ARGB_8888)
                    tinyBlackout.setPixel(0, 0, Color.BLACK)
                    tinyBlackout
                }
            }
        }
    }
}