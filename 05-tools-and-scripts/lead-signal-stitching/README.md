# Lead Signal Stitching

Stitches three disconnected buying signals (RB2B site visits, HubSpot CRM
context, 6sense intent data) into one ranked, actionable lead list,
delivered to an SDR in Slack the moment a high-intent buyer lands on the
site.

**Stack:** RB2B (trigger) → Clay (stitch + enrich) → Claude (score, grade,
route) → Slack (deliver)

## The problem this solves

These three tools each see part of the picture and none of them sees the
whole thing:

- RB2B knows who's on the site right now, with no CRM context
- HubSpot knows the account's history, but is blind to live behavior
- 6sense knows account-level intent, but not the specific person

Without something stitching these together, hot leads sit unworked, SDRs
occasionally cold-prospect existing customers, and every lead gets roughly
equal attention regardless of how ready to buy they actually are.

## How it works

1. A visitor lands on the site and RB2B fires a webhook.
2. Clay does an immediate HubSpot lookup on domain. If the account is an
   existing customer or has an open deal owned by an AE, it's suppressed
   before anything reaches an SDR.
3. Clay stitches the RB2B record with 6sense intent data, joined on
   domain (never on company name, since name formatting is inconsistent
   across tools, e.g. "Apex Mfg" vs. "Apex Manufacturing").
4. Claude scores the stitched record against a deterministic, additive
   rubric, applies suppression rules, assigns a grade (A/B/C), and writes
   a one-sentence action for the SDR.
5. Slack delivers Grade A leads to a priority channel for same-day
   outreach, and Grade B leads to a weekly digest. Grade C and suppressed
   accounts generate no alert at all.

See [`ARCHITECTURE.md`](ARCHITECTURE.md) for the full system diagram and
rollout plan.

## What's in this folder

| File | What it's for |
|---|---|
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | System overview, execution order, rollout plan |
| [`01-scoring-prompt.md`](01-scoring-prompt.md) | Claude column 1: scores the stitched record, assigns grade and route |
| [`02-slack-message-prompt.md`](02-slack-message-prompt.md) | Claude column 2: formats the Slack alert text from the scoring output |
| [`03-slack-delivery-setup.md`](03-slack-delivery-setup.md) | Clay's Slack action: how it's wired and conditioned to only fire on A/B routes |
| [`rubric-reference.md`](rubric-reference.md) | The scoring rubric on its own, for quick lookup when tuning weights |

## Validated on sample data

Run on 7 deliberately messy sample visitors before going anywhere near
production data, this caught exactly the failure modes you'd expect a
naive version of this to miss:

- **Mismatched company names handled correctly** because the join key is
  domain, never name
- **An existing customer browsing pricing was suppressed**, not pitched
  (the -60 point penalty plus the routing override both catch this)
- **A strong lead already owned by an AE was correctly flagged** as not
  the SDR's to work, rather than getting double-prospected
- **Net-new visitors with no 6sense profile were still graded** on
  whatever signal was actually present, instead of erroring out on
  missing data

Result on that sample: 2 accounts graded A (call today), 1 graded B (the
one B was an AE-owned account, correctly held from outreach rather than
routed to an SDR), and 4 deprioritized to C.

## Why this is worth building this way

No-code plumbing (Clay) plus one transparent, editable rubric (a single
prompt) means this can be validated in days, not quarters. There's no
data pipeline to provision and no model to train. If marketing or RevOps
wants to change how much a signal is worth, they edit one block in
`01-scoring-prompt.md` and every future score reflects it automatically.

## Suggested rollout

Don't point this straight at a live SDR channel. Backtest the rubric
against past leads with known outcomes first, then run it in shadow mode
for a week (scoring and grading real traffic, but routing to a private
channel instead of the live one) so a human can sanity-check the calls
before SDRs start relying on them.

## Caveats / honest limitations

- This is a rules-based rubric, not a learned model. It's deterministic
  and auditable (every grade traces back to a `breakdown` of exactly which
  signals contributed), but it won't adapt on its own as buying patterns
  shift. Revisit the weights periodically.
- The suppression logic depends on HubSpot's `lifecycle_stage` and
  `owner` fields being reasonably clean. If those fields are stale or
  inconsistently formatted (e.g. owner names not actually containing
  "(AE)"), the suppression checks will miss cases they're meant to catch.
- This only handles the score-and-route decision. The lookups themselves
  (does this domain exist in HubSpot, what's its 6sense intent score) are
  Clay's job, not something the prompt can verify or correct.
