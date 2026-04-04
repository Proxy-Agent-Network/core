package com.pan.tactical.hardware

/**
 * 🛡️ [PHASE 5] Wearable Hardware Contract
 * Defines the GATT payload structure expected by the Vanguard HapHat firmware.
 * Aligned with Project Copperfield v2.2 specifications.
 */

enum class MotorId(val byte: Byte) {
    M1_FAR_LEFT(0x01), 
    M2_NEAR_LEFT(0x02), 
    M3_CENTER(0x03), 
    M4_NEAR_RIGHT(0x04), 
    M5_FAR_RIGHT(0x05), 
    ALL(0xFF.toByte())
}

enum class LedMode(val byte: Byte) {
    OFF(0x00), SOLID(0x01), PULSE(0x02), STROBE(0x03)
}

enum class LedColor(val byte: Byte) {
    OFF(0x00), 
    WHITE(0x01), 
    CYAN(0x02), 
    GREEN(0x03), 
    RED(0x04), 
    AMBER(0x05),
    ORANGE(0x06), // EN_ROUTE
    YELLOW(0x07), // ON_SCENE
    PURPLE(0x08)  // MISSION_INCOMING
}

data class HapHatCommand(
    val motorId: MotorId = MotorId.ALL,
    
    // 🛡️ FIXED: Note regarding Kotlin's signed Byte limitation vs ESP32's uint8_t
    // intensityPwm is treated as unsigned (0-255) by firmware.
    // Kotlin Byte is signed (-128 to 127) — use .toByte() for values > 127.
    val intensityPwm: Byte = 0x00, // 0-255 (0% to 100% power)
    
    val ledMode: LedMode,
    val ledColor: LedColor,
    
    // 🛡️ FIXED: Note regarding Kotlin's signed Short limitation vs ESP32's uint16_t
    // Kotlin Short is signed (-32768 to 32767) — firmware treats as unsigned uint16_t (0–65535ms).
    // Use .toShort() for values > 32767. Max ~65 seconds.
    val durationMs: Short = 0      // 0 = indefinite
)

interface BleHapHatService {
    /**
     * Attempts to connect to a paired Vanguard HapHat over BLE.
     * Returns true if the GATT connection is established.
     */
    suspend fun connect(): Boolean

    /**
     * Suspending function to ensure the GATT write completes, 
     * returning true if the 6-byte command payload was successfully acknowledged.
     */
    suspend fun sendCommand(command: HapHatCommand): Boolean

    /**
     * Safely closes the BLE GATT connection to prevent battery drain.
     */
    fun close()
}

// --- MOCK INJECTION FOR UI DEVELOPMENT ---
// TODO: Before Pilot, create an AndroidBleHapHatService implementation and toggle via BuildConfig.DEBUG
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember

@Composable
fun rememberBleHapHatService(): BleHapHatService {
    return remember {
        object : BleHapHatService {
            override suspend fun connect(): Boolean {
                println("[HAP_HAT] 🧢 Mock Wearable Connected.")
                return true
            }

            override suspend fun sendCommand(command: HapHatCommand): Boolean {
                println("[HAP_HAT] ⚡ Command Sent: Motor=${command.motorId}, PWM=${command.intensityPwm}, LED=${command.ledColor}[${command.ledMode}], Duration=${command.durationMs}ms")
                return true
            }

            override fun close() {
                println("[HAP_HAT] 🔌 Connection Closed.")
            }
        }
    }
}