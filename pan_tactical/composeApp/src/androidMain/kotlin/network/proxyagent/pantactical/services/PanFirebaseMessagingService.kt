package network.proxyagent.pantactical.services

import android.util.Log
import com.google.firebase.messaging.FirebaseMessagingService
import com.google.firebase.messaging.RemoteMessage

class PanFirebaseMessagingService : FirebaseMessagingService() {

    /**
     * This fires when Firebase generates a unique "phone number" (Token) for this specific device.
     * Central Command needs this token to know exactly where to send the push notification.
     */
    override fun onNewToken(token: String) {
        super.onNewToken(token)
        Log.d("PAN_COMMAND", "New Device Dispatch Token Generated: $token")
        // In a live environment, we would send this token to your backend server right here.
    }

    /**
     * This fires the instant a Push Notification arrives from Command.
     */
    override fun onMessageReceived(remoteMessage: RemoteMessage) {
        super.onMessageReceived(remoteMessage)
        Log.d("PAN_COMMAND", "🚨 INCOMING SECURE TRANSMISSION 🚨")

        // 1. Read the hidden data payload (Target Lat/Lon, Error Codes, Bounty)
        if (remoteMessage.data.isNotEmpty()) {
            Log.d("PAN_COMMAND", "Mission Data Payload: ${remoteMessage.data}")

            // TODO: We will wire this to wake up AgentDashboardScreen and show the "ACCEPT / DECLINE" UI
        }

        // 2. Read the visible notification text (if Command sent a standard text alert)
        remoteMessage.notification?.let {
            Log.d("PAN_COMMAND", "Alert Text: ${it.title} - ${it.body}")
        }
    }
}