# Growth Marketing Portfolio

A working collection of the technical side of growth marketing: scripts,
queries, and writeups built to solve real problems rather than to
demonstrate syntax. See below for a TOC of what's in this portfolio.

## Projects

| Folder | What it is | Why it's here |
|---|---|---|
| [`utm-generator/`](utm-generator) | Python script that generates standardized, validated UTM-tagged URLs and exports to CSV | Teams can turn a messy manual process into something with enforced rules, plus actual tests |
| [`sql-cohort-funnel/`](sql-cohort-funnel) | Two Snowflake queries: cohort retention and funnel conversion | Shows SQL fluency on the two analyses every growth role eventually needs |
| [`no-code-to-code/`](no-code-to-code) | Writeup of automating the UTM tracking spreadsheet that motivated the generator script | Shows the "why" behind the build, not just the "what" |

## How these connect

These aren't three unrelated exercises. The UTM generator exists because of
a real, specific spreadsheet problem, described in the no-code-to-code
writeup. The SQL queries are a separate skill (data analysis vs.
tooling), but the underlying instinct is the same across all three: don't
trust a process to work just because a human is supposed to follow a rule,
build the rule into the system instead.

## What's next

Planned additions: an API integration project pulling from Klaviyo/HubSpot
into a Streamlit dashboard, and an A/B test significance-testing notebook.
Both build on the SQL and Python foundation here.

## Setup

Each project folder has its own README with specific run instructions. The
UTM generator and its tests require Python 3.10+ and `pytest`:

```bash
cd utm-generator
pip install pytest
python -m pytest test_utm_generator.py -v
```

The SQL files are meant to be read and adapted, not run as-is. They assume a
`users` and `events` table that won't exist in a fresh Snowflake account.
