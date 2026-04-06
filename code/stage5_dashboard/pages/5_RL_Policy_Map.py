"""Page 5: RL Policy Map — CQL policy recommendations, Q-values, OPE results."""

import streamlit as st
import pandas as pd
import json
import plotly.graph_objects as go
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
STAGE2 = ROOT / "outputs" / "stage2"

st.set_page_config(page_title="RL Policy Map", layout="wide")
st.title("RL Policy Map")
st.markdown("Conservative Q-Learning (CQL) policy recommendations and off-policy evaluation")

# ── Load data ──
summary_path = STAGE2 / "stage2_summary.json"
ope_path = STAGE2 / "ope_results.json"

if not summary_path.exists() or not ope_path.exists():
    st.error("Stage 2 summary or OPE results not found")
    st.stop()

with open(summary_path) as f:
    summary = json.load(f)
with open(ope_path) as f:
    ope = json.load(f)

# ── Key metrics ──
st.subheader("Off-Policy Evaluation")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Behaviour Value", f"{ope['behaviour_policy_value']:.3f}")
c2.metric("WIS Estimate", f"{ope['WIS_estimate']:.3f}", delta=f"+{ope['policy_improvement_pct_WIS']:.1f}%")
c3.metric("FQE Estimate", f"{ope['FQE_eval_policy_value']:.3f}", delta=f"+{ope['policy_improvement_pct_FQE']:.1f}%")
c4.metric("OOD Action Freq", f"{ope['ood_action_freq_cql_pct']:.1f}%",
          help="Fraction of CQL actions not well-supported by behaviour data")

st.markdown("---")

# ── Policy distribution comparison ──
st.subheader("Policy Distribution: Behaviour vs CQL")

action_labels = ["a0: None", "a1: SMS", "a2: CHW", "a3: Facility", "a4: Incentive"]
behav_dist = summary["behaviour_action_dist"]
cql_dist = summary["policy_action_dist"]

behav_vals = [behav_dist[str(i)] * 100 for i in range(5)]
cql_vals = [cql_dist[str(i)] * 100 for i in range(5)]

fig = go.Figure()
fig.add_trace(go.Bar(
    name="Behaviour (observed)",
    x=action_labels, y=behav_vals,
    marker_color="#1f77b4",
    text=[f"{v:.1f}%" for v in behav_vals],
    textposition="outside",
))
fig.add_trace(go.Bar(
    name="CQL Policy (learned)",
    x=action_labels, y=cql_vals,
    marker_color="#d62728",
    text=[f"{v:.1f}%" for v in cql_vals],
    textposition="outside",
))
fig.update_layout(
    barmode="group", yaxis_title="Frequency (%)", yaxis_range=[0, 85],
    height=450,
)
st.plotly_chart(fig, use_container_width=True)

st.info(
    "CQL shifts from SMS-dominant (70.6%) to CHW-heavy (38.2%) + incentives (19.5%). "
    "This aligns with literature evidence that CHW visits have the largest effect sizes (+15-25%) in LMICs."
)

st.markdown("---")

# ── Stage 2 figures ──
st.subheader("Model Diagnostics")

tab1, tab2, tab3, tab4 = st.tabs([
    "FQI Convergence", "CQL Analysis", "OPE Comparison", "Q-Values by Action"
])

with tab1:
    img = STAGE2 / "fqi_convergence.png"
    if img.exists():
        st.image(str(img), use_container_width=True)
    else:
        st.warning("FQI convergence plot not found")

with tab2:
    img = STAGE2 / "cql_analysis.png"
    if img.exists():
        st.image(str(img), use_container_width=True)
    else:
        st.warning("CQL analysis plot not found")

with tab3:
    img = STAGE2 / "ope_comparison.png"
    if img.exists():
        st.image(str(img), use_container_width=True)
    else:
        st.warning("OPE comparison plot not found")

with tab4:
    img = STAGE2 / "q_values_by_action.png"
    if img.exists():
        st.image(str(img), use_container_width=True)
    else:
        st.warning("Q-values plot not found")

st.markdown("---")

# ── CQL alpha sensitivity ──
st.subheader("CQL Alpha Sensitivity")
alpha_path = STAGE2 / "cql_alpha_sensitivity.csv"
if alpha_path.exists():
    alpha_df = pd.read_csv(alpha_path)
    st.dataframe(alpha_df, use_container_width=True)
else:
    st.info("Alpha sensitivity data not available")

# ── Policy lookup preview ──
st.markdown("---")
st.subheader("Policy Lookup (Sample)")
policy_path = STAGE2 / "policy_lookup.csv"
if policy_path.exists():
    policy_df = pd.read_csv(policy_path)
    st.markdown(f"**{len(policy_df)} state-action pairs** | Columns: child_id, dose_step, optimal_action, Q-values")
    st.dataframe(policy_df.head(20), use_container_width=True, height=400)

st.caption("Source: outputs/stage2/ | CQL alpha=1.0, WIS epsilon=0.1, 1,569 validation episodes")
