"""
Modul Pra-pemrosesan Citra Satelit Landsat 8 & 9 (Collection 2 Level-2 L2SP)
Mencakup:
1. Kalibrasi Radiometrik (Skala dan Offset Reflektansi & Suhu Kecerahan/LST)
2. Masking Awan, Bayangan, Dilated Cloud, dan Ketidakpastian Suhu (QA Filtering)
3. Ekstraksi Fitur Spektral: NDVI, NDBI, MNDWI, dan Broadband Albedo
"""

import numpy as np
from .config import QA_CONFIG, LANDSAT_SCALING, ALBEDO_WEIGHTS

def calibrate_surface_reflectance(raw_sr_band: np.ndarray) -> np.ndarray:
    """
    Mengubah Digital Number (DN) Surface Reflectance Landsat C2 L2 menjadi reflektansi riil [0, 1].
    Ref = DN * 0.0000275 - 0.2
    """
    scaled = raw_sr_band.astype(np.float32) * LANDSAT_SCALING["sr_scale"] + LANDSAT_SCALING["sr_offset"]
    return np.clip(scaled, 0.0, 1.0)

def calibrate_lst_celsius(raw_st_b10: np.ndarray) -> np.ndarray:
    """
    Mengubah DN Thermal Band 10 Landsat C2 L2 menjadi Suhu Permukaan (LST) dalam Celcius.
    Kelvin = DN * 0.00341802 + 149.0
    Celsius = Kelvin - 273.15
    """
    kelvin = raw_st_b10.astype(np.float32) * LANDSAT_SCALING["st_scale"] + LANDSAT_SCALING["st_offset"]
    celsius = kelvin - 273.15
    return celsius

def calibrate_emissivity(raw_st_emis: np.ndarray) -> np.ndarray:
    """
    Mengubah DN Emisivitas ASTER GED menjadi nilai emisivitas permukaan [0, 1].
    Emis = DN * 0.0001
    """
    return raw_st_emis.astype(np.float32) * LANDSAT_SCALING["st_emis_scale"]

def generate_qa_mask(qa_pixel: np.ndarray, st_qa: np.ndarray = None, st_cdist: np.ndarray = None) -> np.ndarray:
    """
    Membuat boolean mask untuk piksel jernih (clean pixels) berbasis:
    - Bit 1: Dilated Cloud == 0
    - Bit 3: Cloud == 0
    - Bit 4: Cloud Shadow == 0
    - ST_QA < ST_QA_MAX (3.0 Kelvin)
    - ST_CDIST > CDIST_MIN_KM (0.2 km)
    """
    mask_dilated = (qa_pixel & (1 << 1)) == 0
    mask_cloud = (qa_pixel & (1 << 3)) == 0
    mask_shadow = (qa_pixel & (1 << 4)) == 0
    valid_mask = mask_dilated & mask_cloud & mask_shadow

    if st_qa is not None:
        qa_kelvin = st_qa * LANDSAT_SCALING["st_qa_scale"]
        valid_mask = valid_mask & (qa_kelvin < QA_CONFIG["st_qa_max_kelvin"])

    if st_cdist is not None:
        cdist_km = st_cdist * LANDSAT_SCALING["st_cdist_scale"]
        valid_mask = valid_mask & (cdist_km > QA_CONFIG["cdist_min_km"])

    return valid_mask

def compute_ndvi(nir: np.ndarray, red: np.ndarray, eps: float = 1e-6) -> np.ndarray:
    """
    Normalized Difference Vegetation Index:
    NDVI = (NIR - Red) / (NIR + Red)
    Landsat 8/9: NIR = SR_B5, Red = SR_B4
    """
    denominator = nir + red
    denominator = np.where(denominator == 0, eps, denominator)
    ndvi = (nir - red) / denominator
    return np.clip(ndvi, -1.0, 1.0)

def compute_ndbi(swir1: np.ndarray, nir: np.ndarray, eps: float = 1e-6) -> np.ndarray:
    """
    Normalized Difference Built-up Index:
    NDBI = (SWIR1 - NIR) / (SWIR1 + NIR)
    Landsat 8/9: SWIR1 = SR_B6, NIR = SR_B5
    """
    denominator = swir1 + nir
    denominator = np.where(denominator == 0, eps, denominator)
    ndbi = (swir1 - nir) / denominator
    return np.clip(ndbi, -1.0, 1.0)

def compute_mndwi(green: np.ndarray, swir1: np.ndarray, eps: float = 1e-6) -> np.ndarray:
    """
    Modified Normalized Difference Water Index:
    MNDWI = (Green - SWIR1) / (Green + SWIR1)
    Landsat 8/9: Green = SR_B3, SWIR1 = SR_B6
    """
    denominator = green + swir1
    denominator = np.where(denominator == 0, eps, denominator)
    mndwi = (green - swir1) / denominator
    return np.clip(mndwi, -1.0, 1.0)

def compute_broadband_albedo(b2_blue: np.ndarray, b4_red: np.ndarray,
                             b5_nir: np.ndarray, b6_swir1: np.ndarray,
                             b7_swir2: np.ndarray) -> np.ndarray:
    """
    Broadband Shortwave Surface Albedo (Formula Liang 2001 / Tasumi et al. 2008):
    Albedo = 0.356*B2 + 0.130*B4 + 0.373*B5 + 0.085*B6 + 0.072*B7 - 0.0018
    """
    albedo = (
        ALBEDO_WEIGHTS["SR_B2"] * b2_blue +
        ALBEDO_WEIGHTS["SR_B4"] * b4_red +
        ALBEDO_WEIGHTS["SR_B5"] * b5_nir +
        ALBEDO_WEIGHTS["SR_B6"] * b6_swir1 +
        ALBEDO_WEIGHTS["SR_B7"] * b7_swir2 +
        ALBEDO_WEIGHTS["offset"]
    )
    return np.clip(albedo, 0.0, 1.0)
