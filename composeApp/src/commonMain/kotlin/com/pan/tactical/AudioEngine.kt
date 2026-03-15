package com.pan.tactical

// Our shared KMP Voice Model
data class TacticalVoice(val id: String, val name: String)

// The Multiplatform Engine Contract
expect class AudioEngine() {
    fun speak(text: String, volume: Float = 1.0f)
    fun stop()

    // The Voice API
    fun getAvailableVoices(): List<TacticalVoice>
    fun setVoice(voiceId: String)

    // THE FIX: Adding the 'volume' parameter so App.kt stops crashing!
    fun playAlertBeep(volume: Int)
}