package network.proxyagent.pantactical.services

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.Context
import android.content.Intent
import android.os.Build
import android.os.IBinder
import android.os.Looper
import androidx.core.app.NotificationCompat
import com.google.android.gms.location.*
import kotlinx.coroutines.*
import network.proxyagent.pantactical.network.PanApiClient
import network.proxyagent.pantactical.R // Keeping your custom tactical icon!

class PanLocationService : Service() {

    private val apiClient = PanApiClient()
    private val serviceJob = SupervisorJob()
    private val serviceScope = CoroutineScope(Dispatchers.IO + serviceJob)

    private lateinit var fusedLocationClient: FusedLocationProviderClient
    private lateinit var locationCallback: LocationCallback

    private val CHANNEL_ID = "PAN_TACTICAL_UPLINK"

    override fun onCreate() {
        super.onCreate()
        createNotificationChannel()
        fusedLocationClient = LocationServices.getFusedLocationProviderClient(this)

        locationCallback = object : LocationCallback() {
            override fun onLocationResult(locationResult: LocationResult) {
                for (location in locationResult.locations) {
                    println("🛰️ [GPS TELEMETRY] Live Lock: ${location.latitude}, ${location.longitude}")
                    // Stream coordinates silently to your specific Firebase UID
                    serviceScope.launch {
                        apiClient.updateLocationTelemetry(location.latitude, location.longitude)
                    }
                }
            }
        }
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // Start the foreground presence to prevent battery optimization kills
        startForeground(1417, createNotification())
        requestLocationUpdates()

        return START_STICKY
    }

    override fun onBind(intent: Intent?): IBinder? {
        return null
    }

    override fun onDestroy() {
        super.onDestroy()
        fusedLocationClient.removeLocationUpdates(locationCallback)
        serviceJob.cancel()
        println("🛰️ [GPS TELEMETRY] Location Service Terminated.")
    }

    private fun requestLocationUpdates() {
        val locationRequest = LocationRequest.Builder(Priority.PRIORITY_HIGH_ACCURACY, 5000)
            .setMinUpdateDistanceMeters(5f) // Ping server only if moved 5 meters
            .build()

        try {
            fusedLocationClient.requestLocationUpdates(
                locationRequest,
                locationCallback,
                Looper.getMainLooper()
            )
        } catch (unlikely: SecurityException) {
            println("🛰️ [GPS ERROR] Missing location permissions.")
        }
    }

    private fun createNotification(): Notification {
        val intent = Intent(this, Class.forName("network.proxyagent.pantactical.MainActivity")).apply {
            addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP)
        }
        val pendingIntent = PendingIntent.getActivity(
            this, 0, intent,
            PendingIntent.FLAG_ONE_SHOT or PendingIntent.FLAG_IMMUTABLE
        )

        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("🟢 PAN COMMAND: ONLINE")
            .setContentText("Streaming encrypted GPS telemetry to Dispatch...")
            .setSmallIcon(R.drawable.ic_stat_pan_logo) // Your tactical icon
            .setPriority(NotificationCompat.PRIORITY_HIGH) // Keeps it visible
            .setContentIntent(pendingIntent)
            .setOngoing(true) // Cannot be swiped away
            .build()
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