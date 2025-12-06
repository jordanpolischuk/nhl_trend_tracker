from __future__ import annotations

from nhlpy import NHLClient
from sqlalchemy import text
from sqlalchemy.engine import Engine

from src.nhl_trend_tracker.db.connection import get_engine


def fetch_all_teams() -> list[dict]:
    client = NHLClient()
    teams_payload = client.teams.teams()
    if isinstance(teams_payload, dict):
        return teams_payload.get("teams", [])
    return teams_payload


def upsert_all_teams(engine: Engine, teams: list[dict]) -> None:
    if not teams:
        return

    with engine.begin() as conn:
        for t in teams:
            team_id = t.get("id")
            if team_id is None:
                continue

            team_code = (t.get("abbreviation") or t.get("abbrev") or "")[:3]
            team_name = t.get("name") or f"Team {team_id}"
            city = t.get("locationName") or t.get("city")

            conference = None
            division = None
            first_season = None

            conf = t.get("conference") or {}
            if conf:
                conference = conf.get("name")

            div = t.get("division") or {}
            if div:
                division = div.get("name")

            first_year = t.get("firstYearOfPlay")
            if first_year:
                try:
                    first_season = int(first_year)
                except ValueError:
                    first_season = None

            conn.execute(
                text(
                    """
                    INSERT INTO dim_team (
                        team_id, team_code, team_name, city,
                        conference, division, first_season
                    )
                    VALUES (
                        :team_id, :team_code, :team_name, :city,
                        :conference, :division, :first_season
                    )
                    ON CONFLICT (team_id) DO UPDATE
                    SET team_code    = EXCLUDED.team_code,
                        team_name    = EXCLUDED.team_name,
                        city         = EXCLUDED.city,
                        conference   = EXCLUDED.conference,
                        division     = EXCLUDED.division,
                        first_season = EXCLUDED.first_season
                    """
                ),
                {
                    "team_id": team_id,
                    "team_code": team_code,
                    "team_name": team_name,
                    "city": city,
                    "conference": conference,
                    "division": division,
                    "first_season": first_season,
                },
            )


def run_load_all_teams() -> None:
    engine = get_engine()
    teams = fetch_all_teams()
    upsert_all_teams(engine, teams)