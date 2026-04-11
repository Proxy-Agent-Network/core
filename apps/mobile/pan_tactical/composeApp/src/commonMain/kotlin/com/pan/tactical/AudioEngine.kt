package com.pan.tactical

import com.pan.tactical.ui.TacticalAudioEngine
import com.pan.tactical.ui.VoiceProfile

// 🛡️ FIX: The AudioEngine now implements the shared interface from the UI package.
// This allows the commonMain UI to control audio without knowing Android-specifics.
expect class AudioEngine() : TacticalAudioEngine {
    
    // Interface overrides
    override fun speak(text: String, volume: Float)
    override fun getAvailableVoices(): List<VoiceProfile>
    override fun setVoice(voiceId: String)
    override fun playAlertBeep(volume: Int)

    // Platform-specific lifecycle methods (not needed by the UI, but required for memory management)
    fun stop()
    fun shutdown()
}