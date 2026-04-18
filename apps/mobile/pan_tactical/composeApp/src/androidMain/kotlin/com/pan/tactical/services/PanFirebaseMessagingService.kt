package com.pan.tactical.services

import android.util.Log
import com.google.firebase.messaging.FirebaseMessagingService
import com.google.firebase.messaging.RemoteMessage
import com.pan.tactical.managers.MissionEventManager
import com.pan.tactical.network.PanApiClient
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.cancel
import kotlinx.coroutines.launch

class PanFirebaseMessagingService : FirebaseMessagingService() {

    companion object {
        private const val TAG = "PanFCM"
    }

    // 🛡️ PHASE 4 FIX: Use a tied CoroutineScope instead of GlobalScope to prevent memory leaks
    private val serviceScope = CoroutineScope(SupervisorJob() + Dispatchers.IO)

    override fun onMessageReceived(message: RemoteMessage) {
        super.onMessageReceived(message)
        
        // We strictly use data payloads for tactical operations to avoid OS-level notification grouping
        val data = message.data
        if (data.isEmpty()) return

        Log.d(TAG, "📥 Received Tactical FCM: ${data["type"]}")

        when (data["type"]) {
            "SENTRY_EXTENSION_OFFER" -> {
                val taskId = data["task_id"] ?: run {
                    Log.w(TAG, "SENTRY_EXTENSION_OFFER missing task_id — discarding")
                    return
                }
                
                val minutes = data["extension_minutes"]?.toIntOrNull() ?: run { 
                    Log.w(TAG, "Missing extension_minutes in payload, using default 10")
                    10 
                }
                val bountyUsd = data["bounty_usd"]?.toDoubleOrNull() ?: run { 
                    Log.w(TAG, "Missing bounty_usd in payload, using default 5.00")
                    5.00 
                }

                MissionEventManager.triggerExtensionRequest(taskId, minutes, bountyUsd)
            }
            "NEW_DISPATCH" -> {
                // TODO: Wire up the phase 5 "Next Up" sticky queue trigger
            }
            else -> {
                Log.w(TAG, "Unknown FCM payload type: ${data["type"]}")
            }
        }
    }

    override fun onNewToken(token: String) {
        super.onNewToken(token)
        Log.i(TAG, "🔑 New FCM Device Token generated.")
        
        // 🛡️ PHASE 4 FIX: Launch on the Service's dedicated scope
        serviceScope.launch {
            try {
                val client = PanApiClient()
                client.registerFcmToken(token)
                client.close() // Close the client engine to free resources immediately
            } catch (e: Exception) {
                Log.e(TAG, "Failed to register FCM token: ${e.message}")
            }
        }
    }

    // 🛡️ PHASE 4 FIX: Clean up all running coroutines when the OS destroys the service
    override fun onDestroy() {
        super.onDestroy()
        serviceScope.cancel()
    }
}