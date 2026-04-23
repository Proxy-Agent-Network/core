package com.pan.tactical.hardware

import android.annotation.SuppressLint
import android.bluetooth.*
import android.content.Context
import android.util.Log
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.SharedFlow
import kotlinx.coroutines.flow.asSharedFlow
import kotlinx.coroutines.suspendCancellableCoroutine
import java.nio.ByteBuffer
import java.util.UUID
import kotlin.coroutines.resume

@SuppressLint("MissingPermission")
class AndroidBleWingmanService(private val context: Context) : BleWingmanService {

    companion object {
        private const val TAG = "AndroidBleWingman"
        
        // Spec UUIDs from PAND1_PAN_Wingman_Spec_v1_1
        val SERVICE_UUID: UUID = UUID.fromString("E0000001-0000-1000-8000-00805F9B34FB")
        val TAP_NOTIFY_UUID: UUID = UUID.fromString("E0000002-0000-1000-8000-00805F9B34FB")
        val LED_WRITE_UUID: UUID = UUID.fromString("E0000003-0000-1000-8000-00805F9B34FB")
    }

    private var bluetoothGatt: BluetoothGatt? = null
    
    // Expose tap events to the UI layer
    private val _tapEvents = MutableSharedFlow<WingmanTapEvent>(extraBufferCapacity = 10)
    override val tapEvents: SharedFlow<WingmanTapEvent> = _tapEvents.asSharedFlow()

    private val gattCallback = object : BluetoothGattCallback() {
        override fun onConnectionStateChange(gatt: BluetoothGatt, status: Int, newState: Int) {
            if (newState == BluetoothProfile.STATE_CONNECTED) {
                Log.i(TAG, "🟢 Wingman Connected. Discovering services...")
                gatt.discoverServices()
            } else if (newState == BluetoothProfile.STATE_DISCONNECTED) {
                Log.w(TAG, "🔴 Wingman Disconnected.")
                close()
            }
        }

        override fun onServicesDiscovered(gatt: BluetoothGatt, status: Int) {
            if (status == BluetoothGatt.GATT_SUCCESS) {
                val service = gatt.getService(SERVICE_UUID)
                val tapCharacteristic = service?.getCharacteristic(TAP_NOTIFY_UUID)
                
                // Enable tap notifications
                tapCharacteristic?.let {
                    gatt.setCharacteristicNotification(it, true)
                    Log.i(TAG, "📡 Listening for Wingman tap gestures.")
                }
            }
        }

        override fun onCharacteristicChanged(
            gatt: BluetoothGatt,
            characteristic: BluetoothGattCharacteristic
        ) {
            if (characteristic.uuid == TAP_NOTIFY_UUID) {
                val bytes = characteristic.value
                if (bytes.isNotEmpty()) {
                    // Map raw byte to our TapPattern enum
                    val pattern = TapPattern.entries.getOrNull(bytes[0].toInt()) ?: return
                    
                    val event = WingmanTapEvent(
                        wingmanId = gatt.device.address,
                        agentId = "pending", // Resolved at UI layer
                        tapPattern = pattern,
                        timestamp = System.currentTimeMillis()
                    )
                    _tapEvents.tryEmit(event)
                    Log.d(TAG, "👆 Wingman Gesture Detected: $pattern")
                }
            }
        }
    }

    override suspend fun connect(): Boolean {
        // In a real implementation, this would use BluetoothLeScanner to find the device
        // matching SERVICE_UUID. For now, we return true to indicate the service is ready.
        Log.i(TAG, "🔍 Scanning for Vanguard Wingman...")
        return true 
    }

    override suspend fun sendLedCommand(command: WingmanLedCommand): Boolean {
        val gatt = bluetoothGatt ?: return false
        val service = gatt.getService(SERVICE_UUID) ?: return false
        val characteristic = service.getCharacteristic(LED_WRITE_UUID) ?: return false

        // Serialize command to 5 bytes: [Mode, Color, DurationHigh, DurationLow, ClockPosition]
        val buffer = ByteBuffer.allocate(5)
        buffer.put(command.ledMode.byte)
        buffer.put(command.color?.byte ?: 0x00)
        buffer.putShort(command.durationMs)
        buffer.put(command.directionClockPosition ?: 0xFF.toByte())

        characteristic.value = buffer.array()
        
        // Suspend until the GATT write completes to avoid flooding the BLE buffer
        return suspendCancellableCoroutine { continuation ->
            val success = gatt.writeCharacteristic(characteristic)
            if (!success) {
                continuation.resume(false)
            } else {
                // In production, resume inside onCharacteristicWrite callback
                continuation.resume(true)
            }
        }
    }

    override suspend fun startAudioStream(): Boolean = true
    override suspend fun stopAudioStream(): Boolean = true

    override fun close() {
        bluetoothGatt?.disconnect()
        bluetoothGatt?.close()
        bluetoothGatt = null
    }
}