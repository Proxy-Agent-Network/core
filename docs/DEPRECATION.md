# Proxy Agent Network (PAN) | API Versioning & Deprecation Policy

**Philosophy:** Mission Stability First.
We understand that autonomous vehicle (AV) fleets run continuously and rely on the PAN protocol for critical physical recovery. We commit to a strict stability policy to ensure zero-downtime operations for our Fleet Partners and Vanguard Agents in the field.

---

## 1. Versioning Strategy
We use **Semantic Versioning (SemVer)** for our Agent SDKs and **URI Versioning** for the Fleet Gateway REST API.

* **Current Stable (Mesa Pilot):** `v2026.1` (e.g., `https://api.proxyagent.network/v2026.1/`)
* **Legacy (Deprecated):** `v1` (Pre-Pilot Prototype)

---

## 2. Breaking Changes (The "No-Break" Promise)
A **"Breaking Change"** is defined as:
* Removing an existing endpoint (e.g., `/fleet/dispatch`).
* Renaming a field in a JSON response (e.g., changing `l402_bounty` to `payment`).
* Adding a mandatory new request parameter that causes existing UDS webhooks to fail.

**Non-Breaking Changes (Allowed in Minor Updates):**
* Adding new optional parameters (e.g., `priority_surge`).
* Adding new endpoints (e.g., `/fleet/audit_logs`).
* Adding new enum values to `status` (e.g., `AGENT_EN_ROUTE` or `ORP_COMPLETE`).

---

## 3. Deprecation Lifecycle (Enterprise Standard)
If a major architectural shift requires us to decommission an API version, we adhere to a strict **18-Month Sunset** schedule to align with automotive software development cycles.

1.  **Announcement (Day 0):** Notification sent to all registered Fleet Operations Centers and integrated AV engineering teams. A `Deprecation` warning header is added to all API responses.
2.  **Sunset Mode (Month 12):** Scheduled "Brownout" tests (short, pre-announced 5-minute routing delays during lowest-traffic hours, 0200-0300 MST) are conducted to alert inactive integration teams.
3.  **End of Life (Month 18):** The version is officially decommissioned. The endpoint returns `410 Gone`.

---

## 4. LTS (Long Term Support)
The core physical infrastructure layers—specifically the **L402 Settlement Engine** (`/escrow/`) and the **SB 1417 Audit Engine** (`/compliance/log/`)—are considered **LTS components** and are guaranteed to remain backward compatible for a **minimum of 5 years**.

> [!TIP]
> Always verify the `X-API-Version` header in our responses to ensure your AV's onboard AI is negotiating with the latest stable release of the PAN Gateway.