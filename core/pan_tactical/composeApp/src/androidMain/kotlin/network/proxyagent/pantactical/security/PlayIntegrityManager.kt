package network.proxyagent.pantactical.security

import android.content.Context
import android.util.Base64
import com.google.android.play.core.integrity.IntegrityManagerFactory
import com.google.android.play.core.integrity.IntegrityTokenRequest
import kotlinx.coroutines.suspendCancellableCoroutine
import java.security.SecureRandom
import kotlin.coroutines.resume
import kotlin.coroutines.resumeWithException

class PlayIntegrityManager(private val context: Context) {

    /**
     * Fetches the Play Integrity Attestation Token.
     * This suspend function pauses the background coroutine until Google's servers
     * return the cryptographic proof of the device's integrity.
     */
    suspend fun fetchAttestationToken(serverNonce: String? = null): String {
        val integrityManager = IntegrityManagerFactory.create(context)

        // The Nonce (Number Used Once) prevents replay attacks.
        // In production, the PAN Gateway generates this. For local development, we generate our own.
        val nonceToUse = serverNonce ?: generateLocalNonce()

        val request = IntegrityTokenRequest.builder()
            // TODO: Replace with the actual Vanguard Google Cloud Project Number before the Mesa Pilot
            .setCloudProjectNumber(1234567890L)
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
     * Generates a cryptographically secure random string for the challenge nonce.
     */
    private fun generateLocalNonce(): String {
        val random = SecureRandom()
        val nonceBytes = ByteArray(32)
        random.nextBytes(nonceBytes)
        // URL_SAFE and NO_WRAP are strict requirements from the Play API
        return Base64.encodeToString(nonceBytes, Base64.URL_SAFE or Base64.NO_WRAP)
    }
}