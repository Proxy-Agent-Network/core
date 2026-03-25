package com.pan.tactical.security

import android.content.Context
import android.util.Log
import com.google.android.play.core.integrity.IntegrityManagerFactory
import com.google.android.play.core.integrity.IntegrityTokenRequest
import com.pan.tactical.BuildConfig
import kotlinx.coroutines.suspendCancellableCoroutine
import kotlin.coroutines.resume
import kotlin.coroutines.resumeWithException

class AttestationEngine {

    companion object {
        private const val TAG = "AttestationEngine"
    }

    /**
     * Pings the physical Google Play Services chip on the device to verify
     * the hardware has not been rooted or tampered with.
     *
     * @return A signed JWS (JSON Web Signature) token from Google Play.
     * 🛑 SECURITY NOTE: This token MUST be sent to the PAN backend for server-side verification
     * via the Google Play Integrity API. Never evaluate this token client-side.
     */
    suspend fun generateHardwareToken(context: Context, cryptographicNonce: String): String {

        // 1. Fail-Fast Precondition: Validation happens synchronously before suspension.
        require(cryptographicNonce.length >= 16) {
            "Nonce too short. Minimum 16 characters required by Play Integrity API."
        }

        // 2. Suspend and await the async callback from Google Play Services
        return suspendCancellableCoroutine { continuation ->
            try {
                val integrityManager = IntegrityManagerFactory.create(context)

                // 3. Package our payload (nonce) and securely bind it to our GCP Billing account
                val request = IntegrityTokenRequest.builder()
                    .setNonce(cryptographicNonce)
                    .setCloudProjectNumber(BuildConfig.PLAY_INTEGRITY_CLOUD_PROJECT_NUMBER.toLong())
                    .build()

                // 4. Fire the request to Google's hardware backend
                integrityManager.requestIntegrityToken(request)
                    .addOnSuccessListener { response ->
                        Log.i(TAG, "🛡️ ATTESTATION SUCCESS: Hardware verified by Google Play.")
                        continuation.resume(response.token())
                    }
                    .addOnFailureListener { e ->
                        // 🛑 FAIL-CLOSED: Device is rooted, an emulator, or spoofing.
                        Log.e(TAG, "🛑 FATAL ATTESTATION FAILURE: Device integrity compromised: ${e.message}")
                        continuation.resumeWithException(SecurityException("Hardware Attestation Failed: Untrusted Device Environment."))
                    }

            } catch (e: Exception) {
                // 🛑 FAIL-CLOSED on internal crashes.
                Log.e(TAG, "🛑 ATTESTATION CRASHED: ${e.message}")
                continuation.resumeWithException(SecurityException("Hardware Attestation Engine Crashed: ${e.message}"))
            }
        }
    }
}