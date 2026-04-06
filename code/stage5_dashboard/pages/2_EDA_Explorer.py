"""Page 2: EDA Explorer — descriptive statistics, choropleth, funnel, spatial clusters."""

import streamlit as st
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
STAGE0 = ROOT / "outputs" / "stage0"

st.set_page_config(page_title="EDA Explorer", layout="wide")
st.title("EDA Explorer")
st.markdown("Exploratory data analysis of DTP dropout determinants")

# ── TableOne ──
st.subheader("Descriptive Statistics (TableOne)")
table_path = STAGE0 / "descriptive_statistics_table.csv"
if table_path.exists():
    df = pd.read_csv(table_path)
    st.dataframe(df, use_container_width=True, height=500)
else:
    st.warning("TableOne CSV not found")

st.markdown("---")

# ── Figures gallery ──
st.subheader("EDA Figures")

tab1, tab2, tab3, tab4 = st.tabs([
    "Choropleth Map", "Funnel Plot", "Spatial Clusters", "Zonal Analysis"
])

with tab1:
    st.markdown("**Dropout prevalence by state (choropleth)**")
    choropleth = STAGE0 / "dropout_choropleth_map.png"
    if choropleth.exists():
        st.image(str(choropleth), use_container_width=True)
    else:
        st.warning("Choropleth map not found")

with tab2:
    st.markdown("**Funnel plot — observed vs expected dropout by state**")
    funnel = STAGE0 / "dropout_funnel_plot.png"
    if funnel.exists():
        st.image(str(funnel), use_container_width=True)
    else:
        st.warning("Funnel plot not found")

with tab3:
    st.markdown("**Local Moran's I — spatial clustering of dropout (HH/LL/LH/HL)**")
    moran = STAGE0 / "local_moran_clusters_map.png"
    if moran.exists():
        st.image(str(moran), use_container_width=True)
    else:
        st.warning("Moran cluster map not found")

with tab4:
    st.markdown("**Dropout by geopolitical zone and wealth gradient**")
    zonal = STAGE0 / "zonal_analysis.png"
    if zonal.exists():
        st.image(str(zonal), use_container_width=True)
    else:
        st.warning("Zonal analysis figure not found")

st.markdown("---")

# ── Profiling reports ──
st.subheader("Profiling Reports")
col1, col2 = st.columns(2)
with col1:
    profile = STAGE0 / "dropout_profile_report.html"
    if profile.exists():
        st.markdown(f"[Open YData Profiling Report]({profile})")
    else:
        st.info("Profiling report not available")
with col2:
    sweetviz = STAGE0 / "dropout_sweetviz_report.html"
    if sweetviz.exists():
        st.markdown(f"[Open Sweetviz Report]({sweetviz})")
    else:
        st.info("Sweetviz report not available")

# ── Prevalence by state ──
st.subheader("Dropout Prevalence by State")
prev_img = STAGE0 / "dropout_prevalence_by_state.png"
if prev_img.exists():
    st.image(str(prev_img), use_container_width=True)

st.caption("Source: outputs/stage0/ | N=3,194 DTP1 recipients")
