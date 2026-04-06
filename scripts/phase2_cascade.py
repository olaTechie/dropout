#!/usr/bin/env python3
"""Phase 2: Cascade Construction & Trajectory Reconstruction.

Reads analytic dataset from Phase 1, constructs:
- Cascade metrics (DTP1/2/3 coverage, transition rates, timeliness)
- Trajectory reconstruction (inter-dose intervals, delay accumulation)
- Community-level variables
- Merged geospatial covariates

Outputs → outputs/stage1/ and data/processed/
"""

import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROC = ROOT / "data/processed"
OUT1 = ROOT / "outputs/stage1"
GEO_CSV = ROOT / "data/raw/NGGC8AFL.csv"
DATA_KR = ROOT / "data/dhs/raw/nga_2024/NGKR8BFL.dta"
OUT1.mkdir(parents=True, exist_ok=True)

ZONE_MAP = {1: "North Central", 2: "North East", 3: "North West",
            4: "South East", 5: "South South", 6: "South West"}

# ── Load analytic sample ──────────────────────────────────────────────
print("Loading analytic dataset...")
df = pd.read_parquet(PROC / "analytic_dtp1_received.parquet")
print(f"  {df.shape[0]:,} rows")

# ══════════════════════════════════════════════════════════════════════
# 2.1 Cascade Metrics
# ══════════════════════════════════════════════════════════════════════
print("\n2.1 Computing cascade metrics...")

def weighted_mean(x, w):
    valid = ~(x.isna() | w.isna())
    if valid.sum() == 0:
        return np.nan
    return np.average(x[valid], weights=w[valid])

# National coverage
nat_dtp1 = weighted_mean(df["vac_dpt1"], df["wt"])
nat_dtp2 = weighted_mean(df["vac_dpt2"], df["wt"])
nat_dtp3 = weighted_mean(df["vac_dpt3"], df["wt"])
nat_dropout_rate = (nat_dtp1 - nat_dtp3) / nat_dtp1 * 100  # WHO dropout rate

print(f"  National (among DTP1 recipients):")
print(f"    DTP1: {nat_dtp1*100:.1f}% (by definition ~100%)")
print(f"    DTP2: {nat_dtp2*100:.1f}%")
print(f"    DTP3: {nat_dtp3*100:.1f}%")
print(f"    WHO Dropout Rate: {nat_dropout_rate:.1f}%")

# By zone
cascade_zone = []
for z_code, z_label in ZONE_MAP.items():
    sub = df[df["szone"] == z_code]
    w = sub["wt"]
    cascade_zone.append({
        "zone": z_label,
        "n": len(sub),
        "dtp1_pct": weighted_mean(sub["vac_dpt1"], w) * 100,
        "dtp2_pct": weighted_mean(sub["vac_dpt2"], w) * 100,
        "dtp3_pct": weighted_mean(sub["vac_dpt3"], w) * 100,
        "retention_t1": weighted_mean(sub["vac_dpt2"], w) / weighted_mean(sub["vac_dpt1"], w) * 100,
        "retention_t2": np.where(
            weighted_mean(sub["vac_dpt2"], w) > 0,
            weighted_mean(sub["vac_dpt3"], w) / weighted_mean(sub["vac_dpt2"], w) * 100,
            np.nan
        ),
        "who_dropout": (weighted_mean(sub["vac_dpt1"], w) - weighted_mean(sub["vac_dpt3"], w))
                        / weighted_mean(sub["vac_dpt1"], w) * 100,
    })

cascade_df = pd.DataFrame(cascade_zone)
cascade_df.to_csv(OUT1 / "cascade_metrics.csv", index=False)
print(cascade_df.to_string(index=False))

# Cascade figure
fig, ax = plt.subplots(figsize=(10, 7))
x_pos = np.arange(len(ZONE_MAP))
width = 0.25
for i, dose in enumerate(["dtp1_pct", "dtp2_pct", "dtp3_pct"]):
    label = ["DTP1", "DTP2", "DTP3"][i]
    ax.bar(x_pos + i * width, cascade_df[dose], width, label=label)
ax.set_xticks(x_pos + width)
ax.set_xticklabels(cascade_df["zone"], rotation=30, ha="right")
ax.set_ylabel("Coverage (%)")
ax.set_title("DTP Vaccination Cascade by Geopolitical Zone (Among DTP1 Recipients)")
ax.legend()
ax.set_ylim(0, 110)
plt.tight_layout()
fig.savefig(OUT1 / "cascade_by_zone.pdf", dpi=300, bbox_inches="tight")
plt.close()
print("  → cascade_by_zone.pdf saved")

# ══════════════════════════════════════════════════════════════════════
# 2.2 Trajectory Reconstruction
# ══════════════════════════════════════════════════════════════════════
print("\n2.2 Reconstructing trajectories from card dates...")

# Date variables are already in the analytic dataset from Phase 1
# No need to re-merge; just verify they exist
required_date_cols = ["h3d", "h3m", "h3y", "h5d", "h5m", "h5y", "h7d", "h7m", "h7y", "h25d", "h25m", "h25y"]
present = [c for c in required_date_cols if c in df.columns]
print(f"  Date columns present: {len(present)} of {len(required_date_cols)}")

def parse_dhs_date(day_col, month_col, year_col, df):
    """Parse DHS date variables, treating 97/98 as missing."""
    d = df[day_col].copy()
    m = df[month_col].copy()
    y = df[year_col].copy()

    # 97 = inconsistent, 98 = don't know → missing
    d = d.where(~d.isin([97, 98]))
    m = m.where(~m.isin([97, 98]))
    y = y.where(~y.isin([97, 98]))

    # Impute missing day with 15 (midpoint)
    d = d.fillna(15).clip(1, 28)
    # Need valid month and year
    valid = m.notna() & y.notna() & (y > 0) & (m > 0) & (m <= 12)

    dates = pd.to_datetime(
        {"year": y.where(valid), "month": m.where(valid), "day": d.where(valid)},
        errors="coerce"
    )
    return dates

# Card-confirmed subset (h3 == 1 means vaccination date on card)
card_mask = df["h3"] == 1
print(f"  Card-confirmed DTP1: {card_mask.sum():,} children")

# Parse dates
df["date_birth"] = parse_dhs_date("h25d", "h25m", "h25y", df)
df["date_dtp1"] = parse_dhs_date("h3d", "h3m", "h3y", df)
df["date_dtp2"] = parse_dhs_date("h5d", "h5m", "h5y", df)
df["date_dtp3"] = parse_dhs_date("h7d", "h7m", "h7y", df)

# Inter-dose intervals (days)
df["interval_birth_dtp1"] = (df["date_dtp1"] - df["date_birth"]).dt.days
df["interval_dtp1_dtp2"] = (df["date_dtp2"] - df["date_dtp1"]).dt.days
df["interval_dtp2_dtp3"] = (df["date_dtp3"] - df["date_dtp2"]).dt.days

# Clean: negative or implausible intervals → NaN
for col in ["interval_birth_dtp1", "interval_dtp1_dtp2", "interval_dtp2_dtp3"]:
    df.loc[df[col] < 0, col] = np.nan
    df.loc[df[col] > 365, col] = np.nan

# Timeliness flags (card-confirmed only)
df["dtp1_timely"] = np.where(card_mask & df["interval_birth_dtp1"].notna(),
                              (df["interval_birth_dtp1"] <= 56).astype(float), np.nan)

# DTP2 timely: ≤ 84 days from birth
df["dtp2_age_days"] = (df["date_dtp2"] - df["date_birth"]).dt.days
df["dtp2_timely"] = np.where(df["dtp2_age_days"].notna() & card_mask,
                              (df["dtp2_age_days"] <= 84).astype(float), np.nan)

# DTP3 timely: ≤ 112 days from birth
df["dtp3_age_days"] = (df["date_dtp3"] - df["date_birth"]).dt.days
df["dtp3_timely"] = np.where(df["dtp3_age_days"].notna() & card_mask,
                              (df["dtp3_age_days"] <= 112).astype(float), np.nan)

# Delay accumulation: cumulative delay relative to schedule
# Schedule: DTP1 at 6w (42d), DTP2 at 10w (70d), DTP3 at 14w (98d)
df["delay_dtp1"] = np.where(df["interval_birth_dtp1"].notna(),
                             np.maximum(df["interval_birth_dtp1"] - 42, 0), np.nan)
df["delay_dtp2"] = np.where(df["dtp2_age_days"].notna(),
                             np.maximum(df["dtp2_age_days"] - 70, 0), np.nan)
df["delay_dtp3"] = np.where(df["dtp3_age_days"].notna(),
                             np.maximum(df["dtp3_age_days"] - 98, 0), np.nan)

# Print timeliness cascade (card-confirmed)
card_sub = df[card_mask]
print(f"\n  Timeliness Cascade (card-confirmed, n={len(card_sub):,}):")
for dose, col in [("DTP1", "dtp1_timely"), ("DTP2", "dtp2_timely"), ("DTP3", "dtp3_timely")]:
    valid = card_sub[col].dropna()
    if len(valid) > 0:
        pct = valid.mean() * 100
        print(f"    {dose} timely: {pct:.1f}% (n={len(valid):,})")

# Interval summary
print(f"\n  Inter-dose intervals (days, card-confirmed):")
for col, label in [("interval_birth_dtp1", "Birth→DTP1"),
                   ("interval_dtp1_dtp2", "DTP1→DTP2"),
                   ("interval_dtp2_dtp3", "DTP2→DTP3")]:
    valid = df.loc[card_mask, col].dropna()
    if len(valid) > 0:
        print(f"    {label}: median={valid.median():.0f}, IQR=[{valid.quantile(0.25):.0f}-{valid.quantile(0.75):.0f}], n={len(valid):,}")

# ══════════════════════════════════════════════════════════════════════
# 2.3 Community-Level Variables
# ══════════════════════════════════════════════════════════════════════
print("\n2.3 Constructing community-level variables...")

# Community composites from cluster aggregates
cluster_agg = df.groupby("v001").agg(
    com_poverty=("wealth", lambda x: (x <= 2).mean()),       # % poorest/poorer
    com_illit=("medu", lambda x: (x == 0).mean()),           # % no education
    com_uemp=("v714", lambda x: (x == 0).mean()),            # % not working
    com_media=("media2", "mean"),                             # % any media
    n_cluster=("v001", "count"),
).reset_index()

# Community diversity (ethnic fractionalisation within cluster)
def ethnic_frac(x):
    """Compute Herfindahl-based ethnic fractionalisation index."""
    counts = x.value_counts(normalize=True)
    return 1 - (counts ** 2).sum()

cluster_eth = df.groupby("v001")["v131"].apply(ethnic_frac).reset_index(name="com_diversity")
cluster_agg = cluster_agg.merge(cluster_eth, on="v001", how="left")

# Community SES z-score (composite of poverty, illiteracy, unemployment)
from scipy.stats import zscore
cluster_agg["com_zses"] = zscore(
    cluster_agg[["com_poverty", "com_illit", "com_uemp"]].mean(axis=1)
)

# Community dropout rate
cluster_dropout = df.groupby("v001").apply(
    lambda g: np.average(g["vac_dropout"], weights=g["wt"]), include_groups=False
).reset_index(name="community_dropout")

# Cluster DTP coverage
cluster_cov = df.groupby("v001").apply(
    lambda g: np.average(g["vac_dpt3"], weights=g["wt"]), include_groups=False
).reset_index(name="cluster_dtp_coverage")

cluster_agg = cluster_agg.merge(cluster_dropout, on="v001", how="left")
cluster_agg = cluster_agg.merge(cluster_cov, on="v001", how="left")

# Merge back to individual data
df = df.merge(cluster_agg.drop(columns=["n_cluster"]), on="v001", how="left")

# ── Merge geospatial covariates ───────────────────────────────────────
print("  Merging geospatial covariates from NGGC8AFL.csv...")
geo = pd.read_csv(GEO_CSV)
print(f"  Geospatial data: {geo.shape[0]} clusters, {geo.shape[1]} columns")

# Key geospatial vars per CLAUDE.md
geo_vars_wanted = [
    "DHSCLUST",  # cluster ID = v001
    "UN_Population_Density_2020",
    "Travel_Times",
    "Nightlights_Composite",
    "Malaria_Prevalence_2020",
    "ITN_Coverage_2020",
]
geo_vars_present = [v for v in geo_vars_wanted if v in geo.columns]
print(f"  Found {len(geo_vars_present)} of {len(geo_vars_wanted)} geo variables")

if "DHSCLUST" in geo.columns:
    geo_merge = geo[geo_vars_present].rename(columns={"DHSCLUST": "v001"})
    df = df.merge(geo_merge, on="v001", how="left")
    print(f"  Merged {len(geo_vars_present)-1} geospatial variables")
else:
    print("  ⚠ DHSCLUST not found in geospatial CSV. Checking column names...")
    print(f"  Columns: {list(geo.columns[:10])}")

# ── Save updated analytic dataset ─────────────────────────────────────
df.to_csv(PROC / "analytic_dtp1_received.csv", index=False)
df.to_parquet(PROC / "analytic_dtp1_received.parquet", index=False)
print(f"\n  Updated analytic dataset saved: {df.shape[0]:,} rows, {df.shape[1]} cols")

# ── Timeliness cascade figure ─────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Left: Coverage cascade
doses = ["DTP1", "DTP2", "DTP3"]
nat_cov = [nat_dtp1 * 100, nat_dtp2 * 100, nat_dtp3 * 100]
axes[0].bar(doses, nat_cov, color=["#2ecc71", "#f39c12", "#e74c3c"])
for i, v in enumerate(nat_cov):
    axes[0].text(i, v + 1, f"{v:.1f}%", ha="center", fontsize=12)
axes[0].set_ylabel("Coverage (%)")
axes[0].set_title("DTP Coverage Cascade\n(Among DTP1 Recipients)")
axes[0].set_ylim(0, 110)

# Right: Interval distributions
card_intervals = df.loc[card_mask, ["interval_birth_dtp1", "interval_dtp1_dtp2", "interval_dtp2_dtp3"]].melt(
    var_name="interval", value_name="days"
).dropna()
interval_labels = {
    "interval_birth_dtp1": "Birth→DTP1",
    "interval_dtp1_dtp2": "DTP1→DTP2",
    "interval_dtp2_dtp3": "DTP2→DTP3"
}
card_intervals["interval"] = card_intervals["interval"].map(interval_labels)
sns.boxplot(data=card_intervals, x="interval", y="days", ax=axes[1], palette="Set2")
axes[1].set_ylabel("Days")
axes[1].set_title("Inter-Dose Intervals (Card-Confirmed)")
axes[1].set_xlabel("")

plt.tight_layout()
fig.savefig(OUT1 / "cascade_and_intervals.pdf", dpi=300, bbox_inches="tight")
plt.close()
print("  → cascade_and_intervals.pdf saved")

print("\nPhase 2 Cascade Construction complete.")
