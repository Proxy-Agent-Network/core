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
            .setSmallIcon(android.R.drawable.ic_dialog_alert)
            .setContentTitle(title)
            .setContentText(messageBody)
            .setAutoCancel(true)
            .setSound(defaultSoundUri)
            .setPriority(NotificationCompat.PRIORITY_MAX)
            .setContentIntent(pendingIntent)

        val notificationManager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager

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