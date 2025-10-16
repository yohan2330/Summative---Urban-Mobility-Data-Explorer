#!/usr/bin/env bash
set -euo pipefail

# 1) Create venv and install deps
if [ ! -d .venv ]; then
  python3 -m venv .venv
fi
source .venv/bin/activate
pip install -r backend/requirements.txt

# 2) Run pipeline and load DB
python backend/data_processor.py
python backend/database.py

# 3) Run backend
python backend/app.py
