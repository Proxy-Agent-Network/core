package com.pan.tactical

import platform.AVFAudio.AVSpeechBoundary
import platform.AVFAudio.AVSpeechSynthesizer
import platform.AVFAudio.AVSpeechUtterance

// --- THE FIX: This makes the audio engine global so voices never overlap! ---
private val globalSynthesizer = AVSpeechSynthesizer()

actual class AudioEngine {
    actual fun speak(text: String, volume: Float) {
        globalSynthesizer.stopSpeakingAtBoundary(AVSpeechBoundary.AVSpeechBoundaryImmediate)

        val utterance = AVSpeechUtterance(string = text)
        utterance.volume = volume
        globalSynthesizer.speakUtterance(utterance)
    }

    actual fun stop() {
        globalSynthesizer.stopSpeakingAtBoundary(AVSpeechBoundary.AVSpeechBoundaryImmediate)
    }

    actual fun playAlertBeep(volumeLevel: Int) {
        // iOS alert bridge coming soon
    }
}