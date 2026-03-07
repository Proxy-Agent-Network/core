package network.proxyagent.pantactical.security

import android.graphics.Bitmap
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Paint
import com.google.mlkit.vision.common.InputImage
import com.google.mlkit.vision.face.FaceDetection
import com.google.mlkit.vision.face.FaceDetectorOptions
import com.google.mlkit.vision.text.TextRecognition
import com.google.mlkit.vision.text.latin.TextRecognizerOptions
import kotlinx.coroutines.tasks.await

object PrivacyFilter {

    suspend fun sanitizeImage(originalBitmap: Bitmap): Bitmap {
        // 1. Create a mutable copy of the bitmap so we can draw on it
        val sanitizedBitmap = originalBitmap.copy(Bitmap.Config.ARGB_8888, true)
        val canvas = Canvas(sanitizedBitmap)

        // Tactical Redaction Paint (Solid Black)
        val paint = Paint().apply {
            color = Color.BLACK
            style = Paint.Style.FILL
        }

        val image = InputImage.fromBitmap(originalBitmap, 0)

        // 2. Configure & Run Face Detection
        val faceOptions = FaceDetectorOptions.Builder()
            .setPerformanceMode(FaceDetectorOptions.PERFORMANCE_MODE_FAST)
            .build()
        val faceDetector = FaceDetection.getClient(faceOptions)

        try {
            val faces = faceDetector.process(image).await()
            for (face in faces) {
                // Expand the bounding box slightly to ensure the whole head is covered
                val rect = face.boundingBox
                rect.inset(-20, -20)
                canvas.drawRect(rect, paint)
            }
        } catch (e: Exception) {
            println("Face detection failed: ${e.message}")
        } finally {
            faceDetector.close()
        }

        // 3. Configure & Run Text Recognition (For License Plates)
        val textRecognizer = TextRecognition.getClient(TextRecognizerOptions.DEFAULT_OPTIONS)

        try {
            val visionText = textRecognizer.process(image).await()
            for (block in visionText.textBlocks) {
                // If it looks like a license plate (alphanumeric block), redact it.
                // For maximum security MVP, we will redact ALL detected text blocks.
                block.boundingBox?.let { rect ->
                    // Expand bounding box slightly
                    rect.inset(-10, -10)
                    canvas.drawRect(rect, paint)
                }
            }
        } catch (e: Exception) {
            println("Text detection failed: ${e.message}")
        } finally {
            textRecognizer.close()
        }

        // Return the newly redacted image
        return sanitizedBitmap
    }
}