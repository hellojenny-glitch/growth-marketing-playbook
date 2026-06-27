# Growth Marketing Playbook

A working collection of frameworks, templates, swipe files, and tools I bring with me across teams and companies. Everything here is built to solve a real problem I've run into, not to demonstrate that I know how to do something. Use what's useful, adapt what's close, and ignore the rest.

## How this is organized

| Folder | What's in it |
|---|---|
| `01-frameworks/` | Strategic thinking: positioning, channel strategy, growth loops. Use these when you're deciding what to do. |
| `02-templates/` | Briefs, checklists, reporting structures. Use these when you're running something and don't want to start from a blank page. |
| `03-swipe-files/` | Real examples: email campaigns, landing pages, ad copy. Use these for inspiration or a starting draft. |
| `04-case-studies/` | Longer writeups of specific campaigns or decisions, including what worked, what didn't, and why. |
| `05-tools-and-scripts/` | Actual working tools: scripts, queries, and writeups built to solve specific technical problems. |

Each top-level folder has its own README with more detail on what's inside and how to use it.

## What's in tools-and-scripts right now

| Folder | What it is | When to use it |
|---|---|---|
| `utm-generator/` | Python script that generates standardized, validated UTM-tagged URLs and exports to CSV | When a team's UTM tagging is inconsistent or manual, and you want rules enforced by the system instead of a doc nobody reads |
| `sql-cohort-funnel/` | Two Snowflake queries: cohort retention and funnel conversion | Starting point for the two analyses almost every growth role eventually needs, adapt the table names to your schema |
| `no-code-to-code/` | Writeup of automating a UTM tracking spreadsheet that motivated the generator script | The "why" behind the build, useful if you're trying to make the case for automating a manual process on your own team |


### Setup

The UTM generator and its tests require Python 3.10+ and pytest:

```
cd 05-tools-and-scripts/utm-generator
pip install pytest
python -m pytest test_utm_generator.py -v
```

The SQL files are meant to be read and adapted, not run as-is. They assume a `users` and `events` table that won't exist in a fresh Snowflake account.

## Using this with a team

If you're on a team I'm working with and pulling from this repo: everything here is meant to be copied, forked, or adapted into your own workflows. If something's unclear or missing context, the case studies and writeups usually have the reasoning behind a choice, not just the artifact itself.
