package com.pan.tactical

import android.media.AudioManager
import android.media.ToneGenerator
import android.speech.tts.TextToSpeech
import java.util.Locale

actual class AudioEngine actual constructor() {
    private var tts: TextToSpeech? = null

    init {
        val context = MainActivity.appContext
        if (context != null) {
            tts = TextToSpeech(context) { status ->
                if (status == TextToSpeech.SUCCESS) {
                    tts?.language = Locale.US
                }
            }
        }
    }

    actual fun speak(text: String, volume: Float) {
        val params = android.os.Bundle().apply {
            putFloat(TextToSpeech.Engine.KEY_PARAM_VOLUME, volume)
        }
        tts?.speak(text, TextToSpeech.QUEUE_FLUSH, params, null)
    }

    actual fun playAlertBeep(volumeLevel: Int) {
        try {
            val toneGen = ToneGenerator(AudioManager.STREAM_ALARM, volumeLevel)
            toneGen.startTone(ToneGenerator.TONE_CDMA_ALERT_CALL_GUARD, 150)
        } catch (e: Exception) {
            println("Audio Error: ${e.message}")
        }
    }

    actual fun stop() {
        tts?.stop()
        tts?.shutdown()
    }
}