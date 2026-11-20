"""Validate provenance boundaries, spatial holdouts, inference, and site isolation."""
import io
import json
import tempfile
import unittest
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import rasterio
from rasterio.transform import from_origin

from dip_pipeline.ml.dataset import MLDatasetManager, ALL_CLASSIFICATION_FEATURES, spatial_groups
from dip_pipeline.ml.supervised_classification import LandCoverClassifier
from dip_pipeline.ml.raster_prediction import classify_raster
from dip_pipeline.ml.runner_ml import main


def fixture(site_id="aws_pdx"):
    rng = np.random.default_rng(23)
    records = []
    for block in range(9):
        for c in range(1, 5):
            for pixel in range(2):
                row = {feature: float(rng.normal(c * 0.1, 0.12)) for feature in ALL_CLASSIFICATION_FEATURES}
                row.update(site_id=site_id, longitude=-119.7 + block * 0.012 + pixel * 0.0001,
                           latitude=(45.81 if site_id == "aws_pdx" else 47.24) + c * 0.0001,
                           year=2025, land_cover_class=c, reference_id=f"r_{block}_{c}",
                           data_source="synthetic_demo", label_source="synthetic_demo")
                records.append(row)
    return pd.DataFrame(records)


class DatasetTests(unittest.TestCase):
    def test_legacy_requires_both_explicit_site_and_override(self):
        frame = fixture().drop(columns=["site_id", "data_source", "label_source"])
        with self.assertRaisesRegex(ValueError, "site_id"):
            MLDatasetManager(frame=frame)
        with self.assertRaises(ValueError):
            MLDatasetManager(frame=frame, site_id="aws_pdx")
        manager = MLDatasetManager(frame=frame, site_id="aws_pdx", allow_unverified=True)
        self.assertEqual(manager.claim_status, "development_only")

    def test_pseudolabels_and_synthetic_are_not_reference_accuracy(self):
        frame = fixture()
        with self.assertRaisesRegex(ValueError, "Synthetic"):
            MLDatasetManager(frame=frame)
        frame["data_source"] = "gee_landsat"
        frame["label_source"] = "spectral_threshold_pseudolabel"
        with self.assertRaisesRegex(ValueError, "independent"):
            MLDatasetManager(frame=frame)
        manager = MLDatasetManager(frame=frame, allow_unverified=True)
        self.assertEqual(manager.claim_status, "development_only")

    def test_synthetic_flag_does_not_authorize_unverified_rows(self):
        frame = fixture()
        frame.loc[0, "data_source"] = "unverified_legacy"
        with self.assertRaisesRegex(ValueError, "independent"):
            MLDatasetManager(frame=frame, allow_synthetic=True)

    def test_reference_labels_need_dated_source_and_homogeneous_regions(self):
        frame = fixture()
        frame["data_source"] = "gee_landsat"
        frame["label_source"] = "manual_dated_imagery"
        with self.assertRaisesRegex(ValueError, "reference_date"):
            MLDatasetManager(frame=frame)
        frame["reference_date"] = "2025-07-01"
        frame["reference_source"] = "test reference citation, not real research data"
        self.assertEqual(MLDatasetManager(frame=frame).claim_status, "reference_labels_spatial_validation")
        frame.loc[0, "reference_date"] = "2024-07-01"
        with self.assertRaisesRegex(ValueError, "match"):
            MLDatasetManager(frame=frame)

    def test_duplicate_and_nonfinite_pixels_rejected(self):
        frame = fixture()
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            MLDatasetManager(frame=pd.concat([frame, frame.iloc[:1]]), allow_synthetic=True)
        frame.loc[0, "SR_B2"] = np.inf
        with self.assertRaisesRegex(ValueError, "non-finite"):
            MLDatasetManager(frame=frame, allow_synthetic=True)

    def test_reference_polygon_connects_distant_blocks(self):
        frame = fixture()
        frame.loc[[0, 8], "reference_id"] = "same_polygon"
        groups = spatial_groups(frame)
        self.assertEqual(groups[0], groups[8])
        repeated = frame.iloc[[0]].copy()
        repeated["year"] = 2024
        combined = pd.concat([frame, repeated], ignore_index=True)
        self.assertEqual(spatial_groups(combined)[0], spatial_groups(combined)[-1])


class ClassificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.directory = Path(cls.temp.name)
        cls.manager = MLDatasetManager(frame=fixture(), allow_synthetic=True)
        cls.classifier = LandCoverClassifier(cls.manager)
        cls.result = cls.classifier.train_and_evaluate(n_splits=3, output_dir=cls.directory / "run")

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_spatial_folds_have_no_group_or_pixel_leakage(self):
        for fold in self.result["folds"]:
            self.assertFalse(set(fold["train_groups"]) & set(fold["test_groups"]))
        self.assertTrue(self.classifier.predictions.fold.ge(0).all())
        self.assertEqual(self.result["n_evaluated_samples"], len(self.manager.df))
        self.assertEqual(sum(map(sum, self.result["models_comparison"]["Random Forest"]["confusion_matrix"])),
                         len(self.manager.df))
        self.assertEqual(self.result["claim_status"], "development_only")

    def test_saved_models_reproduce_predictions_and_cli_inference(self):
        run = self.directory / "run"
        bundle = joblib.load(run / "models.joblib")
        X = self.manager.df[bundle["features"]].to_numpy()
        np.testing.assert_array_equal(bundle["models"]["Random Forest"].predict(X),
                                      self.classifier.predict_land_cover(X))
        csv = self.directory / "pixels.csv"
        self.manager.df.to_csv(csv, index=False)
        output = self.directory / "predicted.csv"
        self.assertEqual(main(["predict", "--model", str(run / "models.joblib"),
                               "--csv", str(csv), "--output", str(output)]), 0)
        self.assertEqual(len(pd.read_csv(output)), len(self.manager.df))
        self.assertEqual(json.loads((run / "metrics.json").read_text())["schema_version"], 2)

    def test_no_silent_training_or_invalid_model_selection(self):
        with self.assertRaisesRegex(RuntimeError, "Train"):
            LandCoverClassifier(self.manager).predict_land_cover(np.ones((1, 10)))
        with self.assertRaisesRegex(ValueError, "rf or svm"):
            self.classifier.predict_land_cover(np.ones((1, 10)), "typo")

    def test_transfer_scaler_and_model_do_not_fit_target_site(self):
        both = pd.concat([fixture(), fixture("h5_quincy2")], ignore_index=True)
        both.loc[both.site_id.eq("h5_quincy2"), "SR_B2"] += 10
        classifier = LandCoverClassifier(MLDatasetManager(frame=both, allow_synthetic=True))
        result = classifier.train_and_evaluate(validation="leave_site_out", test_site="h5_quincy2")
        self.assertEqual(set(result["per_site_performance"]), {"h5_quincy2"})
        scaler = classifier.models["Support Vector Machine"].steps[0][1]
        expected = both[both.site_id.eq("aws_pdx")][classifier.feature_names].mean().to_numpy()
        np.testing.assert_allclose(scaler.mean_, expected)

    def test_too_few_groups_fails_without_random_split_fallback(self):
        frame = fixture().iloc[:8].copy()
        classifier = LandCoverClassifier(MLDatasetManager(frame=frame, allow_synthetic=True))
        with self.assertRaisesRegex(ValueError, "groups"):
            classifier.train_and_evaluate(n_splits=5)

    def test_raster_preserves_crs_nodata_class_values_and_provenance(self):
        source = self.directory / "features.tif"
        output = self.directory / "classified.tif"
        data = np.full((10, 4, 5), 0.2, dtype="float32")
        data[:, 0, 0] = -9999
        with rasterio.open(source, "w", driver="GTiff", width=5, height=4, count=10,
                           dtype="float32", crs="EPSG:32611", nodata=-9999,
                           transform=from_origin(300000, 5100000, 30, 30)) as target:
            target.write(data)
            for i, name in enumerate(ALL_CLASSIFICATION_FEATURES, 1):
                target.set_band_description(i, name)
        report = classify_raster(self.directory / "run/models.joblib", source, output,
                                 site_id="aws_pdx", year=2025)
        with rasterio.open(output) as result:
            classes = result.read(1)
            self.assertEqual(result.crs.to_epsg(), 32611)
            self.assertEqual(classes[0, 0], 0)
            self.assertTrue(set(np.unique(classes[1:])).issubset({1, 2, 3, 4}))
            self.assertEqual(result.tags()["claim_status"], "development_only")
            self.assertEqual(result.colormap(1)[1][:3], (44, 160, 44))
        self.assertEqual(report["site_id"], "aws_pdx")


if __name__ == "__main__":
    unittest.main()
