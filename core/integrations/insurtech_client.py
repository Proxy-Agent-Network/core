import os
import logging
import aiohttp
import asyncio
import uuid
import hashlib
from typing import Optional

logger = logging.getLogger("PAN_InsurTech")

class InsurTechClient:
    def __init__(self):
        self.api_url = os.getenv("INSURTECH_API_URL", "https://api.sandbox.insurtech-partner.com/v1/policies/bind")
        
        # Explicit mock fallback with visible warning
        self.api_key = os.getenv("INSURTECH_API_KEY")
        if not self.api_key:
            logger.warning("⚠️ [INSURANCE] INSURTECH_API_KEY not set — operating in mock mode")
            self.api_key = "mock_key_123"
        
    async def bind_hnoa_policy(self, session: aiohttp.ClientSession, task_id: str, agent_id: str, role: str) -> bool:
        """
        Fires an asynchronous webhook to bind a $1M HNOA micro-policy for the duration of the task.
        """
        # Generate a deterministic UUID for strict API gateways
        idempotency_str = f"bind_{task_id}_{agent_id}"
        idempotency_key = str(uuid.UUID(hashlib.md5(idempotency_str.encode()).hexdigest()))
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-Idempotency-Key": idempotency_key
        }
        
        payload = {
            "agent_id": agent_id,
            "mission_id": task_id,
            "coverage_type": "HNOA_1M",
            "risk_profile": "PERIMETER" if role.upper() == "SENTRY" else "MECHANIC",
            "status": "ACTIVE"
        }

        # Specific timeouts for connection vs total response time
        timeout = aiohttp.ClientTimeout(total=3.0, connect=1.0)

        # 3 Retries with exponential backoff for network resilience (5xx only)
        for attempt in range(3):
            try:
                async with session.post(self.api_url, json=payload, headers=headers, timeout=timeout) as response:
                    if response.status in (200, 201):
                        data = await response.json()
                        policy_id = data.get("policy_id", "UNKNOWN_POLICY")
                        logger.info(f"🛡️ [INSURANCE] Bound $1M HNOA policy {policy_id} for Agent {agent_id} on {task_id}")
                        return True
                    elif response.status >= 500:
                        logger.warning(f"⚠️ [INSURANCE] Provider error {response.status} on attempt {attempt + 1}")
                        # Fall through to backoff and retry
                    else:
                        # 4xx — retrying won't help
                        logger.error(f"❌ [INSURANCE] Provider rejected bind for {task_id}. Status: {response.status}. Not retrying.")
                        return False
                        
            except asyncio.TimeoutError:
                logger.warning(f"⚠️ [INSURANCE] Timeout on attempt {attempt + 1} for {task_id}")
            except Exception as e:
                logger.error(f"❌ [INSURANCE] Failed to bind policy for {task_id}: {e}")
            
            # Backoff before retrying (0.5s, 1.0s, 2.0s)
            await asyncio.sleep(0.5 * (2 ** attempt))

        logger.critical(f"🛑 [INSURANCE] FATAL: Could not bind coverage for {task_id} after 3 attempts. Agent {agent_id} is operating UNINSURED.")
        return False