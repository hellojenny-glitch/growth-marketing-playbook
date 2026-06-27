"""
UTM Parameter Generator
========================
Generates standardized, validated UTM-tagged URLs in bulk and exports them
to CSV. Built to solve a real problem: marketers hand-typing UTMs in
spreadsheets, which leads to inconsistent casing, typos in source/medium
values, and broken attribution data downstream in GA4/HubSpot/Klaviyo.

This enforces a controlled vocabulary for source/medium, lowercases and
slugifies campaign names, warns on duplicate URLs, and outputs a clean CSV
ready to import into a tracking sheet or share with a team.

Usage:
    python utm_generator.py
    (interactive mode, prompts for each campaign)

    or import as a module:
    from utm_generator import build_utm_url, UTMBatch
"""

import csv
import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from urllib.parse import urlencode, urlparse, urlunparse, parse_qsl

# ---------------------------------------------------------------------------
# Controlled vocabulary. Edit these to match your org's naming conventions.
# Keeping this centralized is the whole point: it's the difference between
# UTMs that roll up cleanly in GA4 and UTMs that fragment into 40 variants
# of "email" / "Email" / "e-mail" / "newsletter".
# ---------------------------------------------------------------------------

VALID_SOURCES = {
    "google", "facebook", "instagram", "linkedin", "twitter", "tiktok",
    "newsletter", "klaviyo", "hubspot", "partner", "direct", "youtube",
    "reddit", "pinterest",
}

VALID_MEDIUMS = {
    "cpc", "social", "email", "organic_social", "affiliate", "referral",
    "display", "paid_social", "sms", "push",
}


@dataclass
class UTMLink:
    base_url: str
    source: str
    medium: str
    campaign: str
    term: str = ""
    content: str = ""
    full_url: str = field(init=False)

    def __post_init__(self):
        self.full_url = build_utm_url(
            self.base_url, self.source, self.medium,
            self.campaign, self.term, self.content,
        )


def slugify(value: str) -> str:
    """Lowercase, strip punctuation, replace spaces/underscores with hyphens.
    Keeps campaign naming consistent: 'Q3 Email Blast!' -> 'q3-email-blast'
    """
    value = value.strip().lower()
    value = re.sub(r"[^\w\s-]", "", value)
    value = re.sub(r"[\s_]+", "-", value)
    return value.strip("-")


def validate_source(source: str) -> str:
    s = source.strip().lower()
    if s not in VALID_SOURCES:
        raise ValueError(
            f"'{source}' is not an approved utm_source. "
            f"Approved values: {', '.join(sorted(VALID_SOURCES))}"
        )
    return s


def validate_medium(medium: str) -> str:
    m = medium.strip().lower()
    if m not in VALID_MEDIUMS:
        raise ValueError(
            f"'{medium}' is not an approved utm_medium. "
            f"Approved values: {', '.join(sorted(VALID_MEDIUMS))}"
        )
    return m


def build_utm_url(base_url: str, source: str, medium: str, campaign: str,
                   term: str = "", content: str = "") -> str:
    """Builds a UTM-tagged URL, preserving any existing query params on
    base_url and merging UTM params in cleanly rather than double-appending.
    """
    source = validate_source(source)
    medium = validate_medium(medium)
    campaign = slugify(campaign)

    parsed = urlparse(base_url)
    existing_params = dict(parse_qsl(parsed.query))

    utm_params = {
        "utm_source": source,
        "utm_medium": medium,
        "utm_campaign": campaign,
    }
    if term:
        utm_params["utm_term"] = slugify(term)
    if content:
        utm_params["utm_content"] = slugify(content)

    existing_params.update(utm_params)
    new_query = urlencode(existing_params)

    return urlunparse((
        parsed.scheme or "https",
        parsed.netloc,
        parsed.path,
        parsed.params,
        new_query,
        parsed.fragment,
    ))


class UTMBatch:
    """Collects multiple UTM links, checks for duplicates, and exports to CSV."""

    def __init__(self):
        self.links: list[UTMLink] = []

    def add(self, base_url: str, source: str, medium: str, campaign: str,
            term: str = "", content: str = "") -> UTMLink:
        link = UTMLink(base_url, source, medium, campaign, term, content)
        duplicate = next((l for l in self.links if l.full_url == link.full_url), None)
        if duplicate:
            print(f"  Warning: this combination already exists -> {link.full_url}")
        self.links.append(link)
        return link

    def to_csv(self, filepath: str = None) -> str:
        if filepath is None:
            filepath = f"utm_links_{date.today().isoformat()}.csv"
        with open(filepath, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "base_url", "source", "medium", "campaign",
                "term", "content", "full_url",
            ])
            for link in self.links:
                writer.writerow([
                    link.base_url, link.source, link.medium, link.campaign,
                    link.term, link.content, link.full_url,
                ])
        return filepath


def interactive_session():
    print("UTM Generator — press Enter on 'base URL' with nothing typed to finish.\n")
    batch = UTMBatch()

    while True:
        base_url = input("Base URL: ").strip()
        if not base_url:
            break
        try:
            source = input(f"Source ({'/'.join(sorted(VALID_SOURCES))}): ").strip()
            medium = input(f"Medium ({'/'.join(sorted(VALID_MEDIUMS))}): ").strip()
            campaign = input("Campaign name: ").strip()
            term = input("Term (optional, Enter to skip): ").strip()
            content = input("Content (optional, Enter to skip): ").strip()
            link = batch.add(base_url, source, medium, campaign, term, content)
            print(f"  -> {link.full_url}\n")
        except ValueError as e:
            print(f"  Error: {e}\n")
            continue

    if batch.links:
        path = batch.to_csv()
        print(f"\nSaved {len(batch.links)} link(s) to {path}")
    else:
        print("\nNo links generated.")


if __name__ == "__main__":
    interactive_session()
