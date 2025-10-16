#!/usr/bin/env bash
set -euo pipefail

if ! command -v pandoc >/dev/null 2>&1; then
  echo "pandoc not found. Please install pandoc to generate PDF." >&2
  exit 1
fi

pandoc -s docs/report.md -o docs/report.pdf
