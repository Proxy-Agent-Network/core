package com.pan.tactical

import android.media.AudioManager
import android.media.ToneGenerator
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.speech.tts.TextToSpeech
import android.speech.tts.Voice
import android.util.Log
import java.util.Locale

// 🛡️ FIX: Import the new interface and data model from the UI package
import com.pan.tactical.ui.TacticalAudioEngine
import com.pan.tactical.ui.VoiceProfile

// 🛡️ FIX: Implement the shared TacticalAudioEngine interface
actual class AudioEngine : TacticalAudioEngine {

    companion object {
        private const val TAG = "AudioEngine"
    }

    private var tts: TextToSpeech? = null
    private var isInitialized = false

    private val pendingUtterances = mutableListOf<Pair<String, Float>>()
    private val nativeVoices = mutableMapOf<String, Voice>()

    init {
        // Relies on PanApplication.instance being set in the Android Application class
        val context = PanApplication.instance

        tts = TextToSpeech(context) { status ->
            if (status == TextToSpeech.SUCCESS) {
                isInitialized = true
                tts?.language = Locale.US

                // Flush queued commands from boot sequence
                pendingUtterances.forEach { (text, vol) ->
                    val params = Bundle().apply { putFloat(TextToSpeech.Engine.KEY_PARAM_VOLUME, vol) }
                    // QUEUE_ADD used here ONLY so boot messages don't step on each other
                    tts?.speak(text, TextToSpeech.QUEUE_ADD, params, "pan_init_${System.currentTimeMillis()}")
                }
                pendingUtterances.clear()
            } else {
                Log.e(TAG, "TTS Initialization failed with status: $status")
            }
        }
    }

    actual override fun speak(text: String, volume: Float) {
        if (!isInitialized) {
            Log.w(TAG, "TTS not ready yet. Queuing: '$text'")
            pendingUtterances.add(Pair(text, volume))
            return
        }

        try {
            val params = Bundle()
            params.putFloat(TextToSpeech.Engine.KEY_PARAM_VOLUME, volume)
            tts?.speak(text, TextToSpeech.QUEUE_FLUSH, params, "pan_utterance_${System.currentTimeMillis()}")
        } catch (e: Exception) {
            Log.e(TAG, "TTS Speak failed: ${e.message}", e)
        }
    }

    actual fun stop() {
        try {
            tts?.stop()
        } catch (e: Exception) {
            Log.e(TAG, "TTS Stop failed: ${e.message}", e)
        }
    }

    actual override fun setVoice(voiceId: String) {
        try {
            nativeVoices[voiceId]?.let { voice ->
                tts?.voice = voice
            } ?: Log.w(TAG, "Voice ID $voiceId not found in native mapping.")
        } catch (e: Exception) {
            Log.e(TAG, "TTS setVoice failed: ${e.message}", e)
        }
    }

    // 🛡️ FIX: Updated to return List<VoiceProfile> to match the interface
    actual override fun getAvailableVoices(): List<VoiceProfile> {
        return try {
            val voices = tts?.voices ?: return emptyList()

            voices.filter { it.locale.language == Locale.ENGLISH.language }
                .take(6)
                .map { voice ->
                    nativeVoices[voice.name] = voice
                    val lang = voice.locale.toLanguageTag().uppercase()
                    VoiceProfile(
                        id = voice.name,
                        name = "OS Voice: ${voice.name.takeLast(4).uppercase()} ($lang)"
                    )
                }
        } catch (e: Exception) {
            Log.e(TAG, "Failed to retrieve voices: ${e.message}", e)
            emptyList()
        }
    }

    actual override fun playAlertBeep(volume: Int) {
        try {
            val safeVolume = volume.coerceIn(0, 100)
            val toneGen = ToneGenerator(AudioManager.STREAM_ALARM, safeVolume)
            toneGen.startTone(ToneGenerator.TONE_PROP_BEEP, 150)

            Handler(Looper.getMainLooper()).postDelayed({
                try {
                    toneGen.release()
                } catch (e: Exception) {
                    Log.e(TAG, "Failed to release ToneGenerator: ${e.message}", e)
                }
            }, 200)

        } catch (e: Exception) {
            Log.e(TAG, "Alert beep failed: ${e.message}", e)
        }
    }

    actual fun shutdown() {
        try {
            tts?.stop()
            tts?.shutdown()
            tts = null
            isInitialized = false
        } catch (e: Exception) {
            Log.e(TAG, "TTS Shutdown failed: ${e.message}", e)
        }
    }
}