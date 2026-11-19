# Audit Kronologi dan Identitas Footprint Quincy

Tanggal pemeriksaan: 20 November 2026. Status: **belum cukup bukti untuk menetapkan
periode pra/pasca konstruksi pada poligon pengguna**. Jangan mengisi kekosongan ini
dengan periode AWS Boardman.

## Bukti yang diperiksa

| Sumber primer | Informasi yang didukung | Yang tidak dapat disimpulkan |
|---|---|---|
| [Operator H5 Quincy II](https://h5datacenters.com/quincy-II-data-center.html) | Operator memasarkan Quincy II/III bersama, beralamat 1305 Intermodal Way NE; tautan petanya mengarah ke 1500 M Street NE | Penamaan listing tidak menentukan bahwa poligon pengguna tepat sama dengan seluruh kampus |
| [Ecology, dokumen teknis 13 Juli 2017](https://ecology.wa.gov/getattachment/399a8926-5aa6-4cbd-bf04-bf97f41f088f/20170713YahooTechSupport.pdf) | Memisahkan fasilitas Yahoo yang sudah ada dari Project Genesis; permohonan ekspansi 2015 serta perubahan penjadwalan 2017 | Tanggal izin bukan tanggal konstruksi selesai atau operasi semua atap dalam poligon |
| [H5, akuisisi Intuit 18 Juli 2018](https://h5datacenters.com/h5-acquires-quincy-data-center.html) | Akuisisi fasilitas Intuit yang sudah ada | Bukan bukti pembangunan baru Quincy II pada 2018 |

Operator memasarkan kampus II/III dengan cakupan lebih luas daripada metadata
2.93 ha di konfigurasi. Ini tidak membuktikan poligon salah: poligon mungkin
subtapak. Tetapi label seluruh kampus dan batas subtapak tidak boleh dipertukarkan.
Koordinat pengguna sekitar (-119.8253, 47.2476) tetap dipertahankan; tidak digeser
ke titik listing tanpa verifikasi lapangan/citra.

## Keputusan konfigurasi

- `SITES['h5_quincy2']['pre_years'] = None` dan `post_years = None`.
- Analisis tahunan tetap diperbolehkan. `fetch_epoch_composites()` menolak Quincy
  sampai konfigurasi periode terisi berdasarkan bukti.
- Boardman mempertahankan 2019–2021/2025–2026 sebagai **asumsi lama**, bukan
  kronologi yang diperiksa ulang dalam audit ini.
- Kandidat kontrol Quincy (-119.8550, 47.2340) belum dipastikan sebagai lokasi
  industri non-DC dengan histori dan tutupan lahan sebanding.
- Enam feature atap adalah enam anotasi, bukan enam gedung terverifikasi; beberapa
  poligon saling tumpang tindih dan harus di-union untuk menghitung luas.

## Bukti yang masih diperlukan

1. Cocokkan footprint dengan batas persil, alamat operator dan bentuk atap pada
   citra resolusi tinggi bertanggal. Simpan sumber/tanggal dan tangkapan layar.
2. Susun urutan citra sebelum pembukaan lahan, konstruksi, atap selesai, serta
   sesudahnya. Catat per gedung bila pembangunan bertahap.
3. Cocokkan ke site plan/izin yang mencakup lokasi yang sama. Pisahkan tanggal
   permohonan, persetujuan, instalasi generator, selesai bangunan dan operasi.
4. Pilih tahun pra dengan tapak belum berubah dan pasca setelah konstruksi selesai,
   cukup observasi, serta musim setara. Keluarkan tahun transisi.
5. Bila fasilitas lama telah ada sebelum 2013, Landsat 8/9 tidak menyediakan
   baseline sebelum pembangunan awal. Ubah pertanyaan menjadi perubahan selama
   operasi/ekspansi, atau rancang analisis Landsat 5/7 dengan harmonisasi sensor.

Perubahan NDVI/LST sekitar 2015–2016 pada grafik pengguna adalah petunjuk yang
perlu diperiksa, bukan bukti tanggal pembangunan. Belum dilakukan analisis ulang
citra historis atau audit geodesik luas dalam pembaruan ini.

Setelah bukti tersedia, isi periode spesifik Quincy di `config.py`, simpan daftar
sumber dan versi, lalu ekspor ulang hasil pra/pasca. Jangan mengubah tanggal hanya
agar cocok dengan dugaan kenaikan suhu.
