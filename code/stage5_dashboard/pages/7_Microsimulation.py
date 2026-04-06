"""Page 7: Microsimulation Scenarios — side-by-side comparison, equity, cost-effectiveness."""

import streamlit as st
import pandas as pd
import json
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
STAGE3 = ROOT / "outputs" / "stage3"

st.set_page_config(page_title="Microsimulation", layout="wide")
st.title("Microsimulation Scenarios")
st.markdown("10,000-population microsimulation with 1,000 bootstrap iterations")

# ── Load data ──
results_path = STAGE3 / "microsim_results.json"
if not results_path.exists():
    st.error("Microsimulation results not found")
    st.stop()

with open(results_path) as f:
    results = json.load(f)

# ── Scenario comparison table ──
st.subheader("Scenario Comparison")

rows = []
for name, d in results.items():
    rows.append({
        "Scenario": name,
        "DTP3 Rate": f"{d['dtp3_rate_mean']:.3f}",
        "95% CI": f"[{d['dtp3_rate_ci_low']:.4f}, {d['dtp3_rate_ci_high']:.4f}]",
        "Cost/Child (N)": f"{d['cost_per_child_mean']:.0f}",
        "Equity Gap": f"{d['equity_gap_mean']:.3f}",
        "ICER vs S0": f"{d.get('icer_vs_s0', '-')}",
    })
st.dataframe(pd.DataFrame(rows), use_container_width=True)

st.markdown("---")

# ── DTP3 completion rates ──
st.subheader("DTP3 Completion Rates by Scenario")

scenarios = list(results.keys())
dtp3_means = [results[s]["dtp3_rate_mean"] * 100 for s in scenarios]
dtp3_lo = [results[s]["dtp3_rate_ci_low"] * 100 for s in scenarios]
dtp3_hi = [results[s]["dtp3_rate_ci_high"] * 100 for s in scenarios]

colours = ["#7f7f7f", "#2ca02c", "#1f77b4", "#ff7f0e", "#d62728", "#e377c2"]

fig = go.Figure()
fig.add_trace(go.Bar(
    x=scenarios, y=dtp3_means,
    marker_color=colours,
    text=[f"{v:.1f}%" for v in dtp3_means],
    textposition="outside",
    error_y=dict(
        type="data",
        symmetric=False,
        array=[h - m for h, m in zip(dtp3_hi, dtp3_means)],
        arrayminus=[m - l for m, l in zip(dtp3_means, dtp3_lo)],
    ),
))
fig.update_layout(yaxis_title="DTP3 Completion (%)", yaxis_range=[80, 105], height=450)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ── Cost-effectiveness ──
st.subheader("Cost-Effectiveness Plane")

delta_dtp3 = [results[s].get("delta_dtp3_vs_s0", 0) * 100 for s in scenarios]
delta_cost = [results[s].get("delta_cost_vs_s0", 0) for s in scenarios]

fig2 = go.Figure()
for i, s in enumerate(scenarios):
    if s == "S0: Status Quo":
        continue
    fig2.add_trace(go.Scatter(
        x=[delta_cost[i]], y=[delta_dtp3[i]],
        mode="markers+text",
        marker=dict(size=15, color=colours[i]),
        text=[s.split(":")[0]],
        textposition="top center",
        name=s,
    ))

fig2.add_hline(y=0, line_dash="dash", line_color="grey")
fig2.add_vline(x=0, line_dash="dash", line_color="grey")
fig2.update_layout(
    xaxis_title="Incremental Cost per Child (N) vs S0",
    yaxis_title="Incremental DTP3 (pp) vs S0",
    height=500,
    showlegend=True,
)
# Quadrant labels
fig2.add_annotation(x=-30, y=8, text="Dominates", showarrow=False, font=dict(color="green", size=12))
fig2.add_annotation(x=600, y=-1.5, text="Dominated", showarrow=False, font=dict(color="red", size=12))
st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# ── Equity dashboard ──
st.subheader("Equity Analysis")

eq_gaps = [results[s]["equity_gap_mean"] * 100 for s in scenarios]
eq_lo = [results[s]["equity_gap_ci_low"] * 100 for s in scenarios]
eq_hi = [results[s]["equity_gap_ci_high"] * 100 for s in scenarios]

fig3 = go.Figure()
fig3.add_trace(go.Bar(
    x=scenarios, y=eq_gaps,
    marker_color=[
        "#d62728" if g > 5 else "#ff7f0e" if g > 0.5 else "#2ca02c"
        for g in eq_gaps
    ],
    text=[f"{v:.1f}%" for v in eq_gaps],
    textposition="outside",
    error_y=dict(
        type="data",
        symmetric=False,
        array=[h - m for h, m in zip(eq_hi, eq_gaps)],
        arrayminus=[m - l for m, l in zip(eq_gaps, eq_lo)],
    ),
))
fig3.add_hline(y=5.1, line_dash="dash", line_color="grey", annotation_text="S0 baseline (5.1%)")
fig3.update_layout(
    yaxis_title="Equity Gap: Richest - Poorest (pp)",
    height=450,
)
st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")

# ── Pre-rendered figures ──
st.subheader("Microsimulation Figures")

tab1, tab2, tab3 = st.tabs(["Scenario Panels", "Bootstrap Distributions", "Summary"])

with tab1:
    img = STAGE3 / "microsim_scenarios.png"
    if img.exists():
        st.image(str(img), use_container_width=True)

with tab2:
    img = STAGE3 / "bootstrap_distributions.png"
    if img.exists():
        st.image(str(img), use_container_width=True)

with tab3:
    st.markdown("""
    **Recommended strategy for manuscript**:
    1. **Primary finding**: RL-optimised policy (S4) achieves 99.7% DTP3 with no equity gap widening
    2. **Cost-effectiveness case**: S1 (SMS) dominates on ICER but depends on model assumptions
    3. **Pragmatic recommendation**: S3 (risk-targeted CHW for top 30%) at N446/child
    4. **Policy warning**: Community-level bandit (S5) is inferior — individual-level targeting matters
    """)

st.caption("Source: outputs/stage3/ | 10K population x 1,000 bootstrap iterations")
