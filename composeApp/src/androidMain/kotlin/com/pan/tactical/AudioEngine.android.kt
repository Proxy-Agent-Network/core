package com.pan.tactical

import android.content.Context
import android.media.AudioManager
import android.media.ToneGenerator
import android.os.Bundle
import android.speech.tts.TextToSpeech
import android.speech.tts.Voice
import java.util.Locale

actual class AudioEngine {
    private var tts: TextToSpeech? = null
    private var isInitialized = false
    private val nativeVoices = mutableMapOf<String, Voice>()

    init {
        val context = com.pan.tactical.MainApplication.appContext
        tts = TextToSpeech(context) { status ->
            if (status == TextToSpeech.SUCCESS) {
                tts?.language = Locale.US
                isInitialized = true

                tts?.voices?.filter { it.locale.language == "en" }?.forEach { voice ->
                    nativeVoices[voice.name] = voice
                }
            }
        }
    }

    actual fun speak(text: String, volume: Float) {
        if (!isInitialized) return
        val params = Bundle().apply { putFloat(TextToSpeech.Engine.KEY_PARAM_VOLUME, volume) }
        tts?.speak(text, TextToSpeech.QUEUE_FLUSH, params, "TacticalAudio")
    }

    actual fun stop() {
        tts?.stop()
    }

    actual fun getAvailableVoices(): List<TacticalVoice> {
        return nativeVoices.values.take(6).map {
            TacticalVoice(id = it.name, name = "OS Voice: ${it.name.takeLast(4).uppercase()}")
        }
    }

    actual fun setVoice(voiceId: String) {
        nativeVoices[voiceId]?.let { tts?.voice = it }
    }

    // THE FIX: Uses the volume passed from your UI slider
    actual fun playAlertBeep(volume: Int) {
        try {
            val toneGen = ToneGenerator(AudioManager.STREAM_ALARM, volume)
            toneGen.startTone(ToneGenerator.TONE_PROP_BEEP, 150)
        } catch (e: Exception) { }
    }
}