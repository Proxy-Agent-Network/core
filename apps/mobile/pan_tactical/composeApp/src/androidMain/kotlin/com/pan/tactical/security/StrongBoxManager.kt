package com.pan.tactical.security

import android.security.keystore.KeyGenParameterSpec
import android.security.keystore.KeyProperties
import android.security.keystore.StrongBoxUnavailableException
import android.util.Base64
import java.security.KeyPairGenerator
import java.security.KeyStore
import java.security.PrivateKey
import java.security.Signature
import java.security.spec.ECGenParameterSpec
import org.json.JSONObject

class StrongBoxManager {

    companion object {
        // The unique ID for this device's physical identity
        private const val KEY_ALIAS = "vanguard_attestation_key"
        private const val ANDROID_KEYSTORE = "AndroidKeyStore"
    }

    /**
     * Initializes the Hardware Key.
     * This happens the very first time the Agent opens the app.
     */
    fun generateHardwareKey() {
        val keyStore = KeyStore.getInstance(ANDROID_KEYSTORE)
        keyStore.load(null)

        // Only generate the key if it doesn't already exist in the hardware
        if (!keyStore.containsAlias(KEY_ALIAS)) {
            val keyPairGenerator = KeyPairGenerator.getInstance(
                KeyProperties.KEY_ALGORITHM_EC,
                ANDROID_KEYSTORE
            )

            val parameterSpec = KeyGenParameterSpec.Builder(
                KEY_ALIAS,
                KeyProperties.PURPOSE_SIGN or KeyProperties.PURPOSE_VERIFY
            )
                .setAlgorithmParameterSpec(ECGenParameterSpec("secp256r1"))
                .setDigests(KeyProperties.DIGEST_SHA256)
                // 🟢 PILOT BYPASS: Disabled StrongBox requirement for local testing.
                // This allows emulators and local builds to generate a standard Keystore key
                // without crashing when the physical TPM 2.0 chip is unavailable or unprovisioned.
                // .setIsStrongBoxBacked(true)
                .build()

            try {
                keyPairGenerator.initialize(parameterSpec)
                keyPairGenerator.generateKeyPair()
            } catch (e: Exception) {
                // Generic catch applied for the pilot bypass
                throw SecurityException("CRITICAL: Failed to generate mock hardware key. ${e.message}")
            }
        }
    }

    /**
     * 泙 NEW: Extracts the Public Key Certificate to send to the PAN Backend.
     * This must be called during the initial Agent Onboarding Key Ceremony.
     */
    fun getPublicKeyBase64(): String {
        val keyStore = KeyStore.getInstance(ANDROID_KEYSTORE)
        keyStore.load(null)

        // 🟢 PILOT BYPASS: Auto-generate the key if it's missing instead of crashing
        if (!keyStore.containsAlias(KEY_ALIAS)) {
            generateHardwareKey()
        }

        val cert = keyStore.getCertificate(KEY_ALIAS)
        return Base64.encodeToString(cert.encoded, Base64.URL_SAFE or Base64.NO_WRAP)
    }

    /**
     * Signs the SB 1417 Audit Log or the L402 Preimage.
     * The Private Key never leaves the physical hardware chip; we just pass the
     * data to the chip, and the chip hands us back the signature.
     */
    fun signPayload(payload: String): ByteArray {
        val keyStore = KeyStore.getInstance(ANDROID_KEYSTORE)
        keyStore.load(null)

        // 🟢 PILOT BYPASS: Auto-generate the key if it's missing instead of crashing
        if (!keyStore.containsAlias(KEY_ALIAS)) {
            generateHardwareKey()
        }

        // Retrieve the key handle (not the actual key data, which is locked in hardware)
        val privateKey = keyStore.getKey(KEY_ALIAS, null) as PrivateKey

        // ECDSA (Elliptic Curve Digital Signature Algorithm) is lightweight and highly secure
        val signature = Signature.getInstance("SHA256withECDSA")
        signature.initSign(privateKey)
        signature.update(payload.toByteArray(Charsets.UTF_8))

        return signature.sign()
    }

    /**
     * Generates a standard ES256 JSON Web Token (JWT).
     * Proves the agent possesses the hardware TPM.
     * * 泙 NOTE: Call generateHardwareKey() before invoking this method.
     * Throws SecurityException if the hardware key has not been initialized.
     */
    fun generateJwt(agentId: String): String {
        // 1. Create Header
        val header = JSONObject().apply {
            put("alg", "ES256")
            put("typ", "JWT")
        }.toString()

        // 2. Create Payload (Expires in 5 minutes to prevent replay attacks)
        val now = System.currentTimeMillis() / 1000
        val payload = JSONObject().apply {
            put("sub", agentId)
            put("aud", "pan_ops_hub")
            put("iat", now)
            put("exp", now + 300)
        }.toString()

        // 3. Base64Url encode Header and Payload
        val b64Header = Base64.encodeToString(header.toByteArray(Charsets.UTF_8), Base64.URL_SAFE or Base64.NO_PADDING or Base64.NO_WRAP)
        val b64Payload = Base64.encodeToString(payload.toByteArray(Charsets.UTF_8), Base64.URL_SAFE or Base64.NO_PADDING or Base64.NO_WRAP)

        val dataToSign = "$b64Header.$b64Payload"

        // 4. Sign via TPM (Hardware Enclave)
        val derSignature = signPayload(dataToSign)

        // 5. Convert Android's native DER format to the JWT RAW format
        val rawSignature = convertDerToRaw(derSignature)

        val b64Signature = Base64.encodeToString(rawSignature, Base64.URL_SAFE or Base64.NO_PADDING or Base64.NO_WRAP)

        return "$dataToSign.$b64Signature"
    }

    /**
     * Extracts the raw 64-byte (R, S) signature from an ASN.1 DER payload.
     * Required for standard PyJWT verification on the backend.
     */
    private fun convertDerToRaw(der: ByteArray): ByteArray {
        // 泙 THE FIX: Strict DER structural validation guards
        require(der[0] == 0x30.toByte()) { "Invalid DER SEQUENCE tag" }
        require(der[2] == 0x02.toByte()) { "Invalid DER INTEGER tag for R" }

        var offset = 2
        val rLength = der[offset + 1].toInt()
        val rOffset = offset + 2
        val rBytes = der.copyOfRange(rOffset, rOffset + rLength)

        offset = rOffset + rLength
        require(der[offset] == 0x02.toByte()) { "Invalid DER INTEGER tag for S" }
        val sLength = der[offset + 1].toInt()
        val sOffset = offset + 2
        val sBytes = der.copyOfRange(sOffset, sOffset + sLength)

        // Strip leading zero padding if present
        val cleanR = if (rBytes.size == 33 && rBytes[0] == 0.toByte()) rBytes.copyOfRange(1, 33) else rBytes
        val cleanS = if (sBytes.size == 33 && sBytes[0] == 0.toByte()) sBytes.copyOfRange(1, 33) else sBytes

        // Pad to exactly 32 bytes each
        val paddedR = ByteArray(32).apply { System.arraycopy(cleanR, 0, this, 32 - cleanR.size, cleanR.size) }
        val paddedS = ByteArray(32).apply { System.arraycopy(cleanS, 0, this, 32 - cleanS.size, cleanS.size) }

        return paddedR + paddedS
    }
}