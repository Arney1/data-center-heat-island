# Classification and application audit

Audit date: 20 November 2026. Scope: current repository, local artifacts,
configured geometry, supervised-classification code, and dashboard behavior.
No historical-image verification or live GEE run was performed. Independent
reference samples and local GEE credentials are not available.

## Findings and changes

| Finding | Impact | Resolution |
|---|---|---|
| One implicit legacy training file; no site metadata | A generic run could be mistaken for both sites | Explicit CSV and site scope; pooled mode requires both site IDs |
| Random pixel split; spatial groups unused | Nearby pixels could leak between train and test | Stratified spatial-group folds; merge blocks connected by a reference region |
| Old 100% scores without source metadata | Unsupported field-accuracy claims | Keep original artifacts, exclude them from current results, require development overrides |
| Threshold-derived labels in live fetcher | Evaluates imitation of spectral rules | Independent reference-label schema plus GEE reference-polygon sampling workflow |
| Prediction silently trained a model | Inference could change the model or fetch data | Explicit training; save/load fitted RF and scaled SVM |
| No full-AOI Python raster inference | Sample scores could be mistaken for a land-cover map | Windowed GeoTIFF prediction, nodata, CRS, feature-order and provenance handling |
| Boardman-only menus and Quincy early stop | Different capabilities and misleading site scope | One English navigation, per-site data loading, no cross-site fallback |
| Fixed scientific success statements | Unverified chronology and heat attribution | Display provenance/limitations and keep old DIP results as legacy artifacts |
| Artifact runner declared everything verified | File reads were confused with empirical verification | Replace with reproducible local audit and explicit research blockers |
| README only had Windows guidance | Incomplete onboarding | English README, Linux/macOS and PowerShell setup, common CLI commands |

## Geometry measurements

Calculated on the configured digitized polygons using WGS84 geodesic area;
roof polygons are merged and clipped to the campus. These are measurements of
the supplied geometry, not verification of facility boundaries.

| Site | Digitized campus | Union/clipped roofs | Roof overlap double counting |
|---|---:|---:|---:|
| Boardman | 38.236 ha | 13.306 ha | 0.000 ha |
| Quincy | 2.785 ha | 1.510 ha | 0.233 ha |

Legacy Quincy metadata stated 2.93 ha campus and 1.35 ha roofs. These figures
are not consistent with the current digitization. Six roof features also do not
establish six separate data halls. Legacy metadata is preserved for traceability
and is no longer presented as a freshly verified measurement.

Machine-readable audit: `data/processed/classification/local_audit.json`.
Recreate with `python -m dip_pipeline.audit --output PATH`.

## Executed development classification

Dataset: 1,200 legacy pixels, explicitly assigned to Boardman for a software
check. Source, labeling method, dates, and reference IDs are missing; **these
numbers are not verified research accuracy**.

- Five spatial grouped folds; 500 m approximate metric blocks; seed 42.
- Default optical bands B2–B7 and NDVI/NDBI/MNDWI/albedo; no thermal predictors.
- RF: OA 0.9917, macro-F1 approximately 0.9919.
- SVM: OA 0.9925, macro-F1 approximately 0.9918.
- Fixed spectral baseline: OA 0.8325, macro-F1 approximately 0.8607.
- Reports and held-out sample predictions are stored under
  `data/processed/classification/aws_pdx_development_optical_spatial/`.
- Fitted model serialization was produced locally and is ignored by Git.

High development scores do not resolve unknown data provenance. No Quincy or
pooled research score is reported without the corresponding samples. Synthetic
multi-site fixtures exercise cross-site isolation in tests only.

## Validation and remaining limits

Automated checks cover provenance and missing-data rejection, duplicate pixels,
polygon-connected blocks and repeated years, fold separation, transfer isolation,
saved-model prediction, class raster georeferencing/nodata/colors, and all five
dashboard pages at both sites. JavaScript passes a local Node syntax check.
See the final test command in the README; test fixtures are not research samples.

Spatial grouping reduces leakage but does not enforce a geographic buffer gap.
The default 500 m block size requires sensitivity analysis. The grid uses a
fixed local distance approximation for these two sites, not a map-area CRS.
Reported macro-F1 averages the fixed four-class schema, including zero support
classes; review class support alongside each score. Fold-score spread is
descriptive, not a confidence interval. Hyperparameters are fixed rather than
tuned on evaluation data.

Still required for empirical completion:

1. Dated, independently interpreted reference regions across both AOIs.
2. Actual GEE sample and feature-raster exports for each site/year.
3. Review of label quality, coverage, spatial dependence, and block sensitivity.
4. Validation of Quincy footprint identity and construction chronology before
   before/after or causal language.
5. Separate checks of regional references, industrial controls, and historical
   image counts before treating legacy DIP outputs as verified results.

Technical basis: [Earth Engine classification](https://developers.google.com/earth-engine/guides/classification),
[grouped validation](https://scikit-learn.org/stable/modules/cross_validation.html),
and [pipeline leakage prevention](https://scikit-learn.org/stable/common_pitfalls.html).
