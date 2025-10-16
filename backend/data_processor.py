import os
from pathlib import Path
import pandas as pd
import numpy as np
from math import radians, sin, cos, sqrt, atan2
import zipfile
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
DATA_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

def haversine(lat1, lon1, lat2, lon2):
    # Calculate distance (in km) between two lat/lon points
    R = 6371
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c

def _ensure_train_csv() -> Path:
    """Ensure train.csv exists by extracting train.zip if present."""
    train_csv = DATA_DIR / "train.csv"
    if train_csv.exists():
        return train_csv
    train_zip = DATA_DIR / "train.zip"
    if train_zip.exists():
        with zipfile.ZipFile(train_zip, 'r') as zf:
            # Extract the first CSV named train.csv or similar
            members = [m for m in zf.namelist() if m.lower().endswith('.csv')]
            if not members:
                raise FileNotFoundError("No CSV found inside train.zip")
            # Prefer a file named train.csv
            preferred = [m for m in members if os.path.basename(m).lower() == 'train.csv']
            target = preferred[0] if preferred else members[0]
            zf.extract(target, DATA_DIR)
            extracted = DATA_DIR / target
            # Normalize name to train.csv
            extracted.rename(train_csv)
            return train_csv
    raise FileNotFoundError("Expected data/train.csv or data/train.zip. Please place the official dataset under data/.")


def clean_data():
    print("Loading dataset...")
    csv_path = _ensure_train_csv()
    df = pd.read_csv(csv_path)

    print("Cleaning data...")
    # Basic normalization of column names (strip spaces)
    df.columns = [c.strip() for c in df.columns]

    # Drop exact duplicates
    before = len(df)
    df.drop_duplicates(inplace=True)

    # Handle missing values: drop rows missing critical fields
    critical_cols = [
        'id', 'vendor_id', 'pickup_datetime', 'dropoff_datetime',
        'passenger_count', 'pickup_longitude', 'pickup_latitude',
        'dropoff_longitude', 'dropoff_latitude', 'trip_duration'
    ]
    missing_mask = df[critical_cols].isna().any(axis=1)
    dropped_missing = int(missing_mask.sum())
    df = df[~missing_mask]

    # Parse timestamps to ISO8601 strings
    for col in ['pickup_datetime', 'dropoff_datetime']:
        df[col] = pd.to_datetime(df[col], errors='coerce', utc=True)
    invalid_ts_mask = df[['pickup_datetime', 'dropoff_datetime']].isna().any(axis=1)
    dropped_invalid_ts = int(invalid_ts_mask.sum())
    df = df[~invalid_ts_mask]

    # NYC plausible bounding box
    nyc_lat_min, nyc_lat_max = 40.3, 41.2
    nyc_lon_min, nyc_lon_max = -74.5, -72.8
    geo_mask = (
        (df['pickup_latitude'].between(nyc_lat_min, nyc_lat_max)) &
        (df['dropoff_latitude'].between(nyc_lat_min, nyc_lat_max)) &
        (df['pickup_longitude'].between(nyc_lon_min, nyc_lon_max)) &
        (df['dropoff_longitude'].between(nyc_lon_min, nyc_lon_max))
    )
    dropped_geo = int((~geo_mask).sum())
    df = df[geo_mask]

    # Compute distance using haversine
    df['distance_km'] = df.apply(
        lambda row: haversine(
            row['pickup_latitude'], row['pickup_longitude'],
            row['dropoff_latitude'], row['dropoff_longitude']
        ), axis=1
    )

    # Remove zero or unrealistic distances/durations
    mask_dist = (df['distance_km'] > 0.2) & (df['distance_km'] < 100)
    mask_dur = (df['trip_duration'] > 60) & (df['trip_duration'] < 4 * 3600)
    # Derived speed for sanity check (km/h)
    speed_kmh = df['distance_km'] / (df['trip_duration'] / 3600)
    mask_speed = (speed_kmh > 1) & (speed_kmh < 130)
    valid_mask = mask_dist & mask_dur & mask_speed
    dropped_outliers = int((~valid_mask).sum())
    df = df[valid_mask]

    # Derived features
    df['trip_speed_kmh'] = df['distance_km'] / (df['trip_duration'] / 3600)
    df['fare_estimate'] = 2.5 + 1.2 * df['distance_km']  # simple fare model
    df['fare_per_km'] = df['fare_estimate'] / df['distance_km']
    df['pickup_hour'] = df['pickup_datetime'].dt.hour
    df['pickup_dow'] = df['pickup_datetime'].dt.weekday  # 0=Mon

    # Normalize timestamps to ISO strings
    for col in ['pickup_datetime', 'dropoff_datetime']:
        df[col] = df[col].dt.strftime('%Y-%m-%dT%H:%M:%SZ')

    # Log excluded/suspicious records
    exclusions_path = LOGS_DIR / 'exclusions.csv'
    with open(exclusions_path, 'w') as f:
        f.write('reason,count\n')
        f.write(f'dropped_missing,{dropped_missing}\n')
        f.write(f'dropped_invalid_timestamps,{dropped_invalid_ts}\n')
        f.write(f'dropped_out_of_nyc_bounds,{dropped_geo}\n')
        f.write(f'dropped_outliers,{dropped_outliers}\n')

    print(f" Final rows: {len(df)} (see logs/exclusions.csv for drops)")

    # Save cleaned dataset
    cleaned_path = DATA_DIR / "cleaned_data.csv"
    df.to_csv(cleaned_path, index=False)
    print("Saved cleaned data → data/cleaned_data.csv")

if __name__ == "__main__":
    clean_data()
