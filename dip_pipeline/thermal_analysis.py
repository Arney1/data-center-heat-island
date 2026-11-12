"""
Modul Analisis Termal dan Dinamika Suhu Permukaan (LST)
Mencakup:
1. Perhitungan Anomali Termal terhadap Area Referensi Pertanian Regional
2. Profil Gradien Spasial menurut Cincin Jarak (Spatial Gradients C/km)
3. Analisis Tren Non-Parametrik: Sen's Slope dan Mann-Kendall Tau
4. Audit Emisivitas ASTER GED terhadap Perubahan NDVI
"""

import numpy as np
from typing import Dict, List, Tuple
from scipy import stats

def compute_thermal_anomaly(lst_map: np.ndarray, reference_lst_scalar: float) -> np.ndarray:
    """
    Menghitung anomali termal piksel terhadap baseline suhu regional:
    LSTanom = LST - T_ref
    """
    return lst_map - reference_lst_scalar

def compute_spatial_gradient(lst_near: float, lst_far: float,
                            dist_near_km: float, dist_far_km: float) -> float:
    """
    Menghitung gradien penurunan suhu terhadap jarak (C/km):
    G = (T_far - T_near) / (d_far - d_near)
    """
    delta_dist = dist_far_km - dist_near_km
    if abs(delta_dist) < 1e-6:
        raise ValueError("Jarak cincin near dan far tidak boleh sama.")
    return (lst_far - lst_near) / delta_dist

def compute_sens_slope(time_series_1d: np.ndarray, years: List[int]) -> float:
    """
    Menghitung kemiringan tren non-parametrik Sen's Slope untuk deret waktu tahunan.
    Median dari semua pasangan kemiringan (y_j - y_i) / (t_j - t_i).
    """
    slopes = []
    n = len(years)
    for i in range(n):
        for j in range(i + 1, n):
            if not np.isnan(time_series_1d[i]) and not np.isnan(time_series_1d[j]):
                slope = (time_series_1d[j] - time_series_1d[i]) / (years[j] - years[i])
                slopes.append(slope)
    if not slopes:
        return 0.0
    return float(np.median(slopes))

def compute_mann_kendall_tau(time_series_1d: np.ndarray) -> Tuple[float, float]:
    """
    Menghitung uji korelasi rank Kendall's Tau dan p-value untuk mendeteksi
    signifikansi tren monotonik tanpa asumsi distribusi normal.
    """
    valid_idx = ~np.isnan(time_series_1d)
    y = time_series_1d[valid_idx]
    x = np.arange(len(y))
    if len(y) < 3:
        return 0.0, 1.0
    res = stats.kendalltau(x, y)
    return float(res.correlation), float(res.pvalue)

def audit_emissivity_artifact(delta_ndvi: np.ndarray, delta_emis: np.ndarray,
                              delta_lst: np.ndarray) -> Dict[str, float]:
    """
    Audit gerbang G5 untuk mendeteksi apakah kenaikan LST merupakan artefak penyesuaian emisivitas ASTER GED:
    Korelasi Pearson antara:
    1. Delta NDVI vs Delta Emisivitas
    2. Delta Emisivitas vs Delta LST
    """
    mask = (~np.isnan(delta_ndvi)) & (~np.isnan(delta_emis)) & (~np.isnan(delta_lst))
    x_ndvi = delta_ndvi[mask]
    x_emis = delta_emis[mask]
    x_lst = delta_lst[mask]

    corr_ndvi_emis, _ = stats.pearsonr(x_ndvi, x_emis)
    corr_emis_lst, _ = stats.pearsonr(x_emis, x_lst)

    return {
        "corr_delta_ndvi_vs_delta_emis": float(corr_ndvi_emis),
        "corr_delta_emis_vs_delta_lst": float(corr_emis_lst),
        "is_artifact_suspected": bool(abs(corr_emis_lst) > 0.85)
    }
