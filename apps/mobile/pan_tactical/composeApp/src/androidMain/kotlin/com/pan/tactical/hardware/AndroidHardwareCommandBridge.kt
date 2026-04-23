package com.pan.tactical.hardware

import android.util.Log
import kotlinx.coroutines.async
import kotlinx.coroutines.coroutineScope

class AndroidHardwareCommandBridge(
    private val hapHat: BleHapHatService,
    private val wingman: BleWingmanService // 🟢 NEW: Added Wingman dependency
) : HardwareCommandBridge {

    companion object {
        private const val TAG = "AndroidHardwareBridge"
    }

    override suspend fun connect(): Boolean {
        // Connect to both peripherals concurrently
        return coroutineScope {
            val hatConnected = async { hapHat.connect() }
            val wingmanConnected = async { wingman.connect() }
            
            val hatRes = try { hatConnected.await() } catch (e: Exception) { false }
            val wingmanRes = try { wingmanConnected.await() } catch (e: Exception) { false }
            
            if (!hatRes && !wingmanRes) {
                Log.e(TAG, "No tactical hardware found. Degrading to software-only mode.")
            }
            
            // Return true if AT LEAST ONE device connected successfully
            hatRes || wingmanRes
        }
    }

    override suspend fun close() {
        try { hapHat.close() } catch (e: Exception) { Log.e(TAG, "HapHat close error", e) }
        try { wingman.close() } catch (e: Exception) { Log.e(TAG, "Wingman close error", e) }
    }

    override suspend fun onMissionIncoming() {
        // HapHat: M3 Pulse Purple
        hapHat.sendCommand(HapHatCommand(motorId = MotorId.M3_CENTER, intensityPwm = 200.toByte(), ledMode = LedMode.PULSE, ledColor = LedColor.PURPLE, durationMs = 15000))
        
        // Wingman: 2x Flash Purple, then solid
        wingman.sendLedCommand(WingmanLedCommand(ledMode = LedRingMode.FLASH, color = LedColor.PURPLE, durationMs = 15000))
    }

    override suspend fun onMissionAccepted() {
        // HapHat: M3 Solid Orange
        hapHat.sendCommand(HapHatCommand(motorId = MotorId.M3_CENTER, intensityPwm = 255.toByte(), ledMode = LedMode.SOLID, ledColor = LedColor.ORANGE, durationMs = 0))
        
        // Wingman: Solid Orange
        wingman.sendLedCommand(WingmanLedCommand(ledMode = LedRingMode.SOLID, color = LedColor.ORANGE))
    }

    override suspend fun onMissionDeclined() {
        hapHat.sendCommand(HapHatCommand(ledMode = LedMode.OFF, ledColor = LedColor.OFF))
        wingman.sendLedCommand(WingmanLedCommand(ledMode = LedRingMode.OFF, color = LedColor.OFF))
    }

    override suspend fun onArrivedAtScene() {
        // HapHat: ALL motors max, Yellow Solid
        hapHat.sendCommand(HapHatCommand(motorId = MotorId.ALL, intensityPwm = 255.toByte(), ledMode = LedMode.SOLID, ledColor = LedColor.YELLOW, durationMs = 0))
        
        // Wingman: Yellow Pulse 3x, then Solid
        wingman.sendLedCommand(WingmanLedCommand(ledMode = LedRingMode.FLASH, color = LedColor.YELLOW, durationMs = 3000))
    }

    override suspend fun onBleHandshakeSuccess() {
        hapHat.sendCommand(HapHatCommand(ledMode = LedMode.SOLID, ledColor = LedColor.CYAN, durationMs = 0))
        wingman.sendLedCommand(WingmanLedCommand(ledMode = LedRingMode.SOLID, color = LedColor.CYAN))
    }

    override suspend fun onBleHandshakeFailed() {
        wingman.sendLedCommand(WingmanLedCommand(ledMode = LedRingMode.FLASH, color = LedColor.RED, durationMs = 2000))
    }

    override suspend fun onMissionSuccess() {
        hapHat.sendCommand(HapHatCommand(motorId = MotorId.ALL, intensityPwm = 255.toByte(), ledMode = LedMode.STROBE, ledColor = LedColor.GREEN, durationMs = 3000))
        wingman.sendLedCommand(WingmanLedCommand(ledMode = LedRingMode.CASCADE_UP, color = LedColor.GREEN, durationMs = 4000))
    }

    override suspend fun onMissionFailed() {
        hapHat.sendCommand(HapHatCommand(motorId = MotorId.ALL, intensityPwm = 255.toByte(), ledMode = LedMode.STROBE, ledColor = LedColor.RED, durationMs = 3000))
        wingman.sendLedCommand(WingmanLedCommand(ledMode = LedRingMode.FLASH, color = LedColor.RED, durationMs = 3000))
    }

    override suspend fun onMissionAborted() {
        hapHat.sendCommand(HapHatCommand(ledMode = LedMode.OFF, ledColor = LedColor.OFF))
        wingman.sendLedCommand(WingmanLedCommand(ledMode = LedRingMode.OFF, color = LedColor.OFF))
    }

    override suspend fun onChainedMission() {
        // Orange solid for chained missions
        hapHat.sendCommand(HapHatCommand(motorId = MotorId.ALL, intensityPwm = 150.toByte(), ledMode = LedMode.SOLID, ledColor = LedColor.ORANGE, durationMs = 0))
        wingman.sendLedCommand(WingmanLedCommand(ledMode = LedRingMode.SOLID, color = LedColor.ORANGE))
    }

    // ─── SIGNATURE FEATURE: DIRECTIONAL NAVIGATION SYNC ──────────────
    override suspend fun onDirectionalTick(clockPosition: Byte) {
        // Hat vibrates the standard clock position on the head
        hapHat.sendCommand(
            HapHatCommand(
                motorId = mapClockToMotor(clockPosition), // e.g., 2 o'clock -> M4
                intensityPwm = 255.toByte(),
                ledMode = LedMode.PULSE,
                ledColor = LedColor.ORANGE,
                durationMs = 3000
            )
        )

        // 🪞 THE MIRROR TEST: Chest-worn displays viewed from above have an inverted X-axis.
        // Hat 2 o'clock (Front-Right) = Wingman 10 o'clock (Front-Right from top-down perspective).
        val mirroredClock = if (clockPosition == 0.toByte()) {
            0.toByte() // 12 o'clock stays 12 o'clock
        } else {
            (12 - clockPosition).toByte()
        }

        // Fire the 7-second firmware macro on the Wingman
        wingman.sendLedCommand(
            WingmanLedCommand(
                ledMode = LedRingMode.DIRECTIONAL_SWEEP, // Instructs firmware to run the 3x Sweep & Hold
                color = LedColor.GREEN, // The target color at the end of the sweep
                directionClockPosition = mirroredClock
            )
        )
    }

    private fun mapClockToMotor(clockPosition: Byte): MotorId {
        // Map the 12 clock positions to the 5 physical motors on the HapHat forehead
        return when (clockPosition.toInt()) {
            0 -> MotorId.M3_CENTER          // 12 o'clock (Straight ahead)
            1, 2 -> MotorId.M4_NEAR_RIGHT   // 1 and 2 o'clock
            3, 4, 5 -> MotorId.M5_FAR_RIGHT // 3, 4, and 5 o'clock
            6 -> MotorId.ALL                // 6 o'clock (Behind - firing all motors to signal 'turn around')
            7, 8, 9 -> MotorId.M1_FAR_LEFT  // 7, 8, and 9 o'clock
            10, 11 -> MotorId.M2_NEAR_LEFT  // 10 and 11 o'clock
            else -> MotorId.M3_CENTER
        }
    }
}