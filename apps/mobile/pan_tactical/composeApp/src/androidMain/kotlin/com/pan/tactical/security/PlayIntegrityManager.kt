package com.pan.tactical.security

import android.content.Context
import android.util.Base64
import com.google.android.play.core.integrity.IntegrityManagerFactory
import com.google.android.play.core.integrity.IntegrityTokenRequest
import com.pan.tactical.BuildConfig
import kotlinx.coroutines.suspendCancellableCoroutine
import java.security.MessageDigest
import kotlin.coroutines.resume
import kotlin.coroutines.resumeWithException

class PlayIntegrityManager(private val context: Context) {

    /**
     * Fetches the Play Integrity Attestation Token.
     * This suspend function pauses the background coroutine until Google's servers
     * return the cryptographic proof of the device's integrity.
     */
    suspend fun fetchAttestationToken(agentId: String, publicKeyB64: String): String {
        val integrityManager = IntegrityManagerFactory.create(context)

        // Cryptographically bind the device token to the specific agent and key.
        val nonceToUse = generateBoundNonce(agentId, publicKeyB64)

        val request = IntegrityTokenRequest.builder()
            // 🟢 THE FIX: Shifted to BuildConfig to avoid hardcoding GCP Project Numbers.
            // Ensure GCP_PROJECT_NUMBER is set in your local.properties or app/build.gradle
            .setCloudProjectNumber(BuildConfig.GCP_PROJECT_NUMBER)
            .setNonce(nonceToUse)
            .build()

        // We wrap Google's asynchronous Task API in a Kotlin Coroutine so we don't freeze the main thread.
        return suspendCancellableCoroutine { continuation ->
            integrityManager.requestIntegrityToken(request)
                .addOnSuccessListener { response ->
                    continuation.resume(response.token())
                }
                .addOnFailureListener { exception ->
                    // If this fails, the device is compromised, rooted, or an emulator.
                    // We throw a fatal error to halt the Vanguard Agent's session.
                    continuation.resumeWithException(
                        SecurityException("CRITICAL: Play Integrity Attestation Failed. Device untrusted.", exception)
                    )
                }
        }
    }

    /**
     * Generates a cryptographically secure challenge nonce bound to the payload.
     * The backend will recreate this exact hash to verify the token wasn't replayed.
     */
    private fun generateBoundNonce(agentId: String, publicKeyB64: String): String {
        val payload = "$agentId$publicKeyB64".toByteArray(Charsets.UTF_8)
        val digest = MessageDigest.getInstance("SHA-256")
        val hashBytes = digest.digest(payload)
        // URL_SAFE and NO_WRAP are strict requirements from the Play API
        return Base64.encodeToString(hashBytes, Base64.URL_SAFE or Base64.NO_WRAP)
    }
}