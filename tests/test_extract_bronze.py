"""Unit tests for the pure functions in extract/extract_bronze.py."""

from pathlib import Path

import pytest

from extract_bronze import build_url, build_path, check_complete


def test_build_url_returns_full_api_url():
    url = build_url("driverstandings", 2024)
    assert url == "https://api.jolpi.ca/ergast/f1/2024/driverstandings.json?limit=100"


def test_build_path_returns_full_bronze_path():
    path = build_path("driver_standings", 2024)
    assert path == Path("data/bronze/driver_standings/2024.json")


class FakeResponse:
    """Stands in for requests.Response with only what check_complete uses."""

    def __init__(self, payload: dict):
        self._payload = payload
        self.url = "https://fake.test/f1"

    def json(self):
        return self._payload


def test_check_complete_with_total_below_limit():
    response = FakeResponse({"MRData": {"total": "20", "limit": "100"}})
    check_complete(response)  # should not raise


def test_check_complete_for_total_above_limit_raises_value_error():
    response = FakeResponse({"MRData": {"total": "200", "limit": "100"}})
    with pytest.raises(ValueError):
        check_complete(response)


def test_check_complete_for_total_equal_to_limit():
    response = FakeResponse({"MRData": {"total": "100", "limit": "100"}})
    check_complete(response)  # should not raise