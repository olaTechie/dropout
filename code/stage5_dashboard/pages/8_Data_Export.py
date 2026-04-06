"""Page 8: Data Export — download cascade data, policy recommendations, scenario results."""

import streamlit as st
import pandas as pd
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

st.set_page_config(page_title="Data Export", layout="wide")
st.title("Data Export")
st.markdown("Download all pipeline outputs and results")


def file_download(path: Path, label: str, mime: str = "application/octet-stream"):
    """Render a download button for a file."""
    if path.exists():
        data = path.read_bytes()
        st.download_button(
            label=f"Download {label}",
            data=data,
            file_name=path.name,
            mime=mime,
        )
    else:
        st.caption(f"{label}: not found")


# ── Stage 1: Cascade and ML ──
st.subheader("Stage 1: Cascade + ML Outputs")

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("**Cascade Metrics**")
    file_download(ROOT / "outputs/stage1/cascade_metrics.csv", "cascade_metrics.csv", "text/csv")
with col2:
    st.markdown("**XGBoost Results Summary**")
    file_download(ROOT / "outputs/stage1/xgb_results_summary.json", "xgb_results_summary.json", "application/json")
with col3:
    st.markdown("**Trajectory Dataset**")
    file_download(ROOT / "outputs/stage1/trajectory_dataset.csv", "trajectory_dataset.csv", "text/csv")

st.markdown("---")

# ── Stage 1: Figures ──
st.subheader("Stage 1: Figures (PDF)")
fig_cols = st.columns(4)
stage1_pdfs = [
    "cascade_and_intervals.pdf", "cascade_by_zone.pdf",
    "andersen_decomp_comparison.pdf",
]
for i, name in enumerate(stage1_pdfs):
    with fig_cols[i % 4]:
        file_download(ROOT / f"outputs/stage1/{name}", name, "application/pdf")

# SHAP and model figures
shap_pdfs = []
for model in ["full", "t1", "t2"]:
    for kind in ["shap_bar", "shap_beeswarm", "roc_pr", "calibration", "andersen_decomp"]:
        fname = f"{kind}_model_{model}.pdf"
        if (ROOT / f"outputs/stage1/{fname}").exists():
            shap_pdfs.append(fname)

if shap_pdfs:
    st.markdown("**Model-specific figures**")
    cols = st.columns(4)
    for i, name in enumerate(shap_pdfs):
        with cols[i % 4]:
            file_download(ROOT / f"outputs/stage1/{name}", name, "application/pdf")

st.markdown("---")

# ── Stage 2: RL Outputs ──
st.subheader("Stage 2: Offline RL Outputs")

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("**Policy Lookup**")
    file_download(ROOT / "outputs/stage2/policy_lookup.csv", "policy_lookup.csv", "text/csv")
with col2:
    st.markdown("**OPE Results**")
    file_download(ROOT / "outputs/stage2/ope_results.json", "ope_results.json", "application/json")
with col3:
    st.markdown("**CQL Alpha Sensitivity**")
    file_download(ROOT / "outputs/stage2/cql_alpha_sensitivity.csv", "cql_alpha_sensitivity.csv", "text/csv")

st.markdown("**Stage 2 Figures**")
s2_cols = st.columns(4)
for i, name in enumerate(["fqi_convergence.pdf", "cql_analysis.pdf", "ope_comparison.pdf", "q_values_by_action.pdf"]):
    with s2_cols[i]:
        file_download(ROOT / f"outputs/stage2/{name}", name, "application/pdf")

st.markdown("---")

# ── Stage 3: Microsim Outputs ──
st.subheader("Stage 3: Bandit + Microsimulation Outputs")

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("**Community Allocation**")
    file_download(ROOT / "outputs/stage3/lga_allocation.csv", "lga_allocation.csv", "text/csv")
with col2:
    st.markdown("**Microsim Results (JSON)**")
    file_download(ROOT / "outputs/stage3/microsim_results.json", "microsim_results.json", "application/json")
with col3:
    st.markdown("**Microsim Results (CSV)**")
    file_download(ROOT / "outputs/stage3/microsim_results.csv", "microsim_results.csv", "text/csv")

# Bootstrap data
st.markdown("**Bootstrap Distributions**")
boot_cols = st.columns(3)
for i, scenario in enumerate(["s0_status_quo", "s1_uniform_sms", "s2_uniform_chw",
                                "s3_risk_targeted", "s4_rl_optimised", "s5_bandit_allocated"]):
    fname = f"bootstrap_{scenario}.csv"
    with boot_cols[i % 3]:
        file_download(ROOT / f"outputs/stage3/{fname}", fname, "text/csv")

st.markdown("**Stage 3 Figures**")
s3_cols = st.columns(3)
for i, name in enumerate(["bandit_allocation.pdf", "microsim_scenarios.pdf", "bootstrap_distributions.pdf"]):
    with s3_cols[i]:
        file_download(ROOT / f"outputs/stage3/{name}", name, "application/pdf")

st.markdown("---")

# ── Stage 0: EDA ──
st.subheader("Stage 0: EDA Outputs")

col1, col2 = st.columns(2)
with col1:
    st.markdown("**Descriptive Statistics**")
    file_download(ROOT / "outputs/stage0/descriptive_statistics_table.csv", "descriptive_statistics_table.csv", "text/csv")
with col2:
    st.markdown("**EDA Figures**")
    for name in ["dropout_choropleth_map.pdf", "dropout_funnel_plot.pdf",
                  "local_moran_clusters_map.pdf", "zonal_analysis.pdf", "dropout_prevalence_by_state.pdf"]:
        file_download(ROOT / f"outputs/stage0/{name}", name, "application/pdf")

st.markdown("---")

# ── Literature ──
st.subheader("Literature Review Outputs")
lit_cols = st.columns(3)
with lit_cols[0]:
    file_download(ROOT / "outputs/literature/dropout_literature_review.csv", "dropout_literature_review.csv", "text/csv")
    file_download(ROOT / "outputs/literature/intervention_effect_sizes.csv", "intervention_effect_sizes.csv", "text/csv")
with lit_cols[1]:
    file_download(ROOT / "outputs/literature/references.bib", "references.bib", "text/plain")
    file_download(ROOT / "outputs/literature/action_space_calibration.json", "action_space_calibration.json", "application/json")
with lit_cols[2]:
    file_download(ROOT / "outputs/literature/rl_health_precedents.md", "rl_health_precedents.md", "text/markdown")
    file_download(ROOT / "outputs/literature/ml_validation_recommendations.md", "ml_validation_recommendations.md", "text/markdown")

st.markdown("---")

# ── Processed data ──
st.subheader("Processed Datasets")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("**Analytic Dataset**")
    for ext in ["csv", "parquet"]:
        p = ROOT / f"data/processed/analytic_dtp1_received.{ext}"
        if p.exists():
            file_download(p, f"analytic_dtp1_received.{ext}")
with col2:
    st.markdown("**Trajectory Dataset**")
    file_download(ROOT / "data/processed/trajectory_dataset.csv", "trajectory_dataset.csv", "text/csv")
with col3:
    st.markdown("**State Space Definition**")
    file_download(ROOT / "data/processed/state_space_definition.json", "state_space_definition.json", "application/json")

st.caption("All outputs from the 4-stage pipeline")
