package com.pan.tactical.hardware

class AndroidHardwareCommandBridge(
    private val hapHat: BleHapHatService
) : HardwareCommandBridge {

    companion object {
        private const val TAG = "AndroidHapHatBridge"
    }

    override suspend fun connect(): Boolean {
        return try {
            hapHat.connect()
            true
        } catch (e: Exception) {
            Log.e(TAG, "Hardware connection failed, degrading to software-only mode: ${e.message}")
            false
        }
    }

    override suspend fun close() {
        try {
            hapHat.close()
        } catch (e: Exception) {
            Log.e(TAG, "Error closing hardware connection: ${e.message}")
        }
    }

    override suspend fun onMissionIncoming() {
        hapHat.sendCommand(
            HapHatCommand(
                motorId = MotorId.M3_CENTER,
                intensityPwm = 200.toByte(),
                ledMode = LedMode.PULSE,
                ledColor = LedColor.PURPLE,
                durationMs = 15000
            )
        )
    }

    override suspend fun onMissionAccepted() {
        hapHat.sendCommand(
            HapHatCommand(
                motorId = MotorId.M3_CENTER,
                intensityPwm = 200.toByte(),
                ledMode = LedMode.SOLID,
                ledColor = LedColor.WHITE,
                durationMs = 500
            )
        )
        delay(500)
        hapHat.sendCommand(
            HapHatCommand(
                ledMode = LedMode.SOLID,
                ledColor = LedColor.ORANGE,
                durationMs = 0
            )
        )
    }

    override suspend fun onMissionDeclined() {
        hapHat.sendCommand(
            HapHatCommand(
                ledMode = LedMode.OFF,
                ledColor = LedColor.OFF
            )
        )
    }

    override suspend fun onArrivedAtScene() {
        hapHat.sendCommand(
            HapHatCommand(
                motorId = MotorId.ALL,
                intensityPwm = 255.toByte(),
                ledMode = LedMode.SOLID,
                ledColor = LedColor.YELLOW,
                durationMs = 0
            )
        )
    }

    override suspend fun onBleHandshakeSuccess() {
        hapHat.sendCommand(
            HapHatCommand(
                ledMode = LedMode.SOLID,
                ledColor = LedColor.CYAN,
                durationMs = 0
            )
        )
    }

    override suspend fun onBleHandshakeFailed() {
        // No explicit LED pattern for failure yet in Vanguard 50 pilot.
        // Reserved for future integration.
    }

    override suspend fun onMissionSuccess() {
        hapHat.sendCommand(
            HapHatCommand(
                motorId = MotorId.ALL,
                intensityPwm = 255.toByte(),
                ledMode = LedMode.STROBE,
                ledColor = LedColor.GREEN,
                durationMs = 3000
            )
        )
    }

    override suspend fun onMissionFailed() {
        hapHat.sendCommand(
            HapHatCommand(
                motorId = MotorId.ALL,
                intensityPwm = 255.toByte(),
                ledMode = LedMode.STROBE,
                ledColor = LedColor.RED,
                durationMs = 3000
            )
        )
    }

    override suspend fun onMissionAborted() {
        hapHat.sendCommand(
            HapHatCommand(
                ledMode = LedMode.OFF,
                ledColor = LedColor.OFF
            )
        )
    }

    override suspend fun onChainedMission() {
        hapHat.sendCommand(
            HapHatCommand(
                ledMode = LedMode.SOLID,
                ledColor = LedColor.ORANGE
            )
        )
    }
}