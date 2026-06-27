"""Tests for utm_generator.py. Run with: python -m pytest test_utm_generator.py -v"""

import pytest
from utm_generator import build_utm_url, slugify, validate_source, validate_medium, UTMBatch


def test_slugify_basic():
    assert slugify("Q3 Email Blast!") == "q3-email-blast"


def test_slugify_underscores_and_spaces():
    assert slugify("summer_sale 2026") == "summer-sale-2026"


def test_validate_source_accepts_known_value():
    assert validate_source("Google") == "google"


def test_validate_source_rejects_unknown_value():
    with pytest.raises(ValueError):
        validate_source("googel")  # common typo


def test_validate_medium_rejects_unknown_value():
    with pytest.raises(ValueError):
        validate_medium("e-mail")  # should be 'email'


def test_build_utm_url_basic():
    url = build_utm_url(
        "https://example.com/landing",
        source="newsletter",
        medium="email",
        campaign="Q3 Promo",
    )
    assert "utm_source=newsletter" in url
    assert "utm_medium=email" in url
    assert "utm_campaign=q3-promo" in url


def test_build_utm_url_preserves_existing_query_params():
    url = build_utm_url(
        "https://example.com/landing?ref=abc123",
        source="google",
        medium="cpc",
        campaign="brand",
    )
    assert "ref=abc123" in url
    assert "utm_source=google" in url


def test_build_utm_url_with_term_and_content():
    url = build_utm_url(
        "https://example.com",
        source="facebook",
        medium="paid_social",
        campaign="retargeting",
        term="lookalike audience",
        content="carousel ad v2",
    )
    assert "utm_term=lookalike-audience" in url
    assert "utm_content=carousel-ad-v2" in url


def test_batch_warns_on_duplicate(capsys):
    batch = UTMBatch()
    batch.add("https://example.com", "google", "cpc", "brand")
    batch.add("https://example.com", "google", "cpc", "brand")
    captured = capsys.readouterr()
    assert "Warning" in captured.out
    assert len(batch.links) == 2


def test_batch_to_csv_creates_file(tmp_path):
    batch = UTMBatch()
    batch.add("https://example.com", "linkedin", "social", "launch week")
    out_path = tmp_path / "test_output.csv"
    batch.to_csv(str(out_path))
    assert out_path.exists()
    content = out_path.read_text()
    assert "linkedin" in content
    assert "launch-week" in content
