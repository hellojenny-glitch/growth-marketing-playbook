# Clay AI Column 2: Slack Message Builder (Claude)

This is the second Claude column. It runs **after** the scoring column and
turns its JSON output into the actual Slack alert text. It only produces a
message for `slack_a` and `slack_b` routes; for `report` or `none` it
returns an empty string so nothing fires.

---

## Prompt

```
You format Slack alerts for an SDR team. Build the alert message from the
fields below. Follow the rules exactly. Do not invent any facts that are
not in the fields.

FIELDS
- Route: {{route}}
- Grade: {{grade}}
- Score: {{score}}
- Account: {{account}}
- Contact name: {{visitor_name}}
- Email: {{email}}
- SDR line: {{sdr_line}}
- Signal breakdown: {{breakdown}}

RULES
- If Route is "report" or "none", output an empty string. Write nothing
  else.
- If Route is "slack_a", build a GRADE A alert (call now).
- If Route is "slack_b", build a GRADE B alert (call this week).
- Use Slack markdown: bold with single asterisks, not double.
- Keep it to four short lines. No em-dashes. Do not use "not X, but Y"
  phrasing.
- If Email is blank, write "no email on file" in the contact line.
- Use the Signal breakdown text as the signals line as-is.

FORMAT FOR A GRADE A ALERT (fill the bracketed parts)
:rotating_light: GRADE A, CALL NOW
· [Account] (score [Score])
Contact: [Contact name] · [Email or "no email on file"]
Signals: [Signal breakdown]
Action: [SDR line]

FORMAT FOR A GRADE B ALERT (fill the bracketed parts)
:large_yellow_circle: GRADE B, CALL THIS WEEK
· [Account] (score [Score])
Contact: [Contact name] · [Email or "no email on file"]
Signals: [Signal breakdown]
Action: [SDR line]

OUTPUT
Output ONLY the finished message text (or an empty string for
report/none). No quotes, no code fences, no commentary.
```

## Wiring notes

- `{{route}}`, `{{grade}}`, `{{score}}`, `{{sdr_line}}`, `{{breakdown}}`
  come from the scoring column (see `01-scoring-prompt.md`). If Clay
  stored that column's output as one JSON blob, add small formula columns
  first to extract each key, then reference those columns here.
- `{{account}}`, `{{visitor_name}}`, `{{email}}` can come from either the
  scoring JSON or the original stitched columns, whichever is cleanly
  populated in your table.
- Channel routing is **not** decided in this prompt. This prompt only
  builds the message text. Clay's conditional Slack step decides *where*
  it goes: `slack_a` → priority channel or DM the owner; `slack_b` →
  weekly digest channel.
- Because `report`/`none` returns an empty string, this column is safe to
  run on every row. Only graded-for-outreach rows actually produce a
  message.

## Optional: DM the lead owner instead of a channel for A grades

If A-grade alerts should DM the HubSpot owner rather than post to a
channel, add the owner's Slack handle as a column, then have Clay's Slack
step target that handle when `route = slack_a` and the owner is an SDR
(not an AE). AE-owned accounts are already routed to `none`, so they're
excluded automatically.
