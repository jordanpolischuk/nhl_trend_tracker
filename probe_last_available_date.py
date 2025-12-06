from datetime import date, timedelta
from nhlpy import NHLClient

def test_available_dates(days_back: int = 60):
    client = NHLClient()
    today = date.today()

    latest_date_with_games = None
    results = []

    for i in range(days_back):
        d = today - timedelta(days=i)
        d_str = d.isoformat()

        try:
            data = client.schedule.daily_schedule(date=d_str)
        except Exception as e:
            print(f"Error for {d_str}: {e}")
            continue

        games = data.get("games", [])
        if games:
            results.append((d_str, len(games)))
            if latest_date_with_games is None:
                latest_date_with_games = d_str

    print("\n=== Dates with Games Found ===")
    for d, count in results:
        print(f"{d}: {count} games")

    print("\nMost recent date with games:", latest_date_with_games)

if __name__ == "__main__":
    test_available_dates(days_back=90)