#!/usr/bin/env python3
"""Validation: S0 calibration + subgroup calibration checks."""

from __future__ import annotations

import json
import warnings

import numpy as np
import pandas as pd

from dropout_rl.config import PROCESSED_DIR, VALIDATION_DIR
from dropout_rl.microsim import run_scenario
from dropout_rl.transitions import load_t1, load_t2
from dropout_rl.validation import calibration_check, subgroup_calibration

warnings.filterwarnings("ignore")
VALIDATION_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("VALIDATION: S0 CALIBRATION + SUBGROUP CHECKS")
print("=" * 60)

# ── Load ─────────────────────────────────────────────────
analytic_df = pd.read_parquet(PROCESSED_DIR / "analytic_dtp1_received.parquet")
t1 = load_t1()
t2 = load_t2()

# Observed DTP3 rate (survey-weighted)
observed_overall = 1.0 - (analytic_df["vac_dropout"] *
                          analytic_df["v005"] / 1e6).sum() / \
                          (analytic_df["v005"] / 1e6).sum()
print(f"Observed overall DTP3 rate: {observed_overall:.3f}")

# ── S0 microsim on actual sample (no bootstrap) ──────────
def s0_policy(X, idx):
    return np.zeros(len(X), dtype=np.int64)

result = run_scenario(
    name="S0_calibration",
    policy_fn_t1=s0_policy,
    policy_fn_t2=s0_policy,
    analytic_df=analytic_df,
    t1_model=t1,
    t2_model=t2,
    n_pop=len(analytic_df),
    n_bootstrap=50,
    cluster_bootstrap=False,
    psa=False,
    seed=42,
    is_status_quo=True,
    feature_cols=t1.feature_names,
)
predicted_overall = float(result.dtp3_rate.mean())
print(f"Predicted S0 DTP3 rate: {predicted_overall:.3f}")

internal_result = calibration_check(
    predicted_rate=predicted_overall,
    observed_rate=observed_overall,
    tolerance=0.01,
)
print(f"Internal calibration: {'PASS' if internal_result['passed'] else 'FAIL'} "
      f"(error={internal_result['absolute_error']:.4f})")

with open(VALIDATION_DIR / "internal_calibration.json", "w") as f:
    json.dump(internal_result, f, indent=2, default=str)

# ── Subgroup calibration ─────────────────────────────────
def predicted_by_group(analytic_df, group_col, n_bootstrap=30):
    records = []
    groups = analytic_df[group_col].dropna().unique()
    for g in groups:
        sub = analytic_df[analytic_df[group_col] == g]
        if len(sub) < 10:
            continue
        res = run_scenario(
            name=f"g_{g}",
            policy_fn_t1=lambda X, i: np.zeros(len(X), dtype=np.int64),
            policy_fn_t2=lambda X, i: np.zeros(len(X), dtype=np.int64),
            analytic_df=sub,
            t1_model=t1,
            t2_model=t2,
            n_pop=min(500, len(sub)),
            n_bootstrap=n_bootstrap,
            cluster_bootstrap=False,
            psa=False,
            seed=42,
            is_status_quo=True,
            feature_cols=t1.feature_names,
        )
        records.append({"group": g, "rate": float(res.dtp3_rate.mean())})
    return pd.DataFrame(records)


def observed_by_group(analytic_df, group_col):
    df = analytic_df.copy()
    df["dtp3"] = 1 - df["vac_dropout"]
    df["w"] = df["v005"] / 1e6
    rows = []
    for g, sub in df.groupby(group_col):
        w_sum = sub["w"].sum()
        if w_sum == 0 or len(sub) < 10:
            continue
        rate = (sub["dtp3"] * sub["w"]).sum() / w_sum
        rows.append({"group": g, "rate": float(rate)})
    return pd.DataFrame(rows)


subgroup_vars = [
    ("sstate", "state"),
    ("szone", "zone"),
    ("medu", "maternal_education"),
    ("wealth", "wealth_quintile"),
    ("rural", "urban_rural"),
]

all_subgroup_results = {}
for col, label in subgroup_vars:
    if col not in analytic_df.columns:
        continue
    print(f"\nSubgroup: {label} ({col})")
    pred = predicted_by_group(analytic_df, col)
    obs = observed_by_group(analytic_df, col)
    if len(pred) == 0 or len(obs) == 0:
        print(f"  skipped: no groups")
        continue
    check = subgroup_calibration(pred, obs, flag_threshold=0.03)
    check.to_csv(VALIDATION_DIR / f"subgroup_{label}.csv", index=False)
    n_flagged = check["flagged"].sum()
    print(f"  Strata: {len(check)}, flagged: {n_flagged}")
    all_subgroup_results[label] = {
        "n_strata": int(len(check)),
        "n_flagged": int(n_flagged),
        "max_error": float(check["absolute_error"].max()),
    }

with open(VALIDATION_DIR / "subgroup_summary.json", "w") as f:
    json.dump(all_subgroup_results, f, indent=2, default=str)

# Validation report
with open(VALIDATION_DIR / "validation_report.md", "w") as f:
    f.write("# Microsimulation Validation Report\n\n")
    f.write("## Internal Calibration\n\n")
    f.write(f"- Predicted S0 DTP3 rate: {predicted_overall:.4f}\n")
    f.write(f"- Observed DTP3 rate: {observed_overall:.4f}\n")
    f.write(f"- Absolute error: {internal_result['absolute_error']:.4f}\n")
    f.write(f"- Tolerance: {internal_result['tolerance']}\n")
    f.write(f"- **{'PASS' if internal_result['passed'] else 'FAIL'}**\n\n")
    f.write("## Subgroup Calibration\n\n")
    for label, r in all_subgroup_results.items():
        f.write(f"- **{label}**: {r['n_strata']} strata, {r['n_flagged']} flagged "
                f"(max |error| = {r['max_error']:.4f})\n")

print(f"\nSaved to {VALIDATION_DIR}")
