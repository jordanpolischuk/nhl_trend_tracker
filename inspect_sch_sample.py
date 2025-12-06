from datetime import date
import json

from nhlpy import NHLClient


def main():
    client = NHLClient()
    target = date(2025, 12, 5)  # a date we know has games from your probe
    d_str = target.isoformat()

    schedule = client.schedule.daily_schedule(date=d_str)
    print("Top-level keys:", schedule.keys())

    games = schedule.get("games", [])
    print("Number of games:", len(games))

    if not games:
        print("No games found for", d_str)
        return

    game = games[0]
    print("\nFirst game keys:", list(game.keys()))

    home = game.get("homeTeam", {})
    away = game.get("awayTeam", {})

    print("\nHome team raw dict:")
    print(json.dumps(home, indent=2))

    print("\nAway team raw dict:")
    print(json.dumps(away, indent=2))

    print("\nSeason:", game.get("season"))
    print("gameType:", game.get("gameType"))
    print("Potential id fields in game:")
    print({k: v for k, v in game.items() if "id" in k.lower()})


if __name__ == "__main__":
    main()