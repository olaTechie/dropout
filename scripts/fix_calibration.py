#!/usr/bin/env python3
"""Fix T1 and T2 XGBoost calibration via isotonic regression.

Problem:
  - T1 calibration slope = 0.87 (underconfident)
  - T2 calibration slope = 1.60 (overconfident)
  Both need recalibration before feeding into the RL pipeline.

Approach:
  1. Reload data and saved best_params for T1 and T2
  2. Re-run 5-fold cluster-robust CV to get out-of-fold predictions
  3. Fit isotonic regression calibrators on OOF predictions
  4. Evaluate recalibrated metrics (slope, intercept, Brier)
  5. Generate before/after calibration figures
  6. Save calibrators as pickle files
  7. Re-export trajectory dataset (unchanged — actions are observation-based)
  8. Update xgb_results_summary.json with recalibrated metrics
"""

import warnings
warnings.filterwarnings("ignore")

import json
import pickle
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.model_selection import GroupKFold
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss
from sklearn.calibration import calibration_curve
from sklearn.isotonic import IsotonicRegression
from sklearn.preprocessing import LabelEncoder
import xgboost as xgb

ROOT = Path(__file__).resolve().parent.parent
PROC = ROOT / "data" / "processed"
OUT1 = ROOT / "outputs" / "stage1"

# ── Feature list (must match phase3_completion.py) ───────────────────
STATIC_FEATURES = [
    "mage", "male", "bord", "parity",
    "medu", "fedu", "v505", "v131",
    "v743a", "v467b", "v159", "v158", "v157", "media2", "s1112s", "s1112p",
    "wealth", "v714", "v481", "v136", "v151", "v137",
    "rural", "szone", "v483a",
    "com_poverty", "com_illit", "com_uemp", "com_media", "com_diversity", "com_zses",
    "UN_Population_Density_2020", "Travel_Times", "Nightlights_Composite",
    "Malaria_Prevalence_2020", "ITN_Coverage_2020",
    "h1a", "antenat", "facility_del", "h34", "m70", "m74", "v393",
    "h69", "contact_count", "h11", "h22",
    "community_dropout", "cluster_dtp_coverage",
]

ANDERSEN_MAP = {
    "mage": "Predisposing", "male": "Predisposing", "bord": "Predisposing",
    "parity": "Predisposing", "medu": "Predisposing", "fedu": "Predisposing",
    "v505": "Predisposing", "v131": "Predisposing", "v743a": "Predisposing",
    "v467b": "Predisposing", "v159": "Predisposing", "v158": "Predisposing",
    "v157": "Predisposing", "media2": "Predisposing", "s1112s": "Predisposing",
    "s1112p": "Predisposing",
    "wealth": "Enabling", "v714": "Enabling", "v481": "Enabling",
    "v136": "Enabling", "v151": "Enabling", "v137": "Enabling",
    "rural": "Enabling", "szone": "Enabling", "v483a": "Enabling",
    "com_poverty": "Enabling", "com_illit": "Enabling", "com_uemp": "Enabling",
    "com_media": "Enabling", "com_diversity": "Enabling", "com_zses": "Enabling",
    "UN_Population_Density_2020": "Enabling", "Travel_Times": "Enabling",
    "Nightlights_Composite": "Enabling", "Malaria_Prevalence_2020": "Enabling",
    "ITN_Coverage_2020": "Enabling",
    "h1a": "Need", "antenat": "Need", "facility_del": "Need",
    "h34": "Need", "m70": "Need", "m74": "Need", "v393": "Need",
    "h69": "Need", "contact_count": "Need", "h11": "Need", "h22": "Need",
    "child_age_weeks": "Dynamic", "doses_received": "Dynamic",
    "dose_step": "Dynamic", "last_dose_timely": "Dynamic",
    "inter_dose_interval": "Dynamic", "delay_accumulation": "Dynamic",
    "community_dropout": "Dynamic", "cluster_dtp_coverage": "Dynamic",
}


# ═══════════════════════════════════════════════════════════════════════
# Helper functions
# ═══════════════════════════════════════════════════════════════════════

def calibration_slope_intercept(y_true, y_prob):
    """Cox calibration slope and intercept via logistic regression on logit(p)."""
    from statsmodels.api import Logit, add_constant
    logit_p = np.log(np.clip(y_prob, 1e-8, 1 - 1e-8) /
                     (1 - np.clip(y_prob, 1e-8, 1 - 1e-8)))
    X = add_constant(logit_p)
    try:
        model = Logit(y_true, X).fit(disp=0)
        return {"intercept": float(model.params[0]), "slope": float(model.params[1])}
    except Exception:
        return {"intercept": float("nan"), "slope": float("nan")}


def brier_decomposition(y_true, y_prob, weights=None):
    """Brier score with reliability/resolution/uncertainty."""
    if weights is None:
        weights = np.ones(len(y_true))
    weights = weights / weights.sum()
    brier = np.sum(weights * (y_prob - y_true) ** 2)
    mean_obs = np.sum(weights * y_true)
    n_bins = 10
    bins = np.linspace(0, 1, n_bins + 1)
    reliability = 0
    resolution = 0
    for i in range(n_bins):
        mask = (y_prob >= bins[i]) & (y_prob < bins[i + 1])
        if mask.sum() == 0:
            continue
        w_bin = weights[mask].sum()
        obs_rate = np.sum(weights[mask] * y_true[mask]) / w_bin
        pred_rate = np.sum(weights[mask] * y_prob[mask]) / w_bin
        reliability += w_bin * (obs_rate - pred_rate) ** 2
        resolution += w_bin * (obs_rate - mean_obs) ** 2
    uncertainty = mean_obs * (1 - mean_obs)
    return {
        "brier": float(brier),
        "reliability": float(reliability),
        "resolution": float(resolution),
        "uncertainty": float(uncertainty),
    }


def plot_calibration_comparison(y_true, y_prob_raw, y_prob_cal, weights,
                                model_name, out_path):
    """Side-by-side calibration curves: raw vs isotonic-calibrated."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10),
                             gridspec_kw={"height_ratios": [3, 1]})

    for col, (probs, label, colour) in enumerate([
        (y_prob_raw, "Raw XGBoost", "#e74c3c"),
        (y_prob_cal, "Isotonic Calibrated", "#2ecc71"),
    ]):
        ax_cal, ax_hist = axes[0, col], axes[1, col]
        prob_true, prob_pred = calibration_curve(y_true, probs,
                                                  n_bins=10, strategy="quantile")
        ax_cal.plot(prob_pred, prob_true, "s-", label=label, color=colour)
        ax_cal.plot([0, 1], [0, 1], "k--", label="Perfect")
        cal = calibration_slope_intercept(y_true, probs)
        brier = brier_score_loss(y_true, probs)
        ax_cal.set_title(f"{label}\nSlope={cal['slope']:.3f}, "
                         f"Intercept={cal['intercept']:.3f}, Brier={brier:.4f}")
        ax_cal.set_xlabel("Mean Predicted Probability")
        ax_cal.set_ylabel("Observed Frequency")
        ax_cal.legend(loc="upper left")
        ax_cal.set_xlim(0, max(0.3, probs.max() * 1.1))
        ax_cal.set_ylim(0, max(0.3, prob_true.max() * 1.3))

        ax_hist.hist(probs, bins=50, color=colour, alpha=0.7)
        ax_hist.set_xlabel("Predicted Probability")
        ax_hist.set_ylabel("Count")

    fig.suptitle(f"Calibration Recalibration — {model_name}", fontsize=14, y=1.01)
    plt.tight_layout()
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()


# ═══════════════════════════════════════════════════════════════════════
# Load data
# ═══════════════════════════════════════════════════════════════════════
print("=" * 60)
print("CALIBRATION FIX: T1 and T2 Isotonic Recalibration")
print("=" * 60)

print("\nLoading analytic dataset...")
df = pd.read_parquet(PROC / "analytic_dtp1_received.parquet")
print(f"  {df.shape[0]:,} rows, {df.shape[1]} cols")

# Prepare features (same label encoding as original)
available = [f for f in STATIC_FEATURES if f in df.columns]
cat_cols = ["v131", "v505", "v743a", "v467b", "h1a", "h34", "m70", "m74",
            "v393", "h69", "h11", "h22", "v151", "szone"]
cat_cols = [c for c in cat_cols if c in available]

le_map = {}
for col in cat_cols:
    df[col] = df[col].fillna(-999)
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col].astype(str))
    le_map[col] = le

for col in available:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Load existing results
with open(OUT1 / "xgb_results_summary.json") as f:
    results = json.load(f)


# ═══════════════════════════════════════════════════════════════════════
# Recalibrate each model
# ═══════════════════════════════════════════════════════════════════════

recal_log = {}

for model_key, target_col, df_filter_fn, model_label in [
    ("t1", "t1_dropout", lambda d: d.dropna(subset=["t1_dropout"]).copy(), "Model T1"),
    ("t2", "t2_dropout",
     lambda d: d[d["vac_dpt2"] == 1].dropna(subset=["t2_dropout"]).copy(), "Model T2"),
]:
    print(f"\n{'='*60}")
    print(f"Recalibrating {model_label}")
    print(f"{'='*60}")

    df_model = df_filter_fn(df)
    if model_key == "t2":
        df_model["t2_dropout"] = df_model["t2_dropout"].astype(int)

    X = df_model[available].copy()
    y = df_model[target_col].values.astype(int)
    w = df_model["wt"].values
    groups = df_model["v021"].values

    print(f"  N={len(y):,}, prevalence={y.mean():.4f}")

    # Load saved best_params
    best_params = results[model_key]["best_params"]
    # Convert types back from JSON
    best_params = {k: (int(v) if k in ("max_depth", "n_estimators", "min_child_weight") else float(v))
                   for k, v in best_params.items()}

    # Original calibration metrics
    orig_cal = results[model_key]["metrics"]["calibration"]
    orig_brier = results[model_key]["metrics"]["brier"]
    print(f"  Original calibration: slope={orig_cal['slope']:.3f}, "
          f"intercept={orig_cal['intercept']:.3f}")
    print(f"  Original Brier: {orig_brier['brier']:.4f}")

    # ── Re-run 5-fold cluster-robust CV to get out-of-fold predictions ──
    print("  Running 5-fold CV for out-of-fold predictions...")
    gkf = GroupKFold(n_splits=5)
    oof_y_true = np.full(len(y), -1, dtype=int)
    oof_y_prob = np.full(len(y), np.nan)
    oof_weights = np.full(len(y), np.nan)

    for fold, (train_idx, val_idx) in enumerate(gkf.split(X, y, groups)):
        clf = xgb.XGBClassifier(
            **best_params, objective="binary:logistic",
            eval_metric="logloss", random_state=42,
            tree_method="hist", verbosity=0, n_jobs=-1
        )
        clf.fit(X.iloc[train_idx], y[train_idx],
                sample_weight=w[train_idx], verbose=False)
        probs = clf.predict_proba(X.iloc[val_idx])[:, 1]
        oof_y_true[val_idx] = y[val_idx]
        oof_y_prob[val_idx] = probs
        oof_weights[val_idx] = w[val_idx]
        auc = roc_auc_score(y[val_idx], probs, sample_weight=w[val_idx])
        print(f"    Fold {fold}: AUC={auc:.4f}")

    # Verify no missing
    assert not np.any(np.isnan(oof_y_prob)), "Missing OOF predictions"

    # ── Fit isotonic regression calibrator ──
    print("  Fitting isotonic regression...")
    iso_reg = IsotonicRegression(y_min=0, y_max=1, out_of_bounds="clip")
    iso_reg.fit(oof_y_prob, oof_y_true, sample_weight=oof_weights)

    # Apply calibration
    oof_y_prob_cal = iso_reg.predict(oof_y_prob)

    # ── Evaluate recalibrated metrics ──
    new_cal = calibration_slope_intercept(oof_y_true, oof_y_prob_cal)
    new_brier = brier_decomposition(oof_y_true, oof_y_prob_cal, oof_weights)

    print(f"\n  Recalibrated metrics:")
    print(f"    Calibration slope:     {orig_cal['slope']:.3f} → {new_cal['slope']:.3f}")
    print(f"    Calibration intercept: {orig_cal['intercept']:.3f} → {new_cal['intercept']:.3f}")
    print(f"    Brier score:           {orig_brier['brier']:.4f} → {new_brier['brier']:.4f}")
    print(f"    Reliability:           {orig_brier['reliability']:.4f} → {new_brier['reliability']:.4f}")

    # ── Save calibrator ──
    cal_path = OUT1 / f"isotonic_calibrator_{model_key}.pkl"
    with open(cal_path, "wb") as f_pkl:
        pickle.dump(iso_reg, f_pkl)
    print(f"  -> Calibrator saved: {cal_path.name}")

    # ── Generate comparison calibration figure ──
    fig_path = OUT1 / f"calibration_{model_label.lower().replace(' ', '_')}_recalibrated.pdf"
    plot_calibration_comparison(
        oof_y_true, oof_y_prob, oof_y_prob_cal, oof_weights,
        model_label, fig_path
    )
    print(f"  -> Calibration figure saved: {fig_path.name}")

    # ── Update results ──
    results[model_key]["metrics"]["calibration_original"] = orig_cal
    results[model_key]["metrics"]["calibration"] = new_cal
    results[model_key]["metrics"]["brier_original"] = orig_brier
    results[model_key]["metrics"]["brier"] = new_brier
    results[model_key]["metrics"]["recalibration_method"] = "isotonic_regression"

    # Log for report
    recal_log[model_key] = {
        "model": model_label,
        "n": int(len(y)),
        "prevalence": float(y.mean()),
        "original": {
            "slope": orig_cal["slope"],
            "intercept": orig_cal["intercept"],
            "brier": orig_brier["brier"],
            "reliability": orig_brier["reliability"],
        },
        "recalibrated": {
            "slope": new_cal["slope"],
            "intercept": new_cal["intercept"],
            "brier": new_brier["brier"],
            "reliability": new_brier["reliability"],
        },
    }


# ═══════════════════════════════════════════════════════════════════════
# Save updated results summary
# ═══════════════════════════════════════════════════════════════════════
with open(OUT1 / "xgb_results_summary.json", "w") as f:
    json.dump(results, f, indent=2, default=str)
print(f"\n-> xgb_results_summary.json updated with recalibrated metrics")


# ═══════════════════════════════════════════════════════════════════════
# Re-export trajectory dataset
# ═══════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("Re-exporting trajectory dataset")
print("=" * 60)

# Reload original (un-label-encoded) data for trajectory construction
df_orig = pd.read_parquet(PROC / "analytic_dtp1_received.parquet")
df_orig["child_age_weeks"] = df_orig["age_months"] * 4.345

# Static features for state vector
static_state = [f for f in available if ANDERSEN_MAP.get(f) in
                ["Predisposing", "Enabling", "Need"]]

# Read old trajectory to compare
old_traj = pd.read_csv(PROC / "trajectory_dataset.csv")
old_action_dist = old_traj["action"].value_counts().sort_index()

trajectories = []
for _, row in df_orig.iterrows():
    child_id = f"{int(row['v001'])}_{int(row['v002'])}_{int(row['v003'])}"
    base_state = {f: (float(row[f]) if pd.notna(row.get(f)) else None)
                  for f in static_state if f in row.index}

    # Step 0: After DTP1 → deciding on DTP2
    state_0 = {**base_state}
    state_0["doses_received"] = 1
    state_0["dose_step"] = 0
    state_0["child_age_weeks"] = float(row.get("child_age_weeks", 0))
    state_0["last_dose_timely"] = (float(row["dtp1_timely"])
                                   if pd.notna(row.get("dtp1_timely")) else None)
    state_0["inter_dose_interval"] = (float(row["interval_birth_dtp1"])
                                      if pd.notna(row.get("interval_birth_dtp1")) else None)
    state_0["delay_accumulation"] = (float(row["delay_dtp1"])
                                     if pd.notna(row.get("delay_dtp1")) else 0.0)
    state_0["community_dropout"] = (float(row["community_dropout"])
                                    if pd.notna(row.get("community_dropout")) else None)
    state_0["cluster_dtp_coverage"] = (float(row["cluster_dtp_coverage"])
                                       if pd.notna(row.get("cluster_dtp_coverage")) else None)

    got_dtp2 = row["vac_dpt2"] == 1

    # Infer action (behaviour policy per CLAUDE.md)
    if got_dtp2:
        interval = row.get("interval_dtp1_dtp2")
        if pd.notna(interval) and interval <= 42:
            if row.get("v393") == 1:
                action_0 = 2
            elif row.get("h1a", 0) >= 1:
                action_0 = 1
            else:
                action_0 = 1
        elif pd.notna(interval) and interval > 42:
            action_0 = 0
        else:
            action_0 = 1
        reward_0 = 0.3
    else:
        action_0 = 0
        reward_0 = 0.0

    # Next state
    state_1 = {**base_state}
    state_1["doses_received"] = 2 if got_dtp2 else 1
    state_1["dose_step"] = 1
    interval_12 = row.get("interval_dtp1_dtp2")
    state_1["child_age_weeks"] = state_0["child_age_weeks"] + (
        float(interval_12) / 7 if pd.notna(interval_12) else 4.0)
    state_1["last_dose_timely"] = (float(row["dtp2_timely"])
                                   if pd.notna(row.get("dtp2_timely")) else None)
    state_1["inter_dose_interval"] = float(interval_12) if pd.notna(interval_12) else None
    state_1["delay_accumulation"] = (float(row["delay_dtp2"])
                                     if pd.notna(row.get("delay_dtp2"))
                                     else state_0["delay_accumulation"])
    state_1["community_dropout"] = (float(row["community_dropout"])
                                    if pd.notna(row.get("community_dropout")) else None)
    state_1["cluster_dtp_coverage"] = (float(row["cluster_dtp_coverage"])
                                       if pd.notna(row.get("cluster_dtp_coverage")) else None)

    trajectories.append({
        "child_id": child_id,
        "dose_step": 0,
        "state": json.dumps(state_0, default=str),
        "action": action_0,
        "reward": reward_0,
        "next_state": json.dumps(state_1, default=str),
        "done": 0 if got_dtp2 else 1,
        "weight": float(row["wt"]),
    })

    # Step 1: After DTP2 → deciding on DTP3
    if got_dtp2:
        got_dtp3 = row["vac_dpt3"] == 1

        if got_dtp3:
            interval_23 = row.get("interval_dtp2_dtp3")
            if pd.notna(interval_23) and interval_23 <= 42:
                if row.get("v393") == 1:
                    action_1 = 2
                elif row.get("h69") == 41:
                    action_1 = 3
                elif row.get("h1a", 0) >= 1:
                    action_1 = 1
                else:
                    action_1 = 1
            elif pd.notna(interval_23) and interval_23 > 42:
                action_1 = 0
            else:
                action_1 = 1
            reward_1 = 1.0
        else:
            action_1 = 0
            reward_1 = 0.0

        state_2 = {**base_state}
        state_2["doses_received"] = 3 if got_dtp3 else 2
        state_2["dose_step"] = 2
        interval_23 = row.get("interval_dtp2_dtp3")
        state_2["child_age_weeks"] = state_1["child_age_weeks"] + (
            float(interval_23) / 7 if pd.notna(interval_23) else 4.0)
        state_2["last_dose_timely"] = (float(row["dtp3_timely"])
                                       if pd.notna(row.get("dtp3_timely")) else None)
        state_2["inter_dose_interval"] = float(interval_23) if pd.notna(interval_23) else None
        state_2["delay_accumulation"] = (float(row["delay_dtp3"])
                                         if pd.notna(row.get("delay_dtp3"))
                                         else state_1["delay_accumulation"])
        state_2["community_dropout"] = (float(row["community_dropout"])
                                        if pd.notna(row.get("community_dropout")) else None)
        state_2["cluster_dtp_coverage"] = (float(row["cluster_dtp_coverage"])
                                           if pd.notna(row.get("cluster_dtp_coverage")) else None)

        trajectories.append({
            "child_id": child_id,
            "dose_step": 1,
            "state": json.dumps(state_1, default=str),
            "action": action_1,
            "reward": reward_1,
            "next_state": json.dumps(state_2, default=str),
            "done": 1,
            "weight": float(row["wt"]),
        })

traj_df = pd.DataFrame(trajectories)

# Compare with old trajectory
new_action_dist = traj_df["action"].value_counts().sort_index()
n_changed = 0
if len(old_traj) == len(traj_df):
    n_changed = int((old_traj["action"].values != traj_df["action"].values).sum())

traj_df.to_csv(PROC / "trajectory_dataset.csv", index=False)
traj_df.to_csv(OUT1 / "trajectory_dataset.csv", index=False)

print(f"  Trajectory dataset: {len(traj_df):,} rows "
      f"({traj_df['child_id'].nunique():,} children)")
print(f"  Action distribution:")
print(traj_df["action"].value_counts().sort_index().to_string())
print(f"\n  Actions changed from previous export: {n_changed}")


# ═══════════════════════════════════════════════════════════════════════
# Write recalibration log
# ═══════════════════════════════════════════════════════════════════════
log_lines = [
    "# Recalibration Log",
    "",
    "**Date**: 2026-04-06",
    "**Method**: Isotonic regression (sklearn.isotonic.IsotonicRegression)",
    "**Approach**: 5-fold cluster-robust CV out-of-fold predictions → fit isotonic → evaluate",
    "",
]

for key in ["t1", "t2"]:
    r = recal_log[key]
    log_lines.extend([
        f"## {r['model']}",
        f"- N = {r['n']:,}, prevalence = {r['prevalence']:.4f}",
        "",
        "| Metric | Original | Recalibrated |",
        "|--------|----------|--------------|",
        f"| Calibration slope | {r['original']['slope']:.4f} | {r['recalibrated']['slope']:.4f} |",
        f"| Calibration intercept | {r['original']['intercept']:.4f} | {r['recalibrated']['intercept']:.4f} |",
        f"| Brier score | {r['original']['brier']:.4f} | {r['recalibrated']['brier']:.4f} |",
        f"| Reliability | {r['original']['reliability']:.4f} | {r['recalibrated']['reliability']:.4f} |",
        "",
    ])

log_lines.extend([
    "## Trajectory Dataset",
    f"- Total rows: {len(traj_df):,}",
    f"- Unique children: {traj_df['child_id'].nunique():,}",
    f"- Actions changed from previous export: {n_changed}",
    "- Note: Behaviour policy actions are inferred from observed DHS data "
    "(intervals, fieldworker visits, card presence), not from model predictions. "
    "The trajectory structure is unchanged; the calibration fix affects model "
    "risk predictions used downstream by the RL agent.",
    "",
    "## Files Updated",
    "- `outputs/stage1/xgb_results_summary.json` — recalibrated metrics added",
    "- `outputs/stage1/isotonic_calibrator_t1.pkl` — T1 calibrator",
    "- `outputs/stage1/isotonic_calibrator_t2.pkl` — T2 calibrator",
    "- `outputs/stage1/calibration_model_t1_recalibrated.pdf` — T1 before/after figure",
    "- `outputs/stage1/calibration_model_t2_recalibrated.pdf` — T2 before/after figure",
    "- `data/processed/trajectory_dataset.csv` — re-exported",
    "- `outputs/stage1/trajectory_dataset.csv` — re-exported",
])

log_text = "\n".join(log_lines) + "\n"
log_path = OUT1 / "recalibration_log.md"
log_path.write_text(log_text)
print(f"\n-> Recalibration log written: {log_path}")

print("\n" + "=" * 60)
print("CALIBRATION FIX: COMPLETE")
print("=" * 60)
