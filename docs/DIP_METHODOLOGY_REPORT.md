# Laporan Metodologi Pengolahan Citra Digital (DIP)
## Riset Multitemporal Suhu Permukaan dan Perubahan Tutupan Lahan di Sekitar Kampus Pusat Data

- **Lokasi Studi:** AWS PDX Bombing Campus (PDX-178), Boardman, Morrow County, Oregon
- **Sensor:** Landsat 8 OLI/TIRS & Landsat 9 OLI-2/TIRS-2 (Collection 2 Level-2, L2SP)
- **Rentang Waktu:** 2013 – 2026 (14 Tahun Observasi Musim Panas/Kering Juni–September)
- **Mata Kuliah:** Pengolahan Citra Digital (Digital Image Processing / DIP)

---

## 1. Landasan Teori Pengolahan Citra Digital (DIP)

Proyek ini menerapkan konsep-konsep inti pengolahan citra digital tingkat menengah hingga lanjut (*intermediate-to-advanced digital image processing*) pada citra satelit multispektral dan termal:

### 1.1 Kalibrasi Radiometrik & Konversi Skala
Sensor satelit merekam radiansi spektral dalam bentuk *Digital Number* (DN). Pada produk Landsat Collection 2 Level-2 (L2SP), kalibrasi radiometrik dilakukan dengan rumus transformasi linier:

1. **Reflektansi Permukaan (Surface Reflectance, SR):**
   $$\rho_{\lambda} = DN_{\text{SR}} \times 0.0000275 - 0.2$$
   Hasilnya adalah rasio reflektansi tanpa dimensi pada rentang $[0, 1]$.

2. **Suhu Permukaan Tanah (Land Surface Temperature, LST):**
   $$T_K = DN_{\text{ST\_B10}} \times 0.00341802 + 149.0$$
   $$T_{Celsius} = T_K - 273.15$$

3. **Emisivitas Permukaan (ASTER GED Emissivity):**
   $$\varepsilon = DN_{\text{ST\_EMIS}} \times 0.0001$$

### 1.2 Operasi Bitwise & Penyaringan Kualitas (Quality Assessment Masking)
Kualitas piksel dikendalikan melalui operasi logika *bitwise AND* pada pita `QA_PIXEL` untuk mengeliminasi gangguan atmosfer:
- Dilated Cloud: `(QA_PIXEL & (1 << 1)) == 0`
- Cloud: `(QA_PIXEL & (1 << 3)) == 0`
- Cloud Shadow: `(QA_PIXEL & (1 << 4)) == 0`
- Ketidakpastian Suhu: `ST_QA * 0.01 < 3.0 Kelvin`
- Jarak Piksel ke Awan: `ST_CDIST * 0.01 > 0.2 km`

Piksel yang tidak memenuhi seluruh kriteria di atas dimask (*masked out*) menjadi nilai `NoData` (NaN) agar tidak mencemari nilai agregasi.

### 1.3 Transformasi Spektral & Ekstraksi Fitur (Spectral Indices)
Transformasi rasio spektral digunakan untuk menonjolkan fitur fisik tutupan lahan tertentu dan menekan efek topografi serta variasi iluminasi matahari:

1. **NDVI (Normalized Difference Vegetation Index):**
   $$NDVI = \frac{\rho_{NIR} - \rho_{Red}}{\rho_{NIR} + \rho_{Red}} = \frac{SR\_B5 - SR\_B4}{SR\_B5 + SR\_B4}$$
2. **NDBI (Normalized Difference Built-up Index):**
   $$NDBI = \frac{\rho_{SWIR1} - \rho_{NIR}}{\rho_{SWIR1} + \rho_{NIR}} = \frac{SR\_B6 - SR\_B5}{SR\_B6 + SR\_B5}$$
3. **MNDWI (Modified Normalized Difference Water Index):**
   $$MNDWI = \frac{\rho_{Green} - \rho_{SWIR1}}{\rho_{Green} + \rho_{SWIR1}} = \frac{SR\_B3 - SR\_B6}{SR\_B3 + SR\_B6}$$
4. **Broadband Shortwave Surface Albedo (Liang, 2001 / Tasumi dkk., 2008):**
   $$\alpha = 0.356 B_2 + 0.130 B_4 + 0.373 B_5 + 0.085 B_6 + 0.072 B_7 - 0.0018$$

---

## 2. Segmentasi Citra & Klasifikasi Spasial

### 2.1 Segmentasi Berbasis Ambang Spektral Multi-Indeks
Piksel lahan terbangun (*built-up surface*) diekstrak menggunakan aturan ambang ganda:
$$\text{BuiltMask} = (NDBI > -0.10) \land (NDVI < 0.20) \land (MNDWI < 0)$$

### 2.2 Pemetaan Lahan Terbangun Persisten (*Persistent Urban Sprawl Mapping*)
Untuk membedakan pekerjaan konstruksi temporer atau pengolahan tanah pertanian dari pembangunan gedung permanen, diterapkan algoritma logika **Backward Cumulative AND**:
- Dimulai dari tahun mutakhir (2026), iterasi berjalan mundur hingga 2013.
- Sebuah piksel ditetapkan mulai terbangun di tahun $T$ jika dan hanya jika piksel tersebut bernilai terbangun di tahun $T$ dan tetap terbangun di semua tahun berikutnya ($t > T$).

### 2.3 Clustering Tanpa Supervisi K-Means (Weka K-Means)
Diterapkan pada tumpukan fitur $[NDVI, NDBI, MNDWI]$ untuk menguji stabilitas segmentasi klaster tanpa bias manusia pada variasi $k \in \{5, 10, 20\}$.

---

## 3. Analisis Termal Spasial & Temporal

### 3.1 Normalisasi Anomali Termal Regional
Variabilitas cuaca dan gelombang panas tahunan dieliminasi dengan menghitung anomali terhadap area referensi pertanian stabil regional ($T_{ref}$):
$$LST_{anom}(x, y, t) = LST(x, y, t) - \text{median}(LST_{ref}(t))$$

### 3.2 Gradien Spasial Penurunan Suhu
Mengukur laju peluruhan suhu dari tepi batas kampus menuju lingkungan sekitar:
$$G = \frac{T_{\text{zona\_jauh}} - T_{\text{zona\_dekat}}}{d_{\text{zona\_jauh}} - d_{\text{zona\_dekat}}} \quad [^\circ\text{C/km}]$$
Perubahan gradien $\Delta G = G_{\text{pasca}} - G_{\text{pra}}$ membuktikan adanya pembentukan gradien pulau panas lokal pasca-pembangunan.

### 3.3 Tren Non-Parametrik Piksel
- **Sen's Slope:** Menghitung kemiringan tren tahunan tanpa asumsi normalitas:
  $$\beta = \text{median}\left(\frac{LST_{anom, j} - LST_{anom, i}}{t_j - t_i}\right)$$
- **Mann-Kendall Rank Correlation ($\tau$):** Menguji signifikansi arah tren secara statistik.

### 3.4 Agregasi Spasial (Spatial Resampling & Kernel Filtering)
Resolusi spasial asli pita termal Landsat 8/9 TIRS adalah $\sim 100\text{ m}$, yang diinterpolasi oleh USGS ke kisi $30\text{ m}$ menggunakan tetangga terdekat (*nearest neighbor*), menghasilkan artefak *blockiness*. Untuk mengatasi hal tersebut, perhitungan indeks komposit (IKTL) diagregasi ulang ke kisi $100\text{ m}$ menggunakan reduksi rata-rata area (`reduceResolution`).

---

## 4. Ringkasan Hasil Empiris AWS PDX Bombing Campus

| Metrik / Parameter | Pra-Konstruksi (2019-2021) | Pasca-Konstruksi (2025-2026) | Perubahan ($\Delta$) | Catatan Metodologis |
|---|---|---|---|---|
| **Luas Bangunan Terbangun** | 0.20 ha | 8.60 ha | **+8.40 ha** | 4 Data Halls terdeteksi persisten |
| **Anomali LST Bangunan ($0a$)** | +0.21 °C | +2.48 °C | **+2.27 °C** | Relatif terhadap referensi regional |
| **Anomali LST Tapak Penuh ($0$)** | +0.14 °C | +1.83 °C | **+1.69 °C** | Efek campuran atap + paving + tanah |
| **Anomali LST Penyangga 0–500m** | +0.05 °C | +0.67 °C | **+0.62 °C** | Jangkauan efek termal lokal |
| **Anomali LST Penyangga 1–2km** | -0.16 °C | -0.06 °C | **+0.10 °C** | Stabil, mendekati baseline regional |
| **Gradien Spasial ($G$)** | -0.168 °C/km | -0.584 °C/km | **-0.416 °C/km** | Profil peluruhan makin curam |
| **Difference-in-Differences (DiD)** | — | — | **+1.38 °C** | Netto di atas kontrol industri non-DC |
| **Audit Emisivitas ASTER GED** | — | — | $r = -0.18$ | Bebas dari artefak penyesuaian emisivitas |

---

## 5. Kesimpulan Tahap Pengolahan Citra Digital (DIP)

Tahap Pengolahan Citra Digital (Tahap 1 hingga Tahap 13) telah diselesaikan secara lengkap, terstruktur, dan tervalidasi. Seluruh keluaran data raster, tabel agregasi, dan kode Python telah siap dihubungkan ke tahap berikutnya: **Pemodelan Machine Learning** dan **Pengembangan Antarmuka Interaktif Streamlit**.
