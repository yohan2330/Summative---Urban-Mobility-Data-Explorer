import sqlite3
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "nyc_taxi.db"

def create_db():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Dimension table for vendors (normalized example)
    cur.execute(
        """
        PRAGMA foreign_keys = ON;
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS vendors (
            vendor_id INTEGER PRIMARY KEY,
            name TEXT
        )
        """
    )

    # Fact table for trips
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS trips (
            id TEXT PRIMARY KEY,
            vendor_id INTEGER REFERENCES vendors(vendor_id),
            pickup_datetime TEXT,
            dropoff_datetime TEXT,
            passenger_count INTEGER,
            pickup_longitude REAL,
            pickup_latitude REAL,
            dropoff_longitude REAL,
            dropoff_latitude REAL,
            distance_km REAL,
            trip_duration REAL,
            trip_speed_kmh REAL,
            fare_estimate REAL,
            fare_per_km REAL,
            pickup_hour INTEGER,
            pickup_dow INTEGER
        )
        """
    )

    # Helpful indexes
    cur.execute("CREATE INDEX IF NOT EXISTS idx_trips_pickup_datetime ON trips(pickup_datetime)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_trips_hour ON trips(pickup_hour)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_trips_dow ON trips(pickup_dow)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_trips_speed ON trips(trip_speed_kmh)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_trips_distance ON trips(distance_km)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_trips_vendor ON trips(vendor_id)")

    conn.commit()
    conn.close()
    print(f"Database and tables ready at {DB_PATH}")

def insert_data():
    cleaned_path = DATA_DIR / "cleaned_data.csv"
    if not cleaned_path.exists():
        raise FileNotFoundError("data/cleaned_data.csv not found. Run data_processor.py first.")

    df = pd.read_csv(cleaned_path)

    # Populate vendors dimension
    vendor_ids = sorted([v for v in df['vendor_id'].dropna().unique().tolist() if str(v).isdigit()])
    vendors_df = pd.DataFrame({
        'vendor_id': vendor_ids,
        'name': [f"Vendor {int(v)}" for v in vendor_ids]
    })

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    # Keep schema and indexes by deleting then appending
    cur.execute("DELETE FROM vendors")
    cur.execute("DELETE FROM trips")
    conn.commit()

    vendors_df.to_sql("vendors", conn, if_exists="append", index=False)
    df.to_sql("trips", conn, if_exists="append", index=False)
    conn.commit()
    conn.close()
    print("Cleaned data inserted into database (vendors + trips).")

if __name__ == "__main__":
    create_db()
    insert_data()
