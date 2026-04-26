"""
Executive Reports API for the Vanguard 50 Command Center dashboard.

Migrated from Flask app.py routes (Stage 1d-3-b, 2026-04-25).

These endpoints power the reports.html dashboard at apps/web/command_center/reports.html.
The frontend calls each endpoint with a ?timeframe= query string and renders KPIs, tables,
and charts from the response. Response shapes are CONTRACT-BOUND with reports.html - any
shape change here requires a coordinated update on the frontend side.

All four endpoints currently return random/synthetic data. They are stubs in the sense
that no real data sources back them yet, but the response shapes are real and stable.
Future work: replace random data with queries against the production data warehouse.
The replacement should preserve the JSON contract so reports.html keeps working.
"""

import logging
import random
from datetime import datetime, timedelta

from fastapi import APIRouter, Query

logger = logging.getLogger("PAN_Reports")
router = APIRouter()

# Timeframe query parameter to days mapping. Used identically by all four endpoints.
TIMEFRAME_DAYS = {
    "24h": 1,
    "1w": 7,
    "1m": 30,
    "3m": 90,
    "1y": 365,
    "custom": 30,
}


def _resolve_days(timeframe: str) -> int:
    """Convert a timeframe string to a day count, defaulting to 30 days for unknown values."""
    return TIMEFRAME_DAYS.get(timeframe, 30)


@router.get("/reports/compliance")
async def get_compliance_report(timeframe: str = Query(default="1m")):
    """SB 1417 compliance dashboard: avg clearance time, disengagement count, breach rate, and audit trail."""
    days = _resolve_days(timeframe)

    now = datetime.utcnow()
    audit_trail = []
    total_seconds = 0
    disengagements = 0
    breaches = 0

    target_incidents = int(1.5 * days)
    if target_incidents < 5:
        target_incidents = 5

    incident_types = [
        ("manual_override", "Manual Drive Takeover"),
        ("scene_securement", "Scene Securement (Fire/Police)"),
        ("path_clearing", "Path Clearing (Debris)"),
        ("sensor_cleaning", "Sensor Obstruction"),
        ("spill_remediation", "Bio/Liquid Remediation"),
    ]

    for _ in range(target_incidents):
        fault_code, fault_name = random.choice(incident_types)
        if fault_code == "manual_override":
            disengagements += 1

        clearance_seconds = random.randint(240, 1020)
        total_seconds += clearance_seconds
        if clearance_seconds > 900:
            breaches += 1

        event_time = now - timedelta(
            days=random.randint(0, max(0, days - 1)),
            hours=random.randint(0, 23),
        )

        audit_trail.append({
            "timestamp": event_time.strftime("%Y-%m-%d %H:%M:%S"),
            "asset_id": f"AV-ACT-{random.randint(1000, 9999)}",
            "incident_type": fault_name,
            "clearance_time": f"{clearance_seconds // 60:02d}m {clearance_seconds % 60:02d}s",
            "agent": f"VAN-{str(random.randint(1, 15)).zfill(3)}",
            "compliant": clearance_seconds <= 900,
            "raw_time": event_time.timestamp(),
        })

    audit_trail.sort(key=lambda x: x["raw_time"], reverse=True)
    avg_seconds = total_seconds // target_incidents if target_incidents > 0 else 0

    return {
        "kpis": {
            "avg_clearance": f"{avg_seconds // 60}m {avg_seconds % 60:02d}s",
            "is_avg_compliant": avg_seconds < 900,
            "disengagements": disengagements,
            "breach_rate": f"{(breaches / target_incidents) * 100:.2f}%",
        },
        "audit_trail": audit_trail[:15],
    }


@router.get("/reports/operations")
async def get_operations_report(timeframe: str = Query(default="1m")):
    """Operations dashboard: uptime, MTTR, fault distribution by type, and geographic hotspots."""
    days = _resolve_days(timeframe)
    mult = max(1, days / 30)

    distribution = [
        {"type": "Sensor Cleaning", "count": int(random.randint(30, 50) * mult), "color": "#00BCD4"},
        {"type": "Path Clearing", "count": int(random.randint(20, 35) * mult), "color": "#FF9800"},
        {"type": "Cabin Sweep & Trash", "count": int(random.randint(15, 25) * mult), "color": "#4CAF50"},
        {"type": "Manual Drive Takeover", "count": int(random.randint(5, 14) * mult), "color": "#F44336"},
        {"type": "Tire Pressure", "count": int(random.randint(2, 8) * mult), "color": "#FFEB3B"},
    ]

    total_faults = sum(d["count"] for d in distribution)
    for d in distribution:
        d["pct"] = int((d["count"] / total_faults) * 100) if total_faults > 0 else 0
    distribution.sort(key=lambda x: x["count"], reverse=True)

    hotspots = [
        {"name": "Mill Ave (Tempe - High Foot Traffic)", "incidents": int(random.randint(18, 25) * mult)},
        {"name": "Old Town (Scottsdale - Congestion)", "incidents": int(random.randint(15, 20) * mult)},
        {"name": "Mesa Riverview (Construction)", "incidents": int(random.randint(10, 15) * mult)},
        {"name": "Downtown Chandler (Events)", "incidents": int(random.randint(5, 12) * mult)},
    ]

    return {
        "kpis": {
            "uptime": f"99.{random.randint(2, 8)}%",
            "mttr": f"{random.randint(9, 14)}m {random.randint(10, 59)}s",
            "total_faults": total_faults,
            "deadhead_reduction": f"{random.randint(12, 18)}%",
        },
        "distribution": distribution,
        "hotspots": hotspots,
    }


@router.get("/reports/financials")
async def get_financials_report(timeframe: str = Query(default="1m")):
    """Financials dashboard: escrow balance, total spend, average mission cost, cancel fees, and recent transactions."""
    days = _resolve_days(timeframe)

    now = datetime.utcnow()
    transactions = []
    starting_escrow = 25000.00
    if days > 90:
        starting_escrow = 150000.00

    total_spend = 0.0
    cancel_fees = 0.0
    total_incidents = 0
    fault_prices = [15.00, 25.00, 55.00, 85.00]

    target_incidents = int(1.5 * days)
    if target_incidents < 5:
        target_incidents = 5

    for _ in range(target_incidents):
        cost = random.choice(fault_prices)
        total_spend += cost
        total_incidents += 1

        if random.random() < 0.10:
            cancel_fees += 5.00
            total_spend -= 5.00

        event_time = now - timedelta(
            days=random.randint(0, max(0, days - 1)),
            hours=random.randint(0, 23),
        )

        transactions.append({
            "timestamp": event_time.strftime("%Y-%m-%d %H:%M:%S"),
            "ref_id": f"FLT-{random.randint(1000, 9999)}",
            "desc": "Escrow Settlement (Mission Cleared)",
            "amount": f"-${cost:.2f}",
            "is_negative": True,
            "raw_time": event_time.timestamp(),
        })

    transactions.sort(key=lambda x: x["raw_time"], reverse=True)
    current_balance = starting_escrow - total_spend + cancel_fees
    avg_cost = (total_spend / total_incidents) if total_incidents > 0 else 0.00

    return {
        "kpis": {
            "balance": f"${current_balance:,.2f}",
            "total_spend": f"${total_spend:,.2f}",
            "avg_cost": f"${avg_cost:.2f}",
            "cancel_fees": f"${cancel_fees:.2f}",
        },
        "transactions": transactions[:20],
    }


@router.get("/reports/vendor_sla")
async def get_vendor_sla_report(timeframe: str = Query(default="1m")):
    """Vendor SLA dashboard: avg response time, completion rate, global rating, top performing agents, and SLA infractions."""
    days = _resolve_days(timeframe)
    mult = max(1, days / 30)

    now = datetime.utcnow()

    top_agents = []
    for _ in range(5):
        missions = int(random.randint(15, 60) * mult)
        rating = round(random.uniform(4.8, 5.0), 2)
        resp_time = f"{random.randint(6, 11)}m {random.randint(10, 59)}s"

        top_agents.append({
            "agent_id": f"VAN-{str(random.randint(1, 40)).zfill(3)}",
            "rating": f"{rating} \u2b50",
            "missions": missions,
            "response": resp_time,
        })

    top_agents.sort(key=lambda x: x["missions"], reverse=True)

    infractions = []
    target_infractions = int(random.randint(2, 6) * mult)
    if target_infractions < 1:
        target_infractions = 1

    issues = [
        ("Mission Aborted (Flake)", "Agent Reassigned"),
        ("Late Arrival (>15m)", "Warning Issued"),
        ("Poor Resolution Quality", "Rating Deducted"),
    ]

    for _ in range(target_infractions):
        issue, action = random.choice(issues)
        event_time = now - timedelta(
            days=random.randint(0, max(0, days - 1)),
            hours=random.randint(0, 23),
        )

        infractions.append({
            "date": event_time.strftime("%Y-%m-%d"),
            "agent_id": f"VAN-{str(random.randint(41, 99)).zfill(3)}",
            "issue": issue,
            "action": action,
            "raw_time": event_time.timestamp(),
        })

    infractions.sort(key=lambda x: x["raw_time"], reverse=True)

    return {
        "kpis": {
            "avg_response": f"0{random.randint(7, 9)}m {random.randint(10, 59)}s",
            "completion_rate": f"98.{random.randint(1, 9)}%",
            "global_rating": f"4.{random.randint(85, 98)} / 5.0",
        },
        "top_agents": top_agents,
        "infractions": infractions[:8],
    }
