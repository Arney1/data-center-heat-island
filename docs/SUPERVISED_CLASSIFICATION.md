# Supervised classification: from GEE labels to two-site maps

This is a runnable workflow, not a claim that real reference labels are already
available. Start with one year (for example 2025) for both sites. Extend to other
years only with appropriate same-year reference interpretation.

## 1. Understand the input

Your LST time-series CSV contains zone averages. Classification needs individual
pixels with spectral features and a known reference class. An example reference
is a small homogeneous patch that you identify as cropland in dated imagery.
The RF/SVM learns these class relationships and predicts other pixels.

Use four land-cover classes throughout the project:

| ID | Class | Examples |
|---|---|---|
| 1 | Vegetation / agriculture | Irrigated field, grass, trees |
| 2 | Built-up | Roofs, paved surfaces; not necessarily a data center |
| 3 | Bare soil / fallow | Exposed soil, unplanted field |
| 4 | Water | Pond, canal, open water |

Collect examples throughout the campus **and surrounding AOI**, not just roofs.
Distribute each class across at least five independent spatial groups if using
five folds. More pixels within one polygon do not create more independent sites.
Keep polygons small, homogeneous, mutually nonoverlapping, and away from mixed
edges. Dated, higher-resolution imagery is preferable for reference interpretation.

## 2. Open the supplied GEE script

Copy `gee_scripts/02_supervised_land_cover.js` into Earth Engine Code Editor.
It already includes the configured campus geometries for both sites.

Set these parameters near the top:

```javascript
var SITE_ID = 'h5_quincy2'; // or 'aws_pdx'
var YEAR = 2025;
var INCLUDE_THERMAL = false;
```

Click Run. With no reference labels, it displays the AOI and RGB composite and
prints the next step. The yellow AOI is a **2.5 km buffer from the campus edge**.
Classification covers that whole AOI, not just the campus.

The composite is a June–September median. Optical preprocessing masks fill,
dilated cloud, cirrus, cloud, shadow, snow, and radiometric saturation. Reflectance
scaling and offsets are applied. Optical classification does not require valid
thermal bands; enabling thermal exports also requires valid LST/EMIS pixels.

The composite RGB helps navigation; record the actual dated imagery used to
assign reference classes. Do not invent a date from the undated satellite basemap.

## 3. Draw and record reference areas

In Code Editor, create a geometry import named **reference_polygons**, imported
as a **FeatureCollection**. Draw separate polygons for homogeneous areas across
the AOI. Each feature must have these properties:

| Property | Example | Meaning |
|---|---|---|
| `land_cover_class` | `1` (numeric) | One of the four IDs above |
| `reference_id` | `quincy_field_01` | Stable ID for the reference region |
| `reference_date` | `2025-07-12` | Date of the imagery/observation used for the label |
| `reference_source` | Actual image ID or citation | Traceable source of the interpretation |

If your drawing layer only provides shared properties, use separate collections
for the reference areas and combine them in code. For example, import a drawn
Geometry named `field_01`, then create a feature explicitly:

```javascript
// Illustration of the structure. Fill the date/source from real evidence.
var reference_polygons = ee.FeatureCollection([
  ee.Feature(field_01, {
    land_cover_class: 1,
    reference_id: 'quincy_field_01',
    reference_date: 'REPLACE_WITH_REAL_2025_DATE',
    reference_source: 'REPLACE_WITH_ACTUAL_IMAGE_ID_OR_CITATION'
  })
  // Add separate features for additional reference areas in ALL four classes.
]);
```

Do not keep both a Geometry import and a conflicting variable with the same name.
`reference_polygons` must be a FeatureCollection; `field_01` is a Geometry.
The illustration is intentionally incomplete: one vegetation feature cannot
support four-class training. Never use example placeholder dates as real evidence.

Alternatively, upload an annotated table asset with these properties and set
`LABEL_ASSET` in the supplied script to its asset ID. Leave the interactive
`reference_polygons` import absent when using that route.

Reference dates must match YEAR. Keep the same reference_id for the same physical
region across years so all its pixels remain grouped during validation.

## 4. Export pixels and full-area maps

Run again after supplying labels. The script checks that all labels have required
properties, lie/intersect within the AOI, use the selected year, and cover all four
classes. Polygons should stay inside the AOI. It creates these tasks:

- `SITE_reference_pixels_YEAR`: CSV of calibrated optical features, labels,
  coordinates, site/year, and provenance.
- `SITE_rf_landcover_YEAR`: full-AOI RF class GeoTIFF, **validation pending**.
- `SITE_optical_features_YEAR`: calibrated feature GeoTIFF for the exact
  Python-trained model. With INCLUDE_THERMAL enabled it also contains LST/EMIS.
- `SITE_rf_zonal_area_YEAR`: class areas by campus and distance zone, as GeoJSON.

Open **Tasks**, click **Run** on the exports, and download them from Google Drive.
The script deliberately does not present training-set accuracy as validation.
The RF preview uses all supplied labels and is a separate GEE estimator from
the Python RF; do not attach the Python model's scores directly to that estimator.
To use the exact Python model, classify the exported feature raster in step 6.

CSV exports sample at 30 m on a Landsat optical grid. Overlapping reference
polygons can export duplicate pixel records; the Python loader rejects duplicates.
If this happens, correct the polygons rather than arbitrarily keeping one label.
Only valid optical pixels are sampled. For thermal ablation set INCLUDE_THERMAL
to true and use that same common-validity CSV for every compared feature variant.

Repeat the process for the other SITE_ID, using that site's own reference areas.
Save the CSVs with the filenames in the README. An imported FeatureCollection
can be saved as an asset for reuse; preserve its dates and source properties.

## 5. Train, validate, and decide the model scope

From the project directory, with the virtual environment active:

```bash
python -m dip_pipeline.ml.runner_ml train --csv data/processed/reference_pixels_aws_pdx.csv --site aws_pdx
python -m dip_pipeline.ml.runner_ml train --csv data/processed/reference_pixels_h5_quincy2.csv --site h5_quincy2
```

These are two per-site models. For one shared model over both AOIs:

```bash
python -m dip_pipeline.ml.runner_ml train --csv data/processed/reference_pixels_aws_pdx.csv data/processed/reference_pixels_h5_quincy2.csv --site pooled
```

Pooled spatial validation can include training blocks from both sites. It does
not test transfer to a completely unseen city. For that test:

```bash
python -m dip_pipeline.ml.runner_ml train --csv data/processed/reference_pixels_aws_pdx.csv data/processed/reference_pixels_h5_quincy2.csv --site pooled --validation leave_site_out --test-site h5_quincy2
```

Spatial folds are shared by RF, SVM, and the spectral baseline. Reference polygons
that cross blocks connect those blocks, preventing the same reference area from
appearing in both train and test. Grouping can leave too few independent regions;
collect more separated examples or justify fewer folds, not a random fallback.
No exclusion gap is enforced; assess the block size and residual dependence.

Review `metrics.json` and `heldout_predictions.csv`, class support, confusion
matrices, and per-site scores. Accuracy alone is insufficient. Class-area exports
are mapped areas, not statistically error-adjusted estimates.

## 6. Apply the saved Python classifier to a full AOI

Use `predict-raster` as shown in the README. Match every feature name, order,
calibration, and compositing choice. This applies the exact fitted RF or SVM to
all valid pixels in the feature raster. Class 0 denotes no data.

For a pooled model, run prediction once on the Boardman feature raster and once
on the Quincy feature raster using the same model path. Store the outputs in
that run's directory. The dashboard shows the matching site-tagged raster separately
from the held-out sample-point map. For a transfer model, the target site remains
excluded from the saved model's training data.

## What is complete and what still needs your input?

The software for sampling/export, model validation, inference, and dashboard
display is implemented. A development run on existing legacy Boardman data is
available. Real validated maps for both sites require the reference areas you
interpret and the GEE exports from your account. Neither labels nor GEE access
can be reconstructed from the existing LST chart.

Reference: [Earth Engine supervised classification](https://developers.google.com/earth-engine/guides/classification).
