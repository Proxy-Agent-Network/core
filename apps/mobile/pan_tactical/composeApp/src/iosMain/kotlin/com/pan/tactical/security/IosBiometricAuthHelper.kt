package com.pan.tactical.security

import kotlinx.coroutines.suspendCancellableCoroutine
import platform.LocalAuthentication.LAContext
import platform.LocalAuthentication.LAPolicyDeviceOwnerAuthenticationWithBiometrics
import kotlin.coroutines.resume

class IosBiometricAuthHelper : BiometricAuthHelper {

    override suspend fun authenticate(promptTitle: String, promptSubtitle: String): Boolean =
        suspendCancellableCoroutine { continuation ->
            val context = LAContext()

            // 1. Check if the device has biometrics configured and available
            val canEvaluate = context.canEvaluatePolicy(
                LAPolicyDeviceOwnerAuthenticationWithBiometrics,
                null
            )

            if (!canEvaluate) {
                println("[iOS_ATTESTATION] Biometrics not available on this device.")
                if (continuation.isActive) continuation.resume(false)
                return@suspendCancellableCoroutine
            }

            // 2. Trigger the Face ID / Touch ID system prompt
            context.evaluatePolicy(
                policy = LAPolicyDeviceOwnerAuthenticationWithBiometrics,
                localizedReason = promptSubtitle
            ) { success, error ->
                if (success) {
                    println("[iOS_ATTESTATION] ✅ Agent Verified. Secure Enclave Authorized.")
                    if (continuation.isActive) continuation.resume(true)
                } else {
                    println("[iOS_ATTESTATION] ❌ Biometric error: ${error?.localizedDescription}")
                    if (continuation.isActive) continuation.resume(false)
                }
            }
        }
}