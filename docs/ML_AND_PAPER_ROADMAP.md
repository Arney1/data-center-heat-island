# Roadmap Machine Learning, Riset Komparatif Multi-Site, & Publikasi Ilmiah

Dokumen ini memetakan rancangan strategis, eksperimen Machine Learning (ML), dan struktur naskah ilmiah untuk memenuhi target publikasi **Jurnal Terakreditasi Nasional (SINTA 2)** atau **Prosiding Internasional Bereputasi (IEEE / ISPRS)**.

---

## 1. Problem Statement: Masalah Apa yang Sedang Diselesaikan?

Banyak mahasiswa dan peneliti pemula remote sensing terjebak dalam pertanyaan: *"Apakah kita hanya mendeskripsikan data (KNOW) atau memecahkan masalah (IMPROVE)?"*

Dalam riset penginderaan jauh (*Earth Observation*) dan *Environmental AI*, masalah ilmiah utama bukanlah sekadar "membuat aplikasi perangkat lunak", melainkan **memecahkan masalah atribusi kausalitas (*Attribution Problem*), bias generalisasi (*Domain Shift*), dan pemodelan prediktif untuk mitigasi (*Predictive Engineering*)**:

### A. Tiga Masalah Ilmiah yang Kita Pecahkan
1. **Masalah Kontroversi & Bias Literatur (Empirical Attribution Gap):**
   - *Latar Belakang:* Paper Marinoni dkk. (arXiv 2026) mengklaim pusat data AI memicu pulau panas ekstrem (*Data Heat Island*) hingga **+9 °C dengan radius dampak mencapai 10 km**.
   - *Kelemahan Literatur:* Menggunakan data MODIS resolusi kasar (500m), tanpa kelompok kontrol berpasangan, dan tanpa memisahkan apakah panas berasal dari **panas buangan server (IT waste heat)** atau **konversi fisik material (atap hitam & semen pengganti vegetasi)**.
   - *Solusi Kita:* Menerapkan resolusi tinggi (30m Landsat 8/9), isolasi piksel murni atap gedung (-15m buffer), normalisasi anomali regional, dan kuasi-eksperimental Difference-in-Differences (DiD) terhadap fasilitas industri non-DC.

2. **Masalah Generalisasi Lintas Tapak (*Cross-Site Generalizability & Domain Adaptation*):**
   - *Latar Belakang:* Apakah dampak termal data center bersifat universal atau bergantung pada topologi fasilitas?
   - *Solusi Kita (Dual-Site):* Membandingkan **AWS PDX Bombing Campus** (kampus mega 38 ha di Oregon) dengan **H5 Quincy II** (klaster kompak 2.9 ha di Washington) pada rezim iklim semi-arid Columbia Basin yang sama.

3. **Masalah Kebocoran Data Spasial (*Spatial Data Leakage*):**
   - Dalam machine learning geospasial, membagi data train/test secara acak (*Random Split*) melanggar *Hukum Pertama Tobler* (*Everything is related to everything else, but near things are more related than distant things*). Akibatnya, akurasi tampak tinggi palsu (*over-optimistic bias*).
   - *Solusi Kita:* Menerapkan **Spatial Block Cross-Validation (5-Fold Grid)** untuk menguji performa model machine learning pada blok wilayah yang benar-benar belum pernah dilihat.

---

## 2. Dari *KNOW* Menjadi *IMPROVE*: Bagaimana ML Memberi Solusi Nyata?

Machine Learning dalam riset ini tidak hanya diletakkan sebagai pelengkap (*gimmick*), melainkan sebagai instrumen solusi (*IMPROVE*):

```
[ RETROSPEKTIF (DIP) ]                  [ PREDIKTIF & SOLUTIF (ML) ]
Mengetahui apa yang terjadi (2013-2026)  ---> Mensimulasikan skenario mitigasi rekayasa tapak
- LST Anomali naik +1.72 °C             - Berapa derajat LST turun jika Albedo atap dinaikkan (Cool Roof)?
- NDBI naik, NDVI turun                 - Berapa luas sabuk hijau minimum agar spillover panas < 0.2 °C?
- Gradien meluruh hingga 1 km            - Seberapa baik model mentransfer pengetahuan ke data center lain?
```

### Eksperimen Machine Learning yang Dilakukan:
1. **Eksperimen 1: Ablasi Fitur Spektral-Termal pada Klasifikasi Tutupan Lahan (Minggu 1 - SELESAI ✅)**
   - Menguji seberapa besar kontribusi band termal (LST) dan SWIR (B6, B7) dalam membedakan material kedap air atap data center dari tanah terbuka semi-arid.
   - *Hasil:* LST dan MNDWI menyumbang >33% kepentingan Gini (*Gini Importance*), membuktikan bahwa fitur termal memisahkan atap gedung dengan presisi 100%.

2. **Eksperimen 2: Regresi Spasial LST & Simulator Mitigasi Atap Hijau/Cool Roof (Minggu 2)**
   - Formulasi: $\widehat{LST}_{anom} = f(NDVI, NDBI, \alpha, \text{Elevasi}, \text{Jarak}_{DC})$
   - Model: Random Forest Regressor, Gradient Boosting (LightGBM/XGBoost), dan Ridge Regression.
   - *Eksperimen Parameter & Validasi:* Membandingkan skor $R^2$ dan RMSE antara **Random CV** vs **5-Fold Spatial Block CV**.
   - *XAI (Explainable AI):* Menggunakan nilai **SHAP (SHapley Additive exPlanations)** untuk membuktikan: Berapa persen pemanasan disebabkan oleh kehilangan vegetasi ($NDVI$) vs emisivitas/kekedapan atap ($NDBI, \alpha$) vs jarak langsung ke server hall.

3. **Eksperimen 3: Transfer Lintas Tapak (*Cross-Site Domain Transfer*) (Minggu 3)**
   - Latih model ML pada dataset AWS PDX Boardman (Site 1), uji inferensi langsung (*zero-shot*) pada dataset H5 Quincy II (Site 2), lalu evaluasi penurunan kinerja (*generalization drop*).

4. **Eksperimen 4: Deteksi Anomali Spasial Tanpa Supervisi (*Hotspot Outliers*) (Minggu 3)**
   - Menggunakan **Isolation Forest** dan **DBSCAN** pada anomali residual regresi spasial untuk menemukan piksel yang mengalami pemanasan abnormal di luar prediksi biofisik tutupan lahan.

---

## 3. Jadwal Kerja 4 Minggu Menuju Deadline Proyek

| Minggu | Fokus & Tahapan | Luaran Metodologis & Eksperimental | Status |
|---|---|---|---|
| **Minggu 1** | **Data Fetcher (`ee` & `geemap`) & Klasifikasi Tutupan Lahan** | Porting `01_full_analysis_aws_pdx.js` ke Python [`dip_pipeline/gee_fetcher.py`](file:///home/arney1/dev/courses/dip/projects/tubes/dip_pipeline/gee_fetcher.py); penarikan fitur 30m; pelatihan **Random Forest & SVM** (4 kelas); evaluasi matriks konfusi, Kappa, dan *Gini Feature Importance*. | **SELESAI** ✅ |
| **Minggu 2** | **Regresi Spasial LST, Spatial Block CV, & Explainable AI (SHAP)** | Pemodelan regresi spasial non-linear ($LST_{anom}$); perbandingan **Random CV vs 5-Fold Spatial Block CV**; analisis atribusi fitur SHAP; simulator interaktif mitigasi *cool roof*. | **TERJADWAL** ⏳ |
| **Minggu 3** | **Cross-Site Domain Adaptation, DBSCAN Hotspot, & Uji Plasebo** | Evaluasi transfer model Site 1 (Boardman) $\rightarrow$ Site 2 (Quincy); deteksi anomali tanpa supervisi (**DBSCAN & Isolation Forest**); klasterisasi K-Means; uji Difference-in-Differences (DiD) & plasebo. | **TERJADWAL** ⏳ |
| **Minggu 4** | **Dashboard Web Interaktif & Finalisasi Paper Ilmiah** | Integrasi peta interaktif Geemap (*split map slider*) ke Streamlit; penyusunan manuskrip paper lengkap (format IEEE/ISPRS) di folder [`paper/`](file:///home/arney1/dev/courses/dip/projects/tubes/paper/). | **TERJADWAL** ⏳ |

---

## 4. Analisis Kelayakan Publikasi SINTA 2 / Jurnal Bereputasi

### Apakah Topik Ini Layak Masuk SINTA 2?
**YA, SANGAT LAYAK.** Jurnal bereputasi SINTA 2 (seperti *Jurnal Ilmu Komputer dan Informasi (JIKI)* UI, *Jurnal RESTI*, *Jurnal Penginderaan Jauh LAPAN/BRIN*, atau *IJACSA*) memiliki kriteria ketat yang dapat kita penuhi melalui checklist berikut:

| Kriteria Reviewer Jurnal SINTA 2 / IEEE | Keadaan Riset Biasa (Ditolak / SINTA 4-5) | Keunggulan Riset Kita (Target SINTA 2) |
|---|---|---|
| **Novelty (Kebaruan)** | Hanya deskripsi LST di 1 kota tanpa pembanding | **Audit kritis multi-site terhadap paper global kontroversial (Marinoni 2026), membandingkan 2 data center (Oregon & Washington).** |
| **Rigor Metodologi ML** | Random Train/Test Split biasa (bocor autokorelasi spasial) | **Penerapan Spatial Block Cross-Validation (5-Fold Grid) + Cross-Site Transferability.** |
| **Attribution & Validitas** | Mengklaim pemanasan adalah efek IT tanpa bukti kontrol | **Kuasi-eksperimental Difference-in-Differences (DiD) terhadap kontrol industri non-DC + Audit Emisivitas ASTER GED.** |
| **Explainability (XAI)** | Model black-box tanpa penjelasan kontribusi fitur | **Dekomposisi atribusi fitur menggunakan SHAP Values (Memisahkan efek Albedo vs Vegetasi vs Jarak Server).** |
| **Nilai Solutif (Impact)** | Hanya tahu masa lalu (*KNOW*) | **Simulator prediksi mitigasi rekayasa tapak (*IMPROVE*) untuk perencanaan data center ramah lingkungan.** |

---

## 5. Struktur Naskah Paper Riset Ilmiah (IEEE / ISPRS)

- **Judul Kerja:** *Comparative Multitemporal Analysis of Land Surface Temperature and Land-Cover Dynamics Around Hyperscale AI Data Centers: A Landsat 8/9 and Machine Learning Study in the Columbia Basin*
- **Penulis & Afiliasi:** Laboratorium Pengolahan Citra Digital & Sains Komputasi
- **I. Introduction:**
  - Ledakan komputasi kecerdasan buatan (*AI hyperscalers*) dan tantangan disipasi panas fasilitas pendingin.
  - Tinjauan kritis paper Marinoni dkk. (2026) mengenai resolusi MODIS 500m dan ketiadaan kelompok kontrol.
- **II. Study Areas & Multi-Site Dataset:**
  - Deskripsi komparatif Site 1 (AWS PDX Boardman, 38 ha) dan Site 2 (H5 Quincy II, 2.9 ha).
  - Katalog citra Landsat 8/9 Level-2 Collection 2 musim panas (Juni–September) 2013–2026.
- **III. Methodology (DIP & Machine Learning):**
  - Alur pra-pemrosesan (masking bitwise QA awan, ST_QA uncertainty < 3.0K, ST_CDIST > 0.2km).
  - Ekstraksi indeks biofisik (NDVI, NDBI, MNDWI, Albedo Liang 2001).
  - Desain cincin penyangga spasial (0–500m, 500–1000m, 1–2km) dan area referensi regional.
  - Evaluasi kuasi-eksperimental Difference-in-Differences (DiD).
  - Pemodelan Machine Learning: Klasifikasi tutupan lahan terbimbing (RF & SVM) dan regresi spasial dengan *Spatial Block Cross-Validation*.
  - Atribusi Explainable AI (SHAP).
- **IV. Results & Comparative Discussion:**
  - Perbandingan lintasan ekspansi fisik bangunan (Boardman +13.12 ha vs Quincy klaster padat).
  - Anomali termal lokal (+1.72 °C tapak kampus, +2.31 °C atap gedung, DiD net effect +1.42 °C).
  - Peluruhan gradien termal yang tajam dalam radius < 1 km (membantah klaim dampak 10 km).
  - Hasil evaluasi model ML dan perbandingan akurasi *Random CV* vs *Spatial Block CV*.
- **V. Threats to Validity & Limitations:**
  - Perbedaan LST radiatif siang hari vs suhu udara ambient.
  - Keterbatasan resolusi temporal revisi Landsat 16-hari.
- **VI. Conclusion & Environmental Recommendations:**
  - Kesimpulan ringkas menjawab RQ1–RQ7 dan rekomendasi penerapan *cool roof* serta *green buffer* untuk kampus data center masa depan.
