package com.pan.tactical.hardware

import android.content.Context
import android.content.pm.PackageManager
import android.util.Log
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlin.math.cos
import kotlin.math.sin

class AndroidUwbClient(private val context: Context) : UwbClient {

    companion object {
        private const val TAG = "AndroidUwbClient"
    }

    private val _rangingState = MutableStateFlow(UwbRangingResult())
    override val rangingState: StateFlow<UwbRangingResult> = _rangingState.asStateFlow()

    private var rangingJob: Job? = null
    private val coroutineScope = CoroutineScope(Dispatchers.Default + SupervisorJob())

    private val hasUwbHardware: Boolean
        get() = context.packageManager.hasSystemFeature(PackageManager.FEATURE_UWB)

    override suspend fun startRanging(avMacAddress: String, secureSessionKey: ByteArray): Boolean {
        if (rangingJob?.isActive == true) return true

        if (!hasUwbHardware) {
            startSimulationLoop()
            return true
        }

        try {
            startSimulationLoop()
            return true
        } catch (e: Exception) {
            return false
        }
    }

    override fun stopRanging() {
        // TODO: BleHapHatService — Send MOTOR_ALL_STOP and LED_OFF payload on ranging end.
        rangingJob?.cancel()
        rangingJob = null
        
        _rangingState.update { 
            UwbRangingResult(
                isRanging = false, 
                distanceMeters = null, 
                azimuthDegrees = null, 
                elevationDegrees = null
            ) 
        }
    }

    // 🟢 THE FIX: Added the 'override' modifier to satisfy the UwbClient interface
    override fun close() {
        stopRanging()
        coroutineScope.cancel()
    }

    private fun startSimulationLoop() {
        rangingJob = coroutineScope.launch {
            _rangingState.update { it.copy(isRanging = true) }
            
            var simulatedDistance = 15.0f 
            var timeTicks = 0f

            while (isActive) {
                if (simulatedDistance > 0.5f) {
                    simulatedDistance -= 0.05f 
                }

                val simulatedAzimuth = (sin(timeTicks) * 30f) 
                val simulatedElevation = -5.0f + (cos(timeTicks * 0.5f) * 2f) 

                _rangingState.update {
                    it.copy(
                        isRanging = true,
                        distanceMeters = simulatedDistance,
                        azimuthDegrees = simulatedAzimuth,
                        elevationDegrees = simulatedElevation,
                        vehicleHeadingDegrees = 180f 
                    )
                }

                // TODO: BleHapHatService — Consume UwbRangingResult here to drive directional crown haptics & LED.
                // Translate azimuthDegrees → [MOTOR_ID_LEFT | MOTOR_ID_RIGHT] and distanceMeters → pulse frequency.
                // Distance > 15ft: 1Hz slow pulse. Distance < 15ft: inverse scale. Distance <= 2ft: triple burst.
                // BLE payload format: [MOTOR_ID, PULSE_SPEED, LED_MODE, LED_COLOR] → nRF52 crown controller via BleHapHatService.kt
                // LED_MODE: 0x00=OFF, 0x01=SOLID, 0x02=PULSE, 0x03=STROBE
                // LED_COLOR: 0x01=WHITE(task), 0x02=CYAN(ranging), 0x03=GREEN(strike zone), 0x04=RED(alert), 0x05=AMBER(caution)

                timeTicks += 0.1f
                delay(100) 
            }
        }
    }
}