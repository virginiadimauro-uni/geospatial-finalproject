# Madrid Airbnb — Geospatial Analysis

This repository provides a reproducible geospatial workflow to study Airbnb prices in Madrid using Inside Airbnb data. The analysis combines data preparation, OLS and spatial econometric models (SAR/SEM), and map-based inspection of residual patterns.

Research question: to what extent does location (accessibility + neighbourhood context) explain nightly prices beyond listing/host characteristics, and when are spatial models preferable to OLS?

## Requirements

- macOS/Linux
- `micromamba` (recommended) or `conda`
- internet connection to download InsideAirbnb data

## Full Reproduction from Scratch

Run all commands from the project root.

### 1) Reproducible environment

```bash
micromamba env create -f environment/environment.yml
micromamba activate geo
```

If the environment already exists:

```bash
micromamba activate geo
```

### 2) Raw data download + checksum validation

Raw files are not versioned in this repository. Download them with:

```bash
python scripts/00_download_data.py
```

The script:
- downloads Madrid snapshot (InsideAirbnb, 2025-09-14),
- extracts required `.gz` files,
- stores raw files in `data/original/`,
- writes `data/original/checksums.sha256`,
- validates against `data/original/checksums_expected.sha256`.

### 3) Preprocessing (authoritative notebook)

```bash
jupyter execute notebooks/05_final_pipeline.ipynb --inplace
```

This generates cleaned datasets in `data/processed/`.

### 4) Model analysis and diagnostics

```bash
python scripts/03_ols_price_analysis.py
python scripts/04_spatial_autocorr_morans_i.py
python scripts/05_lm_diagnostic_tests.py
python scripts/06_morans_i_subset_consistency_check.py
python scripts/07_spatial_models_sar_sem.py
```

Main outputs are written to `outputs/tables/`.

### 5) Web map layer preparation

```bash
python scripts/07b_extract_residuals.py
python scripts/08_prepare_map_layers.py
```

This generates:
- `outputs/tables/residuals_for_map.csv`
- `data/processed/map_points_sample.geojson`
- `data/processed/map_grid_cells.geojson`

### 6) Launch web map

```bash
bash webmap/run.sh
```

or:

```bash
streamlit run webmap/app.py
```

### 7) Final report

The final PDF artifact is included at:

- `reports/GeospatialProject.pdf`

## Expected structure

```text
geospatial-project/
├── README.md
├── .gitignore
├── environment/
│   └── environment.yml
├── data/
│   ├── original/
│   │   ├── .gitkeep
│   │   └── checksums_expected.sha256
│   └── processed/
│       └── .gitkeep
├── notebooks/
│   └── 05_final_pipeline.ipynb
├── scripts/
│   ├── 00_download_data.py
│   ├── 03_ols_price_analysis.py
│   ├── 04_spatial_autocorr_morans_i.py
│   ├── 05_lm_diagnostic_tests.py
│   ├── 06_morans_i_subset_consistency_check.py
│   ├── 07_spatial_models_sar_sem.py
│   ├── 07b_extract_residuals.py
│   └── 08_prepare_map_layers.py
├── src/
├── outputs/
│   ├── .gitkeep
│   ├── figures/.gitkeep
│   ├── logs/.gitkeep
│   ├── metrics/.gitkeep
│   └── tables/.gitkeep
├── reports/
│   ├── GeospatialProject.pdf
│   ├── figures/.gitkeep
│   └── maps/.gitkeep
└── webmap/
    ├── app.py
    ├── run.sh
    └── runtime.txt
```