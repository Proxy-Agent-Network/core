# Proxy Agent Network (PAN) | TODO

Tracking deferred work that has been identified but scheduled for later. Items are grouped by area and rough priority. This is not an authoritative backlog (GitHub Issues remain the source of truth for bugs and features); it is a working notebook for decisions and known gaps that surfaced during code reviews, security sweeps, and documentation passes.

Items tagged **[PILOT BLOCKER]** must be resolved before the Vanguard 50 Mesa Pilot goes live. Search for that tag to triage launch-critical work.

Last updated: 2026-04-23.

---

## Documentation

### High priority

* **Docs Cleanup Pass 3 (Category 3 content updates).** Review list of 22 files flagged for minor updates to reflect the Mesa Pilot pivot and v2026.2 Wingman + KMP + KYC + JWT aud work. See `docs/CHANGELOG.md` for the v2026.2.0-beta release notes that anchor the narrative. Groupings proposed:
    * Wingman integration updates to `docs/hardware/ATTESTATION.md`, `docs/hardware/UWB_HOMING.md`, `docs/hardware/TELEMETRY.md`, `docs/hardware/VANGUARD_MANUAL.md`
    * KMP migration updates to `docs/CONTRIBUTING.md`, `docs/CONTRIBUTING_ZH.md`, `docs/DEVELOPER.md`, `docs/README.md`, `docs/README_zh.md`
    * JWT aud claim + 409 Conflict updates to `docs/sdk/AUTH.md`, `docs/API_SPEC.md`
    * Brand, deprecation, and webhook refresh for `docs/brand/ASSETS.md`, `docs/sdk/DEPRECATION.md`, `docs/sdk/WEBHOOK_SECURITY.md`, root `docs/DEPRECATION.md`
    * Remaining Cat 3C minor-review files: `docs/architecture/specs/hardware/NODE_RECOVERY.md`, `REFERENCE_DESIGN.md`, `SECURITY_ARCHITECTURE.md`, `docs/economics/ESCROW_MECHANICS.md`, `docs/economics/REWARD_TYPES.md`, `docs/hardware/SETUP_GUIDE.md`

* **Docs Cleanup Pass 4 (Category 4 new files).** Create 8 new documents. The source HTML specs are already in hand for most of the hardware ones.
    * `docs/hardware/WINGMAN_SPEC.md` (source: PAND1_PAN_Wingman_Spec_v1_1.html)
    * `docs/hardware/HAPHAT_SPEC.md` (source: VFH1_Project_Copperfield_HapHat_v2_3.html)
    * `docs/hardware/VEST_SPEC.md` (source: VFV1_Vanguard_Field_Vest_Spec_v1_2.html)
    * `docs/hardware/POLO_SPEC.md` (source: VFP1_Aegis_Polo_Spec_v1_2.html)
    * `docs/hardware/GAUNTLETS_SPEC.md` (source: VFG1_Vanguard_Gauntlets_Spec_v1_3.html)
    * `docs/operations/DECOMPRESSION_SYSTEM.md` (source: VDS_Future_Plan_Vanguard_Decompression_System.html)
    * `docs/security/DEVICE_TRANSFER_KYC.md` (automated biometric KYC flow; 409 Conflict trap and hardware key obliteration)
    * `docs/architecture/KMP_MIGRATION.md` (PanApiClient to PanWalletClient transition)

* **Update SUMMARY.md when Cat 4 files land.** Each Cat 4 commit should append the new entry to the SUMMARY index so navigation stays current.

### Medium priority

* **Markdown case-sensitivity audit.** SUMMARY.md was fixed to use uppercase filenames matching on-disk reality, but other docs in the repo likely contain the same lowercase-link pattern. This is a repo-wide convention issue: filenames are uppercase but internal links often use lowercase. Works on Windows (case-insensitive filesystem) but breaks on Linux, macOS with HFS+ case-sensitive, and GitHub Pages rendering. Needs a full sweep and probably a .gitattributes or lint rule to prevent regressions.

* **Fix remaining Google-search-wrapped links.** Two known cases that survived Pass 1:
    * `docs/integration/WEBHOOKS.md:45` - bad link to WEBHOOK_SECURITY.md
    * `docs/sdk/UDS_WEBHOOKS.md:93` - bad link to auth.md (also wrong casing)
    These will be resolved as part of their Cat 3 updates.

### Low priority

* **V2X Integration Docs Consolidation.** `docs/sdk/` and `docs/integration/` folders contain near-duplicate content targeting the same audience ("Fleet API (V2X) Integrations"). Five file pairs overlap:
    * `sdk/ERRORS.md` / `integration/ERROR_CODES.md`
    * `sdk/QUOTAS.md` / `integration/QUOTA_GUIDE.md`
    * `sdk/UDS_WEBHOOKS.md` / `integration/WEBHOOKS.md`
    * `sdk/WEBHOOK_SECURITY.md` / `integration/WEBHOOK_SECURITY.md`
    * Plus root `docs/DEPRECATION.md` vs `docs/sdk/DEPRECATION.md`
    SUMMARY.md currently blesses `sdk/` as canonical. Consolidation needs: pair-by-pair review, merge best content into sdk/ version, delete integration/ duplicates, decide if integration/ folder survives at all.

* **Root DEPRECATION.md vs sdk/DEPRECATION.md.** Decide whether to keep as separate docs (high-level platform philosophy vs detailed V2X integrator policy) or consolidate. SUMMARY currently labels them distinctly.

---

## Backend / Gateway

### High priority

* **[PILOT BLOCKER] Secure `/dev/override-hardware` endpoint.** The hardware lockout override added in commit `a27c7c4` hardcodes deletion of `pan:agent:DEV_AGENT_01:pubkey`. Two fixes required before production: (1) dynamically scope the deletion to the authenticated agent's JWT subject, and (2) rigorously wrap the entire endpoint in an `if os.getenv("ENVIRONMENT") != "production"` block. Current state allows a malicious actor who discovers the endpoint path to wipe the hardware lock of the hardcoded DEV_AGENT_01 identity with no authentication.

* **[PILOT BLOCKER] Complete Checkr API wiring in `onboarding_api.py`.** Background checks are a strict requirement per `docs/legal/COMPLIANCE.md`. The onboarding flow needs `CHECKR_API_KEY` fully wired through candidate creation, invitation, and webhook verification paths so agents cannot complete the Key Ceremony without a cleared background check. Env vars `CHECKR_TEST_SECRET_KEY` and `CHECKR_WEBHOOK_SECRET` already defined in `.env.example`.

* **Authenticate `/api/v1/telemetry/history`.** Currently unauthenticated. Anyone with network access can dump the full forensic GPS ledger via `?global=true`. Needs admin auth or OPS_HUB_TOKEN check. Pre-existing, flagged in security sweep.

* **Fix config-loader warning typos in `apps/backend/src/utils/webhook_auth.py`.**
    * "reejected" (two e's) appears on the WHSEC_DHL and WHSEC_UPS warning paths
    * "webhookss" appears on both PUBKEY_* warning paths
    * "be  rejected" (double space) on the WHSEC_FEDEX path
    * Also: PUBKEY warnings incorrectly say "webhooks will be rejected" when PUBKEY_* is actually for V2X Ed25519 distress-signal auth, not webhooks. Needs its own warning template.

### Medium priority

* **Worker mock endpoints.** `/api/v1/node/register`, `/api/v1/task/request`, `/api/v1/task/submit` in `apps/backend/entrypoints/app.py` now 403 in production, but they use a server-side shared-secret HMAC rather than per-agent pubkey verification. If these endpoints are genuinely dead, delete them. If they have a future purpose, replace with proper agent-pubkey auth.

* **Decide the fate of the Flask `/api/v1/node/register` workflow.** Same file as above. The mock_register endpoint uses `HARDWARE_ATTESTATION_SEED` as an HMAC key which is structurally weaker than the TPM-signed per-agent JWT path used everywhere else in the gateway. Pre-pilot question: is anything still calling this?

* **Consolidate `decode_redis_hash` helper.** Same function is duplicated across at least `apps/backend/src/api/v2x_bounty_api.py`, `apps/backend/src/api/agent_api.py`, and probably other modules. Extract to `apps/backend/src/utils/redis_helpers.py` or similar.

* **Partner multi-tenant migration.** Current `PARTNER_API_KEY` is a single-tenant bearer token used by the Flask `/api/v1/dispatch/request` endpoint. Future partners should either get `PARTNER_API_KEY_WAYMO` / `PARTNER_API_KEY_ZOOX` style namespacing, or (preferred) migrate to the V2X Ed25519 signature path.

### Low priority

* **Hardware attestation substring check.** `apps/backend/entrypoints/app.py` line 50 does `HW_SECURED = "0x8F9B" in MY_NODE_ID`, which is a magic-string prefix check rather than a cryptographic verification. TODO comment exists in the file for the Rust team to migrate to a signed-payload attestation.

* **Migrate `@app.on_event("startup")` to lifespan context managers.** FastAPI deprecation notice in `apps/backend/src/main.py`. Still functional but slated for a future architectural pass.

* **Remove now-orphaned `load_optional_router` helper.** After Pass 1's hard-import promotion in `main.py`, nothing calls `load_optional_router` anymore. Harmless dead code.

---

## Compliance / Storage

### High priority

* **[PILOT BLOCKER] Migrate SB 1417 evidence uploads from imgbb to S3/GCP.** The tactical camera currently uploads redacted 720p/3fps evidence frames to imgbb. Acceptable for sandbox, not acceptable for the Vanguard 50 pilot. Evidence must route to WORM-compliant AWS S3 or GCP Cloud Storage before fleet-partner onboarding. This is a statutory Arizona SB 1417 retention requirement and a condition of the $5M tech E&O liability shield. Target bucket configuration already sketched via `S3_EVIDENCE_BUCKET_NAME` env var in `.env.example`.

---

## Hardware / Bluetooth

### High priority

* **[PILOT BLOCKER] Implement `AndroidBleHapHatService`.** `AgentDashboardScreen.kt` currently calls `rememberBleHapHatService()` which returns a mock hardware service. Need the real Android BLE implementation to command the ESP32-C3 motors and NeoPixels on the HapHat module. Without this, agents in the field cannot receive haptic or visual mission alerts through the HapHat hardware. See `docs/hardware/HAPHAT_SPEC.md` (Pass 4 Cat 4 item) for the target BLE UUIDs and command protocol.

---

## Security & Verification Items (from original sweep, not yet reverified)

These items were flagged during an earlier security review and marked `[NEEDS VERIFICATION]` against the current codebase. Each deserves a targeted review to confirm whether the issue still exists or was already resolved by intervening commits.

* `apps/backend/src/ops/compliance_auditor.py` - possible hardcoded secrets
* `apps/backend/src/ops/compliance_export_api.py`
* `apps/backend/src/ops/forensic_data_exporter.py`
* `apps/backend/src/ops/logistics_webhook_api.py`
* `apps/backend/src/reputation/verification_webhook.py` - fallback WEBHOOK_SECRET
* `apps/backend/src/api/hub_discovery_api.py` - X-Forwarded-For trust
* `apps/backend/src/ops/anomaly_detection.py` - possible race conditions
* `apps/backend/src/reputation/snapshot_utility.py` - silent error swallowing
* `apps/backend/src/reputation/slashing_engine.py` - WiFi heuristic needs review
* `apps/backend/src/ops/proof_archive_api.py` - possible path traversal
* `apps/backend/src/middleware/traffic_shaper.py` - hardcoded actor context
* `apps/backend/src/core/langchain_client.py` - prompt injection concern

Note: several files above are in modules (`ops/`, `reputation/`) that may have been partially deprecated during the Phase 5+ cleanup. First step on each is "does this file still exist and is it reachable from active routes?"

* **compliance/audit_engine.py** - load-bearing for SB 1417. Not yet reviewed in detail. Priority review before fleet-partner-facing beta.

* **Dispatch endpoint auth strength.** `/api/v1/dispatch/request` now uses PARTNER_API_KEY + secrets.compare_digest, which is good. But bearer tokens can still leak via logs, screenshots, Slack pastes, etc. For Waymo/Zoox-level partners, prefer the V2X Ed25519 signature path.

---

## Developer Tooling

* **Expand commit-msg hook scopes.** Current hook at `.git/hooks/commit-msg` allows five scopes: `core | gateway | ops-hub | app | ui`. Historical commits have used at least: `patrol`, `sync`, `telemetry`, `navigation`, `dispatch`, `ledger`, `hardware`, `security`, `docs`, `build`. Proposed additions (architectural, not feature-scoped):
    * `docs` - documentation-only changes
    * `hardware` - BLE, UWB, TPM, sensor integration
    * `security` - authentication, attestation, key ceremony, auth middleware
    Avoid adding narrow feature scopes (`patrol`, `sync`, `dispatch`) - those belong in the subject line.

* **Set PYTHONUTF8=1 globally.** Windows Git Bash defaults to cp1252 which mangles the emojis in source and docs. Setting this in the user profile avoids intermittent "invalid byte 0x8f" errors when Python opens files without explicit encoding.

* **Second venv at `apps/backend/venv/`.** A stray venv exists alongside the root `.venv/`. Contains `google.genai` and `langsmith` packages from the deprecated chatbot subsystem. Likely leftover and deletable, but verify nothing (IDE config, script) is pointing at it first.

* **Pin `python-multipart` floor in requirements.txt.** Done in 14e967e (added `>=0.0.16`). Leaving this note in case a future dependency resolver needs a pin adjustment.

* **`.gitattributes` for line endings.** Currently no rules. Every file edit on Windows produces `warning: LF will be replaced by CRLF` messages. Not harmful but noisy. Consider `*.md text eol=lf` or similar to lock a convention.

---

## Mobile / UI

### High priority

* **Resolve `@file:Suppress` hacks in network clients.** Both `PanWalletClient.kt` and `PanApiClient.kt` currently suppress `INVISIBLE_REFERENCE` and `INVISIBLE_MEMBER` warnings as a workaround for a Gradle `visibility(PUBLIC)` compilation issue. Fix the underlying visibility config, then remove the suppressions. Risk of future breakage: Kotlin/KMP version bumps may promote these warnings to hard errors, which would turn a cosmetic workaround into a build failure.

### Medium priority

* **iOS feature parity with Android.** Tracking release of `-beta` tag on `2026.2.0-beta` until iOS catches up to the Android app. No concrete feature list yet; start from comparing iOS shared/common module coverage vs Android expected from the KMP migration.

* **Fleet dashboard beta-test cycle.** Same gating as iOS parity.

### Low priority

* **Dynamic GPS injection for Dev Menu.** The `LOC 1`, `LOC 2`, `LOC 3` buttons in `AgentDashboardScreen.kt` hardcode Mesa, AZ intersections. When we expand beyond Mesa, these need to dynamically pull coordinates from the active Sector's Geohash polygon. Purely a dev-UX item; doesn't affect production routing.

---

## Notes on this file

* Add new items as they surface. Move items to GitHub Issues when they are ready to be planned into a sprint.
* Remove items when they ship. Link to the closing commit or PR in the removal commit message.
* This file is not a substitute for the CHANGELOG. The CHANGELOG records what shipped; this file tracks what we are putting off.
* Search for **[PILOT BLOCKER]** to surface Mesa Pilot launch-critical items across all sections.
