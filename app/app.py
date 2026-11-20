"""Consistent two-site dashboard for LST, land cover, and audited results."""
import json
import sys
from pathlib import Path

import folium
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_folium import st_folium

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
from dip_pipeline.config import SITES
from dip_pipeline.timeseries import load_zonal_timeseries

DATA_DIR = BASE_DIR / "data" / "processed"
st.set_page_config(page_title="Data Center LST & Land Cover", page_icon="🛰️", layout="wide")
SITE_LABELS = {"aws_pdx": "AWS Boardman", "h5_quincy2": "H5 Quincy II"}
site_id = st.sidebar.selectbox("Study site", list(SITE_LABELS), format_func=SITE_LABELS.get)
site = SITES[site_id]
page = st.sidebar.radio("Explore", ["Overview", "Study area", "LST & spectral time series",
                                    "Supervised classification", "Saved DIP artifacts"])
st.sidebar.caption("Landsat 8/9 Collection 2 Level-2 • June–September • 2013–2026")
st.sidebar.caption("30 m optical grid; thermal measurements originate at 100 m.")
st.title(f"{SITE_LABELS[site_id]} — LST & Land Cover")


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def read_timeseries():
    uploaded = st.sidebar.file_uploader("Upload this site's GEE time-series CSV", type="csv", key=f"ts_{site_id}")
    filename = ("zonal_lst_timeseries_2013_2026.csv" if site_id == "aws_pdx"
                else "h5_quincy2_timeseries.csv")
    source = uploaded if uploaded is not None else DATA_DIR / filename
    if uploaded is None and not source.exists():
        return None
    try:
        return load_zonal_timeseries(source, site_id)
    except (ValueError, OSError, UnicodeError) as error:
        st.error(f"The time-series CSV could not be loaded: {error}")
        return None


def site_map():
    lon, lat = site["campus_centroid"]
    result = folium.Map(location=[lat, lon], zoom_start=14, tiles="OpenStreetMap")
    folium.Polygon([[p[1], p[0]] for p in site["campus_bounds"]],
                   color="cyan", weight=3, tooltip="Digitized campus boundary").add_to(result)
    for i, ring in enumerate(site["buildings_multipolygon"]):
        folium.Polygon([[p[1], p[0]] for p in ring], color="red", fill=True,
                       fill_opacity=0.3, tooltip=f"Roof annotation {i + 1}").add_to(result)
    return result


def show_scores(scores):
    rows = [{"Model": name, "Overall accuracy": values["overall_accuracy"],
             "Macro F1": values["macro_f1"], "Cohen's kappa": values["cohen_kappa"]}
            for name, values in scores.items()]
    st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
    model = st.selectbox("Model details", list(scores))
    values = scores[model]
    matrix = pd.DataFrame(values["confusion_matrix"], index=values["labels"], columns=values["labels"])
    st.plotly_chart(px.imshow(matrix, text_auto=True, color_continuous_scale="Blues",
                             labels={"x": "Predicted class", "y": "Reference class", "color": "Samples"}),
                    width="stretch")
    st.dataframe(pd.DataFrame(values["per_class"]), hide_index=True, width="stretch")


if page == "Overview":
    st.write("Explore surface temperature and land cover at two data-center study sites using the same navigation.")
    st.write(f"**Location:** {site['location']}")
    st.write(f"**Digitized roof polygons:** {len(site['buildings_multipolygon'])}")
    st.caption("Roof annotations can overlap; annotation count is not a verified count of data halls. See the geometry audit for measured polygon areas; these do not verify facility parcels.")
    st.info("Classification assigns vegetation, built-up land, bare soil, or water to pixels throughout each campus and its 2.5 km surroundings. It does not identify whether a building is a data center.")
    st.write("A pooled model can learn from both sites. Each site's map and evaluation remain identifiable, and leave-site-out tests measure transfer to the other site.")
    st.info("Research accuracy requires independent, dated reference labels. Development-only runs and legacy scores are not verified field accuracy.")
    st.write(f"**Construction chronology:** {site['chronology_status'].replace('_', ' ')}.")
    st.caption("LST is surface temperature. Observed differences do not directly measure server heat or establish a causal effect of operations.")

elif page == "Study area":
    st_folium(site_map(), height=520, use_container_width=True, key=f"geometry_{site_id}")
    st.caption("Cyan: digitized campus. Red: roof annotations. These are the configured study footprints; their identity and chronology still need verification.")
    st.write("Analysis zones: campus, roofs, campus excluding roofs, 0–500 m, 500–1,000 m, and 1–2 km from the campus edge. The classification AOI extends 2.5 km from that edge.")
    st.caption("The regional reference and industrial control require separate suitability checks. No construction-period comparison is inferred from this map.")

elif page == "LST & spectral time series":
    frame = read_timeseries()
    if frame is None:
        st.info("No usable time series is available for this site. Upload its GEE CSV in the sidebar.")
    else:
        if site_id == "aws_pdx":
            st.caption("Boardman data are stored legacy results; image-level provenance has not been revalidated.")
        st.caption("An uploaded CSV without site_id is assigned to the selected site. Check its origin before uploading.")
        zones = frame.zona.unique().tolist()
        selected = st.multiselect("Zones", zones, default=["0_tapak_penuh"] if "0_tapak_penuh" in zones else zones[:1])
        variable = st.selectbox("Variable", ["LST", "LSTanom", "NDVI", "NDBI", "EMIS"])
        view = frame[frame.zona.isin(selected)]
        if not view.empty:
            st.line_chart(view.pivot(index="tahun", columns="zona", values=variable))
            stats = view.groupby("zona")[variable].agg(["count", "mean", "min", "max"])
            st.dataframe(stats, width="stretch")
            st.caption("Statistics summarize available annual zone means. Missing values remain missing; LST/LSTanom use °C. Anomalies depend on a suitable regional reference.")
            st.dataframe(view, hide_index=True, width="stretch")
            st.download_button("Download selected time series", view.to_csv(index=False),
                               file_name=f"{site_id}_timeseries.csv", mime="text/csv")

elif page == "Supervised classification":
    st.write("Classes: vegetation/agriculture, built-up land, bare soil/fallow, and water.")
    st.caption("Models cover the full AOI of each selected site. A pooled run uses both AOIs, not the land between the cities.")
    runs = []
    for path in sorted((DATA_DIR / "classification").glob("*/metrics.json")):
        try:
            result = read_json(path)
            if result.get("schema_version") == 2 and site_id in result.get("site_ids", []):
                runs.append((path, result))
        except (ValueError, OSError):
            st.warning(f"A saved classification run could not be read: {path.parent.name}")
    if not runs:
        st.info("No classification run is available for this site. Reference-label collection is the next step; an LST zone-average CSV cannot train a pixel classifier.")
        st.write("See the README and supervised-classification guide for drawing reference areas in GEE, exporting labeled pixels, and running RF/SVM.")
    else:
        selected_run = st.selectbox("Saved run", range(len(runs)), format_func=lambda i: runs[i][0].parent.name)
        path, report = runs[selected_run]
        if report["claim_status"] == "development_only":
            st.warning("DEVELOPMENT ONLY — source metadata or independent labels are missing. Scores below are software-check results, not verified land-cover accuracy.")
        else:
            st.info("Scores use spatially held-out reference labels. Label interpretation and sampling representativeness still require review.")
        st.write(f"**Validation:** {report['validation']} · **Evaluated samples:** {report['n_evaluated_samples']} · **Folds:** {report['n_folds']}")
        scores = report.get("per_site_performance", {}).get(site_id)
        if scores:
            st.caption(f"Held-out scores for {SITE_LABELS[site_id]}; run-wide results are available in the report download.")
            # Baseline site scores are optional for older schema-v2 artifacts.
            show_scores(scores)
        else:
            st.info("This site was used for training only in this transfer run; no held-out score is available for it.")
        predictions_path = path.parent / "heldout_predictions.csv"
        if predictions_path.exists():
            predictions = pd.read_csv(predictions_path)
            pixels = predictions[predictions.site_id.eq(site_id) & predictions.fold.ge(0)]
            with st.expander("Held-out sample predictions"):
                st.dataframe(pixels.head(1000), hide_index=True, width="stretch")
                if not pixels.empty:
                    model_col = "Random Forest"
                    points = pixels.head(1000)
                    fig = px.scatter_map(points, lat="latitude", lon="longitude",
                                         color=points[model_col].astype(str),
                                         map_style="open-street-map", zoom=12,
                                         title="Held-out sample points — not a classified raster")
                    st.plotly_chart(fig, width="stretch")
                st.download_button("Download held-out samples", pixels.to_csv(index=False),
                                   file_name=f"{site_id}_heldout_predictions.csv", mime="text/csv")
        importance = pd.DataFrame(report["gini_feature_importance"])
        st.plotly_chart(px.bar(importance.sort_values("importance"), x="importance", y="feature",
                              orientation="h", title="RF feature importance — descriptive, not causal"),
                        width="stretch")
        st.subheader("Full-area classified raster")
        matching_rasters = []
        for raster_path in sorted(path.parent.glob("*.tif")):
            try:
                import rasterio
                with rasterio.open(raster_path) as raster:
                    tags = raster.tags()
                    if tags.get("site_id") == site_id and tags.get("dataset_sha256") == report["dataset_sha256"]:
                        matching_rasters.append(raster_path)
            except (OSError, ImportError):
                st.warning(f"Could not inspect raster {raster_path.name}.")
        if matching_rasters:
            raster_path = st.selectbox("Classified raster", matching_rasters, format_func=lambda p: p.name)
            with rasterio.open(raster_path) as raster:
                factor = min(1, 1000 / max(raster.height, raster.width))
                classes = raster.read(1, out_shape=(max(1, int(raster.height * factor)),
                                                   max(1, int(raster.width * factor))))
                colors = np.array([[255, 255, 255], [44, 160, 44], [214, 39, 40],
                                   [188, 189, 34], [31, 119, 180]], dtype="uint8")
                if not np.isin(classes, [0, 1, 2, 3, 4]).all():
                    st.error("Raster contains unexpected class IDs.")
                else:
                    st.image(colors[classes], caption=f"{raster_path.name}: green vegetation; red built-up; yellow bare soil; blue water; white no data.")
                    st.caption("Downsampled class-raster preview. It is separate from the held-out sample map and inherits this run's validation limitations.")
        else:
            st.info("No full-area classification raster has been produced for this run and site. Held-out sample points above are not a complete land-cover map.")
        st.download_button("Download run report", json.dumps(report, indent=2),
                           file_name=f"{path.parent.name}_metrics.json", mime="application/json")
        for limitation in report["limitations"]:
            st.caption(limitation)

elif page == "Saved DIP artifacts":
    st.warning("Saved DIP artifacts are legacy outputs, not a fresh image audit. Chronology, control suitability, and image counts are not verified by loading these files.")
    if site_id != "aws_pdx":
        st.info("No Quincy built-area, DiD, gradient, or IKTL artifacts are available. Boardman artifacts are never substituted.")
    else:
        metrics_path = DATA_DIR / "spatial_metrics_summary.json"
        built_path = DATA_DIR / "builtup_expansion_trajectory.csv"
        if built_path.exists():
            built = pd.read_csv(built_path)
            st.subheader("Stored built-area trajectory")
            st.bar_chart(built.pivot(index="tahun", columns="zona", values="ha"))
            st.caption("Stored spectral built-up estimates are not ground-truth roof areas.")
        if metrics_path.exists():
            legacy = read_json(metrics_path)
            section = st.selectbox("Stored artifact", list(legacy))
            st.json(legacy[section])
        st.caption("The old 100% classification JSON is retained on disk for traceability and is excluded from current classification results.")

st.divider()
st.caption("Data Center LST & Land Cover • observational remote-sensing study")
