#!/usr/bin/env python3
"""Convert dropout pipeline outputs into tidy JSON for the website.

Reads from outputs/stage1/, outputs/stage3_v2/, outputs/validation/ and writes
optimised JSON files to website/public/data/.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
STAGE1 = REPO / "outputs" / "stage1"
STAGE3 = REPO / "outputs" / "stage3_v2"
VALID = REPO / "outputs" / "validation"
OUT = REPO / "website" / "public" / "data"
OUT.mkdir(parents=True, exist_ok=True)


def round_floats(obj, ndigits: int = 4):
    if isinstance(obj, float):
        if np.isnan(obj) or np.isinf(obj):
            return None
        return round(obj, ndigits)
    if isinstance(obj, dict):
        return {k: round_floats(v, ndigits) for k, v in obj.items()}
    if isinstance(obj, list):
        return [round_floats(v, ndigits) for v in obj]
    return obj


def write_json(name: str, data) -> None:
    path = OUT / f"{name}.json"
    with open(path, "w") as f:
        json.dump(round_floats(data), f, separators=(",", ":"))
    size_kb = path.stat().st_size / 1024
    print(f"  {name}.json ({size_kb:.1f} KB)")


def prepare_cascade():
    df = pd.read_csv(STAGE1 / "cascade_metrics.csv")
    write_json("cascade", df.to_dict(orient="records"))


def prepare_shap():
    with open(STAGE1 / "xgb_results_summary.json") as f:
        xgb = json.load(f)
    summary = {
        model: {
            "andersen_domains": xgb[model].get("andersen_domains", {}),
            "metrics": {k: v for k, v in xgb[model].get("metrics", {}).items()
                        if not isinstance(v, list) or len(v) <= 10},
            "delong": xgb[model].get("delong"),
            "prevalence": xgb[model].get("prevalence"),
            "n": xgb[model].get("n"),
        }
        for model in ["t1", "t2", "full"]
        if model in xgb
    }
    write_json("shap_summary", summary)


def prepare_scenarios():
    df = pd.read_csv(STAGE3 / "microsim_results.csv")
    scenarios = []
    for _, row in df.iterrows():
        scenarios.append({
            "id": row["scenario"],
            "dtp3_mean": float(row["dtp3_mean"]),
            "dtp3_ci_low": float(row["dtp3_ci_low"]),
            "dtp3_ci_high": float(row["dtp3_ci_high"]),
            "cost_per_child_mean": float(row["cost_per_child_mean"]),
            "cost_per_child_ci_low": float(row.get("cost_per_child_ci_low", row["cost_per_child_mean"])),
            "cost_per_child_ci_high": float(row.get("cost_per_child_ci_high", row["cost_per_child_mean"])),
            "concentration_index": float(row.get("concentration_index", 0)),
            "wealth_gap": float(row.get("wealth_gap", 0)),
            "slope_index": float(row.get("slope_index", 0)),
        })
    write_json("scenarios", scenarios)


def prepare_icer():
    df = pd.read_csv(STAGE3 / "icer_distribution.csv")
    write_json("icer", df.to_dict(orient="records"))


def prepare_ceac():
    df = pd.read_csv(STAGE3 / "ceac_data.csv")
    write_json("ceac", df.to_dict(orient="records"))


def prepare_psa_summary():
    """PSA point cloud for CE-plane, thinned to 250 per scenario."""
    df = pd.read_csv(STAGE3 / "microsim_psa.csv")
    out = []
    for scenario, sub in df.groupby("scenario"):
        thinned = sub.sample(n=min(250, len(sub)), random_state=42)
        for _, row in thinned.iterrows():
            out.append({
                "scenario": scenario,
                "dtp3_rate": float(row["dtp3_rate"]),
                "cost_per_child": float(row["cost_per_child"]),
                "concentration_index": float(row.get("concentration_index", 0)),
            })
    write_json("psa_summary", out)


def prepare_validation():
    vdata = {}
    internal_path = VALID / "internal_calibration.json"
    if internal_path.exists():
        with open(internal_path) as f:
            vdata["internal"] = json.load(f)
    for csv in VALID.glob("subgroup_*.csv"):
        key = csv.stem.replace("subgroup_", "")
        vdata.setdefault("subgroups", {})[key] = pd.read_csv(csv).to_dict(orient="records")
    write_json("validation", vdata)


def prepare_cohort_sample():
    """Anonymised sample of 100 trajectories for Act II click vignettes."""
    traj = pd.read_csv(REPO / "data" / "processed" / "trajectory_dataset.csv")
    sample = traj.sample(n=min(100, len(traj)), random_state=42)[
        ["child_id", "dose_step", "action", "reward", "weight"]
    ].copy()
    sample["child_id"] = [f"C{i:04d}" for i in range(len(sample))]
    out = []
    for _, row in sample.iterrows():
        out.append({
            "id": row["child_id"],
            "dose_step": int(row["dose_step"]),
            "action": int(row["action"]),
            "reward": float(row["reward"]),
            "weight": round(float(row["weight"]), 3),
        })
    write_json("cohort_sample", out)


def main():
    print(f"Writing data to: {OUT}")
    prepare_cascade()
    prepare_shap()
    prepare_scenarios()
    prepare_icer()
    prepare_ceac()
    prepare_psa_summary()
    prepare_validation()
    prepare_cohort_sample()
    print("Done.")


if __name__ == "__main__":
    main()
