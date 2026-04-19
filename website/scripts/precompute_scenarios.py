#!/usr/bin/env python3
"""Precompute a scenario cube for client-side interpolation.

Grid: 5 budgets × 5 targeting rules × 3 SMS RRR × 3 CHW RRR = 225 scenarios.
Each runs 100 bootstrap iterations. Output: scenario_cube.json.
"""

from __future__ import annotations

import json
import sys
import warnings
from itertools import product
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from dropout_rl.microsim import run_scenario
from dropout_rl.transitions import load_t1, load_t2
from dropout_rl import config as cfg
from dropout_rl import interventions as iv
from dropout_rl import costs as cst

warnings.filterwarnings("ignore")

OUT = REPO / "website" / "public" / "data"
OUT.mkdir(parents=True, exist_ok=True)

BUDGETS = [250_000_000, 500_000_000, 750_000_000, 1_000_000_000, 1_500_000_000]
TARGETING_RULES = [
    "uniform_sms",
    "uniform_chw",
    "top30_risk",
    "top10_incentive",
    "rl_optimised",
]
SMS_RRR_LEVELS = [0.05, 0.10, 0.15]
CHW_RRR_LEVELS = [0.15, 0.20, 0.25]
N_BOOTSTRAP = 100
N_POP = 5000


def make_policy(rule: str, t1_model):
    def uniform_sms(X, idx):
        return np.ones(len(X), dtype=np.int64)

    def uniform_chw(X, idx):
        return np.full(len(X), 2, dtype=np.int64)

    def top30_risk(X, idx):
        risk = t1_model.predict_dropout(X)
        thr = np.percentile(risk, 70)
        return np.where(risk >= thr, 2, 1).astype(np.int64)

    def top10_incentive(X, idx):
        risk = t1_model.predict_dropout(X)
        thr = np.percentile(risk, 90)
        return np.where(risk >= thr, 2, 1).astype(np.int64)

    def rl_optimised(X, idx):
        import joblib
        path = REPO / "outputs" / "stage2_v2" / "selected_policy.joblib"
        if not path.exists():
            return top30_risk(X, idx)
        policy = joblib.load(path)
        return policy.predict_action(X)

    return {
        "uniform_sms": uniform_sms,
        "uniform_chw": uniform_chw,
        "top30_risk": top30_risk,
        "top10_incentive": top10_incentive,
        "rl_optimised": rl_optimised,
    }[rule]


def patch_priors(sms_rrr: float, chw_rrr: float):
    """Replace the central RRR for a1 and a2 with fixed values for this grid point."""
    orig_rrr = dict(cfg.RRR_RANGES)
    cfg.RRR_RANGES[1] = (sms_rrr, sms_rrr * 0.9, sms_rrr * 1.1)
    cfg.RRR_RANGES[2] = (chw_rrr, chw_rrr * 0.9, chw_rrr * 1.1)
    return orig_rrr


def restore_priors(orig):
    cfg.RRR_RANGES.clear()
    cfg.RRR_RANGES.update(orig)


def main():
    analytic = pd.read_parquet(REPO / "data" / "processed" / "analytic_dtp1_received.parquet")
    t1 = load_t1()
    t2 = load_t2()
    total = len(BUDGETS) * len(TARGETING_RULES) * len(SMS_RRR_LEVELS) * len(CHW_RRR_LEVELS)
    print(f"Precomputing {total} grid points × {N_BOOTSTRAP} bootstraps × {N_POP} pop...")

    results = []
    i = 0
    for budget, rule, sms, chw in product(BUDGETS, TARGETING_RULES, SMS_RRR_LEVELS, CHW_RRR_LEVELS):
        i += 1
        print(f"  [{i}/{total}] budget={budget/1e6:.0f}M, rule={rule}, sms={sms}, chw={chw}")
        orig = patch_priors(sms, chw)
        try:
            policy = make_policy(rule, t1)
            res = run_scenario(
                name=f"g_{i}",
                policy_fn_t1=policy,
                policy_fn_t2=policy,
                analytic_df=analytic,
                t1_model=t1,
                t2_model=t2,
                n_pop=N_POP,
                n_bootstrap=N_BOOTSTRAP,
                cluster_bootstrap=True,
                psa=True,
                seed=42,
                is_status_quo=False,
                feature_cols=t1.feature_names,
            )
            results.append({
                "budget": int(budget),
                "rule": rule,
                "sms_rrr": float(sms),
                "chw_rrr": float(chw),
                "dtp3_mean": float(res.dtp3_rate.mean()),
                "dtp3_ci_low": float(np.percentile(res.dtp3_rate, 2.5)),
                "dtp3_ci_high": float(np.percentile(res.dtp3_rate, 97.5)),
                "cost_per_child": float(res.cost_per_child.mean()),
                "concentration_index": float(res.concentration_index.mean()),
                "wealth_gap": float(res.wealth_gap.mean()),
            })
        finally:
            restore_priors(orig)

    out_path = OUT / "scenario_cube.json"
    with open(out_path, "w") as f:
        json.dump({
            "grid": {
                "budgets": BUDGETS,
                "rules": TARGETING_RULES,
                "sms_rrr": SMS_RRR_LEVELS,
                "chw_rrr": CHW_RRR_LEVELS,
            },
            "points": results,
        }, f, separators=(",", ":"))
    size_kb = out_path.stat().st_size / 1024
    print(f"Wrote scenario_cube.json ({size_kb:.1f} KB)")


if __name__ == "__main__":
    main()
