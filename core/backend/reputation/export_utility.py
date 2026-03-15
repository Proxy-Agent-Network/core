import csv
import json
import hashlib
import time
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

# Proxy Protocol Internal Modules
from core.reputation.oracle import ReputationOracle, ReputationAttestation

# PROXY PROTOCOL - REPUTATION EXPORT UTILITY (v1.0)
# "Proof of standing for the machine-to-human economy."
# ----------------------------------------------------

@dataclass
class ExportManifest:
    node_id: str
    export_timestamp: str
    report_hash: str
    oracle_signature: Optional[str] = None
    protocol_version: str = "v2.5.6"

class ReputationExporter:
    """
    Generates cryptographically-signed performance reports for Node Operators.
    Used for external credit verification and insurance auditing.
    """
    def __init__(self, oracle: ReputationOracle):
        self.oracle = oracle

    def generate_json_export(self, node_id: str, events: List[Dict]) -> str:
        """
        Creates a JSON payload of reputation history and binds it with a signature.
        """
        # 1. Fetch current standing from Oracle
        # Simulation: Normally this pulls from the global state
        current_score = 982 # Elite score for NODE_ELITE_X29
        
        # 2. Construct Data Body
        payload = {
            "node_identity": node_id,
            "generated_at": datetime.now().isoformat(),
            "current_score": current_score,
            "event_history": events
        }
        
        # 3. Cryptographic Binding
        # We hash the data and request a signature from the Oracle identity
        data_string = json.dumps(payload, sort_keys=True)
        report_hash = hashlib.sha256(data_string.encode()).hexdigest()
        
        # In production, this call utilizes the Oracle's TPM-bound key
        manifest = ExportManifest(
            node_id=node_id,
            export_timestamp=payload['generated_at'],
            report_hash=report_hash,
            oracle_signature=self.oracle._sign_with_identity(report_hash)
        )
        
        # 4. Final Package
        export_package = {
            "manifest": asdict(manifest),
            "data": payload
        }
        
        return json.dumps(export_package, indent=2)

    def generate_csv_export(self, node_id: str, events: List[Dict], output_file: str):
        """
        Generates a flat CSV file for use in spreadsheet/accounting software.
        """
        print(f"[*] Generating CSV Reputation Export for {node_id}...")
        
        with open(output_file, 'w', newline='') as csvfile:
            fieldnames = ['timestamp', 'event_type', 'delta', 'new_score', 'reference_id']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for event in events:
                writer.writerow({
                    'timestamp': event.get('timestamp'),
                    'event_type': event.get('type'),
                    'delta': event.get('delta'),
                    'new_score': event.get('score'),
                    'reference_id': event.get('ref_id')
                })
        
        print(f"✅ Export complete: {output_file}")

# --- CLI Integration ---
if __name__ == "__main__":
    from core.reputation.oracle import ReputationOracle
    
    oracle_engine = ReputationOracle()
    exporter = ReputationExporter(oracle_engine)

    # Mock Data: History for NODE_ELITE_X29
    history = [
        {"timestamp": "2026-02-11T12:00:00Z", "type": "TASK_SUCCESS", "delta": 2, "score": 982, "ref_id": "T-9901"},
        {"timestamp": "2026-02-10T09:15:00Z", "type": "JURY_CONSENSUS", "delta": 5, "score": 980, "ref_id": "CASE-992"},
        {"timestamp": "2026-02-04T00:00:00Z", "type": "DECAY", "delta": -1, "score": 975, "ref_id": "CRON-01"}
    ]

    # 1. JSON Export (Signed)
    signed_json = exporter.generate_json_export("NODE_ELITE_X29", history)
    print("\n--- SIGNED JSON EXPORT PREVIEW ---")
    print(signed_json[:500] + "...")

    # 2. CSV Export
    exporter.generate_csv_export("NODE_ELITE_X29", history, "reputation_export.csv")
