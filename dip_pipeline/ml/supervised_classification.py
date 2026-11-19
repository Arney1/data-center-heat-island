"""
Modul Klasifikasi Tutupan Lahan Terbimbing (Supervised Classification) - Minggu 1
Menerapkan:
1. Random Forest (RF) Classifier dengan penyeimbangan bobot kelas
2. Support Vector Machine (SVM) Classifier dengan RBF Kernel
3. Evaluasi Kinerja Lengkap: Matriks Konfusi, Overall Accuracy, Cohen's Kappa, Precision, Recall, F1
4. Analisis Kepentingan Fitur (Gini Impurity & Permutation Importance)
"""

import os
import json
import logging
from typing import Dict, List, Tuple, Optional, Any
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.metrics import (
    confusion_matrix,
    accuracy_score,
    cohen_kappa_score,
    classification_report,
    precision_recall_fscore_support
)
from sklearn.inspection import permutation_importance

from .dataset import (
    MLDatasetManager,
    ALL_CLASSIFICATION_FEATURES,
    CLASS_NAMES,
    CLASS_COLORS
)
from ..config import PROCESSED_DATA_DIR

logger = logging.getLogger("LandCoverClassifier")


class LandCoverClassifier:
    """
    Model Klasifikasi Tutupan Lahan Terbimbing untuk Kawasan Sekitar Kampus Pusat Data AWS PDX.
    """

    def __init__(self, random_state: int = 42):
        self.random_state = random_state
        self.dataset_manager = MLDatasetManager()
        self.rf_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=12,
            min_samples_split=4,
            class_weight="balanced",
            random_state=self.random_state,
            n_jobs=-1
        )
        self.svm_model = SVC(
            kernel="rbf",
            C=10.0,
            gamma="scale",
            class_weight="balanced",
            random_state=self.random_state
        )
        self.feature_names: List[str] = ALL_CLASSIFICATION_FEATURES
        self.is_trained = False
        self.metrics_summary: Dict[str, Any] = {}

    def train_and_evaluate(
        self,
        features: Optional[List[str]] = None,
        test_size: float = 0.25
    ) -> Dict[str, Any]:
        """
        Melatih Random Forest dan SVM, menghitung matriks evaluasi,
        serta membandingkan akurasi kedua model.
        """
        self.feature_names = features or ALL_CLASSIFICATION_FEATURES

        # 1. Ambil data terstratifikasi
        X_train, X_test, y_train, y_test, feat_names = self.dataset_manager.get_classification_data(
            features=self.feature_names,
            test_size=test_size,
            random_state=self.random_state,
            scale_features=False
        )

        # Standarisasi terpisah untuk SVM
        X_train_scaled = self.dataset_manager.scaler.fit_transform(X_train)
        X_test_scaled = self.dataset_manager.scaler.transform(X_test)

        logger.info(f"Melatih Random Forest dengan {len(X_train)} sampel pelatihan dan {len(X_test)} sampel pengujian...")
        # 2. Latih Random Forest
        self.rf_model.fit(X_train, y_train)
        rf_pred = self.rf_model.predict(X_test)

        # 3. Latih SVM
        logger.info("Melatih Support Vector Machine (RBF Kernel)...")
        self.svm_model.fit(X_train_scaled, y_train)
        svm_pred = self.svm_model.predict(X_test_scaled)

        # 4. Hitung Metrik Evaluasi Random Forest
        rf_oa = accuracy_score(y_test, rf_pred)
        rf_kappa = cohen_kappa_score(y_test, rf_pred)
        rf_cm = confusion_matrix(y_test, rf_pred, labels=[1, 2, 3, 4])
        rf_prec, rf_rec, rf_f1, _ = precision_recall_fscore_support(
            y_test, rf_pred, labels=[1, 2, 3, 4], zero_division=0
        )

        # 5. Hitung Metrik Evaluasi SVM
        svm_oa = accuracy_score(y_test, svm_pred)
        svm_kappa = cohen_kappa_score(y_test, svm_pred)
        svm_cm = confusion_matrix(y_test, svm_pred, labels=[1, 2, 3, 4])
        svm_prec, svm_rec, svm_f1, _ = precision_recall_fscore_support(
            y_test, svm_pred, labels=[1, 2, 3, 4], zero_division=0
        )

        # 6. Analisis Feature Importance (Random Forest Gini MDI)
        mdi_importances = self.rf_model.feature_importances_
        sorted_idx = np.argsort(mdi_importances)[::-1]
        feature_importance_list = [
            {"feature": self.feature_names[i], "importance": round(float(mdi_importances[i]), 4)}
            for i in sorted_idx
        ]

        # 7. Permutation Importance pada Test Set
        perm_res = permutation_importance(
            self.rf_model, X_test, y_test, n_repeats=5, random_state=self.random_state
        )
        perm_importance_list = [
            {
                "feature": self.feature_names[i],
                "mean_importance": round(float(perm_res.importances_mean[i]), 4),
                "std": round(float(perm_res.importances_std[i]), 4)
            }
            for i in np.argsort(perm_res.importances_mean)[::-1]
        ]

        # 8. Struktur Laporan Per Kelas
        class_eval = {}
        for c_id in [1, 2, 3, 4]:
            c_name = CLASS_NAMES[c_id]
            idx = c_id - 1
            class_eval[c_name] = {
                "class_id": c_id,
                "rf_users_accuracy_precision": round(float(rf_prec[idx]), 4),
                "rf_producers_accuracy_recall": round(float(rf_rec[idx]), 4),
                "rf_f1_score": round(float(rf_f1[idx]), 4),
                "svm_users_accuracy_precision": round(float(svm_prec[idx]), 4),
                "svm_producers_accuracy_recall": round(float(svm_rec[idx]), 4),
                "svm_f1_score": round(float(svm_f1[idx]), 4),
            }

        self.metrics_summary = {
            "status": "success",
            "n_train_samples": int(len(X_train)),
            "n_test_samples": int(len(X_test)),
            "features_used": self.feature_names,
            "models_comparison": {
                "Random Forest": {
                    "overall_accuracy": round(float(rf_oa), 4),
                    "cohen_kappa": round(float(rf_kappa), 4),
                    "confusion_matrix": rf_cm.tolist(),
                    "labels": [CLASS_NAMES[i] for i in [1, 2, 3, 4]]
                },
                "Support Vector Machine": {
                    "overall_accuracy": round(float(svm_oa), 4),
                    "cohen_kappa": round(float(svm_kappa), 4),
                    "confusion_matrix": svm_cm.tolist(),
                    "labels": [CLASS_NAMES[i] for i in [1, 2, 3, 4]]
                }
            },
            "per_class_performance": class_eval,
            "gini_feature_importance": feature_importance_list,
            "permutation_feature_importance": perm_importance_list
        }

        self.is_trained = True

        # Simpan ringkasan hasil ke data/processed/ml_classification_results.json
        output_json = os.path.join(PROCESSED_DATA_DIR, "ml_classification_results.json")
        with open(output_json, "w") as f:
            json.dump(self.metrics_summary, f, indent=2)
        logger.info(f"Hasil evaluasi klasifikasi ML berhasil disimpan ke {output_json}")

        return self.metrics_summary

    def predict_land_cover(self, feature_array: np.ndarray, model_type: str = "rf") -> np.ndarray:
        """
        Melakukan prediksi kelas tutupan lahan untuk array fitur masukan.
        """
        if not self.is_trained:
            self.train_and_evaluate()

        if model_type.lower() == "rf":
            return self.rf_model.predict(feature_array)
        else:
            scaled = self.dataset_manager.scaler.transform(feature_array)
            return self.svm_model.predict(scaled)
