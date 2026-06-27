# UTM Parameter Generator

A small Python tool that solves a problem every growth marketer has run into:
UTM tags getting typed inconsistently across a team, breaking attribution in
GA4, HubSpot, or Klaviyo. One person tags `email`, another tags `e-mail` or
`Email`, and now your channel report has three rows that should be one.

This tool enforces a controlled vocabulary for `utm_source` and `utm_medium`,
auto-slugifies campaign names, catches duplicate links before they go out,
and exports everything to a clean CSV you can hand off to a team or import
into a tracking sheet.

## Why this exists

Before this, UTM tagging at most places I've worked happened in a shared
spreadsheet with a column for each parameter and a prayer that nobody
fat-fingers `Facebook` instead of `facebook`. That prayer doesn't get
answered often enough. This script makes the naming conventions
non-negotiable instead of aspirational.

## What it does

- Validates `utm_source` and `utm_medium` against an approved list (edit
  `VALID_SOURCES` / `VALID_MEDIUMS` in the script to match your org's taxonomy)
- Slugifies campaign, term, and content values automatically (`Q3 Email Blast!`
  becomes `q3-email-blast`)
- Preserves any existing query parameters on the base URL instead of
  clobbering them
- Warns when you're about to generate a duplicate tagged URL
- Exports a dated CSV with every link generated in the session

## Usage

Interactive mode:

```bash
python utm_generator.py
```

It'll prompt you for a base URL, source, medium, campaign, and optional
term/content, then loop until you press Enter on an empty URL. At the end it
writes a CSV.

As a module, for use inside a larger script or notebook:

```python
from utm_generator import build_utm_url, UTMBatch

url = build_utm_url(
    "https://example.com/spring-sale",
    source="klaviyo",
    medium="email",
    campaign="Spring Sale Reminder",
)
# -> https://example.com/spring-sale?utm_source=klaviyo&utm_medium=email&utm_campaign=spring-sale-reminder

batch = UTMBatch()
batch.add("https://example.com", "google", "cpc", "Brand Search")
batch.add("https://example.com/demo", "linkedin", "paid_social", "ABM Q3")
batch.to_csv("q3_links.csv")
```

## Tests

```bash
pip install pytest
python -m pytest test_utm_generator.py -v
```

10 tests covering slug normalization, vocabulary validation, query param
preservation, and CSV export.

## Extending this

A natural next step would be wiring this into a Google Sheets-backed
front end (so non-technical teammates can generate links without touching
Python), or adding a `--vocab-file` flag to load source/medium lists from
a shared YAML config instead of hardcoding them.
