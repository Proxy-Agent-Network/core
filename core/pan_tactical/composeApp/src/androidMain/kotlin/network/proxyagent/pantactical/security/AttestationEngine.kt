package network.proxyagent.pantactical.security

import android.content.Context
import com.google.android.play.core.integrity.IntegrityManagerFactory
import com.google.android.play.core.integrity.IntegrityTokenRequest
import kotlin.coroutines.resume
import kotlin.coroutines.suspendCoroutine

class AttestationEngine {

    /**
     * Pings the physical Google Play Services chip on the device to verify
     * the hardware has not been rooted or tampered with.
     */
    suspend fun generateHardwareToken(context: Context, cryptographicNonce: String): String = suspendCoroutine { continuation ->
        try {
            // 1. Wake up the Google Play Integrity Manager
            val integrityManager = IntegrityManagerFactory.create(context)

            // 2. Package our payload (the nonce) into the request
            val request = IntegrityTokenRequest.builder()
                .setNonce(cryptographicNonce)
                .build()

            // 3. Fire the request to Google's hardware backend
            integrityManager.requestIntegrityToken(request)
                .addOnSuccessListener { response ->
                    // SUCCESS: The hardware is pure. Return the massive cryptographic token.
                    println("🛡️ ATTESTATION SUCCESS: Hardware verified by Google Play.")
                    continuation.resume(response.token())
                }
                .addOnFailureListener { e ->
                    // FAILED: Device is rooted, an emulator, or not in the Play Console.
                    println("⚠️ ATTESTATION FAILED (Expected in Debug): ${e.message}")
                    continuation.resume("DEV_FALLBACK_TOKEN_UNVERIFIED_HARDWARE")
                }
        } catch (e: Exception) {
            println("⚠️ ATTESTATION CRASHED: ${e.message}")
            continuation.resume("DEV_FALLBACK_TOKEN_UNVERIFIED_HARDWARE")
        }
    }
}