"""RF/SVM classification with identical spatial folds and explicit provenance."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (accuracy_score, cohen_kappa_score, confusion_matrix,
                             precision_recall_fscore_support)
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from .dataset import MLDatasetManager, CLASS_NAMES


def evaluate(y, pred):
    labels = list(CLASS_NAMES)
    precision, recall, f1, support = precision_recall_fscore_support(
        y, pred, labels=labels, zero_division=0)
    kappa = cohen_kappa_score(y, pred, labels=labels)
    return {"overall_accuracy": float(accuracy_score(y, pred)),
            "macro_f1": float(np.mean(f1)),
            "cohen_kappa": float(kappa) if np.isfinite(kappa) else None,
            "confusion_matrix": confusion_matrix(y, pred, labels=labels).tolist(),
            "labels": list(CLASS_NAMES.values()),
            "per_class": [{"class_id": c, "class_name": CLASS_NAMES[c],
                           "precision": float(precision[i]), "recall": float(recall[i]),
                           "f1": float(f1[i]), "support": int(support[i])}
                          for i, c in enumerate(labels)]}


def threshold_predict(frame):
    """Fixed baseline, never a substitute for reference labels."""
    return np.select([frame.MNDWI.gt(0), frame.NDBI.gt(-0.05) & frame.NDVI.lt(0.22),
                      frame.NDVI.gt(0.30) & frame.NDBI.lt(0)], [4, 2, 1], default=3)


class LandCoverClassifier:
    def __init__(self, dataset_manager=None, *, random_state=42, **dataset_options):
        self.dataset_manager = dataset_manager or MLDatasetManager(**dataset_options)
        self.random_state = random_state
        self.feature_names = self.dataset_manager.features
        self.models = {}
        self.is_trained = False

    def _models(self):
        return {"Random Forest": RandomForestClassifier(n_estimators=150, max_depth=16,
                    min_samples_leaf=2, class_weight="balanced", random_state=self.random_state, n_jobs=1),
                "Support Vector Machine": make_pipeline(StandardScaler(),
                    SVC(C=10, kernel="rbf", class_weight="balanced"))}

    def train_and_evaluate(self, *, n_splits=5, block_size_m=500, output_dir=None,
                           validation="spatial", test_site=None):
        df = self.dataset_manager.df
        X, y = df[self.feature_names].to_numpy(), df.land_cover_class.to_numpy()
        groups = self.dataset_manager.get_spatial_blocks(block_size_m)
        if validation == "leave_site_out":
            test = np.flatnonzero(df.site_id.eq(test_site))
            train = np.flatnonzero(~df.site_id.eq(test_site))
            if not len(train) or not len(test):
                raise ValueError("Leave-site-out evaluation requires training and selected test-site samples.")
            splits = [(train, test)]
        elif validation == "spatial":
            if n_splits < 2 or len(set(groups)) < n_splits:
                raise ValueError("Not enough independent spatial groups for the requested folds.")
            for c in CLASS_NAMES:
                if len(set(groups[y == c])) < n_splits:
                    raise ValueError(f"Class {c} needs at least {n_splits} independent spatial groups.")
            splitter = StratifiedGroupKFold(n_splits, shuffle=True, random_state=self.random_state)
            splits = list(splitter.split(X, y, groups))
        else:
            raise ValueError("validation must be spatial or leave_site_out.")
        predictions = df[[c for c in ("site_id", "year", "longitude", "latitude", "reference_id",
                                      "land_cover_class", "data_source", "label_source") if c in df]].copy()
        predictions["spatial_group"] = groups
        predictions["fold"] = -1
        model_names = list(self._models())
        predicted = {name: np.full(len(df), -1, dtype=int) for name in model_names}
        folds = []
        for fold, (train, test) in enumerate(splits):
            if set(groups[train]) & set(groups[test]):
                raise ValueError("Spatial group leakage detected.")
            if set(y[train]) != set(CLASS_NAMES):
                raise ValueError(f"Fold {fold} training set lacks one or more land-cover classes.")
            predictions.loc[test, "fold"] = fold
            entry = {"fold": fold, "n_train": len(train), "n_test": len(test),
                     "train_groups": sorted(set(groups[train])), "test_groups": sorted(set(groups[test])),
                     "models": {}}
            for name, model in self._models().items():
                model.fit(X[train], y[train])
                pred = model.predict(X[test])
                predicted[name][test] = pred
                entry["models"][name] = evaluate(y[test], pred)
            folds.append(entry)
        mask = predictions.fold.ge(0).to_numpy()
        model_results = {}
        for name in model_names:
            model_results[name] = evaluate(y[mask], predicted[name][mask])
            model_results[name]["fold_macro_f1_std"] = float(np.std(
                [f["models"][name]["macro_f1"] for f in folds]))
            predictions[name] = np.where(mask, predicted[name], np.nan)
        baseline = threshold_predict(df)
        model_results["Spectral threshold baseline"] = evaluate(y[mask], baseline[mask])
        predictions["Spectral threshold baseline"] = np.where(mask, baseline, np.nan)
        per_site = {}
        for site in sorted(df.site_id.unique()):
            smask = mask & df.site_id.eq(site).to_numpy()
            if smask.any():
                per_site[site] = {name: evaluate(y[smask], pred[smask])
                                  for name, pred in predicted.items()}
                per_site[site]["Spectral threshold baseline"] = evaluate(y[smask], baseline[smask])
        self.models = self._models()
        # Transfer inference keeps the target site held out.
        final_train = splits[0][0] if validation == "leave_site_out" else np.arange(len(df))
        for model in self.models.values():
            model.fit(X[final_train], y[final_train])
        self.is_trained = True
        fingerprint = hashlib.sha256(pd.util.hash_pandas_object(df, index=False).values.tobytes()).hexdigest()
        self.metrics_summary = {"schema_version": 2, "status": "completed",
            "created_at": datetime.now(timezone.utc).isoformat(),
            **self.dataset_manager.provenance, "features_used": self.feature_names,
            "validation": validation, "test_site": test_site,
            "n_folds": len(folds), "block_size_m": block_size_m,
            "random_state": self.random_state, "n_evaluated_samples": int(mask.sum()),
            "dataset_sha256": fingerprint, "sklearn_version": sklearn.__version__,
            "classification_scope": "land cover across each site's full AOI, not data-center identity",
            "models_comparison": model_results, "per_site_performance": per_site, "folds": folds,
            "gini_feature_importance": [{"feature": f, "importance": float(v)} for f, v in
                zip(self.feature_names, self.models["Random Forest"].feature_importances_)],
            "limitations": ["Spatial blocks reduce but do not eliminate spatial dependence; no buffer gap is enforced.",
                "Sample metrics are not area-adjusted accuracy or proof of operational heat.",
                "Final fitted models are for inference; scores use held-out predictions only."]}
        if self.dataset_manager.claim_status == "development_only":
            self.metrics_summary["limitations"].insert(0, "Development-only data: these scores are not field accuracy.")
        self.predictions = predictions
        if output_dir is not None:
            self.save(output_dir)
        return self.metrics_summary

    def save(self, output_dir):
        output = Path(output_dir)
        output.mkdir(parents=True, exist_ok=True)
        (output / "metrics.json").write_text(json.dumps(self.metrics_summary, indent=2, allow_nan=False), encoding="utf-8")
        self.predictions.to_csv(output / "heldout_predictions.csv", index=False)
        joblib.dump({"models": self.models, "features": self.feature_names,
                     "metadata": self.metrics_summary}, output / "models.joblib")

    def predict_land_cover(self, feature_array, model_type="rf"):
        if not self.is_trained:
            raise RuntimeError("Train or load a model first; prediction never silently retrains.")
        names = {"rf": "Random Forest", "svm": "Support Vector Machine"}
        if model_type not in names:
            raise ValueError("model_type must be rf or svm.")
        values = np.asarray(feature_array, dtype=float)
        if values.ndim != 2 or values.shape[1] != len(self.feature_names) or not np.isfinite(values).all():
            raise ValueError("Prediction features must be finite and match the trained feature order.")
        return self.models[names[model_type]].predict(values)
