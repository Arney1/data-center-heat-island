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

# Geometri & Koordinat Presisi Digitasi Manual
CAMPUS_COORDS = [
    [-119.64171195208215, 45.81800973804475],
    [-119.63429296194695, 45.8180321700963],
    [-119.63383778657992, 45.81812409215994],
    [-119.62763950444914, 45.81813904683127],
    [-119.62761412100413, 45.81829961862225],
    [-119.62517331080058, 45.81832578921197],
    [-119.6251947684727,  45.82055398288432],
    [-119.62525404980258, 45.820627992663724],
    [-119.62750174095706, 45.82087099464729],
    [-119.62901450684146, 45.82087473313103],
    [-119.63007129719333, 45.82077753247144],
    [-119.63051117947177, 45.820598084653994],
    [-119.63057555248812, 45.82051583754439],
    [-119.63146068146304, 45.820508360528414],
    [-119.63154114773349, 45.82058686914621],
    [-119.63215805580691, 45.820762578508734],
    [-119.63524796059207, 45.82083360979578],
    [-119.64057482769564, 45.82081491736061],
    [-119.64174963524417, 45.82077005549056],
    [-119.64171195208215, 45.81800973804475]
]

BUILDINGS_MULTIPOLYGON = [
    # Gedung NW
    [
        [-119.63834382441334, 45.81937363830602],
        [-119.63423468020252, 45.81935868396625],
        [-119.63425613787464, 45.820330707696094],
        [-119.63834382441334, 45.82030827657055],
        [-119.63834382441334, 45.81937363830602]
    ],
    # Gedung NE
    [
        [-119.63411666300587, 45.81938111547438],
        [-119.629996789959,   45.81940354697348],
        [-119.63002897646717, 45.82036061584945],
        [-119.63411666300587, 45.82032323065526],
        [-119.63411666300587, 45.81938111547438]
    ],
    # Gedung SW
    [
        [-119.6383545532494,  45.81838664326721],
        [-119.63425613787464, 45.81838664326721],
        [-119.63424540903858, 45.819321298099304],
        [-119.63837601092152, 45.81929138938767],
        [-119.6383545532494,  45.81838664326721]
    ],
    # Gedung SE
    [
        [-119.63411666300587, 45.81837916596529],
        [-119.63001824763111, 45.81840907516693],
        [-119.63003970530323, 45.81935868396625],
        [-119.63410593416981, 45.81929886656709],
        [-119.63411666300587, 45.81837916596529]
    ]
]

STUDY_AREA = {
    "campus_name": "AWS PDX Bombing Campus (PDX-178)",
    "location": "Boardman, Morrow County, Oregon",
    "campus_centroid": [-119.6334, 45.8194],
    "control_pair_centroid": [-119.6975, 45.8361],
    "campus_bounds": CAMPUS_COORDS,
    "campus_ha": 38.14,
    "buildings_ha": 13.27,
    "building_ratio_pct": 34.80,
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
