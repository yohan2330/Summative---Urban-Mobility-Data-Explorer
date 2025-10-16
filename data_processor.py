import pandas as pd
import numpy as np
from math import radians, sin, cos, sqrt, atan2

def haversine(lat1, lon1, lat2, lon2):
    # Calculate distance (in km) between two lat/lon points
    R = 6371
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c

def clean_data():
    print("Loading dataset...")
    df = pd.read_csv("../data/train.csv")

    print("Cleaning data...")
    df.dropna(inplace=True)
    df.drop_duplicates(inplace=True)

    # Filter invalid coordinates
    df = df[
        (df['pickup_longitude'] != 0) &
        (df['dropoff_longitude'] != 0)
    ]

    # Compute distance using haversine
    df['distance_km'] = df.apply(
        lambda row: haversine(
            row['pickup_latitude'], row['pickup_longitude'],
            row['dropoff_latitude'], row['dropoff_longitude']
        ), axis=1
    )

    # Remove zero or unrealistic distances/durations
    df = df[(df['distance_km'] > 0.2) & (df['distance_km'] < 100)]
    df = df[(df['trip_duration'] > 60) & (df['trip_duration'] < 7200)]

    # Derived features
    df['trip_speed_kmh'] = df['distance_km'] / (df['trip_duration'] / 3600)
    df['fare_estimate'] = 2.5 + 1.2 * df['distance_km']  # simple formula
    df['fare_per_km'] = df['fare_estimate'] / df['distance_km']

    # Log excluded/suspicious records
    print(f" Final rows: {len(df)}")

    # Save cleaned dataset
    df.to_csv("../data/cleaned_data.csv", index=False)
    print("Saved cleaned data → data/cleaned_data.csv")

if __name__ == "__main__":
    clean_data()
