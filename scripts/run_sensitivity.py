#!/usr/bin/env python3
"""Sensitivity analysis: CEAC plot, cost-effectiveness plane, tornado diagram.

Uses already-run microsim outputs from outputs/stage3_v2/.
Tornado diagram uses a lightweight one-way sensitivity by varying RRR/cost
for the winning scenario (S3 Risk-Targeted).
"""

from __future__ import annotations

import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from dropout_rl.config import (
    N_BOOTSTRAP_DEFAULT,
    N_POP_DEFAULT,
    PROCESSED_DIR,
    STAGE3_V2_DIR,
)
from dropout_rl.microsim import run_scenario
from dropout_rl.sensitivity import tornado_diagram
from dropout_rl.transitions import load_t1, load_t2

warnings.filterwarnings("ignore")

# -- Load --------------------------------------------------
analytic_df = pd.read_parquet(PROCESSED_DIR / "analytic_dtp1_received.parquet")
t1 = load_t1()
t2 = load_t2()
ceac_df = pd.read_csv(STAGE3_V2_DIR / "ceac_data.csv")

# -- CEAC plot ---------------------------------------------
print("CEAC plot...")
fig, ax = plt.subplots(figsize=(9, 6))
for col in ceac_df.columns:
    if col == "wtp":
        continue
    ax.plot(ceac_df["wtp"], ceac_df[col], label=col, linewidth=2)
ax.set_xlabel("Willingness-to-pay (N per additional DTP3 completion)")
ax.set_ylabel("Probability of being optimal")
ax.set_title("Cost-effectiveness acceptability curves")
ax.legend(loc="center right")
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(STAGE3_V2_DIR / "ceac.pdf", dpi=300)
fig.savefig(STAGE3_V2_DIR / "ceac.png", dpi=300)
plt.close(fig)
print(f"  saved {STAGE3_V2_DIR}/ceac.pdf")

# -- CE plane ----------------------------------------------
print("CE plane...")
psa = pd.read_csv(STAGE3_V2_DIR / "microsim_psa.csv")
s0 = psa[psa["scenario"] == "S0: Status Quo"]

fig, ax = plt.subplots(figsize=(9, 7))
colors = {
    "S1: Uniform SMS": "#81C784",
    "S2: Uniform CHW": "#4FC3F7",
    "S3: Risk-Targeted": "#FFB74D",
    "S4: RL-Optimised": "#E91E63",
    "S5: Bandit-Allocated": "#9C27B0",
}
for name, color in colors.items():
    sub = psa[psa["scenario"] == name]
    if len(sub) == 0:
        continue
    merged = s0[["bootstrap", "dtp3_rate", "cost_per_child"]].rename(
        columns={"dtp3_rate": "s0_dtp3", "cost_per_child": "s0_cost"}
    ).merge(sub, on="bootstrap")
    d_effect = merged["dtp3_rate"] - merged["s0_dtp3"]
    d_cost = merged["cost_per_child"] - merged["s0_cost"]
    ax.scatter(d_effect, d_cost, s=10, alpha=0.3, color=color, label=name)
ax.axhline(0, color="grey", linewidth=0.5)
ax.axvline(0, color="grey", linewidth=0.5)
ax.set_xlabel("Delta DTP3 completion vs S0")
ax.set_ylabel("Delta cost per child (N) vs S0")
ax.set_title("Cost-effectiveness plane (bootstrap x PSA)")
ax.legend()
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(STAGE3_V2_DIR / "ce_plane.pdf", dpi=300)
fig.savefig(STAGE3_V2_DIR / "ce_plane.png", dpi=300)
plt.close(fig)
print(f"  saved {STAGE3_V2_DIR}/ce_plane.pdf")

# -- Tornado: vary S3 risk-targeted parameters -------------
print("Tornado diagram (S3)...")


def s3_action(X, idx):
    risk = t1.predict_dropout(X)
    thr = np.percentile(risk, 70)
    return np.where(risk >= thr, 2, 1).astype(np.int64)


def run_s3_with_scaled_rrr(rrr_scale, cost_scale, n_bootstrap=30):
    """Run S3 with global RRR and cost scaling."""
    from dropout_rl import interventions as iv
    from dropout_rl import costs as cst
    orig_sample_rrr = iv.sample_rrr
    orig_sample_cost = cst.sample_cost

    def scaled_rrr(action, rng):
        return orig_sample_rrr(action, rng) * rrr_scale

    def scaled_cost(action, rng):
        return orig_sample_cost(action, rng) * cost_scale

    iv.sample_rrr = scaled_rrr
    cst.sample_cost = scaled_cost
    try:
        result = run_scenario(
            name="s3_sens",
            policy_fn_t1=s3_action,
            policy_fn_t2=s3_action,
            analytic_df=analytic_df,
            t1_model=t1,
            t2_model=t2,
            n_pop=2000,
            n_bootstrap=n_bootstrap,
            cluster_bootstrap=False,
            psa=True,
            seed=42,
            is_status_quo=False,
            feature_cols=t1.feature_names,
        )
        return float(result.dtp3_rate.mean())
    finally:
        iv.sample_rrr = orig_sample_rrr
        cst.sample_cost = orig_sample_cost


base = run_s3_with_scaled_rrr(1.0, 1.0, n_bootstrap=30)
print(f"  base S3 DTP3: {base:.4f}")

param_results = {
    "RRR (-25%)": (run_s3_with_scaled_rrr(0.75, 1.0, 20), run_s3_with_scaled_rrr(1.25, 1.0, 20)),
    "Cost (-25%)": (run_s3_with_scaled_rrr(1.0, 0.75, 20), run_s3_with_scaled_rrr(1.0, 1.25, 20)),
}

rows = []
for name, (low, high) in param_results.items():
    rows.append({"parameter": name, "low": low, "high": high, "base": base, "range": abs(high - low)})
tornado = pd.DataFrame(rows).sort_values("range", ascending=False).reset_index(drop=True)
tornado.to_csv(STAGE3_V2_DIR / "tornado_data.csv", index=False)

fig, ax = plt.subplots(figsize=(9, 5))
params = tornado["parameter"].tolist()
lows = tornado["low"].values
highs = tornado["high"].values
y_pos = np.arange(len(params))
ax.barh(y_pos, highs - base, left=base, color="#81C784", label="Upper bound")
ax.barh(y_pos, lows - base, left=base, color="#E57373", label="Lower bound")
ax.axvline(base, color="black", linewidth=1)
ax.set_yticks(y_pos)
ax.set_yticklabels(params)
ax.set_xlabel("S3 DTP3 completion rate")
ax.set_title("Tornado diagram: S3 one-way sensitivity")
ax.legend()
fig.tight_layout()
fig.savefig(STAGE3_V2_DIR / "tornado.pdf", dpi=300)
fig.savefig(STAGE3_V2_DIR / "tornado.png", dpi=300)
plt.close(fig)
print(f"  saved {STAGE3_V2_DIR}/tornado.pdf")

print(f"\nAll figures in {STAGE3_V2_DIR}")
