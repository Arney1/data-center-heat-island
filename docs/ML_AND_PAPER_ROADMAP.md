# Roadmap Tahap Lanjutan: Machine Learning & Penulisan Paper
## Riset Pengolahan Citra Digital (DIP) Pusat Data

Dokumen ini memetakan langkah konkret setelah selesainya tahap **Pengolahan Citra Digital (DIP)** untuk memenuhi seluruh luaran tugas besar:
1. **Penerapan Machine Learning (ML)** pada data citra satelit
2. **Pengembangan Antarmuka Interaktif Streamlit**
3. **Penyusunan Paper Riset Ilmiah** (Format IEEE / ISPRS)

---

## 1. Rencana Implementasi Machine Learning (ML)

### Tugas ML 1: Klasifikasi Tutupan Lahan Terbimbing (Supervised Classification)
- **Model:** Random Forest (RF) Classifier & Support Vector Machine (SVM)
- **Fitur Masukan (Features):**
  - Reflektansi Permukaan: $SR\_B2, SR\_B3, SR\_B4, SR\_B5, SR\_B6, SR\_B7$
  - Indeks Spektral: $NDVI, NDBI, MNDWI, Albedo$
- **Target Kelas:** 4 Kelas Tutupan Lahan:
  1. Vegetasi Alami / Tanaman
  2. Lahan Terbangun / Atap Bangunan
  3. Tanah Terbuka / Pasir
  4. Permukaan Air / Kolam Retensi
- **Evaluasi Model:**
  - Matriks Konfusi (Confusion Matrix)
  - Overall Accuracy (Target: $> 88\%$)
  - Cohen's Kappa Coefficient (Target: $> 0.82$)
  - Feature Importance (Gini Impurity / Mean Decrease in Impurity)

### Tugas ML 2: Regresi Prediksi Suhu Permukaan (LST Spatial Regression)
- **Model:** Random Forest Regressor / Gradient Boosting (XGBoost/LightGBM)
- **Tujuan:** Memprediksi nilai $LST_{anom}$ berdasarkan konfigurasi biofisik permukaan dan jarak ke pusat data.
- **Formulasi:**
  $$\widehat{LST}_{anom} = f(NDVI, NDBI, \alpha, \text{Elevasi}, \text{Jarak}_{\text{pusat}})$$
- **Validasi:** *Spatial Block Cross-Validation* (5-fold blok spasial untuk mencegah autokorelasi spasial bocor ke set evaluasi).
- **Interpretasi SHAP / Permutation Importance:** Mengukur seberapa besar porsi pemanasan yang dapat dijelaskan oleh hilangnya vegetasi vs kekedapan bangunan vs kedekatan ke data center.

### Tugas ML 3: Deteksi Hotspot Spasial Tanpa Supervisi (Unsupervised Thermal Anomaly Detection)
- **Model:** DBSCAN (Density-Based Spatial Clustering of Applications with Noise) atau Isolation Forest.
- **Tujuan:** Menemukan klaster anomali panas ekstrem di luar variasi latar belakang normal.

---

## 2. Antarmuka Interaktif Streamlit (`app/app.py`)

Aplikasi Streamlit telah disiapkan di folder `app/` dengan arsitektur modular:
- **Halaman 1:** Ringkasan Eksekutif & Pertanyaan Penelitian
- **Halaman 2:** Visualisasi Spasial Cincin Penyangga & Lokasi Kampus
- **Halaman 3:** Grafik Interaktif Runtun Waktu (2013–2026)
- **Halaman 4:** Lintasan Ekspansi Lahan Terbangun (ha)
- **Halaman 5:** Analisis Gradien Spasial & Tren Sen's Slope
- **Halaman 6:** Difference-in-Differences (DiD) Evaluasi Kontrol Berpasangan
- **Halaman 7:** Indeks IKTL & Simulator Sensitivitas Ablasi
- **Halaman 8:** Roadmap Machine Learning & Penulisan Paper

### Cara Menjalankan Streamlit:
```bash
# Aktifkan virtual environment
source .venv/bin/activate

# Jalankan dashboard
streamlit run app/app.py
```

---

## 3. Struktur Draf Paper Riset Ilmiah (IEEE / ISPRS)

### Struktur Bab:
1. **Title & Abstract:**
   - *Judul:* Multitemporal Analysis of Land Surface Temperature and Land-Cover Change Around Hyperscale Data Centers: A Case Study of AWS PDX Campus Using Landsat 8/9 and Machine Learning
   - *Abstract:* 200–250 kata merangkum latar belakang, metode DIP & ML, hasil kenaikan LST (+1.69 °C pada tapak, +2.27 °C pada bangunan, DiD +1.38 °C), dan batasan atribusi.
2. **I. Introduction:**
   - Pertumbuhan infrastruktur AI hyperscale dan kebutuhan energi/pendinginan.
   - Audit kritis terhadap paper Marinoni dkk. (2026) mengenai keterbatasan kelompok kontrol dan artefak retrieval.
3. **II. Study Area & Dataset:**
   - Deskripsi kampus AWS PDX-178 (Morrow County, Oregon, 127 acres, 4 data halls).
   - Katalog Landsat 8/9 Collection 2 Level-2 (L2SP) periode musim panas 2013–2026.
4. **III. Methodology (DIP & ML):**
   - Pra-pemrosesan (radiometrik, masking QA, ASTER GED emisivitas).
   - Ekstraksi indeks spektral dan albedo broadband (Liang 2001).
   - Analisis spasial: Cincin penyangga (0-500m, 500-1000m, 1-2km), area referensi regional.
   - Persistent sprawl mapping, Sen's slope, Mann-Kendall.
   - Difference-in-Differences (DiD) terhadap kontrol logistik non-DC.
   - Indeks Koinsidensi Termal-Lahan (IKTL) dan pengujian sensitivitas ablasi.
   - Pemodelan Machine Learning (Random Forest).
5. **IV. Results & Discussion:**
   - Verifikasi kronologi pembangunan vs tren spektral.
   - Gradien penurunan suhu terhadap jarak.
   - Hasil evaluasi kuasi-eksperimental DiD.
   - Audit artefak emisivitas ASTER GED.
6. **V. Limitations & Threats to Validity:**
   - Perbedaan suhu permukaan (LST) siang hari vs suhu udara ambient.
   - Batasan atribusi kausalitas panas buangan server vs perubahan biofisik material atap.
7. **VI. Conclusion:**
   - Kesimpulan ringkas menjawab RQ1–RQ7.
