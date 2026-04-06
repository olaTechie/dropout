"""Page 3: Transition SHAP Explorer — SHAP plots and Andersen domain decomposition."""

import streamlit as st
import json
import plotly.graph_objects as go
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
STAGE1 = ROOT / "outputs" / "stage1"

st.set_page_config(page_title="SHAP Explorer", layout="wide")
st.title("Transition SHAP Explorer")
st.markdown("Feature importance and Andersen domain decomposition across XGBoost models")

# ── Load Andersen decomposition data ──
results_path = STAGE1 / "xgb_results_summary.json"
if results_path.exists():
    with open(results_path) as f:
        xgb_results = json.load(f)
else:
    st.error("XGBoost results not found")
    st.stop()

# ── Model selector ──
model_choice = st.radio(
    "Select model",
    ["Model T1 (DTP1-DTP2)", "Model T2 (DTP2-DTP3)", "Model Full (Overall)"],
    horizontal=True,
)

model_key = {"Model T1 (DTP1-DTP2)": "t1", "Model T2 (DTP2-DTP3)": "t2", "Model Full (Overall)": "full"}[model_choice]
suffix = {"t1": "t1", "t2": "t2", "full": "full"}[model_key]

st.markdown("---")

# ── SHAP plots ──
col1, col2 = st.columns(2)

with col1:
    st.subheader("SHAP Bar Plot (Top 20)")
    bar_img = STAGE1 / f"shap_bar_model_{suffix}.pdf"
    bar_png = STAGE1 / f"shap_bar_model_{suffix}.png"
    # Try PNG first (Streamlit renders PNG natively)
    if bar_png.exists():
        st.image(str(bar_png), use_container_width=True)
    elif bar_img.exists():
        st.info("PDF available — download from Data Export page")
    else:
        st.warning("SHAP bar plot not found")

with col2:
    st.subheader("SHAP Beeswarm Plot")
    bee_png = STAGE1 / f"shap_beeswarm_model_{suffix}.png"
    if bee_png.exists():
        st.image(str(bee_png), use_container_width=True)
    else:
        st.warning("SHAP beeswarm plot not found")

st.markdown("---")

# ── Andersen Domain Decomposition ──
st.subheader("Andersen Domain Decomposition")

domains = xgb_results.get(model_key, {}).get("andersen_domains", {})
if domains:
    total = sum(domains.values())
    pct = {k: v / total * 100 for k, v in domains.items()}

    colours = {
        "Predisposing": "#1f77b4",
        "Enabling": "#ff7f0e",
        "Need": "#2ca02c",
        "Dynamic": "#d62728",
    }

    fig = go.Figure(go.Bar(
        x=list(pct.keys()),
        y=list(pct.values()),
        marker_color=[colours.get(k, "#999") for k in pct],
        text=[f"{v:.1f}%" for v in pct.values()],
        textposition="outside",
    ))
    fig.update_layout(
        yaxis_title="Share of Total SHAP (%)",
        yaxis_range=[0, 70],
        height=400,
    )
    st.plotly_chart(fig, use_container_width=True)

    st.info(f"**Dynamic features account for {pct.get('Dynamic', 0):.1f}%** of total SHAP importance "
            f"in {model_choice}, challenging the Andersen predisposing/enabling hypothesis.")
else:
    st.warning("Andersen decomposition data not found for this model")

st.markdown("---")

# ── Side-by-side comparison ──
st.subheader("Cross-Model Andersen Comparison")
comparison_img = STAGE1 / "andersen_decomp_comparison.png"
if comparison_img.exists():
    st.image(str(comparison_img), use_container_width=True)
else:
    st.warning("Comparison figure not found")

# ── Model performance summary ──
st.markdown("---")
st.subheader("Model Performance")

if model_key in xgb_results and "metrics" in xgb_results[model_key]:
    metrics = xgb_results[model_key]["metrics"]
    delong = xgb_results[model_key].get("delong", {})

    mc1, mc2, mc3, mc4 = st.columns(4)
    mc1.metric("AUC-ROC", f"{metrics['auc_roc']:.4f}",
               help=f"95% CI: [{metrics['auc_roc_ci'][0]:.4f}, {metrics['auc_roc_ci'][1]:.4f}]")
    mc2.metric("AUC-PR", f"{metrics['auc_pr']:.4f}",
               help=f"95% CI: [{metrics['auc_pr_ci'][0]:.4f}, {metrics['auc_pr_ci'][1]:.4f}]")
    mc3.metric("Brier Score", f"{metrics['brier']['brier']:.4f}")
    if delong:
        mc4.metric("DeLong p-value", f"{delong['p']:.2e}", help="XGBoost vs Logistic Regression")

    # Calibration
    cal = metrics.get("calibration", {})
    if cal:
        st.markdown(f"**Calibration**: slope = {cal['slope']:.3f}, intercept = {cal['intercept']:.3f}")

    # ROC/PR figure
    roc_img = STAGE1 / f"roc_pr_model_{suffix}.png"
    cal_img = STAGE1 / f"calibration_model_{suffix}.png"

    c1, c2 = st.columns(2)
    with c1:
        if roc_img.exists():
            st.image(str(roc_img), caption="ROC + PR Curves", use_container_width=True)
    with c2:
        if cal_img.exists():
            st.image(str(cal_img), caption="Calibration Curve", use_container_width=True)

st.caption("Source: outputs/stage1/ | Cluster-robust CV (GroupKFold on PSU), survey-weighted")
