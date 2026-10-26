# f1-data-pipeline

An end-to-end data pipeline for 20 seasons of Formula 1 history: raw API data in, analysis-ready tables and a dashboard out. Built **local-first** at zero cost, with an optional move to Google Cloud at the end.

```
Jolpica-F1 API ──► bronze (raw JSON) ──► DuckDB ──► dbt silver ──► dbt gold ──► dashboard
```

---

## Goal

Build a production-style pipeline from scratch, covering extraction, storage, transformation, testing, orchestration and visualisation, using the same patterns a cloud data platform would use. The extraction layer is written by hand (no FastF1 wrapper) so every request, check and file is under control.

## Questions the dashboard answers

1. **Championship standings:** driver and constructor standings for every season from 2006 to 2025 (2026 added after the season ends).
2. **Classic circuits:** driver and constructor win counts at four historic Grands Prix from 2006 to 2026: **Britain**, **Belgium (Spa)**, **Japan** and **Italy (Monza)**.
3. **Era comparison:** the V8 era (2006–2013) against the hybrid era (2014+), measured as **% of the maximum possible points** rather than raw points.

## Scope

| | |
|---|---|
| **Source** | [Jolpica-F1 API](https://github.com/jolpica/jolpica-f1), the open successor to the Ergast API (free, no key) |
| **Seasons** | 2006–2025 |
| **Requests** | ~60 in total (3 endpoints × 20 seasons), one page each |

| Data | Endpoint | Bronze folder |
|---|---|---|
| Driver standings | `/{season}/driverstandings.json` | `driver_standings` |
| Constructor standings | `/{season}/constructorstandings.json` | `constructor_standings` |
| Race winners | `/{season}/results/1.json` | `race_winners` |

## Architecture

The project follows the **medallion architecture**:

| Layer | Where | What it holds |
|---|---|---|
| **Bronze** | `data/bronze/<endpoint>/<season>.json` | Raw API responses, saved byte for byte and never modified |
| **Silver** | DuckDB, dbt staging models | Flattened, typed, `snake_case` tables |
| **Gold** | DuckDB, dbt marts | Tables that answer the three questions directly |

Because bronze is immutable, silver and gold can always be rebuilt from scratch without calling the API again.

## Key design decisions

- **Fail loudly on incomplete data.** Every request uses `limit=100`. If the response reports `total > limit`, the extractor stops with an error instead of saving a partial season. The check uses the `limit` the server actually applied, not the one requested.
- **Idempotent extraction.** Files that already exist are never downloaded again, so the extractor can be re-run safely and stays well under the API rate limit (4 req/s burst, 500 req/h).
- **Japan is filtered by country, not circuit.** The Japanese GP was held at Fuji in 2007–2008 and at Suzuka otherwise. Filtering by circuit would silently drop two seasons.
- **Fair era comparison.** The points system changed in 2010 (a win went from 10 to 25 points), sprint races award points from 2021, and a fastest-lap bonus existed from 2019 to 2024. Raw points are not comparable across eras, so the comparison uses each driver's share of the maximum points available that season.
- **Data quirks handled in silver.** The API returns every number as a string, a driver's `permanentNumber` reflects their *current* number rather than the one used that season, and a driver can appear under two constructors in one season.

## Tech stack

| Area | Tool | Status |
|---|---|---|
| Language & environment | Python 3.12, [uv](https://github.com/astral-sh/uv) | ✅ |
| Extraction | `requests` | ✅ |
| Storage & query engine | DuckDB | Planned |
| Transformation & tests | dbt (`dbt-duckdb`) | Planned |
| Dashboard | Streamlit or Evidence | Planned |
| Orchestration | Apache Airflow (Docker) | Planned |
| Cloud (optional) | GCS, BigQuery, Looker Studio | Planned |

## How to run

Requires [uv](https://github.com/astral-sh/uv).

```bash
git clone https://github.com/KaanErcetingoz/f1-data-pipeline.git
cd f1-data-pipeline
uv sync
uv run python extract/extract_bronze.py
```

The extractor downloads 60 files (3 endpoints × 20 seasons) into `data/bronze/` in about 30 seconds. Running it again skips every file that already exists and makes no API calls:

```
downloaded  data/bronze/driver_standings/2006.json
...
skipped     data/bronze/race_winners/2025.json
```

## Project structure

```
f1-data-pipeline/
├── extract/        # Python extractor: Jolpica API → bronze JSON files
├── data/           # Local data, not committed
│   ├── bronze/     #   raw API responses
│   ├── silver/
│   └── gold/
├── dbt/            # dbt project: silver (staging) and gold (marts) models
├── dags/           # Airflow DAGs
└── notebooks/      # Exploration and setup checks
```

## Status

🚧 **Loading bronze into DuckDB.**

- [x] Explore the API and define scope
- [x] Extract → bronze (Python): 60 raw JSON files, idempotent re-runs
- [ ] Load bronze → DuckDB
- [ ] dbt: silver + gold, with tests
- [ ] Dashboard
- [ ] Orchestration with Airflow
- [ ] Optional: migrate to Google Cloud

## License

[MIT](LICENSE)
