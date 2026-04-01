package com.pan.tactical.services

import android.util.Log
import com.google.firebase.messaging.FirebaseMessagingService
import com.google.firebase.messaging.RemoteMessage
import com.pan.tactical.managers.MissionEventManager
import com.pan.tactical.network.PanApiClient
import kotlinx.coroutines.DelicateCoroutinesApi
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.GlobalScope
import kotlinx.coroutines.launch

class PanFirebaseMessagingService : FirebaseMessagingService() {

    companion object {
        private const val TAG = "PanFCM"
    }

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
                
                // Safely parse the incoming strings with visible warnings for malformed payloads
                val minutes = data["extension_minutes"]?.toIntOrNull() ?: run { 
                    Log.w(TAG, "Missing extension_minutes in payload, using default 10")
                    10 
                }
                val bountyUsd = data["bounty_usd"]?.toDoubleOrNull() ?: run { 
                    Log.w(TAG, "Missing bounty_usd in payload, using default 5.00")
                    5.00 
                }

                // Fire the event to wake up the Compose UI
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

    @OptIn(DelicateCoroutinesApi::class)
    override fun onNewToken(token: String) {
        super.onNewToken(token)
        Log.i(TAG, "🔑 New FCM Device Token generated.")
        
        // Launch on a background scope — onNewToken runs on main thread and the 
        // service lifecycle is too short for scoped coroutines
        GlobalScope.launch(Dispatchers.IO) {
            try {
                // NOTE: Requires adding registerFcmToken(token: String) to PanApiClient
                PanApiClient().registerFcmToken(token)
            } catch (e: Exception) {
                Log.e(TAG, "Failed to register FCM token: ${e.message}")
            }
        }
    }
}