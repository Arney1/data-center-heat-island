"""
Modul Klasifikasi dan Segmentasi Citra
Mencakup:
1. Segmentasi Berbasis Ambang Spektral (Built-up Mask: NDBI > THR, NDVI < THR, MNDWI < 0)
2. Peta Tahun Mulai Terbangun Persisten (Persistent Urban Sprawl Mapping via Backward Cumulative AND)
3. Clustering K-Means Tanpa Supervisi (k = 5, 10, 20)
4. Validasi Matriks Konfusi dan Koefisien Kappa
"""

import numpy as np
from typing import Dict, List, Tuple
from sklearn.cluster import KMeans
from sklearn.metrics import confusion_matrix, cohen_kappa_score
from .config import SPECTRAL_THRESHOLDS

def extract_built_up_mask(ndbi: np.ndarray, ndvi: np.ndarray, mndwi: np.ndarray,
                          thr_ndbi: float = None, thr_ndvi: float = None) -> np.ndarray:
    """
    Segmentasi piksel lahan terbangun / buatan menggunakan ambang multi-indeks:
    Built-up = (NDBI > thr_ndbi) & (NDVI < thr_ndvi) & (MNDWI < 0)
    """
    if thr_ndbi is None:
        thr_ndbi = SPECTRAL_THRESHOLDS["thr_ndbi"]
    if thr_ndvi is None:
        thr_ndvi = SPECTRAL_THRESHOLDS["thr_ndvi_built"]

    is_built = (ndbi > thr_ndbi) & (ndvi < thr_ndvi) & (mndwi < SPECTRAL_THRESHOLDS["thr_mndwi_water"])
    return is_built.astype(np.uint8)

def compute_persistent_sprawl_year(annual_built_masks: Dict[int, np.ndarray],
                                  years_sorted_asc: List[int]) -> np.ndarray:
    """
    Menghitung tahun pertama sebuah piksel mulai terbangun secara persisten.
    Algoritma Backward Cumulative AND:
    Mulai dari tahun terbaru (2026), iterasi mundur ke 2013.
    Sebuah piksel dianggap persisten di tahun T jika ia terbangun di tahun T
    DAN tetap terbangun di semua tahun setelah T.
    """
    years_desc = sorted(years_sorted_asc, reverse=True)
    shape = annual_built_masks[years_desc[0]].shape
    start_year_map = np.zeros(shape, dtype=np.int16)
    
    persistent_mask = None
    for y in years_desc:
        mask_y = (annual_built_masks[y] > 0)
        if persistent_mask is None:
            persistent_mask = mask_y
        else:
            persistent_mask = mask_y & persistent_mask
        
        # Di mana persistent_mask True, perbarui tahun mulai menjadi y
        start_year_map = np.where(persistent_mask, y, start_year_map)

    return start_year_map

def run_kmeans_clustering(feature_stack: np.ndarray,
                          k_values: List[int] = [5, 10, 20],
                          random_state: int = 42) -> Dict[int, Tuple[np.ndarray, float]]:
    """
    Menjalankan unsupervised K-Means clustering pada tumpukan fitur (NDVI, NDBI, MNDWI, Albedo, LST).
    Mengembalikan label klaster spasial dan inertia (Within-Cluster Sum of Squares) untuk tiap k.
    """
    # feature_stack shape: (H, W, Channels)
    H, W, C = feature_stack.shape
    X = feature_stack.reshape(-1, C)

    # Tangani NaN bila ada
    nan_mask = np.isnan(X).any(axis=1)
    X_clean = X[~nan_mask]

    results = {}
    for k in k_values:
        kmeans = KMeans(n_clusters=k, random_state=random_state, n_init=10)
        labels_clean = kmeans.fit_predict(X_clean)
        
        full_labels = np.full(H * W, fill_value=-1, dtype=np.int32)
        full_labels[~nan_mask] = labels_clean
        cluster_map = full_labels.reshape(H, W)
        
        results[k] = (cluster_map, float(kmeans.inertia_))

    return results

def evaluate_classification_accuracy(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """
    Menghitung akurasi klasifikasi tutupan lahan:
    - Overall Accuracy (OA)
    - Cohen's Kappa Coefficient
    """
    mask = (~np.isnan(y_true)) & (~np.isnan(y_pred))
    yt = y_true[mask].astype(int)
    yp = y_pred[mask].astype(int)

    cm = confusion_matrix(yt, yp)
    oa = float(np.sum(np.diag(cm)) / np.sum(cm))
    kappa = float(cohen_kappa_score(yt, yp))

    return {
        "overall_accuracy": oa,
        "cohen_kappa": kappa,
        "confusion_matrix": cm.tolist()
    }
