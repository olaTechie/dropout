#!/usr/bin/env python3
"""Phase 3: Transition-Specific XGBoost with SHAP & Trajectory Export.

Three models:
  T1: predict t1_dropout (DTP1→DTP2)
  T2: predict t2_dropout (DTP2→DTP3, among DTP2 recipients)
  Full: predict overall_dropout

Includes:
- Optuna hyperparameter tuning (200 trials)
- Cluster-robust CV (hold out PSUs)
- AUC-ROC/PR with bootstrap CIs
- DeLong test vs logistic regression
- Calibration curves + Brier decomposition
- SHAP with Andersen domain decomposition
- State space construction + trajectory export

Outputs → outputs/stage1/ and data/processed/
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
import seaborn as sns
from pathlib import Path
from scipy import stats
from sklearn.model_selection import GroupKFold
from sklearn.metrics import (
    roc_auc_score, average_precision_score, brier_score_loss,
    roc_curve, precision_recall_curve, log_loss
)
from sklearn.calibration import calibration_curve
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
import xgboost as xgb
import optuna
import shap

optuna.logging.set_verbosity(optuna.logging.WARNING)

ROOT = Path(__file__).resolve().parent.parent
PROC = ROOT / "data/processed"
OUT1 = ROOT / "outputs/stage1"
OUT1.mkdir(parents=True, exist_ok=True)

# ── Andersen domain mapping ───────────────────────────────────────────
ANDERSEN_MAP = {
    # Predisposing (demographic)
    "mage": "Predisposing", "male": "Predisposing", "bord": "Predisposing",
    "parity": "Predisposing",
    # Predisposing (social structure)
    "medu": "Predisposing", "fedu": "Predisposing", "v505": "Predisposing",
    "v131": "Predisposing",
    # Predisposing (health beliefs)
    "v743a": "Predisposing", "v467b": "Predisposing",
    "v159": "Predisposing", "v158": "Predisposing", "v157": "Predisposing",
    "media2": "Predisposing", "s1112s": "Predisposing", "s1112p": "Predisposing",
    # Enabling (personal/family)
    "wealth": "Enabling", "v714": "Enabling", "v481": "Enabling",
    "v136": "Enabling", "v151": "Enabling", "v137": "Enabling",
    # Enabling (community)
    "rural": "Enabling", "szone": "Enabling", "v483a": "Enabling",
    "com_poverty": "Enabling", "com_illit": "Enabling",
    "com_uemp": "Enabling", "com_media": "Enabling",
    "com_diversity": "Enabling", "com_zses": "Enabling",
    # Enabling (geospatial)
    "UN_Population_Density_2020": "Enabling", "Travel_Times": "Enabling",
    "Nightlights_Composite": "Enabling", "Malaria_Prevalence_2020": "Enabling",
    "ITN_Coverage_2020": "Enabling",
    # Need (perceived)
    "h1a": "Need", "antenat": "Need", "facility_del": "Need",
    "h34": "Need", "m70": "Need", "m74": "Need", "v393": "Need",
    # Need (evaluated)
    "h69": "Need", "contact_count": "Need", "h11": "Need", "h22": "Need",
    # Dynamic/temporal
    "child_age_weeks": "Dynamic", "doses_received": "Dynamic",
    "dose_step": "Dynamic", "last_dose_timely": "Dynamic",
    "inter_dose_interval": "Dynamic", "delay_accumulation": "Dynamic",
    "community_dropout": "Dynamic", "cluster_dtp_coverage": "Dynamic",
}

# ── Feature sets ──────────────────────────────────────────────────────
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

# ── Load data ─────────────────────────────────────────────────────────
print("Loading analytic dataset...")
df = pd.read_parquet(PROC / "analytic_dtp1_received.parquet")
print(f"  {df.shape[0]:,} rows, {df.shape[1]} cols")

# ── Prepare features ──────────────────────────────────────────────────
print("\nPreparing features...")
available = [f for f in STATIC_FEATURES if f in df.columns]
missing_feats = [f for f in STATIC_FEATURES if f not in df.columns]
if missing_feats:
    print(f"  Missing features (will skip): {missing_feats}")
print(f"  Using {len(available)} features")

# Label encode categorical columns for XGBoost
cat_cols = ["v131", "v505", "v743a", "v467b", "h1a", "h34", "m70", "m74",
            "v393", "h69", "h11", "h22", "v151", "szone"]
cat_cols = [c for c in cat_cols if c in available]

le_map = {}
for col in cat_cols:
    df[col] = df[col].fillna(-999)
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col].astype(str))
    le_map[col] = le

# Ensure numeric
for col in available:
    df[col] = pd.to_numeric(df[col], errors="coerce")


# ══════════════════════════════════════════════════════════════════════
# Helper Functions
# ══════════════════════════════════════════════════════════════════════

def delong_test(y_true, y_score1, y_score2):
    """Simplified DeLong test for comparing two AUCs."""
    from scipy.stats import norm
    n1 = np.sum(y_true == 1)
    n0 = np.sum(y_true == 0)
    auc1 = roc_auc_score(y_true, y_score1)
    auc2 = roc_auc_score(y_true, y_score2)

    # Variance estimation via placement values
    pos = y_true == 1
    neg = y_true == 0
    v10_1 = np.array([np.mean(y_score1[neg] < s) for s in y_score1[pos]])
    v10_2 = np.array([np.mean(y_score2[neg] < s) for s in y_score2[pos]])
    v01_1 = np.array([np.mean(y_score1[pos] > s) for s in y_score1[neg]])
    v01_2 = np.array([np.mean(y_score2[pos] > s) for s in y_score2[neg]])

    s10 = np.cov(v10_1, v10_2)
    s01 = np.cov(v01_1, v01_2)
    s = s10 / n1 + s01 / n0

    z = (auc1 - auc2) / np.sqrt(s[0, 0] + s[1, 1] - 2 * s[0, 1])
    p = 2 * norm.sf(abs(z))
    return auc1, auc2, auc1 - auc2, z, p


def bootstrap_auc(y_true, y_score, weights=None, n_boot=1000, seed=42):
    """Bootstrap CI for AUC-ROC and AUC-PR."""
    rng = np.random.RandomState(seed)
    aucs_roc, aucs_pr = [], []
    n = len(y_true)
    for _ in range(n_boot):
        idx = rng.choice(n, n, replace=True)
        if len(np.unique(y_true[idx])) < 2:
            continue
        w = weights[idx] if weights is not None else None
        aucs_roc.append(roc_auc_score(y_true[idx], y_score[idx], sample_weight=w))
        aucs_pr.append(average_precision_score(y_true[idx], y_score[idx], sample_weight=w))
    return {
        "auc_roc": roc_auc_score(y_true, y_score, sample_weight=weights),
        "auc_roc_ci": (np.percentile(aucs_roc, 2.5), np.percentile(aucs_roc, 97.5)),
        "auc_pr": average_precision_score(y_true, y_score, sample_weight=weights),
        "auc_pr_ci": (np.percentile(aucs_pr, 2.5), np.percentile(aucs_pr, 97.5)),
    }


def brier_decomposition(y_true, y_prob, weights=None):
    """Brier score with Spiegelhalter decomposition."""
    if weights is None:
        weights = np.ones(len(y_true))
    weights = weights / weights.sum()

    brier = np.sum(weights * (y_prob - y_true) ** 2)
    mean_prob = np.sum(weights * y_prob)
    mean_obs = np.sum(weights * y_true)

    # Reliability (calibration) component
    n_bins = 10
    bins = np.linspace(0, 1, n_bins + 1)
    reliability = 0
    for i in range(n_bins):
        mask = (y_prob >= bins[i]) & (y_prob < bins[i + 1])
        if mask.sum() == 0:
            continue
        w_bin = weights[mask].sum()
        obs_rate = np.sum(weights[mask] * y_true[mask]) / w_bin
        pred_rate = np.sum(weights[mask] * y_prob[mask]) / w_bin
        reliability += w_bin * (obs_rate - pred_rate) ** 2

    # Resolution component
    resolution = 0
    for i in range(n_bins):
        mask = (y_prob >= bins[i]) & (y_prob < bins[i + 1])
        if mask.sum() == 0:
            continue
        w_bin = weights[mask].sum()
        obs_rate = np.sum(weights[mask] * y_true[mask]) / w_bin
        resolution += w_bin * (obs_rate - mean_obs) ** 2

    uncertainty = mean_obs * (1 - mean_obs)

    return {
        "brier": brier,
        "reliability": reliability,
        "resolution": resolution,
        "uncertainty": uncertainty,
    }


def calibration_slope_intercept(y_true, y_prob):
    """Cox calibration slope and intercept."""
    from statsmodels.api import Logit, add_constant
    logit_p = np.log(np.clip(y_prob, 1e-8, 1 - 1e-8) / (1 - np.clip(y_prob, 1e-8, 1 - 1e-8)))
    X = add_constant(logit_p)
    try:
        model = Logit(y_true, X).fit(disp=0)
        return {"intercept": model.params[0], "slope": model.params[1]}
    except Exception:
        return {"intercept": np.nan, "slope": np.nan}


def plot_calibration(y_true, y_prob, weights, model_name, out_path):
    """Publication-quality calibration plot with histogram."""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 8),
                                     gridspec_kw={"height_ratios": [3, 1]})

    # Calibration curve
    prob_true, prob_pred = calibration_curve(y_true, y_prob, n_bins=10, strategy="quantile")
    ax1.plot(prob_pred, prob_true, "s-", label=model_name, color="steelblue")
    ax1.plot([0, 1], [0, 1], "k--", label="Perfect calibration")
    ax1.set_xlabel("Mean Predicted Probability")
    ax1.set_ylabel("Observed Frequency")
    ax1.set_title(f"Calibration Curve — {model_name}")
    ax1.legend()
    ax1.set_xlim(0, 1)
    ax1.set_ylim(0, 1)

    # Histogram of predictions
    ax2.hist(y_prob, bins=50, color="steelblue", alpha=0.7)
    ax2.set_xlabel("Predicted Probability")
    ax2.set_ylabel("Count")

    plt.tight_layout()
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()


# ══════════════════════════════════════════════════════════════════════
# 3.1 Model Training with Optuna + Cluster-Robust CV
# ══════════════════════════════════════════════════════════════════════

def train_model(df_model, features, target, model_name, n_trials=200):
    """Train XGBoost with Optuna tuning and cluster-robust CV."""
    print(f"\n{'='*60}")
    print(f"Training {model_name}")
    print(f"{'='*60}")

    # Prepare data
    X = df_model[features].copy()
    y = df_model[target].values.astype(int)
    w = df_model["wt"].values
    groups = df_model["v021"].values  # PSU for cluster-robust CV

    print(f"  N={len(y):,}, prevalence={y.mean():.3f}")
    print(f"  Unique PSUs: {len(np.unique(groups)):,}")

    # Cluster-robust CV: hold out entire PSUs
    gkf = GroupKFold(n_splits=5)

    # ── Optuna tuning ──
    print(f"  Optuna tuning ({n_trials} trials)...")

    def objective(trial):
        params = {
            "max_depth": trial.suggest_int("max_depth", 3, 8),
            "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
            "n_estimators": trial.suggest_int("n_estimators", 100, 500),
            "min_child_weight": trial.suggest_int("min_child_weight", 1, 10),
            "subsample": trial.suggest_float("subsample", 0.6, 1.0),
            "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
            "gamma": trial.suggest_float("gamma", 0, 5),
            "reg_alpha": trial.suggest_float("reg_alpha", 1e-8, 10, log=True),
            "reg_lambda": trial.suggest_float("reg_lambda", 1e-8, 10, log=True),
            "scale_pos_weight": trial.suggest_float("scale_pos_weight", 1, 5),
        }

        aucs = []
        for train_idx, val_idx in gkf.split(X, y, groups):
            clf = xgb.XGBClassifier(
                **params, objective="binary:logistic",
                eval_metric="logloss", random_state=42,
                tree_method="hist", verbosity=0, n_jobs=-1
            )
            clf.fit(X.iloc[train_idx], y[train_idx],
                    sample_weight=w[train_idx],
                    eval_set=[(X.iloc[val_idx], y[val_idx])],
                    verbose=False)
            y_pred = clf.predict_proba(X.iloc[val_idx])[:, 1]
            try:
                aucs.append(roc_auc_score(y[val_idx], y_pred, sample_weight=w[val_idx]))
            except ValueError:
                aucs.append(0.5)
        return np.mean(aucs)

    study = optuna.create_study(direction="maximize", sampler=optuna.samplers.TPESampler(seed=42))
    study.optimize(objective, n_trials=n_trials, show_progress_bar=False)

    best_params = study.best_params
    print(f"  Best AUC (CV): {study.best_value:.4f}")
    print(f"  Best params: max_depth={best_params['max_depth']}, "
          f"lr={best_params['learning_rate']:.4f}, "
          f"n_estimators={best_params['n_estimators']}")

    # ── Final model with best params, full CV evaluation ──
    print("  Running final CV evaluation...")

    all_y_true, all_y_prob, all_weights = [], [], []
    all_y_prob_lr = []  # logistic regression baseline
    fold_aucs, fold_shap_values = [], []

    for fold, (train_idx, val_idx) in enumerate(gkf.split(X, y, groups)):
        X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
        y_train, y_val = y[train_idx], y[val_idx]
        w_train, w_val = w[train_idx], w[val_idx]

        # XGBoost
        clf = xgb.XGBClassifier(
            **best_params, objective="binary:logistic",
            eval_metric="logloss", random_state=42,
            tree_method="hist", verbosity=0, n_jobs=-1
        )
        clf.fit(X_train, y_train, sample_weight=w_train, verbose=False)
        y_prob = clf.predict_proba(X_val)[:, 1]

        # Logistic regression baseline
        lr = LogisticRegression(max_iter=1000, random_state=42, solver="lbfgs")
        X_train_filled = X_train.fillna(X_train.median())
        X_val_filled = X_val.fillna(X_train.median())
        lr.fit(X_train_filled, y_train, sample_weight=w_train)
        y_prob_lr = lr.predict_proba(X_val_filled)[:, 1]

        all_y_true.append(y_val)
        all_y_prob.append(y_prob)
        all_weights.append(w_val)
        all_y_prob_lr.append(y_prob_lr)

        auc_fold = roc_auc_score(y_val, y_prob, sample_weight=w_val)
        fold_aucs.append(auc_fold)

        # SHAP on validation fold
        explainer = shap.TreeExplainer(clf)
        shap_vals = explainer.shap_values(X_val)
        fold_shap_values.append(shap_vals)

    all_y_true = np.concatenate(all_y_true)
    all_y_prob = np.concatenate(all_y_prob)
    all_weights = np.concatenate(all_weights)
    all_y_prob_lr = np.concatenate(all_y_prob_lr)
    all_shap = np.concatenate(fold_shap_values, axis=0)

    print(f"  Fold AUCs: {[f'{a:.4f}' for a in fold_aucs]}")
    print(f"  Mean AUC: {np.mean(fold_aucs):.4f} ± {np.std(fold_aucs):.4f}")

    # ── Metrics ──
    metrics = bootstrap_auc(all_y_true, all_y_prob, all_weights)
    brier = brier_decomposition(all_y_true, all_y_prob, all_weights)
    cal = calibration_slope_intercept(all_y_true, all_y_prob)

    print(f"\n  Discrimination:")
    print(f"    AUC-ROC: {metrics['auc_roc']:.4f} (95% CI: {metrics['auc_roc_ci'][0]:.4f}–{metrics['auc_roc_ci'][1]:.4f})")
    print(f"    AUC-PR:  {metrics['auc_pr']:.4f} (95% CI: {metrics['auc_pr_ci'][0]:.4f}–{metrics['auc_pr_ci'][1]:.4f})")
    print(f"  Calibration:")
    print(f"    Brier score: {brier['brier']:.4f}")
    print(f"    Reliability: {brier['reliability']:.4f}")
    print(f"    Resolution:  {brier['resolution']:.4f}")
    print(f"    Cal slope: {cal['slope']:.3f}, Cal intercept: {cal['intercept']:.3f}")

    # DeLong test
    auc_xgb, auc_lr, diff, z_stat, p_val = delong_test(all_y_true, all_y_prob, all_y_prob_lr)
    print(f"\n  DeLong test (XGBoost vs Logistic Regression):")
    print(f"    XGBoost AUC: {auc_xgb:.4f}, LR AUC: {auc_lr:.4f}")
    print(f"    Diff: {diff:.4f}, z={z_stat:.3f}, p={p_val:.4f}")

    # ── Calibration plot ──
    plot_calibration(all_y_true, all_y_prob, all_weights, model_name,
                     OUT1 / f"calibration_{model_name.lower().replace(' ', '_')}.pdf")
    print(f"  → calibration plot saved")

    # ── ROC + PR curves ──
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    fpr, tpr, _ = roc_curve(all_y_true, all_y_prob, sample_weight=all_weights)
    ax1.plot(fpr, tpr, color="steelblue", label=f"XGBoost (AUC={metrics['auc_roc']:.3f})")
    fpr_lr, tpr_lr, _ = roc_curve(all_y_true, all_y_prob_lr, sample_weight=all_weights)
    ax1.plot(fpr_lr, tpr_lr, color="orange", ls="--", label=f"LR (AUC={auc_lr:.3f})")
    ax1.plot([0, 1], [0, 1], "k:", lw=0.8)
    ax1.set_xlabel("False Positive Rate")
    ax1.set_ylabel("True Positive Rate")
    ax1.set_title(f"ROC Curve — {model_name}")
    ax1.legend()

    prec, rec, _ = precision_recall_curve(all_y_true, all_y_prob, sample_weight=all_weights)
    ax2.plot(rec, prec, color="steelblue", label=f"XGBoost (AP={metrics['auc_pr']:.3f})")
    prec_lr, rec_lr, _ = precision_recall_curve(all_y_true, all_y_prob_lr, sample_weight=all_weights)
    ax2.plot(rec_lr, prec_lr, color="orange", ls="--", label=f"LR")
    ax2.set_xlabel("Recall")
    ax2.set_ylabel("Precision")
    ax2.set_title(f"PR Curve — {model_name}")
    ax2.legend()

    plt.tight_layout()
    fig.savefig(OUT1 / f"roc_pr_{model_name.lower().replace(' ', '_')}.pdf", dpi=300, bbox_inches="tight")
    plt.close()

    # ── Train final model on all data ──
    print("  Training final model on full dataset...")
    final_clf = xgb.XGBClassifier(
        **best_params, objective="binary:logistic",
        eval_metric="logloss", random_state=42,
        tree_method="hist", verbosity=0, n_jobs=-1
    )
    final_clf.fit(X, y, sample_weight=w, verbose=False)

    # Save model
    model_path = OUT1 / f"xgb_{model_name.lower().replace(' ', '_')}.json"
    final_clf.save_model(str(model_path))
    print(f"  → Model saved: {model_path.name}")

    results = {
        "model_name": model_name,
        "n": len(y),
        "prevalence": float(y.mean()),
        "best_params": best_params,
        "metrics": {
            "auc_roc": metrics["auc_roc"],
            "auc_roc_ci": list(metrics["auc_roc_ci"]),
            "auc_pr": metrics["auc_pr"],
            "auc_pr_ci": list(metrics["auc_pr_ci"]),
            "brier": brier,
            "calibration": cal,
            "fold_aucs": fold_aucs,
        },
        "delong": {"auc_xgb": auc_xgb, "auc_lr": auc_lr, "diff": diff, "z": z_stat, "p": p_val},
        "features": available,
    }

    return final_clf, all_shap, X, all_y_true, results


def shap_analysis(clf, shap_values, X, model_name, features):
    """SHAP analysis with Andersen domain decomposition."""
    print(f"\n  SHAP analysis for {model_name}...")

    # Global bar plot
    fig, ax = plt.subplots(figsize=(10, 10))
    mean_abs_shap = np.abs(shap_values).mean(axis=0)
    sorted_idx = np.argsort(mean_abs_shap)[-20:]
    ax.barh(range(len(sorted_idx)), mean_abs_shap[sorted_idx], color="steelblue")
    ax.set_yticks(range(len(sorted_idx)))
    ax.set_yticklabels([features[i] for i in sorted_idx])
    ax.set_xlabel("Mean |SHAP value|")
    ax.set_title(f"Top 20 Features — {model_name}")
    plt.tight_layout()
    fig.savefig(OUT1 / f"shap_bar_{model_name.lower().replace(' ', '_')}.pdf", dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  → shap_bar saved")

    # Beeswarm plot
    fig, ax = plt.subplots(figsize=(10, 10))
    shap.summary_plot(shap_values, X, feature_names=features, max_display=20, show=False)
    plt.title(f"SHAP Beeswarm — {model_name}")
    plt.tight_layout()
    plt.savefig(OUT1 / f"shap_beeswarm_{model_name.lower().replace(' ', '_')}.pdf", dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  → shap_beeswarm saved")

    # Andersen domain decomposition
    domain_shap = {}
    for i, feat in enumerate(features):
        domain = ANDERSEN_MAP.get(feat, "Other")
        if domain not in domain_shap:
            domain_shap[domain] = 0
        domain_shap[domain] += mean_abs_shap[i]

    total = sum(domain_shap.values())
    print(f"\n  Andersen Domain Decomposition ({model_name}):")
    for domain in ["Predisposing", "Enabling", "Need", "Dynamic", "Other"]:
        if domain in domain_shap:
            pct = domain_shap[domain] / total * 100
            print(f"    {domain}: {domain_shap[domain]:.4f} ({pct:.1f}%)")

    dominant = max(domain_shap, key=domain_shap.get)
    print(f"    → Dominant domain: {dominant}")

    # Domain decomposition figure
    domains = [d for d in ["Predisposing", "Enabling", "Need", "Dynamic"] if d in domain_shap]
    vals = [domain_shap[d] for d in domains]
    pcts = [v / total * 100 for v in vals]

    fig, ax = plt.subplots(figsize=(8, 5))
    colors = {"Predisposing": "#3498db", "Enabling": "#2ecc71", "Need": "#e74c3c", "Dynamic": "#f39c12"}
    bar_colors = [colors.get(d, "grey") for d in domains]
    ax.bar(domains, pcts, color=bar_colors)
    for i, (d, p) in enumerate(zip(domains, pcts)):
        ax.text(i, p + 0.5, f"{p:.1f}%", ha="center", fontsize=11)
    ax.set_ylabel("% of Total |SHAP| Contribution")
    ax.set_title(f"Andersen Domain Decomposition — {model_name}")
    plt.tight_layout()
    fig.savefig(OUT1 / f"andersen_decomp_{model_name.lower().replace(' ', '_')}.pdf", dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  → andersen_decomp saved")

    return domain_shap


# ══════════════════════════════════════════════════════════════════════
# Run Three Models
# ══════════════════════════════════════════════════════════════════════

print("="*60)
print("PHASE 3: Transition-Specific XGBoost Models")
print("="*60)

all_results = {}

# Model Full: predict overall dropout
print("\n[MODEL FULL] Overall dropout prediction")
df_full = df.dropna(subset=["vac_dropout"]).copy()
clf_full, shap_full, X_full, y_full, res_full = train_model(
    df_full, available, "vac_dropout", "Model Full", n_trials=200
)
domain_full = shap_analysis(clf_full, shap_full, X_full, "Model Full", available)
all_results["full"] = res_full
all_results["full"]["andersen_domains"] = {k: float(v) for k, v in domain_full.items()}

# Model T1: predict T1 dropout (DTP1→DTP2)
print("\n[MODEL T1] DTP1→DTP2 transition dropout")
df_t1 = df.dropna(subset=["t1_dropout"]).copy()
clf_t1, shap_t1, X_t1, y_t1, res_t1 = train_model(
    df_t1, available, "t1_dropout", "Model T1", n_trials=200
)
domain_t1 = shap_analysis(clf_t1, shap_t1, X_t1, "Model T1", available)
all_results["t1"] = res_t1
all_results["t1"]["andersen_domains"] = {k: float(v) for k, v in domain_t1.items()}

# Model T2: predict T2 dropout (DTP2→DTP3, among DTP2 recipients)
print("\n[MODEL T2] DTP2→DTP3 transition dropout (among DTP2 recipients)")
df_t2 = df[df["vac_dpt2"] == 1].dropna(subset=["t2_dropout"]).copy()
df_t2["t2_dropout"] = df_t2["t2_dropout"].astype(int)
clf_t2, shap_t2, X_t2, y_t2, res_t2 = train_model(
    df_t2, available, "t2_dropout", "Model T2", n_trials=200
)
domain_t2 = shap_analysis(clf_t2, shap_t2, X_t2, "Model T2", available)
all_results["t2"] = res_t2
all_results["t2"]["andersen_domains"] = {k: float(v) for k, v in domain_t2.items()}

# Save all results
with open(OUT1 / "xgb_results_summary.json", "w") as f:
    json.dump(all_results, f, indent=2, default=str)
print(f"\n→ xgb_results_summary.json saved")

# ── Hypothesis test: T1 vs T2 domain dominance ──
print("\n" + "="*60)
print("HYPOTHESIS TEST: T1 vs T2 Domain Dominance")
print("="*60)
print("Hypothesis: T1 dominated by Predisposing, T2 by Enabling/Need")
for model_name, domains in [("T1", domain_t1), ("T2", domain_t2)]:
    total = sum(domains.values())
    print(f"\n  {model_name}:")
    for d in ["Predisposing", "Enabling", "Need", "Dynamic"]:
        if d in domains:
            print(f"    {d}: {domains[d]/total*100:.1f}%")


# ══════════════════════════════════════════════════════════════════════
# 3.3 State Space Construction + Trajectory Export
# ══════════════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("3.3 State Space Construction + Trajectory Export")
print("="*60)

# Dynamic/temporal features for state vector
state_features = [
    "child_age_weeks", "doses_received", "dose_step",
    "last_dose_timely", "inter_dose_interval", "delay_accumulation",
    "community_dropout", "cluster_dtp_coverage",
]

# Static features that form part of the state
static_state = [f for f in available if ANDERSEN_MAP.get(f) in ["Predisposing", "Enabling", "Need"]]

# Create child_age_weeks
df["child_age_weeks"] = df["age_months"] * 4.345  # approximate

# Build trajectory rows: each child has up to 3 dose steps
trajectories = []
for _, row in df.iterrows():
    child_id = f"{int(row['v001'])}_{int(row['v002'])}_{int(row['v003'])}"
    base_state = {f: row.get(f, np.nan) for f in static_state if f in row.index}

    # Step 0: After DTP1 received → deciding on DTP2
    state_0 = {**base_state}
    state_0["doses_received"] = 1
    state_0["dose_step"] = 0
    state_0["child_age_weeks"] = row.get("child_age_weeks", np.nan)
    state_0["last_dose_timely"] = float(row.get("dtp1_timely", np.nan)) if pd.notna(row.get("dtp1_timely")) else np.nan
    state_0["inter_dose_interval"] = float(row.get("interval_birth_dtp1", np.nan)) if pd.notna(row.get("interval_birth_dtp1")) else np.nan
    state_0["delay_accumulation"] = float(row.get("delay_dtp1", 0)) if pd.notna(row.get("delay_dtp1")) else 0
    state_0["community_dropout"] = row.get("community_dropout", np.nan)
    state_0["cluster_dtp_coverage"] = row.get("cluster_dtp_coverage", np.nan)

    got_dtp2 = row["vac_dpt2"] == 1

    # Infer action for step 0→1
    if got_dtp2:
        interval = row.get("interval_dtp1_dtp2", np.nan)
        if pd.notna(interval) and interval <= 42:  # on time (≤6 weeks = ≤42 days)
            if row.get("v393") == 1:  # fieldworker visited
                action_0 = 2  # a2: CHW visit
            elif row.get("h1a", 0) >= 1:  # has card
                action_0 = 1  # a1: SMS reminder
            else:
                action_0 = 1
        elif pd.notna(interval) and interval > 42:
            action_0 = 0  # late → weak/no intervention
        else:
            action_0 = 1  # default if we can't determine
        reward_0 = 0.3  # next dose received
    else:
        action_0 = 0  # no effective intervention
        reward_0 = 0.0

    # Next state after step 0
    state_1 = {**base_state}
    state_1["doses_received"] = 2 if got_dtp2 else 1
    state_1["dose_step"] = 1
    state_1["child_age_weeks"] = state_0["child_age_weeks"] + (
        row.get("interval_dtp1_dtp2", 28) / 7 if pd.notna(row.get("interval_dtp1_dtp2")) else 4
    )
    state_1["last_dose_timely"] = float(row.get("dtp2_timely", np.nan)) if pd.notna(row.get("dtp2_timely")) else np.nan
    state_1["inter_dose_interval"] = float(row.get("interval_dtp1_dtp2", np.nan)) if pd.notna(row.get("interval_dtp1_dtp2")) else np.nan
    state_1["delay_accumulation"] = float(row.get("delay_dtp2", 0)) if pd.notna(row.get("delay_dtp2")) else state_0["delay_accumulation"]
    state_1["community_dropout"] = row.get("community_dropout", np.nan)
    state_1["cluster_dtp_coverage"] = row.get("cluster_dtp_coverage", np.nan)

    trajectories.append({
        "child_id": child_id,
        "dose_step": 0,
        "state": json.dumps(state_0, default=str),
        "action": action_0,
        "reward": reward_0,
        "next_state": json.dumps(state_1, default=str),
        "done": 0 if got_dtp2 else 1,
    })

    # Step 1: After DTP2 → deciding on DTP3 (only if got DTP2)
    if got_dtp2:
        got_dtp3 = row["vac_dpt3"] == 1

        if got_dtp3:
            interval = row.get("interval_dtp2_dtp3", np.nan)
            if pd.notna(interval) and interval <= 42:
                if row.get("v393") == 1:
                    action_1 = 2
                elif row.get("h69") == 41:  # campaign
                    action_1 = 3
                elif row.get("h1a", 0) >= 1:
                    action_1 = 1
                else:
                    action_1 = 1
            elif pd.notna(interval) and interval > 42:
                action_1 = 0
            else:
                action_1 = 1
            reward_1 = 1.0  # DTP3 completed!
        else:
            action_1 = 0
            reward_1 = 0.0

        state_2 = {**base_state}
        state_2["doses_received"] = 3 if got_dtp3 else 2
        state_2["dose_step"] = 2
        state_2["child_age_weeks"] = state_1["child_age_weeks"] + (
            row.get("interval_dtp2_dtp3", 28) / 7 if pd.notna(row.get("interval_dtp2_dtp3")) else 4
        )
        state_2["last_dose_timely"] = float(row.get("dtp3_timely", np.nan)) if pd.notna(row.get("dtp3_timely")) else np.nan
        state_2["inter_dose_interval"] = float(row.get("interval_dtp2_dtp3", np.nan)) if pd.notna(row.get("interval_dtp2_dtp3")) else np.nan
        state_2["delay_accumulation"] = float(row.get("delay_dtp3", 0)) if pd.notna(row.get("delay_dtp3")) else state_1["delay_accumulation"]
        state_2["community_dropout"] = row.get("community_dropout", np.nan)
        state_2["cluster_dtp_coverage"] = row.get("cluster_dtp_coverage", np.nan)

        trajectories.append({
            "child_id": child_id,
            "dose_step": 1,
            "state": json.dumps(state_1, default=str),
            "action": action_1,
            "reward": reward_1,
            "next_state": json.dumps(state_2, default=str),
            "done": 1,  # terminal after DTP3 decision
        })

traj_df = pd.DataFrame(trajectories)
traj_df.to_csv(PROC / "trajectory_dataset.csv", index=False)
traj_df.to_csv(OUT1 / "trajectory_dataset.csv", index=False)
print(f"\n  Trajectory dataset: {len(traj_df):,} rows ({traj_df['child_id'].nunique():,} children)")
print(f"  Action distribution:")
print(traj_df["action"].value_counts().sort_index().to_string())

# State space definition
state_space_def = {
    "static_features": static_state,
    "dynamic_features": [f for f in state_features if f != "child_age_weeks"],
    "temporal_features": ["child_age_weeks"],
    "n_static": len(static_state),
    "n_dynamic": len(state_features),
    "total_state_dim": len(static_state) + len(state_features),
    "action_space": {
        "n_actions": 5,
        "actions": {
            "0": "No intervention",
            "1": "SMS reminder",
            "2": "CHW home visit",
            "3": "Facility recall + defaulter tracing",
            "4": "Conditional incentive",
        }
    },
    "reward": {
        "completion": 1.0,
        "next_dose": 0.3,
        "cost_lambda": 0.001,
    },
    "andersen_domain_mapping": {f: ANDERSEN_MAP.get(f, "Other") for f in static_state + state_features},
}

with open(OUT1 / "state_space_definition.json", "w") as f:
    json.dump(state_space_def, f, indent=2)
with open(PROC / "state_space_definition.json", "w") as f:
    json.dump(state_space_def, f, indent=2)
print(f"  → state_space_definition.json saved")
print(f"  State dimension: {state_space_def['total_state_dim']}")

# ── Combined domain decomposition comparison figure ──
fig, axes = plt.subplots(1, 3, figsize=(18, 6))
domains_list = ["Predisposing", "Enabling", "Need", "Dynamic"]
colors = {"Predisposing": "#3498db", "Enabling": "#2ecc71", "Need": "#e74c3c", "Dynamic": "#f39c12"}

for ax, (name, domains) in zip(axes, [("Model T1", domain_t1), ("Model T2", domain_t2), ("Model Full", domain_full)]):
    total = sum(domains.values())
    vals = [domains.get(d, 0) / total * 100 for d in domains_list]
    bar_colors = [colors[d] for d in domains_list]
    ax.bar(domains_list, vals, color=bar_colors)
    for i, v in enumerate(vals):
        ax.text(i, v + 0.5, f"{v:.1f}%", ha="center", fontsize=10)
    ax.set_ylabel("% of Total |SHAP|")
    ax.set_title(name)
    ax.set_ylim(0, max(vals) * 1.2)
    ax.tick_params(axis="x", rotation=20)

plt.suptitle("Andersen Domain Decomposition Across Transition Models", fontsize=14, y=1.02)
plt.tight_layout()
fig.savefig(OUT1 / "andersen_decomp_comparison.pdf", dpi=300, bbox_inches="tight")
plt.close()
print("  → andersen_decomp_comparison.pdf saved")

print("\n" + "="*60)
print("PHASE 3 COMPLETE")
print("="*60)
