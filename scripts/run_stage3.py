#!/usr/bin/env python3
"""Stage 3 v2: Microsimulation with PSA, cluster-bootstrap, 6 scenarios.

Primary analysis: 6 scenarios using 3-action space {a0, a1, a2}.
"""

from __future__ import annotations

import json
import warnings

import joblib
import numpy as np
import pandas as pd

from dropout_rl.config import (
    N_BOOTSTRAP_DEFAULT,
    N_POP_DEFAULT,
    PROCESSED_DIR,
    STAGE2_V2_DIR,
    STAGE3_V2_DIR,
)
from dropout_rl.microsim import run_scenario
from dropout_rl.sensitivity import ceac, probabilistic_icer
from dropout_rl.transitions import load_t1, load_t2

warnings.filterwarnings("ignore")
STAGE3_V2_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("STAGE 3 v2: MICROSIMULATION (PSA + CLUSTER BOOTSTRAP)")
print("=" * 60)

# ── Load ─────────────────────────────────────────────────
analytic_df = pd.read_parquet(PROCESSED_DIR / "analytic_dtp1_received.parquet")
print(f"Analytic sample: {len(analytic_df)} children, {analytic_df['v021'].nunique()} PSUs")

t1 = load_t1()
t2 = load_t2()
print(f"T1 model: {len(t1.feature_names)} features")

# Selected RL policy from Stage 2
selected_policy = joblib.load(STAGE2_V2_DIR / "selected_policy.joblib")
print(f"Loaded RL policy: {type(selected_policy).__name__}")

# ── Policies ─────────────────────────────────────────────
def s0_t1(X, idx):
    return np.zeros(len(X), dtype=np.int64)

def s0_t2(X, idx):
    return np.zeros(len(X), dtype=np.int64)

def s1(X, idx):
    return np.ones(len(X), dtype=np.int64)

def s2(X, idx):
    return np.full(len(X), 2, dtype=np.int64)

def s3(X, idx):
    risk = t1.predict_dropout(X)
    threshold = np.percentile(risk, 70)
    return np.where(risk >= threshold, 2, 1).astype(np.int64)

def s4(X, idx):
    return selected_policy.predict_action(X)

def s5(X, idx):
    risk = t1.predict_dropout(X)
    threshold = np.percentile(risk, 50)
    return np.where(risk >= threshold, 2, 1).astype(np.int64)

# ── Run scenarios ────────────────────────────────────────
primary_scenarios = [
    ("S0: Status Quo", s0_t1, s0_t2, True),
    ("S1: Uniform SMS", s1, s1, False),
    ("S2: Uniform CHW", s2, s2, False),
    ("S3: Risk-Targeted", s3, s3, False),
    ("S4: RL-Optimised", s4, s4, False),
    ("S5: Bandit-Allocated", s5, s5, False),
]

print(f"\nRunning {len(primary_scenarios)} primary scenarios × {N_BOOTSTRAP_DEFAULT} bootstraps...")

all_results = {}
for name, fn_t1, fn_t2, is_sq in primary_scenarios:
    print(f"\n  {name}{' [SQ]' if is_sq else ''}")
    result = run_scenario(
        name=name,
        policy_fn_t1=fn_t1,
        policy_fn_t2=fn_t2,
        analytic_df=analytic_df,
        t1_model=t1,
        t2_model=t2,
        n_pop=N_POP_DEFAULT,
        n_bootstrap=N_BOOTSTRAP_DEFAULT,
        cluster_bootstrap=True,
        psa=True,
        seed=42,
        is_status_quo=is_sq,
        feature_cols=t1.feature_names,
    )
    all_results[name] = result
    print(f"    DTP3: {result.dtp3_rate.mean():.3f} "
          f"[{np.percentile(result.dtp3_rate, 2.5):.3f}, "
          f"{np.percentile(result.dtp3_rate, 97.5):.3f}]")
    print(f"    Cost: ₦{result.cost_per_child.mean():.0f}/child")
    print(f"    Concentration index: {result.concentration_index.mean():.4f}")

# ── ICER vs S0 ───────────────────────────────────────────
s0 = all_results["S0: Status Quo"]
icer_table = []
print("\n--- Probabilistic ICER vs S0 ---")
for name, res in all_results.items():
    if name == "S0: Status Quo":
        continue
    icer = probabilistic_icer(res, s0)
    icer["scenario"] = name
    icer_table.append(icer)
    print(f"  {name}: ICER=₦{icer['mean_icer']:,.0f} "
          f"dominant={icer['n_dominant']}/{N_BOOTSTRAP_DEFAULT}")

# ── CEAC ──────────────────────────────────────────────────
wtp_range = np.linspace(0, 100_000, 101)
ceac_df = ceac(list(all_results.values()), wtp_range=wtp_range, reference="S0: Status Quo")
ceac_df.to_csv(STAGE3_V2_DIR / "ceac_data.csv", index=False)

# ── Save ─────────────────────────────────────────────────
summary_rows = []
for name, res in all_results.items():
    summary_rows.append({
        "scenario": name,
        "dtp3_mean": float(res.dtp3_rate.mean()),
        "dtp3_ci_low": float(np.percentile(res.dtp3_rate, 2.5)),
        "dtp3_ci_high": float(np.percentile(res.dtp3_rate, 97.5)),
        "cost_per_child_mean": float(res.cost_per_child.mean()),
        "cost_per_child_ci_low": float(np.percentile(res.cost_per_child, 2.5)),
        "cost_per_child_ci_high": float(np.percentile(res.cost_per_child, 97.5)),
        "concentration_index": float(res.concentration_index.mean()),
        "wealth_gap": float(res.wealth_gap.mean()),
        "slope_index": float(res.slope_index.mean()),
    })
pd.DataFrame(summary_rows).to_csv(STAGE3_V2_DIR / "microsim_results.csv", index=False)
pd.DataFrame(icer_table).to_csv(STAGE3_V2_DIR / "icer_distribution.csv", index=False)

# Full PSA draws
psa_rows = []
for name, res in all_results.items():
    for b in range(len(res.dtp3_rate)):
        psa_rows.append({
            "scenario": name,
            "bootstrap": b,
            "dtp3_rate": float(res.dtp3_rate[b]),
            "cost_per_child": float(res.cost_per_child[b]),
            "concentration_index": float(res.concentration_index[b]),
        })
pd.DataFrame(psa_rows).to_csv(STAGE3_V2_DIR / "microsim_psa.csv", index=False)

stage3_summary = {
    "n_primary_scenarios": len(primary_scenarios),
    "n_bootstrap": N_BOOTSTRAP_DEFAULT,
    "n_pop_per_bootstrap": N_POP_DEFAULT,
    "cluster_bootstrap": True,
    "psa_enabled": True,
    "action_space": [0, 1, 2],
    "scenario_summary": {name: {
        "dtp3_mean": float(res.dtp3_rate.mean()),
        "cost_per_child_mean": float(res.cost_per_child.mean()),
        "concentration_index_mean": float(res.concentration_index.mean()),
    } for name, res in all_results.items()},
}
with open(STAGE3_V2_DIR / "stage3_v2_summary.json", "w") as f:
    json.dump(stage3_summary, f, indent=2, default=str)

print(f"\nSaved to {STAGE3_V2_DIR}")
