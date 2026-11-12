# Multitemporal Analysis of Land Surface Temperature and Land-Cover Change Around Hyperscale Data Centers

[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Earth Engine](https://img.shields.io/badge/Platform-Google%20Earth%20Engine-brightgreen)](https://earthengine.google.com/)
[![Streamlit](https://img.shields.io/badge/Dashboard-Streamlit-red)](https://streamlit.io/)

> **Tugas Besar Pengolahan Citra Digital (Digital Image Processing / DIP)**  
> **Studi Kasus:** AWS PDX Bombing Campus (PDX-178), Boardman, Morrow County, Oregon, USA  
> **Sensor:** Landsat 8 & 9 Collection 2 Level-2 (L2SP) | 2013 – 2026 (14 Tahun Observasi)

---

## 📌 Daftar Isi / Table of Contents
1. [Ringkasan Proyek (Overview)](#-ringkasan-proyek-overview)
2. [Pertanyaan Penelitian (Research Questions)](#-pertanyaan-penelitian-research-questions)
3. [Arsitektur Repositori (Repository Structure)](#-arsitektur-repositori-repository-structure)
4. [Panduan Instalasi & Penggunaan (Getting Started)](#-panduan-instalasi--penggunaan-getting-started)
   - [A. Menjalankan Skrip GEE (Google Earth Engine)](#a-menjalankan-skrip-gee-google-earth-engine)
   - [B. Menjalankan Pipeline DIP Python](#b-menjalankan-pipeline-dip-python)
   - [C. Menjalankan Dashboard Streamlit](#c-menjalankan-dashboard-streamlit)
5. [Metodologi Pengolahan Citra Digital (DIP Pipeline)](#-metodologi-pengolahan-citra-digital-dip-pipeline)
6. [Ringkasan Temuan Empiris (Empirical Findings)](#-ringkasan-temuan-empiris-empirical-findings)
7. [Rencana Lanjutan: Machine Learning & Paper](#-rencana-lanjutan-machine-learning--paper)
8. [Referensi & Paper Acuan](#-referensi--paper-acuan)

---

## 📖 Ringkasan Proyek (Overview)

Pesatnya ekspansi pusat data kecerdasan buatan (*AI Hyperscale Data Centers*) menimbulkan pertanyaan mengenai dampak lingkungan lokalnya, khususnya fenomena pulau panas (*Data Heat Island Effect*). Penelitian ini mengkaji perubahan suhu permukaan tanah (*Land Surface Temperature*, LST) dan dinamika tutupan lahan di sekitar kampus pusat data **AWS PDX Bombing Campus (PDX-178)** di Boardman, Oregon sepanjang tahun 2013 hingga 2026.

Penelitian ini mengadopsi kerangka kerja metodologis dari audit kritis terhadap studi Marinoni dkk. (2026) dengan menambahkan:
1. **Normalisasi Anomali Suhu Regional** terhadap area pertanian stabil.
2. **Cincin Penyangga Spasial** (Tapak, Bangunan, 0–500m, 500–1000m, 1–2km) untuk mengevaluasi gradien peluruhan panas.
3. **Difference-in-Differences (DiD)** kuasi-eksperimental terhadap fasilitas kontrol logistik/industri non-DC.
4. **Audit Emisivitas ASTER GED** untuk memastikan kenaikan LST bukan artefak retrieval satelit.
5. **Indeks Koinsidensi Termal-Lahan (IKTL)** dengan analisis sensitivitas ablasi.

---

## 🎯 Pertanyaan Penelitian (Research Questions)

- **RQ1:** Bagaimana perubahan LST dan tutupan lahan antarperiode (pra-konstruksi, konstruksi, pasca-operasi) di tapak kampus dan zona penyangga sekitarnya?
- **RQ2:** Apakah kenaikan LST berasosiasi secara konsisten dengan penurunan indeks vegetasi (NDVI) dan kenaikan indeks terbangun (NDBI)?
- **RQ3:** Bagaimana profil gradien penurunan suhu menurut jarak ($G = \Delta T / \Delta d$), dan apakah gradien pasca-konstruksi lebih curam dibanding pra-konstruksi?
- **RQ4:** Di area mana anomali suhu menunjukkan kecenderungan naik persisten berdasarkan uji non-parametrik Sen's Slope dan Mann-Kendall?
- **RQ5:** Bagaimana pergeseran koefisien jarak dalam regresi spasial multivariat sebelum dan sesudah operasional?
- **RQ6:** Seberapa stabil peringkat sel pada Indeks Koinsidensi Termal-Lahan (IKTL) terhadap pengujian ablasi komponen?
- **RQ7 (Tingkat C):** Apakah kenaikan suhu di kampus pusat data berbeda secara signifikan dari fasilitas industri kontrol non-DC melalui estimator Difference-in-Differences (DiD)?

---

## 📂 Arsitektur Repositori (Repository Structure)

```text
tubes/
├── .gitignore
├── README.md                          # Dokumentasi utama proyek
├── requirements.txt                   # Dependensi Python
├── data/
│   ├── raw/
│   │   └── aws_pdx_boardman.geojson   # Poligon batas kampus, gedung, & titik kontrol
│   └── processed/
│       ├── zonal_lst_timeseries_2013_2026.csv
│       ├── builtup_expansion_trajectory.csv
│       └── spatial_metrics_summary.json
├── dip_pipeline/                      # Modul Inti Pengolahan Citra Digital (DIP)
│   ├── __init__.py
│   ├── config.py                      # Konfigurasi parameter spektral & sensor
│   ├── landsat_preprocessing.py       # Kalibrasi L2SP, masking bitwise QA, indeks spektral
│   ├── compositing.py                 # Reduksi median musiman bebas awan
│   ├── classification_segmentation.py # Ambang spektral, persistent sprawl, K-Means
│   ├── thermal_analysis.py            # Anomali LST, gradien spasial, Sen's slope, audit emisivitas
│   ├── spatial_indices.py             # Indeks IKTL & analisis sensitivitas ablasi
│   └── runner.py                      # CLI runner eksekutor seluruh modul DIP
├── gee_scripts/
│   └── 01_full_analysis_aws_pdx.js    # Skrip lengkap GEE JavaScript (Self-Contained)
├── app/
│   └── app.py                         # Antarmuka Dashboard Interaktif Streamlit
├── docs/
│   ├── PROGRES-PROYEK-DATA-CENTER-v2-refactor.md  # Rencana riset & dokumen audit awal
│   ├── DIP_METHODOLOGY_REPORT.md      # Laporan lengkap metodologi & teori DIP
│   └── ML_AND_PAPER_ROADMAP.md        # Panduan tahap Machine Learning & penulisan paper
└── paper/
    └── draft_paper_outline.md         # Kerangka draf publikasi ilmiah
```

---

## 🚀 Panduan Instalasi & Penggunaan (Getting Started)

### Persyaratan Awal:
- Python 3.10+
- Akun Google Earth Engine (opsional untuk menjalankan ulang raster langsung di cloud)

### 1. Kloning Repositori & Persiapan Lingkungan:
```bash
git clone https://github.com/<username>/<repo-name>.git
cd tubes

# Buat dan aktifkan virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Di Linux/macOS
# .venv\Scripts\activate   # Di Windows

# Pasang dependensi
pip install -r requirements.txt
```

### A. Menjalankan Skrip GEE (Google Earth Engine)
1. Buka browser dan kunjungi [Google Earth Engine Code Editor](https://code.earthengine.google.com/).
2. Buat skrip baru (*New Script*).
3. Buka file [`gee_scripts/01_full_analysis_aws_pdx.js`](file:///home/arney1/dev/courses/dip/projects/tubes/gee_scripts/01_full_analysis_aws_pdx.js) dan salin seluruh kodenya.
4. Tempel (*paste*) ke Code Editor dan klik **Run**.
5. Skrip bersifat **100% self-contained** (seluruh koordinat poligon kampus dan gedung telah diikutsertakan).

### B. Menjalankan Pipeline DIP Python
Jalankan modul CLI runner untuk memverifikasi seluruh perhitungan DIP:
```bash
python3 -m dip_pipeline.runner
```

### C. Menjalankan Dashboard Streamlit
Untuk mengeksplorasi hasil pengolahan citra digital secara interaktif melalui antarmuka web:
```bash
streamlit run app/app.py
```
Akses melalui peramban di `http://localhost:8501`.

---

## 🔬 Metodologi Pengolahan Citra Digital (DIP Pipeline)

Pipeline DIP mencakup 13 tahap yang dikelompokkan ke dalam 3 tingkat:
- **Tingkat A (Inti):**
  - **Tahap 1:** Definisi geometri tapak, gedung, cincin jarak penyangga, dan area referensi.
  - **Tahap 2 & Gerbang G3:** Pra-pemrosesan citra, masking `QA_PIXEL` (bit awan, bayangan, dilated), ketidakpastian suhu `ST_QA < 3.0K`, dan jarak ke awan `ST_CDIST > 0.2km`.
  - **Tahap 3:** Kompositing median musiman (Juni–September) dari Landsat 8 & 9 (2013–2026).
  - **Tahap 4:** Clustering tanpa supervisi K-Means ($k = 5, 10, 20$) pada fitur spektral.
  - **Tahap 5:** Kalibrasi ambang spektral lahan terbangun ($NDBI > -0.10, NDVI < 0.20$).
  - **Tahap 6:** Pemetaan tahun mulai terbangun persisten (*Persistent Urban Sprawl Mapping*) menggunakan logika *Backward Cumulative AND*.
  - **Tahap 8:** Audit gerbang emisivitas ASTER GED ($\Delta NDVI$ vs $\Delta EMIS$).
- **Tingkat B (Lanjutan):**
  - **Tahap 7:** Pemetaan LST dan anomali terhadap area referensi regional.
  - **Tahap 9:** Analisis tren piksel non-parametrik (Sen's Slope & Mann-Kendall $\tau$).
  - **Tahap 10:** Profil gradien spasial ($G = \Delta T / \Delta d$) dan perubahan gradien ($\Delta G$).
  - **Tahap 11:** Model regresi linear spasial kovariat (NDVI, NDBI, Elevasi, Albedo, Jarak).
  - **Tahap 12:** Indeks Koinsidensi Termal-Lahan (IKTL) dan analisis sensitivitas ablasi.
- **Tingkat C (Kuasi-Eksperimental):**
  - **Tahap 13:** Evaluasi Difference-in-Differences (DiD) terhadap kontrol berpasangan non-DC di kawasan industri terdekat.

---

## 📊 Ringkasan Temuan Empiris (Empirical Findings)

| Indikator | Pra-Konstruksi (2019-2021) | Pasca-Operasional (2025-2026) | Selisih ($\Delta$) | Keterangan |
|---|---|---|---|---|
| **Luas Bangunan Pusat Data** | 0.20 ha | 8.60 ha | **+8.40 ha** | 4 Data Halls terdeteksi persisten |
| **Anomali LST Bangunan ($0a$)** | +0.21 °C | +2.48 °C | **+2.27 °C** | Relatif terhadap referensi regional |
| **Anomali LST Tapak Penuh ($0$)** | +0.14 °C | +1.83 °C | **+1.69 °C** | Rata-rata tapak kampus |
| **Anomali LST Penyangga 0–500m** | +0.05 °C | +0.67 °C | **+0.62 °C** | Peluruhan efek termal lokal |
| **Anomali LST Penyangga 1–2km** | -0.16 °C | -0.06 °C | **+0.10 °C** | Menyerupai kondisi latar regional |
| **Gradien Spasial ($G$)** | -0.168 °C/km | -0.584 °C/km | **-0.416 °C/km** | Gradien meluruh curam terbentuk |
| **Net Effect DiD** | — | — | **+1.38 °C** | Kelebihan pemanasan di atas kontrol non-DC |

---

## 🔮 Rencana Lanjutan: Machine Learning & Paper

Lihat dokumen lengkap di [`docs/ML_AND_PAPER_ROADMAP.md`](file:///home/arney1/dev/courses/dip/projects/tubes/docs/ML_AND_PAPER_ROADMAP.md).
1. **Klasifikasi Tutupan Lahan Terbimbing:** Penerapan Random Forest (RF) dan SVM untuk memetakan perubahan tutupan lahan multi-kelas dengan evaluasi Matriks Konfusi & Kappa.
2. **Prediksi Spasial LST (Downscaling):** Model Random Forest Regressor untuk mengisolasi kontribusi relatif hilangnya vegetasi vs atap bangunan vs jarak pusat data.
3. **Penyusunan Paper Riset:** Penulisan naskah publikasi ilmiah berformat IEEE/ISPRS.

---

## 📚 Referensi & Paper Acuan

1. **Marinoni, A., dkk. (2026).** *The Data Heat Island Effect: Quantifying the Impact of AI Data Centers in a Warming World.* arXiv:2603.20897v3.
2. **Liang, S. (2001).** *Narrowband to broadband conversions of land surface albedo I: Algorithms.* Remote Sensing of Environment, 76(2), 213–238.
3. **Tasumi, M., dkk. (2008).** *At-surface albedo from the Landsat and MODIS satellites for use in energy balance models of evaporation.* Journal of Hydrologic Engineering, 13(1), 51–63.
4. **USGS.** *Landsat Collection 2 Level 2 Science Products & Surface Temperature Guides.*
