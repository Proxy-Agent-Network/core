package com.pan.tactical.hardware

import android.annotation.SuppressLint
import android.bluetooth.*
import android.bluetooth.le.ScanCallback
import android.bluetooth.le.ScanFilter
import android.bluetooth.le.ScanResult
import android.bluetooth.le.ScanSettings
import android.content.Context
import android.os.ParcelUuid
import android.util.Log
import kotlinx.coroutines.*
import java.util.UUID
import java.util.concurrent.atomic.AtomicBoolean

class AndroidBleClient(private val context: Context) : BleHomingClient {
    private val bluetoothManager = context.getSystemService(Context.BLUETOOTH_SERVICE) as BluetoothManager?
    private val bluetoothAdapter = bluetoothManager?.adapter
    private val bleScanner = bluetoothAdapter?.bluetoothLeScanner
    
    private var gattConnection: BluetoothGatt? = null
    private var scanCallback: ScanCallback? = null
    
    // Thread-safe atomic flag retained from Phase 3
    private val isScanning = AtomicBoolean(false)

    companion object {
        private const val TAG = "PAN_BleClient"
        
        // 🟢 THE FIX: Valid Hex UUIDs for PAN Fleet Services
        val PAN_AV_SERVICE_UUID: UUID = UUID.fromString("A0000001-0000-1000-8000-00805F9B34FB")
        val UWB_MAC_CHAR_UUID: UUID = UUID.fromString("A0000002-0000-1000-8000-00805F9B34FB")
        val SESSION_KEY_CHAR_UUID: UUID = UUID.fromString("A0000003-0000-1000-8000-00805F9B34FB")
    }
    
    @SuppressLint("MissingPermission")
    override suspend fun executeOobHandshake(missionId: String): OobHandshakeResult {
        if (bluetoothAdapter == null || !bluetoothAdapter.isEnabled || bleScanner == null) {
            return OobHandshakeResult(false, errorMessage = "BLE Not Supported or Disabled")
        }
        
        // Ensure clean state before starting
        close()
        
        return withContext(Dispatchers.IO) {
            val deferredResult = CompletableDeferred<OobHandshakeResult>()
            
            // 1. Setup the BLE Scan Callback
            scanCallback = object : ScanCallback() {
                override fun onScanResult(callbackType: Int, result: ScanResult) {
                    val device = result.device
                    Log.i(TAG, "📍 Stranded AV Found: ${device.address}. Initiating GATT connection...")
                    
                    // Stop scanning immediately to save battery and prevent duplicate callbacks
                    stopScanning()
                    
                    // 2. Connect to the AV's GATT Server
                    gattConnection = device.connectGatt(context, false, createGattCallback(deferredResult))
                }

                override fun onScanFailed(errorCode: Int) {
                    Log.e(TAG, "❌ BLE Scan Failed with code: $errorCode")
                    stopScanning()
                    deferredResult.complete(OobHandshakeResult(false, errorMessage = "Scan Failed: $errorCode"))
                }
            }

            // Target the specific PAN Fleet Service UUID
            val scanFilter = ScanFilter.Builder()
                .setServiceUuid(ParcelUuid(PAN_AV_SERVICE_UUID))
                .build()
                
            val scanSettings = ScanSettings.Builder()
                .setScanMode(ScanSettings.SCAN_MODE_LOW_LATENCY)
                .build()

            // 3. Execute the Scan with a 15-second timeout safeguard
            try {
                isScanning.set(true)
                bleScanner.startScan(listOf(scanFilter), scanSettings, scanCallback)
                
                withTimeout(15_000L) {
                    deferredResult.await()
                }
            } catch (e: TimeoutCancellationException) {
                Log.w(TAG, "⏳ OOB Handshake Timed Out.")
                stopScanning()
                close()
                OobHandshakeResult(false, errorMessage = "Handshake Timed Out after 15s")
            } catch (e: Exception) {
                Log.e(TAG, "⚠️ OOB Execution Error: ${e.message}")
                stopScanning()
                close()
                OobHandshakeResult(false, errorMessage = e.message)
            }
        }
    }

    @SuppressLint("MissingPermission")
    private fun createGattCallback(deferredResult: CompletableDeferred<OobHandshakeResult>) = object : BluetoothGattCallback() {
        var uwbMacAddress: String? = null
        var sessionKey: ByteArray? = null

        override fun onConnectionStateChange(gatt: BluetoothGatt, status: Int, newState: Int) {
            if (status == BluetoothGatt.GATT_SUCCESS && newState == BluetoothProfile.STATE_CONNECTED) {
                Log.i(TAG, "🔗 Connected to AV GATT Server. Discovering services...")
                gatt.discoverServices()
            } else if (newState == BluetoothProfile.STATE_DISCONNECTED) {
                Log.w(TAG, "⚠️ AV GATT Disconnected (Status: $status).")
                if (!deferredResult.isCompleted) {
                    deferredResult.complete(OobHandshakeResult(false, errorMessage = "GATT Disconnected unexpectedly"))
                }
                close()
            }
        }

        override fun onServicesDiscovered(gatt: BluetoothGatt, status: Int) {
            if (status == BluetoothGatt.GATT_SUCCESS) {
                val service = gatt.getService(PAN_AV_SERVICE_UUID)
                if (service != null) {
                    val macChar = service.getCharacteristic(UWB_MAC_CHAR_UUID)
                    gatt.readCharacteristic(macChar) // Trigger the first read
                } else {
                    deferredResult.complete(OobHandshakeResult(false, errorMessage = "PAN Service not found on AV"))
                    close()
                }
            }
        }

        // 🟢 THE FIX: Documented the minSdk 26 compatibility suppression
        // Using deprecated API intentionally for minSdk 26 compatibility.
        // API 33+ variant: onCharacteristicRead(gatt, characteristic, value, status)
        @Deprecated("Deprecated in Java")
        override fun onCharacteristicRead(gatt: BluetoothGatt, characteristic: BluetoothGattCharacteristic, status: Int) {
            if (status == BluetoothGatt.GATT_SUCCESS) {
                when (characteristic.uuid) {
                    UWB_MAC_CHAR_UUID -> {
                        uwbMacAddress = characteristic.value.decodeToString()
                        Log.i(TAG, "✅ UWB MAC Retrieved: $uwbMacAddress")
                        
                        // Chain the next read
                        val service = gatt.getService(PAN_AV_SERVICE_UUID)
                        val keyChar = service?.getCharacteristic(SESSION_KEY_CHAR_UUID)
                        if (keyChar != null) gatt.readCharacteristic(keyChar)
                    }
                    SESSION_KEY_CHAR_UUID -> {
                        sessionKey = characteristic.value
                        Log.i(TAG, "✅ Secure Session Key Retrieved.")
                        
                        // Both pieces acquired! Complete the coroutine.
                        deferredResult.complete(
                            OobHandshakeResult(
                                success = true,
                                uwbMacAddress = uwbMacAddress,
                                secureSessionKey = sessionKey
                            )
                        )
                        // Disconnect cleanly now that we have the payload
                        close()
                    }
                }
            } else {
                deferredResult.complete(OobHandshakeResult(false, errorMessage = "Failed to read characteristic: $status"))
                close()
            }
        }
    }

    @SuppressLint("MissingPermission")
    override fun stopScanning() {
        if (isScanning.compareAndSet(true, false)) {
            try {
                scanCallback?.let { bleScanner?.stopScan(it) }
            } catch (e: Exception) {
                Log.e(TAG, "Error stopping BLE scan: ${e.message}")
            }
        }
    }

    @SuppressLint("MissingPermission")
    override fun close() {
        stopScanning()
        try {
            gattConnection?.disconnect()
            gattConnection?.close()
        } catch (e: Exception) {
            Log.e(TAG, "Error closing GATT connection: ${e.message}")
        } finally {
            gattConnection = null
        }
    }
}