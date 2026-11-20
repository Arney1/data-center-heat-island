"""Validated pixel datasets and leakage-resistant spatial groups."""
from pathlib import Path
import numpy as np
import pandas as pd
from ..config import SITES

SPECTRAL_BANDS = [f"SR_B{i}" for i in range(2, 8)]
SPECTRAL_INDICES = ["NDVI", "NDBI", "MNDWI", "Albedo"]
THERMAL_FEATURES = ["LST", "EMIS"]
# Thermal predictors are optional to avoid baking temperature into land-cover labels.
ALL_CLASSIFICATION_FEATURES = SPECTRAL_BANDS + SPECTRAL_INDICES
REGRESSION_FEATURES = ["NDVI", "NDBI", "Albedo", "elevation", "distance_dc_km"]
CLASS_NAMES = {1: "Vegetation / Agriculture", 2: "Built-up", 3: "Bare Soil / Fallow", 4: "Water"}
CLASS_COLORS = {1: "#2ca02c", 2: "#d62728", 3: "#bcbd22", 4: "#1f77b4"}
REFERENCE_LABEL_SOURCES = {"manual_dated_imagery", "field_reference"}


def spatial_groups(frame, block_size_m=500):
    """Merge blocks connected by a reference polygon, including repeated years.

    The fixed approximate local metric grid is for grouping these sites,
    not for measuring area. No buffer gap between adjacent groups is enforced.
    """
    if block_size_m <= 0:
        raise ValueError("block_size_m must be positive.")
    x = frame.longitude.to_numpy() * 111320 * np.cos(np.deg2rad(46.5))
    y = frame.latitude.to_numpy() * 111320
    blocks = [f"{s}:{int(a)}:{int(b)}" for s, a, b in
              zip(frame.site_id, np.floor(x / block_size_m), np.floor(y / block_size_m))]
    parents = {b: b for b in blocks}

    def find(key):
        while parents[key] != key:
            parents[key] = parents[parents[key]]
            key = parents[key]
        return key

    if "reference_id" in frame:
        first = {}
        for site, ref, block in zip(frame.site_id, frame.reference_id, blocks):
            if pd.isna(ref) or not str(ref).strip():
                continue
            key = (site, str(ref))
            if key in first:
                parents[find(block)] = find(first[key])
            else:
                first[key] = block
    return np.asarray([find(b) for b in blocks])


class MLDatasetManager:
    """Read explicitly supplied pixels; never fetch or synthesize on load."""
    def __init__(self, csv_path=None, *, frame=None, site_id=None,
                 allow_unverified=False, allow_synthetic=False, features=None):
        self.csv_path = str(csv_path) if csv_path is not None else None
        if frame is None:
            if csv_path is None or not Path(csv_path).is_file():
                raise FileNotFoundError("Provide a pixel-sample CSV; zonal LST CSVs are not training data.")
            frame = pd.read_csv(csv_path)
        self.df = frame.copy().reset_index(drop=True)
        self.features = list(features or ALL_CLASSIFICATION_FEATURES)
        self._validate(site_id, allow_unverified, allow_synthetic)

    def _validate(self, site_id, allow_unverified, allow_synthetic):
        df = self.df
        if df.empty:
            raise ValueError("The pixel dataset is empty.")
        required = {"longitude", "latitude", "year", "land_cover_class", *self.features, *SPECTRAL_INDICES}
        missing = required - set(df)
        if missing:
            raise ValueError("Missing pixel-sample columns: " + ", ".join(sorted(missing)))
        if "site_id" not in df:
            if not allow_unverified or site_id not in SITES:
                raise ValueError("Missing site_id. Legacy data require an explicit site and --allow-unverified.")
            df["site_id"] = site_id
        if df.site_id.isna().any() or not set(df.site_id).issubset(SITES):
            raise ValueError("Unknown or missing site_id.")
        if site_id is not None and not df.site_id.eq(site_id).all():
            raise ValueError(f"Dataset contains rows outside selected site {site_id}.")
        for column in required:
            df[column] = pd.to_numeric(df[column], errors="raise")
            if not np.isfinite(df[column]).all():
                raise ValueError(f"Missing or non-finite values in {column}; do not fill invalid pixels with zero.")
        if not df.longitude.between(-180, 180).all() or not df.latitude.between(-90, 90).all():
            raise ValueError("Coordinates must be WGS84 longitude/latitude.")
        if (df.year % 1 != 0).any() or not df.year.between(2013, 2026).all():
            raise ValueError("year must be an integer in the configured observation period, 2013–2026.")
        if not df.land_cover_class.isin(CLASS_NAMES).all():
            raise ValueError("land_cover_class must use IDs 1, 2, 3, 4.")
        df["land_cover_class"] = df.land_cover_class.astype(int)
        if df.duplicated(["site_id", "year", "longitude", "latitude"]).any():
            raise ValueError("Duplicate site/year/pixel rows; remove overlapping label polygons.")
        for column in ("data_source", "label_source"):
            if column not in df:
                df[column] = "unverified_legacy"
            if df[column].isna().any() or df[column].astype(str).str.strip().eq("").any():
                raise ValueError(f"Missing values in {column}.")
        synthetic_rows = df.data_source.str.contains("synthetic|demo", case=False, regex=True)
        reference_rows = df.data_source.eq("gee_landsat") & df.label_source.isin(REFERENCE_LABEL_SOURCES)
        verified = reference_rows.all()
        if synthetic_rows.any() and not allow_synthetic:
            raise ValueError("Synthetic samples require --allow-synthetic; results are development-only.")
        if (~reference_rows & ~synthetic_rows).any() and not allow_unverified:
            raise ValueError("Labels/provenance are not independent reference data. Supply dated labels or explicitly use --allow-unverified.")
        if reference_rows.any():
            reference = df.loc[reference_rows]
            for column in ("reference_id", "reference_date", "reference_source"):
                if column not in reference or reference[column].isna().any() or reference[column].astype(str).str.strip().eq("").any():
                    raise ValueError(f"Independent labels require {column} for every row.")
            if not pd.to_datetime(reference.reference_date, errors="raise").dt.year.eq(reference.year).all():
                raise ValueError("Reference dates must match the sampled composite year.")
            if reference.groupby(["site_id", "year", "reference_id"]).land_cover_class.nunique().gt(1).any():
                raise ValueError("A homogeneous reference polygon cannot have conflicting classes in the same year.")
        self.claim_status = "reference_labels_spatial_validation" if verified else "development_only"
        self.provenance = {"claim_status": self.claim_status,
                           "data_sources": sorted(df.data_source.unique().tolist()),
                           "label_sources": sorted(df.label_source.unique().tolist()),
                           "site_ids": sorted(df.site_id.unique().tolist()), "n_samples": len(df)}

    def get_spatial_blocks(self, block_size_m=500):
        return spatial_groups(self.df, block_size_m)
