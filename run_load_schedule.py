from datetime import date
from src.nhl_trend_tracker.etl.load_schedule import run_for_date

print("RUNNER FILE EXECUTED")

def main():
    # For the first test, hard-code a date we know has games.
    # From your probe: 2025-12-05 has 5 games.
    target = date(2025, 12, 5)
    print(f"Loading schedule for {target} ...")
    run_for_date(target)
    print("Done.")

if __name__ == "__main__":
    main()
