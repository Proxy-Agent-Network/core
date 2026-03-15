import org.jetbrains.compose.desktop.application.dsl.TargetFormat
import org.jetbrains.kotlin.gradle.dsl.JvmTarget
import java.util.Properties

plugins {
    alias(libs.plugins.kotlinMultiplatform)
    alias(libs.plugins.androidApplication)
    alias(libs.plugins.composeMultiplatform)
    alias(libs.plugins.composeCompiler)
    // Add the serialization plugin to handle JSON data models
    kotlin("plugin.serialization") version "2.0.20"

    id("com.github.gmazzo.buildconfig") version "4.1.2"
}

// --- SECURE VAULT EXTRACTION (HOISTED FOR KMP) ---
val localProperties = Properties()
val localPropertiesFile = rootProject.file("local.properties")
if (localPropertiesFile.exists()) {
    localProperties.load(localPropertiesFile.inputStream())
}
val secureMapsKey = localProperties.getProperty("MAPS_API_KEY") ?: "MISSING_KEY"
val secureImgbbKey = localProperties.getProperty("IMGBB_API_KEY") ?: "MISSING_KEY"
// -------------------------------------------------

// --- KMP SECRETS BRIDGE ---
buildConfig {
    packageName("com.pan.tactical")
    buildConfigField("String", "MAPS_API_KEY", "\"$secureMapsKey\"")
    buildConfigField("String", "IMGBB_API_KEY", "\"$secureImgbbKey\"")
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

            // Firebase (Auth & Cloud Messaging)
            implementation("com.google.firebase:firebase-auth-ktx:23.0.0")
            implementation("com.google.firebase:firebase-messaging-ktx:24.0.0")

            // Google Maps & Location Telemetry
            implementation("com.google.android.gms:play-services-location:21.2.0")
            implementation("com.google.maps.android:maps-compose:4.4.1") {
                exclude(group = "com.google.android.gms", module = "play-services-maps")
            }

            // Google Navigation SDK (For TacticalNavEngine)
            implementation("com.google.android.libraries.navigation:navigation:5.1.1")

            // Explicitly required Cronet fallback for the Nav SDK
            implementation("org.chromium.net:cronet-fallback:101.4951.41")

            // Hardware Security & Attestation
            implementation("com.google.android.play:integrity:1.4.0")
            implementation("androidx.security:security-crypto:1.1.0-alpha06")

            // ML Kit (On-Device Face & Text Privacy Redaction)
            implementation("com.google.mlkit:face-detection:16.1.6")
            implementation("com.google.mlkit:text-recognition:16.0.0")

            // Ktor Android Engine (For PanApiClient)
            implementation("io.ktor:ktor-client-okhttp:2.3.11")
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

            // Image Loading (To load the Escrow Proof images)
            implementation("io.coil-kt.coil3:coil-compose:3.0.0-alpha10")
            implementation("io.coil-kt.coil3:coil-network-ktor3:3.0.0-alpha10")
        }

        commonTest.dependencies {
            implementation(libs.kotlin.test)
        }
    }
}

android {
    namespace = "com.pan.tactical"
    compileSdk = libs.versions.android.compileSdk.get().toInt()

    // Turned off the Android-specific BuildConfig to prevent duplicate class crashes
    buildFeatures {
        buildConfig = false
    }

    defaultConfig {
        applicationId = "com.pan.tactical"
        minSdk = 26
        targetSdk = libs.versions.android.targetSdk.get().toInt()
        versionCode = 1
        versionName = "1.0"

        // Keeping the manifest placeholder so the Android Google Maps SDK still works!
        manifestPlaceholders["MAPS_API_KEY"] = secureMapsKey
    }
    packaging {
        resources {
            excludes += "/META-INF/{AL2.0,LGPL2.1}"
        }
    }
    buildTypes {
        getByName("release") {
            isMinifyEnabled = false
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