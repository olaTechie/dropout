#!/usr/bin/env python3
"""Stage 2 v2: Offline RL with CQL / IQL / BCQ comparison.

Trains three offline RL algorithms on the same 3-action trajectory dataset,
evaluates each with WIS and FQE (with gamma=0.0 due to cross-sectional DHS
data), selects the best-performing policy for downstream use in the microsim.
"""

from __future__ import annotations

import json
import warnings
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from dropout_rl.config import STAGE2_V2_DIR, PROCESSED_DIR
from dropout_rl.rl.bcq import DiscreteBCQ
from dropout_rl.rl.common import build_mdp_dataset
from dropout_rl.rl.cql import CQL
from dropout_rl.rl.iql import IQL
from dropout_rl.rl.ope import fqe_value, ood_frequency, wis_value
from dropout_rl.transitions import load_t1

warnings.filterwarnings("ignore")
STAGE2_V2_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("STAGE 2 v2: OFFLINE RL — CQL vs IQL vs BCQ (3-ACTION)")
print("=" * 60)

# ── Load data ─────────────────────────────────────────────
traj_df = pd.read_csv(PROCESSED_DIR / "trajectory_dataset.csv")
print(f"Trajectory: {len(traj_df)} rows")

_t1_for_features = load_t1()
dataset = build_mdp_dataset(traj_df, n_actions=3, feature_names=_t1_for_features.feature_names)
print(f"Feature alignment: using {len(_t1_for_features.feature_names)} features from TransitionModel T1")
print(f"MDP dataset: states {dataset['states'].shape}, actions in {set(dataset['actions'])}")

behav_action_dist = np.bincount(dataset["actions"], minlength=3) / len(dataset["actions"])
print(f"Behaviour policy action distribution: {dict(enumerate(behav_action_dist.round(3)))}")

behaviour_probs = np.tile(behav_action_dist, (len(dataset["actions"]), 1))

FQE_GAMMA = 0.0  # Cross-sectional DHS data: immediate reward only
N_ITER_RL = 30  # training iterations per algorithm
N_ITER_FQE = 20

# ── Train three algorithms ────────────────────────────────
results = {}

# CQL with α sensitivity
print("\n--- CQL ---")
cql_candidates = {}
for alpha in [0.5, 1.0, 2.0, 5.0]:
    print(f"  Training CQL(α={alpha})...")
    cql = CQL(n_actions=3, alpha=alpha, n_iterations=N_ITER_RL)
    cql.fit(dataset, rng=np.random.default_rng(42))
    fqe_v = fqe_value(cql.predict_action, dataset, gamma=FQE_GAMMA, n_iterations=N_ITER_FQE)
    wis_v = wis_value(cql.predict_action, dataset, behaviour_probs, epsilon=0.1)
    preds = cql.predict_action(dataset["states"])
    ood = ood_frequency(preds, dataset["actions"], min_behaviour_prob=0.05)
    cql_candidates[alpha] = {
        "model": cql,
        "fqe": fqe_v,
        "wis": wis_v,
        "ood": ood,
    }
    print(f"    FQE={fqe_v:.3f}, WIS={wis_v:.3f}, OOD={ood:.3f}")

# Select best CQL: max FQE subject to OOD ≤ 10%
best_cql = max(
    [(a, r) for a, r in cql_candidates.items() if r["ood"] <= 0.10],
    key=lambda x: x[1]["fqe"],
    default=max(cql_candidates.items(), key=lambda x: x[1]["fqe"]),
)
print(f"  Best CQL: α={best_cql[0]}, FQE={best_cql[1]['fqe']:.3f}, OOD={best_cql[1]['ood']:.3f}")
results["CQL"] = best_cql[1]

# IQL
print("\n--- IQL ---")
iql_candidates = {}
for tau in [0.7, 0.9]:
    for beta in [3.0, 10.0]:
        key = (tau, beta)
        print(f"  Training IQL(τ={tau}, β={beta})...")
        iql = IQL(n_actions=3, tau=tau, beta=beta, n_iterations=N_ITER_RL)
        iql.fit(dataset, rng=np.random.default_rng(42))
        fqe_v = fqe_value(iql.predict_action, dataset, gamma=FQE_GAMMA, n_iterations=N_ITER_FQE)
        wis_v = wis_value(iql.predict_action, dataset, behaviour_probs, epsilon=0.1)
        preds = iql.predict_action(dataset["states"])
        ood = ood_frequency(preds, dataset["actions"], min_behaviour_prob=0.05)
        iql_candidates[key] = {
            "model": iql,
            "fqe": fqe_v,
            "wis": wis_v,
            "ood": ood,
            "tau": tau,
            "beta": beta,
        }
        print(f"    FQE={fqe_v:.3f}, WIS={wis_v:.3f}, OOD={ood:.3f}")
best_iql = max(
    [(k, r) for k, r in iql_candidates.items() if r["ood"] <= 0.10],
    key=lambda x: x[1]["fqe"],
    default=max(iql_candidates.items(), key=lambda x: x[1]["fqe"]),
)
print(f"  Best IQL: {best_iql[0]}, FQE={best_iql[1]['fqe']:.3f}")
results["IQL"] = best_iql[1]

# BCQ
print("\n--- BCQ ---")
bcq = DiscreteBCQ(n_actions=3, threshold=0.3, n_iterations=N_ITER_RL)
bcq.fit(dataset, rng=np.random.default_rng(42))
fqe_v = fqe_value(bcq.predict_action, dataset, gamma=FQE_GAMMA, n_iterations=N_ITER_FQE)
wis_v = wis_value(bcq.predict_action, dataset, behaviour_probs, epsilon=0.1)
preds = bcq.predict_action(dataset["states"])
ood = ood_frequency(preds, dataset["actions"], min_behaviour_prob=0.05)
print(f"  BCQ: FQE={fqe_v:.3f}, WIS={wis_v:.3f}, OOD={ood:.3f}")
results["BCQ"] = {"model": bcq, "fqe": fqe_v, "wis": wis_v, "ood": ood}

# ── Select winner ────────────────────────────────────────
print("\n--- Selection ---")
eligible = {k: v for k, v in results.items() if v["ood"] <= 0.10}
if eligible:
    winner = max(eligible.items(), key=lambda x: x[1]["fqe"])
    print(f"Winner (OOD ≤ 10%, max FQE): {winner[0]}")
else:
    winner = max(results.items(), key=lambda x: x[1]["fqe"])
    print(f"NO algorithm satisfies OOD ≤ 10%. Best by FQE: {winner[0]}")
    print("This is a reportable limitation — discuss in Methods.")

# ── Save outputs ─────────────────────────────────────────
joblib.dump(results["CQL"]["model"], STAGE2_V2_DIR / "cql_model.joblib")
joblib.dump(results["IQL"]["model"], STAGE2_V2_DIR / "iql_model.joblib")
joblib.dump(results["BCQ"]["model"], STAGE2_V2_DIR / "bcq_model.joblib")
joblib.dump(winner[1]["model"], STAGE2_V2_DIR / "selected_policy.joblib")

comparison_df = pd.DataFrame([
    {
        "algorithm": name,
        "fqe": res["fqe"],
        "wis": res["wis"],
        "ood_frequency": res["ood"],
        "is_winner": name == winner[0],
    }
    for name, res in results.items()
])
comparison_df.to_csv(STAGE2_V2_DIR / "ope_comparison.csv", index=False)

summary = {
    "winner": winner[0],
    "winner_fqe": float(winner[1]["fqe"]),
    "winner_wis": float(winner[1]["wis"]),
    "winner_ood": float(winner[1]["ood"]),
    "fqe_gamma": FQE_GAMMA,
    "fqe_gamma_note": "gamma=0.0 used due to cross-sectional DHS data (no next_states)",
    "behaviour_action_distribution": {
        str(i): float(p) for i, p in enumerate(behav_action_dist)
    },
    "n_trajectories": int(len(traj_df)),
    "n_actions": 3,
}
with open(STAGE2_V2_DIR / "stage2_v2_summary.json", "w") as f:
    json.dump(summary, f, indent=2, default=str)

# Selection report
with open(STAGE2_V2_DIR / "algorithm_selection.md", "w") as f:
    f.write(f"# Stage 2 v2 Algorithm Selection\n\n")
    f.write(f"**Winner: {winner[0]}**\n\n")
    f.write(f"Selection criterion: maximum FQE subject to OOD ≤ 10%.\n\n")
    f.write(f"Note: FQE uses gamma=0.0 due to cross-sectional DHS data.\n\n")
    f.write(comparison_df.to_markdown(index=False))
    f.write("\n")

print(f"\nSaved to {STAGE2_V2_DIR}")
