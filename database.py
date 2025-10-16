import sqlite3
import pandas as pd

def create_db():
    conn = sqlite3.connect("../data/nyc_taxi.db")
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS trips (
            id TEXT PRIMARY KEY,
            vendor_id INTEGER,
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
            fare_per_km REAL
        )
    """)

    conn.commit()
    conn.close()
    print("Database and table created.")

def insert_data():
    df = pd.read_csv("../data/cleaned_data.csv")
    conn = sqlite3.connect("../data/nyc_taxi.db")
    df.to_sql("trips", conn, if_exists="replace", index=False)
    conn.close()
    print("Cleaned data inserted into database.")

if __name__ == "__main__":
    create_db()
    insert_data()
