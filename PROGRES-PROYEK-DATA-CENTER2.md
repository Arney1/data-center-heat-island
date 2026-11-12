# Progres Penentuan Topik Proyek Pusat Data dan Suhu Permukaan

Tanggal pembaruan: 22 Oktober 2026

## 1. Ringkasan progres

Proyek telah memasuki tahap perumusan penelitian: paper acuan telah dipilih dan ditelaah, judul kerja telah disusun, ruang lingkup telah disederhanakan, serta rancangan metode pengolahan citra di Google Earth Engine (GEE) telah ditentukan. Objek penelitian tetap pusat data. Modul Intermediate GEE digunakan sebagai acuan tingkat kompleksitas, bukan sebagai sumber topik penelitian.

Lokasi pusat data dan periode pengamatan belum ditetapkan secara final. Pengumpulan citra, implementasi skrip GEE, dan analisis hasil belum dilakukan dalam progres yang dirangkum di dokumen ini.

| Komponen | Progres saat ini | Status |
|---|---|---|
| Paper acuan | Paper tentang data heat island telah dipilih dan diaudit secara metodologis | Selesai pada tahap kajian awal |
| Judul | Judul kerja telah dirumuskan sesuai hasil audit | Usulan untuk digunakan |
| Masalah penelitian | Difokuskan pada perubahan suhu permukaan, tutupan lahan, dan pola menurut jarak | Telah dirumuskan |
| Lokasi pusat data | Kandidat wilayah telah disebutkan dalam diskusi; fasilitas dan koordinat belum diverifikasi | Belum final |
| Metode | Rancangan analisis multitemporal dan per zona di GEE telah disusun | Rancangan awal |
| Implementasi dan hasil | Belum ada hasil pengolahan citra yang dapat dilaporkan | Belum dilakukan |

## 2. Paper acuan dan dasar pemilihan topik

Paper utama yang digunakan adalah:

Marinoni, A., dkk. (2026). *The Data Heat Island Effect: Quantifying the Impact of AI Data Centers in a Warming World*. arXiv:2603.20897v3, versi 21 April 2026.

- Halaman paper: https://arxiv.org/abs/2603.20897v3
- Teks lengkap: https://arxiv.org/html/2603.20897v3

Paper tersebut meneliti perubahan suhu permukaan di sekitar pusat data dari sisi waktu dan jarak. Penulis melaporkan kenaikan rata-rata sekitar 2 °C setelah awal operasi. Angka tersebut merupakan temuan yang dilaporkan penulis, bukan hasil proyek ini maupun nilai yang harus ditemukan kembali.

Hasil audit awal menunjukkan bahwa perbandingan sebelum–sesudah tanpa kelompok pembanding yang memadai belum cukup untuk mengatribusikan pemanasan pada operasi pusat data. Perubahan vegetasi, pembangunan, dan perubahan lingkungan sekitar perlu dipertimbangkan. Dokumentasi tanggal operasi dan data rekonstruksi suhu juga membatasi replikasi.

Karena itu, proyek ini mengambil masalah penelitian paper sebagai dasar, dengan metode yang disederhanakan dan interpretasi yang lebih terbatas. Proyek tidak dirancang untuk membuktikan bahwa panas server menyebabkan kenaikan suhu tertentu.

## 3. Judul kerja

**Analisis Multitemporal Suhu Permukaan dan Perubahan Tutupan Lahan di Sekitar Pusat Data Menggunakan Landsat dan Google Earth Engine**

Versi bahasa Inggris:

*Multitemporal Analysis of Land Surface Temperature and Land-Cover Change Around Data Centers Using Landsat and Google Earth Engine.*

Nama wilayah dan rentang tahun akan ditambahkan setelah kelayakan lokasi serta ketersediaan citra diperiksa.

Judul ini mempertahankan pusat data sebagai objek utama dan hubungan antara pembangunan kawasan dengan kondisi termal sebagai fokus. Istilah “analisis” digunakan karena rancangan penelitian bersifat observasional. Judul tidak menjanjikan pemisahan panas operasional dari pengaruh perubahan tutupan lahan.

## 4. Rumusan masalah dan tujuan

Rumusan masalah utama:

> Bagaimana suhu permukaan dan tutupan lahan di sekitar pusat data berubah sebelum dan sesudah pengembangan kawasan, serta bagaimana pola suhu tersebut bervariasi menurut jarak dari pusat data?

Pertanyaan penelitian:

1. Bagaimana perubahan suhu permukaan pada periode sebelum, transisi pembangunan, dan sesudah pengembangan kawasan pusat data?
2. Apakah lokasi dengan perubahan suhu lebih tinggi juga memperlihatkan penurunan vegetasi atau peningkatan lahan terbangun?
3. Bagaimana perbedaan suhu antara tapak pusat data dan zona di sekitarnya?

Tujuan proyek adalah menghasilkan peta perubahan tutupan lahan, peta suhu permukaan, serta ringkasan pola suhu menurut periode dan jarak. Keterkaitan yang ditemukan akan dibahas sebagai asosiasi, bukan bukti sebab-akibat.

## 5. Progres penentuan lokasi pusat data

Lokasi studi belum dipilih secara final. Teks diskusi sebelumnya menyebut beberapa kandidat wilayah berikut, tetapi tidak menyertakan tabel fasilitas, koordinat, atau sumber primer yang cukup untuk menetapkannya sebagai sampel.

| Kandidat wilayah dalam diskusi | Informasi yang masih diperlukan | Status |
|---|---|---|
| Prineville, Oregon, Amerika Serikat | Nama fasilitas, batas kampus, tanggal pembangunan dan operasi, serta citra sebelum pembangunan | Kandidat belum diverifikasi |
| The Dalles, Oregon, Amerika Serikat | Identitas kampus, tahapan ekspansi, koordinat, dan dokumentasi tanggal | Kandidat belum diverifikasi |
| Boydton, Virginia, Amerika Serikat | Batas fasilitas, kronologi pengembangan, dan ketercukupan citra | Kandidat belum diverifikasi |
| Quincy, Washington, Amerika Serikat | Pemilihan fasilitas atau klaster, batas area, dan pengaruh fasilitas berdekatan | Kandidat belum diverifikasi |
| Cikarang/Jabodetabek, Indonesia | Nama fasilitas spesifik, sumber resmi, kronologi pembangunan, dan konteks kawasan industri | Alternatif lokal belum diverifikasi |

Nama-nama tersebut adalah kandidat wilayah, bukan daftar pusat data yang telah tervalidasi. Tanggal operasi dan koordinat tidak dicantumkan karena belum dikonfirmasi.

### Kriteria pemilihan lokasi

Target awal adalah 2–3 kampus pusat data dalam satu wilayah yang memiliki kondisi lingkungan relatif sebanding. Kelayakannya ditentukan oleh:

1. Identitas dan lokasi fasilitas dapat diverifikasi melalui sumber operator atau dokumen resmi.
2. Tapak kampus cukup besar dan jelas pada citra untuk dianalisis pada skala termal Landsat.
3. Kronologi pembangunan dan ekspansi dapat ditelusuri; tanggal peresmian tidak langsung dianggap sebagai tanggal perubahan fisik lahan.
4. Tersedia citra yang memadai sebelum dan sesudah pengembangan dengan musim pengamatan yang sebanding.
5. Pembangunan di sekitar lokasi dapat diidentifikasi dan dibahas sebagai faktor lain.
6. Tersedia area referensi yang relatif stabil untuk memberi konteks perubahan suhu regional.

Untuk rancangan Landsat 8/9, periode observasi harus memperhatikan bahwa Landsat 8 tersedia sejak 2013. Fasilitas yang sudah beroperasi sebelumnya belum tentu cocok untuk kajian sebelum–sesudah pembangunan awal. Pilih fasilitas yang lebih baru atau tahap ekspansi yang terdokumentasi; penggunaan sensor Landsat yang lebih lama akan menambah pekerjaan harmonisasi.

## 6. Rancangan metode di Google Earth Engine

### 6.1 Ruang lingkup

- Unit kajian: 2–3 kampus pusat data yang lolos pemeriksaan kelayakan.
- Periode: tiga periode pengamatan, yaitu sebelum pengembangan, transisi pembangunan, dan sesudah pengembangan.
- Pemilihan waktu: jendela musim yang sama antarperiode, disesuaikan dengan jumlah observasi bebas awan.
- Pendekatan: analisis deskriptif multitemporal, perubahan tutupan lahan, dan perbandingan statistik per zona.
- Area referensi: wilayah sekitar yang relatif stabil untuk konteks, bukan otomatis kelompok kontrol kausal.

### 6.2 Data utama

| Data | Kegunaan |
|---|---|
| Landsat 8 Collection 2 Level-2 (`LANDSAT/LC08/C02/T1_L2`) | Reflektansi permukaan dan suhu permukaan |
| Landsat 9 Collection 2 Level-2 (`LANDSAT/LC09/C02/T1_L2`), bila diperlukan | Pelengkap observasi pada periode yang tersedia |
| Batas kampus pusat data yang diverifikasi | Menentukan tapak dan zona jarak |
| Dokumen operator atau sumber resmi | Memeriksa identitas dan kronologi fasilitas |
| Citra referensi dengan tanggal yang sesuai | Memeriksa interpretasi tutupan lahan |

Landsat dipilih untuk analisis lokal karena detail spasial termalnya lebih sesuai dibandingkan MODIS untuk kampus individual. Grid keluaran 30 m tidak berarti resolusi termal asli 30 m; jumlah piksel keluaran tidak boleh diperlakukan sebagai jumlah pengamatan independen.

### 6.3 Tahapan pengolahan

1. **Penetapan area studi.** Membuat poligon tapak kampus dan memeriksa konteks pembangunan sekitar.
2. **Pemilihan citra.** Memfilter koleksi menurut lokasi, tanggal, dan ketersediaan produk suhu (`L2SP`).
3. **Prapengolahan.** Melakukan masking awan dan bayangan berbasis QA, scaling reflektansi dan suhu, serta pemeriksaan kualitas data.
4. **Komposit musiman.** Menyusun komposit untuk setiap periode dengan mencatat jumlah observasi valid dan cakupan area yang tersedia.
5. **Indeks spektral.** Menghitung NDVI untuk vegetasi, NDBI sebagai indikator lahan terbangun, serta MNDWI untuk membantu identifikasi air.
6. **Pemetaan tutupan lahan.** Menggunakan ambang yang dikalibrasi dan pemeriksaan visual. K-means dapat digunakan sebagai eksplorasi tambahan, bukan tahapan wajib.
7. **Perubahan tutupan lahan.** Membandingkan luas vegetasi dan lahan terbangun antarperiode. Tanah terbuka perlu diperiksa karena dapat menyerupai lahan terbangun pada NDBI.
8. **Pemetaan suhu.** Mengolah `ST_B10` menjadi derajat Celsius dan menyajikan distribusi LST untuk setiap periode.
9. **Analisis per zona.** Menghitung statistik suhu pada tapak kampus dan zona di sekitarnya.
10. **Interpretasi.** Membandingkan perubahan suhu dengan perubahan tutupan lahan dan kondisi area referensi.

Konversi suhu Landsat Collection 2 Level-2:

```text
LST (°C) = ST_B10 × 0.00341802 + 149.0 − 273.15
```

### 6.4 Zona analisis yang diusulkan

| Zona | Definisi |
|---|---|
| Tapak kampus | Poligon kampus pusat data |
| Zona 1 | 0–500 m di luar batas kampus |
| Zona 2 | 500–1.000 m di luar batas kampus |
| Zona 3 | 1–2 km di luar batas kampus |

Zona dibuat tidak saling tumpang tindih dan diukur dari batas kampus. Jarak tersebut merupakan pilihan awal untuk perbandingan spasial, bukan klaim jangkauan panas pusat data. Tumpang tindih zona antar-kampus harus diperiksa agar hasil tidak dianggap sebagai sampel independen.

### 6.5 Validasi dan uji sensitivitas

- Memeriksa kelas tutupan lahan menggunakan titik referensi terpisah dari titik kalibrasi ambang.
- Melaporkan kesalahan klasifikasi, terutama antara tanah terbuka dan lahan terbangun.
- Membandingkan hasil beberapa pilihan ambang indeks.
- Memeriksa jumlah observasi bebas awan dan konsistensi musim antarperiode.
- Menguji apakah kesimpulan berubah ketika batas zona atau cakupan tapak sedikit diubah.
- Memeriksa kemungkinan artefak estimasi suhu terkait perubahan vegetasi dan emisivitas.

Validasi tutupan lahan tidak sama dengan validasi akurasi suhu. Tanpa pengukuran suhu lapangan yang sesuai, akurasi absolut LST tidak dapat dinyatakan telah tervalidasi secara lokal.

## 7. Penyesuaian setelah audit

| Rancangan sebelumnya | Penyesuaian untuk proyek mata kuliah |
|---|---|
| Puluhan kampus lintas negara | 2–3 kampus dalam satu wilayah |
| Pemisahan panas operasional dan perubahan lahan | Analisis hubungan perubahan LST dan tutupan lahan |
| Difference-in-differences dan event study | Perbandingan antarkurun waktu dan antar-zona |
| Analisis kapasitas listrik dan dose-response | Dikeluarkan dari lingkup inti |
| Estimasi populasi terdampak dan mitigasi | Dikeluarkan dari lingkup inti |
| Jangkauan hingga 10 km mengikuti paper | Zona awal hingga 2 km untuk kajian lokal |

Kode MODIS/DiD dan judul multi-metode dalam teks diskusi lama merupakan usulan terdahulu yang belum diuji. Keduanya tidak digunakan sebagai metode final dalam rancangan yang disederhanakan ini.

## 8. Batas interpretasi

LST adalah suhu permukaan yang diamati satelit, bukan suhu udara atau ukuran langsung paparan panas manusia. Pola suhu dapat dipengaruhi vegetasi, material permukaan, cuaca, musim, pembangunan di sekitar kampus, serta ketidakpastian produk satelit.

USGS mencatat masalah penyesuaian emisivitas pada produk suhu Landsat Collection 2 di lokasi dengan perubahan vegetasi yang besar. Hal ini relevan dengan pembangunan kampus dan perlu diperiksa dalam analisis. Sumber: https://www.usgs.gov/landsat-missions/landsat-collection-2-surface-temperature

Kesimpulan yang dapat dituju adalah adanya atau tidak adanya perubahan suhu permukaan yang beriringan dengan perubahan tutupan lahan di lokasi kajian. Proyek tidak dapat langsung menyatakan bahwa kenaikan suhu berasal dari beban komputasi, aktivitas AI, atau panas operasional pusat data.

## 9. Rencana luaran

1. Tabel lokasi berisi nama fasilitas, koordinat, batas kampus, kronologi, sumber, dan status verifikasi.
2. Skrip GEE untuk prapengolahan, indeks spektral, suhu permukaan, serta statistik zona.
3. Peta tutupan lahan dan perubahan antarperiode.
4. Peta LST dengan skala warna yang konsisten untuk perbandingan.
5. Grafik suhu menurut periode dan zona jarak.
6. Tabel perubahan vegetasi, lahan terbangun, dan suhu.
7. Laporan interpretasi beserta validasi dan keterbatasan.

## 10. Langkah berikutnya

Prioritas berikutnya adalah memverifikasi satu kampus sebagai studi percontohan: identitas, batas, kronologi pengembangan, serta ketersediaan citra. Setelah itu, lakukan pemeriksaan observasi bebas awan dan cakupan suhu sebelum menetapkan lokasi tambahan serta periode penelitian.

Keberhasilan tahap percontohan menjadi dasar untuk memfinalkan wilayah pada judul dan memulai implementasi GEE. Dokumen ini mencatat progres perencanaan; belum memuat temuan empiris proyek.

## Referensi teknis

- Marinoni dkk. (2026), paper acuan: https://arxiv.org/abs/2603.20897v3
- Katalog Landsat 8 GEE: https://developers.google.com/earth-engine/datasets/catalog/LANDSAT_LC08_C02_T1_L2
- Katalog Landsat 9 GEE: https://developers.google.com/earth-engine/datasets/catalog/LANDSAT_LC09_C02_T1_L2
- Dokumentasi dan keterbatasan suhu Landsat USGS: https://www.usgs.gov/landsat-missions/landsat-collection-2-surface-temperature
