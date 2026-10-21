# F1 Data Pipeline — Progress

> The brain of this project. Read this first in every session.
> Tasks are ticked `[x]` and **Where are we?** is updated as soon as a step is done.

---

## 📍 Where are we?

| | |
|---|---|
| **Phase** | 2 — Extract → bronze |
| 👉 **Now** | Check: `total <= limit`, otherwise raise an error |
| ⏭️ **Next** | Skip the request if the file already exists (no re-downloads) |
| 🕒 **Last updated** | 2026-10-21 |

### Overview

| Phase | | Progress |
|---|---|---|
| 0 — Setup | ✅ Done | 9 / 9 |
| 1 — Explore the API and define scope | 🟡 Almost done (README left) | 6 / 7 |
| **2 — Extract → bronze** | 👉 **In progress** | **4 / 11** |
| 3 — Load bronze → DuckDB | ⬜ Not started | 0 / 3 |
| 4 — dbt: silver + gold | ⬜ Not started | 0 / 7 |
| 5 — Dashboard | ⬜ Not started | 0 / 3 |
| 6 — Orchestration | ⬜ Not started | 0 / 3 |
| 7 — Cloud migration (optional) | ⬜ Not started | 0 / 5 |

---

## Project goal

An end-to-end F1 data pipeline, built **local-first** (free) and optionally moved to Google Cloud at the end.

**Questions the dashboard must answer**

1. Driver and constructor championship standings, 2006–2025 (2026 added after the season ends)
2. Driver and constructor win counts at four Grands Prix, 2006–2026: Britain, Belgium (Spa), Japan, Italy (Monza)
3. Era comparison: V8 era (2006–2013) vs hybrid era (2014+), using **% of maximum possible points** rather than raw points

---

## Design decisions

| Decision | Choice | Why |
|---|---|---|
| Approach | Local first, cloud later (Option C) | €0 cost; the skills transfer directly to the cloud |
| Data source | Jolpica-F1 API (`https://api.jolpi.ca/ergast/f1/`) | Free, no API key, successor to Ergast |
| No FastF1 library | Write the extraction ourselves | Extraction is the skill being learned |
| Architecture | Medallion: bronze → silver → gold | Industry standard |
| Bronze | Raw JSON files, never modified | Can always rebuild silver/gold from bronze |
| Silver | Cleaned, flattened, typed tables in DuckDB (dbt staging) | |
| Gold | Tables that answer the questions (dbt marts) | |
| Bronze layout | Option A: `data/bronze/<endpoint_folder>/<season>.json` | Every season fits in one page with `limit=100` |
| Bronze folder names | `driver_standings`, `constructor_standings`, `race_winners` | Describe the content, not the URL; `constructor` matches the API's terms; `race_winners` avoids a clash with a future `race_results` |
| Extractor flow | Outer loop: endpoint, inner loop: season. Per item: skip if file exists (no pause) → request with timeout → stop on HTTP error → stop if `total > limit` → mkdir + save raw response text → log → pause | Pause only after real requests; saving raw text keeps bronze truly unchanged |
| Page size | Always `limit=100` | Fewest requests, stays well under rate limits |
| Fail loudly | If `total > limit`, stop with an error | Never continue silently with incomplete data |
| Japan | Filter by **country**, not circuit | Covers both Suzuka and Fuji (2007–2008) |
| Points comparison | % of maximum possible points; pre-2010 points system shown separately, not compared directly | Points system changed in 2010; sprints added in 2021 |
| Naming | `snake_case` for folders, files, columns | Consistent and readable |
| Language | Code, comments, docs and commits in English | Portfolio |

---

## Endpoints

| Data | Endpoint | Bronze folder | Requests (2006–2025) |
|---|---|---|---|
| Driver standings | `/{season}/driverstandings.json` | `driver_standings` | 20 |
| Constructor standings | `/{season}/constructorstandings.json` | `constructor_standings` | 20 |
| Race winners (incl. circuit and country) | `/{season}/results/1.json` | `race_winners` | 20 |

**Rate limits:** 4 requests/second burst, 500 requests/hour sustained. Total needed: ~60 requests.

---

## Data findings (things to handle later)

- [ ] `permanentNumber` reflects the driver's **current** number, not the number in that season (e.g. 2024 data shows Norris = 1, Verstappen = 3). This is a slowly changing dimension.
- [ ] All numbers arrive as **strings** (`"points": "437"`), so cast them in silver.
- [ ] `Constructors` is a **list**: a driver can race for two teams in one season (e.g. Bearman 2024: Ferrari + Haas).
- [ ] No Belgian GP in **2006**, so expect a gap at Spa.
- [ ] Japanese GP was at **Fuji** in 2007–2008 and at Suzuka otherwise.
- [ ] Points system changed in **2010** (winner 10 → 25 points).
- [ ] Sprint races award points from **2021** onwards.
- [ ] A fastest-lap bonus point existed in **2019–2024**, which affects the maximum possible points per race.

---

## Roadmap

### Phase 0 — Setup ✅
- [x] Install Homebrew
- [x] Install git + uv, configure git user
- [x] VS Code with Python + Jupyter extensions
- [x] Create GitHub repo `f1-data-pipeline` and clone it
- [x] Create folder structure (`extract/`, `data/`, `notebooks/`, `dbt/`, `dags/`)
- [x] `.gitignore`: `data/`, `*.duckdb`
- [x] uv project, Python 3.12, `requests pandas pyarrow duckdb`, `ipykernel` (dev)
- [x] First commit and push
- [x] `notebooks/00_setup_check.ipynb`: imports, versions, DuckDB test query

### Phase 1 — Explore the API and define scope 🟡
- [x] Read the driver standings JSON and understand its nesting
- [x] Understand pagination (`total`, `limit`, `offset`) and the stop rule
- [x] Define the questions the dashboard will answer
- [x] Choose endpoints and year range
- [x] Choose architecture (medallion) and bronze layout (Option A)
- [ ] Document goal, questions, scope and decisions in `README.md` (English) and commit
- [x] Rename `data/raw/` → `data/bronze/`

### Phase 2 — Extract → bronze (Python) 👉
- [x] Choose bronze folder names for the 3 endpoints
- [x] Design the extractor in plain English (inputs, loop, checks, outputs)
- [x] Function: build the URL for an endpoint + season (`build_url` in `extract/extract_bronze.py`)
- [x] Function: fetch one page with a timeout and error handling (`fetch_page`: returns the raw `Response`, no `try/except`)
- [ ] 👉 **Check: `total <= limit`, otherwise raise an error** ← you are here
- [ ] Skip the request if the file already exists (no re-downloads)
- [ ] Pause between requests (rate limit)
- [ ] Save the raw JSON response unchanged to `data/bronze/<endpoint>/<season>.json`
- [ ] Loop over seasons 2006–2025 and all 3 endpoints
- [ ] Logging: print what was downloaded or skipped
- [ ] Run it, verify 60 files, commit the code

### Phase 3 — Load bronze → DuckDB
- [ ] Create a DuckDB database file (e.g. `data/f1.duckdb`)
- [ ] Read bronze JSON files into raw tables with DuckDB
- [ ] Verify row counts per season

### Phase 4 — dbt: silver + gold
- [ ] Install `dbt-duckdb`, initialise the dbt project in `dbt/`
- [ ] Silver (staging): flatten JSON, cast types, rename to `snake_case`
- [ ] Gold (marts): standings 2006–2025 (drivers, constructors)
- [ ] Gold: wins at Britain, Belgium, Japan and Italy, by driver and constructor
- [ ] Gold: % of maximum points, V8 vs hybrid
- [ ] dbt tests (not null, unique, accepted values)
- [ ] dbt docs and lineage graph

### Phase 5 — Dashboard
- [ ] Choose a tool (Streamlit or Evidence)
- [ ] Build visuals for each question
- [ ] Screenshot in README

### Phase 6 — Orchestration
- [ ] Airflow locally with Docker
- [ ] DAG: extract → load → dbt run → dbt test
- [ ] Add the 2026 season after it ends

### Phase 7 — Cloud migration (optional)
- [ ] GCP account + **budget alert**
- [ ] Upload bronze to GCS
- [ ] Load into BigQuery, switch dbt to `dbt-bigquery`
- [ ] Looker Studio dashboard
- [ ] Cloud Composer briefly, then delete it the same day (it is not free)