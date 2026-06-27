# From Spreadsheet to Script: Automating UTM Tracking

## The problem, in its original form

For about a year, our UTM tracking lived in a Google Sheet. One tab per
quarter, one row per campaign link. The process for adding a new tracked
link looked like this:

1. Copy the row above
2. Manually overwrite `utm_campaign`, sometimes remembering to lowercase it
3. Eyeball `utm_source` and `utm_medium` against a list of "approved" values
   that lived in a different tab, which people opened maybe half the time
4. Concatenate the columns into a URL using a formula that someone had
   written two years earlier and nobody fully understood anymore
5. Paste the resulting URL somewhere else to actually use it

This worked, in the sense that links got made. It did not work in the sense
that mattered: by the time we pulled a GA4 channel report each quarter, we
routinely found `email`, `Email`, and `e-mail` as three separate rows,
`q3_promo` and `Q3 Promo` splitting the same campaign's traffic in two, and
at least one link per quarter missing a UTM entirely because someone typed
the destination URL directly into a calendar tool instead of going through
the sheet.

None of this was anyone being careless. It's just what happens when the
thing enforcing your naming convention is a second tab that people have to
remember to check, rather than something that simply won't let the
inconsistency happen.

## Why I automated it

The actual fix isn't clever, it's removing the step where a human has to
remember a rule. Once I framed it that way, the rest was just deciding what
the rules should be and writing them down as code instead of as a tab people
might skip.

## What changed

I wrote a small Python script (in
[`../utm-generator`](../utm-generator)) that:

- Holds the approved `utm_source` and `utm_medium` values as actual
  constants, so a typo throws an error instead of silently creating a new
  category in next quarter's report
- Lowercases and slugifies campaign names automatically, so `Q3 Email
  Blast!` becomes `q3-email-blast` no matter who typed it
- Builds the full URL with proper query-string handling, so it doesn't break
  when a base URL already has its own query parameters (the old sheet
  formula did break on this, more than once)
- Flags duplicate links before they go out, instead of us finding out a
  campaign's traffic was split across two near-identical URLs after the
  fact
- Exports a clean CSV at the end, which is the one part of the old workflow
  worth keeping. People still wanted something they could open and skim.

## What this actually changed downstream

The direct effect was fewer broken reports. The more interesting effect was
on attribution trust. Before this, when channel numbers looked off, the
first instinct was to question the tracking before questioning the strategy.
After standardizing tagging, a weird number in a report was much more likely
to reflect something real happening in the business, which is the entire
point of tracking in the first place.

## The honest caveat

This didn't fix everything. Someone can still paste a destination URL
straight into an email tool without running it through the script, and
nothing stops that today. The realistic next step is wrapping this in a
lightweight Sheets sidebar or a Slack shortcut, something with near-zero
friction sitting where people already are, since "open a terminal and run a
Python script" is not a workflow most of a marketing team will adopt without
a push. The validation logic doesn't have to change, just where the rules
get enforced.

## Takeaway

Most no-code-to-code transitions aren't really about learning to write
loops or functions. They're about noticing where a process depends on a
human remembering something, and moving that dependency into a place where
forgetting isn't an option.
