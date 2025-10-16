PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS vendors (
  vendor_id INTEGER PRIMARY KEY,
  name TEXT
);

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
);

CREATE INDEX IF NOT EXISTS idx_trips_pickup_datetime ON trips(pickup_datetime);
CREATE INDEX IF NOT EXISTS idx_trips_hour ON trips(pickup_hour);
CREATE INDEX IF NOT EXISTS idx_trips_dow ON trips(pickup_dow);
CREATE INDEX IF NOT EXISTS idx_trips_speed ON trips(trip_speed_kmh);
CREATE INDEX IF NOT EXISTS idx_trips_distance ON trips(distance_km);
CREATE INDEX IF NOT EXISTS idx_trips_vendor ON trips(vendor_id);
