"""Reproducible local artifact audit; does not authenticate or fetch imagery."""
import argparse
import json
from pathlib import Path

import pandas as pd
from pyproj import Geod
from shapely.geometry import Polygon
from shapely.ops import unary_union

from .config import PROCESSED_DATA_DIR, SITES
from .timeseries import load_zonal_timeseries
from .ml.dataset import MLDatasetManager


def audit_project():
    data = Path(PROCESSED_DATA_DIR)
    report = {"scope": "local artifacts and geometry, not historical-image or independent-label verification",
              "sites": {}, "legacy_ml": {}}
    geod = Geod(ellps="WGS84")
    for site_id, site in SITES.items():
        campus = Polygon(site["campus_bounds"])
        roofs = [Polygon(ring) for ring in site["buildings_multipolygon"]]
        union = unary_union(roofs).intersection(campus)
        campus_area = abs(geod.geometry_area_perimeter(campus)[0]) / 10000
        roof_area = abs(geod.geometry_area_perimeter(union)[0]) / 10000
        sum_roofs = sum(abs(geod.geometry_area_perimeter(r.intersection(campus))[0]) for r in roofs) / 10000
        entry = {"chronology_status": site["chronology_status"],
                 "geometry_valid": campus.is_valid and all(r.is_valid for r in roofs),
                 "digitized_campus_ha": campus_area, "union_clipped_roofs_ha": roof_area,
                 "overlap_double_count_ha": max(0, sum_roofs - roof_area),
                 "legacy_campus_ha": site["campus_ha"], "legacy_roofs_ha": site["buildings_ha"]}
        reference_path = data / f"reference_pixels_{site_id}.csv"
        if reference_path.exists():
            try:
                reference = MLDatasetManager(reference_path, site_id=site_id)
                entry["label_status"] = "reference metadata pass schema checks; interpretation still requires review"
                entry["n_reference_pixels"] = len(reference.df)
            except (ValueError, OSError) as error:
                entry["label_status"] = f"reference CSV rejected: {error}"
        else:
            entry["label_status"] = "independent reference samples not supplied in the repository"
        filename = "zonal_lst_timeseries_2013_2026.csv" if site_id == "aws_pdx" else "h5_quincy2_timeseries.csv"
        path = data / filename
        if path.exists():
            try:
                frame = load_zonal_timeseries(path, site_id)
                entry["timeseries"] = {"status": "schema_valid", "n_rows": len(frame),
                                       "missing_values": frame.isna().sum().to_dict()}
            except (ValueError, OSError) as error:
                entry["timeseries"] = {"status": "invalid", "error": str(error)}
        else:
            entry["timeseries"] = {"status": "not_available"}
        report["sites"][site_id] = entry
    old_csv = data / "ml_feature_dataset.csv"
    if old_csv.exists():
        frame = pd.read_csv(old_csv)
        report["legacy_ml"] = {"n_samples": len(frame),
            "missing_metadata": sorted({"site_id", "data_source", "label_source", "reference_id",
                                        "reference_date", "reference_source"} - set(frame)),
            "claim_status": "unverified_legacy_not_field_accuracy"}
    report["research_blockers"] = ["Review independent reference-label quality and spatial coverage at each site.",
        "Quincy footprint identity and construction chronology remain unverified.",
        "The old 100% accuracy result uses a random split and unknown data provenance.",
        "Image counts, control suitability, and historical construction dates are not established by local CSVs."]
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output")
    args = parser.parse_args(argv)
    report = audit_project()
    content = json.dumps(report, indent=2, allow_nan=False)
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(content, encoding="utf-8")
    print(content)
    return report


if __name__ == "__main__":
    main()
