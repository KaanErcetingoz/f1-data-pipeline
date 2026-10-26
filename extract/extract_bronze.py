"""Extract raw JSON from the Jolpica-F1 API into the bronze layer."""

from pathlib import Path

import requests

BASE_URL = "https://api.jolpi.ca/ergast/f1"
LIMIT = 100
TIMEOUT = 30  # seconds

BRONZE_PATH = Path("data/bronze")

# bronze folder name -> API path
ENDPOINTS = {
    "driver_standings": "driverstandings",
    "constructor_standings": "constructorstandings",
    "race_winners": "results/1",
}


def build_url(endpoint_path: str, season: int) -> str:
    """Return the full API URL for one endpoint and season."""
    return f"{BASE_URL}/{season}/{endpoint_path}.json?limit={LIMIT}"


def build_path(folder: str, season: int) -> Path:
    """Return the full path to the bronze file for one endpoint and season."""
    return BRONZE_PATH / folder / f"{season}.json"


def fetch_page(url: str) -> requests.Response:
    """Fetch one page from the API and fail on HTTP errors."""
    response = requests.get(url, timeout=TIMEOUT)
    response.raise_for_status()
    return response


def check_complete(response: requests.Response) -> None:
    """Raise an error if the page does not contain every record."""
    mr_data = response.json()["MRData"]
    total = int(mr_data["total"])
    limit = int(mr_data["limit"])
    if total > limit:
        raise ValueError(
            f"Incomplete data for {response.url}: total={total}, limit={limit}")


path = build_path("race_winners", 2024)
print(path)
print(path.exists())



