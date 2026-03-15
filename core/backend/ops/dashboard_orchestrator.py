import asyncio
import json
import logging
import time
import requests
from typing import Dict, List, Set
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

# PROXY PROTOCOL - DASHBOARD ORCHESTRATOR (v1.0)
# "Single-stream synchronization for the protocol UI suite."
# ----------------------------------------------------

app = FastAPI(title="Proxy Protocol Dashboard Orchestrator")

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Orchestrator")

class ConnectionManager:
    """Manages active WebSocket connections for real-time broadcasting."""
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"[*] Portal Connected. Active Streams: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"[*] Portal Disconnected. Active Streams: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        if not self.active_connections:
            return
        
        # Broadcast to all connected portals simultaneously
        tasks = [connection.send_json(message) for connection in self.active_connections]
        await asyncio.gather(*tasks, return_exceptions=True)

manager = ConnectionManager()

class DataAggregator:
    """
    Polls internal protocol APIs and constructs a unified state object.
    Reduces frontend complexity by providing a pre-joined data model.
    """
    def __init__(self):
        # Internal API Endpoints (Established in previous Canvas versions)
        self.endpoints = {
            "status": "http://localhost:8001/v1/status",
            "reputation": "http://localhost:8004/v1/reputation/batch",
            "registry": "http://localhost:8006/v1/registry/batch"
        }
        self.cache = {}

    async def fetch_unified_state(self) -> Dict:
        """Aggregates data from Status, Reputation, and Registry services."""
        # Simulation: In production, these use aiohttp for non-blocking IO
        # Here we mock the combined output for architectural demonstration
        
        timestamp = int(time.time())
        
        unified_payload = {
            "type": "PROTOCOL_TICK",
            "timestamp": timestamp,
            "network": {
                "api_gateway": "OPERATIONAL",
                "lightning_rails": "OPERATIONAL",
                "active_nodes": 1248,
                "congestion": 1.0,
                "latency_ms": 42
            },
            "reputation": {
                "avg_score": 942.5,
                "stability_index": "99.2%",
                "top_performers": ["NODE_ELITE_X29", "NODE_WHALE_04", "NODE_ALPHA_001"]
            },
            "economics": {
                "treasury_reserves": 71790100,
                "insurance_pool": 10450200,
                "active_escrows": 4200500
            }
        }
        
        return unified_payload

# Initialize Aggregator
aggregator = DataAggregator()

# --- Background Task: The Heartbeat ---

async def protocol_heartbeat_loop():
    """
    Main background thread that drives the WebSocket stream.
    Updates all portals every 2 seconds.
    """
    logger.info("[*] Starting Background Heartbeat Loop...")
    while True:
        try:
            # 1. Fetch the unified state from all internal services
            state = await aggregator.fetch_unified_state()
            
            # 2. Broadcast the state to all connected frontends
            await manager.broadcast(state)
            
        except Exception as e:
            logger.error(f"[!] Aggregation Error: {str(e)}")
            
        await asyncio.sleep(2) # 2-second synchronization interval

@app.on_event("startup")
async def startup_event():
    """Triggers the heartbeat loop on FastAPI initialization."""
    asyncio.create_task(protocol_heartbeat_loop())

# --- WebSocket Endpoint ---

@app.websocket("/v1/orchestrator/stream")
async def websocket_stream(websocket: WebSocket):
    """
    High-performance entry point for Portals (React/HTML).
    Usage: ws://localhost:8008/v1/orchestrator/stream
    """
    await manager.connect(websocket)
    try:
        while True:
            # Keep-alive loop
            data = await websocket.receive_text()
            # Portals can optionally send commands back (e.g., filter changes)
            logger.info(f"[*] Received command from portal: {data}")
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"[!] WebSocket Error: {str(e)}")
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    # Launched on a dedicated port for frontend orchestration
    print("[*] Launching Protocol Dashboard Orchestrator on port 8008...")
    uvicorn.run(app, host="0.0.0.0", port=8008)
