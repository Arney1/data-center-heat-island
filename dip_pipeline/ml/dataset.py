"""
Dataset Manager untuk Machine Learning
Menangani pemuatan fitur, pembagian data (Stratified & Spatial Block CV),
dan standarisasi data masukan.
"""

import os
from typing import Dict, List, Tuple, Optional
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from ..config import PROCESSED_DATA_DIR
from ..gee_fetcher import GEEDataFetcher

# Definisi Kelompok Fitur
SPECTRAL_BANDS = ["SR_B2", "SR_B3", "SR_B4", "SR_B5", "SR_B6", "SR_B7"]
SPECTRAL_INDICES = ["NDVI", "NDBI", "MNDWI", "Albedo"]
THERMAL_FEATURES = ["LST", "EMIS"]
TOPOGRAPHIC_FEATURES = ["elevation", "slope", "distance_dc_km"]

ALL_CLASSIFICATION_FEATURES = SPECTRAL_BANDS + SPECTRAL_INDICES + THERMAL_FEATURES
REGRESSION_FEATURES = ["NDVI", "NDBI", "Albedo", "elevation", "distance_dc_km"]

CLASS_NAMES = {
    1: "Vegetation / Agriculture",
    2: "Built-up / Data Center",
    3: "Bare Soil / Fallow",
    4: "Water / Retention Pond"
}

CLASS_COLORS = {
    1: "#2ca02c",  # Hijau
    2: "#d62728",  # Merah
    3: "#bcbd22",  # Kuning tanah
    4: "#1f77b4"   # Biru
}


class MLDatasetManager:
    """
    Mengelola pemuatan, persiapan, dan validasi dataset Machine Learning.
    """

    def __init__(self, csv_path: Optional[str] = None):
        self.csv_path = csv_path or os.path.join(PROCESSED_DATA_DIR, "ml_feature_dataset.csv")
        self.df: Optional[pd.DataFrame] = None
        self.scaler = StandardScaler()
        self._load_or_fetch_dataset()

    def _load_or_fetch_dataset(self):
        """Memuat dataset fitur dari disk, atau memicunya lewat GEEDataFetcher jika belum ada."""
        if not os.path.exists(self.csv_path):
            fetcher = GEEDataFetcher()
            self.df = fetcher.extract_ml_feature_dataset(n_samples=1200)
        else:
            self.df = pd.read_csv(self.csv_path)

    def get_classification_data(
        self,
        features: Optional[List[str]] = None,
        test_size: float = 0.25,
        random_state: int = 42,
        scale_features: bool = False
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, List[str]]:
        """
        Menyiapkan data training dan testing untuk klasifikasi tutupan lahan (Supervised).
        Menggunakan stratified sampling agar proporsi kelas seimbang di train dan test.
        """
        if self.df is None:
            raise ValueError("Dataset belum dimuat.")

        feat_cols = features or ALL_CLASSIFICATION_FEATURES
        X = self.df[feat_cols].values
        y = self.df["land_cover_class"].values

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )

        if scale_features:
            X_train = self.scaler.fit_transform(X_train)
            X_test = self.scaler.transform(X_test)

        return X_train, X_test, y_train, y_test, feat_cols

    def get_spatial_blocks(self, n_blocks_x: int = 2, n_blocks_y: int = 2) -> np.ndarray:
        """
        Membuat indeks blok spasial (Spatial Block K-Fold) berbasis grid koordinat (lon, lat)
        untuk mencegah kebocoran autokorelasi spasial (Spatial Data Leakage).
        """
        if self.df is None:
            raise ValueError("Dataset belum dimuat.")

        lons = self.df["longitude"].values
        lats = self.df["latitude"].values

        lon_min, lon_max = lons.min(), lons.max()
        lat_min, lat_max = lats.min(), lats.max()

        x_bins = np.linspace(lon_min, lon_max, n_blocks_x + 1)
        y_bins = np.linspace(lat_min, lat_max, n_blocks_y + 1)

        x_idx = np.digitize(lons, x_bins) - 1
        x_idx = np.clip(x_idx, 0, n_blocks_x - 1)

        y_idx = np.digitize(lats, y_bins) - 1
        y_idx = np.clip(y_idx, 0, n_blocks_y - 1)

        block_ids = y_idx * n_blocks_x + x_idx
        return block_ids
