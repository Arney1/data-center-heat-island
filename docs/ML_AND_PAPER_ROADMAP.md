# Roadmap DIP, Machine Learning, dan Paper

Diperbarui 20 November 2026. Rancangan dasar tetap
`PROGRES-PROYEK-DATA-CENTER-v2-refactor.md`; status di dokumen ini mencerminkan kode
yang diperiksa, bukan janji semua tahap telah selesai.

## Masalah dan kontribusi yang fokus

Masalah praktisnya adalah kesulitan membedakan atap/lahan terbangun dari tanah
terbuka, serta menilai apakah model tersebut tetap andal di lingkungan spasial
yang baru. Perubahan LST menjadi konteks dampak perubahan permukaan, bukan bukti
langsung panas dari komputasi atau jumlah beban AI.

Pertanyaan inti:

1. Bagaimana LST dan indeks permukaan berubah antar tahun dan zona pada dua tapak?
2. Apakah RF/SVM memperbaiki klasifikasi dibanding ambang NDVI/NDBI/MNDWI,
   menggunakan label referensi yang tidak diturunkan dari fitur yang diuji?
3. Bagaimana skor berubah antara pembagian acak, blok spasial, dan uji lintas lokasi?

Judul kerja: **Evaluasi Spasial dan Lintas Lokasi Klasifikasi Tutupan Lahan serta
Dinamika Suhu Permukaan di Sekitar Dua Tapak Pusat Data**. Nama H5 Quincy II tetap
label kerja sampai footprint dipadankan dengan sumber operator dan citra historis.

## Audit implementasi saat ini

| Komponen | Status aktual |
|---|---|
| RF dan SVM, scaling fit pada train, confusion matrix, OA/Kappa/F1 | Ada di `supervised_classification.py` |
| Pembagian train/test | Stratified spatial-group folds pada RF/SVM; leave-site-out tersedia |
| Grid blok | Grid jarak lokal; blok yang terhubung polygon referensi digabung agar tidak bocor antar fold |
| Data label hasil sampling GEE | Fetcher lama tetap pseudo-label; skrip `02_supervised_land_cover.js` mengekspor label referensi pengguna |
| Data lama dan akurasi 100% | Belum layak dijadikan bukti lapangan; metadata asal tidak tersedia dan generator sintetis ada di versi lama |
| Ablasi fitur, Spatial Block CV, cross-site | Pilihan fitur, Spatial CV dan cross-site diimplementasikan; eksekusi data riset menunggu label independen kedua lokasi |
| Regresi nonlinier, SHAP, simulator | Rencana tambahan |

Pembaruan implementasi: lihat [audit klasifikasi](CLASSIFICATION_AUDIT.md) dan
[panduan supervised classification](SUPERVISED_CLASSIFICATION.md). README dan
dashboard kini berbahasa Inggris, dengan instruksi Linux/macOS dan Windows.
Run development Boardman sudah dieksekusi menggunakan data lama yang belum
memiliki provenance; hasilnya bukan bukti akurasi lapangan. Raster inference RF/SVM
dan model pooled sudah tersedia, tetapi peta dua lokasi yang tervalidasi tetap
memerlukan sampel referensi dan ekspor fitur GEE yang sesungguhnya.

Feature importance dari satu model bukan eksperimen ablasi. Akurasi terhadap
pseudo-label yang dibuat dari indeks masukan terutama mengukur peniruan aturan,
bukan validasi tutupan lahan independen. Kelas built-up juga bukan otomatis kelas
data center: jenis penggunaan bangunan memerlukan referensi lain.

## Urutan eksperimen dan kriteria lanjut

### A. Audit data dan label

- Simpan provenance: `site_id`, tanggal/scene, tahun, koordinat, zona, `data_source`,
  metode masking, resolusi, `label_source`, anotator dan ketidakpastian label.
- Pisahkan tabel zonal dari sampel piksel. CSV LST tahunan tidak dapat menggantikan
  sampel berlabel untuk klasifikasi.
- Buat empat kelas: vegetasi/pertanian, terbangun, tanah terbuka, air. Digitasi
  sampel referensi menggunakan citra bertanggal, cek silang dan pisahkan polygon
  label train dari test. Jangan menganggap WorldCover satu tahun sebagai kebenaran
  historis seluruh periode.
- Verifikasi enam poligon Quincy: ada tumpang tindih, sehingga union diperlukan
  sebelum luas dijumlahkan. Jangan menyebutnya enam gedung/data hall terverifikasi.
- Status kronologi: ikuti [audit Quincy](QUINCY_CHRONOLOGY_AUDIT.md). Jangan memilih
  batas waktu hanya karena menghasilkan perubahan suhu terbesar.

### B. Baseline dan ablasi klasifikasi

Gunakan sampel, label, dan fold identik untuk setiap eksperimen:

| Eksperimen | Fitur/model | Tujuan |
|---|---|---|
| Baseline | Aturan NDVI/NDBI/MNDWI | Pembanding sederhana pada label independen |
| Spektral | SR B2–B7; RF dan SVM | Baseline model terbimbing |
| Spektral + indeks | Tambah NDVI/NDBI/MNDWI/albedo | Uji manfaat transformasi DIP |
| Tambah termal | Tambah LST/EMIS | Uji kontribusi termal terhadap klasifikasi |
| Ablasi SWIR | Keluarkan B6/B7 serta indeks turunannya | Uji peran SWIR tanpa menyisakan informasinya melalui indeks |

Bandingkan macro-F1, OA, Kappa, confusion matrix serta precision/recall per kelas.
Tuning RF (`n_estimators`, `max_depth`, `min_samples_leaf`) dan SVM (`C`, `gamma`)
hanya pada fold train, termasuk scaling di dalam pipeline. Gunakan seed tersimpan;
laporkan rentang parameter, jumlah fold dan ketidakpastian antar blok.

### C. Validasi spasial dan transfer

- Random split hanya baseline pembanding; bukan hasil generalisasi utama.
- Bentuk blok pada CRS proyeksi dalam meter, gunakan `GroupKFold` atau pendekatan
  setara dengan kelompok yang terpisah. Ukuran blok/gap dipilih melalui analisis
  ketergantungan spasial dan sensitivitas, bukan sekadar grid derajat 2x2.
- Jangan membagi piksel dari polygon anotasi atau unit termal yang sama ke train
  dan test. Lima fold hanya jika tersedia cukup blok dan kelas di fold pelatihan.
- Setelah parameter dikunci, latih Boardman dan uji Quincy, lalu arah sebaliknya.
  Test lintas lokasi tidak dipakai untuk tuning. Kedua lokasi membutuhkan sampel
  piksel/label sebanding; dua CSV zonal saja belum cukup.

### D. Regresi dan mitigasi sebagai tambahan

Mulai hanya setelah A–C memiliki data dan evaluasi yang dapat dipercaya. Prediksi
LST/LSTanom dengan NDVI, NDBI, albedo, elevasi dan jarak, memakai baseline Ridge
dan RF, RMSE/MAE/R² per blok. Jangan memasukkan LST atau turunan target sebagai
prediktor target yang sama. Definisi referensi regional harus terdokumentasi.

SHAP/permutation importance menjelaskan perilaku prediksi, bukan persentase panas
yang disebabkan server. Mengubah albedo pada model observasional hanya skenario
sensitivitas bersyarat; tidak membuktikan penurunan suhu kausal akibat cool roof.
Penggunaan termal pada klasifikasi juga perlu dianalisis sensitivitasnya sebelum
kelas hasil model dipakai untuk menyimpulkan perbedaan LST.

## Luaran minimum sebelum paper

1. Manifest data dan audit footprint/kronologi kedua lokasi.
2. Grafik tahunan dengan jumlah observasi valid, tabel missing data dan definisi zona.
3. Sampel referensi independen beserta protokol anotasi.
4. Tabel baseline/RF/SVM dan ablasi pada random split serta spatial split.
5. Uji transfer lintas lokasi atau pernyataan jelas mengapa belum dapat dilakukan.
6. Kode konfigurasi/fold/seed dan berkas metrik dengan provenance.

Riset deskriptif yang mengurangi ketidakpastian pengukuran tetap bernilai. Tidak
perlu menambahkan banyak algoritma agar terkesan kompleks. SINTA 2/3 adalah target
seleksi jurnal setelah validitas dan hasil tersedia; dokumentasi ini tidak
menjamin penerimaan dan tidak memverifikasi peringkat jurnal tertentu.

## Struktur paper

Pendahuluan (gap pengukuran dan generalisasi), lokasi/data (status kronologi dan
label), metode DIP, eksperimen ML, hasil dengan ketidakpastian, pembahasan serta
batas validitas. Hindari klaim membantah literatur, memastikan panas AI, atau
mengoptimalkan mitigasi sebelum bukti yang sesuai tersedia.

Sumber metode: [katalog Landsat](https://developers.google.com/earth-engine/datasets/catalog/LANDSAT_LC08_C02_T1_L2),
[validasi scikit-learn](https://scikit-learn.org/stable/modules/cross_validation.html).
