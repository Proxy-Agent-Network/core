# Proxy Agent Network (PAN) | TODO

Tracking deferred work that has been identified but scheduled for later. Items are grouped by area and rough priority. This is not an authoritative backlog (GitHub Issues remain the source of truth for bugs and features); it is a working notebook for decisions and known gaps that surfaced during code reviews, security sweeps, and documentation passes.

Items tagged **[PILOT BLOCKER]** must be resolved before the Vanguard 50 Mesa Pilot goes live. There are currently 7 pilot blockers across Backend, Compliance, Hardware, Architecture, and Mobile sections. Search for that tag to triage launch-critical work.

Last updated: 2026-04-24.

---

## Architectural Context (read this first)

The repository is currently mid-pivot from the original "Proxy AI" cognitive-vault Flask monolith to the "Proxy Agent Network" FastAPI V2X gateway for the Mesa autonomous-vehicle-recovery pilot.

**The canonical future stack:**
* **Backend:** FastAPI, entrypoint at `apps/backend/src/main.py`. This is what gets hardened, audited, and shipped to Mesa.
* **Mobile:** `apps/mobile/pan_tactical/composeApp/` (Kotlin Multiplatform, Android first, iOS parity pending).
* **Ops Hub:** `apps/web/internal_dashboards/` (React + Vite).
* **Docs:** `docs/` (the tree at the repo root, not `core/docs/`).

**What is legacy and scheduled for removal:**
* `core/` — 75 tracked files remaining (down from 444 at start of migration). The v2 "AI civilization" backend code has been fully purged. Remaining content is mostly pre-pivot infrastructure (Dockerfile, docker-compose.yml, requirements.txt, Cargo.toml), pre-pivot Python entrypoints (master_node.py, mcp_server.py, dashboard.py, agent_engine_v2.py, autonomous_worker.py), and legacy subdirectories that may overlap with canonical locations elsewhere in the repo. See the Repo Hygiene / Architecture section for the residual cleanup plan.
* `apps/backend/entrypoints/app.py` — the Flask monolith. Currently broken: imports from `core.db` and `core.lightning_engine` which no longer exist after the Stage 1c purge. Scheduled for retirement in Stage 1d.
* Root `Dockerfile` and `docker-compose.yml` — both build the pre-pivot Flask + cognitive vault + LND + bitcoind stack. The `proxy_agent` container they produce no longer boots after Stage 1c. Need to be rewritten or deleted (Stage 1d or later).

Understanding this context is important because several items in this file reference files or symptoms that only make sense if you know the pivot is in progress.

---

## Repo Hygiene / Architecture

### Completed migration stages (history)

The pre-pivot-to-monorepo migration has been substantially executed across two days of cleanup work. Stages completed and the commits that landed them:

* **Stage 0a** (`b503b04`): Purged core/docs/ and core/legacy/ (86 files).
* **Stage 0c** (`4a9c087`): Purged core/pan_tactical/ duplicate KMP project (85 files).
* **Stage 0d** (`c06877d`): Purged core/static/, core/templates/, core/streamlit_core/, core/cognitive_vault/, core/node_legacy/ (105 files).
* **Stage 1a** (`d133f3e`): Removed five orphan importer files in apps/backend/src/ (reputation_api, master_orchestrator, security_alert_system, export_utility, migration_engine) and patched run_workers.py to fix the broken core.economics.surge_pricing_engine import path.
* **Stage 1c** (`21db5df`): Wholesale deletion of core/backend/ (93 files). Eliminated the v2 "AI civilization" backend (Jury Tribunal, Immigration Office, sovereign identity, etc.) from the repo entirely.

Cumulative deletion across Stages 0-1: 374 files, ~36,000 lines. apps/backend/src/ now has zero `from core.*` imports.

### Stage 1d — retire the Flask monolith (priority: medium)

`apps/backend/entrypoints/app.py` is the dying Flask monolith. After Stage 1c, its `from core.db import get_db_conn` and `from core.lightning_engine` imports point at deleted files. The Flask app no longer boots, and the `proxy_agent` container in the root `docker-compose.yml` no longer starts.

This is acceptable broken state because:
* The Mesa Pilot ships on the FastAPI gateway at `apps/backend/src/main.py`, not the Flask monolith
* No production workflow depends on the Flask app currently running
* Local dev work has moved to direct `uvicorn apps.backend.src.main:app` invocation

To formally retire Flask:
* Decide between deleting `apps/backend/entrypoints/app.py` outright, or migrating any still-useful endpoints (mock worker endpoints, dispatch stub, agent registration mocks) into the FastAPI gateway as proper routers under `apps/backend/src/api/` first.
* Delete `apps/backend/entrypoints/master_node.py` if it has no remaining purpose.
* Remove the `proxy_agent` service from the root `docker-compose.yml`. Decide what (if anything) replaces it. Probably a lightweight compose file with just postgres and redis is sufficient for local dev.
* Delete or rewrite the root `Dockerfile` (currently builds the pre-pivot Flask + cognitive_vault + LND + bitcoind stack via `COPY proxy-core /build/proxy-core` and friends).
* Delete the now-dead `load_optional_router` helper in `apps/backend/src/main.py` (defined at line 86, never invoked).
* Update TODO.md to reflect what landed.

### Stage 2 — investigate and clean the residual core/ contents (priority: low)

After Stages 0 and 1, `core/` still has 75 tracked files across these residuals:

* **Root files** (~25): Dockerfile, docker-compose.yml, requirements.txt, Cargo.toml, Cargo.lock, README.md, LICENSE, CITATION.cff, .dockerignore, .flake8, .gitignore, .gitmessage, start_node.sh, favicon.ico, sample.mp3, sample.mp4, master_node.py, autonomous_worker.py, dashboard.py, agent_engine_v2.py, mcp_server.py.
* **core/hardware-node/** (7 files): Exact duplicate of `hardware/python-node/` at the repo root. Each file matches a sibling in the canonical location. Likely deletable wholesale.
* **core/proxy-core/** (6 files): Pre-monorepo Rust TPM bindings. The canonical location per the root Dockerfile is `proxy-core/` at the repo root. The `hardware/proxy-core/` and `core/proxy-core/` copies are duplicates.
* **core/infrastructure/** (12 files): Unknown content. Probably scripts and config, possibly some still-useful operational tooling.
* **core/examples/** (9 files): Example code, probably mundane.
* **core/proxy-core/**, **core/sdk/** (3), **core/tools/** (2), **core/pan_command_center/** (4): Various subdirectories with small file counts.
* **Single-file subdirectories** (7 dirs × 1 file each): core/core/, core/economics/, core/integrations/, core/pan_gateway/, core/protocols/, core/src/, core/utils/.

None of these contain v2 civilization code (governance, jury, immigration, sovereign identity). The investor-optics concern is resolved. Stage 2 is cleanup-for-tidiness, not cleanup-for-safety. Lower priority than the pilot-blocker work.

### Stage 2 sub-items (work back-burner)

* **Verify core/hardware-node/ is fully duplicated by hardware/python-node/.** If yes, single-commit deletion.
* **Resolve the three proxy-core/ duplicates.** Confirm the repo-root `proxy-core/` is canonical (per root Dockerfile line 24 `COPY proxy-core /build/proxy-core`). Delete `core/proxy-core/` and `hardware/proxy-core/`.
* **Audit core/infrastructure/.** Read the 12 files, classify each as live/legacy/obsolete.
* **Audit the loose pre-pivot Python files at core/ root** (master_node.py, autonomous_worker.py, dashboard.py, agent_engine_v2.py, mcp_server.py). Most likely all dead, but some might have informational value worth preserving in a separate archive branch.
* **Decide the fate of the loose top-level non-Python files.** sample.mp3 and sample.mp4 are obvious deletes. Cargo.toml/Cargo.lock at core/ root are probably superseded by hardware/proxy-core/Cargo.toml.

### Stage 3 — Downstream cleanup (priority: low)

* **`apps/web/internal_dashboards/src/protocol_data_purge_dashboard.jsx`** contains a hardcoded string referencing `core/ops/proof_archive_api.py` (a file that no longer exists after Stage 1c). Update the string or delete the dashboard.
* **`.gitmessage`** at the repo root contains a URL reference to `https://github.com/Proxy-Agent-Network/core/docs/` (a path that no longer exists after Stage 0a). Update to the actual docs location.

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

## Architecture / Economics

### High priority

* **[PILOT BLOCKER] Reconcile fee math across code, backend, and docs.** Three sources of truth currently disagree:
    * **Kotlin UI code** (`MissionAlertOverlay.kt`, `AgentDashboardScreen.kt`): calculates agent-side network fee as 15% (Veteran) or 25% (Standard)
    * **Backend** (`apps/backend/src/api/v2x_bounty_api.py::complete_mission`): uses `multiplier = 0.85 if is_veteran else 0.75`, matching the UI
    * **Docs** (`docs/API_SPEC.md`, `docs/legal/COMPLIANCE.md`): state a flat 10% PAN network fee with no veteran tier
    
    **Canonical economic model (source of truth going forward):**
    * Agent-side network fee: Veterans pay 15%, non-Veterans pay 25%.
    * Platform fee (AV companies): 10% default, reduced to 5% when the fleet partner maintains $25,000 or more in their escrow account at mission start time.
    
    **Required fixes:**
    * Update `docs/API_SPEC.md` and `docs/legal/COMPLIANCE.md` to reflect the tiered agent fee structure (15% / 25%) and the platform fee structure (5% / 10% with escrow threshold).
    * Backend should become the authoritative calculator: `complete_mission` should return `net_payout` as a field on the response, rather than returning gross amounts that the client subtracts from.
    * UI should render the `net_payout` field directly rather than computing locally. This eliminates the Item below (`isVeteran` hardcoded mock) as a side effect.
    * Backend must check escrow account balance at mission-start time and apply either 5% or 10% platform fee accordingly. Verify this logic exists; if not, add it.
    * Add contract/compliance note to `docs/legal/COMPLIANCE.md` clarifying that the fee structure is disclosed to agents in their onboarding agreement and to fleet partners in their API integration agreement. Legal must sign off on this before Mesa launch.

---

## Compliance / Storage

### High priority

* **[PILOT BLOCKER] Migrate SB 1417 evidence uploads from imgbb to S3/GCP.** The tactical camera currently uploads redacted 720p/3fps evidence frames to imgbb. Acceptable for sandbox, not acceptable for the Vanguard 50 pilot. Evidence must route to WORM-compliant AWS S3 or GCP Cloud Storage before fleet-partner onboarding. This is a statutory Arizona SB 1417 retention requirement and a condition of the $5M tech E&O liability shield. Target bucket configuration already sketched via `S3_EVIDENCE_BUCKET_NAME` env var in `.env.example`.

---

## Hardware / Bluetooth

### High priority

* **[PILOT BLOCKER] Implement `AndroidBleHapHatService`.** `AgentDashboardScreen.kt` currently calls `rememberBleHapHatService()` which returns a mock hardware service. Need the real Android BLE implementation to command the ESP32-C3 motors and NeoPixels on the HapHat module. Without this, agents in the field cannot receive haptic or visual mission alerts through the HapHat hardware. See `docs/hardware/HAPHAT_SPEC.md` (Pass 4 Cat 4 item) for the target BLE UUIDs and command protocol.

---

## Security Items (post-core/ purge)

The earlier security review flagged 12 files as `[NEEDS VERIFICATION]`. All 12 lived in `core/backend/` and were removed by Stage 1c (commit `21db5df`). The findings are now auto-resolved.

Two items from that review remain active because they concern files that live in `apps/backend/src/`, not in the deleted `core/backend/`:

* **`apps/backend/src/compliance/audit_engine.py`** — load-bearing for SB 1417. Not yet reviewed in detail. Priority review before fleet-partner-facing beta.

* **Dispatch endpoint auth strength.** `/api/v1/dispatch/request` now uses `PARTNER_API_KEY` + `secrets.compare_digest`, which is good. But bearer tokens can still leak via logs, screenshots, Slack pastes, etc. For Waymo/Zoox-level partners, prefer the V2X Ed25519 signature path.

---

## Developer Tooling

* **Expand commit-msg hook scopes.** Current hook at `.git/hooks/commit-msg` allows five scopes: `core | gateway | ops-hub | app | ui`. Historical commits have used at least: `patrol`, `sync`, `telemetry`, `navigation`, `dispatch`, `ledger`, `hardware`, `security`, `docs`, `build`. Proposed additions (architectural, not feature-scoped):
    * `docs` - documentation-only changes
    * `hardware` - BLE, UWB, TPM, sensor integration
    * `security` - authentication, attestation, key ceremony, auth middleware
    Avoid adding narrow feature scopes (`patrol`, `sync`, `dispatch`) - those belong in the subject line.

* **Retire or repurpose root `Dockerfile` and `docker-compose.yml`.** Currently build the pre-pivot Flask + cognitive vault + LND + bitcoind stack. The FastAPI app at `apps/backend/src/main.py` is NOT what docker-compose runs today. When the operator runs `docker-compose up`, it builds a pre-pivot container that is not the real shipping backend. Decision needed: rewrite both files to build and run the FastAPI stack, or delete them and move dev to direct `uvicorn apps.backend.src.main:app` invocation with an optional lightweight docker-compose for postgres/redis only.

* **Set PYTHONUTF8=1 globally.** Windows Git Bash defaults to cp1252 which mangles the emojis in source and docs. Setting this in the user profile avoids intermittent "invalid byte 0x8f" errors when Python opens files without explicit encoding. Also prevents the heredoc emoji-stripping problem that damaged SUMMARY.md once during this cleanup.

* **Second venv at `apps/backend/venv/`.** A stray venv exists alongside the root `.venv/`. Contains `google.genai` and `langsmith` packages from the deprecated chatbot subsystem. Likely leftover and deletable, but verify nothing (IDE config, script) is pointing at it first.

* **Pin `python-multipart` floor in requirements.txt.** Done in 14e967e (added `>=0.0.16`). Leaving this note in case a future dependency resolver needs a pin adjustment.

* **`.gitattributes` for line endings.** Currently no rules. Every file edit on Windows produces `warning: LF will be replaced by CRLF` messages. Not harmful but noisy. Consider `*.md text eol=lf` or similar to lock a convention.

* **Update `.gitmessage` URL reference.** Current template contains `See: https://github.com/Proxy-Agent-Network/core/docs/` which is a dead URL path (the repo structure no longer has `core/docs/` as a documentation root). Update to point at the repo's actual docs location on GitHub.

---

## Mobile / UI

### High priority

* **[PILOT BLOCKER] Build real Firebase Auth end-to-end flow.** `PanWalletClient.kt` identity resolution currently falls back to `if (BuildConfig.IS_DEBUG) "DEV_AGENT_01" else null`. Fine for local testing, but there is no real login screen or Firebase Auth flow in the app yet. Without this, real agents arriving at the Mesa Hub cannot sign in to begin their Key Ceremony. Needs: login UI, Firebase Auth integration for email/password or OAuth, identity-to-agent_id mapping logic in `PanWalletClient`, and end-to-end testing against the backend auth middleware.

* **[PILOT BLOCKER] Remove hardcoded `isVeteran` mock in `AgentDashboardScreen.kt`.** Currently: `val isVeteran = true  // MOCKED FEE STATUS for UI testing`. Every agent gets the veteran fee tier regardless of actual status. Resolution depends on the Architecture / Economics fee reconciliation item - once the backend returns `net_payout` directly, the client no longer needs to know `isVeteran` at all. Until that lands, at minimum the flag should be pulled from the agent's `verified_credentials` array in their backend profile rather than hardcoded.

* **Resolve `@file:Suppress` hacks in network clients.** Both `PanWalletClient.kt` and `PanApiClient.kt` currently suppress `INVISIBLE_REFERENCE` and `INVISIBLE_MEMBER` warnings as a workaround for a Gradle `visibility(PUBLIC)` compilation issue. Fix the underlying visibility config, then remove the suppressions. Risk of future breakage: Kotlin/KMP version bumps may promote these warnings to hard errors, which would turn a cosmetic workaround into a build failure.

### Medium priority

* **iOS feature parity with Android.** Tracking release of `-beta` tag on `2026.2.0-beta` until iOS catches up to the Android app. No concrete feature list yet; start from comparing iOS shared/common module coverage vs Android expected from the KMP migration.

* **Fleet dashboard beta-test cycle.** Same gating as iOS parity.

### Low priority

* **Dynamic GPS injection for Dev Menu.** The `LOC 1`, `LOC 2`, `LOC 3` buttons in `AgentDashboardScreen.kt` hardcode Mesa, AZ intersections. When we expand beyond Mesa, these need to dynamically pull coordinates from the active Sector's Geohash polygon. Purely a dev-UX item; doesn't affect production routing.

---

## Post-Pilot Features

These are feature ideas that have been scoped and designed but are deliberately deferred until after Mesa Pilot ships. None are pilot blockers. They are recorded here so the design thinking is not lost. Each links to a more detailed design doc under `docs/design/`.

### Loadout Modes (Vehicle / E-Bike-Scooter / Foot Patrol)

Adds three loadout modes that determine an agent's service radius, eligible mission tiers, and equipment requirements. Vehicle remains the default; E-Bike/Scooter and Foot Patrol open up new agent demographics and service contexts (campus deployments, dense urban cores, airport terminals).

Key design decisions captured:
* Vehicle: 1-8 mile radius, default 5 miles. Eligible for all mission tiers.
* E-Bike/Scooter: 0.5-3 mile radius, default 1.5 miles. Eligible for Tier 1 and Tier 2 with constraints. Blocked from vehicle takeover missions because the agent cannot leave their bike or scooter behind to drive the AV.
* Foot Patrol: 0.125-1 mile radius, default 0.5 miles. Tier 1 only (door closing, trash cleanup, light diagnostics). No gear-heavy or driving-required missions.
* Service radius is enforced at dispatch: only missions within the agent's eligibility zone get routed to them. Includes the second-mission-in-queue case (radius is measured from the location of the prior mission's AV, not the agent's current location).
* Loadout mode does NOT affect base fee. Surge pricing applies uniformly per zone.
* SLA targets remain tier-based (15 min Tier 1, 20 min Tier 2, 25 min Tier 3) regardless of loadout. Adjustments may follow once pilot data exists.

Full design at `docs/design/LOADOUT_MODES.md`.

### Priority Bonus

Optional fleet-manager-set bonus paid to agents who complete a mission within a target time. Bonus is invisible to the agent at dispatch time and accept time; it appears as a pleasant surprise notification after job completion. This is intentional: hiding the bonus prevents cream-skimming, prevents SLA gaming, and removes any temptation for agents to drive recklessly to chase a known reward.

Preset structure:
* OFF (default): No bonus. ($0 / $0 / $0)
* Balanced: $3 at 15 min, $6 at 20 min, $9 at 25 min.
* Fastest: $5 at 15 min, $10 at 20 min, $15 at 25 min.
* Custom: Any manual modification of any tier value (including turning the OFF preset on with a non-zero amount, or tweaking any value in Balanced or Fastest) auto-switches the preset to Custom.

The name "Priority Bonus" was chosen over "Commendation" (commendation has formal meaning in military and first-responder culture and should be reserved for a future non-monetary honor feature), and over "Rush Fee" or "Speed Bonus" (legal concern: framing risks encouraging agents to run red lights or drive recklessly to chase the bonus).

Full design at `docs/design/PRIORITY_BONUS.md`.

---

## Notes on this file

* Add new items as they surface. Move items to GitHub Issues when they are ready to be planned into a sprint.
* Remove items when they ship. Link to the closing commit or PR in the removal commit message.
* This file is not a substitute for the CHANGELOG. The CHANGELOG records what shipped; this file tracks what we are putting off.
* Search for **[PILOT BLOCKER]** to surface Mesa Pilot launch-critical items across all sections.
* When working in this file, the Architectural Context section at the top is the orientation for new contributors — keep it current as the pivot resolves.
