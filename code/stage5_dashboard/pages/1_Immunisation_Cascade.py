"""Page 1: Immunisation Cascade — DTP1-DTP2-DTP3 retention by zone."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

st.set_page_config(page_title="Immunisation Cascade", layout="wide")
st.title("Immunisation Cascade")
st.markdown("DTP1 - DTP2 - DTP3 retention rates by geopolitical zone")

# ── Load cascade data ──
cascade_path = ROOT / "outputs" / "stage1" / "cascade_metrics.csv"
if not cascade_path.exists():
    st.error(f"Cascade metrics not found: {cascade_path}")
    st.stop()

df = pd.read_csv(cascade_path)

# ── Zone filter ──
zones = sorted(df["zone"].unique())
selected_zones = st.multiselect("Filter by zone", zones, default=zones)
filtered = df[df["zone"].isin(selected_zones)]

# ── Cascade bar chart ──
st.subheader("Vaccination Cascade by Zone")

fig = go.Figure()
for dose, col, colour in [
    ("DTP1", "dtp1_pct", "#2ca02c"),
    ("DTP2", "dtp2_pct", "#ff7f0e"),
    ("DTP3", "dtp3_pct", "#d62728"),
]:
    fig.add_trace(go.Bar(
        name=dose,
        x=filtered["zone"],
        y=filtered[col],
        marker_color=colour,
        text=[f"{v:.1f}%" for v in filtered[col]],
        textposition="outside",
    ))

fig.update_layout(
    barmode="group",
    yaxis_title="Coverage (%)",
    yaxis_range=[0, 110],
    legend_title="Dose",
    height=500,
)
st.plotly_chart(fig, use_container_width=True)

# ── Retention rates ──
st.subheader("Transition Retention Rates")

fig2 = go.Figure()
fig2.add_trace(go.Bar(
    name="T1: DTP1→DTP2",
    x=filtered["zone"],
    y=filtered["retention_t1"],
    marker_color="#1f77b4",
    text=[f"{v:.1f}%" for v in filtered["retention_t1"]],
    textposition="outside",
))
fig2.add_trace(go.Bar(
    name="T2: DTP2→DTP3",
    x=filtered["zone"],
    y=filtered["retention_t2"],
    marker_color="#9467bd",
    text=[f"{v:.1f}%" for v in filtered["retention_t2"]],
    textposition="outside",
))
fig2.update_layout(
    barmode="group",
    yaxis_title="Retention (%)",
    yaxis_range=[0, 110],
    height=500,
)
st.plotly_chart(fig2, use_container_width=True)

# ── WHO Dropout Rate ──
st.subheader("WHO Dropout Rate by Zone")
st.markdown("Dropout rate = (DTP1 - DTP3) / DTP1 x 100")

fig3 = go.Figure(go.Bar(
    x=filtered["zone"],
    y=filtered["who_dropout"],
    marker_color=["#d62728" if v > 15 else "#ff7f0e" if v > 10 else "#2ca02c"
                   for v in filtered["who_dropout"]],
    text=[f"{v:.1f}%" for v in filtered["who_dropout"]],
    textposition="outside",
))
fig3.update_layout(yaxis_title="WHO Dropout Rate (%)", yaxis_range=[0, 25], height=400)
st.plotly_chart(fig3, use_container_width=True)

# ── Data table ──
st.subheader("Raw Data")
st.dataframe(
    filtered.style.format({
        "dtp1_pct": "{:.1f}%", "dtp2_pct": "{:.1f}%", "dtp3_pct": "{:.1f}%",
        "retention_t1": "{:.1f}%", "retention_t2": "{:.1f}%", "who_dropout": "{:.1f}%",
    }),
    use_container_width=True,
)

st.caption("Source: outputs/stage1/cascade_metrics.csv | N=3,194 DTP1 recipients")
