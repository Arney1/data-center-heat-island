"""
Eksekutor Pipeline Machine Learning (Week 1 Runner)
Menjalankan pelatihan, validasi, perbandingan model, dan ekspor metrik klasifikasi tutupan lahan.
"""

import os
import json
import pandas as pd
import numpy as np

from .supervised_classification import LandCoverClassifier
from .dataset import MLDatasetManager, CLASS_NAMES
from ..config import PROCESSED_DATA_DIR


def run_week1_ml_pipeline():
    print("=" * 75)
    print("PIPELINE MACHINE LEARNING - MINGGU 1: SUPERVISED LAND COVER CLASSIFICATION")
    print("Studi Kasus: AWS PDX Bombing Campus (Boardman, Oregon)")
    print("=" * 75)

    # 1. Pastikan Dataset Fitur Tersedia
    print("\n[LANGKAH 1] Inisialisasi & Pemeriksaan Dataset Fitur Spektral-Termal...")
    dm = MLDatasetManager()
    df = dm.df
    print(f"  - Total Sampel Piksel: {len(df)}")
    print(f"  - Fitur yang Diekstraksi: {len(df.columns) - 4} kolom (Spektral, Indeks, Termal, Spasial)")
    
    print("\n  Distribusi Kelas Tutupan Lahan:")
    class_counts = df["land_cover_class"].value_counts().sort_index()
    for c_id, count in class_counts.items():
        c_name = CLASS_NAMES.get(c_id, "Unknown")
        pct = (count / len(df)) * 100
        print(f"    * Kelas {c_id} ({c_name}): {count} piksel ({pct:.1f}%)")

    # 2. Latih & Evaluasi Model
    print("\n[LANGKAH 2] Pelatihan Model Klasifikasi Terbimbing (Random Forest & SVM)...")
    classifier = LandCoverClassifier()
    results = classifier.train_and_evaluate()

    # 3. Cetak Perbandingan Kinerja Model
    rf_res = results["models_comparison"]["Random Forest"]
    svm_res = results["models_comparison"]["Support Vector Machine"]

    print("\n" + "-" * 75)
    print("HASIL EVALUASI MODEL KLASIFIKASI (TEST SET 25%):")
    print("-" * 75)
    print(f"  - RANDOM FOREST CLASSIFIER:")
    print(f"      * Overall Accuracy (OA) : {rf_res['overall_accuracy'] * 100:.2f}% (Target: > 88%)")
    print(f"      * Cohen's Kappa         : {rf_res['cohen_kappa']:.4f} (Target: > 0.82)")
    print(f"  - SUPPORT VECTOR MACHINE (RBF):")
    print(f"      * Overall Accuracy (OA) : {svm_res['overall_accuracy'] * 100:.2f}%")
    print(f"      * Cohen's Kappa         : {svm_res['cohen_kappa']:.4f}")

    # 4. Matriks Konfusi Random Forest
    print("\n[LANGKAH 3] Matriks Konfusi Random Forest:")
    cm = np.array(rf_res["confusion_matrix"])
    labels = ["1_Vegetation", "2_Built-up", "3_Bare_Soil", "4_Water"]
    cm_df = pd.DataFrame(cm, index=[f"True_{l}" for l in labels], columns=[f"Pred_{l}" for l in labels])
    print(cm_df.to_string())

    # 5. Kinerja Per Kelas
    print("\n[LANGKAH 4] Evaluasi Per Kelas (User's Accuracy & Producer's Accuracy):")
    for c_name, m in results["per_class_performance"].items():
        print(f"  * {c_name}:")
        print(f"      - Precision (User's Acc)     : {m['rf_users_accuracy_precision'] * 100:.2f}%")
        print(f"      - Recall (Producer's Acc)    : {m['rf_producers_accuracy_recall'] * 100:.2f}%")
        print(f"      - F1-Score                   : {m['rf_f1_score']:.4f}")

    # 6. Fitur Paling Berpengaruh (Feature Importance)
    print("\n[LANGKAH 5] 5 Fitur Spektral-Termal Paling Berpengaruh (Gini Importance):")
    for item in results["gini_feature_importance"][:5]:
        print(f"  - {item['feature']:<12}: {item['importance']:.4f}")

    print("\n" + "=" * 75)
    print("STATUS MINGGU 1: TUGAS MACHINE LEARNING & EE FETCHER TELAH TUNTAS!")
    print(f"Hasil lengkap tersimpan di {os.path.join(PROCESSED_DATA_DIR, 'ml_classification_results.json')}")
    print("=" * 75)

    return results


if __name__ == "__main__":
    run_week1_ml_pipeline()
