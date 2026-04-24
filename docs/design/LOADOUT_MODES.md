# Design: Loadout Modes (Vehicle / E-Bike-Scooter / Foot Patrol)

**Status:** Design draft. Deferred until after Mesa Pilot.
**Owner:** Rob.
**Last updated:** 2026-04-24.

## Problem

The Vanguard 50 Mesa Pilot launches with a single agent loadout assumption: every agent is operating from a personal vehicle. That assumption works for suburban Mesa where service zones span several miles. It does not scale cleanly to:

* Dense urban cores (downtown Phoenix, downtown Tempe, downtown Scottsdale) where parking is scarce and a vehicle-based agent is slower than alternatives.
* Constrained-geography settings (Phoenix Sky Harbor terminals, ASU Tempe campus, sports and entertainment venues) where a foot-patrol agent can be on scene in 3 minutes while a vehicle-based agent might take 15 just to find parking.
* Cost-sensitive recruitment pools. Not every prospective agent has access to a personal vehicle. E-bike or scooter operators expand the agent pool meaningfully, especially in college-town and urban-core demographics.

Without first-class loadout support, the system either turns away these agents at onboarding or routes them missions they cannot serve well.

## Proposal

Introduce three loadout modes selected at agent onboarding and modifiable in the agent app's settings.

### Vehicle

The default and the only loadout supported in the Mesa Pilot itself. Agent operates from a personal car or truck.

* Service radius: configurable 1 to 8 miles. Default 5 miles.
* Eligible mission tiers: All (Tier 1 through Tier 3).
* Equipment requirement: Full hardware kit (toolkit, OBD reader, traffic cone, safety vest, HapHat).
* Notes: This is the default loadout. Existing dispatch logic and the pilot SLA targets are calibrated against this mode.

### E-Bike / Scooter

Agent operates from a personal e-bike or scooter. Battery and storage capacity constrain what missions they can serve.

* Service radius: configurable 0.5 to 3 miles. Default 1.5 miles.
* Eligible mission tiers: Tier 1 and Tier 2 with constraints. **Blocked from vehicle-takeover missions** regardless of tier, because the agent cannot leave a personally-owned bike or scooter unattended at the AV scene to drive the AV miles away.
* Eligible Tier 2 examples: charging an AV battery from a portable pack, cleaning sensors, inflating a low tire. Each requires the agent to physically carry the relevant gear in a saddle bag or backpack.
* Equipment requirement: Subset of full kit. The exact subset depends on which Tier 2 missions the agent has opted into.
* Notes: Sensible workhorse for the dense-urban use case. Must be paired with sector-level eligibility rules that route only urban-core sectors to bike and scooter agents.

### Foot Patrol

Agent operates entirely on foot. No personal vehicle required.

* Service radius: configurable 0.125 to 1 mile. Default 0.5 miles.
* Eligible mission tiers: Tier 1 only.
* Eligible Tier 1 examples: Door-closing, trash and litter cleanup inside the AV cabin, light visual diagnostics that do not require tools.
* Blocked: Anything requiring tools, anything requiring driving the AV, anything requiring exposure to live traffic.
* Equipment requirement: Minimum safety kit (vest, ID, phone, water).
* Notes: Niche loadout. Limited beta deployment in defined high-density zones (airport terminals, campuses, downtown entertainment districts). Should not be enabled in arbitrary suburban or highway-adjacent sectors.

## Dispatch logic

Service radius is **enforced at dispatch**. The system will only route a mission to an agent if:

1. The mission's AV location is within the agent's configured service radius from the agent's current GPS location, OR
2. The mission is the second-in-queue for that agent (the agent already has an active mission), in which case the eligibility radius is measured from the location of the FIRST mission's AV, not from the agent's current location.

Loadout mode also acts as a binary filter on tier eligibility. A foot-patrol agent will never see Tier 2 or Tier 3 missions in their queue. An e-bike agent will never see vehicle-takeover missions.

## Fee structure

Loadout mode does **NOT** affect the base mission fee. All loadouts on the same mission earn the same base fee.

The only loadout-relevant fee variation is surge pricing. If a mission falls inside an active surge zone at dispatch time, all eligible agents (regardless of loadout) earn the surge multiplier. Surge logic itself is an open design question and is not finalized in this document.

## SLA accountability

For the initial release, **SLA targets are tier-based, not loadout-based**:

* Tier 1: 15 minutes
* Tier 2: 20 minutes
* Tier 3: 25 minutes

The same target applies whether the agent is on foot, on a bike, or in a vehicle. This is intentional for the first deployment because we do not yet have data on how often each loadout actually meets these targets in real conditions. After the pilot, SLA tiering may be refined per-loadout based on observed arrival-time distributions.

## Safety considerations

Foot-patrol and e-bike agents responding to an AV in active traffic face a meaningfully higher injury risk than vehicle-based agents who can stay in their car until the scene is assessed. The Vanguard wearables (vest, helmet, HapHat) partially address this. Operations policy must add explicit rules:

* Foot-patrol and e-bike agents are not dispatched to missions where the AV is reported in a live traffic lane unless a vehicle-based agent backup is also dispatched.
* Foot-patrol agents are not dispatched to highway-adjacent sectors at all.
* In severe weather (Phoenix summer above 110°F, dust storm, lightning) foot-patrol availability is suspended automatically.

These rules belong in `docs/operations/AGENT_SAFETY.md` (a new doc to be created when this feature ships).

## Open questions

* Insurance: do foot-patrol and e-bike agents need a different liability tier than vehicle-based agents? Probably yes, but the specific premium delta needs underwriter consultation.
* Equipment certification: do we issue different equipment kits at onboarding based on loadout, or do agents purchase their own tier-appropriate gear? Affects unit economics.
* Hub geography: foot-patrol and e-bike viability assumes a deployment hub geographically close to the service area. Is the Mesa Hub well-suited to non-vehicle agents post-pilot, or do we need urban-core hubs first?

## Sequencing

Not for Mesa Pilot. Targets v2026.3 or v2026.4 release window, after pilot data confirms which loadouts the market actually supports. Initial post-pilot rollout would likely be:

1. Vehicle remains generally available (status quo).
2. E-bike and scooter open in a designated pilot sector (probably an urban core selected jointly with the lead fleet partner).
3. Foot patrol opens last, in airport, campus, and stadium sectors only.

## Related work

* Affects mobile app loadout-selection UI in `apps/mobile/pan_tactical/composeApp/`.
* Affects dispatch eligibility logic in `apps/backend/src/api/v2x_bounty_api.py`.
* Affects the surge-pricing module in `apps/backend/src/economics/dynamic_pricing.py`.
* Eventually requires updates to `docs/legal/COMPLIANCE.md` and `docs/operations/AGENT_SAFETY.md`.
