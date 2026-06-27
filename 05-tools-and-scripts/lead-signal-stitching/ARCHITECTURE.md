# Architecture

## The problem

The best buying signals for an SDR team usually live in three tools that
don't talk to each other:

- **RB2B** sees who's on the site right now, with no CRM context or deal
  stage attached to that visit.
- **HubSpot** knows the account's history (lifecycle stage, owner, open
  deals) but is blind to live, on-site behavior.
- **6sense** knows account-level buying intent but not the exact person
  behind it.

Looked at separately, each tool has a blind spot that causes real damage:
hot leads sit unworked because no one connects the dots in time, SDRs
cold-prospect accounts that are already paying customers because they
never checked CRM context, and reps spread effort evenly across leads
because there's no way to tell a ready-to-buy visitor from idle traffic.

## The fix: stitch on domain, then score and act

Domain is the one key all three tools share. A visitor's domain ties their
live RB2B session to their HubSpot account record and their 6sense intent
profile, even when the company name is formatted differently across
systems (`"Apex Mfg"` in one tool, `"Apex Manufacturing"` in another).
Joining on domain instead of name avoids that whole class of bug.

```
RB2B webhook          Clay                    Claude                 Slack
(visitor lands,   →   (stitches +        →    (scores, grades,   →   (A/B alerts
 fires trigger)        enriches the            writes action,         to reps)
                        3 sources)              applies routing)
```

**Clay** is the no-code plumbing layer: it receives the RB2B webhook,
looks up the domain in HubSpot and 6sense, and assembles one merged
record.

**Claude** is the scoring and action layer, not an optional add-on. It
applies a deterministic point rubric, computes a grade, applies
suppression rules (don't pitch existing customers, don't poach AE-owned
deals), and writes the Slack-ready output.

**Slack** is the delivery layer. Only Grade A and Grade B accounts ever
generate a message. Grade C and suppressed accounts stay quiet, so SDRs
never have to sift signal from noise.

## Tiered execution order

```
Trigger                          Tier 1 — instant safety gate (seconds)
RB2B webhook            splits   HubSpot live lookup on domain
Visitor lands, fires now  →      Customer? AE deal? Suppress before any alert

Tier 2 — enrichment (seconds to minutes)
Clay stitches RB2B + HubSpot + 6sense, enriches the record
6sense intent snapshot added; missing fields handled gracefully

                    ↓
        Claude scores, grades, writes action
        Applies rubric + routing overrides
                    ↓
        ┌───────────┼───────────┐
   Slack: A      Slack: B    Report: C / held
   Call now      Digest,     No alert
                 this week
```

The HubSpot suppression check runs early and fast, before the more
expensive 6sense enrichment, so a known customer or AE-owned account never
even gets scored, let alone alerted on.

## Why this is worth doing now

This is no-code plumbing (Clay) plus a transparent, editable rubric (the
prompt). That combination means it can be validated in days, not
quarters. There's no data pipeline to provision and no model to train,
just a webhook, three lookups, one prompt, and a Slack action.

## Suggested rollout

1. **Backtest** the rubric against past leads with known outcomes
   (closed-won, closed-lost, never converted) to sanity-check the point
   weights before anyone relies on it.
2. **Run in shadow mode** for a week: let it score and grade real traffic,
   but route everything to a private channel instead of the live SDR
   channel, so a human can compare the system's calls against what
   actually happened.
3. **Turn on live routing** once shadow mode results look right, starting
   with Grade A only, then adding Grade B once the team trusts the
   signal.

## Who uses what

| Role | What they get |
|---|---|
| SDRs | Graded, ranked leads in Slack. Work the A's first, B's after. |
| Marketing / RevOps | Own the rubric. Tuning a weight means editing one block in the scoring prompt; grades and routing recompute automatically on the next run. |
| Sales leadership | Visibility into which live signals actually predict conversion, since `breakdown` shows the exact point sources behind every grade. |

## Files in this folder

- `01-scoring-prompt.md` — the Claude column that scores, grades, and
  decides routing
- `02-slack-message-prompt.md` — the Claude column that formats the Slack
  alert text
- `03-slack-delivery-setup.md` — how the Slack send step is wired and
  conditioned in Clay
- `rubric-reference.md` — the scoring rubric on its own, for quick lookup
  and tuning without digging through the full prompts
