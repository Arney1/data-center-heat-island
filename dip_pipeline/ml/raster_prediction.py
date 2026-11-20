"""Windowed inference using a trusted Python model and a georeferenced feature stack."""

import json
from pathlib import Path

import joblib
import numpy as np

from ..config import SITES


def classify_raster(model_path, raster_path, output_path, *, site_id, year,
                    model_type="rf", band_order=None):
    import rasterio
    from rasterio.windows import Window

    if site_id not in SITES or model_type not in ("rf", "svm"):
        raise ValueError("Supply a configured site and rf or svm model.")
    if not 2013 <= year <= 2026:
        raise ValueError("year must be in 2013–2026.")
    # Only load trusted joblib files; never accept arbitrary uploaded model files.
    bundle = joblib.load(model_path)
    names = bundle["features"]
    model_name = "Random Forest" if model_type == "rf" else "Support Vector Machine"
    output_path = Path(output_path)
    if output_path.exists():
        raise ValueError("Raster output already exists. Choose a new path.")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(raster_path) as source:
        if source.crs is None:
            raise ValueError("Input raster needs a CRS.")
        available = list(band_order) if band_order is not None else list(source.descriptions)
        if len(available) != source.count or any(not name for name in available):
            raise ValueError("Supply --band-order when the GeoTIFF has no band descriptions.")
        if len(set(available)) != len(available) or not set(names).issubset(available):
            raise ValueError("Raster band names must be unique and contain every trained feature.")
        indices = [available.index(name) + 1 for name in names]
        profile = source.profile.copy()
        profile.update(count=1, dtype="uint8", nodata=0, compress="deflate", driver="GTiff",
                       tiled=True, blockxsize=256, blockysize=256, photometric="palette", interleave="band")
        with rasterio.open(output_path, "w", **profile) as target:
            target.write_colormap(1, {0: (0, 0, 0, 0), 1: (44, 160, 44, 255),
                                     2: (214, 39, 40, 255), 3: (188, 189, 34, 255), 4: (31, 119, 180, 255)})
            for row in range(0, source.height, 256):
                for col in range(0, source.width, 256):
                    window = Window(col, row, min(256, source.width-col), min(256, source.height-row))
                    data = source.read(indices, window=window, masked=True).astype(np.float64)
                    valid = ~np.ma.getmaskarray(data).any(axis=0) & np.isfinite(data.filled(np.nan)).all(axis=0)
                    result = np.zeros(valid.shape, dtype="uint8")
                    if valid.any():
                        values = np.asarray(data.data[:, valid]).T
                        result[valid] = bundle["models"][model_name].predict(values).astype("uint8")
                    target.write(result, 1, window=window)
            target.set_band_description(1, "land_cover_class")
            target.update_tags(site_id=site_id, year=str(year), model=model_name,
                claim_status=bundle["metadata"]["claim_status"],
                dataset_sha256=bundle["metadata"]["dataset_sha256"])
    report = {"site_id": site_id, "year": year, "model": model_name,
              "claim_status": bundle["metadata"]["claim_status"],
              "features": names, "source_raster": str(raster_path),
              "model_dataset_sha256": bundle["metadata"]["dataset_sha256"],
              "nodata": 0, "classes": {1: "vegetation", 2: "built-up", 3: "bare soil", 4: "water"}}
    output_path.with_suffix(".json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report
