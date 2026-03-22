package com.pan.tactical.network

import com.pan.tactical.models.MissionData
import io.ktor.client.*
import io.ktor.client.plugins.contentnegotiation.*
import io.ktor.client.request.*
import io.ktor.client.statement.*
import io.ktor.http.*
import io.ktor.serialization.kotlinx.json.*
import kotlinx.serialization.json.Json
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.IO
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

    private const val BASE_URL = "https://api.proxyagent.network"

    // --- THE FIX: A state flag so the server doesn't spam you ---
    private var hasSentMockDispatch = false

    suspend fun fetchActiveMissions(): List<MissionData> {
        return withContext(Dispatchers.IO) {
            try {
                println("NETWORK: Attempting to contact Python backend...")

                // Only send the mission if we haven't sent it yet!
                if (!hasSentMockDispatch) {
                    hasSentMockDispatch = true // Mark the queue as empty

                    listOf(
                        MissionData(
                            lat = 33.4255,
                            lon = -111.9400,
                            errorCode = "NET-001: Server Dispatch",
                            bounty = "$75.00",
                            intersection = "Tempe Town Lake"
                        )
                    )
                } else {
                    // The server has no new missions for you right now
                    emptyList()
                }

            } catch (e: Exception) {
                println("NETWORK ERROR: Server connection failed - ${e.message}")
                emptyList()
            }
        }
    }

    // A helper command just in case you want to manually reload the server queue later
    fun resetMockQueue() {
        hasSentMockDispatch = false
    }
}