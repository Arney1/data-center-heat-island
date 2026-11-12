"""
Konfigurasi Parameter Riset Pengolahan Citra Digital (DIP)
Studi Kasus: AWS PDX Bombing Campus (Boardman, Oregon)
Sensor: Landsat 8 & 9 Collection 2 Level-2 (L2SP)
"""

import os

# Direktori Dasar
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")

# Geometri & Koordinat
STUDY_AREA = {
    "campus_name": "AWS PDX Bombing Campus (PDX-178)",
    "location": "Boardman, Morrow County, Oregon",
    "campus_centroid": [-119.6342, 45.8193],
    "control_pair_centroid": [-119.6975, 45.8361],
    "campus_bounds": [
        [-119.6385, 45.8160],
        [-119.6295, 45.8160],
        [-119.6295, 45.8225],
        [-119.6385, 45.8225],
        [-119.6385, 45.8160]
    ],
    "buffer_zones_m": {
        "zone_campus": 0,
        "zone_1": 500,
        "zone_2": 1000,
        "zone_3": 2000
    },
    "regional_ref_ring_km": [5.0, 12.0]
}

# Periode Observasi & Jendela Musim
YEARS = list(range(2013, 2027))
SEASON_START_MONTH = 6  # Juni (musim panas/kering)
SEASON_END_MONTH = 9    # September

PRE_YEARS = [2019, 2020, 2021]
CONSTRUCTION_YEARS = [2022, 2023, 2024]
POST_YEARS = [2025, 2026]
K_MEANS_REF_YEAR = 2025

# Ambang Batas Kualitas Citra (Quality Assessment Gates)
QA_CONFIG = {
    "st_qa_max_kelvin": 3.0,     # Batas ketidakpastian suhu maksimum ST_QA
    "cdist_min_km": 0.2,         # Jarak minimum piksel ke awan ST_CDIST
    "fv_min": 0.70,              # Fraksi piksel valid minimum per scene
    "cloud_bits": [1, 3, 4]      # Dilated cloud (1), cloud (3), cloud shadow (4)
}

# Ambang Spektral Indeks Lahan Terbangun
SPECTRAL_THRESHOLDS = {
    "thr_ndbi": -0.10,          # Ambang awal NDBI
    "thr_ndvi_built": 0.20,     # Ambang NDVI vegetasi vs terbangun
    "thr_mndwi_water": 0.00     # Ambang MNDWI air
}

# Formula Liang (2001) / Tasumi et al. (2008) untuk Broadband Surface Albedo
# Albedo = 0.356*B2 + 0.130*B4 + 0.373*B5 + 0.085*B6 + 0.072*B7 - 0.0018
ALBEDO_WEIGHTS = {
    "SR_B2": 0.356,
    "SR_B4": 0.130,
    "SR_B5": 0.373,
    "SR_B6": 0.085,
    "SR_B7": 0.072,
    "offset": -0.0018
}

# Parameter Sensor Landsat 8 & 9 (L2SP)
LANDSAT_SCALING = {
    "sr_scale": 0.0000275,
    "sr_offset": -0.2,
    "st_scale": 0.00341802,
    "st_offset": 149.0,
    "st_emis_scale": 0.0001,
    "st_qa_scale": 0.01,
    "st_cdist_scale": 0.01
}
