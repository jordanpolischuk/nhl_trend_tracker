from nhlpy import NHLClient
import json

def main():
    client = NHLClient()

    # 1) Test a known example date
    sched_old = client.schedule.get_schedule(date="2024-10-08")
    print("2024-10-08: number of games:", len(sched_old.get("games", [])))

    # 2) Test today's date
    sched_today = client.schedule.get_schedule(date="2025-12-05")
    print("2025-12-05: number of games:", len(sched_today.get("games", [])))

    # Optionally print first game structure for inspection
    if sched_today.get("games"):
        print("First game sample:")
        print(json.dumps(sched_today["games"][0], indent=2)[:1500])

if __name__ == "__main__":
    main()