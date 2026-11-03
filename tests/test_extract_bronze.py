"""Unit tests for the pure functions in extract/extract_bronze.py."""

from extract_bronze import build_url


def test_build_url_returns_full_api_url():
    url = build_url("driverstandings", 2024)
    assert url == "https://api.jolpi.ca/ergast/f1/2024/driverstandings.json?limit=100"
