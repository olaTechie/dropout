"""
Nigeria DTP Vaccine Dropout — RL-Optimised Sequential Intervention Dashboard
Warwick Applied Health, Warwick Medical School, University of Warwick

Main Streamlit app entry point.
Launch: streamlit run code/stage5_dashboard/app.py
"""

import streamlit as st
from pathlib import Path

# ── Project root (two levels up from this file) ──
ROOT = Path(__file__).resolve().parents[2]

st.set_page_config(
    page_title="Nigeria DTP Dropout — RL Dashboard",
    page_icon=":syringe:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Sidebar ──
st.sidebar.title("Nigeria DTP Dropout")
st.sidebar.caption("RL-Optimised Sequential Intervention")
st.sidebar.markdown("---")
st.sidebar.markdown(
    "**Pipeline stages**\n"
    "1. Literature Review\n"
    "2. EDA + Cascade + ML\n"
    "3. Offline RL + Bandit + Microsim\n"
    "4. Dashboard (this app)"
)
st.sidebar.markdown("---")
st.sidebar.markdown(
    "Warwick Applied Health  \n"
    "Warwick Medical School  \n"
    "University of Warwick"
)

# ── Main landing page ──
st.title("RL-Optimised Sequential Intervention for Reducing DTP1-to-DTP3 Vaccine Dropout")
st.markdown("**Nigeria DHS 2024 | N = 3,194 DTP1 recipients aged 12-23 months**")

st.markdown("---")

# Key metrics row
col1, col2, col3, col4 = st.columns(4)
col1.metric("Study Population", "3,194", help="Children 12-23 months who received DTP1")
col2.metric("Overall Dropout", "14.8%", help="(DTP1 - DTP3) / DTP1 coverage")
col3.metric("CQL Policy Improvement", "+6.9 - 9.5%", help="OPE: WIS +9.5%, FQE +6.9%")
col4.metric("Best ICER", "Dominates (S1)", help="S1 Uniform SMS: negative ICER (saves money)")

st.markdown("---")

st.subheader("Key Findings")

st.markdown("""
| Finding | Detail |
|---------|--------|
| **Dynamic features dominate** | 35-59% of SHAP importance across all XGBoost models, challenging Andersen predisposing/enabling hypothesis |
| **CQL policy shifts** | From SMS-dominant (70.6%) to CHW-heavy (38.2%) + incentives (19.5%) |
| **S1 (SMS) dominates on ICER** | 100% DTP3 at lower cost than status quo (but model-optimistic) |
| **S4 (RL) most robust** | 99.7% DTP3 with no equity gap widening |
| **S5 (Bandit) fails** | Widens equity gap from 5.1% to 7.2% |
| **Recommended** | S3 (risk-targeted CHW for top 30%) as pragmatic choice |
""")

st.markdown("---")

st.subheader("Navigate the Dashboard")

st.markdown("""
Use the sidebar pages to explore:

| Page | Content |
|------|---------|
| **1 - Immunisation Cascade** | DTP1-DTP2-DTP3 retention by zone, state, wealth |
| **2 - EDA Explorer** | Descriptive statistics, choropleth, funnel, spatial clusters |
| **3 - SHAP Explorer** | Feature importance, beeswarm plots, Andersen decomposition |
| **4 - Timeliness** | Inter-dose interval distributions, delay patterns |
| **5 - RL Policy Map** | CQL policy recommendations, Q-values, OPE results |
| **6 - Bandit Allocation** | Community-level budget allocation, coverage projections |
| **7 - Microsimulation** | Side-by-side scenario comparison, equity, cost-effectiveness |
| **8 - Data Export** | Download all datasets and results |
""")
