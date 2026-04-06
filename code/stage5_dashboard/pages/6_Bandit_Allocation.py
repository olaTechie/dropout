"""Page 6: Bandit Allocation — community-level budget-constrained allocation."""

import streamlit as st
import pandas as pd
import json
import plotly.graph_objects as go
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
STAGE3 = ROOT / "outputs" / "stage3"

st.set_page_config(page_title="Bandit Allocation", layout="wide")
st.title("Bandit Allocation")
st.markdown("LinUCB community-level budget-constrained intervention allocation")

# ── Load data ──
summary_path = STAGE3 / "stage3_summary.json"
alloc_path = STAGE3 / "lga_allocation.csv"

if not summary_path.exists():
    st.error("Stage 3 summary not found")
    st.stop()

with open(summary_path) as f:
    s3 = json.load(f)

# ── Key metrics ──
c1, c2, c3, c4 = st.columns(4)
c1.metric("Communities", f"{s3['n_communities']:,}")
c2.metric("Context Features", s3["n_context_features"])
c3.metric("LinUCB Alpha", s3["linucb_alpha"])
c4.metric("Primary Budget", f"N{s3['budget_primary']/1e6:.0f}M")

st.markdown("---")

# ── Budget sensitivity ──
st.subheader("Budget Sensitivity")

budget_data = s3.get("budget_sensitivity", {})
if budget_data:
    rows = []
    for level, d in budget_data.items():
        rows.append({
            "Budget Level": level.title(),
            "Budget (N)": f"N{int(d['budget']):,}",
            "Total Cost": f"N{int(d['total_cost']):,}",
            "Communities": d["communities_covered"],
            "SMS (a1)": int(d["action_dist"].get("1", 0)),
            "CHW (a2)": int(d["action_dist"].get("2", 0)),
            "Facility (a3)": int(d["action_dist"].get("3", 0)),
            "Incentive (a4)": int(d["action_dist"].get("4", 0)),
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True)
    st.info(
        "Total cost is << budget because community sizes are small (median ~3 children per cluster). "
        "LinUCB correctly identifies SMS as the most cost-effective per-child intervention."
    )

st.markdown("---")

# ── Allocation data ──
st.subheader("Community Allocation Details")
if alloc_path.exists():
    alloc_df = pd.read_csv(alloc_path)
    action_map = {0: "None", 1: "SMS", 2: "CHW", 3: "Facility", 4: "Incentive"}
    alloc_df["action_label"] = alloc_df["assigned_action"].map(action_map)

    # Action distribution chart
    action_counts = alloc_df["action_label"].value_counts()
    fig = go.Figure(go.Bar(
        x=action_counts.index,
        y=action_counts.values,
        marker_color=["#2ca02c", "#1f77b4", "#ff7f0e", "#d62728", "#9467bd"][:len(action_counts)],
        text=action_counts.values,
        textposition="outside",
    ))
    fig.update_layout(
        yaxis_title="Number of Communities",
        height=400,
    )
    st.plotly_chart(fig, use_container_width=True)

    # Preview
    st.markdown(f"**{len(alloc_df)} communities allocated**")
    st.dataframe(alloc_df.head(20), use_container_width=True)

st.markdown("---")

# ── Bandit figures ──
st.subheader("LinUCB Diagnostics")
bandit_img = STAGE3 / "bandit_allocation.png"
if bandit_img.exists():
    st.image(str(bandit_img), use_container_width=True)
else:
    st.warning("Bandit allocation figure not found")

st.markdown("---")

# ── Warning ──
st.warning(
    "**S5 (Bandit-Allocated) underperforms status quo** and widens the equity gap (5.1% to 7.2%). "
    "Community-level assignment does not account for individual-level risk variation. "
    "Individual-level targeting (S3 or S4) is recommended."
)

st.caption("Source: outputs/stage3/ | LinUCB with 19-dim context, 1,140 communities")
