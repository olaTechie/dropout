#!/usr/bin/env python3
"""Stage 3 v2 sensitivity scenarios S6 (recall-enhanced) and S7 (incentive-poorest).

Uses 5-action space {a0, a1, a2, a3, a4} with literature-informed RRR for
a3 (facility recall) and a4 (conditional incentive). Reported in supplementary.
"""

from __future__ import annotations

import json
import warnings

import numpy as np
import pandas as pd

from dropout_rl.config import (
    N_BOOTSTRAP_DEFAULT,
    N_POP_DEFAULT,
    PROCESSED_DIR,
    STAGE3_V2_DIR,
)
from dropout_rl.microsim import run_scenario
from dropout_rl.transitions import load_t1, load_t2

warnings.filterwarnings("ignore")
STAGE3_V2_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("STAGE 3 v2 SENSITIVITY: S6 (recall) + S7 (incentive)")
print("=" * 60)

analytic_df = pd.read_parquet(PROCESSED_DIR / "analytic_dtp1_received.parquet")
t1 = load_t1()
t2 = load_t2()

# S6: top 10% risk → a3 (recall), next 20% → a2 (CHW), rest → a1 (SMS)
def s6(X, idx):
    risk = t1.predict_dropout(X)
    actions = np.ones(len(X), dtype=np.int64)
    thr_top10 = np.percentile(risk, 90)
    thr_top30 = np.percentile(risk, 70)
    actions[risk >= thr_top30] = 2
    actions[risk >= thr_top10] = 3
    return actions

# S7: poorest quintile → a4, else top-30% risk → a2, rest → a1
def s7(X, idx):
    # Need analytic_df wealth for the sampled indices
    risk = t1.predict_dropout(X)
    actions = np.ones(len(X), dtype=np.int64)
    thr_top30 = np.percentile(risk, 70)
    actions[risk >= thr_top30] = 2
    # Pull wealth from analytic_df via idx
    wealth = analytic_df["wealth"].to_numpy()[idx % len(analytic_df)]
    actions[wealth == 1] = 4
    return actions

scenarios = [
    ("S6: Recall-Enhanced", s6),
    ("S7: Incentive-Poorest", s7),
]

all_results = {}
for name, fn in scenarios:
    print(f"\n  {name}")
    result = run_scenario(
        name=name,
        policy_fn_t1=fn,
        policy_fn_t2=fn,
        analytic_df=analytic_df,
        t1_model=t1,
        t2_model=t2,
        n_pop=N_POP_DEFAULT,
        n_bootstrap=N_BOOTSTRAP_DEFAULT,
        cluster_bootstrap=True,
        psa=True,
        seed=42,
        is_status_quo=False,
        n_actions=5,
        feature_cols=t1.feature_names,
    )
    all_results[name] = {
        "dtp3_mean": float(result.dtp3_rate.mean()),
        "dtp3_ci_low": float(np.percentile(result.dtp3_rate, 2.5)),
        "dtp3_ci_high": float(np.percentile(result.dtp3_rate, 97.5)),
        "cost_per_child_mean": float(result.cost_per_child.mean()),
        "concentration_index_mean": float(result.concentration_index.mean()),
    }
    print(f"    DTP3: {all_results[name]['dtp3_mean']:.3f} "
          f"[{all_results[name]['dtp3_ci_low']:.3f}, "
          f"{all_results[name]['dtp3_ci_high']:.3f}]")
    print(f"    Cost: ₦{all_results[name]['cost_per_child_mean']:.0f}/child")

pd.DataFrame([{"scenario": k, **v} for k, v in all_results.items()]).to_csv(
    STAGE3_V2_DIR / "sensitivity_scenarios.csv", index=False
)
with open(STAGE3_V2_DIR / "sensitivity_scenarios.json", "w") as f:
    json.dump(all_results, f, indent=2, default=str)

print(f"\nSaved to {STAGE3_V2_DIR}/sensitivity_scenarios.*")
