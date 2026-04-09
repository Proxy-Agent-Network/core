package com.pan.tactical.security

/**
 * Platform-agnostic bridge for biometric attestation.
 * - Android: Wraps AndroidX BiometricPrompt
 * - iOS: Wraps LocalAuthentication (Face ID / Touch ID)
 */
interface BiometricAuthHelper {
    suspend fun authenticate(
        promptTitle: String = "Agent Attestation Required",
        promptSubtitle: String = "Authenticate to cryptographically sign mission evidence"
    ): Boolean
}