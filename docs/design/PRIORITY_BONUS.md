# Design: Priority Bonus

**Status:** Design draft. Deferred until after Mesa Pilot.
**Owner:** Rob.
**Last updated:** 2026-04-24.

## Problem

Fleet partners value fast incident resolution differently. A premium AV operator (think: paid black-car AV service with riders aboard) loses real revenue every minute their car is stuck and may also be taking brand damage on social media. A scrappy startup AV operator with idle test fleet may not feel the same urgency. The current dispatch system treats all missions equally and pays all agents the same flat tier-based fee, which means the system has no mechanism for fleet partners to surface their own business urgency to the agents who can act on it.

We need a way for fleet partners to translate "this mission is more important to us than average" into "the agent who handles it earns more" — without creating the bad behaviors that come with making the bonus visible to agents in advance.

## Proposal

Introduce an optional Priority Bonus that the fleet manager configures per-mission or per-fleet. If a mission is completed within the configured target time, the agent receives the bonus on top of their normal fee.

**Critical design rule: the bonus is invisible to the agent at dispatch time and at accept time.** The agent learns about the bonus only after the mission is completed and the bonus has been awarded. It appears as a pleasant surprise notification, not as an advertised reward.

## Why hide the bonus

The instinct to advertise a bonus upfront is strong. It feels fair: tell the agent what they could earn, let them decide. We are deliberately not doing this. Three reasons:

* **Cream-skimming.** If agents see bonus amounts at accept time, they accept high-bonus missions and ignore low-bonus or zero-bonus missions. Fleet partners who pay no bonus suffer slower service. This is a known DoorDash failure mode in markets where tips are visible at accept time.
* **SLA gaming.** An agent who knows that arriving by minute 15 earns $9 versus arriving by minute 16 earns $0 has financial pressure to take risks in the final minute. We do not want to incentivize traffic-rule violations or unsafe driving for any reason.
* **Legal risk.** If the bonus is framed as "Speed Bonus" or "Rush Fee" and an agent is involved in an at-fault accident while attempting to earn it, the framing of the bonus may itself become evidence of negligent dispatch. Hiding the bonus and naming it "Priority Bonus" both reduce this risk.

The fleet partner still gets the value they want (more agents prioritizing fast response in aggregate, because agents who consistently respond fast earn consistently more). The agent still earns the bonus when they earn it. We just disconnect the dispatch decision from the per-mission bonus visibility.

## Preset structure

Fleet managers configure Priority Bonus per fleet (default) or per mission (override). The configuration UI offers four presets:

| Preset | Tier 1 (≤15 min) | Tier 2 (≤20 min) | Tier 3 (≤25 min) |
|---|---|---|---|
| OFF (default) | $0 | $0 | $0 |
| Balanced | $3 | $6 | $9 |
| Fastest | $5 | $10 | $15 |
| Custom | (any) | (any) | (any) |

The "Custom" preset is auto-selected if the manager modifies any individual tier value, regardless of which preset they started from. This includes:

* Turning the OFF preset on with a non-zero amount in any tier (auto-switch to Custom).
* Tweaking any value in Balanced (auto-switch to Custom).
* Tweaking any value in Fastest (auto-switch to Custom).

This rule prevents user confusion about which preset is "really" active when their values no longer match a named preset.

## Naming

The feature is named **Priority Bonus**. Rejected alternatives:

* **Commendation.** "Commendation" has formal meaning in military, law enforcement, and emergency services culture as a recognition of meritorious conduct, often symbolic rather than monetary, and typically attached to a specific incident. Vanguard agents are recruited heavily from veterans and first responders. They will read "Commendation" as the formal honor and find a generic time-based payout disrespectful or trivializing. We are reserving "Commendation" for a future non-monetary honor feature where a fleet manager or sector captain can award an agent for exceptional incident handling, displayed on the agent's profile.
* **Rush Fee.** Suggests the agent should rush. Legal exposure if an agent rushes unsafely.
* **Speed Bonus.** Same problem as Rush Fee, with bonus liability framing.
* **Response Bonus.** Acceptable alternative; close second choice.

Final choice: **Priority Bonus.** Captures fleet partner intent (this mission is a priority) without telling the agent how to behave.

## Eligibility and edge cases

* **Bonus is paid only on successful completion.** Cancelled, failed, or escalated missions do not earn the bonus.
* **Bonus is paid only if the target time is met.** Tier 1 mission at 14:59 earns the bonus. Tier 1 mission at 15:01 does not. The cutoff is hard.
* **Multi-stop or queued missions:** Each mission's bonus is independent. The clock resets when the next mission starts.
* **Surge pricing interaction:** Priority Bonus and surge multiplier stack. A mission in an active surge zone with Fastest priority bonus earns surge × base fee + priority bonus.
* **Veteran fee tier interaction:** Priority Bonus is paid on top of net payout. The Veteran (15%) vs. non-Veteran (25%) network fee is computed against the base fee only, not against the bonus. The bonus passes through 100% to the agent.
* **Fee math reconciliation:** When this feature ships, `docs/API_SPEC.md` and `docs/legal/COMPLIANCE.md` need to document the bonus passthrough explicitly so fleet partners and agents both understand what they are agreeing to.

## Notification flow

When a mission completes within target time and a Priority Bonus is owed:

1. Backend calculates final payout (base fee + surge if applicable + priority bonus).
2. Mission completion notification to the agent's mobile app shows the surprise: "Mission complete. You earned a $9 Priority Bonus."
3. Bonus appears in the agent's earnings ledger as a separate line item.
4. Fleet partner's invoice itemizes the bonus separately so they can see their bonus spend per period.

## What fleet managers see

Fleet managers should be able to see:

* Total Priority Bonus spend in a configurable time period.
* Number of missions where the bonus was paid out vs. missed.
* Average response time for missions with bonuses set vs. without.
* Aggregate pattern: "You spent $X on bonuses, which bought you Y minutes of average speed improvement." This helps fleet managers calibrate their bonus configuration over time.

This data lives in the fleet-facing dashboard (planned, currently in `apps/web/internal_dashboards/`).

## Open questions

* Should there be a hard cap on the highest tier amount in Custom? If a fleet manager sets the Tier 1 bonus to $500, does the system push back? Probably yes, but the cap and the warning UX needs design.
* Should fleet managers be able to set time-of-day or day-of-week bonus rules? (Higher bonus during morning rush, lower at 3am.) Probably a v2 of this feature.
* Should agents see aggregate bonus stats AFTER missions complete, even though they cannot see per-mission bonus before? "You earned $47 in Priority Bonuses this week." Probably yes; reinforces the surprise loop without enabling cream-skimming.

## Sequencing

Not for Mesa Pilot. Pilot launches with flat tier fees plus the Veteran fee tier and the Platform fee tier (5% / 10% with $25K escrow threshold). Priority Bonus is a v2026.3 or later feature.

## Related work

* Affects mission completion logic in `apps/backend/src/api/v2x_bounty_api.py::complete_mission`.
* Affects fleet-facing API in the partner dispatch surface.
* Requires fleet dashboard UI work in `apps/web/internal_dashboards/`.
* Requires agent app notification UX in `apps/mobile/pan_tactical/composeApp/`.
* Pairs well with: a future Commendation feature (non-monetary honor), and possibly a future tipping mechanism from individual riders to individual agents.
