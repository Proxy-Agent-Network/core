package com.pan.tactical.managers

import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.asSharedFlow

data class SentryExtensionRequest(
    val taskId: String,
    val extensionMinutes: Int,
    val offeredBountyUsd: Double
)

object MissionEventManager {
    // extraBufferCapacity = 1 ensures the event isn't dropped if the UI is momentarily recomposing
    private val _sentryExtensionEvents = MutableSharedFlow<SentryExtensionRequest>(extraBufferCapacity = 1)
    val sentryExtensionEvents = _sentryExtensionEvents.asSharedFlow()

    fun triggerExtensionRequest(taskId: String, minutes: Int, bountyUsd: Double) {
        val emitted = _sentryExtensionEvents.tryEmit(
            SentryExtensionRequest(taskId, minutes, bountyUsd)
        )
        
        if (!emitted) {
            // TODO: Replace with KMP logger (e.g., Kermit/Napier) for production telemetry
            println("⚠️ [MissionEventManager] Extension event dropped — buffer full for $taskId")
        }
    }
}