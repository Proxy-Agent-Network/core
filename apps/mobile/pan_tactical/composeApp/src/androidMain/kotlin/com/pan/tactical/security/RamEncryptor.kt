package com.pan.tactical.security

import java.security.PublicKey
import java.security.SecureRandom
import javax.crypto.Cipher
import javax.crypto.KeyGenerator
import javax.crypto.spec.GCMParameterSpec

class RamEncryptor {

    companion object {
        private const val AES_KEY_SIZE = 256
        private const val GCM_TAG_LENGTH = 128
        private const val GCM_IV_LENGTH = 12
    }

    /**
     * Encrypts raw image data entirely in Volatile RAM.
     * * @param rawImageData The unencrypted byte array of the photo.
     * @param fleetPublicKey The public RSA key of the Fleet Operator (e.g., Waymo).
     * @return A Pair containing <Encrypted AES Key, Encrypted Image Data>.
     */
    fun encryptAndWipe(rawImageData: ByteArray, fleetPublicKey: PublicKey): Pair<ByteArray, ByteArray> {
        try {
            // 1. Generate a one-time symmetric AES key for this specific mission
            val keyGen = KeyGenerator.getInstance("AES")
            keyGen.init(AES_KEY_SIZE, SecureRandom())
            val aesKey = keyGen.generateKey()

            // 2. Generate a random Initialization Vector (IV) for AES-GCM
            val iv = ByteArray(GCM_IV_LENGTH)
            SecureRandom().nextBytes(iv)
            val gcmSpec = GCMParameterSpec(GCM_TAG_LENGTH, iv)

            // 3. Encrypt the heavy image data using AES-GCM (Fast, handles large files)
            val aesCipher = Cipher.getInstance("AES/GCM/NoPadding")
            aesCipher.init(Cipher.ENCRYPT_MODE, aesKey, gcmSpec)

            // We prepend the IV to the encrypted data payload so the Gateway can decrypt it
            val encryptedImage = iv + aesCipher.doFinal(rawImageData)

            // 4. Encrypt the lightweight AES key using the Fleet's RSA Public Key (The Envelope)
            val rsaCipher = Cipher.getInstance("RSA/ECB/OAEPWithSHA-256AndMGF1Padding")
            rsaCipher.init(Cipher.ENCRYPT_MODE, fleetPublicKey)
            val encryptedAesKey = rsaCipher.doFinal(aesKey.encoded)

            return Pair(encryptedAesKey, encryptedImage)

        } finally {
            // 5. THE BURN PROTOCOL (PIP-016 Compliance)
            // The 'finally' block ensures that even if the encryption crashes halfway through,
            // we mathematically destroy the original unencrypted image data in RAM by
            // overwriting every single byte with a zero.
            rawImageData.fill(0)
        }
    }
}