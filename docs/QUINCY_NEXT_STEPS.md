# Langkah Quincy Setelah Grafik LST

Pembaruan 20 November 2026: software klasifikasi RF/SVM, validasi blok spasial,
model pooled/cross-site dan inferensi GeoTIFF kini tersedia. Ikuti
[panduan terbaru](SUPERVISED_CLASSIFICATION.md) untuk langkah GEE dan ekspor label.
Sampel referensi Quincy belum tersedia di repositori; daftar di bawah adalah
pekerjaan data yang masih relevan, bukan klaim bahwa seluruh software belum ada.

Panduan lanjutan untuk kondisi saat ini: CSV hasil GEE sudah tampil di Streamlit.
Kode terbaru berada di `app/app.py`; tidak perlu mencari salinan
`app_dua_lokasi.py` dari panduan percobaan sebelumnya.

## 1. Simpan dan periksa hasil yang sudah ada

Simpan salinan CSV asli, parameter GEE, tanggal ekspor dan geometri. Agar tidak
perlu unggah setiap sesi, salin CSV ke
`data/processed/h5_quincy2_timeseries.csv`. Jangan mengganti CSV Boardman.

```powershell
.\.venv\Scripts\python.exe -m streamlit run app/app.py
```

Pilih H5 Quincy II. Dashboard membaca file tersimpan jika tidak ada unggahan;
unggahan dapat menggantikannya untuk sesi tersebut. CSV harus memiliki
`tahun,zona,LST,LSTanom,NDVI,NDBI,EMIS`. Identitas lokasi, jika ada, harus Quincy.
Tahun/zona duplikat dan kolom angka yang tidak valid ditolak.

Periksa grafik untuk kampus, atap, sisa tapak dan cincin jarak. Rata-rata antar
tahun adalah rata-rata statistik zona tahunan, bukan rata-rata semua scene.
Perubahan tahun akhir–awal bukan estimasi efek pembangunan. Nilai hilang tidak
diganti nol. LST adalah suhu permukaan, bukan suhu udara atau server.

## 2. Kembali ke GEE untuk audit kualitas

Pada skrip Quincy, jalankan modul ketersediaan citra dan seri waktu. Simpan jumlah
scene dan piksel valid per zona/tahun; jangan hanya menyimpan grafik. Pastikan
mask awan, musim, skala dan definisi zona sama dengan Boardman untuk perbandingan.
Periksa area referensi: pertanian yang diairi bisa lebih dingin dari area industri;
LSTanom besar belum membuktikan panas server.

Jika skrip masih memuat PRE_TAHUN 2019–2021 / POST_TAHUN 2025–2026 dari AWS,
jangan aktifkan hasil berlabel sebelum/sesudah konstruksi Quincy. Biarkan modul
DiD, regresi pra/pasca dan IKTL berbasis perubahan nonaktif sampai kronologi valid.
Ikuti [audit kronologi](QUINCY_CHRONOLOGY_AUDIT.md) terlebih dahulu.

## 3. Tambahkan DIP tutupan lahan

1. Periksa tumpang tindih poligon atap dan buat union untuk luas.
2. Tampilkan komposit RGB/false-color, NDVI, NDBI dan MNDWI pada beberapa tahun.
3. Jalankan threshold built-up dan K-Means sebagai eksplorasi. Klaster bukan
   kelas tutupan lahan sampai diinterpretasi dan divalidasi.
4. Cocokkan perubahan spektral dengan citra bertanggal. Jangan menggunakan luas
   metadata lama atau pixel threshold sebagai luas atap ground truth.

## 4. Siapkan data untuk ML

CSV seri waktu berisi rerata zona; dataset pelatihan membutuhkan **sampel piksel**
beserta fitur dan label independen. Ekspor minimal band B2–B7, NDVI, NDBI, MNDWI,
albedo, LST/EMIS, koordinat, tahun, `site_id`, `data_source`, `label_source`,
kelas referensi dan ID polygon/blok. Buat label vegetasi, terbangun, tanah dan air
dari anotasi citra bertanggal; aturan indeks hanya baseline/pseudo-label.

Sampling GEE dalam fetcher sekarang tidak beralih diam-diam ke generator.
`allow_synthetic=True` hanya membuat contoh bertanda `synthetic_demo`. Jangan
menggunakan contoh itu atau metrik JSON lama sebagai bukti akurasi lapangan.

## 5. Eksperimen pertama yang disarankan

Bandingkan threshold, RF dan SVM dengan label/fold yang sama. Uji tanpa/dengan
indeks dan termal, evaluasi macro-F1 serta confusion matrix pada blok spasial.
Kemudian lakukan train Boardman/test Quincy jika data independen dua lokasi siap.
Lihat [roadmap eksperimen](ML_AND_PAPER_ROADMAP.md).

Prioritas berikutnya adalah **validasi footprint, kronologi, kualitas citra dan
label ML**, bukan langsung mengaktifkan semua sakelar GEE. Untuk peta termal,
ekspor raster/tiles; untuk DiD, siapkan kontrol dan periode; untuk IKTL, siapkan
komponen per piksel. Ketiganya tidak dapat direkonstruksi hanya dari CSV seri LST.
