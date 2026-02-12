# API Versioning & Deprecation Policy

**Philosophy:** Stability First.  
We understand that autonomous agents run continuously. We commit to minimizing breaking changes to ensure zero-downtime operations for the Proxy ecosystem.

---

## 1. Versioning Strategy
We use **Semantic Versioning (SemVer)** for SDKs and **URI Versioning** for the REST API.

* **Current Stable:** `v1` (e.g., `https://api.proxyprotocol.com/v1/`)
* **Beta:** `v2-beta` (Sandbox Only)

---

## 2. Breaking Changes
A **"Breaking Change"** is defined as:
* Removing an existing endpoint.
* Renaming a field in a JSON response.
* Adding a mandatory new request parameter.

**Non-Breaking Changes (Allowed):**
* Adding new optional parameters.
* Adding new endpoints.
* Adding new enum values to `status` or `task_type`.

---

## 3. Deprecation Lifecycle
If we must decommission a version, we adhere to a **12-Month Sunset** schedule.

1.  **Announcement (Day 0):** Notification sent to all registered Agent emails. A `Deprecation` warning header is added to all API responses.
2.  **Sunset Mode (Month 9):** "Brownout" tests (short intentional outages) are conducted to alert inactive developers.
3.  **End of Life (Month 12):** The version is officially decommissioned. The endpoint returns `410 Gone`.

---

## 4. LTS (Long Term Support)
The core settlement layer (`/escrow`) is considered an **LTS component** and is guaranteed to remain backward compatible for a **minimum of 3 years**.

> [!TIP]
> Always check the `X-API-Version` header in our responses to ensure your agent is running on the latest stable release.
