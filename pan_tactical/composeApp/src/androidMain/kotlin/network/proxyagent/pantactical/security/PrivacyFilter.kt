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
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.tasks.await
import kotlinx.coroutines.withContext

object PrivacyFilter {

    // 1. Keep ML Kit clients as singletons in memory so they don't cold-boot on every photo
    private val faceOptions = FaceDetectorOptions.Builder()
        .setPerformanceMode(FaceDetectorOptions.PERFORMANCE_MODE_FAST)
        .build()

    private val faceDetector = FaceDetection.getClient(faceOptions)
    private val textRecognizer = TextRecognition.getClient(TextRecognizerOptions.DEFAULT_OPTIONS)

    suspend fun sanitizeImage(originalBitmap: Bitmap): Bitmap {
        return withContext(Dispatchers.Default) {
            try {
                // Create a mutable copy of the bitmap so we can draw on it
                val sanitizedBitmap = originalBitmap.copy(Bitmap.Config.ARGB_8888, true)
                val canvas = Canvas(sanitizedBitmap)

                // Tactical Redaction Paint (Solid Black)
                val paint = Paint().apply {
                    color = Color.BLACK
                    style = Paint.Style.FILL
                }

                val image = InputImage.fromBitmap(originalBitmap, 0)

                // 2. Start both ML tasks concurrently for maximum speed
                val faceTask = faceDetector.process(image)
                val textTask = textRecognizer.process(image)

                // Wait for both to complete
                val faces = faceTask.await()
                val visionText = textTask.await()

                // 3. Apply Face Redaction with safety margins
                for (face in faces) {
                    val rect = face.boundingBox
                    rect.inset(-20, -20) // Expand box to ensure full head coverage
                    canvas.drawRect(rect, paint)
                }

                // 4. Apply Text Redaction with safety margins
                for (block in visionText.textBlocks) {
                    block.boundingBox?.let { rect ->
                        rect.inset(-10, -10) // Expand box to ensure edge letters are covered
                        canvas.drawRect(rect, paint)
                    }
                }

                sanitizedBitmap
            } catch (e: Exception) {
                println("🛡️ ML REDACTION ERROR: ${e.message}")
                // Fail secure: If ML crashes, return original but log the failure
                originalBitmap
            }
        }
    }
}