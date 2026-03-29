package com.pan.tactical.sync

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.util.Log
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import kotlinx.coroutines.withContext
import kotlinx.serialization.Serializable
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import com.pan.tactical.ui.WalletNetworkClient
import java.io.File
import java.io.FileOutputStream

@Serializable
data class PendingClaim(
    val taskId: String, 
    val localImagePaths: List<String>
)

class OfflineSyncEngine(
    private val context: Context, 
    private val apiClient: WalletNetworkClient,
    private val uploadEvidence: suspend (List<Bitmap>) -> List<String> // 🟢 THE FIX: Decoupled DI
) {

    companion object {
        private const val TAG = "OfflineSyncEngine"
    }

    private val prefs = context.getSharedPreferences("PanSyncQueue", Context.MODE_PRIVATE)
    
    // 🟢 THE FIX: Concurrency lock for safe Read-Modify-Write cycles
    private val queueMutex = Mutex()

    private fun getQueue(): MutableList<PendingClaim> {
        val jsonStr = prefs.getString("queue", "[]") ?: "[]"
        return try { 
            Json.decodeFromString<List<PendingClaim>>(jsonStr).toMutableList() 
        } catch(e: Exception) { 
            mutableListOf() 
        }
    }

    private fun saveQueue(queue: List<PendingClaim>) {
        prefs.edit().putString("queue", Json.encodeToString(queue)).apply()
    }

    // 1. Dumps the evidence to the internal SSD when 5G drops
    suspend fun enqueueClaim(taskId: String, bitmaps: List<Bitmap>) = withContext(Dispatchers.IO) {
        val paths = mutableListOf<String>()
        val timestamp = System.currentTimeMillis()
        
        bitmaps.forEachIndexed { index, bitmap ->
            try {
                // Save to internal storage so it can't be tampered with by other apps
                val file = File(context.filesDir, "evidence_${taskId}_${timestamp}_$index.jpg")
                
                // 🟢 THE FIX: Safe resource management via 'use {}'
                FileOutputStream(file).use { out ->
                    bitmap.compress(Bitmap.CompressFormat.JPEG, 80, out)
                }
                paths.add(file.absolutePath)
            } catch (e: Exception) {
                Log.e(TAG, "Failed to save offline evidence locally: ${e.message}")
            }
        }

        // Lock the queue, append, and save
        queueMutex.withLock {
            val queue = getQueue()
            queue.add(PendingClaim(taskId = taskId, localImagePaths = paths))
            saveQueue(queue)
        }
        
        Log.i(TAG, "✅ [SYNC ENGINE] Mission $taskId queued for offline sync with ${paths.size} images.")
    }

    // 2. Tries to push all pending claims when connection is restored
    suspend fun syncPendingClaims() = withContext(Dispatchers.IO) {
        // Take a snapshot of the queue to iterate over so we don't hold the lock during long network calls
        val claimsToProcess = queueMutex.withLock { getQueue().toList() }
        if (claimsToProcess.isEmpty()) return@withContext

        Log.i(TAG, "🔄 [SYNC ENGINE] Attempting to sync ${claimsToProcess.size} offline claims...")

        for (claim in claimsToProcess) {
            try {
                // Rehydrate bitmaps from disk
                val bitmaps = claim.localImagePaths.mapNotNull { path ->
                    val file = File(path)
                    if (file.exists()) BitmapFactory.decodeFile(path) else null
                }

                if (bitmaps.isNotEmpty()) {
                    // 1. Push evidence to the cloud via the injected lambda
                    val uploadedUrls = uploadEvidence(bitmaps)

                    // 2. If upload succeeds, finalize the mission via the Python backend
                    if (uploadedUrls.isNotEmpty() && apiClient.completeMission(taskId = claim.taskId, evidenceUrls = uploadedUrls)) {
                        // Success! Scrub the local files to save storage space
                        claim.localImagePaths.forEach { File(it).delete() }
                        
                        // Safely remove the claim from the real queue
                        queueMutex.withLock {
                            val currentQueue = getQueue()
                            currentQueue.removeAll { it.taskId == claim.taskId }
                            saveQueue(currentQueue)
                        }
                        Log.i(TAG, "✅ [SYNC ENGINE] Offline claim for task ${claim.taskId} synced to ledger successfully!")
                    } else {
                        throw Exception("Backend rejection or evidence upload failed.")
                    }
                } else {
                    // If the files got deleted somehow, drop the claim to prevent infinite loop crashes
                    Log.w(TAG, "⚠️ [SYNC ENGINE] Local evidence missing for task ${claim.taskId}. Dropping claim.")
                    queueMutex.withLock {
                        val currentQueue = getQueue()
                        currentQueue.removeAll { it.taskId == claim.taskId }
                        saveQueue(currentQueue)
                    }
                }
            } catch (e: Exception) {
                Log.e(TAG, "❌ [SYNC ENGINE] Sync failed for ${claim.taskId}: ${e.message}. Retrying next cycle.")
                // It stays in the queue to be retried next time.
            }
        }
    }
}