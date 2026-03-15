import requests
import json
import os

# PROXY PROTOCOL - SWAG AUTOMATION (v1)
# "Real Humans deserve Real Shirts."
# ----------------------------------------------------
# Dependencies: pip install requests

# Configuration
PRINTFUL_API_KEY = os.getenv("PRINTFUL_API_KEY", "pk_test_...")
PROXY_API_URL = "https://api.proxyprotocol.com/v1"
SHIRT_VARIANT_ID = 1337  # ID for "Proxy Potion" Tee (Large) - In prod, map to sizes

class SwagDistributor:
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {PRINTFUL_API_KEY}",
            "Content-Type": "application/json"
        }
        self.COHORT_LIMIT = 100

    def check_eligibility(self, node_id: str) -> bool:
        """
        Verifies if the Node is Tier 2+ and within the first 100 winners.
        """
        # 1. Check Cohort Count (Mock DB query)
        current_winners = 42 # Simulate 42 shirts already sent
        if current_winners >= self.COHORT_LIMIT:
            print(f"[Swag] Cohort Full ({current_winners}/100). No shirt for you.")
            return False

        # 2. Check Node Tier
        # In prod: response = requests.get(f"{PROXY_API_URL}/nodes/{node_id}")
        node_tier = 2
        if node_tier < 2:
            print(f"[Swag] Node {node_id} is Tier {node_tier}. Upgrade required.")
            return False

        return True

    def trigger_shipment(self, recipient: dict):
        """
        Calls Printful API to drop-ship the shirt.
        """
        print(f"[Swag] Ordering shirt for {recipient['name']}...")
        
        payload = {
            "recipient": {
                "name": recipient['name'],
                "address1": recipient['address'],
                "city": recipient['city'],
                "state_code": recipient['state'],
                "country_code": recipient['country'],
                "zip": recipient['zip']
            },
            "items": [
                {
                    "variant_id": self._map_size_to_variant(recipient['size']),
                    "quantity": 1,
                    "files": [
                        {
                            "url": "https://proxyprotocol.com/assets/human_power_design.png"
                        }
                    ]
                }
            ]
        }

        # Mocking the Printful Request
        # response = requests.post("https://api.printful.com/orders", json=payload, headers=self.headers)
        # order_data = response.json()
        
        print(f"✅ ORDER PLACED! Tracking: #99283-PROXY")
        print(f"   -> Ship to: {recipient['city']}, {recipient['country']}")

    def _map_size_to_variant(self, size: str) -> int:
        # Map "L", "XL" to Printful Variant IDs
        sizes = {"S": 401, "M": 402, "L": 403, "XL": 404}
        return sizes.get(size, 403) # Default to Large

    def handle_webhook(self, event: dict):
        """
        Entry point for the 'task.completed' webhook.
        """
        if event['type'] != 'task.completed':
            return

        node_id = event['data']['node_id']
        
        if self.check_eligibility(node_id):
            # In a real flow, we would trigger a "Claim Swag" email to the user
            # to collect their address securely.
            # For this demo, we assume we have the address from their KYC profile.
            
            human_details = {
                "name": "Jane Doe",
                "address": "123 Cyberpunk Lane",
                "city": "Neo Tokyo",
                "state": "CA",
                "country": "US",
                "zip": "90210",
                "size": "M"
            }
            
            self.trigger_shipment(human_details)

# --- Simulation ---
if __name__ == "__main__":
    bot = SwagDistributor()
    
    print("--- SWAG BOT ACTIVATED ---")
    
    # Mock Event: Human just finished a Tier 2 Identity Verification
    mock_event = {
        "type": "task.completed",
        "data": {
            "task_id": "task_8829",
            "node_id": "node_human_alpha",
            "tier_required": 2
        }
    }
    
    bot.handle_webhook(mock_event)
