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
                .setUserAuthenticationRequired(true)
                .setIsStrongBoxBacked(true) // 🛡️ PHASE 2 FIX: Enforced hardware root-of-trust
                .build()

            keyPairGenerator.initialize(parameterSpec)
            try {
                keyPairGenerator.generateKeyPair()
            } catch (e: StrongBoxUnavailableException) {
                // If this is thrown, the device does not meet Vanguard 50 pilot requirements.
                // The app must gracefully deny onboarding.
                throw IllegalStateException("Device lacks required hardware secure element.", e)
            }
        }
    }

    /**
     * Creates a signed JWT using the physical hardware key.
     * The private key NEVER leaves the secure element.
     */
    fun generateJwt(agentId: String): String {
        // Ensure the key exists in hardware before trying to use it
        generateHardwareKey()

        val keyStore = KeyStore.getInstance(ANDROID_KEYSTORE)
        keyStore.load(null)

        val privateKey = keyStore.getKey(KEY_ALIAS, null) as PrivateKey

        // 1. Build the JWT Header
        val header = JSONObject().apply {
            put("alg", "ES256")
            put("typ", "JWT")
        }

        // 2. Build the JWT Payload (Expires in 5 minutes)
        val now = System.currentTimeMillis() / 1000
        val payload = JSONObject().apply {
            put("iss", "pan_tactical_hardware")
            put("sub", agentId)
            put("iat", now)
            put("exp", now + 300)
            put("attestation_level", "strongbox")
        }

        val b64Header = Base64.encodeToString(header.toString().toByteArray(), Base64.URL_SAFE or Base64.NO_PADDING or Base64.NO_WRAP)
        val b64Payload = Base64.encodeToString(payload.toString().toByteArray(), Base64.URL_SAFE or Base64.NO_PADDING or Base64.NO_WRAP)
        val dataToSign = "$b64Header.$b64Payload"

        // 3. Ask the Hardware to sign the data (The OS passes it to the chip)
        val signature = Signature.getInstance("SHA256withECDSA")
        signature.initSign(privateKey)
        signature.update(dataToSign.toByteArray())
        val derSignatureBytes = signature.sign()

        // 4. Convert the DER signature back into a standard JWT signature
        val rawSignatureBytes = convertDerToRaw(derSignatureBytes)
        val b64Signature = Base64.encodeToString(rawSignatureBytes, Base64.URL_SAFE or Base64.NO_PADDING or Base64.NO_WRAP)

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

        // Ensure exactly 32 bytes for each
        val finalR = ByteArray(32)
        System.arraycopy(cleanR, maxOf(0, cleanR.size - 32), finalR, maxOf(0, 32 - cleanR.size), minOf(32, cleanR.size))

        val finalS = ByteArray(32)
        System.arraycopy(cleanS, maxOf(0, cleanS.size - 32), finalS, maxOf(0, 32 - cleanS.size), minOf(32, cleanS.size))

        return finalR + finalS
    }
}