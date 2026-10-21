"""Extract raw JSON from the Jolpica-F1 API into the bronze layer."""

import requests

BASE_URL = "https://api.jolpi.ca/ergast/f1"
LIMIT = 100
TIMEOUT = 30  # seconds

# bronze folder name -> API path
ENDPOINTS = {
    "driver_standings": "driverstandings",
    "constructor_standings": "constructorstandings",
    "race_winners": "results/1",
}


def build_url(endpoint_path: str, season: int) -> str:
    """Return the full API URL for one endpoint and season."""
    return f"{BASE_URL}/{season}/{endpoint_path}.json?limit={LIMIT}"


def fetch_page(url: str) -> requests.Response:
    """Fetch one page from the API and fail on HTTP errors."""
    response = requests.get(url, timeout=TIMEOUT)
    response.raise_for_status()
    return response

# response = fetch_page(build_url("asdf", 2024)) wrong endpoint test
response = fetch_page(build_url("results/1", 2024))
print(response.status_code, len(response.text))
