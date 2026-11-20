# Data Center LST and Land-Cover Analysis

An observational remote-sensing project for **AWS PDX Boardman** (`aws_pdx`) and
**H5 Quincy II** (`h5_quincy2`), using Landsat 8/9 Collection 2 Level-2.
The configured observation window is June–September, 2013–2026.

The project explores surface temperature and land-cover patterns. It does not
directly measure server waste heat, AI workload, or a causal effect of operations.

## Current status

| Component | Implemented / available | Remaining research requirement |
|---|---|---|
| LST dashboard | Same English navigation for both sites; validated per-site CSV loading | Quincy CSV must be uploaded or saved locally |
| Geometry audit | Geodesic area, union of overlapping roofs, chronology flags | Verify digitized footprints against dated imagery and facility records |
| Supervised classification | RF, scaled RBF-SVM, fixed spectral baseline, spatial grouped validation, pooled and leave-site-out modes | Independent, dated reference samples from both sites |
| Inference | Saved Python models; pixel CSV and full feature-GeoTIFF classification | Export real AOI feature stacks from GEE |
| GEE workflow | Labeled-pixel export, full-AOI RF preview, class raster and zone-area export | Supply reference polygons and run in your authenticated GEE account |
| Available run | 1,200 legacy Boardman pixels evaluated with five spatial folds | **Development only**: source and reference-label metadata are missing |
| Historical DIP artifacts | Kept for traceability in the dashboard | Their image provenance, chronology, and controls remain unverified |

The software workflow is implemented and tested. **Validated supervised
classification of both real sites is not complete**: the repository does not
contain independent reference labels or a Quincy pixel dataset. No such data
are fabricated. The old 100% random-split accuracy JSON is retained but excluded
from the current classification dashboard.

Read the [audit report](docs/CLASSIFICATION_AUDIT.md) and
[step-by-step GEE/classification guide](docs/SUPERVISED_CLASSIFICATION.md).

## What does “whole-area classification” mean?

Classification covers the **full AOI around each data center**: the campus plus
a 2.5 km buffer measured from its boundary, including neighboring land. It assigns:

1. Vegetation / agriculture
2. Built-up land
3. Bare soil / fallow
4. Water

Built-up land is not automatically a data center. Facility identity comes from
the separately verified campus geometry.

Two training scopes are supported:

- **Per-site:** train/evaluate a separate model for Boardman or Quincy.
- **Pooled:** combine labeled pixels from both sites into one model; retain
  site IDs, per-site evaluation, and separate classified maps.

A pooled model does **not** classify the entire region between the two cities.
Leave-site-out evaluation trains on one site and tests on the other, without
refitting the saved transfer model on its test site.

## Installation

Use **Python 3.11 or newer**. Python 3.14 was used for the local checks; choose a
version with binary wheels supported by your platform. Run from the repository root.

### Linux / macOS

```bash
git clone https://github.com/Arney1/data-center-heat-island.git
cd data-center-heat-island
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m streamlit run app/app.py
```

On Debian/Ubuntu, if creating a virtual environment fails because the venv module
is missing, install it with `sudo apt install python3-venv`, then retry.
To leave the environment, run `deactivate`. In a new terminal, activate it again.

### Windows PowerShell

```powershell
git clone https://github.com/Arney1/data-center-heat-island.git
cd data-center-heat-island
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app/app.py
```

If you already have a checkout or virtual environment, reuse it.
Activation on Windows is optional; the explicit executable paths avoid
PowerShell activation-policy issues. In the commands below, `python` means the
activated virtual environment's interpreter. Without activation on Windows,
replace it with `.\.venv\Scripts\python.exe`.

## Use the dashboard

Open the local URL printed by Streamlit, normally `http://localhost:8501`.

Both sites have the same pages: Overview, Study area, LST & spectral time series,
Supervised classification, and Saved DIP artifacts. Missing Quincy data never
falls back to Boardman results. No GEE credentials are needed to browse saved data.

Time-series files:

- Boardman: `data/processed/zonal_lst_timeseries_2013_2026.csv`
- Quincy: `data/processed/h5_quincy2_timeseries.csv`, or upload it in the sidebar.

Required columns: `tahun,zona,LST,LSTanom,NDVI,NDBI,EMIS`.
An optional `site_id` must match the selected site. If omitted, the dashboard
assigns the selected site; verify the CSV's origin yourself. Duplicate year/zone
rows and nonnumeric values are rejected. Missing statistics remain missing.

A time-series CSV contains **zone averages**, not labeled pixels, and cannot train
a land-cover classifier. LST and LST anomalies use °C; they are not air temperature.

## Audit local artifacts

```bash
python -m dip_pipeline.audit --output data/processed/classification/local_audit.json
python -m dip_pipeline.ml.runner_ml audit --csv data/processed/ml_feature_dataset.csv
```

The audit does not authenticate to GEE or silently fetch or generate data.
The compatibility command `python -m dip_pipeline.runner` runs the same local
artifact audit. It no longer claims that loading files verifies all methods.

## Collect actual classification data in GEE

Open `gee_scripts/02_supervised_land_cover.js` in the
[Earth Engine Code Editor](https://code.earthengine.google.com/).
Choose the site and year, inspect the RGB composite, and import reference
polygons interpreted from dated imagery. The detailed guide explains the required
properties, spatial sampling, exports, and full-area map.

Download the labeled CSV exports as, for example:

- `data/processed/reference_pixels_aws_pdx.csv`
- `data/processed/reference_pixels_h5_quincy2.csv`

Keep their original provenance columns. Every reference pixel needs:
`site_id,year,longitude,latitude,land_cover_class,data_source,label_source,`
`reference_id,reference_date,reference_source`, plus the optical bands and indices.
Valid reference label sources are `manual_dated_imagery` and `field_reference`;
the feature source is `gee_landsat`. Recording these fields is not itself proof
that an interpretation is correct; review dates and reference quality.

The older Python fetcher's threshold labels are exploratory **pseudo-labels**,
not independent reference data. They require an explicit development override.

## Train and evaluate

Separate site:

```bash
python -m dip_pipeline.ml.runner_ml train --csv data/processed/reference_pixels_aws_pdx.csv --site aws_pdx
python -m dip_pipeline.ml.runner_ml train --csv data/processed/reference_pixels_h5_quincy2.csv --site h5_quincy2
```

One pooled model:

```bash
python -m dip_pipeline.ml.runner_ml train --csv data/processed/reference_pixels_aws_pdx.csv data/processed/reference_pixels_h5_quincy2.csv --site pooled
```

Train Boardman, test Quincy:

```bash
python -m dip_pipeline.ml.runner_ml train --csv data/processed/reference_pixels_aws_pdx.csv data/processed/reference_pixels_h5_quincy2.csv --site pooled --validation leave_site_out --test-site h5_quincy2
```

Reverse the test-site argument for the opposite direction.

Defaults: 5 spatial folds, 500 m blocks, fixed seed 42, RF/SVM and a fixed
NDVI/NDBI/MNDWI baseline on identical held-out samples. Blocks connected by the
same reference polygon are merged; repeated years stay in the same spatial group.
Too few independent groups/classes causes an error, never a random-split fallback.
500 m is a starting configuration, not a scientifically established decorrelation
distance; test sensitivity with `--block-size-m`. Adjacent blocks have no buffer gap.

Feature variants: `--features bands`, `--features optical` (default), or
`--features optical_thermal` (requires LST/EMIS). Use the same samples and fold
parameters when comparing variants. The CSV must retain spectral indices for the
fixed baseline even in the bands-only experiment. SVM scaling is fitted inside
each training fold. Hyperparameters are fixed, not tuned on test data.

Each run writes `metrics.json`, `heldout_predictions.csv`, and `models.joblib`
under `data/processed/classification/<run-name>/`. Reports contain provenance,
dataset fingerprint, fold membership, OA, macro-F1, Kappa, per-class metrics,
per-site scores, and descriptive RF feature importance. Existing nonempty output
directories are protected; use a fresh `--output` directory for a rerun.

### Reproduce the available development run

```bash
python -m dip_pipeline.ml.runner_ml train --csv data/processed/ml_feature_dataset.csv --site aws_pdx --allow-unverified --output data/processed/classification/boardman_development_rerun
```

This explicitly assigns the legacy dataset to Boardman and marks all results
**development_only**. Synthetic data require `--allow-synthetic` separately.
These overrides do not establish real classification accuracy and are not needed
for proper reference datasets.

## Classify a full feature GeoTIFF using the saved Python model

Export the optical feature stack from the GEE script and keep its band order.
For an optical Boardman model:

```bash
python -m dip_pipeline.ml.runner_ml predict-raster --model data/processed/classification/aws_pdx_optical_spatial/models.joblib --raster data/raw/aws_pdx_optical_features_2025.tif --site aws_pdx --year 2025 --output data/processed/classification/aws_pdx_optical_spatial/landcover_aws_pdx_2025.tif --band-order SR_B2 SR_B3 SR_B4 SR_B5 SR_B6 SR_B7 NDVI NDBI MNDWI Albedo
```

Use your actual paths/site/model. GEE may not preserve band descriptions, so the
explicit band order above is useful. The classifier handles windows, preserves
CRS/transform, keeps invalid pixels as class 0, and writes class IDs 1–4, colors,
and a provenance sidecar. Do not use raw digital-number bands: inputs must use the
same calibrated features and compositing as training. LST/EMIS models need those
additional bands. Full-area maps are separate from held-out validation samples.

The app previews tagged class rasters stored in the selected run directory.
Models and GeoTIFFs are ignored by Git; metrics and held-out predictions remain
reviewable. Share large artifacts separately or configure appropriate artifact
storage rather than committing credentials or large rasters.

For a pixel CSV instead:

```bash
python -m dip_pipeline.ml.runner_ml predict --model PATH_TO_TRUSTED_MODEL.joblib --csv PIXEL_FEATURES.csv --output PIXEL_PREDICTIONS.csv
```

Only load trusted local joblib artifacts; these files use Python serialization.

## Optional Python Earth Engine access

For Python fetching (not needed for the saved-data dashboard):

```bash
earthengine authenticate
```

Linux/macOS:

```bash
export EE_PROJECT="YOUR_REGISTERED_GEE_PROJECT"
```

PowerShell:

```powershell
$env:EE_PROJECT = 'YOUR_REGISTERED_GEE_PROJECT'
```

The project must be registered/enabled for Earth Engine. Authentication failures
do not trigger synthetic fallback. Do not commit tokens, service-account keys,
`.env`, or Streamlit secrets. The GEE JavaScript workflow runs in Code Editor
under your own account; saving its .js file is for reproducibility.

## Checks

```bash
python -m unittest discover -s tests -v
python -m pip check
```

The tests exercise provenance rejection, spatial/polygon grouping, cross-site
training isolation, serialization, pixel and raster inference, nodata/CRS, and
both sites' dashboard pages. Fixtures are synthetic and never become research data.
GEE JavaScript syntax is checked locally; live GEE execution needs your account,
imagery access, and reference polygons and has not been performed in this update.

## Scientific limits and sources

- The geodesic audit measures the configured polygons, not verified facility parcels.
- Quincy construction periods remain unset. Boardman's pre/post periods are legacy
  assumptions requiring evidence; ownership changes are not construction dates.
- Pixel-sample accuracy is not error-adjusted mapped area or proof of waste heat.
- Landsat's 30 m output grid does not create independent 30 m thermal observations.
- Independent samples, representative reference coverage, spatial sensitivity,
  and cross-site evaluation are needed before publication claims.

Technical references: [Earth Engine classification](https://developers.google.com/earth-engine/guides/classification),
[Landsat C2 L2](https://developers.google.com/earth-engine/datasets/catalog/LANDSAT_LC08_C02_T1_L2),
[scikit-learn grouped validation](https://scikit-learn.org/stable/modules/cross_validation.html),
and [pipeline/data-leakage guidance](https://scikit-learn.org/stable/common_pitfalls.html).
Historical planning documents in this repository are retained as plans, not
completion reports. See [Quincy chronology](docs/QUINCY_CHRONOLOGY_AUDIT.md)
and [the updated roadmap](docs/ML_AND_PAPER_ROADMAP.md).
