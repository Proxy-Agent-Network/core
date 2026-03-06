import org.jetbrains.compose.desktop.application.dsl.TargetFormat
import org.jetbrains.kotlin.gradle.dsl.JvmTarget
import java.util.Properties
import java.io.FileInputStream

plugins {
    alias(libs.plugins.kotlinMultiplatform)
    alias(libs.plugins.androidApplication)
    alias(libs.plugins.composeMultiplatform)
    alias(libs.plugins.composeCompiler)

    alias(libs.plugins.kotlinxSerialization)
}

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
            // Default UI dependencies
            implementation(libs.compose.uiToolingPreview)
            implementation(libs.androidx.activity.compose)

            // --- PAN TACTICAL: HARDWARE CHASSIS ---
            // Hardware Root of Trust & Anti-Spoofing
            implementation("com.google.android.play:integrity:1.3.0")
            implementation("androidx.security:security-crypto-ktx:1.1.0-alpha06")

            // PIP-018: Edge-Vision PII Redaction (Face Blurring)
            implementation("com.google.mlkit:face-detection:16.1.6")

            // Precision Spatial Homing (15-meter micro-routing)
            implementation("androidx.core.uwb:uwb:1.0.0-alpha08")

            // Tactical Mapping Engine
            implementation("com.google.maps.android:maps-compose:4.3.3")
            implementation("com.google.android.gms:play-services-maps:18.2.0")

            // Google Play Services: Live Telemetry
            implementation("com.google.android.gms:play-services-location:21.2.0")

            // Ktor Android Engine
            implementation("io.ktor:ktor-client-okhttp:2.3.8")

            // Ktor Networking (Cross-Platform)
            implementation("io.ktor:ktor-client-core:2.3.8")
            implementation("io.ktor:ktor-client-content-negotiation:2.3.8")
            implementation("io.ktor:ktor-serialization-kotlinx-json:2.3.8")

            // THE NEW LIVE LINE:
            implementation("io.ktor:ktor-client-websockets:2.3.8")
        }
        commonMain.dependencies {
            // Default UI dependencies
            implementation(libs.compose.runtime)
            implementation(libs.compose.foundation)
            implementation(libs.compose.material3)
            implementation(libs.compose.ui)
            implementation(libs.compose.components.resources)
            implementation(libs.compose.uiToolingPreview)
            implementation(libs.androidx.lifecycle.viewmodelCompose)
            implementation(libs.androidx.lifecycle.runtimeCompose)

            // --- PAN TACTICAL: SHARED ENGINE ---
            // Asynchronous background threads
            implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.8.0")

            // Ktor Networking (Cross-Platform)
            implementation("io.ktor:ktor-client-core:2.3.8")
            implementation("io.ktor:ktor-client-content-negotiation:2.3.8")
            implementation("io.ktor:ktor-serialization-kotlinx-json:2.3.8")
        }
        commonTest.dependencies {
            implementation(libs.kotlin.test)
        }
    }
}

android {
    namespace = "network.proxyagent.pantactical"
    compileSdk = libs.versions.android.compileSdk.get().toInt()

    defaultConfig {
        applicationId = "network.proxyagent.pantactical"
        minSdk = libs.versions.android.minSdk.get().toInt()
        targetSdk = libs.versions.android.targetSdk.get().toInt()
        versionCode = 1
        versionName = "1.0"

        // --- SECURE API KEY INJECTION ---
        val localProperties = Properties()
        val localPropertiesFile = rootProject.file("local.properties")
        if (localPropertiesFile.exists()) {
            localProperties.load(FileInputStream(localPropertiesFile))
        }
        val mapsApiKey = localProperties.getProperty("MAPS_API_KEY") ?: ""

        manifestPlaceholders["MAPS_API_KEY"] = mapsApiKey
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

