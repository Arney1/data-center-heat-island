# Progres dan Rancangan Proyek: Suhu Permukaan dan Tutupan Lahan di Sekitar Pusat Data (v2, hasil refactor)

Tanggal pembaruan: 23 Oktober 2026
Status: **rencana untuk diaudit**. Belum ada citra yang diolah, skrip yang dijalankan, atau hasil yang dilaporkan.

## 0. Cara membaca dokumen ini

| Penanda | Arti |
|---|---|
| **[TERVERIFIKASI]** | Dicek langsung ke halaman sumber pada 23 Okt 2026 (katalog GEE, paper, halaman USGS) |
| **[DARI MODUL]** | Tercantum di Modul Pra-Tubes, belum dicek ulang ke sumber lain |
| **[VERIFIKASI]** | Dari ingatan atau sumber sekunder; wajib dicek sebelum dipakai |
| **[ASUMSI KERJA]** | Angka atau ambang awal; dikalibrasi di tahap percontohan |
| **[BELUM DIKERJAKAN]** | Langkah yang direncanakan |
| **Konfirmatori / Eksploratif** | Analisis yang ditetapkan sebelum melihat data / analisis untuk menghasilkan hipotesis (tidak boleh dilaporkan sebagai bukti) |

### Ringkasan perubahan dari versi 22-23 Oktober

| Temuan audit | Perbaikan di dokumen ini |
|---|---|
| Tren piksel melintasi lonjakan konstruksi; rawan tahun panas di ujung seri | Tren dihitung pada **anomali terhadap area referensi** (Sen's slope + Mann-Kendall); tambah **seri anomali per zona** dengan pemisahan sebelum/sesudah; peta piksel hanya visualisasi (Tahap 9) |
| Tren dan regresi berjalan di piksel yang rawan artefak emisivitas | **Gerbang audit emisivitas** sebelum tren dan regresi (Tahap 8) |
| Regresi: kolinearitas, tanpa albedo/elevasi, tanpa ketidakpastian valid | Tambah elevasi dan proksi albedo, keluarkan bagian dalam kampus, cek VIF, bandingkan koefisien jarak **sebelum vs sesudah**, evaluasi dengan blok spasial (Tahap 11) |
| Tidak ada pembanding; "area referensi" tidak terdefinisi | Definisi operasional area referensi (Bagian 5.3) dan **pembanding berpasangan** sebagai Tingkat C (Tahap 13) |
| Gradien tercampur komposisi tutupan lahan, tanpa gradien dasar | Gradien per kelas tutupan lahan dan **perubahan gradien** sesudah-sebelum (Tahap 10) |
| Tanggal periode bergantung dokumen | **Penanggalan konstruksi dari citra** lewat peta "tahun mulai terbangun" (Tahap 6) |
| Tanggal akuisisi dan musim berbeda tiap tahun; hanya QA_PIXEL | Jendela musim sempit, laporan tanggal, masking `ST_QA` dan `ST_CDIST` (Tahap 2-3) |
| Validasi tutupan lahan kurang rinci | Skema kelas, ukuran sampel, strata, metrik (Tahap 5, Bagian 9) |
| Tidak ada tabel asumsi; sensitivitas tanpa kriteria | Tabel asumsi 14 butir (Bagian 10) dan matriks sensitivitas dengan kriteria (Bagian 9) |
| Skala "kerumitan" belum setara Pra-Tubes | Pemetaan eksplisit ke Task I-V dan Tugas Mandiri (Bagian 14) |

---

## 1. Ringkasan progres

| Komponen | Progres saat ini | Status |
|---|---|---|
| Paper acuan | Marinoni dkk. (2026) dipilih, dibaca penuh (v3), dan diaudit | Selesai tahap kajian awal |
| Literatur pendukung | Studi analog (LST sebelum-sesudah di sekitar fasilitas besar, LST dan indeks permukaan di GEE, tren Sen/Mann-Kendall, validasi spasial) dikumpulkan; semuanya diberi status akses | Selesai pencarian awal; tinjauan sistematis belum |
| Ketersediaan citra di GEE | Katalog Landsat 8 dan 9 L2 diperiksa langsung (Bagian 6) | Dataset terverifikasi; ketersediaan citra bersih per lokasi belum diperiksa |
| Judul | Judul kerja dengan subjudul metode (Bagian 3) | Usulan |
| Lokasi pusat data | Kandidat wilayah; fasilitas dan koordinat belum diverifikasi | Belum final |
| Metode | 13 tahap, tiga tingkat (Bagian 7) | Rancangan; belum dijalankan |
| Implementasi dan hasil | Tidak ada | Belum dilakukan |

---

## 2. Paper acuan dan literatur

### 2.1 Paper acuan

Marinoni, A. dkk. (2026). *The Data Heat Island Effect: Quantifying the Impact of AI Data Centers in a Warming World.* arXiv:2603.20897v3 (21 April 2026). https://arxiv.org/abs/2603.20897v3 (akses terbuka). Diberitakan belum ditelaah sejawat (Dezeen).

Penulis melaporkan kenaikan LST rata-rata sekitar 2 °C setelah awal operasi (rata-rata 2,07 °C; rentang 0,3 sampai 9,1 °C), dengan jangkauan hingga 10 km, memakai data MODIS rekonstruksi 500 m 2004-2024, 6.733 titik data setelah penyaringan, dan WorldPop. Angka itu adalah temuan penulis, bukan target proyek ini.

Pertanyaan untuk penulis dari hasil audit (bukan kesalahan yang terbukti):
1. Tidak ada kelompok pembanding; hanya perbandingan sebelum-sesudah per lokasi.
2. Asal tanggal "mulai operasi" dan kriteria "AI hyperscaler" tidak dijelaskan; sumber lokasi direktori umum.
3. Pers. 1 memakai garis dasar bergulir; rentang persentil ke-95 bukan selang kepercayaan rerata.
4. Set data suhu rekonstruksi 500 m dirujuk ke Metz dkk. (2014); set data persisnya perlu dipastikan.
5. Estimasi populasi menjumlahkan penduduk di lingkaran 10 km; kemungkinan tumpang tindih lingkaran perlu ditanyakan.

### 2.2 Literatur pendukung (pencarian 23 Okt 2026)

Dalam pencarian singkat **tidak ditemukan makalah lain yang mengukur LST di sekitar pusat data** selain paper acuan. Studi berikut adalah **analog metodologis**: fasilitas atau infrastruktur besar yang diamati sebelum dan sesudah pembangunan, atau hubungan LST dengan indeks permukaan di GEE.

| Kelompok | Makalah | Akses | Yang dipakai proyek |
|---|---|---|---|
| Sebelum-sesudah dan cincin jarak di sekitar fasilitas besar | *Ground-mounted photovoltaic solar parks promote land surface cool islands in arid ecosystems.* Renewable and Sustainable Energy Transition (2021). DOI 10.1016/j.rset.2021.100008. Daftar penulis: [lengkapi] | Terbuka (disebut artikel akses terbuka) | Citra Landsat sebelum dan sesudah pembangunan, efek berkurang dengan jarak (sekitar 700 m), perhitungan LST dengan GEE |
| | Vavassori, A., Puche, M., Brovelli, M. A. (2023). *Measuring the influence of a motorway construction on land surface temperature using Landsat thermal data: a case study in the Metropolitan City of Milan.* ISPRS Archives XLVIII-1/W2-2023. DOI 10.5194/isprs-archives-XLVIII-1-W2-2023-1589-2023 | Terbuka (Copernicus) | Sebelum-sesudah per musim, penyangga jarak dari pembangunan, Landsat 5 dan 8 |
| | Cheng, H. dkk. (2023). *Research on thermal environment analysis of photovoltaic power plants based on remote sensing images.* ISPRS Archives XLVIII-1/W2-2023. DOI 10.5194/isprs-archives-XLVIII-1-W2-2023-1343-2023 | Terbuka (Copernicus) | Perubahan tutupan lahan dan LST sebelum-sesudah (2013-2020), korelasi proporsi fasilitas dengan LST |
| | *Impacts of petrochemical complex of Rio de Janeiro in eastern metropolitan region of Rio de Janeiro using remote sensing data.* ICC 2015 (icaci.org) | Terbuka (prosiding daring) | Preseden **kehati-hatian**: NDVI turun dan indeks lahan terbangun naik di area konstruksi, tetapi kenaikan LST tidak terkonfirmasi uji statistik karena variabilitas cuaca |
| LST, tutupan lahan, dan indeks (NDVI/NDBI) di GEE | *Investigating the relationship between land use/land cover change and land surface temperature using Google Earth Engine; case study: Melbourne, Australia.* Sustainability 14, 14868 (2022) | Terbuka | Regresi LST dengan NDBI, NDVI, dan elevasi di GEE (dasar penambahan elevasi) |
| | *Assessing the impact of land use and land cover changes on surface temperature dynamics using Google Earth Engine: Tlemcen Municipality, NW Algeria (1989-2019).* ISPRS Int. J. Geo-Inf. (2024) | Terbuka (terdaftar DOAJ) | Random Forest + indeks + LST pada Landsat di GEE |
| | *Landsat 9 satellite image data in surface temperature estimation, NDVI and NDBI using Google Earth Engine* (DKI Jakarta; Geoid, ITS) | [cek akses]; judul lengkap [lengkapi] | Konsistensi LST/NDVI/NDBI dari Landsat 8 dan 9 di GEE (konteks Indonesia) |
| Tren per piksel | *Non-Parametric Trend Analysis* (tutorial komunitas Earth Engine) | Terbuka (dokumentasi) | Mann-Kendall dan Sen's slope di GEE |
| | *Exploring the Dynamics of Land Surface Temperature in Jordan's Local Climate Zones: Landsat Entire Archive and Google Earth Engine.* Atmosphere 15(3), 318 (2024) | Terbuka (MDPI) | Seri LST bulanan dari Landsat di GEE dengan Mann-Kendall dan Sen's slope |
| Retrieval dan batas produk suhu | Ermida, S. L. dkk. (2020). *Google Earth Engine Open-Source Code for Land Surface Temperature Estimation from the Landsat Series.* Remote Sensing 12(9), 1471. DOI 10.3390/rs12091471 | Terbuka | Alternatif retrieval (tidak sepenuhnya independen; lihat Tahap 8) |
| | USGS, *Landsat Collection 2 Surface Temperature* dan *Known Issues* | Terbuka | Anomali emisivitas vegetasi dan artefak blokiness (Bagian 8, Tahap 8) |
| | Cook dkk. (2014), dirujuk katalog GEE untuk kesalahan suhu dekat awan. DOI 10.3390/rs61111244. Judul [lengkapi] | [cek akses] | Dasar masking `ST_CDIST` |
| Validasi spasial | *Spatial block cross-validation: lessons from a marine remote sensing case study.* Frontiers in Remote Sensing (2025). DOI 10.3389/frsen.2025.1531097. Judul [konfirmasi] | Terbuka | Validasi silang blok untuk regresi (Tahap 11) |
| | Roberts, D. R. dkk. (2017). *Cross-validation strategies for data with temporal, spatial, hierarchical, or phylogenetic structure.* Ecography. DOI 10.1111/ecog.02881 | [cek akses] | Alasan memakai blok spasial, bukan pembagian acak |

**Catatan jujur tentang literatur:** pencarian singkat, bukan tinjauan sistematis. Telusur Google Scholar, Scopus, dan arXiv (kata kunci: "data center" + "land surface temperature", "hyperscale" + "Landsat", "heat island" + "data centre") perlu dilakukan sebelum menyatakan kebaruan. Tidak ditemukan studi pendeteksi pusat data pada citra satelit (akses terbuka).

---

## 3. Judul kerja

**Utama (ID):** *Analisis Multitemporal Suhu Permukaan dan Perubahan Tutupan Lahan di Sekitar Pusat Data Menggunakan Landsat dan Google Earth Engine*

**Subjudul (ID):** *Gradien Spasial, Tren Berbasis Anomali, dan Regresi Kovariat*

**EN:** *Multitemporal Analysis of Land Surface Temperature and Land-Cover Change Around Data Centers Using Landsat and Google Earth Engine: Spatial Gradients, Anomaly-Based Trends, and Covariate Regression*

Judul utama berbasis masalah, subjudul menjelaskan metode. Nama wilayah dan rentang tahun ditambahkan setelah gerbang percontohan. Judul tidak memuat "AI" (citra tidak membedakan pusat data AI dari konvensional) dan tidak menjanjikan pemisahan panas operasional dari perubahan lahan.

---

## 4. Rumusan masalah, pertanyaan, dan hipotesis

**Rumusan masalah:** bagaimana suhu permukaan dan tutupan lahan di sekitar kampus pusat data berubah antara periode sebelum, transisi, dan sesudah pengembangan; bagaimana pola itu bervariasi menurut jarak; dan seberapa konsisten hasilnya terhadap pilihan metode dan ambang?

| No | Pertanyaan | Sifat |
|---|---|---|
| RQ1 | Bagaimana LST dan tutupan lahan berubah antarperiode di tapak kampus dan zona sekitarnya? | Konfirmatori (deskriptif) |
| RQ2 | Apakah perubahan LST berasosiasi dengan penurunan NDVI dan kenaikan NDBI? | Konfirmatori (asosiasi) |
| RQ3 | Bagaimana pola suhu menurut jarak, dan **apakah gradiennya berubah** setelah pengembangan dibanding gradien dasar sebelum pengembangan? | Konfirmatori |
| RQ4 | Di bagian mana anomali LST (relatif terhadap area referensi) cenderung naik atau turun sepanjang 2014-2025? | Eksploratif |
| RQ5 | Apakah koefisien jarak dalam regresi (dengan NDVI, NDBI, elevasi, albedo) berbeda antara periode sebelum dan sesudah? | Eksploratif |
| RQ6 | Seberapa stabil hasil terhadap ambang, jumlah kluster, batas zona, jendela musim, dan estimator? | Konfirmatori (ketahanan) |
| RQ7 (Tingkat C) | Apakah perubahan LST kampus berbeda dari pembanding berpasangan pada periode yang sama? | Konfirmatori bila >= 6 kampus; deskriptif jika lebih sedikit |

**Hipotesis kerja (asosiasi, bukan kausal):** H1: gradien LST sesudah pengembangan lebih curam daripada sebelum. H2: besar kenaikan LST berasosiasi dengan besar penurunan NDVI dan kenaikan NDBI. H3 (Tingkat C): selisih perubahan LST kampus-pembanding berbeda dari nol. Hasil nol tidak membuktikan tidak adanya panas operasional; laporkan ukuran efek dan efek minimum yang dapat dideteksi.

---

## 5. Lokasi, pembanding, dan area referensi

### 5.1 Kandidat wilayah (belum diverifikasi)

| Kandidat | Yang masih diperlukan | Status |
|---|---|---|
| Prineville, Oregon (AS) | Nama fasilitas, batas kampus, kronologi, citra sebelum pembangunan | Belum diverifikasi |
| The Dalles, Oregon (AS) | Identitas kampus, tahap ekspansi, koordinat | Belum diverifikasi |
| Boydton, Virginia (AS) | Batas fasilitas, kronologi, ketercukupan citra | Belum diverifikasi |
| Quincy, Washington (AS) | Pemilihan fasilitas atau klaster, pengaruh fasilitas berdekatan | Belum diverifikasi |
| Cikarang/Jabodetabek (Indonesia) | Nama fasilitas, sumber resmi, kronologi, konteks kawasan industri | Belum diverifikasi |

Tidak ada nama fasilitas, koordinat, atau tanggal yang dinyatakan benar di sini. Kecocokan iklim bagi ketersediaan citra bebas awan adalah **hipotesis** yang diuji lewat skrip hitung citra bersih (Lampiran A, gerbang G3).

### 5.2 Kriteria kampus

1. Identitas dan lokasi dapat diverifikasi dari sumber operator atau dokumen resmi.
2. Luas tapak >= 15 ha **[ASUMSI KERJA]**. Piksel termal asli ~100 m (~1 ha), jadi 5 ha hanya sekitar lima piksel independen.
3. Kronologi pembangunan dan ekspansi dapat ditelusuri; tanggal peresmian bukan tanggal perubahan fisik lahan.
4. Dibangun atau diekspansi setelah 2013 dengan **pra-periode >= 2 tahun** (Landsat 8 mulai 18 Maret 2013 **[TERVERIFIKASI]**), supaya uji plasebo waktu dimungkinkan.
5. Pembangunan sekitar dapat diidentifikasi (dibahas sebagai faktor lain).
6. Tidak tumpang tindih zona dengan kampus lain (atau diperlakukan sebagai satu klaster).
7. Piksel suhu tersedia di lokasi (produk ST kosong di area tanpa data emisivitas ASTER GED; **[TERVERIFIKASI]** di katalog).

### 5.3 Area referensi (definisi operasional)

Area referensi dipakai untuk membuang efek cuaca dan tren regional bersama (anomali), bukan sebagai kelompok kontrol kausal.

- Terletak 5-30 km dari kampus mana pun, pada adegan Landsat yang sama dan elevasi serupa (selisih elevasi rata-rata <= 100 m **[ASUMSI KERJA]**).
- Tutupan lahan dominan sama dengan tutupan lahan kampus pada pra-periode (mis. lahan pertanian atau semak).
- **Stabil:** perubahan NDVI dan NDBI sepanjang periode di bawah ambang yang ditetapkan dari distribusi data **[ASUMSI KERJA]**; tidak mengandung air, lereng curam, atau pembangunan baru.
- Luas >= 25 km² **[ASUMSI KERJA]** agar median anomali stabil.

### 5.4 Pembanding berpasangan (Tingkat C)

Pengembangan baru non-pusat-data (kawasan logistik atau pabrik), dicocokkan **hanya pada fitur sebelum kejadian**: tutupan lahan sebelumnya, luas, waktu pembangunan (+/- 1 tahun), LST dan NDVI pra-periode, tren pembangunan sekitar; berjarak >= 5 km dari pusat data mana pun, dalam satu wilayah iklim. NDVI, NDBI, atau LST **pasca-kejadian tidak dipakai sebagai kovariat** karena merupakan akibat konstruksi.

---

## 6. Data dan ketersediaan di GEE

Diperiksa langsung pada halaman katalog Earth Engine, 23 Oktober 2026.

| Data | ID di GEE | Ketersediaan (metadata katalog) | Status |
|---|---|---|---|
| Landsat 8 OLI/TIRS Level-2, Tier 1 | `LANDSAT/LC08/C02/T1_L2` | 18 Mar 2013 sampai 11 Okt 2026; ulang 16 hari | **[TERVERIFIKASI]** |
| Landsat 9 OLI-2/TIRS-2 Level-2, Tier 1 | `LANDSAT/LC09/C02/T1_L2` | 31 Okt 2021 sampai 11 Okt 2026; ulang 16 hari. Catatan: ringkasan halaman menyebut "Oktober 2021 hingga Oktober 2025", sedangkan metadata ketersediaan lebih baru; cek di Code Editor | **[TERVERIFIKASI]**, dengan catatan |
| Elevasi SRTM | `USGS/SRTMGL1_003` | Tercantum di Modul Pra-Tubes (Task IV) | **[DARI MODUL]** |
| ESA WorldCover v200 (opsional) | `ESA/WorldCover/v200` | Modul Pra-Tubes | **[DARI MODUL]** |
| Sentinel-2 SR Harmonized (opsional) | `COPERNICUS/S2_SR_HARMONIZED` | Belum diperiksa | **[VERIFIKASI]** |
| Landsat 5/7 L2 (opsional, perluasan lintas sensor) | `LANDSAT/LT05/C02/T1_L2`, `LANDSAT/LE07/C02/T1_L2` | Halaman LE07 ditemukan; LT05 belum | **[VERIFIKASI]** |

**Band dan properti yang diverifikasi di katalog Landsat 8 dan 9:**

| Band / properti | Isi |
|---|---|
| `SR_B2`..`SR_B7` | Reflektansi permukaan; skala 2,75e-05, offset -0,2; B3 = hijau, B4 = merah, B5 = NIR, B6 = SWIR1 |
| `ST_B10` | Suhu permukaan (K); skala 0,00341802, offset 149 |
| `ST_QA` | Ketidakpastian suhu (K); skala 0,01 |
| `ST_CDIST` | Jarak piksel ke awan (km); skala 0,01 |
| `ST_EMIS` | Emisivitas Band 10 dari ASTER GED; skala 0,0001 |
| `QA_PIXEL` | Bit 1 dilated cloud, bit 3 cloud, bit 4 cloud shadow, bit 5 snow, bit 6 clear |
| `PROCESSING_LEVEL` | `L2SP` bila SR dan ST ada; `L2SR` bila hanya SR (band ST ada tetapi kosong) |

**Peringatan dari katalog dan USGS yang berlaku pada proyek ini:**
- Produk suhu memiliki kesalahan yang diketahui dekat awan dan bayangan awan.
- Piksel tanpa data emisivitas ASTER GED tidak punya suhu, dan lubang itu **tetap sama sepanjang waktu**. Lokasi yang jatuh di lubang ini tidak bisa diteliti suhunya.
- Anomali penyesuaian emisivitas vegetasi dapat menghasilkan suhu keliru di piksel dengan perubahan NDVI besar antara era ASTER dan era Landsat. Konversi lahan menjadi kampus adalah kasus rawan.
- Artefak blokiness berasal dari interpolasi tetangga terdekat data 100 m ke grid 30 m.
- Citra malam tidak dapat diproses menjadi suhu permukaan; Landsat hanya siang hari.

**Yang belum terverifikasi:** jumlah citra bersih per lokasi dan musim. Itu hanya bisa dihitung di GEE (Lampiran A) dan menjadi gerbang G3.

---

## 7. Rancangan metode: 13 tahap, tiga tingkat

| Tingkat | Isi | Setara |
|---|---|---|
| **A (inti)** | Tahap 1-6 dan 8 | Task I-III dan Tugas Mandiri 1-3 |
| **B (bila percontohan lolos)** | Tahap 7, 9-12 | Task IV-V dan Tugas Mandiri 4, plus gradien, tren, regresi |
| **C (opsional, di atas Pra-Tubes)** | Tahap 13 dan perluasan | Pembanding, plasebo, Random Forest, lintas sensor |

Unit analisis adalah **kampus**. Ribuan piksel 30 m bukan ribuan sampel independen. Jika n < 6 kampus, semua kesimpulan bersifat studi kasus.

### Tahap 1. Area studi dan zona
Digitasi poligon tapak kampus dan area referensi. Zona non-tumpang tindih dari batas kampus: Tapak; Zona 1 (0-500 m); Zona 2 (500-1.000 m); Zona 3 (1-2 km). Jarak adalah pilihan awal, bukan klaim jangkauan panas.

### Tahap 2. Katalog, filter, dan masking
Gabungkan `LC08` dan `LC09`, filter lokasi, tanggal, dan `PROCESSING_LEVEL = L2SP`. Mask awan, bayangan, dan dilated cloud dari `QA_PIXEL`; mask `ST_QA` dan `ST_CDIST` dengan ambang yang dikalibrasi dari distribusi data **[ASUMSI KERJA]**. Skala reflektansi dan suhu sesuai Bagian 6.

### Tahap 3. Komposit dan observasi
Jendela musim sempit yang sama setiap tahun (mis. 4 bulan musim kering/panas wilayah) **[ASUMSI KERJA]**. Median seperti Task II (tahan terhadap sisa awan). Catat tanggal akuisisi, jumlah observasi valid, dan fraksi area valid untuk setiap komposit.

### Tahap 4. Clustering K-means (setara Task I dan Tugas Mandiri 1)
K-means tanpa data latih pada komposit di sekitar kampus; k = 5, 10, 20, beberapa seed. Bandingkan luas kelas kandidat lahan terbangun (`reduceRegion` dengan `ee.Reducer.sum()` atas `pixelArea()`) dan stabilitas nomor kluster.

### Tahap 5. Indeks dan kalibrasi ambang (setara Task II dan Tugas Mandiri 2)
Hitung NDVI, NDBI, dan MNDWI setelah scaling reflektansi. Kalibrasi ambang NDBI dari titik: minimal 5 lokasi jelas terbangun dan 5 jelas bukan (seperti tugas mandiri), lalu **sampel validasi terpisah** (>= 50 titik per kelas **[ASUMSI KERJA]**; kelas: vegetasi, tanah terbuka, lahan terbangun/atap, air) dilabeli dari citra resolusi tinggi. Bandingkan peta dengan ambang modul (-0,1) dan ambang baru; laporkan perubahan luas terbangun (ha), matriks konfusi, akurasi keseluruhan, kappa, dan akurasi per kelas (terutama tanah terbuka vs terbangun).

### Tahap 6. Multitemporal dan penanggalan konstruksi (setara Task III dan Tugas Mandiri 3)
Iterasi `map` atas tahun (2014-2025, mengikuti tahun yang tersedia): komposit, indeks, dan mask terbangun per tahun. Susun **peta "tahun mulai terbangun"** (nilai-tahun dan komposit min, seperti urban sprawl modul) di sekitar kampus, dan grafik luas terbangun per tahun. T_konstruksi per kampus: penurunan NDVI dan kenaikan NDBI berkelanjutan pada >= 2 observasi berurutan **[ASUMSI KERJA]**. T_operasi hanya dari dokumen; bila tidak ada, dilaporkan "tidak diketahui". Periode: **sebelum**, **transisi**, **sesudah** (transisi dikeluarkan dari estimasi utama).

### Tahap 7. Peta LST (Tingkat B)
Suhu dalam derajat Celsius per komposit; skala warna konsisten antarperiode. Peta perubahan LST (sesudah dikurangi sebelum) dan peta **anomali** (LST dikurangi median LST area referensi pada komposit yang sama).

### Tahap 8. Audit emisivitas (gerbang)
Sebelum Tahap 9-11: plot perubahan `ST_EMIS` terhadap perubahan NDVI; bandingkan LST pada permukaan stabil dan terkonversi; tandai atau mask piksel dengan lonjakan emisivitas tak wajar. Opsional: retrieval kedua (Ermida dkk. 2020); keduanya memakai masukan emisivitas dari ASTER GED sehingga **bukan validasi independen**. Jika sensitivitas tidak terselesaikan, dinyatakan sebagai keterbatasan atribusi.

### Tahap 9. Tren berbasis anomali (Tingkat B; eksploratif)
- **Seri anomali per zona:** rata-rata anomali LST per tahun untuk Tapak, Zona 1-3, dengan pemisahan sebelum/sesudah pada T_konstruksi. Ini keluaran tren utama.
- **Peta tren piksel (visualisasi):** Sen's slope dan Mann-Kendall (`ee.Reducer.sensSlope()` dan `ee.Reducer.kendallsCorrelation()`, **[VERIFIKASI]** nama reducer) pada **anomali**, bukan LST mentah, agar cuaca bersama hilang. Syarat awal >= 5 tahun valid per piksel termasuk awal dan akhir rentang **[ASUMSI KERJA]**. Agregasi ke grid ~100 m (mengurangi blokiness). Peta kemiringan disajikan bersama peta jumlah tahun valid dan peta signifikansi.
- Kemiringan satu garis tidak membedakan lonjakan dan perubahan bertahap; dilaporkan bersama seri zona.
- Jika hanya tiga periode layak, laporkan sebagai perubahan antarperiode, bukan tren.

### Tahap 10. Gradien spasial (Tingkat B)
- Profil LST (rata-rata, median, sebaran, fraksi valid) menurut zona dan periode.
- **Gradien per kelas tutupan lahan** (mis. hanya piksel bervegetasi atau hanya piksel tanah terbuka di tiap zona), supaya komposisi tidak menyamar sebagai jarak.
- `G = (T_zona_jauh - T_zona_dekat) / (d_zona_jauh - d_zona_dekat)` dalam °C/km; laporkan **perubahan gradien** `G_sesudah - G_sebelum`. Gradien sebelum pengembangan adalah garis dasar (sungai, lereng, lahan pertanian).
- Anomali zona terhadap area referensi: `A_zona,t = T_zona,t - T_referensi,t`.

### Tahap 11. Regresi kovariat (Tingkat B; eksploratif)
Model per kampus dan per periode, **di luar bagian dalam kampus** (menghindari titik berpengaruh ekstrem):

```text
LSTanom_i = b0 + b1*NDVI_i + b2*NDBI_i + b3*elevasi_i + b4*albedo_i + b5*jarak_i + e_i
```

- Elevasi dari SRTM; albedo adalah proksi dari reflektansi (rumus albedo dan sumbernya **[VERIFIKASI]**; Melbourne dan studi analog memasukkan elevasi).
- Unit sampel: grid 100-300 m dipilih saat percontohan; agregasi eksplisit.
- Bangun dari NDVI saja, NDBI saja, lalu model gabungan; periksa korelasi dan VIF.
- Pisahkan **blok spasial** untuk pembentukan dan evaluasi (Roberts dkk. 2017; Frontiers in Remote Sensing 2025); laporkan RMSE blok, R², jumlah sampel, peta residual.
- Selang ketidakpastian koefisien lewat bootstrap blok di luar GEE (ekspor tabel sampel ke CSV; Python, R, atau spreadsheet). Jangan melaporkan nilai-p dari galat standar biasa karena autokorelasi spasial.
- **Bandingkan b5 (jarak) sebelum vs sesudah.** Model "sebelum" adalah garis dasar gratis.
- Implementasi GEE: `ee.Reducer.linearRegression()` dengan prediktor konstanta 1, kemudian kovariat, lalu respons.
- NDVI dan NDBI sesudah pembangunan adalah akibat konstruksi; koefisien tidak dibaca sebagai efek operasional.

### Tahap 12. Indeks Koinsidensi Termal-Lahan, IKTL (setara Task IV-V dan Tugas Mandiri 4)
Indeks harkat **deskriptif**: menandai sel tempat kenaikan suhu dan konversi lahan terjadi bersamaan. Ia bukan model dampak, bukan "risiko". Sel diagregasi ~100 m.

| Komponen | Variabel | Arah skor | Ambang awal (dari distribusi area referensi/pembanding, bukan kampus sendiri) |
|---|---|---|---|
| Termal | V1: anomali perubahan LST | Naik = skor besar | Kuantil: <= P50 = 1; P50-P75 = 2; P75-P90 = 3; P90-P97,5 = 4; > P97,5 = 5 **[ASUMSI KERJA]** |
| Permukaan | V2: penurunan NDVI | Turun besar = skor besar | Kuantil serupa |
| Permukaan | V3: kenaikan NDBI | Naik besar = skor besar | Kuantil serupa |
| Konversi | V4: kelas konversi (dari Tahap 5-6) | Vegetasi ke terbangun = 5; tanah terbuka ke terbangun = 3; tidak berubah = 1 | Aturan tabel |

- Jumlah skor 4-20 diharkat kembali ke lima kelas: 4-7, 8-10, 11-13, 14-16, 17-20 **[ASUMSI KERJA]**.
- **Ablasi komponen** (seperti `.add(harkatKerentanan)` pada tugas mandiri 4): bandingkan peta dengan dan tanpa tiap komponen, hitung luas tiap kelas (1-5) dengan `ee.Reducer.histogram()` atau `reduceRegion` bertingkat, dan diskusikan mengapa komponen mengubah (atau tidak mengubah) peringkat.
- Bobot: (A) seragam; (B) V1 x 2; (C) bobot entropi dari data. Bandingkan Spearman dan persentase sel yang berpindah kelas.
- V2 dan V3 berkorelasi tinggi; periksa agar tidak menghitung ganda.
- Tidak ada validasi eksternal. Keandalan dinilai dari **stabilitas**, bukan akurasi; kelas tinggi tidak disebut "berisiko".

### Tahap 13. Pembanding berpasangan dan plasebo (Tingkat C)
Per set kampus-pembanding:

```text
D_i = (T_kampus,sesudah - T_kampus,sebelum) - (T_pembanding,sesudah - T_pembanding,sebelum)
```

dihitung per zona memakai **tanggal bersama** (tanggal yang sama-sama bersih), bila >= 2 kandidat pembanding lolos pencocokan. Periksa selisih awal; **plasebo waktu** (tanggal kejadian palsu di pra-periode); **plasebo ruang** (pengembangan non-pusat-data acak sebagai "kampus"); leave-one-campus-out. Perluasan opsional: Random Forest dan klasifikasi Sentinel-2, atau perluasan lintas sensor (Landsat 5/7) untuk kampus yang dibangun sebelum 2013 (menambah harmonisasi; ID koleksi **[VERIFIKASI]**).

---

## 8. Batas interpretasi

LST adalah suhu permukaan yang dilihat sensor termal pada siang hari, bukan suhu udara dan bukan ukuran paparan manusia. Pola dipengaruhi vegetasi, material permukaan (atap, aspal), irigasi, cuaca, musim, pembangunan sekitar, dan ketidakpastian produk satelit.

| Boleh | Tidak boleh |
|---|---|
| "LST dan tutupan lahan di sekitar kampus X berubah antarperiode dengan pola Y" | "Pusat data menaikkan suhu sebesar Z °C" |
| "Perubahan suhu berasosiasi dengan penurunan NDVI dan kenaikan NDBI" | "Panas server menyebabkan pemanasan" |
| "Gradien sesudah pengembangan lebih curam daripada sebelum" | "Gradien membuktikan jangkauan pelepasan panas" |
| "Selisih dari pembanding adalah D (selang ketidakpastian), konsisten atau tidak konsisten dengan ..." | "Selisih ini membuktikan panas operasional" |
| "Hasil nol tidak menyingkirkan panas operasional kecil" | "Tidak ada panas operasional" |
| "IKTL menandai sel tempat kenaikan suhu dan konversi lahan bersamaan" | "IKTL tinggi berarti berisiko" |
| "Bila kampus dibangun tetapi belum beroperasi dan suhu naik, ini menunjukkan operasi penuh tidak diperlukan untuk kenaikan yang teramati, dengan pemeriksaan cuaca, konstruksi, dan artefak retrieval" | "Maka perubahan lahan adalah penyebab" |

Tiga pendekatan (gradien, tren, regresi) memakai citra dasar yang sama, sehingga **bukan tiga bukti independen**. Selisih pembanding dan area referensi bukan dekomposisi teridentifikasi dari "efek beton". Sebagai preseden kehati-hatian, studi kompleks petrokimia Rio de Janeiro tidak dapat mengonfirmasi kenaikan LST secara statistik karena variabilitas cuaca, walaupun NDVI dan indeks lahan terbangun berubah nyata.

---

## 9. Validasi dan uji sensitivitas

### 9.1 Validasi

| Jenis | Cara | Keterbatasan |
|---|---|---|
| Tutupan lahan | Titik referensi terpisah dari titik kalibrasi; matriks konfusi, kappa, akurasi per kelas | **Tidak** memvalidasi akurasi suhu |
| Suhu | Audit emisivitas; versi retrieval kedua (tidak independen penuh); perbandingan stabil vs terkonversi | Tanpa pengukuran lapangan, akurasi absolut LST tidak tervalidasi |
| Regresi | Blok spasial; RMSE blok; peta residual | Bukan estimasi efek |
| Tren | Kelengkapan observasi; signifikansi; seri contoh; perbandingan seri zona | Sedikit tahun valid, daya uji rendah |
| IKTL | Stabilitas terhadap bobot, ambang, ablasi | Tidak ada acuan eksternal |
| D_i (Tingkat C) | Kondisi awal; plasebo waktu dan ruang; leave-one-out | Kontrafaktual tidak teramati |
| Paper acuan | Bandingkan bentuk hasil secara kualitatif (waktu perubahan, penurunan menurut jarak) | Data MODIS rekonstruksi paper tidak identik dengan yang ada di GEE; bukan replikasi |

### 9.2 Matriks sensitivitas

| Faktor | Variasi | Keluaran yang diuji | Kriteria "stabil" **[ASUMSI KERJA]** |
|---|---|---|---|
| Ambang NDBI/NDVI dan kuantil harkat | +/- satu langkah | Luas terbangun, kelas IKTL | Spearman >= 0,8; < 20% sel berpindah |
| Jumlah kluster | 5, 10, 20; beberapa seed | Luas kelas terbangun | Perubahan luas dilaporkan |
| Batas zona | +/- 100 m; tanpa Zona 3 | LST zona, gradien | Urutan zona tidak berbalik |
| Ukuran grid analisis | 100, 200, 300 m | Regresi, IKTL, tren | Tanda koefisien sama |
| Jumlah tahun valid minimum | 3, 5, 7 | Peta tren | Pola umum sama |
| Jendela musim | Geser +/- 1 bulan | Tren, LST zona | Tanda sama |
| Estimator tren | OLS vs Sen; LST mentah vs anomali | Kemiringan | Selisih dilaporkan |
| Himpunan kovariat | Tanpa elevasi; tanpa albedo | Koefisien jarak | Tanda b5 sama |
| Ukuran blok validasi | Dua ukuran blok | RMSE blok | RMSE berubah dilaporkan |
| Ambang kualitas suhu | Longgar vs ketat | LST zona | Tanda sama |
| Versi retrieval suhu | Standar vs alternatif | LST zona, D_i | Selisih dilaporkan (bukan "validasi") |
| Ablasi komponen IKTL | Tanpa V1, V2/V3, atau V4 | Peringkat sel, luas kelas | Perubahan peringkat dilaporkan |
| Leave-one-campus-out | Hapus satu kampus | Pola lintas kampus | Tidak bergantung satu kampus |

Setiap faktor dilaporkan, termasuk yang **tidak** stabil.

---

## 10. Tabel asumsi

| ID | Asumsi | Risiko bila salah | Uji / penanganan |
|---|---|---|---|
| A1 | Tanggal dari citra mewakili awal perubahan fisik | Periode "sebelum" tercemar konstruksi | Peta tahun mulai terbangun; kurva NDVI/NDBI |
| A2 | Jendela musim yang sama mengendalikan efek musiman | Cuaca antar-tahun tetap bervariasi | Anomali terhadap referensi; sensitivitas musim |
| A3 | Anomali terhadap area referensi membuang cuaca bersama | Referensi tidak stabil atau tidak mewakili | Definisi stabil (5.3); referensi alternatif |
| A4 | Landsat C2 ST cukup andal untuk perubahan relatif | Artefak emisivitas di lahan terkonversi | Tahap 8; retrieval kedua; batasan atribusi |
| A5 | Hari bebas awan tidak bias | Hari jernih cenderung lebih panas | Laporkan distribusi tanggal; catat sebagai keterbatasan |
| A6 | Piksel 30 m ekspor tidak independen | Pseudoreplikasi | Unit = kampus; agregasi ~100 m; bootstrap blok |
| A7 | Zona tidak tumpang tindih dan tak dicemari fasilitas lain | Efek kampus lain terhitung | Periksa tumpang tindih; gabung klaster |
| A8 | Klasifikasi/ambang cukup akurat | Kesalahan tanah terbuka vs terbangun menggeser V3, V4 | Matriks konfusi; sensitivitas ambang |
| A9 | Regresi linear cukup sebagai ringkasan | Hubungan jarak tak linear; kolinearitas | VIF; model bertahap; model non-linear opsional |
| A10 | Albedo dan elevasi menangkap kovariat utama | Material atap, irigasi, aspek terabaikan | Dilaporkan sebagai keterbatasan |
| A11 | L8 dan L9 setara untuk `ST_B10` | Bias sensor | Uji tumpang tindih di lokasi stabil |
| A12 | Ambang harkat mencerminkan variasi nyata | Kelas bergeser menurut ambang | Sensitivitas ambang; ablasi |
| A13 | Tanggal operasi dari dokumen akurat (bila dipakai) | Salah-klasifikasi interval | Pakai hanya yang terdokumentasi |
| A14 | Pembanding mewakili tren tanpa pusat data (Tingkat C) | Kontrafaktual tidak teramati | Pencocokan pra-kejadian; plasebo |

---

## 11. Gerbang percontohan

Langkah pertama: verifikasi **satu** kampus (identitas, batas, kronologi, ketersediaan citra). Angka bertanda **[ASUMSI KERJA]** boleh diubah dengan alasan tertulis.

| Gerbang | Kriteria lolos | Bila gagal |
|---|---|---|
| G1 Identitas dan kronologi | Sumber primer untuk lokasi dan urutan pembangunan | Ganti kampus |
| G2 Ukuran dan data suhu | Tapak >= 15 ha; piksel ST ada (tidak di lubang ASTER GED) | Ganti kampus |
| G3 Observasi di GEE | >= 3 observasi bersih per jendela musim per periode; >= 5 tahun valid untuk tren (skrip Lampiran A) | Perlebar jendela musim atau ganti wilayah; jika tren tak layak, laporkan antarperiode saja |
| G4 Cakupan valid | Fraksi area valid >= 70% di tapak dan zona **[ASUMSI KERJA]** | Tutup Zona 3 atau ganti wilayah |
| G5 Audit emisivitas | Tidak ada anomali besar yang tidak terjelaskan | Pertahankan hanya tutupan lahan; LST dilaporkan terbatas; lewati Tahap 9 dan 11 |
| G6 Pembanding | >= 2 kandidat per kampus lolos pencocokan | Tetap di Tingkat A-B |
| G7 Ekspansi | G1-G6 lolos | Tetap 1-3 kampus |

**Jalur turun-tingkat:** gagal G5 atau G6 tidak membatalkan proyek; Tingkat A (setara Task I-III) selalu bisa diselesaikan.

**Rencana kerja ringkas:** (1) telaah literatur lanjutan dan pilih wilayah, verifikasi satu kampus (G1-G2); (2) jalankan skrip ketersediaan citra (G3-G4); (3) Tahap 1-6; (4) audit emisivitas (G5), lalu Tahap 7-12; (5) Tingkat C bila G6 lolos; (6) laporan.

---

## 12. Rencana luaran

1. Tabel lokasi: nama fasilitas, koordinat, batas, kronologi, sumber, tanggal akses, status verifikasi.
2. Skrip GEE per tahap dengan tautan *Get Link*.
3. Tabel ketersediaan citra bersih per kampus, musim, dan tahun.
4. Hasil K-means (k = 5, 10, 20) dan peta tutupan lahan dengan perubahan, ambang terkalibrasi, matriks konfusi.
5. Peta "tahun mulai terbangun" dan grafik luas terbangun per tahun.
6. Peta LST dan anomali LST dengan skala warna konsisten.
7. Grafik gradien (per kelas tutupan lahan) dan tabel perubahan gradien.
8. Seri anomali per zona, peta tren piksel (visualisasi), peta kelengkapan dan signifikansi.
9. Tabel koefisien regresi sebelum dan sesudah, evaluasi blok, peta residual.
10. Peta IKTL, tabel luas kelas, dan hasil ablasi komponen.
11. Tabel D_i, plasebo, dan efek minimum yang dapat dideteksi (bila Tingkat C).
12. Tabel asumsi, matriks sensitivitas, dan keterbatasan.
13. Laporan interpretasi.

---

## 13. Pemetaan ke Pra-Tubes

Acuan kerumitan adalah Task I-V dan Tugas Mandiri (bukan soal HOTS).

| Pra-Tubes | Di proyek ini |
|---|---|
| Task I: filter citra dan K-means | Tahap 2 dan 4 |
| Task II: median komposit, indeks, ambang, lahan terbangun | Tahap 3 dan 5 |
| Task III: iterasi `map` multitemporal, nilai-tahun, komposit min, grafik luas | Tahap 6 |
| Task IV: harkat variabel ke kelas | Tahap 12 (V1-V4, ambang kuantil) |
| Task V: tiga komponen digabung menjadi risiko | Tahap 12 (komponen Termal, Permukaan, Konversi) |
| Tugas Mandiri 1: sensitivitas k = 5, 10, 20 | Tahap 4 |
| Tugas Mandiri 2: kalibrasi ambang dari titik | Tahap 5 |
| Tugas Mandiri 3: sprawl kota lain, tambah tahun 2024, peta dan grafik | Tahap 6 (tahun hingga 2025, kampus sebagai ROI) |
| Tugas Mandiri 4: aktif/nonaktif komponen, luas per kelas | Ablasi komponen IKTL (Tahap 12) |
| **Di atas Pra-Tubes** | Tahap 8-11 dan 13: audit emisivitas, tren Sen/Mann-Kendall, gradien per kelas, regresi dengan validasi blok, pembanding, plasebo |

Catatan: Modul memakai komposit lintas lima satelit (Landsat 5-9); proyek ini memakai Landsat 8 dan 9 saja untuk Tingkat A-B. Perluasan lintas sensor adalah opsi Tingkat C. Kerumitan di sini datang dari desain dan pengujian, bukan dari klaim yang lebih kuat.

---

## 14. Daftar periksa auditor

- [ ] Apakah ada klaim sebab-akibat yang tidak didukung desain (Bagian 8)?
- [ ] Apakah ada variabel pasca-kejadian di estimasi utama?
- [ ] Apakah unit analisis adalah kampus, dan kesimpulan dinyatakan sebagai studi kasus bila n < 6?
- [ ] Apakah area referensi memenuhi definisi stabil (5.3) dan dipakai hanya untuk anomali?
- [ ] Apakah audit emisivitas (Tahap 8) benar-benar menjadi gerbang sebelum tren dan regresi?
- [ ] Apakah tren dihitung pada anomali, dan seri zona dilaporkan bersama peta piksel?
- [ ] Apakah regresi mengecualikan bagian dalam kampus, memeriksa VIF, memakai blok spasial, dan tidak melaporkan nilai-p biasa?
- [ ] Apakah IKTL dilabeli deskriptif dan tidak dipakai sebagai "risiko"?
- [ ] Apakah semua **[VERIFIKASI]** dicek (reducer `sensSlope`/`kendallsCorrelation`, rumus albedo, ID Sentinel-2 dan Landsat 5/7, daftar penulis dan judul yang bertanda [lengkapi])?
- [ ] Apakah angka **[ASUMSI KERJA]** (15 ha, 70% area valid, 50 titik per kelas, ambang kuantil, kriteria stabil) dapat dipertahankan?
- [ ] Apakah ketersediaan citra bersih per lokasi sudah dihitung di GEE, bukan hanya ketersediaan dataset?
- [ ] Apakah telusur literatur untuk kebaruan sudah dilakukan?

---

## 15. Referensi

1. Marinoni, A. dkk. (2026). *The Data Heat Island Effect.* arXiv:2603.20897v3. https://arxiv.org/abs/2603.20897v3
2. Katalog GEE: Landsat 8 L2 T1. https://developers.google.com/earth-engine/datasets/catalog/LANDSAT_LC08_C02_T1_L2
3. Katalog GEE: Landsat 9 L2 T1. https://developers.google.com/earth-engine/datasets/catalog/LANDSAT_LC09_C02_T1_L2
4. USGS. *Landsat Collection 2 Surface Temperature.* https://www.usgs.gov/landsat-missions/landsat-collection-2-surface-temperature
5. USGS. *Landsat Collection 2 Known Issues.* https://www.usgs.gov/landsat-missions/landsat-collection-2-known-issues
6. Ermida, S. L. dkk. (2020). *Google Earth Engine Open-Source Code for Land Surface Temperature Estimation from the Landsat Series.* Remote Sensing 12(9), 1471. https://doi.org/10.3390/rs12091471
7. Studi analog fasilitas besar (Bagian 2.2): solar park (DOI 10.1016/j.rset.2021.100008); Vavassori dkk. 2023 (DOI 10.5194/isprs-archives-XLVIII-1-W2-2023-1589-2023); Cheng dkk. 2023 (DOI 10.5194/isprs-archives-XLVIII-1-W2-2023-1343-2023); kompleks petrokimia Rio de Janeiro (ICC 2015, icaci.org).
8. LST dan indeks di GEE (Bagian 2.2): Sustainability 14, 14868 (2022); ISPRS Int. J. Geo-Inf. (2024); Geoid ITS (DKI Jakarta).
9. Tren: tutorial komunitas Earth Engine *Non-Parametric Trend Analysis* (https://developers.google.com/earth-engine/tutorials/community/nonparametric-trends); Atmosphere 15(3), 318 (2024). https://www.mdpi.com/2073-4433/15/3/318
10. Validasi spasial: Frontiers in Remote Sensing (2025), DOI 10.3389/frsen.2025.1531097; Roberts dkk. (2017), DOI 10.1111/ecog.02881.
11. Cook dkk. (2014), DOI 10.3390/rs61111244 (dirujuk katalog GEE).
12. Metz, M., Rocchini, D., Neteler, M. (2014). Remote Sensing 6(5), 3822-3840 (dirujuk paper acuan).
13. Modul Praktikum Intermediate Google Earth Engine (`modul-intermediate-gee.docx`).

---

## Lampiran A. Kerangka skrip GEE (belum dijalankan)

Nama band dan skala sesuai katalog (Bagian 6). Nama reducer dan ambang bertanda **[VERIFIKASI]** atau **[ASUMSI KERJA]**.

```javascript
// KERANGKA: BELUM DIJALANKAN
var campus = ee.Geometry.Polygon([/* hasil digitasi, terverifikasi */]);
var refArea = ee.Geometry.Polygon([/* area referensi stabil (5.3) */]);
var aoi = campus.buffer(2500);
var z1 = campus.buffer(500).difference(campus);
var z2 = campus.buffer(1000).difference(campus.buffer(500));
var z3 = campus.buffer(2000).difference(campus.buffer(1000));

var L8 = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2');
var L9 = ee.ImageCollection('LANDSAT/LC09/C02/T1_L2');

function prep(img) {
  var qa = img.select('QA_PIXEL');
  var ok = qa.bitwiseAnd(1 << 1).eq(0)          // dilated cloud
      .and(qa.bitwiseAnd(1 << 3).eq(0))         // cloud
      .and(qa.bitwiseAnd(1 << 4).eq(0))         // cloud shadow
      .and(img.select('ST_QA').multiply(0.01).lt(3))      // K, ambang awal [ASUMSI KERJA]
      .and(img.select('ST_CDIST').multiply(0.01).gt(0.1)); // km, ambang awal [ASUMSI KERJA]
  var sr = img.select('SR_B.').multiply(0.0000275).add(-0.2);
  var lst = img.select('ST_B10').multiply(0.00341802).add(149.0)
      .subtract(273.15).rename('LST');
  var emis = img.select('ST_EMIS').multiply(0.0001).rename('EMIS');
  var ndvi = sr.normalizedDifference(['SR_B5', 'SR_B4']).rename('NDVI');
  var ndbi = sr.normalizedDifference(['SR_B6', 'SR_B5']).rename('NDBI');
  var mndwi = sr.normalizedDifference(['SR_B3', 'SR_B6']).rename('MNDWI');
  return ee.Image.cat([lst, emis, ndvi, ndbi, mndwi])
      .updateMask(ok)
      .copyProperties(img, ['system:time_start']);
}

function seleksi(tahun) {
  return L8.merge(L9)
      .filterBounds(aoi)
      .filter(ee.Filter.eq('PROCESSING_LEVEL', 'L2SP'))
      .filter(ee.Filter.calendarRange(tahun, tahun, 'year'))
      .filter(ee.Filter.calendarRange(6, 9, 'month'))   // jendela musim [ASUMSI KERJA]
      .map(prep);
}

// 1) Gerbang G3: ketersediaan observasi bersih per tahun
var tabelKetersediaan = ee.FeatureCollection(
  ee.List.sequence(2013, 2025).map(function (y) {
    var col = seleksi(y);
    var frac = col.select('LST').count().gt(0).reduceRegion({
      reducer: ee.Reducer.mean(), geometry: aoi, scale: 30, maxPixels: 1e9
    });
    return ee.Feature(null, {tahun: y, nScene: col.size(), fraksiValid: frac.get('LST')});
  })
);
print('Ketersediaan', tabelKetersediaan);

// 2) Komposit tahunan dan anomali terhadap area referensi (Tahap 3, 7)
function anomali(y) {
  var med = seleksi(y).median();
  var ref = ee.Number(med.select('LST').reduceRegion({
    reducer: ee.Reducer.median(), geometry: refArea, scale: 30, maxPixels: 1e9
  }).get('LST'));
  var t = ee.Image.constant(y).float().rename('t');
  return ee.Image.cat([t, med.select('LST').subtract(ref).rename('LSTanom')])
      .set('year', y);
}
var deret = ee.ImageCollection(ee.List.sequence(2014, 2025).map(anomali));

// 3) Tren piksel pada anomali (Tahap 9): urutan band = waktu, lalu respons
var sen = deret.select(['t', 'LSTanom']).reduce(ee.Reducer.sensSlope());          // [VERIFIKASI]
var mk  = deret.select(['t', 'LSTanom']).reduce(ee.Reducer.kendallsCorrelation(2)); // [VERIFIKASI]
var nValid = deret.select('LSTanom').count();    // syarat >= 5 tahun valid

// 4) Statistik zona (Tahap 10)
var fc = ee.FeatureCollection([
  ee.Feature(campus, {zona: 'tapak'}), ee.Feature(z1, {zona: 'z1'}),
  ee.Feature(z2, {zona: 'z2'}), ee.Feature(z3, {zona: 'z3'})
]);
var stat = ee.Reducer.mean().combine(ee.Reducer.stdDev(), '', true)
    .combine(ee.Reducer.count(), '', true);
// Contoh: komposit satu tahun. Ulangi per periode dan per kelas tutupan lahan.
var tabelZona = seleksi(2023).median().select(['LST', 'NDVI', 'NDBI'])
    .reduceRegions({collection: fc, reducer: stat, scale: 30});
print('Statistik zona 2023', tabelZona);
// Catatan: scale 30 hanya grid keluaran; piksel termal asli ~100 m.
```

Belum ada dalam kerangka: klasifikasi dan matriks konfusi, K-means, peta tahun mulai terbangun, regresi dan ekspor sampel, IKTL dan ablasi, tanggal bersama untuk pembanding, serta bootstrap di luar GEE.
