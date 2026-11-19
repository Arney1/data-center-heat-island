"""Validasi CSV zonal; statistik hilang dipertahankan sebagai NaN."""

import numpy as np
import pandas as pd


METRICS = ("LST", "LSTanom", "NDVI", "NDBI", "EMIS")


def load_zonal_timeseries(source, expected_site_id):
    frame = pd.read_csv(source)
    missing = {"tahun", "zona", *METRICS} - set(frame.columns)
    if missing:
        raise ValueError("Kolom belum lengkap: " + ", ".join(sorted(missing)))
    if frame.empty:
        raise ValueError("CSV belum berisi data.")
    if "site_id" in frame and not frame["site_id"].eq(expected_site_id).all():
        raise ValueError(f"CSV bukan hasil lokasi {expected_site_id}.")
    frame["site_id"] = expected_site_id
    if frame["zona"].isna().any():
        raise ValueError("Nama zona tidak boleh kosong.")
    frame["zona"] = frame["zona"].astype(str).str.strip()
    if frame["zona"].eq("").any():
        raise ValueError("Nama zona tidak boleh kosong.")
    for column in ("tahun", *METRICS):
        frame[column] = pd.to_numeric(frame[column], errors="raise")
        if np.isinf(frame[column]).any():
            raise ValueError(f"Nilai tak hingga pada kolom {column}.")
    if frame["tahun"].isna().any() or (frame["tahun"] % 1 != 0).any():
        raise ValueError("Tahun harus bilangan bulat dan tidak boleh kosong.")
    frame["tahun"] = frame["tahun"].astype(int)
    if frame.duplicated(["tahun", "zona"]).any():
        raise ValueError("Ada pasangan tahun/zona yang duplikat.")
    return frame.sort_values(["tahun", "zona"]).reset_index(drop=True)
