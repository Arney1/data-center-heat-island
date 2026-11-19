# Metodologi DIP dan Status Validasi

Pembaruan 20 November 2026. Dua lokasi dikonfigurasi: AWS Boardman dan kandidat
H5 Quincy II. Implementasi modul tidak berarti semua keluaran sudah tervalidasi.
Pengguna sudah menghasilkan dan menampilkan seri LST Quincy; angka Boardman lama
tetap artefak tersimpan, bukan hasil reproduksi baru dalam pembaruan ini.

## 1. Geometri dan skala analisis

Batas kampus dan atap dibedakan. Bentuk union atap, potong terhadap kampus, lalu
hitung sisa tapak dengan difference. Jangan menjumlahkan luas poligon tumpang
tindih; enam input atap Quincy bukan bukti enam data hall. Angka luas konfigurasi
belum dihitung ulang dan harus dilabeli metadata sementara.

Zona utama: kampus, atap, sisa tapak, 0–500 m, 500–1000 m dan 1–2 km dari batas
kampus. Buffer analisis berbasis tepi kampus; lingkaran Folium dari centroid hanya
ilustrasi dan tidak identik dengan geometri buffer GEE.

Reflektansi tersedia pada kisi 30 m. Sensor termal Landsat 8 memiliki resolusi
asli 100 m yang disampel ulang ke produk 30 m; piksel keluaran yang berdekatan
bukan observasi termal 30 m independen. Buffer atap -15 m tidak menjamin piksel
termal murni dan dapat menghapus atap sempit. Jangan menyebutnya isolasi panas
atap/server tanpa analisis campuran dan ukuran tapak.
[Sumber USGS](https://www.usgs.gov/landsat-missions/landsat-8).

## 2. Kalibrasi dan QA

Produk `LANDSAT/LC08/C02/T1_L2` dan `LANDSAT/LC09/C02/T1_L2`, proses `L2SP`:

```text
SR = DN * 0.0000275 - 0.2
LST (°C) = DN_ST_B10 * 0.00341802 + 149.0 - 273.15
EMIS = DN_ST_EMIS * 0.0001
```

Kode saat ini memask QA_PIXEL bit 1/3/4, ST_QA*0.01 < 3 K dan
ST_CDIST*0.01 > 0.2 km. Audit tambahan fill/cirrus/salju/saturasi perlu diselesaikan
dan disamakan antara JavaScript/Python sebelum eksperimen final. Nilai missing
tetap missing; tidak diisi suhu referensi fiktif.

NDVI=(B5-B4)/(B5+B4), NDBI=(B6-B5)/(B6+B5), MNDWI=(B3-B6)/(B3+B6).
Proksi albedo yang diimplementasikan: 0.356 B2 + 0.130 B4 + 0.373 B5 + 0.085 B6
+ 0.072 B7 - 0.0018. Dokumentasikan validitas proksi untuk material atap dan
sensor yang dipakai. `normalizedDifference` GEE memask input negatif; audit efek
ini terhadap reflektansi hasil scaling, jangan menganggap semua nilai SR dalam [0,1].
[Katalog produk](https://developers.google.com/earth-engine/datasets/catalog/LANDSAT_LC08_C02_T1_L2).

## 3. Komposit, ketersediaan dan anomali

Komposit median Juni–September per tahun. Laporkan scene, tanggal, fraksi valid
per scene, jumlah observasi per piksel/zona dan tahun kosong. Menghitung scene
bersih >=70% tidak otomatis berarti komposit hanya memakai scene tersebut:
periksa apakah filter itu benar diterapkan atau hanya dilaporkan.

LSTanom = LST - median LST referensi regional per tahun. Referensi kerja: cincin
5–12 km, WorldCover 2021 pertanian (kelas 40), lereng SRTM <3°. Ini mask satu tahun,
bukan bukti pertanian stabil 2013–2026. Perlu pemeriksaan stabilitas, irigasi dan
perubahan tutupan; perbandingan lintas lokasi dipengaruhi referensi masing-masing.
Jika referensi tidak tersedia, LSTanom harus kosong; LST asli masih dapat dilaporkan.

Fetcher Python kini memakai mask referensi dan median tanpa fallback 32 °C. Jalur
zonal Python masih perlu disamakan dengan skrip JS terkait mask MNDWI dan rounding
sebelum menggabungkan hasil dua jalur sebagai satu eksperimen.

## 4. Kronologi dan sebelum/sesudah

Boardman mempertahankan asumsi lama pra 2019–2021 dan pasca 2025–2026. Statusnya
perlu bukti tanggal citra/operasi. Quincy tidak memakai periode tersebut: fasilitas
lama dan ekspansi Yahoo berbeda, izin bukan bukti tanggal selesai bangunan, dan
akuisisi bukan konstruksi. `fetch_epoch_composites` Quincy diblokir sampai periode
ditetapkan. [Audit kronologi](QUINCY_CHRONOLOGY_AUDIT.md).

Peta persistent built-up adalah hasil aturan spektral, bukan tanggal konstruksi
ground truth. Ambang NDBI >-0.1, NDVI <0.2 dan MNDWI <0 merupakan asumsi awal.
Tahun tertutup awan tidak boleh disamakan dengan tidak terbangun. Validasi dari
citra bertanggal harus mendahului pemilihan periode final.

## 5. Analisis lanjutan dan batas inferensi

- Gradien cincin mengukur perubahan spasial rerata; sesuaikan tutupan lahan dan
  laporkan ketidakpastian. Delta gradien tidak sendirinya membuktikan efek operasi.
- Sen's slope/Kendall tau adalah ringkasan tren; tau saja bukan p-value uji
  Mann–Kendall lengkap. Periksa autokorelasi, multiple testing dan perubahan fase.
- Audit EMIS/NDVI dapat menunjukkan sensitivitas retrieval; korelasi kecil tidak
  menjamin bebas artefak emisivitas.
- Regresi spasial perlu pemeriksaan VIF, residual dan validasi blok; koefisien
  jarak bukan estimasi kausal panas server.
- IKTL adalah indeks deskriptif; kelas dan bobot perlu sensitivitas/ablasi.
- DiD memerlukan kontrol relevan, periode sah, parallel trends, uji plasebo dan
  ketidakpastian. Kandidat koordinat kontrol Quincy belum tervalidasi.

## 6. DIP dan ML

Kalibrasi, masking, komposit, indeks, segmentasi dan zonal statistics adalah bagian
DIP. RF/SVM tersedia dengan random stratified split; spatial block ID tersedia
tetapi evaluator belum memakainya. Sampling GEE memakai pseudo-label dari indeks,
sehingga belum menjadi evaluasi berlabel independen. Data demo sintetis hanya
untuk alur kode, bukan bukti ilmiah. Lihat [roadmap eksperimen](ML_AND_PAPER_ROADMAP.md).

## 7. Status hasil

Dokumen sebelumnya menyatakan semua 13 tahap selesai dan memuat angka yang berbeda
dari JSON Boardman. Tabel tersebut tidak dipakai sebagai kesimpulan baru. Angka
lama tetap disimpan di `data/processed/` agar tidak kehilangan artefak, tetapi
harus ditautkan ke ekspor, parameter, sumber dan versi yang dapat direproduksi
sebelum dikutip dalam paper. Grafik Quincy dari CSV menunjukkan data berhasil
ditampilkan, bukan bahwa seluruh metodologi telah selesai divalidasi.
