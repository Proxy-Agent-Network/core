# **Proxy Agent Network (PAN) | API Versioning & Deprecation Policy**

**Status:** Active (Mesa Pilot)

**Version:** 2026.1.0

**Target:** Fleet API (V2X) Integrations

## **1\. The Cyber-Physical Lifecycle**

In traditional SaaS, an unannounced breaking API change results in a broken dashboard. In the Proxy Agent Network (PAN), a breaking API change could result in an Autonomous Vehicle (AV) being permanently stranded in an intersection, unable to dispatch a Vanguard Agent to clear its sensor array.

Because of these extreme physical world stakes, PAN adheres to a strict, enterprise-grade versioning and deprecation schedule. We guarantee a minimum **12-month support window** for any active API version.

## **2\. API Versioning Scheme**

PAN utilizes date-based versioning, embedded directly into the endpoint URI.

* **Format:** /vYYYY.X/  
* **Example:** https://api.proxyagent.network/v2026.1/fleet/dispatch

When backwards-incompatible (breaking) changes are introduced, PAN will release a new API version (e.g., v2027.1). Your Fleet integrations will remain on your pinned version until you explicitly update your endpoint URLs.

## **3\. Breaking vs. Non-Breaking Changes**

Your Fleet engineering team should build integrations robust enough to handle non-breaking changes without failing.

### **Non-Breaking Changes (No new version required)**

* Adding new API endpoints.  
* Adding new optional parameters to existing requests.  
* Adding new properties to JSON response bodies.  
* Adding new uds\_fault\_code types to the supported enum list.  
* Adding new event types to the Outbound Webhook callbacks.

### **Breaking Changes (Requires new API version)**

* Removing or renaming an API endpoint.  
* Removing or renaming a required parameter or response field.  
* Changing the data type of an existing field.  
* Changes to the HMAC-SHA256 authentication signature requirements.  
* Removing a previously supported uds\_fault\_code from the physical service roster.

## **4\. The Deprecation Timeline (12 Months)**

When a new API version is released, the previous version enters its **Deprecation Lifecycle**.

1. **Announcement (Month 0):** The new version is published. Fleet Partners are notified via the dedicated Signal Command channel and developer mailing list.  
2. **Active Support (Months 0 \- 6):** The deprecated version remains fully functional and receives critical security patches. No new features are backported.  
3. **Maintenance Mode (Months 6 \- 11):** The deprecated version remains functional but is considered legacy. SLAs on dispatch times may be prioritized for fleets on the current API version during network surges.  
4. **Traffic Shaping & Brownouts (Month 11 \- 12):** See *Brownout Protocol* below.  
5. **Final Sunset (Month 12):** The endpoint is permanently disabled and returns a 410 Gone status code.

## **5\. The Brownout Protocol**

To ensure Fleet Partners do not miss the sunset deadline, PAN executes scheduled "Brownouts" during the final 30 days of a deprecated API's life.

During a Brownout, requests to the deprecated API will intentionally fail with a 410 Gone status for short, pre-scheduled windows (e.g., a 2-hour window on a Tuesday at 2:00 AM UTC).

* **Purpose:** Brownouts force hidden or forgotten AV retry loops to fail in a controlled manner, triggering your internal engineering alerts before the permanent sunset.  
* **Schedule:** The Brownout schedule is published 60 days prior to the final sunset.  
* **Exemptions:** Brownouts are instantly suspended if a Level 3+ severe weather event (e.g., Haboob/Dust Storm) is declared in the active Sector Geohash.

## **6\. L402 Smart Contract Upgrades**

While REST API versioning follows the 12-month cycle, updates to the underlying L402 Lightning Network settlement contracts (HTLCs) are entirely backwards-compatible at the protocol layer. Upgrades to our LND nodes or channel routing topology will not require you to update your Fleet API version.