"""Extract raw JSON from the Jolpica-F1 API into the bronze layer."""

BASE_URL = "https://api.jolpi.ca/ergast/f1"
LIMIT = 100

# bronze folder name -> API path
ENDPOINTS = {
    "driver_standings": "driverstandings",
    "constructor_standings": "constructorstandings",
    "race_winners": "results/1",
}


def build_url(endpoint_path: str, season: int) -> str:
    """Return the full API URL for one endpoint and season."""
    return f"{BASE_URL}/{season}/{endpoint_path}.json?limit={LIMIT}"


print(build_url("results/1", 2024))
