# Comparative Multitemporal Analysis of Land Surface Temperature and Land-Cover Dynamics Around Hyperscale AI Data Centers

[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Earth Engine](https://img.shields.io/badge/Platform-Google%20Earth%20Engine-brightgreen)](https://earthengine.google.com/)
[![Geemap](https://img.shields.io/badge/Interactive%20Mapping-Geemap-orange)](https://geemap.org/)
[![Streamlit](https://img.shields.io/badge/Dashboard-Streamlit-red)](https://streamlit.io/)

> **Tugas Besar Pengolahan Citra Digital (Digital Image Processing / DIP) & Machine Learning**  
> **Studi Komparatif Dua Lokasi (Dual-Site Comparative Study):**  
> 1. **Site 1:** AWS PDX Bombing Campus (PDX-178), Boardman, Morrow County, Oregon, USA  
> 2. **Site 2:** H5 Quincy II Data Center, Quincy, Grant County, Washington, USA  
> **Sensor:** Landsat 8 & 9 Collection 2 Level-2 (L2SP) | 2013 – 2026 (14 Tahun Observasi Musim Panas/Kering)  
> **Target Publikasi:** Jurnal Ilmiah Terakreditasi Nasional (SINTA 2) / Prosiding Internasional IEEE / ISPRS

---

## 📌 Daftar Isi / Table of Contents
1. [Ringkasan Proyek & Problem Statement](#-ringkasan-proyek--problem-statement)
2. [Lokasi Studi Komparatif (Dual-Site)](#-lokasi-studi-komparatif-dual-site)
3. [Pertanyaan Penelitian (Research Questions)](#-pertanyaan-penelitian-research-questions)
4. [Arsitektur Repositori (Repository Architecture)](#-arsitektur-repositori-repository-architecture)
5. [Jadwal Kerja 4 Minggu (4-Week Milestone Roadmap)](#-jadwal-kerja-4-minggu-4-week-milestone-roadmap)
6. [Implementasi Minggu 1: Python GEE Fetcher & Machine Learning](#-implementasi-minggu-1-python-gee-fetcher--machine-learning)
7. [Panduan Instalasi & Eksekusi](#-panduan-instalasi--eksekusi)
8. [Temuan Empiris & Hasil Awal](#-temuan-empiris--hasil-awal)
9. [Relevansi Akademik & Strategi Publikasi SINTA 2](#-relevansi-akademik--strategi-publikasi-sinta-2)
10. [Referensi & Literatur Acuan](#-referensi--literatur-acuan)

---

## 📖 Ringkasan Proyek & Problem Statement

### Masalah Apa yang Sedang Diselesaikan? (*What Problem Are We Solving?*)
Pesatnya pertumbuhan infrastruktur komputasi kecerdasan buatan (*AI Hyperscale Data Centers*) memicu kekhawatiran global mengenai dampak termal lokalnya ke lingkungan (*Data Heat Island Effect*). Sebuah studi kontroversial (Marinoni dkk., arXiv 2026) melaporkan bahwa data center menyebabkan pemanasan ekstrem hingga **+9 °C dengan radius dampak hingga 10 km**. 

Namun, audit metodologis menemukan kelemahan mendasar dalam studi tersebut:
1. **Resolusi Kasar & Pengabaian Efek Campur:** Menggunakan MODIS 500m yang mencampurkan tapak gedung dengan tutupan kota sekitarnya.
2. **Absennya Kelompok Kontrol Kuasi-Eksperimental:** Tidak membedakan apakah pemanasan disebabkan oleh **panas buangan operasional server (*IT waste heat*)** atau sekadar **konversi fisik material atap dan hilangnya vegetasi**.
3. **Ketiadaan Validasi Lintas Tapak (*Cross-Site Generalizability*):** Tidak menguji apakah fenomena serupa terjadi pada fasilitas dengan topologi berbeda.

### Dari *KNOW* Menjadi *IMPROVE* (Peran Machine Learning)
Penelitian ini tidak hanya berhenti pada observasi retrospektif (*KNOW*), melainkan menyajikan **solusi rekayasa prediktif (*IMPROVE*)**:
- **Simulator Prediksi Mitigasi LST:** Mengembangkan model Machine Learning ($LST_{anom} = f(NDVI, NDBI, \alpha, \text{Elevasi}, \text{Jarak})$) untuk mensimulasikan dampak strategi mitigasi—misalnya, seberapa besar penurunan suhu lokal jika atap data center menggunakan *cool roof* (peningkatan albedo $\alpha$ dari 0.15 ke 0.40) atau pelestarian sabuk vegetasi hijau 30%.
- **Generalisasi Lintas Domain (*Cross-Site Domain Adaptation*):** Menguji apakah model ML yang dilatih pada kampus mega-skala Oregon dapat digeneralisasi ke klaster data center Washington.
- **Validasi Spasial Tanpa Bocor (*Spatial Block Cross-Validation*):** Membuktikan bahwa validasi acak (*Random CV*) menghasilkan optimisme palsu akibat autokorelasi spasial, sedangkan *Spatial Block CV* menjamin keandalan model di dunia nyata.

---

## 🗺️ Lokasi Studi Komparatif (Dual-Site)

| Parameter | Site 1: AWS PDX-178 (Boardman, OR) | Site 2: H5 Quincy II (Quincy, WA) |
|---|---|---|
| **Negara Bagian / Wilayah** | Oregon, Morrow County (Columbia Basin) | Washington, Grant County (Columbia Basin) |
| **Koordinat Centroid** | -119.6334° W, 45.8194° N | -119.8253° W, 47.2476° N |
| **Topologi Tapak** | 4 Gedung Mega Data Halls terpisah dalam pagar tapak presisi | 6 Gedung Data Halls dalam 1 klaster industri terpadu |
| **Luas Tapak Kampus** | 38.14 ha (127 acres) | ~2.93 ha (Klaster Kompak) |
| **Luas Bangunan Saja** | 13.27 ha (34.8% rasio tutupan) | ~1.35 ha (~46.1% rasio tutupan) |
| **Kontrol Industri (DiD)** | Fasilitas Logistik Boardman (-119.6975, 45.8361) | Kawasan Industri Pemrosesan Quincy (-119.8550, 47.2340) |
| **Karakteristik Lingkungan** | Semi-arid, semak belukar & lingkaran irigasi | Semi-arid, pertanian intensif & hub energi hidro |

---

## 🎯 Pertanyaan Penelitian (Research Questions)

- **RQ1:** Bagaimana dinamika suhu permukaan (LST) dan tutupan lahan antarperiode (pra-konstruksi, konstruksi, pasca-konstruksi) di tapak kampus dan zona penyangga sekitarnya pada kedua lokasi?
- **RQ2:** Apakah respons anomali termal berasosiasi konsisten dengan penurunan NDVI dan kenaikan NDBI di kedua lokasi studi?
- **RQ3:** Bagaimana profil gradien penurunan suhu menurut jarak ($G = \Delta T / \Delta d$), dan apakah gradien pasca-konstruksi meluruh secara curam dalam radius < 1 km?
- **RQ4:** Di area mana anomali suhu menunjukkan tren naik persisten berdasarkan uji non-parametrik Sen's Slope dan Mann-Kendall?
- **RQ5:** Bagaimana pergeseran koefisien jarak dalam regresi multivariat spasial sebelum vs sesudah operasional kampus?
- **RQ6:** Apakah kenaikan suhu di tapak data center secara signifikan melampaui fasilitas industri kontrol non-DC melalui Difference-in-Differences (DiD)?
- **RQ7 (Machine Learning):** Seberapa akurat model klasifikasi terbimbing (Random Forest & SVM) dan regresi spasial berbasis *Spatial Block Cross-Validation* dalam memprediksi tutupan lahan dan anomali suhu di kedua tapak data center?

---

## 📂 Arsitektur Repositori (Repository Architecture)

```text
tubes/
├── README.md                          # Dokumentasi utama proyek
├── requirements.txt                   # Dependensi Python (EE, Geemap, Scikit-Learn, Streamlit)
├── data/
│   ├── raw/
│   │   └── aws_pdx_boardman.geojson   # Batas tapak kampus, data halls, & titik kontrol
│   └── processed/
│       ├── zonal_lst_timeseries_2013_2026.csv
│       ├── builtup_expansion_trajectory.csv
│       ├── spatial_metrics_summary.json
│       ├── ml_feature_dataset.csv     # 1.200 sampel piksel multitemporal terkalibrasi
│       └── ml_classification_results.json # Hasil evaluasi model ML Minggu 1
├── dip_pipeline/                      # Pipeline Pengolahan Citra Digital (DIP) & Fetcher
│   ├── __init__.py
│   ├── config.py                      # Multi-site configuration (AWS PDX + H5 Quincy II)
│   ├── gee_fetcher.py                 # Python GEE & Geemap Data Fetcher (Translasi JS)
│   ├── landsat_preprocessing.py       # Kalibrasi L2SP, QA masking bitwise, indeks spektral
│   ├── compositing.py                 # Reduksi median musiman bebas awan
│   ├── classification_segmentation.py # Ambang spektral & persistent sprawl mapping
│   ├── thermal_analysis.py            # Anomali LST, gradien spasial, Sen's slope, audit emisivitas
│   ├── spatial_indices.py             # Indeks IKTL & analisis sensitivitas ablasi
│   ├── runner.py                      # CLI runner audit DIP lengkap
│   └── ml/                            # Subpaket Machine Learning
│       ├── __init__.py
│       ├── dataset.py                 # Dataset loader, stratified split & spatial block folds
│       ├── supervised_classification.py # Random Forest & SVM land cover classifiers
│       └── runner_ml.py               # CLI runner eksekutor ML Minggu 1
├── gee_scripts/
│   └── 01_full_analysis_aws_pdx.js    # Skrip GEE JavaScript Mandiri (Code Editor)
├── app/
│   └── app.py                         # Web Dashboard Interaktif Streamlit
├── docs/
│   ├── PROGRES-PROYEK-DATA-CENTER-v2-refactor.md  # Rencana riset komprehensif
│   ├── DIP_METHODOLOGY_REPORT.md      # Laporan teoritis & metodologis DIP
│   └── ML_AND_PAPER_ROADMAP.md        # Roadmap riset ML & strategi penulisan paper
└── paper/
    └── draft_paper_outline.md         # Kerangka draf publikasi ilmiah IEEE/ISPRS
```

---

## 🗓️ Jadwal Kerja 4 Minggu (4-Week Milestone Roadmap)

| Minggu | Fokus Utama | Luaran Kunci | Status |
|---|---|---|---|
| **Minggu 1 (Minggu Ini)** | **Data Fetcher (`ee` & `geemap`) & Klasifikasi Tutupan Lahan** | Porting `01_full_analysis_aws_pdx.js` ke Python [`dip_pipeline/gee_fetcher.py`](file:///home/arney1/dev/courses/dip/projects/tubes/dip_pipeline/gee_fetcher.py); ekstraksi dataset fitur 30m; pelatihan model **Random Forest & SVM**; evaluasi OA, Kappa, dan *Feature Importance*. | **SELESAI** ✅ |
| **Minggu 2** | **Regresi Spasial LST & *Explainable AI* (XAI)** | Pemodelan regresi spasial LST ($LST_{anom} = f(NDVI, NDBI, \alpha, \text{Elev}, \text{Dist})$) dengan Random Forest Regressor; evaluasi **5-Fold Spatial Block Cross-Validation** (mencegah *spatial data leakage*); analisis atribusi fitur SHAP. | **TERJADWAL** ⏳ |
| **Minggu 3** | **Deteksi Hotspot Tanpa Supervisi & Uji Hipotesis Lanjutan** | Deteksi anomali spasial tanpa supervisi (**DBSCAN & Isolation Forest**); klasterisasi K-Means multi-$k$ ($k=5, 10, 20$); analisis sensitivitas ablasi IKTL; uji Difference-in-Differences & uji plasebo spasial/temporal. | **TERJADWAL** ⏳ |
| **Minggu 4** | **Integrasi Antarmuka Web Streamlit & Draf Paper Riset** | Integrasi peta interaktif Geemap (*split map slider*) dan simulator prediksi mitigasi ke Streamlit; finalisasi manuskrip paper riset ilmiah format IEEE/ISPRS di folder [`paper/`](file:///home/arney1/dev/courses/dip/projects/tubes/paper/). | **TERJADWAL** ⏳ |

---

## 🤖 Implementasi Minggu 1: Python GEE Fetcher & Machine Learning

### 1. Python Earth Engine & Geemap Fetcher
Modul [`dip_pipeline/gee_fetcher.py`](file:///home/arney1/dev/courses/dip/projects/tubes/dip_pipeline/gee_fetcher.py) bertindak sebagai *data fetcher* aktif langsung ke Google Earth Engine API:
- Mendukung dua site data center secara modular (`site_id="aws_pdx"` atau `site_id="h5_quincy2"`).
- Menyaring citra Landsat 8/9 Level-2 Collection 2 (jendela musim panas Juni–September 2013–2026).
- Menerapkan masking bitwise QA (`QA_PIXEL`), batas ketidakpastian suhu `ST_QA < 3.0 K`, dan jarak awan `ST_CDIST > 0.2 km`.
- Menghasilkan komposit median tahunan dan mengekstraksi 1.200 sampel piksel berfitur spektral-termal lengkap.

### 2. Kinerja Model Klasifikasi Tutupan Lahan (Minggu 1)
Evaluasi pada 300 sampel data uji independen (*25% Test Set*):
- **Random Forest Classifier:** Overall Accuracy = **100.00%**, Cohen's Kappa = **1.0000**
- **Support Vector Machine (RBF):** Overall Accuracy = **100.00%**, Cohen's Kappa = **1.0000**
- **Fitur Spektral-Termal Paling Berpengaruh (Gini Importance):**
  1. `LST` (Suhu Permukaan): 0.2187
  2. `MNDWI` (Indeks Kelembapan/Air): 0.1210
  3. `SR_B4` (Red Band): 0.1145
  4. `SR_B5` (NIR Band): 0.1097
  5. `SR_B7` (SWIR-2 Band): 0.0826

---

## 🚀 Panduan Instalasi & Eksekusi

### 1. Persiapan Lingkungan:
```bash
git clone https://github.com/<username>/<repo-name>.git
cd tubes

# Buat dan aktifkan virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Pasang dependensi
pip install -r requirements.txt
```

### 2. Menjalankan Pipeline Machine Learning Minggu 1:
```bash
python3 -m dip_pipeline.ml.runner_ml
```

### 3. Menjalankan Pipeline DIP Lengkap:
```bash
python3 -m dip_pipeline.runner
```

### 4. Menjalankan Dashboard Interaktif Streamlit:
```bash
streamlit run app/app.py
```
Akses melalui peramban web di `http://localhost:8501`.

---

## 📊 Temuan Empiris & Hasil Awal (AWS PDX Boardman)

| Indikator Spasial-Termal | Pra-Konstruksi (2019-2021) | Pasca-Operasional (2025-2026) | Selisih ($\Delta$) | Keterangan Metodologis |
|---|---|---|---|---|
| **Luas Terbangun Bangunan ($0a$)** | 0.15 ha | 13.27 ha | **+13.12 ha** | 4 Data Halls terdeteksi persisten |
| **Anomali LST Bangunan ($0a$)** | +0.20 °C | +2.51 °C | **+2.31 °C** | Relatif terhadap referensi regional |
| **Anomali LST Tapak Penuh ($0$)** | +0.14 °C | +1.86 °C | **+1.72 °C** | Rata-rata tapak kampus |
| **Anomali LST Penyangga 0–500m** | +0.05 °C | +0.69 °C | **+0.64 °C** | Peluruhan efek termal lokal |
| **Anomali LST Penyangga 1–2km** | -0.16 °C | -0.05 °C | **+0.11 °C** | Menyerupai kondisi latar regional |
| **Gradien Spasial ($G$)** | -0.168 °C/km | -0.592 °C/km | **-0.424 °C/km** | Gradien meluruh curam terbentuk |
| **Net Effect DiD (Tingkat C)** | — | — | **+1.42 °C** | Efek termal bersih relatif kontrol non-DC |

---

## 🎓 Relevansi Akademik & Strategi Publikasi SINTA 2

Riset ini memenuhi kriteria publikasi jurnal terakreditasi **SINTA 2** (seperti *Jurnal Ilmu Komputer dan Informasi (JIKI)* UI, *Jurnal RESTI*, atau *Jurnal Penginderaan Jauh LAPAN/BRIN*) berkat kebaruan metodologis berikut:
1. **Bantahan Empiris Beresolusi Tinggi:** Mengoreksi klaim berlebihan literatur sebelumnya (Marinoni dkk. 2026) dengan resolusi 30m Landsat dan isolasi poligon bangunan murni.
2. **Desain Komparatif Lintas Lokasi (*Dual-Site*):** Membandingkan kampus berskala besar di Oregon dengan klaster fasilitas di Washington pada rezim iklim Columbia Basin yang sama.
3. **Validasi Spasial Ketat (*Spatial Block Cross-Validation*):** Mencegah kebocoran data spasial yang lazim diabaikan dalam studi penginderaan jauh terapan.
4. **Explainable AI (XAI) & Simulasi Solutif:** Memisahkan secara kuantitatif proporsi kenaikan suhu yang berasal dari penurunan albedo vs kehilangan vegetasi vs kedekatan ke data center, serta menyediakan simulasi mitigasi (*cool roof*).

---

## 📚 Referensi & Literatur Acuan

1. **Marinoni, A., dkk. (2026).** *The Data Heat Island Effect: Quantifying the Impact of AI Data Centers in a Warming World.* arXiv:2603.20897v3.
2. **Liang, S. (2001).** *Narrowband to broadband conversions of land surface albedo I: Algorithms.* Remote Sensing of Environment, 76(2), 213–238.
3. **Tasumi, M., dkk. (2008).** *At-surface albedo from the Landsat and MODIS satellites for use in energy balance models of evaporation.* Journal of Hydrologic Engineering, 13(1), 51–63.
4. **Roberts, D. R., dkk. (2017).** *Cross-validation strategies for data with temporal, spatial, hierarchical or phylogenetic structure.* Ecography, 40(8), 913–929. *(Dasar Spatial Block CV)*.
5. **Lundberg, S. M., & Lee, S. I. (2017).** *A unified approach to interpreting model predictions.* NeurIPS 30. *(Dasar SHAP Attribution)*.
