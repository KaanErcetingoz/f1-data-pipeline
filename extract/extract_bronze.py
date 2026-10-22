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

def check_complete(response: requests.Response) -> None:
    """Raise an error if the page does not contain every record."""
    mr_data = response.json()["MRData"]
    total = int(mr_data["total"])
    limit = int(mr_data["limit"])
    if total > limit:
        raise ValueError(f"Incomplete data for {response.url}: total={total}, limit={limit}")


# Happy path: total=24, limit=100 -> no error
response = fetch_page(build_url("results/1", 2024))
check_complete(response)
print("OK:", response.url)

# Failure path: force limit=10 -> must raise ValueError
small_page = fetch_page(f"{BASE_URL}/2024/results/1.json?limit=10")
check_complete(small_page)

