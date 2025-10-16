from flask import Flask, jsonify
import sqlite3

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect("../data/nyc_taxi.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/api/trips")
def get_trips():
    conn = get_db()
    rows = conn.execute("SELECT * FROM trips LIMIT 20").fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])

@app.route("/api/insights")
def get_insights():
    conn = get_db()
    res = conn.execute("""
        SELECT 
            AVG(trip_speed_kmh) as avg_speed,
            AVG(fare_per_km) as avg_fare_per_km,
            AVG(distance_km) as avg_distance
        FROM trips
    """).fetchone()
    conn.close()
    return jsonify(dict(res))

if __name__ == "__main__":
    app.run(debug=True)
