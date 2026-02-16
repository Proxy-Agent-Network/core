import asyncio
import logging
import json
import requests
import time
from typing import List, Dict, Optional
from datetime import datetime

# Proxy Protocol Internal Modules
from core.ops.alert_gateway import AlertGateway

# PROXY PROTOCOL - SECURITY ALERT SYSTEM (v1.0)
# "Bridging the gap between detection and intervention."
# ----------------------------------------------------

class SecurityAlertSystem:
    """
    Background daemon that monitors the Security Incident API.
    Orchestrates multi-channel escalation for high-severity threats.
    """
    def __init__(self, incident_api_url: str = "http://localhost:8020/v1/security/incidents"):
        self.incident_api = incident_api_url
        self.gateway = AlertGateway()
        self.is_running = True
        
        # Track processed incident IDs to avoid duplicate alerts
        self.processed_incidents: set = set()
        
        # Threshold for 'Alert Fatigue' prevention
        self.POLL_INTERVAL_SEC = 30
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("AlertSystem")

    async def fetch_recent_incidents(self) -> List[Dict]:
        """Queries the Incident API for the latest security events."""
        try:
            # In production, uses aiohttp for async requests
            response = requests.get(self.incident_api, timeout=10)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            self.logger.error(f"[!] API Connection Error: {str(e)}")
        return []

    async def analyze_and_escalate(self, incident: Dict):
        """
        Adjudicates whether an incident requires immediate PGP/Signal escalation.
        """
        incident_id = incident.get('incident_id')
        severity = incident.get('severity', 'LOW')
        incident_type = incident.get('type')

        if incident_id in self.processed_incidents:
            return

        # Escalation Logic
        # SEV-1: Immediate PGP + Signal
        # SEV-2: PGP Only
        # SEV-3: Log Only
        
        if severity == "CRITICAL":
            self.logger.critical(f"🚨 ESCALATING SEV-1: {incident_id} ({incident_type})")
            await self.gateway.send_sev1_alert(
                reason=f"PHYSICAL_BREACH_{incident_type}",
                metrics={
                    "incident_id": incident_id,
                    "unit_id": incident.get('unit_id'),
                    "coordinates": incident.get('coordinates'),
                    "timestamp": incident.get('timestamp')
                }
            )
        elif severity == "ELEVATED":
            self.logger.warning(f"[*] Escalating SEV-2: {incident_id} (Internal Audit Required)")
            # In prod: self.gateway.send_email_report(...)
        
        self.processed_incidents.add(incident_id)

    async def monitor_loop(self):
        """Primary watchdog loop."""
        self.logger.info("[*] Security Alert System Active. Monitoring Incident Stream...")
        
        while self.is_running:
            try:
                incidents = await self.fetch_recent_incidents()
                
                for incident in incidents:
                    await self.analyze_and_escalate(incident)
                    
                # Clean up cache periodically (keep last 1000 IDs)
                if len(self.processed_incidents) > 1000:
                    self.processed_incidents.clear()
                    
            except Exception as e:
                self.logger.error(f"[ERROR] Watchdog Cycle Interrupted: {str(e)}")
            
            await asyncio.sleep(self.POLL_INTERVAL_SEC)

if __name__ == "__main__":
    system = SecurityAlertSystem()
    loop = asyncio.get_event_loop()
    
    print("--- PROXY PROTOCOL SECURITY ALERT DAEMON ---")
    try:
        loop.run_until_complete(system.monitor_loop())
    except KeyboardInterrupt:
        print("\n[*] Graceful shutdown initiated.")
        system.is_running = False
