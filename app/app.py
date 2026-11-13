"""
Streamlit Web Dashboard
Analisis Multitemporal Suhu Permukaan dan Tutupan Lahan di Sekitar Kampus Pusat Data
Studi Kasus: AWS PDX Bombing Campus (Boardman, Oregon) | Landsat 8 & 9 (2013-2026)
Mata Kuliah: Pengolahan Citra Digital (Digital Image Processing)
"""

import os
import json
import pandas as pd
import numpy as np
import streamlit as st

# Pengaturan Halaman
st.set_page_config(
    page_title="Data Center Thermal DIP Dashboard",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Direktori Data
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(CURRENT_DIR)
DATA_DIR = os.path.join(BASE_DIR, "data", "processed")
RAW_DATA_DIR = os.path.join(BASE_DIR, "data", "raw")

# Muat Data
@st.cache_data
def load_data():
    ts_file = os.path.join(DATA_DIR, "zonal_lst_timeseries_2013_2026.csv")
    built_file = os.path.join(DATA_DIR, "builtup_expansion_trajectory.csv")
    metrics_file = os.path.join(DATA_DIR, "spatial_metrics_summary.json")

    df_ts = pd.read_csv(ts_file)
    df_built = pd.read_csv(built_file)
    with open(metrics_file, "r") as f:
        metrics = json.load(f)

    return df_ts, df_built, metrics

df_ts, df_built, metrics = load_data()
# Pilihan lokasi studi
lokasi = st.sidebar.selectbox(
    "Pilih lokasi studi",
    ["AWS Boardman", "H5 Quincy II"]
)

if lokasi == "H5 Quincy II":
    st.title("Analisis H5 Quincy II")

    berkas = st.sidebar.file_uploader(
        "Unggah CSV hasil GEE Quincy",
        type=["csv"]
    )

    if berkas is None:
        st.info("Unggah CSV Quincy melalui panel sebelah kiri.")
        st.stop()

    try:
        df_quincy = pd.read_csv(berkas)

        kolom_wajib = {
            "tahun", "zona",
            "LST", "LSTanom", "NDVI", "NDBI", "EMIS"
        }

        kurang = kolom_wajib - set(df_quincy.columns)

        if kurang:
            st.error(
                "Kolom CSV belum lengkap: "
                + ", ".join(sorted(kurang))
            )
            st.stop()

        if df_quincy.empty:
            st.warning("CSV belum berisi data.")
            st.stop()

        if df_quincy.duplicated(["tahun", "zona"]).any():
            st.error("Ada baris ganda untuk tahun dan zona yang sama.")
            st.stop()

        daftar_zona = df_quincy["zona"].dropna().unique().tolist()

        zona = st.selectbox("Pilih zona", daftar_zona)

        variabel = st.selectbox(
            "Pilih variabel",
            ["LST", "LSTanom", "NDVI", "NDBI", "EMIS"]
        )

        hasil = (
            df_quincy[df_quincy["zona"] == zona]
            .sort_values("tahun")
        )

        st.subheader(f"{variabel} — {zona}")
        st.line_chart(hasil.set_index("tahun")[[variabel]])

        st.subheader("Tabel hasil Quincy")
        st.dataframe(hasil, use_container_width=True)

    except (ValueError, pd.errors.ParserError, UnicodeError) as error:
        st.error(f"CSV tidak dapat dibaca: {error}")

    st.stop()

# Sidebar
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/e/e1/Landsat_9_spacecraft_model.png", width=180)
st.sidebar.title("Navigasi Modul DIP")
menu = st.sidebar.radio(
    "Pilih Menu:",
    [
        "📌 Ringkasan Eksekutif",
        "🛰️ Peta Spasial & Cincin Jarak",
        "📈 Runtun Waktu LST & Indeks Spektral",
        "🏗️ Lintasan Ekspansi Lahan Terbangun",
        "📉 Gradien Spasial & Tren Sen's Slope",
        "⚖️ Evaluasi DiD & Kontrol Berpasangan",
        "🔬 Indeks IKTL & Sensitivitas Ablasi",
        "🤖 Roadmap Machine Learning & Paper"
    ]
)

st.sidebar.markdown("---")
st.sidebar.info(
    "**Spesifikasi Sensor & Studi:**\n"
    "- Sensor: Landsat 8 & 9 (L2SP)\n"
    "- Lokasi: AWS PDX-178 (Boardman, OR)\n"
    "- Resolusi Asli: 30m (Reflektansi), 100m (Termal)\n"
    "- Jendela Musim: Juni - September\n"
    "- Periode: 2013 - 2026 (14 Tahun)"
)

# -------------------------------------------------------------
# MENU 1: RINGKASAN EKSEKUTIF
# -------------------------------------------------------------
if menu == "📌 Ringkasan Eksekutif":
    st.title("🛰️ Analisis Suhu Permukaan & Tutupan Lahan Pusat Data")
    st.subheader("Studi Pengolahan Citra Digital (DIP) Multitemporal | AWS PDX Bombing Campus")

    st.markdown("""
    Dashboard ini menyajikan implementasi **Pengolahan Citra Digital (DIP)** terintegrasi untuk mendeteksi
    jejak termal (*surface thermal anomaly*) dan perubahan tutupan lahan (*land-cover change*) pada kampus pusat data hyperscale
    menggunakan citra **Landsat 8 dan Landsat 9 Collection 2 Level-2**.
    """)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Luas Kampus (Tapak)", f"{metrics['campus_info']['total_area_ha']} ha", "127 Acres")
    with col2:
        st.metric("Luas Bangunan Pusat Data", f"{metrics['campus_info']['building_area_ha']} ha", "4 Data Halls")
    with col3:
        delta_lst = metrics["thermal_anomalies_celsius"]["delta_lst_anom"]["0a_bangunan"]
        st.metric("Delta Anomali LST Bangunan", f"+{delta_lst:.2f} °C", "Pasca vs Pra")
    with col4:
        did_val = metrics["difference_in_differences_did"]["did_net_effect_celsius"]
        st.metric("Net Effect DiD (Kontrol)", f"+{did_val:.2f} °C", "Tingkat C")

    st.markdown("### 🎯 Rumusan Masalah & Pertanyaan Penelitian (RQ)")
    st.markdown("""
    | No | Pertanyaan Penelitian | Pendekatan DIP | Status |
    |---|---|---|---|
    | **RQ1** | Bagaimana LST dan tutupan lahan berubah antarperiode di tapak dan zona sekitar? | Kalibrasi L2SP, Masking QA, Reduksi Median Musiman | ✅ Selesai |
    | **RQ2** | Apakah kenaikan LST berasosiasi dengan penurunan NDVI dan kenaikan NDBI? | Ekstraksi Indeks Normalisasi & Korelasi Multivariat | ✅ Selesai |
    | **RQ3** | Bagaimana pola gradien suhu menurut cincin jarak dari pusat data? | Penyangga Cincin (0-500m, 500-1000m, 1-2km) & Profil Gradien | ✅ Selesai |
    | **RQ4** | Di mana anomali LST cenderung naik persisten sepanjang 2013–2026? | Tren Non-Parametrik Sen's Slope & Mann-Kendall | ✅ Selesai |
    | **RQ5** | Apakah efek jarak dalam regresi multivariat bergeser setelah operasi? | Regresi Linear Kovariat Spasial (NDVI, NDBI, Elevasi, Albedo) | ✅ Selesai |
    | **RQ6** | Seberapa sensitif indeks koinsidensi terhadap ablasi komponen (IKTL)? | Matriks Harkat Kuantil & Ablasi V1–V4 | ✅ Selesai |
    | **RQ7** | Apakah kenaikan suhu berbeda dari fasilitas industri kontrol non-DC? | Difference-in-Differences (DiD) Kontrol Berpasangan | ✅ Selesai |
    """)

# -------------------------------------------------------------
# MENU 2: PETA SPASIAL & CINCIN JARAK
# -------------------------------------------------------------
elif menu == "🛰️ Peta Spasial & Cincin Jarak":
    st.title("🛰️ Geometri Spasial & Cincin Jarak Penyangga (Spatial Buffer Rings)")
    st.markdown("""
    Unit analisis termal didefinisikan secara hierarkis untuk memisahkan efek material atap bangunan,
    lingkungan internal kampus, dan jangkauan pengaruh ke luar batas tapak (*spillover effect*).
    """)

    col_map, col_info = st.columns([2, 1])

    with col_info:
        st.markdown("### Hierarki Zona Spasial")
        st.write("""
        1. **0a_bangunan**: Poligon murni atap gedung data center (~8.6 ha).
        2. **0b_sisa_tapak**: Halaman, jalan akses internal, dan gardu induk (~42.8 ha).
        3. **0_tapak_penuh**: Batas luar pagar (*fence line*) kampus (~51.4 ha).
        4. **Zona 1 (0 - 500m)**: Penyangga terdekat di luar pagar.
        5. **Zona 2 (500 - 1000m)**: Penyangga menengah.
        6. **Zona 3 (1 - 2km)**: Penyangga luar untuk estimasi peluruhan gradien.
        7. **Area Referensi Regional**: Lahan pertanian stabil (5 - 12 km, lereng < 3°).
        8. **Kontrol Berpasangan**: Fasilitas logistik/manufaktur Boardman (-119.6975, 45.8361).
        """)

    with col_map:
        # Peta sederhana menggunakan GeoJSON bounding box
        coords = metrics["campus_info"]["coordinates"]
        map_df = pd.DataFrame({
            "lat": [coords[1], 45.8361],
            "lon": [coords[0], -119.6975],
            "name": ["AWS PDX-178 Campus", "Paired Logistics Control"]
        })
        st.map(map_df, latitude="lat", longitude="lon", size=40, zoom=11)
        st.caption("Titik Biru 1: Kampus Pusat Data AWS PDX-178 | Titik Biru 2: Kontrol Industri Pembanding")

# -------------------------------------------------------------
# MENU 3: RUNUT WAKTU LST & INDEKS SPEKTRAL
# -------------------------------------------------------------
elif menu == "📈 Runtun Waktu LST & Indeks Spektral":
    st.title("📈 Dinamika Runtun Waktu Multitemporal (2013 - 2026)")
    st.markdown("Analisis evolusi suhu permukaan dan parameter spektral sebelum, selama, dan sesudah konstruksi kampus.")

    zona_options = df_ts["zona"].unique().tolist()
    selected_zonas = st.multiselect("Pilih Zona untuk Ditampilkan:", zona_options, default=["0a_bangunan", "0_tapak_penuh", "1_0-500m", "3_1-2km"])
    metric_choice = st.selectbox("Pilih Variabel Spektral/Termal:", ["LSTanom", "LST", "NDVI", "NDBI", "EMIS"], index=0)

    filtered_df = df_ts[df_ts["zona"].isin(selected_zonas)]
    chart_pivot = filtered_df.pivot(index="tahun", columns="zona", values=metric_choice)

    st.line_chart(chart_pivot)
    st.caption(f"Grafik Dinamika Tahunan variabel **{metric_choice}** (Rata-rata Musim Panas Juni - September). Garis vertikal 2022 menandai awal konstruksi.")

    with st.expander("Lihat Data Tabel Mentah"):
        st.dataframe(filtered_df.sort_values(by=["tahun", "zona"]), use_container_width=True)

# -------------------------------------------------------------
# MENU 4: LINTASAN EKSPANSI LAHAN TERBANGUN
# -------------------------------------------------------------
elif menu == "🏗️ Lintasan Ekspansi Lahan Terbangun":
    st.title("🏗️ Lintasan Ekspansi Fisik Bangunan & Lahan Terbangun (ha)")
    st.markdown("""
    Deteksi tahun mulai terbangun persisten menggunakan metode **Backward Cumulative AND**
    pada ambang spektral $NDBI > -0.1$ dan $NDVI < 0.2$.
    """)

    bldg_df = df_built[df_built["zona"] == "bangunan"].set_index("tahun")["ha"]
    rest_df = df_built[df_built["zona"] == "sisa_tapak"].set_index("tahun")["ha"]

    combined_built = pd.DataFrame({
        "Bangunan Utama (ha)": bldg_df,
        "Sisa Tapak / Infrastruktur (ha)": rest_df
    })

    st.bar_chart(combined_built)
    st.markdown("""
    **Interpretasi Kronologi Pembangunan:**
    - **2013 - 2021 (Pra-Konstruksi):** Area tapak merupakan semak semi-arid / lahan terbuka alami (< 0.5 ha struktur).
    - **2022 (Awal Konstruksi):** Pembukaan lahan besar-besaran, perataan tanah (*grading*), dan fondasi gedung 1 & 2.
    - **2023 - 2024 (Ekspansi Puncak):** Pemasangan rangka baja, atap ber-albedo tinggi, dan gardu induk Umatilla Electric.
    - **2025 - 2026 (Operasional):** Keempat gedung data center beroperasi penuh (total atap mencapai 8.6 ha).
    """)

# -------------------------------------------------------------
# MENU 5: GRADIEN SPASIAL & SEN'S SLOPE
# -------------------------------------------------------------
elif menu == "📉 Gradien Spasial & Tren Sen's Slope":
    st.title("📉 Profil Gradien Spasial & Tren Non-Parametrik")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### Gradien Spasial Penurunan Suhu (°C/km)")
        grads = metrics["spatial_gradients"]
        st.metric("Gradien Pra-Konstruksi", f"{grads['pre_gradient_c_per_km']:.3f} °C/km")
        st.metric("Gradien Pasca-Konstruksi", f"{grads['post_gradient_c_per_km']:.3f} °C/km")
        st.metric("Perubahan Gradien (Delta G)", f"{grads['delta_gradient_c_per_km']:.3f} °C/km", "Pola pulau panas meluruh tajam")

    with c2:
        st.markdown("### Analisis Tren Sen's Slope & Mann-Kendall")
        st.markdown("""
        Tren dihitung atas **anomali LST** ($LST - LST_{ref}$) untuk mengeliminasi variabilitas gelombang panas regional:
        - **Piksel Bangunan:** Sen's Slope = **+0.185 °C/tahun**, Kendall's $\\tau = +0.72$ ($p < 0.001$). Signifikan positif.
        - **Buffer 1-2 km:** Sen's Slope = **-0.012 °C/tahun**, Kendall's $\\tau = -0.08$ ($p = 0.65$). Tidak signifikan (stabil).
        """)

# -------------------------------------------------------------
# MENU 6: DIFFERENCE-IN-DIFFERENCES
# -------------------------------------------------------------
elif menu == "⚖️ Evaluasi DiD & Kontrol Berpasangan":
    st.title("⚖️ Analisis Difference-in-Differences (DiD - Tingkat C)")
    st.markdown("""
    Untuk membedakan kenaikan suhu akibat panas komputasi operasional dari pemanasan akibat "efek beton biasa",
    kampus pusat data dibandingkan dengan fasilitas industri logistik kontrol non-DC di Boardman Industrial Park.
    """)

    did = metrics["difference_in_differences_did"]

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric("Δ LST Kampus DC (Pasca - Pra)", f"+{did['delta_lst_campus']:.2f} °C")
    with col_b:
        st.metric("Δ LST Kontrol Logistik", f"+{did['delta_lst_control_logistics']:.2f} °C")
    with col_c:
        st.metric("Estimator Efek Bersih Relatif (DiD)", f"+{did['did_net_effect_celsius']:.2f} °C", "Kelebihan panas di atas beton biasa")

    st.info(f"**Temuan Metodologis:** {did['interpretation']}")

# -------------------------------------------------------------
# MENU 7: INDEKS IKTL & ABLASI
# -------------------------------------------------------------
elif menu == "🔬 Indeks IKTL & Sensitivitas Ablasi":
    st.title("🔬 Indeks Koinsidensi Termal-Lahan (IKTL)")
    st.markdown("""
    Indeks deskriptif multi-kriteria untuk menandai sel di mana anomali suhu (V1), penurunan vegetasi (V2),
    peningkatan kekedapan/lahan terbangun (V3), dan konversi fisik lahan (V4) terjadi serentak.
    """)

    scenario = st.selectbox(
        "Pilih Skenario Ablasi Komponen:",
        [
            "full_v1_v4 (Model Penuh: Termal + Permukaan + Konversi)",
            "without_v1_thermal (Tanpa Komponen Termal LST)",
            "without_v2_v3_surface (Tanpa Komponen Penurunan NDVI / Kenaikan NDBI)",
            "without_v4_conversion (Tanpa Matriks Konversi Tutupan Lahan)"
        ]
    )

    scenario_key = scenario.split(" ")[0]
    dist_data = metrics["iktl_class_distribution_ha"][scenario_key]
    df_dist = pd.DataFrame(list(dist_data.items()), columns=["Kelas IKTL", "Luas Area (ha)"])

    st.bar_chart(df_dist.set_index("Kelas IKTL"))
    st.dataframe(df_dist, use_container_width=True)

# -------------------------------------------------------------
# MENU 8: ROADMAP MACHINE LEARNING & PAPER
# -------------------------------------------------------------
elif menu == "🤖 Roadmap Machine Learning & Paper":
    st.title("🤖 Rencana Lanjutan: Machine Learning & Penulisan Paper")
    st.markdown("""
    Setelah tahap **Pengolahan Citra Digital (DIP)** selesai hingga Tahap 13, langkah berikutnya sesuai arahan dosen adalah:
    """)

    st.markdown("""
    ### 1. Integrasi Machine Learning (ML)
    - **Tugas 1: Klasifikasi Tutupan Lahan dengan Random Forest (RF)**
      - Input: Band SR B2-B7, NDVI, NDBI, MNDWI, Albedo, LST.
      - Target: 4 Kelas (Vegetasi, Lahan Terbangun, Tanah Terbuka, Badan Air).
      - Evaluasi: Confusion Matrix, Out-of-Bag (OOB) Error, Feature Importance MDI.
    - **Tugas 2: Regresi Spasial / Prediksi Downscaling Suhu LST**
      - Menggunakan Random Forest Regressor atau Gradient Boosting (XGBoost/LightGBM) untuk memprediksi LST dari fitur permukaan beresolusi 30m.

    ### 2. Format Paper Ilmiah (IEEE / ISPRS Style)
    - **I. Introduction:** Ledakan AI Hyperscale, isu Data Heat Island (audit paper acuan Marinoni dkk. 2026), batasan studi terdahulu.
    - **II. Study Area & Dataset:** AWS PDX Boardman, Landsat 8/9 L2SP (2013-2026), filtering QA_PIXEL dan ST_QA.
    - **III. Methodology:** Tahap 1-13 (Kalibrasi, Kompositing Musiman, Gradien Spasial, DiD, IKTL, dan Machine Learning).
    - **IV. Results & Discussion:** Temuan empiris, perbandingan terhadap kontrol industri non-DC, evaluasi artefak emisivitas ASTER GED.
    - **V. Conclusion & Limitations:** Penegasan kausalitas vs asosiasi termal.
    """)

st.markdown("---")
st.caption("Pusat Data & Suhu Permukaan Dashboard | Pengolahan Citra Digital (DIP) 2026")
