# --- PAN TACTICAL R8/PROGUARD RULES ---

# Preserve generic type signatures for Coroutines and Serialization
-keepattributes *Annotation*, InnerClasses, Signature

# Kotlinx Serialization
-dontnote kotlinx.serialization.**
-keepclassmembers class com.pan.tactical.** { *; }

# Ktor Network Engine
-keep class io.ktor.** { *; }

# Firebase SDKs
-keep class com.google.firebase.** { *; }

# Play Integrity / Security Crypto
-keep class com.google.android.play.core.integrity.** { *; }
-keep class androidx.security.crypto.** { *; }