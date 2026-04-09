package com.pan.tactical.security

import androidx.biometric.BiometricManager
import androidx.biometric.BiometricPrompt
import androidx.core.content.ContextCompat
import androidx.fragment.app.FragmentActivity
import kotlinx.coroutines.suspendCancellableCoroutine
import kotlin.coroutines.resume

class AndroidBiometricAuthHelper(
    private val activity: FragmentActivity
) : BiometricAuthHelper {

    override suspend fun authenticate(promptTitle: String, promptSubtitle: String): Boolean =
        suspendCancellableCoroutine { continuation ->
            val executor = ContextCompat.getMainExecutor(activity)

            val biometricPrompt = BiometricPrompt(
                activity,
                executor,
                object : BiometricPrompt.AuthenticationCallback() {
                    override fun onAuthenticationError(errorCode: Int, errString: CharSequence) {
                        super.onAuthenticationError(errorCode, errString)
                        println("[ATTESTATION] Biometric error/cancellation: $errString")
                        if (continuation.isActive) {
                            continuation.resume(false)
                        }
                    }

                    override fun onAuthenticationSucceeded(result: BiometricPrompt.AuthenticationResult) {
                        super.onAuthenticationSucceeded(result)
                        println("[ATTESTATION] ✅ Agent Verified. StrongBox Signature Authorized.")
                        if (continuation.isActive) {
                            continuation.resume(true)
                        }
                    }

                    override fun onAuthenticationFailed() {
                        super.onAuthenticationFailed()
                        // 🛡️ NOTE: Do NOT resume false here.
                        // Failed means a bad read (e.g., partial fingerprint).
                        // The OS keeps the prompt open to let the user try again.
                        println("[ATTESTATION] ❌ Biometric rejection. Awaiting retry...")
                    }
                }
            )

            val promptInfo = BiometricPrompt.PromptInfo.Builder()
                .setTitle(promptTitle)
                .setSubtitle(promptSubtitle)
                .setNegativeButtonText("Cancel")
                .setAllowedAuthenticators(BiometricManager.Authenticators.BIOMETRIC_STRONG)
                .build()

            // Handle coroutine cancellation (e.g., if the user backgrounds the app)
            continuation.invokeOnCancellation {
                biometricPrompt.cancelAuthentication()
            }

            biometricPrompt.authenticate(promptInfo)
        }
}