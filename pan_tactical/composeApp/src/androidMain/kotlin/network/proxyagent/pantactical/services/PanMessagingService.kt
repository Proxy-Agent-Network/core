package network.proxyagent.pantactical.services

import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.media.RingtoneManager
import android.os.Build
import androidx.core.app.NotificationCompat
import com.google.firebase.messaging.FirebaseMessagingService
import com.google.firebase.messaging.RemoteMessage

class PanMessagingService : FirebaseMessagingService() {

    // 1. This triggers whenever Google assigns a new routing token to this specific phone
    override fun onNewToken(token: String) {
        super.onNewToken(token)
        println("📡 [FCM TELEMETRY] New Hardware Routing Token Generated: $token")
        // In the future, we will upload this token to the agent's Firebase RTDB profile
        // so the dispatch server knows exactly where to send the push payload.
    }

    // 2. This triggers when a secure payload hits the phone
    override fun onMessageReceived(remoteMessage: RemoteMessage) {
        super.onMessageReceived(remoteMessage)
        println("🚨 [FCM TELEMETRY] TACTICAL PAYLOAD RECEIVED!")

        // Extract the data from the Firebase payload
        val title = remoteMessage.data["title"] ?: remoteMessage.notification?.title ?: "🚨 PRIORITY DISPATCH"
        val body = remoteMessage.data["body"] ?: remoteMessage.notification?.body ?: "A new AV requires immediate assistance."

        sendNotification(title, body)
    }

    // 3. Build the high-priority Heads-Up Notification
    private fun sendNotification(title: String, messageBody: String) {
        // When they tap the notification, open the main app
        // Note: Change 'network.proxyagent.pantactical.MainActivity' if your main activity is named differently
        val intent = Intent(this, Class.forName("network.proxyagent.pantactical.MainActivity")).apply {
            addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP)
        }

        val pendingIntent = PendingIntent.getActivity(
            this, 0, intent,
            PendingIntent.FLAG_ONE_SHOT or PendingIntent.FLAG_IMMUTABLE
        )

        val channelId = "VANGUARD_DISPATCH_CHANNEL"
        val defaultSoundUri = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION)

        val notificationBuilder = NotificationCompat.Builder(this, channelId)
            .setSmallIcon(android.R.drawable.ic_dialog_alert) // Standard alert icon
            .setContentTitle(title)
            .setContentText(messageBody)
            .setAutoCancel(true)
            .setSound(defaultSoundUri)
            // MAX Priority forces it to drop down from the top of the screen (Heads-up)
            .setPriority(NotificationCompat.PRIORITY_MAX)
            .setContentIntent(pendingIntent)

        val notificationManager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager

        // Android 8.0+ requires an explicit Notification Channel
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                channelId,
                "Tactical Dispatch Alerts",
                NotificationManager.IMPORTANCE_HIGH
            ).apply {
                description = "Critical rescue alerts for stranded autonomous vehicles."
                enableLights(true)
                enableVibration(true)
            }
            notificationManager.createNotificationChannel(channel)
        }

        notificationManager.notify(System.currentTimeMillis().toInt(), notificationBuilder.build())
    }
}