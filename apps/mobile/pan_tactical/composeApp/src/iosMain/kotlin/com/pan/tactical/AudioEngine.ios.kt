package com.pan.tactical

import platform.AVFAudio.*
import platform.Foundation.*

actual class AudioEngine {
    private val synthesizer = AVSpeechSynthesizer()
    private var currentVoice: AVSpeechSynthesisVoice? = AVSpeechSynthesisVoice.voiceWithLanguage("en-US")

    private val nativeVoices = mutableMapOf<String, AVSpeechSynthesisVoice>()

    init {
        try {
            // --- THE FIX: A VIP list of Apple's most human-sounding professional voices ---
            val premiumRoster = listOf("Samantha", "Daniel", "Karen", "Moira", "Alex", "Arthur", "Rishi", "Martha")

            val voices = AVSpeechSynthesisVoice.speechVoices() as List<AVSpeechSynthesisVoice>

            // Filter the master list to only include our premium agents
            voices.filter { it.name in premiumRoster }.forEach { voice ->
                nativeVoices[voice.identifier] = voice
            }

            // Fallback just in case the Simulator is stripped down
            if (nativeVoices.isEmpty()) {
                voices.filter { it.language.startsWith("en") }.forEach { voice ->
                    nativeVoices[voice.identifier] = voice
                }
            }
        } catch (e: Exception) {
            println("AUDIO ERROR: Failed to load Apple voices")
        }
    }

    actual fun speak(text: String, volume: Float) {
        try {
            val utterance = AVSpeechUtterance(string = text).apply {
                this.volume = volume
                this.voice = currentVoice
            }

            if (synthesizer.isSpeaking()) {
                // Using the strict Enum path to prevent compilation errors
                synthesizer.stopSpeakingAtBoundary(AVSpeechBoundary.AVSpeechBoundaryImmediate)
            }
            synthesizer.speakUtterance(utterance)
        } catch (e: Exception) {
            println("AUDIO ERROR: Utterance failed")
        }
    }

    actual fun stop() {
        if (synthesizer.isSpeaking()) {
            synthesizer.stopSpeakingAtBoundary(AVSpeechBoundary.AVSpeechBoundaryImmediate)
        }
    }

    actual fun getAvailableVoices(): List<TacticalVoice> {
        return nativeVoices.values.take(6).map {
            TacticalVoice(id = it.identifier, name = it.name.uppercase())
        }
    }

    actual fun setVoice(voiceId: String) {
        nativeVoices[voiceId]?.let { currentVoice = it }
    }

    // Added the parameter so App.kt is happy
    actual fun playAlertBeep(volume: Int) {
        // Safe placeholder for iOS
    }
}