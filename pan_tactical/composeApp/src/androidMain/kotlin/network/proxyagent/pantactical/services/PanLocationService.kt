package network.proxyagent.pantactical.services

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.Service
import android.content.Context
import android.content.Intent
import android.os.Build
import android.os.IBinder
import androidx.core.app.NotificationCompat

// THIS IS THE MISSING LINK:
import network.proxyagent.pantactical.R

class PanLocationService : Service() {

    private val CHANNEL_ID = "PAN_TACTICAL_UPLINK"

    override fun onCreate() {
        super.onCreate()
        createNotificationChannel()
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // Build the persistent tactical notification
        val notification: Notification = NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("🟢 PAN COMMAND: ONLINE")
            .setContentText("Secure uplink active. Awaiting AV dispatch...")
            .setSmallIcon(R.drawable.ic_stat_pan_logo) // Now pointing to your new tactical icon!
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setOngoing(true) // Makes it un-swipeable
            .build()

        // Force the OS to keep our app alive by attaching this notification
        startForeground(1, notification)

        // START_STICKY tells the OS to restart this service if it gets killed under extreme memory load
        return START_STICKY
    }

    override fun onDestroy() {
        super.onDestroy()
        // Clean up when the agent goes offline
    }

    override fun onBind(intent: Intent?): IBinder? {
        // We don't need bound services for this architecture
        return null
    }

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val serviceChannel = NotificationChannel(
                CHANNEL_ID,
                "PAN Tactical Dispatch",
                NotificationManager.IMPORTANCE_HIGH
            )
            serviceChannel.description = "Maintains persistent GPS uplink for AV rescue dispatch."
            val manager = getSystemService(NotificationManager::class.java)
            manager.createNotificationChannel(serviceChannel)
        }
    }
}