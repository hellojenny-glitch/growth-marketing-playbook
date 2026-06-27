# Scoring Rubric Reference

A quick-lookup version of the scoring logic in `01-scoring-prompt.md`, for
tuning weights without reading the full prompt each time. If you change a
value here, update the matching value inside the prompt itself, since the
prompt is the source of truth that Claude actually reads.

## Additive points

| Signal | Source | Condition | Points |
|---|---|---|---|
| Website visits | RB2B `visits_7d` | 4 or more in 7 days | +30 |
| | | 2 to 3 in 7 days | +18 |
| | | Fewer than 2 | +6 |
| | | Field missing | +0 |
| High-intent pages | RB2B `pages_viewed` | Contains "pricing", "demo", or "integrations" (case-insensitive substring match) | +20 |
| Buying stage | 6sense `buying_stage` | "Decision" or "Purchase" | +30 |
| | | "Consideration" | +18 |
| | | Any other non-empty stage | +4 |
| | | Missing | +0 |
| Intent score | 6sense `intent_score` | 80 or higher | +10 |
| | | Below 80 / missing | +0 |
| Profile fit | 6sense `profile_fit` | "Strong" | +8 |
| | | Anything else / missing | +0 |
| Lifecycle stage | HubSpot `lifecycle_stage` | "MQL" or "SQL" | +15 |
| | | "Lead" | +6 |
| | | "Subscriber" or anything else | +0 |

## Suppressors (applied after additive scoring)

| Condition | Points |
|---|---|
| `lifecycle_stage` is "Customer" | -60 |
| `open_deals` > 0 AND owner contains "(AE)" | -25 |

## Grade thresholds

| Total score | Grade |
|---|---|
| 70 or higher | A |
| 40 to 69 | B |
| Below 40 | C |

## Routing overrides

Evaluated **in this order**. The first match wins and sets both `action`
and `route`, regardless of what grade the math produced.

| Order | Condition | Action | Route |
|---|---|---|---|
| 1 | Existing customer | Suppress, do not outreach. Route expansion to CSM. | `none` |
| 2 | Open deal owned by an AE | AE-owned, do not outreach. Leave with the AE. | `none` |
| 3 | No contact email (no RB2B email and no HubSpot email) | No contact, needs enrichment before outreach. | `report` |
| 4 | Grade A | Call today. Personalized outreach within 24h. | `slack_a` |
| 5 | Grade B | Call this week after the A accounts. | `slack_b` |
| 6 | Grade C | Nurture; revisit if activity increases. | `report` |

Note that the suppressors and overrides mean a numerically high score
doesn't guarantee an SDR alert. An account can score 95 points on
engagement and intent, then still route to `none` because it's an existing
customer or an AE-owned deal. The overrides exist specifically to catch
that case, since the additive rubric alone has no way to know about
account ownership.

## Tuning guidance

- **If too many B's feel like they should be A's**, lower the A threshold
  or raise point values for the signals you trust most (visits, buying
  stage).
- **If SDRs are getting pinged on noise**, raise thresholds rather than
  removing signals, since removing a signal also removes it from the
  audit trail in `breakdown`.
- **Always change weights in the prompt, not just in this table.** This
  file is documentation; the prompt is what Claude actually executes.
