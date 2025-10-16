const API = "http://127.0.0.1:5000";

function isoLocal(dtInput) {
  if (!dtInput) return null;
  const dt = new Date(dtInput);
  if (isNaN(dt.getTime())) return null;
  // Convert to ISO without milliseconds
  return dt.toISOString().replace(/\.\d{3}Z$/, 'Z');
}

async function loadVendors() {
  const res = await fetch(`${API}/api/vendors`);
  const vendors = await res.json();
  const sel = document.getElementById('vendor');
  vendors.forEach(v => {
    const opt = document.createElement('option');
    opt.value = v.vendor_id;
    opt.textContent = `${v.vendor_id} - ${v.name}`;
    sel.appendChild(opt);
  });
}

async function loadTrips() {
  const params = new URLSearchParams();
  const start = isoLocal(document.getElementById('start').value);
  const end = isoLocal(document.getElementById('end').value);
  const min_speed = document.getElementById('min_speed').value;
  const max_speed = document.getElementById('max_speed').value;
  const vendor = document.getElementById('vendor').value;

  if (start) params.set('start', start);
  if (end) params.set('end', end);
  if (min_speed) params.set('min_speed', min_speed);
  if (max_speed) params.set('max_speed', max_speed);
  if (vendor) params.set('vendor', vendor);
  params.set('limit', '50');

  const res = await fetch(`${API}/api/trips?${params.toString()}`);
  const data = await res.json();
  const list = document.getElementById("trips");
  list.innerHTML = data.map(t => `
    <p>🕒 ${t.pickup_datetime} → ${t.dropoff_datetime} |
    ${(+t.distance_km).toFixed(2)} km | ${(+t.trip_speed_kmh).toFixed(1)} km/h</p>
  `).join("");
}

async function loadInsights() {
  const res = await fetch(`${API}/api/insights`);
  const d = await res.json();
  document.getElementById("insights").innerHTML = `
    <h3>📊 Insights</h3>
    <p>Average Speed: ${(+d.avg_speed).toFixed(2)} km/h</p>
    <p>Average Fare/km: $${(+d.avg_fare_per_km).toFixed(2)}</p>
    <p>Average Distance: ${(+d.avg_distance).toFixed(2)} km</p>
    <p>Trips: ${d.num_trips}</p>
    <p>Busy Hours: ${d.busy_hours.map(h => h.hour).join(', ')}</p>
  `;
  drawBusyHoursChart(d.busy_hours || []);
}

window.addEventListener('DOMContentLoaded', async () => {
  await loadVendors();
  await loadInsights();
  await loadTrips();
  await loadTopLongest();
  await loadAnomalies();
});

async function loadTopLongest() {
  const res = await fetch(`${API}/api/top-longest?k=5&sample=5000`);
  const data = await res.json();
  const summary = document.getElementById('summary');
  const items = data.map(t => `${t.id} (${(+t.trip_duration/60).toFixed(1)} min, ${(+t.distance_km).toFixed(2)} km)`);
  summary.innerHTML = `Top-5 Longest Trips: ${items.join(' • ')}`;
}

async function loadAnomalies() {
  const res = await fetch(`${API}/api/anomalies?field=trip_speed_kmh&m=3&sample=5000`);
  const data = await res.json();
  const summary = document.getElementById('summary');
  const prev = summary.innerHTML;
  summary.innerHTML = `${prev}<br>Speed Anomalies (3σ): ${data.count}`;
}

function drawBusyHoursChart(busyHours) {
  const canvas = document.getElementById('chart');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  if (!busyHours.length) {
    ctx.fillStyle = '#333';
    ctx.fillText('No data yet', 20, 20);
    return;
  }

  const padding = 40;
  const width = canvas.width - padding * 2;
  const height = canvas.height - padding * 2;
  const maxVal = Math.max(...busyHours.map(h => h.count));
  const barW = width / busyHours.length * 0.7;

  ctx.strokeStyle = '#ccc';
  ctx.beginPath();
  ctx.moveTo(padding, padding);
  ctx.lineTo(padding, padding + height);
  ctx.lineTo(padding + width, padding + height);
  ctx.stroke();

  busyHours.forEach((h, i) => {
    const x = padding + i * (width / busyHours.length) + (width / busyHours.length - barW) / 2;
    const bh = (h.count / maxVal) * (height - 10);
    const y = padding + height - bh;
    ctx.fillStyle = '#2b8a3e';
    ctx.fillRect(x, y, barW, bh);
    ctx.fillStyle = '#000';
    ctx.font = '12px sans-serif';
    ctx.fillText(String(h.hour), x + barW / 2 - 6, padding + height + 14);
  });
}
