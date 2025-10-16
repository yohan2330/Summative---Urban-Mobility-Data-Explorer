# NYC Taxi Trip Explorer (Fullstack Assignment)

This project demonstrates a full-cycle data product on the NYC Taxi Trip dataset: ingest, clean, store, serve, and visualize.

## Quick Start

1) Place the official dataset under `data/`:

```
data/train.zip  (or data/train.csv)
```

2) Create a virtual environment and install deps (recommended Python 3.10–3.11):

```
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

3) Run data pipeline and load DB:

```
python backend/data_processor.py
python backend/database.py
```

4) Start backend API:

```
python backend/app.py
```

5) Open the dashboard:

Just open `frontend/index.html` in your browser. It calls the API at `http://127.0.0.1:5000`.

Optional: generate the PDF report (requires `pandoc` installed):

```
scripts/generate_pdf.sh
```

## Architecture

- Backend: Flask API + SQLite. Data pipeline with Pandas for cleaning/feature engineering. Indices for key filters.
- Frontend: Vanilla HTML/CSS/JS; fetches API for filtering and insights.
- Data: Stored in `data/nyc_taxi.db`, populated from `data/cleaned_data.csv`.

## Custom Algorithms

Implemented in `backend/custom_algorithm.py`:

- Top-K longest trips without built-in sort or heap
- Streaming anomaly detection using Welford's online mean/variance

## Deliverables

- Database lives at `data/nyc_taxi.db`
- `logs/exclusions.csv` summarizes dropped records and reasons
- Add your video walkthrough link here: <VIDEO_LINK_HERE>

Note on environment: If using very new Python versions (e.g., 3.13), some
binary wheels may be unavailable. Prefer Python 3.10–3.11 to avoid building
`numpy`/`pandas` from source.
