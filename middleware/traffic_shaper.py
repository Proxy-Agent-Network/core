from typing import Dict, Optional, Tuple
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time

# PROXY PROTOCOL - TRAFFIC SHAPER MIDDLEWARE (v1)
# "Shedding load to preserve whale performance."

class BrownoutLevel:
    GREEN = "GREEN"
    YELLOW = "YELLOW"
    ORANGE = "ORANGE"
    RED = "RED"

# Configuration from specs/v1/brownout_logic.md
BROWNOUT_THRESHOLDS = {
    BrownoutLevel.GREEN: {"max_tasks": 1000, "min_rep": 300},
    BrownoutLevel.YELLOW: {"max_tasks": 5000, "min_rep": 500},
    BrownoutLevel.ORANGE: {"max_tasks": 10000, "min_rep": 700},
    BrownoutLevel.RED: {"max_tasks": float('inf'), "min_rep": 900},
}

class TrafficShaperMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 1. Identify the Actor (Node)
        node_rep = self._get_node_reputation(request)
        
        # 2. Check Network Health
        current_depth = self._get_mempool_depth()
        level, min_rep = self._determine_brownout_level(current_depth)

        # 3. The Gatekeeper Logic
        if level != BrownoutLevel.GREEN and node_rep < min_rep:
            # SHEDDING TRAFFIC
            response = Response(
                content=f"Network Busy. Brownout Level: {level}. Min Rep: {min_rep}", 
                status_code=503
            )
            response.headers["X-Proxy-Brownout"] = "Active"
            response.headers["X-Proxy-Min-Reputation"] = str(min_rep)
            response.headers["Retry-After"] = "600" # Try again in 10 mins
            return response

        # 4. Proceed normally
        response = await call_next(request)
        return response

    def _determine_brownout_level(self, depth: int) -> Tuple[str, int]:
        """Maps mempool depth to the required reputation score."""
        if depth < BROWNOUT_THRESHOLDS[BrownoutLevel.GREEN]["max_tasks"]:
            return BrownoutLevel.GREEN, BROWNOUT_THRESHOLDS[BrownoutLevel.GREEN]["min_rep"]
        
        if depth < BROWNOUT_THRESHOLDS[BrownoutLevel.YELLOW]["max_tasks"]:
            return BrownoutLevel.YELLOW, BROWNOUT_THRESHOLDS[BrownoutLevel.YELLOW]["min_rep"]
            
        if depth < BROWNOUT_THRESHOLDS[BrownoutLevel.ORANGE]["max_tasks"]:
            return BrownoutLevel.ORANGE, BROWNOUT_THRESHOLDS[BrownoutLevel.ORANGE]["min_rep"]
            
        return BrownoutLevel.RED, BROWNOUT_THRESHOLDS[BrownoutLevel.RED]["min_rep"]

    def _get_mempool_depth(self) -> int:
        # In prod, this queries Redis or the LND mempool
        return 6000  # Mock: Simulating "Orange" congestion

    def _get_node_reputation(self, request: Request) -> int:
        # In prod, this extracts the JWT/Auth header and queries the DB
        # Mocking a "Probationary" node for this demo
        return 450
