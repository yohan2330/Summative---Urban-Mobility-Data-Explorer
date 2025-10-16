async function loadTrips() {
  const res = await fetch("http://127.0.0.1:5000/api/trips");
  const data = await res.json();
  const list = document.getElementById("trips");
  list.innerHTML = data.map(t => `
    <p>🕒 ${t.pickup_datetime} → ${t.dropoff_datetime} |
    ${t.distance_km.toFixed(2)} km | ${t.trip_speed_kmh.toFixed(1)} km/h</p>
  `).join("");
}

async function loadInsights() {
  const res = await fetch("http://127.0.0.1:5000/api/insights");
  const d = await res.json();
  document.getElementById("insights").innerHTML = `
    <h3>📊 Insights</h3>
    <p>Average Speed: ${d.avg_speed.toFixed(2)} km/h</p>
    <p>Average Fare/km: $${d.avg_fare_per_km.toFixed(2)}</p>
    <p>Average Distance: ${d.avg_distance.toFixed(2)} km</p>
  `;
}
