# Proxy Agent Network (PAN) | TODO

Tracking deferred work that has been identified but scheduled for later. Items are grouped by area and rough priority. This is not an authoritative backlog (GitHub Issues remain the source of truth for bugs and features); it is a working notebook for decisions and known gaps that surfaced during code reviews, security sweeps, and documentation passes.

Items tagged **[PILOT BLOCKER]** must be resolved before the Vanguard 50 Mesa Pilot goes live. There are currently 4 active pilot blockers across Backend, Compliance, Architecture, and Mobile sections (down from 9 after the 2026-04-26 sweep resolved 4 fully and reduced 1 more to a docs-only follow-up; the HapHat hardware blocker has been deferred to the Q3 2026 to Q2 2027 hardware rollout per the pilot pivot). Search for that tag to triage launch-critical work.

Last updated: 2026-04-26.

---

## Architectural Context (read this first)

The repository is currently mid-pivot from the original "Proxy AI" cognitive-vault Flask monolith to the "Proxy Agent Network" FastAPI V2X gateway for the Mesa autonomous-vehicle-recovery pilot.

**The canonical future stack:**
* **Backend:** FastAPI, entrypoint at `apps/backend/src/main.py`. This is what gets hardened, audited, and shipped to Mesa.
* **Mobile:** `apps/mobile/pan_tactical/composeApp/` (Kotlin Multiplatform, Android first, iOS parity pending).
* **Ops Hub:** `apps/ops-hub/` (React + Vite + Leaflet, post-AV-pivot Sector Command map for live dispatch). Note: `apps/web/internal_dashboards/` previously held pre-fork prototype dashboards but was purged in Stage 3-a; only legitimate AV regulatory legal docs and the `command.html` Sector Command page remain there pending relocation to `docs/legal/`.
* **Docs:** `docs/` (the tree at the repo root, not `core/docs/`).

**What is legacy and scheduled for removal:**
* `core/` — 75 tracked files remaining (down from 444 at start of migration). The v2 "AI civilization" backend code has been fully purged. Remaining content is mostly pre-pivot infrastructure (Dockerfile, docker-compose.yml, requirements.txt, Cargo.toml), pre-pivot Python entrypoints (master_node.py, mcp_server.py, dashboard.py, agent_engine_v2.py, autonomous_worker.py), and legacy subdirectories that may overlap with canonical locations elsewhere in the repo. See the Repo Hygiene / Architecture section for the residual cleanup plan.
* `apps/backend/entrypoints/app.py` — the Flask monolith. Currently broken (imports from deleted `core.db` and `core.lightning_engine`) but contains live backend logic for the Vanguard 50 Command Center web UI (login, admin, partner dispatch endpoint, telemetry history). Cannot be deleted until those endpoints are migrated to FastAPI routers. Tracked as Stage 1d-3 below; the public marketing pages and executive reports endpoints have already been migrated to FastAPI in Stages 1d-3-a and 1d-3-b respectively, but the Flask handlers remain in app.py during the parallel period until Stage 1d-3-c finishes the migration and Stage 1d-5 retires app.py entirely.
* Root `Dockerfile` and `docker-compose.yml` — both build the pre-pivot Flask + cognitive vault + LND + bitcoind stack. The `proxy_agent` container they produce no longer boots after Stage 1c. Cannot be retired until app.py migration completes (Stage 1d-3 + 1d-5).

**Canonical evidence-upload path (added 2026-04-25):** `apps/backend/src/api/agent_api.py` defines the live, hardened `/agent/evidence/upload` endpoint. It is wired into `main.py` at `/api/v1` prefix (final URL `/api/v1/agent/evidence/upload`), is what the Android client calls (`PanApiClient.kt` line 393), and is the production-quality implementation: rate limiting (60/hr/agent), magic-byte content sniffing for JPEG/PNG verification, AES256 server-side encryption, S3 object metadata for chain of custody, presigned URL generation, a Redis ownership index at `pan:agent:{agent_id}:evidence:{blob_id}` used by the mission-completion handler to verify agent ownership of submitted evidence URLs, and a production-blocking startup check that raises `RuntimeError` if `S3_EVIDENCE_BUCKET_NAME` env var is unset in production. The legacy `evidence_api.py` was deleted in Stage 1e-3 (commit `a34123e`) as a half-finished alternative implementation. The single feature evidence_api.py had that agent_api.py lacks is S3 Object Lock in COMPLIANCE mode for SB 1417 §28-9710 12-month tamper-resistant retention. The Object Lock parameters need to be added to `agent_api.py`'s `upload_evidence` handler as part of the existing SB 1417 pilot blocker work (see Compliance / Storage section), NOT by re-introducing a parallel router.

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
* **Stage 1d-1** (`ec15ca4`): Retired pre-pivot Panopticon files. Removed apps/backend/entrypoints/master_node.py (a 278-line standalone Flask server on port 5001 implementing the v2 civilization treasury dashboard) and apps/backend/entrypoints/autonomous_worker.py (the 103-line client that paired with it). 383 lines deleted.
* **Stage 1d-2** (`8bb279f`): Fixed the broken `from backend.core.lightning_engine` import in apps/backend/entrypoints/mcp_server.py to `from core.lightning_engine` and added the standard sys.path.insert pattern. mcp_server.py is the FastMCP server exposing Vanguard dispatch tools to fleet partner AI clients (dispatch_vanguard_agent, check_network_surge, check_mission_status, pull_sb1417_report) — preserved as live AV-pilot code.
* **Stage 1d-4** (`c89ce0c`): Renamed `apps/web/command_center/secrets.js` to `pan_client_config.js`. The file holds `GOOGLE_MAPS_API_KEY` and `FIREBASE_CONFIG` for the command_center frontend; it was correctly gitignored throughout (verified `git ls-files` returns empty), but the filename "secrets.js" in a public repo invited grep curiosity. Audit-time security verification: Firebase Realtime DB / Storage / Firestore all have rules denying all access; Google Maps API key locked down via HTTP referrer restrictions in Google Cloud Console. No key rotation needed. Updated 4 HTML script tag references plus 2 Flask route lines in app.py (the `@app.route('/secrets.js')` and `send_from_directory` filename), updated both gitignores to the new filename, added a committed `pan_client_config.example.js` template with placeholder values and security notes for new developers, deleted accidental `test.rar` check-in. 9 files changed, 41 insertions, 8 deletions.
* **Stage 3-a** (`ee637c1`): Mass deletion of pre-fork content from `apps/web/internal_dashboards/`. 96 files deleted (98 changes total — 96 deletions plus 2 doc patches): all 71 jsx files in `src/` plus 1 .js file (v2 civilization prototype dashboards: high_court_*, jury_*, juror_*, quarantine_*, reputation_slashing_*, insurance_*, regulatory_audit, identity_migration, hodl_escrow, governance_voting, treasury_audit, etc.); 13 pre-fork audio files in `public/audio/`; the `magic_marvin_dance.webp` image; the `internal_dashboards` copy of `human/proxy_node_agreement.md` (a v2 captcha-bypass "Proxy Protocol Network" agreement, distinct from and unrelated to the post-pivot Vanguard MSA file of the same name preserved in `apps/web/public_website/static/human/`); 7 v2 civilization HTML pages (aup, economics, governance, legal, privacy, tos, transparency); and 2 captcha-bypass POA legal templates (ai_power_of_attorney.md, UK_LIMITED_POWER_OF_ATTORNEY.md). Patched `legal/JURISDICTION_MAP.md` and `legal/README.md` to reference the not-yet-drafted `AZ_M2H_MANDATE.md` instead of the deleted `ai_power_of_attorney.md`. ~21,500 lines removed in one commit. Discovered new pilot blocker: AZ_M2H_MANDATE.md does not exist (see Compliance / Storage section below).
* **Stage 1e-1** (`d083892`): Deleted 5 orphan files from `apps/backend/src/api/` totaling 510 lines. Four were standalone-FastAPI-app pattern files (each defining their own `app = FastAPI(...)` and self-launching on dedicated ports 8001, 8002, 8021, 8024) that were never imported by `main.py` and contained pre-pivot v2 civilization concepts: `dashboard_api.py` (High Court cases, VRF jury votes, PIP-882 protocol voting), `insurance_actuary_api.py` (Insurance Pool bayesian solvency engine), `status_api.py` (mock global node count regional health), `threat_intelligence_api.py` (Sybil cluster / TPM revocation IP blacklist). The fifth, `agent_request.py`, was a pre-pivot SDK demo CLI script posting hardcoded fake "Photography" tasks to localhost:5000.
* **Stage 1e-2** (`4f46f53`): Wired `store_api.py` into `main.py`. The router defined four agent gear shop endpoints (checkout, orders, shipment registration, waitlist) but had never been imported, so all four returned 404 in production. Most notably the Vanguard Android app calls `POST /api/v1/store/waitlist` via `PanWalletClient.kt` line 303 when an agent joins the gear waitlist, and this had been silently failing. Stripped explicit `/v1/` prefix from all four route decorators in `store_api.py` so they match the convention used by every other wired router (decorators define routes WITHOUT the `/api/v1` prefix; `main.py` provides it via `include_router(prefix="/api/v1")`). Final URLs: `/api/v1/store/checkout`, `/api/v1/store/orders/{order_id}/shipment`, `/api/v1/store/orders`, `/api/v1/store/waitlist`. 2 files changed, 6 insertions, 4 deletions.
* **Stage 1e-3** (`a34123e`): Deleted `apps/backend/src/api/evidence_api.py` (86 lines) as superseded by the agent_api.py implementation. The file defined a `/v1/agent/evidence/upload` endpoint that was never imported by main.py, while agent_api.py defines a fully-wired `/agent/evidence/upload` endpoint at the same effective URL. The mobile client calls the agent_api version. See the canonical evidence-upload path note in the Architectural Context section for details on which features survive (in agent_api.py) and which need porting (S3 Object Lock for SB 1417 WORM compliance — tracked as part of the SB 1417 evidence pilot blocker, NOT by reintroducing a parallel router).
* **Stage 3-a addendum** (`c74dc13`): Cleaned the missed POA duplicates in `apps/web/public_website/static/legal/`. Yesterday's Stage 3-a only deleted the `internal_dashboards` copies; this commit deleted the parallel `public_website` copies of `ai_power_of_attorney.md` and `UK_LIMITED_POWER_OF_ATTORNEY.md`, and applied identical 3-patch updates to `JURISDICTION_MAP.md` and `README.md` so they no longer reference the deleted ai_power_of_attorney.md filename. Preserved: `singapore_poa.md` and `us_delaware_poa.md` (legitimate post-pivot AV M2H mandate templates for One-North LTA and Delaware UETA jurisdictions respectively), and `static/human/proxy_node_agreement.md` (a completely different file from the v2 captcha-bypass agreement of the same filename deleted in Stage 3-a — this one is the legitimate Vanguard Agent Master Service Agreement v2026.1.0 for the Mesa Pilot). 4 files changed, 4 insertions, 142 deletions. Also surfaced a new pilot blocker: the public_website templates link to `/human/proxy_node_agreement.html` but no file or route serves that URL (the file is `.md`, not `.html`); the MSA link is broken in production. See Backend / Gateway section.
* **Stage 1d-3-a** (`89c3346`): First substage of the Flask-to-FastAPI command_center backend migration. Migrated the four public marketing routes (GET /, /operations, /rates, /investors) from Flask to FastAPI inline in `apps/backend/src/main.py`, matching the pattern already in use for /enlist and /enlist-success. Each route is a thin GET handler calling `templates.TemplateResponse` with the corresponding template filename. The four templates (index.html, operations.html, rates.html, investors.html) are pure HTML with no Jinja inheritance and no template variables, so the FastAPI version requires no global context injection. The Flask handlers in `apps/backend/entrypoints/app.py` lines 477-495 remain in place during the parallel period. Health check endpoint moved from `/` (which now serves index.html) to `/api/v1/health` to free the root path. Pre-existing bug fixed in app.py line 479 along the way: the Flask `/` route called `render_template('home.html')` but home.html does not exist (it was renamed to index.html in commit fd137ea but app.py was never updated); Flask `/` was returning 500 errors in production. Now matches FastAPI behavior. 2 files changed, 21 insertions, 4 deletions.
* **Stage 3-d-1** (`43a1fb8`): Stripped `.html` suffix from 45 broken navbar links across 6 public_website templates (api-spec.html, login.html, operations.html, our-mission.html, partners.html, rates.html). Single regex sweep converted `href="/foo.html"` to `href="/foo"`. Verified `/api/v1/*` references and the `/human/proxy_node_agreement.html` MSA link in base.html were not affected (the MSA link is tracked separately as pilot blocker #3 and requires a different fix). After this commit, navbar links to /, /operations, /rates, /investors, /enlist resolve to FastAPI handlers from Stage 1d-3-a; links to /our-mission, /partners, /login, /api-spec still 404 because those routes are not yet migrated, but a branded 404 page (Stage 3-d-2) softens the dead-end experience. The architectural debt that the 6 templates each duplicate the navbar inline rather than extending base.html is observed but not addressed here. 6 files changed, 45 insertions, 45 deletions.
* **Stage 3-d-2** (`a43e05f`): Added a branded 404 handler to the FastAPI gateway. Catches all 404s and routes them to either a navy/copper PAN-themed HTML page (apps/web/public_website/templates/404.html, 206 lines, self-contained inline CSS so it renders even if /static/css/main.css fails) for browser navigation, or a JSON `{detail: Not Found, path: ...}` response for `/api/`-prefixed requests. Branch detection is intentionally simple: paths starting with `/api/` get JSON; everything else gets HTML. This handles the dead links left behind by Stage 3-d-1 (links to not-yet-migrated routes) and also any future typos. 2 files changed, 223 insertions, 1 deletion.
* **Stage 3-d-3** (`26742d3`): Clarified the warning text in `apps/backend/src/utils/webhook_auth.py` for the centralized `_optional_env()` helper. TODO.md had flagged 4 typos in this file (reejected, webhookss, double space) but inspection found those typos no longer exist — the file was apparently refactored at some point to centralize the warning into a single helper, and the typos got cleaned up as a side effect. The substantive issue still needed fixing: the centralized warning said "Associated webhooks will be rejected" for ALL missing keys, including the PUBKEY_* fleet authentication keys that are NOT webhooks (they are Ed25519 public keys for V2X distress-signal verification). Fix: `_optional_env()` now accepts an optional `category` parameter (default "webhook" for backward compat); CARRIER_SECRETS passes `category="carrier webhook"` and V2X_FLEET_PUBKEYS passes `category="V2X fleet authentication"`. Operators debugging missing config now see accurate warnings. 1 file changed, 13 insertions, 8 deletions.
* **Stage 1d-3-b** (`54a78f3`): Second substage of the Flask-to-FastAPI command_center backend migration. Created `apps/backend/src/api/reports_api.py` (259 lines) containing the four executive reports endpoints (GET `/api/v1/reports/compliance`, `/operations`, `/financials`, `/vendor_sla`) and wired it into main.py with the standard `/api/v1` prefix. These endpoints power the executive reports dashboard at `apps/web/command_center/reports.html`, which calls all four with `?timeframe=` query strings (24h, 1w, 1m, 3m, 1y, custom) and renders KPIs, charts, and tables from the JSON responses. Because reports.html is in production and depends on specific JSON shapes, the migration was done as an exact translation: same logic, same random ranges, same dictionary keys; response shapes are CONTRACT-BOUND with the frontend. Migration mechanics: each Flask handler became an async APIRouter handler with FastAPI's Query parameter for timeframe (replacing `request.args.get`), return-dict-directly (replacing `jsonify`), and module-top imports for random/datetime (replacing the Flask handlers' lazy per-call imports). The TIMEFRAME_DAYS dict and a small `_resolve_days` helper got hoisted to module scope since all four endpoints used them identically. The Flask handlers in app.py lines 519-729 remain in place during the parallel period. Smoke tests included contract verification: each endpoint's response was called and the dictionary key structure was asserted against what reports.html expects to render. NOT migrated in this commit: `/api/v1/network/stats` was originally part of the planned scope but inspection revealed it makes a real Postgres query against the `nodes` table; FastAPI main.py does not have a Postgres connection wired (only Redis), so /api/v1/network/stats is deferred to its own commit (likely Stage 1d-3-b-2). 2 files changed, 261 insertions.
* **Stage 1d-3-b-2** (`19e138c`): Migrated `/api/v1/network/stats` from Flask to FastAPI. Required adding the sync psycopg2 helper module at `apps/backend/src/utils/db.py` with a `DBWrapper` class wrapping a single connection plus a `get_db_dep()` FastAPI dependency that yields a fresh wrapper per request and closes after response. Module-level fail-closed check refuses to load if `DATABASE_URL` env var is missing or contains the insecure default password. Created `apps/backend/src/api/network_stats_api.py` using the established sync `def` route pattern (FastAPI runs sync routes in a threadpool, which is the supported path for blocking psycopg2 calls). The decision to use sync psycopg2 over asyncpg was deliberate: it lets future migrations translate Flask handlers line-for-line during the parallel period without simultaneously rewriting their SQL access. Vanguard 50 pilot scale (50 concurrent agents) does not justify the async migration cost. The Flask handler in app.py remains in place during the parallel period.
* **Stage 1d-3-c** (`306e045`): Migrated session-cookie authentication and command center pages from Flask to FastAPI. Added Starlette `SessionMiddleware` with strict same-site cookies, fail-closed signing-key check at boot. Migrated `/login` (GET form + POST handler), `/logout`, and the three login-gated SPA routes `/command`, `/developers`, `/reports`. Inline auth check via `request.session.get("authenticated")` is used instead of a `Depends()` because a redirect from a dependency requires extra exception-handler plumbing in FastAPI; three routes is too few to justify that abstraction. Migrated static asset serving via `StaticFiles` mounts at `/static`, `/command/css`, `/command/js`, plus the singleton `/pan_client_config.js` route. Templates configured with `FileSystemLoader([COMMAND_CENTER_DIR, PUBLIC_TEMPLATE_DIR])` to mirror the old Flask `ChoiceLoader`. Public marketing routes (`/our-mission`, `/partners`, `/api-spec`, `/`, `/operations`, `/rates`, `/investors`, `/enlist`) are NOT served from this gateway; they were moved to a Netlify static-hosted public website at `apps/web/netlify_public/` so the FastAPI gateway only handles JSON APIs and the authenticated command center. The Flask handlers in app.py remain in place during the parallel period.
* **Pilot Blocker Sweep** (`17bad8d`): Resolved four of nine pilot blockers in a single commit. (1) Secured `/dev/override-hardware` endpoint by moving it into `onboarding_api.py` under `verify_agent_signature` auth, scoping the pubkey deletion to the authenticated agent's identity, and gating the entire endpoint behind an `ENVIRONMENT != "production"` check that returns 403 in production. (2) Completed Checkr API wiring: the `create_checkr_invitation` function now performs real candidate creation and invitation calls against `https://api.checkr.com/v1/`, with strict production boot guards that refuse to start the gateway if `CHECKR_TEST_SECRET_KEY` or `CHECKR_WEBHOOK_SECRET` are missing in production. The `checkr_webhook_listener` verifies HMAC-SHA256 signatures on incoming webhooks before advancing agent status to `VERIFIED_AWAITING_HARDWARE`. (3) Fixed the broken MSA link by adding a `/human/{filename}.html` route to main.py that renders Markdown legal documents from `apps/web/public_website/static/human/*.md` as PAN-themed HTML. Path parameter constrained by regex `^[a-zA-Z0-9_\-]+$` for path-traversal hardening. (4) Added S3 Object Lock COMPLIANCE mode and SHA-256 content-addressable hashing to the `agent_api.py::upload_evidence` handler, satisfying SB 1417 §28-9710 12-month tamper-resistant retention. Object Lock parameters `ObjectLockMode='COMPLIANCE'` and `ObjectLockRetainUntilDate` now set on every PutObject call. Also implemented authoritative backend fee math: `complete_mission` returns `net_payout` directly (15 percent agent fee for veterans, 25 percent for non-veterans), platform fee tier (5 percent or 10 percent based on $25,000 fleet escrow threshold) is locked in at mission genesis in `v2x_bounty_api.py::process_core_distress`. 5 files changed, 237 insertions, 75 deletions.
* **Stage 1d-3-d-1** (`5ac8727`): First endpoint of Stage 1d-3-d migrated. Created `apps/backend/src/api/dispatch_api.py` and migrated `/api/v1/dispatch/request` from Flask to FastAPI with constant-time `PARTNER_API_KEY` bearer auth via a local `verify_partner_api_key` dependency. Behavior preserved bit-for-bit vs the legacy Flask handler: same FLT-NNNNN mission ID format, same tier and bounty math (Tier 1 = $15, Tier 2 = $25 for spill_remediation/tire_pressure, Tier 3 = $85 for manual_override/scene_securement, max cap = base + $20), same 400 contract for missing fields and invalid JSON (manual dict validation chosen over Pydantic specifically to preserve this; Pydantic default would be 422), same 401 contract for missing/invalid auth, same 201 response shape and timestamp wire format. New behavior added during migration: synthesized mission_id is now published to `pan:stream:distress_alerts` Redis channel so the Ops Hub command-center map lights up on partner-originated dispatches. The legacy Flask handler built this `map_payload` dict but never sent it; the downstream subscriber in `api/telemetry_socket.py` was already in place. Smoke tested: 10-curl sequence covering 401 (missing/wrong/no-Bearer-prefix), 400 (empty body, missing field), and 201 across all three tiers with correct escrow and max_cap math. Redis publish verified live via `redis-cli MONITOR`. The Flask handler in `apps/backend/entrypoints/app.py` lines 415-479 remains in place per the parallel-period strategy, but is now eligible for early deletion since (a) the FastAPI version is verified working, (b) nothing is in production yet, and (c) the new Redis publish behavior would not be replicated by the Flask version, creating drift risk if a request ever routes there. 2 files changed, 224 insertions.

Cumulative deletion across Stages 0-3a: ~485 files, ~59,100 lines deleted from the repo. Migration commits across both days have added net ~1,200 lines of new FastAPI code (reports_api.py 259, 404.html 206, network_stats_api.py 47, dispatch_api.py 221, plus session-cookie auth and command-center routes inline in main.py, plus the markdown rendering route, plus the broken-link sweep across 6 templates), but those additions are FastAPI replacements for Flask code that will be deleted in Stage 1d-5. apps/backend/src/api/ now contains 10 files, all using proper APIRouter pattern: agent_api.py, dispatch_api.py (NEW 2026-04-26), network_stats_api.py (NEW 2026-04-26), onboarding_api.py, reports_api.py, store_api.py, telemetry_socket.py, v2x_bounty_api.py, v2x_telemetry_api.py, wallet_api.py (nine wired into main.py directly, the tenth — v2x_telemetry_api — imported transitively via v2x_bounty_api). The two surviving entrypoints in apps/backend/entrypoints/ are app.py (live but substantially superseded by FastAPI; only the worker-mock and seed-dvr endpoints plus the in-app dispatch handler remain unmigrated, awaits final Stage 1d-3-d work and Stage 1d-5 retirement) and mcp_server.py (live and working).

### Stage 1d-3 — migrate command_center backend from Flask to FastAPI (priority: medium-high)

`apps/backend/entrypoints/app.py` is 998 lines of Flask code that cannot be deleted as originally hoped. The Vanguard 50 Command Center web UI (at `apps/web/command_center/`) actively depends on it. The migration is being executed in substages with parallel-period testing between each. Substages already complete are listed in the Completed Migration Stages history above. Remaining substages and what each must accomplish:

**Stage 1d-3-b-2 leftover — `/api/v1/admin/settings`:**
* `/api/v1/admin/settings` — admin UI settings (theme, mood_intensity), needs auth review before migration. The rest of Stage 1d-3-b-2 (network/stats) shipped in commit `19e138c`.

**Stage 1d-3-d remaining endpoints (the first endpoint shipped in commit `5ac8727`):**
* `/api/v1/dispatch/request` — DONE in `5ac8727`. See completed-stages history above.
* `/api/v1/telemetry/history` — real Postgres query, currently UNAUTHENTICATED (security issue, see Backend/Gateway section); migration must include adding auth.
* `/api/v1/node/register`, `/api/v1/task/request`, `/api/v1/task/submit` — mock worker endpoints that 403 in production; decide whether to migrate or delete during this substage.
* `/seed-dvr` — Manhattan-grid demo data seeder for telemetry; dev-only, needs Postgres connection (now available via the `utils/db.py` helper added in `19e138c`).

**Stage 1d-3-d eligible early cleanup (added 2026-04-26):**
* Delete the legacy Flask `api_dispatch_request` handler in `apps/backend/entrypoints/app.py` (lines 415-479). The FastAPI replacement was verified end-to-end on 2026-04-26 with the 10-curl smoke sequence and a live `redis-cli MONITOR` capture of the new `pan:stream:distress_alerts` publish. Nothing is in production yet (no DNS for `command.proxyagent.network`, no deploy workflow, only `tests.yml` in `.github/workflows/`), so the standard parallel-period rationale does not apply. Leaving the Flask version in place creates real drift risk because the Flask handler does not perform the new Redis publish; if a request ever routes there the Ops Hub map will silently miss it.

After all substages complete, Stage 1d-5 retires app.py entirely.

### Stage 1d-5 — retire app.py + Dockerfile + docker-compose.yml (priority: medium)

Only after Stage 1d-3 fully lands (Stage 1d-4 is already complete). With the command_center backend fully migrated:

* Delete `apps/backend/entrypoints/app.py`. All its endpoints now live in FastAPI routers under `apps/backend/src/api/` or inline in `main.py`.
* Delete the now-dead `load_optional_router` helper in `apps/backend/src/main.py` (defined at line 86, never invoked).
* Delete the root `Dockerfile`. It builds the pre-pivot Flask + cognitive_vault + LND + bitcoind stack via `COPY proxy-core /build/proxy-core` and friends.
* Delete the root `docker-compose.yml` OR replace it with a minimal lightweight compose that runs only postgres, redis, bitcoind, and lnd (no proxy_agent container). The minimal-compose option is preferable if local dev still wants those services available via `docker-compose up`.
* Stop and remove the running `proxy_agent` Docker container (which has been doing nothing since Stage 1c).

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
* **Audit the loose pre-pivot Python files at core/ root** (master_node.py, autonomous_worker.py, dashboard.py, agent_engine_v2.py, mcp_server.py). Most likely all dead, but some might have informational value worth preserving in a separate archive branch. Note: `core/mcp_server.py` is a duplicate of the now-fixed `apps/backend/entrypoints/mcp_server.py` and is safely deletable.
* **Decide the fate of the loose top-level non-Python files.** sample.mp3 and sample.mp4 are obvious deletes. Cargo.toml/Cargo.lock at core/ root are probably superseded by hardware/proxy-core/Cargo.toml.

### Stage 3-b — relocate surviving regulatory legal files to docs/ (priority: low, deferred)

After Stage 3-a, `apps/web/internal_dashboards/` contains 11 surviving files: 4 AV regulatory M2H mandate templates (CA_CPUC_MANDATE.md, TX_M2H_MANDATE.md, singapore_poa.md, us_delaware_poa.md), 2 supporting legal docs (JURISDICTION_MAP.md, README.md), 1 post-pivot HTML page (command.html, the Sector Command observability UI), 1 README (DASHBOARD.md), and 3 supporting frontend assets (css/main.css, css/themes.css, js/theme-engine.js). The proper home for the legal/regulatory documents is `docs/legal/` since they are reference documentation read by Fleet Legal Counsel and the PAN Compliance Engine, not assets served by an Ops Hub frontend. The HTML/CSS/JS Sector Command frontend has no host project (no package.json or vite.config.js), and its functionality may eventually be absorbed into the canonical Ops Hub at `apps/ops-hub/`. Recommend a future commit that:
* Creates `docs/legal/` directory if it does not exist
* `git mv` the 6 legal markdown files to `docs/legal/`
* Either deletes or relocates the `command.html` Sector Command page (decision deferred)
* Either deletes or relocates `DASHBOARD.md`, `css/`, `js/` (decision deferred)
* Deletes the now-empty `apps/web/internal_dashboards/` directory shell
* Updates any `docs/` README to mention the legal directory

After Stage 3-a addendum, `apps/web/public_website/static/legal/` similarly has surviving content that may want relocation alongside: the patched JURISDICTION_MAP.md and README.md, plus singapore_poa.md and us_delaware_poa.md. The 50 stock-photo headshots in `apps/web/public_website/static/images/roster/` are unrelated and tracked as a separate audit pass.

This is structural cleanup, not pilot-blocking. Lower priority than Stage 1d-3 and the pilot blockers.

### Stage 3-c — investigate apps/web/public_website/static/images/roster/ (priority: low, new)

The directory contains 50 stock-photo-style headshots in 25 personas (alice, bob, charlie, diana, dr_aris, dr_clara, dr_elena, dr_julian, dr_maeve, dr_nora, dr_silas, dr_thorne, dr_vance, ellen, eve, felix, gordon, liam, marcus, maya, olivia, zoe, plus a couple others), each in 50px and full-size variants. Likely vestigial from a pre-pivot "Team" or "Roster" page. Need to confirm whether any active template references them before deletion. Estimate ~5-10 MB of image data deletable in one commit if unused.

### Stage 3-d — template hygiene cleanups (in progress)

A grouping for small, focused template-and-frontend cleanup commits surfaced during the Flask-to-FastAPI migration. Substages 3-d-1, 3-d-2, and 3-d-3 are already complete (see Completed Migration Stages history). Remaining work in this group:

* **Refactor duplicate inline navbars to extend base.html.** The 6 templates touched in Stage 3-d-1 (api-spec.html, login.html, operations.html, our-mission.html, partners.html, rates.html) each define their own `<nav class="navbar">` block inline rather than extending base.html (which already has a correctly-formed navbar). The right long-term fix is to refactor each template to `{% extends "base.html" %}` with a `{% block content %}`, eliminating navigation duplication entirely. Significant work because each template's CSS classes need review for compatibility with base.html's classes; out of scope for the broken-link sweep but worth doing during Stage 1d-3-c when the auth/static migration touches these files anyway.

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

* **[RESOLVED 2026-04-26 commit `17bad8d`] Secure `/dev/override-hardware` endpoint.** The hardware lockout override added in commit `a27c7c4` hardcoded deletion of `pan:agent:DEV_AGENT_01:pubkey`. Two fixes were required before production: (1) dynamically scope the deletion to the authenticated agent's JWT subject, and (2) rigorously wrap the entire endpoint in an `if os.getenv("ENVIRONMENT") != "production"` block. **Resolution:** the endpoint moved into `apps/backend/src/api/onboarding_api.py` under the `verify_agent_signature` dependency, scoping deletion to the authenticated agent. Production gate added at the top of the handler returns 403 with a `SECURITY FATAL` log line if hit in production. The legacy unauthenticated `@app.post("/api/v1/dev/override-hardware")` route in `main.py` was deleted in the same arc to remove the URL collision with the new auth-gated router version. The DEV_AGENT_01 re-seed convenience was preserved by adding an `if agent_id == "DEV_AGENT_01"` branch that re-seeds the dev agent profile before deleting the pubkey.

* **[RESOLVED 2026-04-26 commit `17bad8d`] Complete Checkr API wiring in `onboarding_api.py`.** Background checks are a strict requirement per `docs/legal/COMPLIANCE.md`. The onboarding flow needed `CHECKR_API_KEY` fully wired through candidate creation, invitation, and webhook verification paths so agents cannot complete the Key Ceremony without a cleared background check. Env vars `CHECKR_TEST_SECRET_KEY` and `CHECKR_WEBHOOK_SECRET` already defined in `.env.example`. **Resolution:** `create_checkr_invitation` now performs real candidate creation and invitation calls against `https://api.checkr.com/v1/candidates` and `https://api.checkr.com/v1/invitations` using the `driver_pro` package slug. Strict production boot guards added at module load: the gateway refuses to start if `S3_PII_BUCKET_NAME`, `CHECKR_TEST_SECRET_KEY`, or `CHECKR_WEBHOOK_SECRET` are missing in production. Local dev retains a fallback that mocks the Checkr clearance and advances the agent to `VERIFIED_AWAITING_HARDWARE` directly. The `checkr_webhook_listener` verifies HMAC-SHA256 signatures on the raw request body before parsing the payload (raw_body is read once and reused, defending against the ASGI body-stream consumption issue that surfaces on some uvicorn configurations).

* **[RESOLVED 2026-04-26 commit `17bad8d`] Broken MSA link in public website templates.** Both `apps/web/public_website/templates/base.html` (line 57) and `apps/web/public_website/templates/enlist.html` (line 169) linked to `/human/proxy_node_agreement.html`. No file with that path existed, no Flask route in `apps/backend/entrypoints/app.py` served it, no markdown rendering middleware translated between `.md` and `.html`. The legitimate Vanguard MSA content lives at `apps/web/public_website/static/human/proxy_node_agreement.md` (a fully drafted post-pivot legal document, version 2026.1.0 Mesa Pilot, covering independent contractor status, the 15-minute SLA, the Optical Reclamation Protocol SOP, strict prohibitions, the $5M HNOA/E&O liability shield, and machine adjudication via L402 settlement). The `enlist.html` signup flow asserts that the agent has read and agreed to the MSA, but the link 404'd, meaning agents were signing the enlist form without being able to read the agreement they were supposedly agreeing to. This was both a basic contract-formation problem and a UX bug. Discovered during Stage 3-a addendum audit (commit `c74dc13`). **Resolution:** added a `/human/{filename}.html` route to `main.py` that reads `apps/web/public_website/static/human/{filename}.md`, renders it via the `markdown` library with `tables` and `fenced_code` extensions, and returns a self-contained PAN-themed HTML page with inline dark-mode styling. The `filename` path parameter is constrained by regex `^[a-zA-Z0-9_\-]+$` so path traversal characters never reach `os.path.join`. The `Markdown>=3.4.0` dependency was added to `requirements.txt` in commit `760fd97`.

* **Authenticate `/api/v1/telemetry/history`.** Currently unauthenticated. Anyone with network access can dump the full forensic GPS ledger via `?global=true`. Needs admin auth or OPS_HUB_TOKEN check. Pre-existing, flagged in security sweep. Should be addressed during Stage 1d-3-d when this endpoint is migrated to FastAPI.

### Medium priority

* **Worker mock endpoints.** `/api/v1/node/register`, `/api/v1/task/request`, `/api/v1/task/submit` in `apps/backend/entrypoints/app.py` now 403 in production, but they use a server-side shared-secret HMAC rather than per-agent pubkey verification. If these endpoints are genuinely dead, delete them. If they have a future purpose, replace with proper agent-pubkey auth. Decision should be made during Stage 1d-3-d.

* **Decide the fate of the Flask `/api/v1/node/register` workflow.** Same file as above. The mock_register endpoint uses `HARDWARE_ATTESTATION_SEED` as an HMAC key which is structurally weaker than the TPM-signed per-agent JWT path used everywhere else in the gateway. Pre-pilot question: is anything still calling this?

* **Consolidate `decode_redis_hash` helper.** Same function is duplicated across at least `apps/backend/src/api/v2x_bounty_api.py`, `apps/backend/src/api/agent_api.py`, and probably other modules. Extract to `apps/backend/src/utils/redis_helpers.py` or similar.

* **Partner multi-tenant migration.** Current `PARTNER_API_KEY` is a single-tenant bearer token used by the Flask `/api/v1/dispatch/request` endpoint. Future partners should either get `PARTNER_API_KEY_WAYMO` / `PARTNER_API_KEY_ZOOX` style namespacing, or (preferred) migrate to the V2X Ed25519 signature path.

### Low priority

* **Hardware attestation substring check.** `apps/backend/entrypoints/app.py` line 50 does `HW_SECURED = "0x8F9B" in MY_NODE_ID`, which is a magic-string prefix check rather than a cryptographic verification. TODO comment exists in the file for the Rust team to migrate to a signed-payload attestation.

* **Migrate `@app.on_event("startup")` to lifespan context managers.** FastAPI deprecation notice in `apps/backend/src/main.py`. Still functional but slated for a future architectural pass.

* **Remove now-orphaned `load_optional_router` helper.** After Pass 1's hard-import promotion in `main.py`, nothing calls `load_optional_router` anymore. Harmless dead code; will be deleted in Stage 1d-5.

* **Audit `asyncpg` in `requirements.txt` (added 2026-04-26).** `requirements.txt` lists both `psycopg2-binary>=2.9.9` and `asyncpg>=0.29.0`. `PROJECT_CONTEXT.md` and the new `apps/backend/src/utils/db.py` standardize on sync psycopg2 for the FastAPI migration period (the rationale being that FastAPI runs sync routes in a threadpool, which is good enough for Vanguard 50 pilot scale and lets handlers be ported line-for-line from Flask). Question: is `asyncpg` actually used by something live in the repo (a worker, an integration, a test fixture), or is it leftover from an abandoned plan? Quick grep: `grep -r "import asyncpg\|from asyncpg" apps/`. If unused, removing it from requirements.txt clarifies the codebase's actual dependencies. If used, document where so the next person who reads `db.py`'s "we picked psycopg2 over asyncpg" comment is not confused.

---

## Architecture / Economics

### High priority

* **[PILOT BLOCKER, partially resolved 2026-04-26 commit `17bad8d`] Reconcile fee math across code, backend, and docs.** Three sources of truth previously disagreed:
    * **Kotlin UI code** (`MissionAlertOverlay.kt`, `AgentDashboardScreen.kt`): calculates agent-side network fee as 15% (Veteran) or 25% (Standard)
    * **Backend** (`apps/backend/src/api/v2x_bounty_api.py::complete_mission`): uses `multiplier = 0.85 if is_veteran else 0.75`, matching the UI
    * **Docs** (`docs/API_SPEC.md`, `docs/legal/COMPLIANCE.md`): state a flat 10% PAN network fee with no veteran tier
    
    **Canonical economic model (source of truth going forward):**
    * Agent-side network fee: Veterans pay 15%, non-Veterans pay 25%.
    * Platform fee (AV companies): 10% default, reduced to 5% when the fleet partner maintains $25,000 or more in their escrow account at mission start time.
    
    **Backend fixes COMPLETE in commit `17bad8d`:**
    * `apps/backend/src/api/agent_api.py::complete_mission` now returns `net_payout` directly on the response (and a duplicate `netPayout` camelCase field for Kotlin client convenience). Lines 302-310 read `is_veteran` from the agent's Redis profile and apply the correct multiplier.
    * `apps/backend/src/api/v2x_bounty_api.py::process_core_distress` now reads `pan:fleet:{fleet_id}:escrow_balance` at mission genesis, sets `platform_fee_pct = 0.05 if escrow_balance >= 25000.0 else 0.10`, and locks that value into the task record so the fee tier is immutable for the life of the mission.
    
    **Remaining work (Mesa launch blockers):**
    * Update `docs/API_SPEC.md` and `docs/legal/COMPLIANCE.md` to reflect the tiered agent fee structure (15% / 25%) and the platform fee structure (5% / 10% with escrow threshold). Currently the docs still state the old flat 10% number.
    * UI should render the `net_payout` field directly rather than computing locally. The Kotlin networking layer at `PanApiClient.kt` already deserializes `netPayout: Double` (verified 2026-04-26), but `AgentDashboardScreen.kt` and `MissionAlertOverlay.kt` need to be confirmed/updated to use that value rather than reading their local `isVeteran` state.
    * Add contract/compliance note to `docs/legal/COMPLIANCE.md` clarifying that the fee structure is disclosed to agents in their onboarding agreement and to fleet partners in their API integration agreement. Legal must sign off on this before Mesa launch.

---

## Compliance / Storage

### High priority

* **[PILOT BLOCKER] Draft `AZ_M2H_MANDATE.md` (Arizona M2H Physical Intervention Mandate).** Discovered during Stage 3-a audit. The PAN Gateway routing logic in `apps/web/internal_dashboards/public/legal/JURISDICTION_MAP.md` (and the parallel patched copy in `apps/web/public_website/static/legal/JURISDICTION_MAP.md` after Stage 3-a addendum) references `AZ_M2H_MANDATE.md` as the active legal authorization document for the Mesa pilot, but the file does not exist anywhere in the repo. CA_CPUC_MANDATE.md and TX_M2H_MANDATE.md exist as drafts for future expansion sectors. Mesa Pilot CANNOT ship without an Arizona-specific M2H mandate that satisfies AZ Rev Stat § 28-9701 (SB 1417) and authorizes Vanguard agents to physically interact with stranded $150,000 autonomous assets. The CA and TX mandates can serve as templates. Should be drafted in coordination with retained mobility counsel before fleet-partner onboarding. Without this, the $5M HNOA/E&O liability transfer cannot legally activate when an agent dispatches in Arizona.

* **[RESOLVED 2026-04-26 commit `17bad8d`] Migrate SB 1417 evidence uploads from imgbb to S3/GCP, AND add S3 Object Lock for WORM compliance.** The tactical camera previously uploaded redacted 720p/3fps evidence frames to imgbb. Acceptable for sandbox, not acceptable for the Vanguard 50 pilot. Evidence had to route to WORM-compliant AWS S3 or GCP Cloud Storage before fleet-partner onboarding. This was a statutory Arizona SB 1417 retention requirement and a condition of the $5M tech E&O liability shield. Target bucket configuration already sketched via `S3_EVIDENCE_BUCKET_NAME` env var in `.env.example`. **Implementation note (added 2026-04-25):** the live evidence upload handler in `apps/backend/src/api/agent_api.py::upload_evidence` already did S3 PutObject with AES256 encryption and rate limiting, but did NOT set `ObjectLockMode='COMPLIANCE'` and `ObjectLockRetainUntilDate`. The deleted-in-Stage-1e-3 `evidence_api.py` had those parameters. The proper fix was to add the Object Lock parameters to the existing `upload_evidence` handler in agent_api.py; not to reintroduce a parallel router. **Resolution:** Object Lock parameters added to the `s3_client.put_object()` call at lines 267-268 of `agent_api.py`, with `retention_until` calculated to satisfy the SB 1417 §28-9710 12-month retention requirement. SHA-256 content-addressable hashing also added (file_hash computed at line 250, embedded into the blob_id and stored as object metadata under `sha256_hash`) so evidence integrity can be cryptographically verified independent of the storage layer. Bucket-side requirement still applies: the S3 bucket itself must have Object Lock enabled at creation time (cannot be enabled retroactively), with a default retention period of at least 366 days. Verify this is in place on the production bucket before pilot launch.

---

## Hardware / Bluetooth

### High priority

* **[DEFERRED to Q3 2026, was PILOT BLOCKER pre-pivot] Implement `AndroidBleHapHatService`.** `AgentDashboardScreen.kt` currently calls `rememberBleHapHatService()` which returns a mock hardware service. The real Android BLE implementation to command the ESP32-C3 motors and NeoPixels on the HapHat module is not yet written. Pre-pivot this was a Mesa launch blocker; per the 2026-04 architectural pivot, all custom hardware (HapHat, Aegis Polo, Vest, Gauntlets) has been pulled from the Vanguard 50 pilot scope so agents can join with a standard safety vest and their smartphone. The custom gear program is now scheduled for the Q3 2026 to Q2 2027 hardware rollout. The mock service in the Kotlin code can stay as-is for the pilot. See `docs/hardware/HAPHAT_SPEC.md` (Pass 4 Cat 4 item) for the eventual BLE UUIDs and command protocol when the real implementation is needed.

---

## Security Items (post-core/ purge)

The earlier security review flagged 12 files as `[NEEDS VERIFICATION]`. All 12 lived in `core/backend/` and were removed by Stage 1c (commit `21db5df`). The findings are now auto-resolved.

Two items from that review remain active because they concern files that live in `apps/backend/src/`, not in the deleted `core/backend/`:

* **`apps/backend/src/compliance/audit_engine.py`** — load-bearing for SB 1417. Not yet reviewed in detail. Priority review before fleet-partner-facing beta.

* **Dispatch endpoint auth strength.** `/api/v1/dispatch/request` (now living in `apps/backend/src/api/dispatch_api.py` after the 2026-04-26 migration in commit `5ac8727`) uses `PARTNER_API_KEY` plus `secrets.compare_digest`, which is good. But bearer tokens can still leak via logs, screenshots, Slack pastes, etc. For Waymo/Zoox-level partners, prefer the V2X Ed25519 signature path. The `verify_partner_api_key` dependency function returns a static partner identifier today; the return value is the seam for future multi-tenant namespacing if the V2X migration does not absorb all partners.

---

## Developer Tooling

* **Expand commit-msg hook scopes.** Current hook at `.git/hooks/commit-msg` allows five scopes: `core | gateway | ops-hub | app | ui`. Historical commits have used at least: `patrol`, `sync`, `telemetry`, `navigation`, `dispatch`, `ledger`, `hardware`, `security`, `docs`, `build`. Proposed additions (architectural, not feature-scoped):
    * `docs` - documentation-only changes
    * `hardware` - BLE, UWB, TPM, sensor integration
    * `security` - authentication, attestation, key ceremony, auth middleware
    Avoid adding narrow feature scopes (`patrol`, `sync`, `dispatch`) - those belong in the subject line.

* **Retire or repurpose root `Dockerfile` and `docker-compose.yml`.** Currently build the pre-pivot Flask + cognitive vault + LND + bitcoind stack. The FastAPI app at `apps/backend/src/main.py` is NOT what docker-compose runs today. When the operator runs `docker-compose up`, it builds a pre-pivot container that is not the real shipping backend. Decision needed: rewrite both files to build and run the FastAPI stack, or delete them and move dev to direct `uvicorn apps.backend.src.main:app` invocation with an optional lightweight docker-compose for postgres/redis only.

* **Set PYTHONUTF8=1 globally.** Windows Git Bash defaults to cp1252 which mangles the emojis in source and docs. Setting this in the user profile avoids intermittent "invalid byte 0x8f" errors when Python opens files without explicit encoding. Also prevents the heredoc emoji-stripping problem that damaged SUMMARY.md once during this cleanup.

* **Second venv at `apps/backend/venv/`.** A stray venv exists alongside the root `.venv/`. Contains `google.genai` and `langsmith` packages from the deprecated chatbot subsystem. Likely leftover and deletable, but verify nothing (IDE config, script) is pointing at it first. Note: the repo root also has both a `venv/` and `.venv/`; the canonical convention is `.venv/` (with leading dot). The unprefixed `venv/` is also a candidate for deletion once verified unused.

* **Pin `python-multipart` floor in requirements.txt.** Done in 14e967e (added `>=0.0.16`). Leaving this note in case a future dependency resolver needs a pin adjustment.

* **`.gitattributes` for line endings.** Currently no rules. Every file edit on Windows produces `warning: LF will be replaced by CRLF` messages. Not harmful but noisy. Consider `*.md text eol=lf` or similar to lock a convention.

* **Pin Python interpreter version (added 2026-04-26).** Local dev `.venv/` is currently running on Python 3.14 (verified from a uvicorn boot traceback), which is bleeding-edge (released October 2025). Several packages in `requirements.txt` are C extensions (`grpcio`, `psycopg2-binary`, `cryptography`); wheel availability for 3.14 is still patchy on some upstream packages and a future `pip install` may fall back to source builds with cryptic compiler error output. More importantly, this is the version mismatch that will be hardest to reproduce on a teammate's machine or a CI runner if either defaults to 3.12 or 3.13. Add a `.python-version` file at the repo root (consumed by pyenv and uv), and optionally pin in `pyproject.toml` if the project ever migrates off raw `requirements.txt`. Document the chosen target version in `PROJECT_CONTEXT.md`.

* **Add `load_dotenv()` to `apps/backend/src/main.py` (added 2026-04-26).** The legacy Flask `app.py` called `load_dotenv()` at module load, so launching the gateway worked from a freshly-opened shell with no environment setup. The FastAPI `main.py` does not, so every uvicorn launch requires the operator to manually `set -a; source .env; set +a` first. The package is already in requirements (`python-dotenv>=1.0.0`). Two-line addition near the top of main.py would restore parity. Until this lands, the developer setup docs need to mention the manual env-source step.

* **Update `.gitmessage` URL reference.** Done in commit `508b8a1` (2026-04-25). Template now points at `https://github.com/Proxy-Agent-Network/core/tree/main/docs/`. Leaving this note as a record.

---

## Mobile / UI

### High priority

* **[PILOT BLOCKER] Build real Firebase Auth end-to-end flow.** `PanWalletClient.kt` identity resolution currently falls back to `if (BuildConfig.IS_DEBUG) "DEV_AGENT_01" else null`. Fine for local testing, but there is no real login screen or Firebase Auth flow in the app yet. Without this, real agents arriving at the Mesa Hub cannot sign in to begin their Key Ceremony. Needs: login UI, Firebase Auth integration for email/password or OAuth, identity-to-agent_id mapping logic in `PanWalletClient`, and end-to-end testing against the backend auth middleware.

* **[PILOT BLOCKER, partially resolved 2026-04-26 commit `17bad8d`] Remove hardcoded `isVeteran` mock in `AgentDashboardScreen.kt`.** Currently: `val isVeteran = true  // MOCKED FEE STATUS for UI testing`. Every agent gets the veteran fee tier regardless of actual status. Resolution depends on the Architecture / Economics fee reconciliation item: once the backend returns `net_payout` directly, the client no longer needs to know `isVeteran` at all. **Backend side is now COMPLETE:** `complete_mission` returns `net_payout` and `netPayout` (camelCase mirror) on the response, and `PanApiClient.kt` now declares `@SerialName("net_payout") val netPayout: Double` at line 82-83 of the data model so the field deserializes correctly. **Remaining UI work:** `AgentDashboardScreen.kt` and any other Compose screen still computing the agent-side fee locally must be updated to read `netPayout` from the mission completion response and render it directly, removing the local `isVeteran` flag entirely. This work has not been verified.

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
