# Technical Report

## 1. Problem Framing and Dataset Analysis
- Dataset: NYC Taxi Trip raw train split (trip-level). Fields include timestamps, lat/lon, duration, distance, vendor, passengers.
- Data challenges:
  - Missing critical fields (timestamps, coordinates)
  - Out-of-bounds coordinates outside NYC
  - Unrealistic durations/speeds
- Assumptions:
  - NYC bounding box: lat [40.3, 41.2], lon [-74.5, -72.8]
  - Valid duration: 1 minute to 4 hours
  - Valid speed: 1–130 km/h
- Unexpected observation:
  - Concentration of trips around certain hours; peak hours strongly skew insights, leading to hour-based indexing and filters.

## 2. System Architecture and Design Decisions
- Frontend: vanilla HTML/CSS/JS to reduce complexity and keep focus on data logic.
- Backend: Flask + SQLite for quick iteration; indices on datetime, hour, DOW, distance, speed.
- Database schema:
  - `vendors(vendor_id PK, name)`
  - `trips(id PK, vendor_id FK, pickup_datetime, dropoff_datetime, passenger_count, pickup_longitude, pickup_latitude, dropoff_longitude, dropoff_latitude, distance_km, trip_duration, trip_speed_kmh, fare_estimate, fare_per_km, pickup_hour, pickup_dow)`
- Trade-offs:
  - SQLite over Postgres for portability; sufficient for local analytics.
  - Simple fare model (feature) rather than using fare field to avoid dataset inconsistencies.

## 3. Algorithmic Logic and Data Structures
### 3.1 Top-K Longest Trips (No sort/heap)
- Code: `backend/custom_algorithm.py` -> `top_k_longest_by_duration`
- Approach: fixed-size insertion buffer of size k; O(n·k) time, O(k) space.
- Pseudocode:
```
function top_k(trips, k):
  top = [None]*k
  for trip in trips:
    d = trip.duration
    for i in 0..k-1:
      if top[i] is None or d > top[i].duration:
        insert trip at top[i]; pop last; break
  return filter_not_none(top)
```
- Complexity: time O(n·k); space O(k)

### 3.2 Streaming Anomaly Detection
- Code: `streaming_anomaly_flags`
- Approach: Welford's online mean/variance; flag |x-μ| > m·σ in a single pass.
- Complexity: O(n) time, O(1) space.

## 4. Insights and Interpretation
1) Average speed, fare/km, distance (API `/api/insights`)
   - How: aggregation over trips.
   - Meaning: Typical mobility characteristics of trips.
2) Busy hours (API `/api/insights` -> `busy_hours`)
   - How: group by `pickup_hour` order by count desc limit 3.
   - Meaning: Peak demand windows for fleet operations.
3) Longest trips and speed anomalies
   - How: `/api/top-longest` and `/api/anomalies` using custom algorithms.
   - Meaning: Rare long trips and abnormal speeds can indicate edge cases or data issues.

## 5. Reflection and Future Work
- Challenges: messy coordinates, timestamp normalization, performance of feature engineering.
- Future work:
  - Switch to Postgres, add PostGIS for spatial queries and zones.
  - Add map visualizations and geohash binning.
  - Batch ingestion with chunked streaming for very large CSVs.
  - Productionize with containerization and CI.
