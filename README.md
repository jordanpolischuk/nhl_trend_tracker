# NHL Trend Tracker

NHL Trend Tracker is a data pipeline and analysis toolkit for quantifying **team** and **player** trends in the NHL using game-by-game data from NHL.com.

The core idea:

- Ingest raw NHL data via the **undocumented NHL APIs** using the Python wrapper **`nhl-api-py`** :contentReference[oaicite:1]{index=1}  
- Store it in a **PostgreSQL** warehouse with a **time-series friendly schema**
- Build derived daily snapshots and **trend / streak features**
- Use Python (and eventually ML) to detect “upward” and “downward” trends for teams and players

The project is designed to be reproducible and shareable so multiple people (e.g. this repo’s collaborators) can work on it.

---

## 1. Tech stack

- **Language:** Python (3.10+ recommended)
- **Database:** PostgreSQL
- **NHL Data Access:** [`nhl-api-py`](https://pypi.org/project/nhl-api-py/) – a wrapper around the new NHL API (`api-web.nhle.com`, `api.nhle.com/stats/rest`, etc.) :contentReference[oaicite:2]{index=2}  
- **ORM / DB Access:** Plain SQL + optional SQLAlchemy (TBD)
- **Environment / Config:** `.env` file loaded by `config.py`

---

## 2. Repository layout

```text
nhl-trend-tracker/
├─ README.md
├─ pyproject.toml           # or requirements.txt
├─ .env.example             # template for DB and app config
├─ sql/
│  └─ 001_init_schema.sql   # DDL for Postgres tables
├─ src/
│  └─ nhl_trend_tracker/
│     ├─ __init__.py
│     ├─ config.py          # env loading, global settings
│     ├─ db/
│     │  ├─ connection.py   # Postgres connection helpers
│     │  └─ schema.py       # optional ORM models
│     ├─ etl/
│     │  ├─ fetch_games.py      # uses nhl-api-py to fetch raw data
│     │  ├─ load_games.py       # loads dim_game, dim_team
│     │  ├─ load_stats.py       # loads fact_team_game, fact_player_game
│     │  └─ build_snapshots.py  # builds fact_team_day, fact_player_day
│     └─ analytics/
│        ├─ team_trends.py
│        └─ player_trends.py
├─ scripts/
│  ├─ init_db.sh            # create DB and apply sql/001_init_schema.sql
│  └─ run_daily_etl.sh      # wrapper for daily ETL run
└─ notebooks/
   └─ exploration.ipynb     # scratchpad for analysis / prototyping

