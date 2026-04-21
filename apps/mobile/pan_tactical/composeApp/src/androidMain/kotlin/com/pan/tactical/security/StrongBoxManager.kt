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
import com.pan.tactical.BuildConfig

class StrongBoxManager {

    companion object {
        private const val KEY_ALIAS = "vanguard_attestation_key"
        private const val ANDROID_KEYSTORE = "AndroidKeyStore"
    }

    fun generateHardwareKey() {
        val keyStore = KeyStore.getInstance(ANDROID_KEYSTORE)
        keyStore.load(null)

        if (!keyStore.containsAlias(KEY_ALIAS)) {
            val keyPairGenerator = KeyPairGenerator.getInstance(
                KeyProperties.KEY_ALGORITHM_EC,
                ANDROID_KEYSTORE
            )

            val builder = KeyGenParameterSpec.Builder(
                KEY_ALIAS,
                KeyProperties.PURPOSE_SIGN or KeyProperties.PURPOSE_VERIFY
            )
                .setAlgorithmParameterSpec(ECGenParameterSpec("secp256r1"))
                .setDigests(KeyProperties.DIGEST_SHA256)

            // 🛡️ DEV BYPASS GUARD: Automatically enforced by the compiler
            if (BuildConfig.IS_DEBUG) {
                builder.setUserAuthenticationRequired(false)
            } else {
                builder.setUserAuthenticationRequired(true)
                // 🛡️ CRITICAL FIX: Authorize key usage for 5 minutes post-unlock to prevent silent background signing failures
                builder.setUserAuthenticationValidityDurationSeconds(300)
                builder.setIsStrongBoxBacked(true)
            }

            keyPairGenerator.initialize(builder.build())
            try {
                keyPairGenerator.generateKeyPair()
            } catch (e: StrongBoxUnavailableException) {
                throw IllegalStateException("Device lacks required hardware secure element.", e)
            }
        }
    }

    fun getPublicKeyBase64(): String {
        val keyStore = KeyStore.getInstance(ANDROID_KEYSTORE)
        keyStore.load(null)
        val certificate = keyStore.getCertificate(KEY_ALIAS)
            ?: throw IllegalStateException("Hardware key not found. Please generate it first.")

        return Base64.encodeToString(certificate.publicKey.encoded, Base64.NO_WRAP)
    }

    fun generateJwt(agentId: String): String {
        generateHardwareKey()

        val keyStore = KeyStore.getInstance(ANDROID_KEYSTORE)
        keyStore.load(null)

        val privateKey = keyStore.getKey(KEY_ALIAS, null) as PrivateKey

        val header = JSONObject().apply {
            put("alg", "ES256")
            put("typ", "JWT")
        }

        val now = System.currentTimeMillis() / 1000
        val payload = JSONObject().apply {
            put("iss", "pan_tactical_hardware")
            put("sub", agentId)
            put("iat", now)
            put("exp", now + 300)
            put("attestation_level", if (BuildConfig.IS_DEBUG) "dev_tee_bypass" else "strongbox")
        }

        val b64Header = Base64.encodeToString(header.toString().toByteArray(), Base64.URL_SAFE or Base64.NO_PADDING or Base64.NO_WRAP)
        val b64Payload = Base64.encodeToString(payload.toString().toByteArray(), Base64.URL_SAFE or Base64.NO_PADDING or Base64.NO_WRAP)
        val dataToSign = "$b64Header.$b64Payload"

        val signature = Signature.getInstance("SHA256withECDSA")
        signature.initSign(privateKey)
        signature.update(dataToSign.toByteArray())
        val derSignatureBytes = signature.sign()

        val rawSignatureBytes = convertDerToRaw(derSignatureBytes)
        val b64Signature = Base64.encodeToString(rawSignatureBytes, Base64.URL_SAFE or Base64.NO_PADDING or Base64.NO_WRAP)

        return "$dataToSign.$b64Signature"
    }

    private fun convertDerToRaw(der: ByteArray): ByteArray {
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

        val cleanR = if (rBytes.size == 33 && rBytes[0] == 0.toByte()) rBytes.copyOfRange(1, 33) else rBytes
        val cleanS = if (sBytes.size == 33 && sBytes[0] == 0.toByte()) sBytes.copyOfRange(1, 33) else sBytes

        val finalR = ByteArray(32)
        System.arraycopy(cleanR, maxOf(0, cleanR.size - 32), finalR, maxOf(0, 32 - cleanR.size), minOf(32, cleanR.size))

        val finalS = ByteArray(32)
        System.arraycopy(cleanS, maxOf(0, cleanS.size - 32), finalS, maxOf(0, 32 - cleanS.size), minOf(32, cleanS.size))

        return finalR + finalS
    }
}