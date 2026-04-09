package com.pan.tactical.hardware

import kotlinx.cinterop.*
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import platform.CoreHaptics.*
import platform.Foundation.NSError

@OptIn(ExperimentalForeignApi::class)
class IosHardwareCommandBridge : HardwareCommandBridge {

    private var hapticEngine: CHHapticEngine? = null
    private var isEngineRunning = false

    override suspend fun connect(): Boolean {
        // 1. Verify hardware supports advanced haptics
        if (!CHHapticEngine.capabilitiesForHardware().supportsHaptics()) {
            println("[iOS_HAPTICS] Hardware does not support CoreHaptics. Degrading to silent mode.")
            return false
        }

        // 2. Initialize the engine safely using C-interop memory scoping
        return memScoped {
            val errorVar = alloc<ObjCObjectVar<NSError?>>()
            hapticEngine = CHHapticEngine(errorVar.ptr)

            if (errorVar.value != null || hapticEngine == null) {
                println("[iOS_HAPTICS] Engine initialization failed: ${errorVar.value?.localizedDescription}")
                return@memScoped false
            }

            // 3. Start the engine
            hapticEngine?.startAndReturnError(errorVar.ptr)
            if (errorVar.value != null) {
                println("[iOS_HAPTICS] Engine failed to start: ${errorVar.value?.localizedDescription}")
                return@memScoped false
            }

            isEngineRunning = true
            true
        }
    }

    override suspend fun close() {
        if (isEngineRunning) {
            hapticEngine?.stopWithCompletionHandler(null)
            isEngineRunning = false
            hapticEngine = null
        }
    }

    /**
     * Helper to generate specific haptic waveforms.
     * 🛡️ FINDING 2 FIXED: Dispatched to Default to prevent blocking the UI thread during C-interop
     */
    private suspend fun playHaptic(intensity: Float, sharpness: Float, duration: Double, isContinuous: Boolean = false) {
        if (!isEngineRunning || hapticEngine == null) return

        withContext(Dispatchers.Default) {
            memScoped {
                val intensityParam = CHHapticEventParameter(CHHapticEventParameterIDHapticIntensity, intensity)
                val sharpnessParam = CHHapticEventParameter(CHHapticEventParameterIDHapticSharpness, sharpness)

                val eventType = if (isContinuous) CHHapticEventTypeHapticContinuous else CHHapticEventTypeHapticTransient

                val event = CHHapticEvent(
                    eventType = eventType,
                    parameters = listOf(intensityParam, sharpnessParam),
                    relativeTime = 0.0,
                    duration = duration
                )

                val errorVar = alloc<ObjCObjectVar<NSError?>>()
                val pattern = CHHapticPattern(listOf(event), listOf<CHHapticDynamicParameter>(), errorVar.ptr)

                if (errorVar.value == null) {
                    val player = hapticEngine?.createPlayerWithPattern(pattern, errorVar.ptr)
                    player?.startAtTime(0.0, errorVar.ptr)
                } else {
                    println("[iOS_HAPTICS] Pattern creation failed: ${errorVar.value?.localizedDescription}")
                }
            }
        }
    }

    // --- SEMANTIC MAPPINGS ---

    override suspend fun onMissionIncoming() {
        // 🛡️ FINDING 3 FIXED: Match Android 15s alert window — continuous pulse for full countdown duration
        playHaptic(intensity = 0.8f, sharpness = 0.4f, duration = 15.0, isContinuous = true)
    }

    override suspend fun onMissionAccepted() {
        // Sharp, validating double-tap
        playHaptic(intensity = 1.0f, sharpness = 0.8f, duration = 0.1)
    }

    override suspend fun onMissionDeclined() {
        // Muted, dull thud
        playHaptic(intensity = 0.4f, sharpness = 0.1f, duration = 0.15)
    }

    override suspend fun onArrivedAtScene() {
        // Solid, heavy arrival confirmation
        playHaptic(intensity = 1.0f, sharpness = 0.5f, duration = 0.3, isContinuous = true)
    }

    override suspend fun onBleHandshakeSuccess() {
        // Crisp, high-frequency "ping" for digital handshake
        playHaptic(intensity = 0.6f, sharpness = 1.0f, duration = 0.05)
    }

    override suspend fun onBleHandshakeFailed() {
        // Heavy, jagged error buzz
        playHaptic(intensity = 1.0f, sharpness = 0.2f, duration = 0.4, isContinuous = true)
    }

    override suspend fun onMissionSuccess() {
        // Triumphant long pulse
        playHaptic(intensity = 0.9f, sharpness = 0.6f, duration = 0.8, isContinuous = true)
    }

    override suspend fun onMissionFailed() {
        // Stuttering failure buzz
        playHaptic(intensity = 1.0f, sharpness = 0.1f, duration = 0.6, isContinuous = true)
    }

    override suspend fun onMissionAborted() {
        // 🛡️ FINDING 1 FIXED: No haptic feedback for abort — engine stays running for next mission.
        // Silence is intentional: the swipe-to-abort gesture itself provides sufficient UI feedback.
    }

    override suspend fun onChainedMission() {
        // Alert but less aggressive than initial dispatch
        playHaptic(intensity = 0.7f, sharpness = 0.5f, duration = 0.2)
    }
}