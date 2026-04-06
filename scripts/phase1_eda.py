#!/usr/bin/env python3
"""Phase 1: Exploratory Data Analysis for Nigeria Vaccine Dropout Study.

Outputs → outputs/stage0/
"""

import warnings
warnings.filterwarnings("ignore")

import os
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
DATA_KR = ROOT / "data/dhs/raw/nga_2024/NGKR8BFL.dta"
SHP_STATE = ROOT / "data/shapefiles/gadm/gadm41_NGA_1.shp"
OUT = ROOT / "outputs/stage0"
PROC = ROOT / "data/processed"
OUT.mkdir(parents=True, exist_ok=True)
PROC.mkdir(parents=True, exist_ok=True)

# ── Zone / State label maps ───────────────────────────────────────────
ZONE_MAP = {1: "North Central", 2: "North East", 3: "North West",
            4: "South East", 5: "South South", 6: "South West"}

STATE_MAP = {
    1: "Abia", 2: "Adamawa", 3: "Akwa Ibom", 4: "Anambra", 5: "Bauchi",
    6: "Bayelsa", 7: "Benue", 8: "Borno", 9: "Cross River", 10: "Delta",
    11: "Ebonyi", 12: "Edo", 13: "Ekiti", 14: "Enugu", 15: "Gombe",
    16: "Imo", 17: "Jigawa", 18: "Kaduna", 19: "Kano", 20: "Katsina",
    21: "Kebbi", 22: "Kogi", 23: "Kwara", 24: "Lagos", 25: "Nassarawa",
    26: "Niger", 27: "Ogun", 28: "Ondo", 29: "Osun", 30: "Oyo",
    31: "Plateau", 32: "Rivers", 33: "Sokoto", 34: "Taraba",
    35: "Yobe", 36: "Zamfara", 37: "FCT Abuja"
}

# ── 1. Load and restrict to study population ──────────────────────────
print("Loading DHS KR data...")
keep_vars = [
    # Identifiers
    "v001", "v002", "v003", "caseid",
    # Survey design
    "v005", "v021", "v022",
    # Geography
    "v024", "v025", "szone", "sstate",
    # Demographics
    "v008", "b3", "b4", "b5", "v012", "v201", "bord",
    # Vaccination
    "h3", "h5", "h7",
    "h3d", "h3m", "h3y", "h5d", "h5m", "h5y", "h7d", "h7m", "h7y",
    "h25d", "h25m", "h25y",
    # Predisposing (social structure)
    "v106", "v701", "v505", "v131",
    # Predisposing (health beliefs)
    "v743a", "v467b", "v159", "v158", "v157", "s1112s", "s1112p",
    # Enabling (personal/family)
    "v190", "v191", "v714", "v481", "v136", "v151", "v137",
    # Enabling (community) - v483a
    "v483a",
    # Need
    "h1a", "m14", "m15", "h34", "m70", "m74", "v393", "h69", "h11", "h22",
]

df_raw = pd.read_stata(DATA_KR, columns=keep_vars, convert_categoricals=False)
print(f"  Raw KR: {df_raw.shape[0]:,} rows")

# Age in months
df_raw["age_months"] = df_raw["v008"] - df_raw["b3"]

# Restrict: alive (b5==1), 12-23 months, DTP1 received (h3 in 1,2,3)
mask = (
    (df_raw["b5"] == 1) &
    (df_raw["age_months"].between(12, 23)) &
    (df_raw["h3"].isin([1, 2, 3]))
)
df = df_raw.loc[mask].copy()
print(f"  After restrictions (alive, 12-23mo, DTP1 received): {df.shape[0]:,} rows")

# ── Derive outcomes ───────────────────────────────────────────────────
df["vac_dpt1"] = df["h3"].isin([1, 2, 3]).astype(int)
df["vac_dpt2"] = df["h5"].isin([1, 2, 3]).astype(int)
df["vac_dpt3"] = df["h7"].isin([1, 2, 3]).astype(int)

# Overall dropout: received DTP1 or DTP2 but NOT DTP3
df["vac_dropout"] = (((df["vac_dpt1"] == 1) | (df["vac_dpt2"] == 1)) & (df["vac_dpt3"] == 0)).astype(int)

# Transition dropouts
df["t1_dropout"] = ((df["h3"].isin([1, 3])) & (df["h5"] == 0)).astype(int)
df["t2_dropout"] = np.where(
    df["h5"].isin([1, 2, 3]),
    ((df["h5"].isin([1, 3])) & (df["h7"] == 0)).astype(int),
    np.nan
)

# Survey weight
df["wt"] = df["v005"] / 1e6

# Derived predictors
df["male"] = (df["b4"] == 1).astype(int)
df["mage"] = df["v012"]
df["medu"] = df["v106"]
df["fedu"] = df["v701"]
df["parity"] = df["v201"]
df["wealth"] = df["v190"]
df["rural"] = (df["v025"] == 2).astype(int)

# Media composite
for v in ["v157", "v158", "v159"]:
    df[v] = pd.to_numeric(df[v], errors="coerce")
df["media2"] = ((df["v157"] > 0) | (df["v158"] > 0) | (df["v159"] > 0)).astype(int)

# Birth order group
df["hbord"] = pd.cut(df["bord"], bins=[0, 1, 3, 6, 99], labels=["1", "2-3", "4-6", "7+"])

# Contact count (ANC + facility delivery proxied via m14 + m15)
df["m14"] = pd.to_numeric(df["m14"], errors="coerce")
df["facility_del"] = df["m15"].isin([21, 22, 23, 26, 31, 32, 33, 36]).astype(int)
df["antenat"] = df["m14"].clip(upper=20)
df["contact_count"] = df["antenat"].fillna(0) + df["facility_del"]

# Zone / state labels
df["zone_label"] = df["szone"].map(ZONE_MAP)
df["state_label"] = df["sstate"].map(STATE_MAP)

# Save analytic dataset
df.to_csv(PROC / "analytic_dtp1_received.csv", index=False)
df.to_parquet(PROC / "analytic_dtp1_received.parquet", index=False)
print(f"  Analytic dataset saved: {df.shape[0]:,} rows, {df.shape[1]} cols")

# ── 1.1 ydata-profiling ──────────────────────────────────────────────
print("\n1.1 Generating ydata-profiling report...")
try:
    from ydata_profiling import ProfileReport
    profile = ProfileReport(
        df.drop(columns=["caseid"], errors="ignore"),
        title="Nigeria Vaccine Dropout — Analytic Sample Profile",
        minimal=True,  # faster
        explorative=True,
    )
    profile.to_file(OUT / "dropout_profile_report.html")
    print("  → dropout_profile_report.html saved")
except Exception as e:
    print(f"  ⚠ ydata-profiling failed: {e}")

# ── 1.1b sweetviz comparison ─────────────────────────────────────────
print("\n1.1b Generating sweetviz comparison report...")
try:
    import sweetviz as sv
    compare_cols = [c for c in df.columns if c not in
                    ["caseid", "v001", "v002", "v003", "v005", "v008", "b3"]]
    report = sv.compare(
        [df.loc[df["vac_dropout"] == 1, compare_cols], "Dropout"],
        [df.loc[df["vac_dropout"] == 0, compare_cols], "Completer"],
    )
    report.show_html(filepath=str(OUT / "dropout_sweetviz_report.html"), open_browser=False)
    print("  → dropout_sweetviz_report.html saved")
except Exception as e:
    print(f"  ⚠ sweetviz failed: {e}")

# ── 1.2 TableOne ─────────────────────────────────────────────────────
print("\n1.2 Generating TableOne...")
from tableone import TableOne

tableone_cols = [
    "mage", "male", "bord", "parity", "medu", "fedu",
    "v505", "v131", "v743a", "v467b", "v159", "v158", "v157",
    "media2", "s1112s", "s1112p",
    "wealth", "v714", "v481", "v136", "v151", "v137", "rural",
    "v483a",
    "h1a", "antenat", "facility_del", "h34", "m70", "m74", "v393",
    "h69", "contact_count", "h11", "h22",
    "zone_label",
]
# Keep only columns that exist
tableone_cols = [c for c in tableone_cols if c in df.columns]

categorical = ["male", "medu", "fedu", "v505", "v131", "v743a", "v467b",
               "media2", "s1112s", "s1112p", "wealth", "v714", "v481",
               "v151", "rural", "h1a", "facility_del", "h34",
               "m70", "m74", "v393", "h69", "h11", "h22", "zone_label"]
categorical = [c for c in categorical if c in tableone_cols]

t1 = TableOne(
    df, columns=tableone_cols, categorical=categorical,
    groupby="vac_dropout", pval=True, htest_name=True,
    missing=True,
)
t1.to_csv(OUT / "descriptive_statistics_table.csv")
t1.to_html(OUT / "descriptive_statistics_table.html")
print("  → descriptive_statistics_table.csv/.html saved")

# ── 1.3 State-Level Prevalence ────────────────────────────────────────
print("\n1.3 State-level dropout prevalence...")

state_prev = (
    df.groupby(["sstate", "state_label"])
    .apply(lambda g: pd.Series({
        "n": len(g),
        "n_dropout": g["vac_dropout"].sum(),
        "wt_dropout": np.average(g["vac_dropout"], weights=g["wt"]),
    }), include_groups=False)
    .reset_index()
)
state_prev["prevalence_pct"] = state_prev["wt_dropout"] * 100
state_prev = state_prev.sort_values("prevalence_pct", ascending=True)

# Horizontal bar chart
fig, ax = plt.subplots(figsize=(10, 14))
colors = plt.cm.RdYlGn_r(state_prev["prevalence_pct"] / state_prev["prevalence_pct"].max())
ax.barh(state_prev["state_label"], state_prev["prevalence_pct"], color=colors)
ax.set_xlabel("Weighted Dropout Prevalence (%)")
ax.set_title("DTP1-to-DTP3 Dropout Prevalence by State\n(Children 12–23 months who received DTP1)")
ax.axvline(state_prev["prevalence_pct"].mean(), color="k", ls="--", lw=0.8, label="National mean")
ax.legend()
plt.tight_layout()
fig.savefig(OUT / "dropout_prevalence_by_state.pdf", dpi=300, bbox_inches="tight")
fig.savefig(OUT / "dropout_prevalence_by_state.png", dpi=300, bbox_inches="tight")
plt.close()
print("  → dropout_prevalence_by_state.pdf saved")

# Choropleth
print("  Generating choropleth map...")
import geopandas as gpd

gdf = gpd.read_file(SHP_STATE)

# Merge state-level data — match on NAME_1
# Need to harmonise names
state_prev["state_upper"] = state_prev["state_label"].str.strip().str.title()
gdf["state_upper"] = gdf["NAME_1"].str.strip().str.title()

# Manual fixes for name mismatches
name_fixes = {
    "Nassarawa": "Nasarawa",
    "Fct Abuja": "Federal Capital Territory",
}
state_prev["state_upper"] = state_prev["state_upper"].replace(name_fixes)
# Also check gdf names
gdf_names = set(gdf["state_upper"].values)
sp_names = set(state_prev["state_upper"].values)
unmatched = sp_names - gdf_names
if unmatched:
    print(f"  ⚠ Unmatched state names: {unmatched}")
    # Try fuzzy matching
    for um in unmatched:
        for gn in gdf_names:
            if um[:4].lower() == gn[:4].lower():
                state_prev.loc[state_prev["state_upper"] == um, "state_upper"] = gn
                print(f"    Fixed: {um} → {gn}")

merged = gdf.merge(state_prev, on="state_upper", how="left")

fig, ax = plt.subplots(1, 1, figsize=(12, 10))
merged.plot(
    column="prevalence_pct", ax=ax, legend=True, cmap="RdYlGn_r",
    legend_kwds={"label": "Dropout Prevalence (%)", "shrink": 0.6},
    missing_kwds={"color": "lightgrey", "label": "No data"},
    edgecolor="black", linewidth=0.3,
)
ax.set_title("DTP1→DTP3 Dropout Prevalence by State, Nigeria 2024 DHS", fontsize=14)
ax.axis("off")
plt.tight_layout()
fig.savefig(OUT / "dropout_choropleth_map.pdf", dpi=300, bbox_inches="tight")
fig.savefig(OUT / "dropout_choropleth_map.png", dpi=300, bbox_inches="tight")
plt.close()
print("  → dropout_choropleth_map.pdf saved")

# ── 1.4 Funnel Plot ──────────────────────────────────────────────────
print("\n1.4 Funnel plot...")

national_rate = np.average(df["vac_dropout"], weights=df["wt"])
state_prev["se"] = np.sqrt(state_prev["wt_dropout"] * (1 - state_prev["wt_dropout"]) / state_prev["n"])

fig, ax = plt.subplots(figsize=(10, 7))
ax.scatter(state_prev["n"], state_prev["wt_dropout"] * 100, s=40, zorder=3, c="steelblue")

# CI funnel
n_range = np.linspace(state_prev["n"].min(), state_prev["n"].max(), 300)
for z, ls, label in [(1.96, "--", "95% CI"), (2.576, ":", "99% CI"), (3.0, "-.", "99.7% CI")]:
    se_range = np.sqrt(national_rate * (1 - national_rate) / n_range)
    ax.plot(n_range, (national_rate + z * se_range) * 100, color="grey", ls=ls, lw=0.8, label=label)
    ax.plot(n_range, (national_rate - z * se_range) * 100, color="grey", ls=ls, lw=0.8)

ax.axhline(national_rate * 100, color="red", ls="-", lw=1, label=f"National rate ({national_rate*100:.1f}%)")
ax.set_xlabel("Sample Size (n)")
ax.set_ylabel("Dropout Prevalence (%)")
ax.set_title("Funnel Plot of State-Level DTP1→DTP3 Dropout Rates")
ax.legend(loc="upper right")
plt.tight_layout()
fig.savefig(OUT / "dropout_funnel_plot.pdf", dpi=300, bbox_inches="tight")
fig.savefig(OUT / "dropout_funnel_plot.png", dpi=300, bbox_inches="tight")
plt.close()
print("  → dropout_funnel_plot.pdf saved")

# ── 1.5 Hot/Cold Spot Analysis (Local Moran's I) ─────────────────────
print("\n1.5 Local Moran's I cluster analysis...")
from esda.moran import Moran_Local
from libpysal.weights import Queen

# Use merged geodataframe
merged_valid = merged.dropna(subset=["prevalence_pct"]).copy()
w = Queen.from_dataframe(merged_valid, use_index=False)
w.transform = "r"

moran_loc = Moran_Local(merged_valid["prevalence_pct"].values, w, seed=42)

# Classification
sig = moran_loc.p_sim < 0.05
quadrant = moran_loc.q  # 1=HH, 2=LH, 3=LL, 4=HL
labels = {1: "High-High", 2: "Low-High", 3: "Low-Low", 4: "High-Low", 0: "Not Significant"}
merged_valid["cluster"] = [labels[q] if s else "Not Significant" for q, s in zip(quadrant, sig)]

cluster_colors = {
    "High-High": "#d7191c", "Low-Low": "#2c7bb6",
    "Low-High": "#abd9e9", "High-Low": "#fdae61",
    "Not Significant": "#f0f0f0"
}

fig, ax = plt.subplots(1, 1, figsize=(12, 10))
for cl, color in cluster_colors.items():
    sub = merged_valid[merged_valid["cluster"] == cl]
    if len(sub) > 0:
        sub.plot(ax=ax, color=color, edgecolor="black", linewidth=0.3, label=cl)
ax.legend(title="LISA Cluster", loc="lower left")
ax.set_title("Local Moran's I Clusters — DTP Dropout Prevalence by State", fontsize=14)
ax.axis("off")
plt.tight_layout()
fig.savefig(OUT / "local_moran_clusters_map.pdf", dpi=300, bbox_inches="tight")
fig.savefig(OUT / "local_moran_clusters_map.png", dpi=300, bbox_inches="tight")
plt.close()
print("  → local_moran_clusters_map.pdf saved")
print(f"  Clusters: {merged_valid['cluster'].value_counts().to_dict()}")

# ── 1.6 Zonal Analysis ───────────────────────────────────────────────
print("\n1.6 Zonal analysis...")

zone_stats = (
    df.groupby("zone_label")
    .apply(lambda g: pd.Series({
        "n": len(g),
        "dropout_rate": np.average(g["vac_dropout"], weights=g["wt"]) * 100,
        "dtp3_coverage": np.average(g["vac_dpt3"], weights=g["wt"]) * 100,
    }), include_groups=False)
    .reset_index()
    .sort_values("dropout_rate", ascending=False)
)
print(zone_stats.to_string(index=False))

# Zonal dropout rates
fig, axes = plt.subplots(1, 2, figsize=(16, 7))

# Left: Dropout by zone
sns.barplot(data=zone_stats, x="dropout_rate", y="zone_label", ax=axes[0],
            palette="RdYlGn_r", hue="zone_label", legend=False)
axes[0].set_xlabel("Weighted Dropout Rate (%)")
axes[0].set_title("DTP Dropout Rate by Geopolitical Zone")

# Right: Wealth gradient by zone
wealth_zone = (
    df.groupby(["zone_label", "wealth"])
    .apply(lambda g: np.average(g["vac_dropout"], weights=g["wt"]) * 100, include_groups=False)
    .reset_index(name="dropout_rate")
)
wealth_labels = {1: "Poorest", 2: "Poorer", 3: "Middle", 4: "Richer", 5: "Richest"}
wealth_zone["wealth_label"] = wealth_zone["wealth"].map(wealth_labels)

for zone in ZONE_MAP.values():
    sub = wealth_zone[wealth_zone["zone_label"] == zone].sort_values("wealth")
    axes[1].plot(sub["wealth_label"], sub["dropout_rate"], marker="o", label=zone)
axes[1].set_xlabel("Wealth Quintile")
axes[1].set_ylabel("Dropout Rate (%)")
axes[1].set_title("Wealth Gradient in DTP Dropout by Zone")
axes[1].legend(title="Zone", fontsize=8)
axes[1].tick_params(axis="x", rotation=20)

plt.tight_layout()
fig.savefig(OUT / "zonal_analysis.pdf", dpi=300, bbox_inches="tight")
fig.savefig(OUT / "zonal_analysis.png", dpi=300, bbox_inches="tight")
plt.close()
print("  → zonal_analysis.pdf saved")

# ── Summary stats ─────────────────────────────────────────────────────
print("\n" + "="*60)
print("PHASE 1 SUMMARY")
print("="*60)
n_wt = df["wt"].sum()
print(f"Analytic sample: {df.shape[0]:,} children (weighted N = {n_wt:,.0f})")
print(f"Overall dropout prevalence (weighted): {national_rate*100:.1f}%")
print(f"T1 dropout (DTP1→DTP2): {np.average(df['t1_dropout'], weights=df['wt'])*100:.1f}%")
t2_sub = df.dropna(subset=["t2_dropout"])
if len(t2_sub) > 0:
    print(f"T2 dropout (DTP2→DTP3): {np.average(t2_sub['t2_dropout'], weights=t2_sub['wt'])*100:.1f}%")
print(f"\nOutputs saved to: {OUT}")
print("Phase 1 EDA complete.")
