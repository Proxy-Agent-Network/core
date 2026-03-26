package com.pan.tactical

import platform.AVFAudio.*
import platform.Foundation.*

actual class AudioEngine {
    private val synthesizer = AVSpeechSynthesizer()
    private var currentVoice: AVSpeechSynthesisVoice? = AVSpeechSynthesisVoice.voiceWithLanguage("en-US")

    private val nativeVoices = mutableMapOf<String, AVSpeechSynthesisVoice>()

    init {
        try {
            // A VIP list of Apple's most human-sounding professional voices
            val premiumRoster = listOf("Samantha", "Daniel", "Karen", "Moira", "Alex", "Arthur", "Rishi", "Martha")

            // 🛠️ THE FIX 5: Safe cast from Objective-C NSArray to prevent runtime crashes
            val voices = AVSpeechSynthesisVoice.speechVoices().filterIsInstance<AVSpeechSynthesisVoice>()

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
            // 🛠️ THE FIX 2: Proper error visibility
            println("[AudioEngine] ERROR: Failed to load Apple voices: ${e.message}")
        }
    }

    actual fun speak(text: String, volume: Float) {
        try {
            val utterance = AVSpeechUtterance(string = text).apply {
                this.volume = volume
                this.voice = currentVoice
            }

            if (synthesizer.isSpeaking) {
                // 🛠️ THE FIX 4: Maintained the strict enum path for safe interop
                synthesizer.stopSpeakingAtBoundary(AVSpeechBoundary.AVSpeechBoundaryImmediate)
            }
            synthesizer.speakUtterance(utterance)
        } catch (e: Exception) {
            // 🛠️ THE FIX 2: Proper error visibility
            println("[AudioEngine] ERROR: Utterance failed: ${e.message}")
        }
    }

    actual fun stop() {
        if (synthesizer.isSpeaking) {
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

    actual fun playAlertBeep(volume: Int) {
        // 🛠️ THE FIX 3: Added the TODO marker so we don't forget to wire up AudioToolbox
        // TODO: Implement using AudioServicesPlaySystemSound(kSystemSoundID_Vibrate)
        // or AudioToolbox for a proper alert tone on iOS
    }

    // 🛠️ THE FIX 1: Satisfying the KMP contract from commonMain
    actual fun shutdown() {
        stop()
        // AVSpeechSynthesizer does not require explicit teardown on iOS like TextToSpeech does on Android
    }
}