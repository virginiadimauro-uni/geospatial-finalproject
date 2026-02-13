#!/bin/bash

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "[INFO] Project root: $PROJECT_ROOT"

if command -v micromamba >/dev/null 2>&1; then
    PY_RUNNER="micromamba run -n geo python"
    STREAMLIT_RUNNER="micromamba run -n geo streamlit"
    echo "[INFO] Using environment runner: micromamba run -n geo"
else
    PY_RUNNER="python"
    STREAMLIT_RUNNER="streamlit"
    echo "[WARNING] micromamba not found; using current shell environment"
fi

if [ ! -f "data/processed/model_sample.parquet" ]; then
    if [ -f "data/processed/listings_clean.parquet" ]; then
        echo "[INFO] model_sample.parquet missing; rebuilding from listings_clean.parquet"
        $PY_RUNNER -c "from pathlib import Path; from src.prep import load_listings_processed, build_model_df; p=Path('data/processed/listings_clean.parquet'); out=Path('data/processed/model_sample.parquet'); df=load_listings_processed(p); build_model_df(df, out_path=out); print('[INFO] Rebuilt', out)"
    else
        echo "[ERROR] Missing data/processed/model_sample.parquet"
        echo "[ERROR] Missing data/processed/listings_clean.parquet"
        echo "[ERROR] Run first: jupyter execute notebooks/05_final_pipeline.ipynb --inplace"
        exit 1
    fi
fi

if [ ! -f "outputs/tables/residuals_for_map.csv" ]; then
    echo "[INFO] Generating outputs/tables/residuals_for_map.csv"
    $PY_RUNNER scripts/07b_extract_residuals.py
fi

if [ ! -f "data/processed/map_points_sample.geojson" ] || [ ! -f "data/processed/map_grid_cells.geojson" ]; then
    echo "[INFO] Generating map layers in data/processed/"
    $PY_RUNNER scripts/08_prepare_map_layers.py
fi

echo "[INFO] Launching webmap on http://localhost:8501"
$STREAMLIT_RUNNER run webmap/app.py
