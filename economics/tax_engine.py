import csv
import json
from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime

# PROXY PROTOCOL - TAX COMPLIANCE ENGINE (v1)
# "Death, Taxes, and Robots."
# ----------------------------------------------------

@dataclass
class Transaction:
    tx_id: str
    timestamp: str
    amount_sats: int
    fiat_value_usd: float
    counterparty_id: str
    jurisdiction: str # 'US', 'EU_DE', 'SG', etc.

class TaxEngine:
    def __init__(self):
        # Configuration based on 2026 Tax Law
        self.THRESHOLDS = {
            "US": {"type": "1099-NEC", "limit_usd": 600.00},
            "EU": {"type": "VAT", "rate": 0.20}, # Standard VAT fallback
            "SG": {"type": "GST", "rate": 0.09}
        }

    def calculate_liability(self, node_id: str, transactions: List[Transaction], year: int) -> Dict:
        """
        Aggregates earnings and determines reporting requirements.
        """
        total_earnings_sats = 0
        total_fiat_usd = 0.0
        reportable = False
        form_type = "NONE"
        
        # Filter for tax year
        year_txs = [t for t in transactions if t.timestamp.startswith(str(year))]
        
        if not year_txs:
            return {"node_id": node_id, "year": year, "reportable": False}

        # Determine Jurisdiction (Assume uniform for node, or take from first tx)
        region = year_txs[0].jurisdiction
        
        for tx in year_txs:
            total_earnings_sats += tx.amount_sats
            total_fiat_usd += tx.fiat_value_usd

        # Logic for US 1099-NEC
        if region == "US":
            if total_fiat_usd >= self.THRESHOLDS["US"]["limit_usd"]:
                reportable = True
                form_type = "1099-NEC"
        
        # Logic for VAT/GST (Simplified)
        elif region in ["EU_DE", "EU_FR"]:
            reportable = True # VAT usually tracked from dollar one for businesses
            form_type = f"VAT_REPORT_{region}"

        return {
            "node_id": node_id,
            "year": year,
            "jurisdiction": region,
            "total_sats": total_earnings_sats,
            "total_usd": round(total_fiat_usd, 2),
            "reportable": reportable,
            "required_form": form_type,
            "transaction_count": len(year_txs)
        }

    def generate_csv_export(self, report_data: Dict, transactions: List[Transaction]) -> str:
        """
        Generates a compliant CSV dump for accounting software (Quickbooks/Xero).
        """
        filename = f"TAX_REPORT_{report_data['node_id']}_{report_data['year']}.csv"
        
        # Mocking CSV generation in memory
        output = []
        output.append("DATE,TX_ID,AMOUNT_SATS,AMOUNT_USD,TYPE,NOTES")
        
        for tx in transactions:
            if tx.timestamp.startswith(str(report_data['year'])):
                line = f"{tx.timestamp},{tx.tx_id},{tx.amount_sats},{tx.fiat_value_usd},INCOME,Proxy Task"
                output.append(line)
        
        # Summary footer
        output.append(f",,,{report_data['total_usd']},TOTAL,")
        
        return "\n".join(output)

# --- CLI Simulation ---
if __name__ == "__main__":
    engine = TaxEngine()
    
    # Mock Data: A Node Operator in New York
    mock_txs = [
        Transaction("tx_101", "2025-02-15", 50000, 45.50, "agent_alpha", "US"),
        Transaction("tx_102", "2025-06-20", 150000, 135.00, "agent_beta", "US"),
        Transaction("tx_103", "2025-11-01", 600000, 540.00, "agent_gamma", "US"),
    ]
    
    print("[*] Generating Year-End Tax Report (2025)...")
    
    liability = engine.calculate_liability("node_nyc_882", mock_txs, 2025)
    
    print(f"Node: {liability['node_id']}")
    print(f"Region: {liability['jurisdiction']}")
    print(f"Total Earnings: ${liability['total_usd']}")
    
    if liability['reportable']:
        print(f"⚠️  STATUS: REPORTABLE ({liability['required_form']})")
        print("   -> Earnings exceed $600 threshold.")
        
        csv_data = engine.generate_csv_export(liability, mock_txs)
        print(f"\n[Preview CSV Output]\n{csv_data}")
    else:
        print("✅ STATUS: Non-Reportable (Below Threshold)")
