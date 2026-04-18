# --- PAN TACTICAL R8/PROGUARD RULES ---

# Preserve generic type signatures for Coroutines and Serialization
-keepattributes *Annotation*, InnerClasses, Signature

# Kotlinx Serialization
-keep class kotlinx.serialization.** { *; }
-dontnote kotlinx.serialization.**

# Preserve PAN Tactical Data Models and Network DTOs for JSON parsing
-keep class com.pan.tactical.models.** { *; }
-keep class com.pan.tactical.network.*Payload { *; }
-keep class com.pan.tactical.network.*Request { *; }

# Ktor Network Engine
-keep class io.ktor.** { *; }

# Firebase SDKs
-keep class com.google.firebase.** { *; }

# Play Integrity / Security Crypto
-keep class com.google.android.play.core.integrity.** { *; }
-keep class androidx.security.crypto.** { *; }

# PAN Tactical Security Enclave
-keep class com.pan.tactical.security.StrongBoxManager { *; }