from typing import Dict, Optional, Tuple, Any
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging

# PROXY PROTOCOL - TRAFFIC SHAPER MIDDLEWARE (v1)
# "Shedding load to preserve whale performance."
# ----------------------------------------------------

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TrafficShaper")

class BrownoutLevel:
    GREEN = "GREEN"    # Normal Operation
    YELLOW = "YELLOW"  # Elevated Load
    ORANGE = "ORANGE"  # High Congestion
    RED = "RED"        # Critical / Whale-Only Mode

# Configuration from specs/v1/brownout_logic.md
BROWNOUT_THRESHOLDS = {
    BrownoutLevel.GREEN: {"max_tasks": 1000, "min_rep": 300},
    BrownoutLevel.YELLOW: {"max_tasks": 5000, "min_rep": 500},
    BrownoutLevel.ORANGE: {"max_tasks": 10000, "min_rep": 700},
    BrownoutLevel.RED: {"max_tasks": float('inf'), "min_rep": 900},
}

class TrafficShaperMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 1. Skip checks for Health/Status endpoints (Always allow ping)
        if request.url.path in ["/health", "/status", "/v1/market/ticker"]:
            return await call_next(request)

        # 2. Identify the Actor (Node or Agent)
        # In a real app, this data comes from the Auth Middleware (JWT/Macaroon)
        # We mock extraction here for the reference implementation.
        actor_context = self._extract_actor_context(request)
        node_rep = actor_context.get("reputation", 0)
        is_whale = actor_context.get("is_whale", False)

        # 3. Check Network Health
        current_depth = self._get_mempool_depth()
        level, min_rep = self._determine_brownout_level(current_depth)

        # 4. The Gatekeeper Logic
        # Whales bypass all brownout checks.
        if is_whale:
            response = await call_next(request)
            response.headers["X-Proxy-Priority"] = "Whale-Pass"
            return response

        # Logic: If we are NOT Green, and the Node's Rep is too low -> Block
        if level != BrownoutLevel.GREEN and node_rep < min_rep:
            logger.warning(f"Brownout Shedding: Level {level}, NodeRep {node_rep} < {min_rep}")
            
            # Construct 503 Response
            response = Response(
                content=f"Network Busy. Brownout Level: {level}. Min Rep Required: {min_rep}", 
                status_code=503
            )
            # Inject Headers so the Node knows WHY it failed (Transparency)
            response.headers["X-Proxy-Brownout"] = "Active"
            response.headers["X-Proxy-Brownout-Level"] = level
            response.headers["X-Proxy-Min-Reputation"] = str(min_rep)
            response.headers["Retry-After"] = "600" # Try again in 10 mins
            return response

        # 5. Proceed normally
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
        """
        Fetches the number of pending tasks in the Redis/LND Queue.
        """
        # Mocking dynamic load for demonstration
        # In prod: redis.llen("task_queue")
        return 6000  # Simulator: Simulating "ORANGE" congestion (requires Rep > 700)

    def _extract_actor_context(self, request: Request) -> Dict[str, Any]:
        """
        Extracts reputation and tier from the request state or headers.
        """
        # Mocking a "Probationary" node (Rep 450) attempting to connect
        # This node should be blocked if level is YELLOW or higher.
        return {
            "reputation": 450,
            "is_whale": False
        }
