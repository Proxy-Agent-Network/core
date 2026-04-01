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

object PrivacyFilter {

    private const val TAG = "PrivacyFilter"

    // Explicitly named as "EXPANSION" with positive values to prevent Rect.inset() confusion
    private const val FACE_EXPANSION_PX = 20
    private const val TEXT_EXPANSION_PX = 10

    // 1. Keep ML Kit clients as singletons in memory so they don't cold-boot on every photo
    private val faceOptions = FaceDetectorOptions.Builder()
        .setPerformanceMode(FaceDetectorOptions.PERFORMANCE_MODE_FAST)
        .build()

    private val faceDetector = FaceDetection.getClient(faceOptions)
    private val textRecognizer = TextRecognition.getClient(TextRecognizerOptions.DEFAULT_OPTIONS)

    // Tactical Redaction Paint (Solid Black) 
    // Instantiated once to prevent Garbage Collection (GC) churn during 3fps camera streams
    private val redactionPaint = Paint().apply {
        color = Color.BLACK
        style = Paint.Style.FILL
    }

    suspend fun sanitizeImage(originalBitmap: Bitmap): Bitmap {
        return withContext(Dispatchers.Default) {
            try {
                // Create a mutable copy. 
                // Deliberately normalizing to ARGB_8888 for consistent Canvas drawing behavior, 
                // even if the camera pipeline feeds a memory-saving RGB_565 frame.
                val sanitizedBitmap = originalBitmap.copy(Bitmap.Config.ARGB_8888, true)
                val canvas = Canvas(sanitizedBitmap)

                val image = InputImage.fromBitmap(originalBitmap, 0)

                // 2. Explicit Coroutine Concurrency for ML Tasks
                val (faces, visionText) = coroutineScope {
                    val facesDeferred = async { faceDetector.process(image).await() }
                    val textDeferred = async { textRecognizer.process(image).await() }
                    
                    Pair(facesDeferred.await(), textDeferred.await())
                }

                // 3. Apply Face Redaction with safety margins
                for (face in faces) {
                    val rect = face.boundingBox
                    // Negating the positive expansion constant to correctly grow the Rect
                    rect.inset(-FACE_EXPANSION_PX, -FACE_EXPANSION_PX) 
                    canvas.drawRect(rect, redactionPaint)
                }

                // 4. Apply Text Redaction with safety margins
                for (block in visionText.textBlocks) {
                    block.boundingBox?.let { rect ->
                        // Negating the positive expansion constant to correctly grow the Rect
                        rect.inset(-TEXT_EXPANSION_PX, -TEXT_EXPANSION_PX) 
                        canvas.drawRect(rect, redactionPaint)
                    }
                }

                sanitizedBitmap
                
            } catch (e: Throwable) {
                // CATCHING THROWABLE: This ensures we catch OutOfMemoryError (which is an Error, not an Exception)
                // If the ESP32-CAM sends a burst of frames and maxes out RAM, we fail-secure here.
                Log.e(TAG, "🛡️ ML REDACTION FATAL ERROR: ${e.message}. Returning fail-safe frame.")
                
                try {
                    // True fail-secure: Black out the entire frame rather than leak PII
                    val blackout = Bitmap.createBitmap(originalBitmap.width, originalBitmap.height, Bitmap.Config.ARGB_8888)
                    val canvas = Canvas(blackout)
                    canvas.drawColor(Color.BLACK)
                    blackout
                } catch (oom: OutOfMemoryError) {
                    // Absolute last resort if the phone is too choked to even allocate a blackout bitmap.
                    // Returns a 1x1 black pixel. The Ops Hub receives a safe, redacted (though tiny) frame.
                    val tinyBlackout = Bitmap.createBitmap(1, 1, Bitmap.Config.ARGB_8888)
                    tinyBlackout.setPixel(0, 0, Color.BLACK)
                    tinyBlackout
                }
            }
        }
    }
}