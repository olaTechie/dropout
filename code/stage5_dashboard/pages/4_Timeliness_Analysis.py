"""Page 4: Timeliness Analysis — inter-dose intervals and delay accumulation."""

import streamlit as st
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
STAGE1 = ROOT / "outputs" / "stage1"

st.set_page_config(page_title="Timeliness Analysis", layout="wide")
st.title("Timeliness Analysis")
st.markdown("Inter-dose interval distributions and delay accumulation patterns")

# ── Cascade + intervals figure ──
st.subheader("Cascade Funnel and Inter-Dose Intervals")
cascade_fig = STAGE1 / "cascade_and_intervals.pdf"
cascade_png = STAGE1 / "cascade_and_intervals.png"
if cascade_png.exists():
    st.image(str(cascade_png), use_container_width=True)
elif cascade_fig.exists():
    st.info("PDF figure available — see Data Export page for download")
else:
    st.warning("Cascade and intervals figure not found")

st.markdown("---")

# ── Cascade by zone ──
st.subheader("Cascade by Geopolitical Zone")
zone_fig = STAGE1 / "cascade_by_zone.pdf"
zone_png = STAGE1 / "cascade_by_zone.png"
if zone_png.exists():
    st.image(str(zone_png), use_container_width=True)
elif zone_fig.exists():
    st.info("PDF figure available — see Data Export page for download")
else:
    st.warning("Cascade by zone figure not found")

st.markdown("---")

# ── Timeliness thresholds reference ──
st.subheader("Timeliness Thresholds (WHO Schedule)")
st.markdown("""
| Dose | Timely If Given By | Schedule |
|------|--------------------|----------|
| DTP1 | 56 days (8 weeks) from birth | 6 weeks |
| DTP2 | 84 days (12 weeks) from birth | 10 weeks |
| DTP3 | 112 days (16 weeks) from birth | 14 weeks |

**Inter-dose intervals**:
- `interval_birth_dtp1` = date(DTP1) - date(birth)
- `interval_dtp1_dtp2` = date(DTP2) - date(DTP1)
- `interval_dtp2_dtp3` = date(DTP3) - date(DTP2)

Only card-confirmed dates (h3==1) are used. Values 97 (inconsistent) and 98 (don't know) are treated as missing.
""")

st.markdown("---")

# ── Key finding ──
st.info(
    "**Key finding**: Dynamic features (delay_accumulation, community_dropout, "
    "cluster_dtp_coverage) account for 35-59% of SHAP importance across all models. "
    "Timeliness and delay patterns are the strongest predictors of dropout, "
    "outweighing traditional sociodemographic and access factors."
)

st.caption("Source: outputs/stage1/ | Card-confirmed vaccination dates only")
