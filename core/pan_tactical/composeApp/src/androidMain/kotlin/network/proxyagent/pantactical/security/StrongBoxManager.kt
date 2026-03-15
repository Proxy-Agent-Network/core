package network.proxyagent.pantactical.security

import android.security.keystore.KeyGenParameterSpec
import android.security.keystore.KeyProperties
import android.security.keystore.StrongBoxUnavailableException
import java.security.KeyPairGenerator
import java.security.KeyStore
import java.security.PrivateKey
import java.security.Signature
import java.security.spec.ECGenParameterSpec

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
                // --- THE FORTRESS WALL ---
                // This boolean is the difference between SB 1417 compliance and a security breach.
                // It forces the key into the physical TPM 2.0 chip.
                .setIsStrongBoxBacked(true)
                .build()

            try {
                keyPairGenerator.initialize(parameterSpec)
                keyPairGenerator.generateKeyPair()
            } catch (e: StrongBoxUnavailableException) {
                // If the device is an emulator or an old phone without a TPM, we kill the process.
                // Vanguard Agents CANNOT operate without hardware attestation.
                throw SecurityException("CRITICAL: Device lacks TPM 2.0 StrongBox. Agent disqualified.")
            }
        }
    }

    /**
     * Signs the SB 1417 Audit Log or the L402 Preimage.
     * The Private Key never leaves the physical hardware chip; we just pass the
     * data to the chip, and the chip hands us back the signature.
     */
    fun signPayload(payload: String): ByteArray {
        val keyStore = KeyStore.getInstance(ANDROID_KEYSTORE)
        keyStore.load(null)

        // Retrieve the key handle (not the actual key data, which is locked in hardware)
        val privateKey = keyStore.getKey(KEY_ALIAS, null) as PrivateKey

        // ECDSA (Elliptic Curve Digital Signature Algorithm) is lightweight and highly secure
        val signature = Signature.getInstance("SHA256withECDSA")
        signature.initSign(privateKey)
        signature.update(payload.toByteArray(Charsets.UTF_8))

        return signature.sign()
    }
}