"""
Modul Kompositing Multitemporal dan Agregasi Waktu
Menerapkan reduksi median musiman (Juni - September) untuk menghasilkan citra
bebas awan tahunan yang tahan terhadap sisa derau (robust composite).
"""

import numpy as np
from typing import List, Dict, Any

def seasonal_median_composite(images: List[np.ndarray], valid_masks: List[np.ndarray]) -> np.ndarray:
    """
    Menghitung komposit median piksel per piksel dengan mempertimbangkan mask validitas.
    Jika sebuah piksel memiliki mask invalid di semua scene, piksel tersebut diisi NaN.
    """
    if not images:
        raise ValueError("Daftar citra masukan kosong.")

    stacked = np.stack(images, axis=0).astype(np.float32)
    stacked_masks = np.stack(valid_masks, axis=0)

    # Isi piksel invalid dengan NaN agar diabaikan dalam nanmedian
    stacked[~stacked_masks] = np.nan
    composite = np.nanmedian(stacked, axis=0)
    return composite

def epoch_aggregation(annual_composites: Dict[int, np.ndarray],
                      epoch_years: List[int]) -> np.ndarray:
    """
    Menggabungkan komposit tahunan dalam suatu rentang kronologis
    (mis. Pre: 2019-2021, Post: 2025-2026) menggunakan median temporal.
    """
    selected = [annual_composites[y] for y in epoch_years if y in annual_composites]
    if not selected:
        raise KeyError(f"Tahun epoch {epoch_years} tidak ditemukan pada komposit tahunan.")
    return np.nanmedian(np.stack(selected, axis=0), axis=0)
