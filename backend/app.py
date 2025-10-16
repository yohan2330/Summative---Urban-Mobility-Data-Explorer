from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
from pathlib import Path
from custom_algorithm import top_k_longest_by_duration, streaming_anomaly_flags

app = Flask(__name__)
CORS(app)
BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = BASE_DIR / "data" / "nyc_taxi.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/api/trips")
def get_trips():
    conn = get_db()
    params = []
    where = []

    # Filters: time range, speed range, distance range, vendor, dow, hour
    start = request.args.get('start')
    end = request.args.get('end')
    min_speed = request.args.get('min_speed', type=float)
    max_speed = request.args.get('max_speed', type=float)
    min_dist = request.args.get('min_dist', type=float)
    max_dist = request.args.get('max_dist', type=float)
    vendor = request.args.get('vendor', type=int)
    dow = request.args.get('dow', type=int)
    hour = request.args.get('hour', type=int)

    if start:
        where.append("pickup_datetime >= ?")
        params.append(start)
    if end:
        where.append("pickup_datetime <= ?")
        params.append(end)
    if min_speed is not None:
        where.append("trip_speed_kmh >= ?")
        params.append(min_speed)
    if max_speed is not None:
        where.append("trip_speed_kmh <= ?")
        params.append(max_speed)
    if min_dist is not None:
        where.append("distance_km >= ?")
        params.append(min_dist)
    if max_dist is not None:
        where.append("distance_km <= ?")
        params.append(max_dist)
    if vendor is not None:
        where.append("vendor_id = ?")
        params.append(vendor)
    if dow is not None:
        where.append("pickup_dow = ?")
        params.append(dow)
    if hour is not None:
        where.append("pickup_hour = ?")
        params.append(hour)

    where_sql = (" WHERE " + " AND ".join(where)) if where else ""

    limit = request.args.get('limit', default=50, type=int)
    offset = request.args.get('offset', default=0, type=int)
    sql = f"SELECT * FROM trips{where_sql} ORDER BY pickup_datetime LIMIT ? OFFSET ?"
    rows = conn.execute(sql, params + [limit, offset]).fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])

@app.route("/api/insights")
def get_insights():
    conn = get_db()
    res = conn.execute(
        """
        SELECT 
            AVG(trip_speed_kmh) as avg_speed,
            AVG(fare_per_km) as avg_fare_per_km,
            AVG(distance_km) as avg_distance,
            COUNT(*) as num_trips
        FROM trips
        """
    ).fetchone()

    top_hours = conn.execute(
        """
        SELECT pickup_hour, COUNT(*) as c
        FROM trips
        GROUP BY pickup_hour
        ORDER BY c DESC
        LIMIT 3
        """
    ).fetchall()

    busy_hours = [{"hour": r[0], "count": r[1]} for r in top_hours]
    conn.close()
    return jsonify({**dict(res), "busy_hours": busy_hours})


@app.route("/api/vendors")
def get_vendors():
    conn = get_db()
    rows = conn.execute("SELECT vendor_id, name FROM vendors ORDER BY vendor_id").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route("/api/top-longest")
def api_top_longest():
    k = request.args.get('k', default=5, type=int)
    sample = request.args.get('sample', default=5000, type=int)
    conn = get_db()
    rows = conn.execute(
        "SELECT id, trip_duration, pickup_datetime, dropoff_datetime, distance_km FROM trips LIMIT ?",
        (sample,),
    ).fetchall()
    conn.close()
    trips = [dict(r) for r in rows]
    top = top_k_longest_by_duration(trips, k=k)
    return jsonify(top)


@app.route("/api/anomalies")
def api_anomalies():
    field = request.args.get('field', default='trip_speed_kmh', type=str)
    m = request.args.get('m', default=3.0, type=float)
    sample = request.args.get('sample', default=5000, type=int)
    conn = get_db()
    rows = conn.execute(
        f"SELECT id, {field} FROM trips WHERE {field} IS NOT NULL LIMIT ?",
        (sample,),
    ).fetchall()
    conn.close()
    values = [r[1] for r in rows]
    flags = list(streaming_anomaly_flags(values, m=m))
    result = []
    for (idx, value, is_anom) in flags:
        if is_anom:
            result.append({"id": rows[idx][0], field: value})
    return jsonify({"field": field, "threshold_m_sigma": m, "count": len(result), "items": result})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
