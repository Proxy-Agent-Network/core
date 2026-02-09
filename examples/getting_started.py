import os
import time
# In a real scenario, this would be installed via 'pip install proxy-agent'
# from proxy_agent import ProxyClient

# Mocking the client import for this example file since we are inside the repo
class ProxyClient:
    def __init__(self, api_key):
        self.api_key = api_key
    
    def get_market_ticker(self):
        # Returns live rates from the Protocol
        return {
            "rates": {"verify_sms_otp": 1500, "legal_notary_sign": 45000},
            "status": "stable"
        }

    def create_task(self, task_type, requirements, max_budget_sats):
        # Dispatches to the human network
        return {
            "id": "task_88293_xyz",
            "status": "matching",
            "estimated_time": "45s"
        }

def print_banner():
    print("""
    ____  ____  ____  ____  __ __ 
   (  _ \(  _ \/ __ \(  _ \(  |  )
    )___/ )   (  (__) ))   / )_  ( 
   (__)  (_)\_)\____/(_)\_)(____/ 
          PROTOCOL v1.0
    [ The Physical Runtime for AI ]
    """)

def main():
    print_banner()
    print("🔌 Connecting to Proxy Network...")
    
    # 1. Initialize with your Secret Key
    client = ProxyClient(api_key="sk_live_demo_key_...")

    # 2. Check the Price
    print("📊 Fetching market rates...")
    ticker = client.get_market_ticker()
    sms_price = ticker['rates']['verify_sms_otp']
    print(f"   -> Current SMS Verification Rate: {sms_price} sats")

    # 3. Hire a Human
    print(f"\n🚀 Dispatching Agent Request: Verify Twitter Account")
    task = client.create_task(
        task_type="verify_sms_otp",
        requirements={
            "service": "Twitter",
            "country": "US",
            "timeout_seconds": 120
        },
        max_budget_sats=2000
    )

    print(f"   -> Task Created! ID: {task['id']}")
    print(f"   -> Human Proxy Status: {task['status']} (Estimated: {task['estimated_time']})")

if __name__ == "__main__":
    main()
