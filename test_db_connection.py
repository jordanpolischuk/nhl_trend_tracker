from sqlalchemy import text
from src.nhl_trend_tracker.db.connection import get_engine

def main():
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 'Connection successful!'"))
        print(result.scalar())

if __name__ == "__main__":
    main()
