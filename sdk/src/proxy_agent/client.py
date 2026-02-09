import requests
from typing import Dict, Any, Optional

class ProxyClient:
    """
    The official Python client for the Proxy Agent Network.
    
    This client allows AI Agents to hire human proxies for physical 
    and digital tasks like SMS verification, KYC, and legal signatures.
    """
    
    def __init__(self, api_key: str, base_url: str = "https://api.proxyprotocol.com/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })

    def get_market_ticker(self) -> Dict[str, Any]:
        """Fetch real-time floor prices for human tasks."""
        response = self.session.get(f"{self.base_url}/market/ticker")
        response.raise_for_status()
        return response.json()

    def create_task(self, task_type: str, requirements: Dict[str, Any], max_budget_sats: int) -> Dict[str, Any]:
        """
        Broadcast a new task to the Human Proxy network.
        
        Args:
            task_type: e.g., 'verify_sms_otp', 'legal_notary_sign'
            requirements: Metadata for the human to complete the task
            max_budget_sats: Maximum price the agent is willing to pay
        """
        payload = {
            "type": task_type,
            "requirements": requirements,
            "max_budget_sats": max_budget_sats
        }
        response = self.session.post(f"{self.base_url}/tasks", json=payload)
        response.raise_for_status()
        return response.json()

    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Check the progress of a specific task."""
        response = self.session.get(f"{self.base_url}/tasks/{task_id}")
        response.raise_for_status()
        return response.json()
