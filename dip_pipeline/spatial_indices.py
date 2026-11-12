"""
Modul Indeks Koinsidensi Termal-Lahan (IKTL) dan Analisis Sensitivitas Ablasi
Menerapkan skema harkat multi-kriteria untuk mengidentifikasi sel tempat
peningkatan suhu dan konversi fisik lahan berlangsung bersamaan.
"""

import numpy as np
from typing import Dict, List

def calculate_percentile_harkat(values: np.ndarray, percentiles: List[float] = [50, 75, 90, 97.5]) -> np.ndarray:
    """
    Menghitung harkat skor 1 sampai 5 berbasis nilai kuantil distribusi area referensi:
    - x <= P50: 1
    - P50 < x <= P75: 2
    - P75 < x <= P90: 3
    - P90 < x <= P97.5: 4
    - x > P97.5: 5
    """
    clean_vals = values[~np.isnan(values)]
    if len(clean_vals) == 0:
        return np.ones_like(values, dtype=np.uint8)

    p_cuts = np.percentile(clean_vals, percentiles)
    harkat = np.ones_like(values, dtype=np.uint8)
    harkat[values > p_cuts[0]] = 2
    harkat[values > p_cuts[1]] = 3
    harkat[values > p_cuts[2]] = 4
    harkat[values > p_cuts[3]] = 5
    return harkat

def compute_conversion_v4(pre_built: np.ndarray, post_built: np.ndarray,
                          pre_ndvi: np.ndarray, veg_thr: float = 0.3) -> np.ndarray:
    """
    Menghitung skor konversi tutupan lahan V4:
    - Vegetasi ke Terbangun: Skor 5
    - Tanah Terbuka ke Terbangun: Skor 3
    - Tidak Berubah / Tetap: Skor 1
    """
    is_new_built = (post_built == 1) & (pre_built == 0)
    was_vegetation = (pre_ndvi > veg_thr)

    v4 = np.ones_like(post_built, dtype=np.uint8)
    v4[is_new_built & (~was_vegetation)] = 3
    v4[is_new_built & was_vegetation] = 5
    return v4

def compute_iktl(v1_h: np.ndarray, v2_h: np.ndarray,
                 v3_h: np.ndarray, v4_score: np.ndarray,
                 scenario: str = "full") -> np.ndarray:
    """
    Menghitung kelas komposit IKTL (1-5) dengan dukungan skenario ablasi:
    - 'full': Rata-rata [v1, v2, v3, v4]
    - 'no_v1': Tanpa V1 (Termal) -> Rata-rata [v2, v3, v4]
    - 'no_v2_v3': Tanpa V2+V3 (Permukaan) -> Rata-rata [v1, v4]
    - 'no_v4': Tanpa V4 (Konversi) -> Rata-rata [v1, v2, v3]
    """
    if scenario == "full":
        components = [v1_h, v2_h, v3_h, v4_score]
    elif scenario == "no_v1":
        components = [v2_h, v3_h, v4_score]
    elif scenario == "no_v2_v3":
        components = [v1_h, v4_score]
    elif scenario == "no_v4":
        components = [v1_h, v2_h, v3_h]
    else:
        raise ValueError(f"Skenario ablasi tidak dikenal: {scenario}")

    mean_score = np.mean(components, axis=0)

    # Harkat kembali ke 5 kelas IKTL
    iktl_class = np.ones_like(mean_score, dtype=np.uint8)
    iktl_class[mean_score >= 2.00] = 2
    iktl_class[mean_score >= 2.75] = 3
    iktl_class[mean_score >= 3.50] = 4
    iktl_class[mean_score >= 4.25] = 5

    return iktl_class
