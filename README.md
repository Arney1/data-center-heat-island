# Suhu Permukaan dan Tutupan Lahan di Sekitar Dua Pusat Data

Proyek Pengolahan Citra Digital (DIP) dan Machine Learning menggunakan Landsat 8/9
Collection 2 Level-2, dengan jendela Juni–September 2013–2026. Dua lokasi yang
dikonfigurasi adalah AWS PDX Boardman (`aws_pdx`) dan kandidat H5 Quincy II
(`h5_quincy2`). Pembaruan dokumentasi: **20 November 2026**.

**Pertanyaan utama:** bagaimana perubahan tutupan lahan berasosiasi dengan LST,
dan seberapa baik model tutupan lahan bekerja ketika diuji pada blok spasial serta
lokasi yang tidak digunakan untuk pelatihan? Pengamatan ini tidak langsung
mengukur panas buangan server atau dampak kausal operasi pusat data.

## Status yang dapat dipertanggungjawabkan

| Komponen | Tersedia | Batas klaim |
|---|---|---|
| Boardman | Geometri, CSV/JSON tersimpan, dashboard modul DIP | Angka tersimpan belum diaudit ulang dari citra dalam pembaruan ini |
| Quincy | Geometri pengguna, unggahan CSV seri waktu, peta | Pengguna sudah sampai grafik LST; identitas footprint dan tanggal konstruksi masih harus dicocokkan |
| Fetcher Python | Pra-pemrosesan, komposit tahunan, sampling fitur | Memerlukan akun/proyek GEE untuk data langsung; berbeda dengan sekadar membuka dashboard |
| RF dan SVM | Implementasi klasifikasi, metrik serta dataset lama | Evaluasi menggunakan pembagian acak; asal data lama belum memiliki metadata sumber |
| Blok spasial | Fungsi pembentukan ID grid | Belum terhubung ke evaluasi model; belum ada hasil Spatial Block CV |
| Transfer lintas lokasi, regresi ML, SHAP, simulator | Rancangan eksperimen | Belum diimplementasikan/divalidasi |

Dataset fitur lama tidak memuat metadata asal. Fetcher lama dapat membangkitkan data
sintetis secara otomatis saat GEE gagal. Karena itu, akurasi 100% dalam JSON lama
tidak boleh dilaporkan sebagai akurasi lapangan. Sampling langsung saat ini juga
menghasilkan **pseudo-label dari indeks spektral**, bukan label referensi independen.

## Lokasi dan periode

| Parameter | Boardman | Quincy |
|---|---|---|
| ID | `aws_pdx` | `h5_quincy2` |
| Titik konfigurasi (longitude, latitude) | (-119.6334, 45.8194) | (-119.8253, 47.2476) |
| Poligon atap masukan | 4 | 6; beberapa tumpang tindih, bukan bukti jumlah data hall |
| Pra/pasca | 2019–2021 / 2025–2026, asumsi lama yang perlu bukti | Belum ditetapkan; tidak mewarisi periode Boardman |
| Kontrol industri | Kandidat konfigurasi | Kandidat konfigurasi; kesesuaian belum diverifikasi |

Angka luas yang ada dalam konfigurasi merupakan metadata lama, bukan perhitungan
ulang geodesik. Luas tapak digitasi juga tidak otomatis sama dengan luas kampus
yang dipasarkan operator. [Audit Quincy](docs/QUINCY_CHRONOLOGY_AUDIT.md)
memisahkan fasilitas lama, ekspansi, dan pergantian pemilik.

## Instalasi dan menjalankan dashboard

Dari direktori proyek, pada PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app/app.py
```

Jika `.venv` sudah tersedia, lewati pembuatannya. Pilih **AWS Boardman** untuk
dashboard lama atau **H5 Quincy II** untuk peta dan seri waktu Quincy. Pada Quincy,
unggah CSV hasil GEE, atau simpan sebagai `data/processed/h5_quincy2_timeseries.csv`.
Kolom wajib: `tahun,zona,LST,LSTanom,NDVI,NDBI,EMIS`. Kolom identitas opsional harus
bernilai `site_id=h5_quincy2`; setiap pasangan tahun/zona harus unik. Data null
tetap null; jangan diganti nol. Grafik dan statistik berubah sesuai zona/variabel.

Dashboard tidak menghitung seluruh modul DIP Quincy hanya dari CSV seri waktu.
CSV tersebut tidak mengandung luas geometri, citra piksel, label validasi, DiD,
atau distribusi IKTL. Lihat [langkah setelah LST](docs/QUINCY_NEXT_STEPS.md).

## Pengambilan data GEE dan keamanan lokasi

```powershell
.\.venv\Scripts\earthengine.exe authenticate
$env:EE_PROJECT='ID_PROYEK_GEE_ANDA'
```

Proyek tersebut harus sudah diaktifkan untuk Earth Engine. Jangan menyimpan token
atau kredensial ke Git. Contoh Python:

```python
from dip_pipeline.gee_fetcher import GEEDataFetcher

fetcher = GEEDataFetcher(site_id="h5_quincy2")
annual = fetcher.fetch_live_zonal_timeseries()
```

Saat offline, Boardman membaca cache lama `zonal_lst_timeseries_2013_2026.csv`;
Quincy hanya membaca `h5_quincy2_timeseries.csv`. Cache Quincy tidak tersedia berarti
error, bukan mengambil hasil Boardman. Perbandingan epoch Quincy sengaja ditolak
sampai `pre_years` dan `post_years` ditetapkan dengan bukti.

Sampling fitur langsung menulis `ml_feature_dataset_<site_id>.csv`. Jika GEE tidak
tersedia/gagal, operasi berhenti. Data demo harus diminta secara eksplisit:

```python
demo = fetcher.extract_ml_feature_dataset(allow_synthetic=True)
# Menulis ml_feature_dataset_h5_quincy2_synthetic.csv, data_source=synthetic_demo.
```

Demo hanya untuk memeriksa alur perangkat lunak. Runner ML lama masih membaca
`ml_feature_dataset.csv` dan bukan otomatis melatih kedua lokasi. Jangan mengganti
file itu dengan data demo untuk mengklaim hasil penelitian.

## Struktur proyek dan validasi

- `dip_pipeline/config.py`: geometri, parameter, status kronologi per lokasi.
- `dip_pipeline/gee_fetcher.py`: akses GEE dan fallback cache yang sesuai lokasi.
- `dip_pipeline/ml/`: klasifikasi RF/SVM dan pemisahan acak; evaluasi spasial masih rencana.
- `gee_scripts/01_full_analysis_aws_pdx.js`: skrip JavaScript lama, khusus Boardman.
- `app/app.py`: dashboard dua lokasi.
- `data/processed/`: artefak lama; jangan menganggap semuanya berasal dari GEE langsung.
- `docs/`: metodologi, audit kronologi dan urutan kerja berikutnya.
- `PROGRES-PROYEK-DATA-CENTER-v2-refactor.md`: rancangan penelitian awal, bukan laporan penyelesaian terbaru.

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

`python -m dip_pipeline.runner` hanya membaca artefak dan mencetak ringkasan;
pesan keberhasilannya tidak menggantikan audit citra. `python -m
dip_pipeline.ml.runner_ml` melatih dan menimpa metrik klasifikasi lama; jalankan
hanya setelah asal dataset dipahami. Pembaruan ini tidak menjalankan ulang kedua runner.

## Riset dan publikasi

Prioritas eksperimen adalah klasifikasi tutupan lahan: baseline ambang, RF/SVM,
ablasi fitur, label independen dan evaluasi spasial. Regresi dan simulasi mitigasi
menjadi tambahan setelah dasar data valid. Analisis deskriptif dapat menjadi
kontribusi ilmiah; tidak wajib membuat simulator untuk dianggap berguna.

SINTA 2/3 adalah target, bukan jaminan kelayakan atau penerimaan. Jangan menyebut
penelitian membantah literatur sebelum ada eksperimen dan ketidakpastian yang
memadai. [Roadmap](docs/ML_AND_PAPER_ROADMAP.md) menjelaskan ruang lingkup fokus.

## Sumber teknis

- [Katalog Landsat C2 L2](https://developers.google.com/earth-engine/datasets/catalog/LANDSAT_LC08_C02_T1_L2): skala band, masking dan batas produk.
- [USGS Landsat 8](https://www.usgs.gov/landsat-missions/landsat-8): termal asli 100 m; kisi produk 30 m tidak memberikan observasi termal independen 30 m.
- [Validasi berkelompok scikit-learn](https://scikit-learn.org/stable/modules/cross_validation.html): pemisahan kelompok pelatihan/pengujian.
- [Operator H5 Quincy II/III](https://h5datacenters.com/quincy-II-data-center.html) dan [dokumen Ecology 13 Juli 2017](https://ecology.wa.gov/getattachment/399a8926-5aa6-4cbd-bf04-bf97f41f088f/20170713YahooTechSupport.pdf): konteks lokasi dan ekspansi, bukan penanggalan pasti footprint pengguna.
