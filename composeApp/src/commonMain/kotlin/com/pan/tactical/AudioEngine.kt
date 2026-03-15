package com.pan.tactical

expect class AudioEngine() {
    fun speak(text: String, volume: Float)
    fun playAlertBeep(volumeLevel: Int)
    fun stop()
}