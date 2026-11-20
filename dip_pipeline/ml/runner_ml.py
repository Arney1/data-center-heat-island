"""Explicit training, audit, and inference CLI. No implicit GEE fetches."""
import argparse
import json
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from .dataset import (MLDatasetManager, ALL_CLASSIFICATION_FEATURES, SPECTRAL_BANDS,
                      THERMAL_FEATURES, CLASS_NAMES)
from .supervised_classification import LandCoverClassifier
from ..config import PROCESSED_DATA_DIR, SITES


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    train = commands.add_parser("train", help="Evaluate spatially, then fit models for inference.")
    train.add_argument("--csv", nargs="+", required=True)
    train.add_argument("--site", choices=[*SITES, "pooled"], required=True)
    train.add_argument("--features", choices=["bands", "optical", "optical_thermal"], default="optical")
    train.add_argument("--folds", type=int, default=5)
    train.add_argument("--block-size-m", type=float, default=500)
    train.add_argument("--validation", choices=["spatial", "leave_site_out"], default="spatial")
    train.add_argument("--test-site", choices=list(SITES))
    train.add_argument("--allow-unverified", action="store_true")
    train.add_argument("--allow-synthetic", action="store_true")
    train.add_argument("--output")
    audit = commands.add_parser("audit", help="Inspect dataset provenance without changing data.")
    audit.add_argument("--csv", required=True)
    predict = commands.add_parser("predict", help="Predict labeled or unlabeled pixel CSVs using a trusted local model.")
    predict.add_argument("--model", required=True)
    predict.add_argument("--csv", required=True)
    predict.add_argument("--output", required=True)
    raster = commands.add_parser("predict-raster", help="Classify a complete georeferenced feature GeoTIFF.")
    raster.add_argument("--model", required=True)
    raster.add_argument("--raster", required=True)
    raster.add_argument("--output", required=True)
    raster.add_argument("--site", choices=list(SITES), required=True)
    raster.add_argument("--year", type=int, required=True)
    raster.add_argument("--model-type", choices=["rf", "svm"], default="rf")
    raster.add_argument("--band-order", nargs="+")
    args = parser.parse_args(argv)
    try:
        if args.command == "predict-raster":
            from .raster_prediction import classify_raster
            report = classify_raster(args.model, args.raster, args.output,
                site_id=args.site, year=args.year, model_type=args.model_type, band_order=args.band_order)
            print(f"Saved classified raster: {args.output}; status={report['claim_status']}")
            return 0
        if args.command == "audit":
            df = pd.read_csv(args.csv)
            report = {"file": args.csv, "n_samples": len(df), "columns": df.columns.tolist(),
                      "missing_provenance_columns": sorted(
                          {"site_id", "data_source", "label_source", "reference_id", "reference_date",
                           "reference_source"} - set(df))}
            if "land_cover_class" in df:
                report["class_counts"] = {str(k): int(v) for k, v in df.land_cover_class.value_counts().items()}
            print(json.dumps(report, indent=2))
            return 0
        if args.command == "predict":
            # joblib uses pickle: only load artifacts produced locally or otherwise trusted.
            bundle = joblib.load(args.model)
            df = pd.read_csv(args.csv)
            needed = {"site_id", "longitude", "latitude", "year", *bundle["features"]}
            if not needed.issubset(df):
                raise ValueError("Prediction CSV is missing: " + ", ".join(sorted(needed - set(df))))
            if not df.site_id.isin(SITES).all():
                raise ValueError("Prediction CSV contains an unknown site.")
            X = df[bundle["features"]].apply(pd.to_numeric, errors="raise").to_numpy()
            if not len(df) or not np.isfinite(X).all():
                raise ValueError("Prediction CSV must contain finite pixel features.")
            for name, model in bundle["models"].items():
                df[name] = model.predict(X)
            df["claim_status"] = bundle["metadata"]["claim_status"]
            df["model_dataset_sha256"] = bundle["metadata"]["dataset_sha256"]
            output = Path(args.output)
            output.parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(output, index=False)
            print(f"Saved {len(df)} pixel predictions to {output}. These are not area totals.")
            return 0
        features = SPECTRAL_BANDS if args.features == "bands" else ALL_CLASSIFICATION_FEATURES
        if args.features == "optical_thermal":
            features = features + THERMAL_FEATURES
        frames = [pd.read_csv(p) for p in args.csv]
        frame = pd.concat(frames, ignore_index=True)
        if args.site != "pooled" and "site_id" in frame:
            frame = frame[frame.site_id.eq(args.site)].copy()
        if args.site == "pooled" and ("site_id" not in frame or frame.site_id.nunique() < 2):
            raise ValueError("Pooled training requires explicitly identified samples from both sites.")
        if args.validation == "leave_site_out" and (args.site != "pooled" or not args.test_site):
            raise ValueError("Use --site pooled --test-site SITE for leave-site-out evaluation.")
        manager = MLDatasetManager(frame=frame, site_id=None if args.site == "pooled" else args.site,
                    allow_unverified=args.allow_unverified, allow_synthetic=args.allow_synthetic, features=features)
        suffix = "_development" if manager.claim_status == "development_only" else ""
        suffix += f"_{args.features}_{args.validation}"
        if args.test_site:
            suffix += f"_{args.test_site}"
        output = Path(args.output or Path(PROCESSED_DATA_DIR) / "classification" / (args.site + suffix))
        if output.exists() and any(output.iterdir()):
            raise ValueError(f"Output directory is not empty: {output}. Choose a new --output to preserve previous runs.")
        results = LandCoverClassifier(manager).train_and_evaluate(
            n_splits=args.folds, block_size_m=args.block_size_m, output_dir=output,
            validation=args.validation, test_site=args.test_site)
        print(f"Classification completed: {results['claim_status']}; sites={results['site_ids']}")
        for name, scores in results["models_comparison"].items():
            print(f"{name}: OA={scores['overall_accuracy']:.4f}, macro-F1={scores['macro_f1']:.4f}")
        print(f"Artifacts: {output}")
        if results["claim_status"] == "development_only":
            print("NOT research accuracy: reference labels/source provenance are missing or synthetic.")
        return 0
    except (ValueError, FileNotFoundError, KeyError, OSError, ImportError) as error:
        parser.exit(2, f"Classification stopped: {error}\n")


if __name__ == "__main__":
    raise SystemExit(main())
