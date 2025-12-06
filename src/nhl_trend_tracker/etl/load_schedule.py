# src/nhl_trend_tracker/etl/load_schedule.py

from __future__ import annotations

from datetime import date
from typing import Optional

from nhlpy import NHLClient
from sqlalchemy import text
from sqlalchemy.engine import Engine

from src.nhl_trend_tracker.db.connection import get_engine


def _map_game_type(game_type_code: int | None) -> str:
    """
    Map nhlpy/NHL numeric gameType to our single-character code.

    Common mapping (NHL Stats API convention):
      1 = Preseason
      2 = Regular season
      3 = Playoffs
      4 = All-star / special

    We'll store:
      'R' = regular, 'P' = playoffs, 'X' = preseason/other
    """
    if game_type_code == 2:
        return "R"
    if game_type_code == 3:
        return "P"
    return "X"


def fetch_daily_schedule(target_date: date) -> dict:
    """
    Call nhlpy to get the schedule for a specific date.

    Returns the raw dict with keys like 'date' and 'games'.
    """
    client = NHLClient()
    schedule = client.schedule.daily_schedule(date=target_date.isoformat())
    return schedule


def upsert_teams(engine: Engine, schedule: dict) -> None:
    """
    Insert or update teams appearing in the schedule into dim_team.

    We'll fill:
      team_id, team_code, team_name, city
    and leave conference/division/first_season NULL for now.

    We are defensive about field names because the NHL web API uses
    different naming conventions in different endpoints.
    """
    games = schedule.get("games", [])
    if not games:
        return

    with engine.begin() as conn:
        for game in games:
            for side in ("homeTeam", "awayTeam"):
                team_info = game.get(side) or {}
                team_id = team_info.get("id")
                if team_id is None:
                    continue

                # Abbreviation can appear as 'abbrev' or 'triCode'
                team_code = (
                    team_info.get("abbrev")
                    or team_info.get("triCode")
                    or ""
                )[:3]

                # Derive a sensible team_name from multiple possible fields
                common = team_info.get("commonName") or {}
                place = team_info.get("placeName") or {}

                team_name = (
                    team_info.get("fullName")
                    or team_info.get("name")
                    or team_info.get("teamName")
                    or common.get("default")
                    or place.get("default")
                    or team_code
                    or f"Team {team_id}"
                )

                # Derive city from multiple possible fields
                team_city = (
                    team_info.get("city")
                    or team_info.get("locationName")
                    or place.get("default")
                )

                conn.execute(
                    text(
                        """
                        INSERT INTO dim_team (
                            team_id, team_code, team_name, city, conference,
                            division, first_season
                        )
                        VALUES (
                            :team_id, :team_code, :team_name, :city,
                            NULL, NULL, NULL
                        )
                        ON CONFLICT (team_id) DO UPDATE
                        SET team_code = EXCLUDED.team_code,
                            team_name = EXCLUDED.team_name,
                            city      = EXCLUDED.city
                        """
                    ),
                    {
                        "team_id": team_id,
                        "team_code": team_code,
                        "team_name": team_name,
                        "city": team_city,
                    },
                )


def upsert_seasons(engine: Engine, schedule: dict) -> None:
    """
    Ensure dim_season has at least a row for each season in the games.

    We'll only insert season_id for now; boundaries can be filled later.
    """
    games = schedule.get("games", [])
    if not games:
        return

    season_ids: set[int] = set()
    for game in games:
        season_str = game.get("season")
        if season_str:
            try:
                season_ids.add(int(season_str))
            except ValueError:
                continue

    if not season_ids:
        return

    with engine.begin() as conn:
        for season_id in season_ids:
            conn.execute(
                text(
                    """
                    INSERT INTO dim_season (season_id)
                    VALUES (:season_id)
                    ON CONFLICT (season_id) DO NOTHING
                    """
                ),
                {"season_id": season_id},
            )


def upsert_games(engine: Engine, schedule: dict) -> None:
    """
    Insert or update games from schedule into dim_game.
    """
    games = schedule.get("games", [])
    if not games:
        return

    schedule_date = schedule.get("date")  # 'YYYY-MM-DD'

    with engine.begin() as conn:
        for game in games:
            game_id = game.get("id") or game.get("gameId") or game.get("gamePk")
            if game_id is None:
                # Not worth guessing; we need a primary key
                continue

            try:
                game_id = int(game_id)
            except ValueError:
                continue

            season_str = game.get("season")
            season_id = int(season_str) if season_str else None

            game_type_code = game.get("gameType")
            game_type = _map_game_type(game_type_code)

            status = game.get("gameState") or game.get("gameStatus")

            home_team = game.get("homeTeam") or {}
            away_team = game.get("awayTeam") or {}
            home_team_id = home_team.get("id")
            away_team_id = away_team.get("id")

            venue_info = game.get("venue") or {}
            venue_name = venue_info.get("name")

            conn.execute(
                text(
                    """
                    INSERT INTO dim_game (
                        game_id, season_id, game_date, game_type,
                        home_team_id, away_team_id, venue, status
                    )
                    VALUES (
                        :game_id, :season_id, :game_date, :game_type,
                        :home_team_id, :away_team_id, :venue, :status
                    )
                    ON CONFLICT (game_id) DO UPDATE
                    SET season_id     = EXCLUDED.season_id,
                        game_date     = EXCLUDED.game_date,
                        game_type     = EXCLUDED.game_type,
                        home_team_id  = EXCLUDED.home_team_id,
                        away_team_id  = EXCLUDED.away_team_id,
                        venue         = EXCLUDED.venue,
                        status        = EXCLUDED.status
                    """
                ),
                {
                    "game_id": game_id,
                    "season_id": season_id,
                    "game_date": schedule_date,
                    "game_type": game_type,
                    "home_team_id": home_team_id,
                    "away_team_id": away_team_id,
                    "venue": venue_name,
                    "status": status,
                },
            )


def run_for_date(target_date: Optional[date] = None) -> None:
    """
    High-level entry point:
      - fetch schedule for the given date
      - upsert seasons, teams, and games into the DB
    """
    if target_date is None:
        target_date = date.today()

    engine = get_engine()
    schedule = fetch_daily_schedule(target_date)

    upsert_seasons(engine, schedule)
    upsert_teams(engine, schedule)
    upsert_games(engine, schedule)