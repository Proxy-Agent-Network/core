package network.proxyagent.pantactical.sync

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import kotlinx.serialization.Serializable
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import network.proxyagent.pantactical.network.PanApiClient
import java.io.File
import java.io.FileOutputStream

@Serializable
data class PendingClaim(
    val claimId: String,
    val netPayout: Double,
    val localImagePaths: List<String>
)

class OfflineSyncEngine(private val context: Context, private val apiClient: PanApiClient) {

    private val prefs = context.getSharedPreferences("PanSyncQueue", Context.MODE_PRIVATE)

    private fun getQueue(): List<PendingClaim> {
        val jsonStr = prefs.getString("queue", "[]") ?: "[]"
        return try { Json.decodeFromString(jsonStr) } catch(e: Exception) { emptyList() }
    }

    private fun saveQueue(queue: List<PendingClaim>) {
        prefs.edit().putString("queue", Json.encodeToString(queue)).apply()
    }

    // 1. Dumps the evidence to the internal SSD when 5G drops
    suspend fun enqueueClaim(payout: Double, bitmaps: List<Bitmap>) = withContext(Dispatchers.IO) {
        val paths = mutableListOf<String>()
        val timestamp = System.currentTimeMillis()

        bitmaps.forEachIndexed { index, bitmap ->
            // Save to the app's secure internal sandbox (No read/write permissions required)
            val file = File(context.filesDir, "pending_evidence_${timestamp}_$index.jpg")
            FileOutputStream(file).use { out ->
                bitmap.compress(Bitmap.CompressFormat.JPEG, 70, out)
            }
            paths.add(file.absolutePath)
        }

        val newClaim = PendingClaim("claim_$timestamp", payout, paths)
        val queue = getQueue().toMutableList()
        queue.add(newClaim)
        saveQueue(queue)
        println("💾 [SYNC ENGINE] Offline detected. Claim enqueued. Queue size: ${queue.size}")
    }

    // 2. The background sweeper that runs when connection is restored
    suspend fun processQueue() = withContext(Dispatchers.IO) {
        val queue = getQueue()
        if (queue.isEmpty()) return@withContext

        println("🔄 [SYNC ENGINE] Processing ${queue.size} offline claims...")
        val remainingQueue = queue.toMutableList()

        for (claim in queue) {
            try {
                // Read the saved Bitmaps back out of the SSD
                val bitmaps = claim.localImagePaths.mapNotNull { path ->
                    val file = File(path)
                    if (file.exists()) BitmapFactory.decodeFile(path) else null
                }

                if (bitmaps.isNotEmpty()) {
                    // Try to push them to the cloud
                    val uploadedUrls = apiClient.uploadEvidenceArray(bitmaps = bitmaps)

                    // If the upload succeeds, mint the smart contract
                    if (uploadedUrls.isNotEmpty() && apiClient.claimEscrowFunds(netPayout = claim.netPayout, evidenceUrls = uploadedUrls)) {
                        // Success! Scrub the local files to save storage space
                        claim.localImagePaths.forEach { File(it).delete() }
                        remainingQueue.remove(claim)
                        println("✅ [SYNC ENGINE] Offline claim ${claim.claimId} synced to ledger successfully!")
                    } else {
                        throw Exception("Ledger rejection.")
                    }
                } else {
                    // If the files got deleted somehow, drop the claim to prevent infinite loop crashes
                    remainingQueue.remove(claim)
                }
            } catch (e: Exception) {
                println("❌ [SYNC ENGINE] Sync failed for ${claim.claimId}: ${e.message}. Retrying next cycle.")
                // It stays in the queue.
            }
        }
        // Save the updated queue
        saveQueue(remainingQueue)
    }
}