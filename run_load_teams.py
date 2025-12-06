from src.nhl_trend_tracker.etl.load_teams import run_load_all_teams, fetch_all_teams

def main():
    print("Fetching teams from nhlpy...")
    teams = fetch_all_teams()
    print(f"Fetched type: {type(teams)}")
    print(f"Fetched length: {len(teams) if hasattr(teams, '__len__') else 'N/A'}")
    print("Sample payload:")
    print(teams[:3] if isinstance(teams, list) else teams)

    print("\nRunning upsert_all_teams()...")
    run_load_all_teams()
    print("Done.")

if __name__ == "__main__":
    main()