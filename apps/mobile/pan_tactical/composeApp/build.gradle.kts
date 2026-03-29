import org.jetbrains.compose.desktop.application.dsl.TargetFormat
import org.jetbrains.kotlin.gradle.dsl.JvmTarget
import org.gradle.api.GradleException
import java.util.Properties
import java.io.FileInputStream

plugins {
    alias(libs.plugins.kotlinMultiplatform)
    alias(libs.plugins.androidApplication)
    alias(libs.plugins.composeMultiplatform)
    alias(libs.plugins.composeCompiler)

    // 🟢 THE FIX: Strictly aligned with the 2.1.0 Kotlin compiler from libs.versions.toml
    kotlin("plugin.serialization") version "2.1.0"

    id("com.github.gmazzo.buildconfig") version "4.1.2"
}

// --- SECURE VAULT EXTRACTION (HOISTED FOR KMP) ---
val localProperties = Properties()
val localPropertiesFile = rootProject.file("local.properties")
if (localPropertiesFile.exists()) {
    localProperties.load(localPropertiesFile.inputStream())
}

// 🛠️ THE FIX 1: Hard fail at build time if a secret is missing
fun requireLocalProperty(key: String): String {
    return localProperties.getProperty(key)
        ?: throw GradleException("🛑 FATAL: Missing required local.properties key: '$key'. Cannot build securely.")
}

val secureMapsKey = requireLocalProperty("MAPS_API_KEY")
val secureIosMapsKey = requireLocalProperty("IOS_MAPS_API_KEY")
val secureImgbbKey = requireLocalProperty("IMGBB_API_KEY")
val firebaseRtdbUrl = requireLocalProperty("FIREBASE_RTDB_URL")

// 🛠️ THE FIX 2: Extracted missing properties for the Network Client and Attestation Engine
val panApiBaseUrl = requireLocalProperty("PAN_API_BASE_URL")
val agentDevToken = requireLocalProperty("AGENT_DEV_TOKEN")

// 🟢 THE FIX: Safely parse the GCP Project Number as a Long, or fail the build if invalid
val playIntegrityProjectNumStr = requireLocalProperty("PLAY_INTEGRITY_CLOUD_PROJECT_NUMBER")
val playIntegrityProjectNumLong = playIntegrityProjectNumStr.toLongOrNull()
    ?: throw GradleException("🛑 FATAL: PLAY_INTEGRITY_CLOUD_PROJECT_NUMBER must be a valid number.")
// -------------------------------------------------

// --- KMP SECRETS BRIDGE ---
buildConfig {
    packageName("com.pan.tactical")
    buildConfigField("String", "MAPS_API_KEY", "\"$secureMapsKey\"")
    buildConfigField("String", "IOS_MAPS_API_KEY", "\"$secureIosMapsKey\"")
    buildConfigField("String", "IMGBB_API_KEY", "\"$secureImgbbKey\"")
    buildConfigField("String", "FIREBASE_RTDB_URL", "\"$firebaseRtdbUrl\"")

    // 🛠️ THE FIX 2: Injecting the missing fields into BuildConfig exactly once!
    buildConfigField("String", "PAN_API_BASE_URL", "\"$panApiBaseUrl\"")
    buildConfigField("String", "AGENT_DEV_TOKEN", "\"$agentDevToken\"")
    
    // 🟢 THE FIX: Injected as a primitive Long so the Kotlin compiler enforces type safety
    buildConfigField("Long", "GCP_PROJECT_NUMBER", "${playIntegrityProjectNumLong}L")
}
// --------------------------

kotlin {
    androidTarget {
        compilerOptions {
            jvmTarget.set(JvmTarget.JVM_11)
        }
    }

    listOf(
        iosArm64(),
        iosSimulatorArm64()
    ).forEach { iosTarget ->
        iosTarget.binaries.framework {
            baseName = "ComposeApp"
            isStatic = true
        }
    }

    sourceSets {
        androidMain.dependencies {
            implementation(libs.compose.uiToolingPreview)
            implementation(libs.androidx.activity.compose)

            // --- PAN TACTICAL ANDROID-SPECIFIC ENGINES ---

            implementation(project.dependencies.platform("com.google.firebase:firebase-bom:33.0.0"))
            implementation("com.google.firebase:firebase-auth-ktx")
            implementation("com.google.firebase:firebase-messaging-ktx")

            // Google Maps & Location Telemetry
            implementation("com.google.android.gms:play-services-location:21.2.0")
            implementation("com.google.maps.android:maps-compose:4.4.1")

            // Hardware Security & Attestation
            implementation("com.google.android.play:integrity:1.4.0")

            // 🛠️ MINOR FIX: Replaced unstable alpha with stable release
            implementation("androidx.security:security-crypto:1.0.0")

            // ML Kit (On-Device Face & Text Privacy Redaction)
            implementation("com.google.mlkit:face-detection:16.1.6")
            implementation("com.google.mlkit:text-recognition:16.0.0")

            // Ktor Android Engine (For PanApiClient)
            implementation("io.ktor:ktor-client-okhttp:2.3.11")
            
            // 🟢 THE FIX: Re-added UWB dependency required by AndroidUwbClient
            // TODO (Q3): Required for real BLE OOB handshake and ranging
            implementation("androidx.core.uwb:uwb:1.0.0-alpha08")
        }

        commonMain.dependencies {
            implementation(libs.compose.runtime)
            implementation(libs.compose.foundation)
            implementation(libs.compose.material3)
            implementation(libs.compose.ui)
            implementation(libs.compose.components.resources)
            implementation(libs.compose.uiToolingPreview)
            implementation(libs.androidx.lifecycle.viewmodelCompose)
            implementation(libs.androidx.lifecycle.runtimeCompose)

            // --- PAN TACTICAL SHARED LIBRARIES ---

            // Serialization (For AgentModels.kt)
            implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.6.3")

            // Ktor (Network Client for the REST APIs)
            implementation("io.ktor:ktor-client-core:2.3.11")
            implementation("io.ktor:ktor-client-content-negotiation:2.3.11")
            implementation("io.ktor:ktor-serialization-kotlinx-json:2.3.11")

            // 🛠️ THE FIX 5: Promoted Coil from unstable alpha to 3.0.4 stable
            implementation("io.coil-kt.coil3:coil-compose:3.0.4")
            implementation("io.coil-kt.coil3:coil-network-ktor2:3.0.4")
        }

        iosMain.dependencies {
            // Ktor iOS Engine (Darwin)
            implementation("io.ktor:ktor-client-darwin:2.3.11")
        }

        commonTest.dependencies {
            implementation(libs.kotlin.test)
        }
    }
}

android {
    namespace = "com.pan.tactical"
    compileSdk = libs.versions.android.compileSdk.get().toInt()

    buildFeatures { 
        // Disabled: We use the gmazzo BuildConfig plugin instead for KMP compatibility
        buildConfig = false 
    }

    defaultConfig {
        applicationId = "com.pan.tactical"
        minSdk = 26
        targetSdk = libs.versions.android.targetSdk.get().toInt()
        versionCode = 1
        versionName = "1.0"

        manifestPlaceholders["MAPS_API_KEY"] = secureMapsKey

    }

    packaging {
        resources {
            excludes += "/META-INF/{AL2.0,LGPL2.1}"
        }
    }

    buildTypes {
        getByName("release") {
            // 🛠️ THE FIX 4: Enabled R8 minification/obfuscation to protect financial logic & keys
            isMinifyEnabled = true
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_11
        targetCompatibility = JavaVersion.VERSION_11
    }
}

dependencies {
    debugImplementation(libs.compose.uiTooling)
}