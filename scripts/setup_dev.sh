#!/usr/bin/env bash
# Setup development environment for FIT-OCR
set -euo pipefail

echo "[setup] creating virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

echo "[setup] installing package in editable mode..."
pip install -e ".[dev,cloud]"

echo "[setup] downloading models..."
bash scripts/fetch_models.sh

echo "[setup] done. activate with: source .venv/bin/activate"
