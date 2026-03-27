package com.pan.tactical.network

import com.pan.tactical.models.MissionData
import io.ktor.client.*
import io.ktor.client.call.*
import io.ktor.client.plugins.contentnegotiation.*
import io.ktor.client.request.*
import io.ktor.client.statement.*
import io.ktor.http.*
import io.ktor.serialization.kotlinx.json.*
import kotlinx.serialization.json.Json
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

object PythonNetworkBridge {
    val client = HttpClient {
        install(ContentNegotiation) {
            json(Json {
                ignoreUnknownKeys = true
                prettyPrint = true
                isLenient = true
            })
        }
    }

    // ⚠️ CRITICAL STEP: Set this to the exact IP address your phone is using to hit the server!
    // If you are using an Android Emulator, 10.0.2.2 is usually correct.
    // If you are using a physical phone, change this to your PC's local Wi-Fi IP (e.g., "http://192.168.0.X:5000")
    // Match whatever IP you are using for your WalletNetworkClient!
    private const val BASE_URL = "http://192.168.0.108:5000"

    suspend fun fetchActiveMissions(): List<MissionData> {
        return withContext(Dispatchers.IO) {
            try {
                // MAKE THE ACTUAL HTTP CALL TO THE NEW FASTAPI ENDPOINT!
                val response: HttpResponse = client.get("$BASE_URL/api/v1/agent/missions") {
                    header("Authorization", "Vanguard-01") // Required by our Python backend security
                }

                if (response.status.isSuccess()) {
                    val missions: List<MissionData> = response.body()
                    if (missions.isNotEmpty()) {
                        println("NETWORK: Successfully fetched ${missions.size} active mission(s) from Ops Hub!")
                    }
                    missions
                } else {
                    println("NETWORK: Server returned error code: ${response.status}")
                    emptyList()
                }
            } catch (e: Exception) {
                println("NETWORK ERROR: Server connection failed - ${e.message}")
                emptyList()
            }
        }
    }
}