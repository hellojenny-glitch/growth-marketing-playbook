# Clay Column 3: Send Message to Slack

This is the third column. It takes the message text from
`02-slack-message-prompt.md` and delivers it to Slack. No AI call here,
just Clay's native Slack action wired to a run condition. Slack and Clay
must be connected as apps inside Clay before this step will work.

## How to wire it in Clay

1. Confirm the scoring column (`01-scoring-prompt.md`, call it
   **"Scoring JSON"** in your table) runs first and outputs the full JSON
   object: `score`, `grade`, `route`, `action`, `sdr_line`, `breakdown`.
2. Confirm the message-builder column (`02-slack-message-prompt.md`) runs
   second and outputs the finished message text (or an empty string).
3. Add Clay's native **Slack** action as the third column.
4. Set the message body to reference the output of the message-builder
   column.
5. Make the Slack action **conditional**, so it only fires when there's
   actually something to send:
   - Check **Add Run Condition**
   - Condition: only run when `{{ Grade }}` is `A` or `B`
   - Reference column input:
     `["slack_a","slack_b"].includes({{Claude AI | JSON Output}}?.route)`

This keeps the Slack action from firing on every row. `report` and `none`
rows produce an empty message and a false run condition, so they sit
quietly and don't ping anyone.

## Routing behavior, end to end

- **Grade A, hot lead** → routes to the Hot Leads Slack channel
- **Grade A, but already owned by an AE** → no message in the Hot Leads
  channel. Instead, the owning AE gets an individual DM that their
  prospect is on the site (see the optional DM setup below)
- **Customer** → doesn't route at all. The suppressor in the scoring
  column already zeroes this out before it gets here

## Optional: DM the lead owner instead of a channel for A grades

If A-grade alerts should go straight to the HubSpot owner instead of a
shared channel, add the owner's Slack handle as its own column in the Clay
table, then point the Slack action at that handle whenever `route =
slack_a` and the listed owner is an SDR. AE-owned accounts never reach
this branch since they're already routed to `none` by the scoring column.
