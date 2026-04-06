#!/usr/bin/env python3
"""Phase 3 Completion: T1, T2 models + trajectory export.

Model Full already completed. This script runs:
  1. Model T1: predict t1_dropout (DTP1->DTP2)
  2. Model T2: predict t2_dropout (DTP2->DTP3, among DTP2 recipients)
  3. SHAP comparison figure across all three models
  4. Trajectory dataset export (s, a, r, s' tuples)
  5. State space definition export
"""

import warnings
warnings.filterwarnings("ignore")

import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from scipy import stats
from sklearn.model_selection import GroupKFold
from sklearn.metrics import (
    roc_auc_score, average_precision_score, brier_score_loss,
    roc_curve, precision_recall_curve
)
from sklearn.calibration import calibration_curve
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


# ══════════════════════════════════════════════════════════════════════
# Load data
# ══════════════════════════════════════════════════════════════════════
print("Loading analytic dataset...")
df = pd.read_parquet(PROC / "analytic_dtp1_received.parquet")
print(f"  {df.shape[0]:,} rows, {df.shape[1]} cols")

# Prepare features
available = [f for f in STATIC_FEATURES if f in df.columns]
missing_feats = [f for f in STATIC_FEATURES if f not in df.columns]
if missing_feats:
    print(f"  Missing features (will skip): {missing_feats}")
print(f"  Using {len(available)} features")

# Label encode categorical columns
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


def calibration_slope_intercept(y_true, y_prob):
    """Cox calibration slope and intercept."""
    from statsmodels.api import Logit, add_constant
    logit_p = np.log(np.clip(y_prob, 1e-8, 1 - 1e-8) / (1 - np.clip(y_prob, 1e-8, 1 - 1e-8)))
    X = add_constant(logit_p)
    try:
        model = Logit(y_true, X).fit(disp=0)
        return {"intercept": float(model.params[0]), "slope": float(model.params[1])}
    except Exception:
        return {"intercept": float("nan"), "slope": float("nan")}


def plot_calibration(y_true, y_prob, weights, model_name, out_path):
    """Publication-quality calibration plot with histogram."""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 8),
                                     gridspec_kw={"height_ratios": [3, 1]})
    prob_true, prob_pred = calibration_curve(y_true, y_prob, n_bins=10, strategy="quantile")
    ax1.plot(prob_pred, prob_true, "s-", label=model_name, color="steelblue")
    ax1.plot([0, 1], [0, 1], "k--", label="Perfect calibration")
    ax1.set_xlabel("Mean Predicted Probability")
    ax1.set_ylabel("Observed Frequency")
    ax1.set_title(f"Calibration Curve — {model_name}")
    ax1.legend()
    ax1.set_xlim(0, 1)
    ax1.set_ylim(0, 1)
    ax2.hist(y_prob, bins=50, color="steelblue", alpha=0.7)
    ax2.set_xlabel("Predicted Probability")
    ax2.set_ylabel("Count")
    plt.tight_layout()
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()


# ══════════════════════════════════════════════════════════════════════
# Model training function
# ══════════════════════════════════════════════════════════════════════

def train_model(df_model, features, target, model_name, n_trials=200):
    """Train XGBoost with Optuna tuning and cluster-robust CV."""
    print(f"\n{'='*60}")
    print(f"Training {model_name}")
    print(f"{'='*60}")

    X = df_model[features].copy()
    y = df_model[target].values.astype(int)
    w = df_model["wt"].values
    groups = df_model["v021"].values

    print(f"  N={len(y):,}, prevalence={y.mean():.3f}")
    print(f"  Unique PSUs: {len(np.unique(groups)):,}")

    gkf = GroupKFold(n_splits=5)

    # Optuna tuning
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

    # Final CV evaluation
    print("  Running final CV evaluation...")
    all_y_true, all_y_prob, all_weights = [], [], []
    all_y_prob_lr = []
    fold_aucs, fold_shap_values = [], []

    for fold, (train_idx, val_idx) in enumerate(gkf.split(X, y, groups)):
        X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
        y_train, y_val = y[train_idx], y[val_idx]
        w_train, w_val = w[train_idx], w[val_idx]

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

        # SHAP on validation fold (test-set only as per literature reviewer)
        explainer = shap.TreeExplainer(clf)
        shap_vals = explainer.shap_values(X_val)
        fold_shap_values.append(shap_vals)

    all_y_true = np.concatenate(all_y_true)
    all_y_prob = np.concatenate(all_y_prob)
    all_weights = np.concatenate(all_weights)
    all_y_prob_lr = np.concatenate(all_y_prob_lr)
    all_shap = np.concatenate(fold_shap_values, axis=0)

    print(f"  Fold AUCs: {[f'{a:.4f}' for a in fold_aucs]}")
    print(f"  Mean AUC: {np.mean(fold_aucs):.4f} +/- {np.std(fold_aucs):.4f}")

    # Metrics
    metrics = bootstrap_auc(all_y_true, all_y_prob, all_weights)
    brier = brier_decomposition(all_y_true, all_y_prob, all_weights)
    cal = calibration_slope_intercept(all_y_true, all_y_prob)

    print(f"\n  Discrimination:")
    print(f"    AUC-ROC: {metrics['auc_roc']:.4f} (95% CI: {metrics['auc_roc_ci'][0]:.4f}-{metrics['auc_roc_ci'][1]:.4f})")
    print(f"    AUC-PR:  {metrics['auc_pr']:.4f} (95% CI: {metrics['auc_pr_ci'][0]:.4f}-{metrics['auc_pr_ci'][1]:.4f})")
    print(f"  Calibration:")
    print(f"    Brier score: {brier['brier']:.4f}")
    print(f"    Reliability: {brier['reliability']:.4f}")
    print(f"    Resolution:  {brier['resolution']:.4f}")
    print(f"    Cal slope: {cal['slope']:.3f}, Cal intercept: {cal['intercept']:.3f}")

    # DeLong test
    auc_xgb, auc_lr, diff, z_stat, p_val = delong_test(all_y_true, all_y_prob, all_y_prob_lr)
    print(f"\n  DeLong test (XGBoost vs LR):")
    print(f"    XGBoost AUC: {auc_xgb:.4f}, LR AUC: {auc_lr:.4f}")
    print(f"    Diff: {diff:.4f}, z={z_stat:.3f}, p={p_val:.4f}")

    # Calibration plot
    plot_calibration(all_y_true, all_y_prob, all_weights, model_name,
                     OUT1 / f"calibration_{model_name.lower().replace(' ', '_')}.pdf")
    print(f"  -> calibration plot saved")

    # ROC + PR curves
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    fpr, tpr, _ = roc_curve(all_y_true, all_y_prob, sample_weight=all_weights)
    ax1.plot(fpr, tpr, color="steelblue", label=f"XGBoost (AUC={metrics['auc_roc']:.3f})")
    fpr_lr, tpr_lr, _ = roc_curve(all_y_true, all_y_prob_lr, sample_weight=all_weights)
    ax1.plot(fpr_lr, tpr_lr, color="orange", ls="--", label=f"LR (AUC={auc_lr:.3f})")
    ax1.plot([0, 1], [0, 1], "k:", lw=0.8)
    ax1.set_xlabel("False Positive Rate")
    ax1.set_ylabel("True Positive Rate")
    ax1.set_title(f"ROC Curve - {model_name}")
    ax1.legend()

    prec, rec, _ = precision_recall_curve(all_y_true, all_y_prob, sample_weight=all_weights)
    ax2.plot(rec, prec, color="steelblue", label=f"XGBoost (AP={metrics['auc_pr']:.3f})")
    prec_lr, rec_lr, _ = precision_recall_curve(all_y_true, all_y_prob_lr, sample_weight=all_weights)
    ax2.plot(rec_lr, prec_lr, color="orange", ls="--", label="LR")
    ax2.set_xlabel("Recall")
    ax2.set_ylabel("Precision")
    ax2.set_title(f"PR Curve - {model_name}")
    ax2.legend()

    plt.tight_layout()
    fig.savefig(OUT1 / f"roc_pr_{model_name.lower().replace(' ', '_')}.pdf", dpi=300, bbox_inches="tight")
    plt.close()

    # Train final model on all data
    print("  Training final model on full dataset...")
    final_clf = xgb.XGBClassifier(
        **best_params, objective="binary:logistic",
        eval_metric="logloss", random_state=42,
        tree_method="hist", verbosity=0, n_jobs=-1
    )
    final_clf.fit(X, y, sample_weight=w, verbose=False)

    model_path = OUT1 / f"xgb_{model_name.lower().replace(' ', '_')}.json"
    final_clf.save_model(str(model_path))
    print(f"  -> Model saved: {model_path.name}")

    results = {
        "model_name": model_name,
        "n": int(len(y)),
        "prevalence": float(y.mean()),
        "best_params": {k: float(v) if isinstance(v, (np.floating, float)) else int(v) if isinstance(v, (np.integer, int)) else v for k, v in best_params.items()},
        "metrics": {
            "auc_roc": float(metrics["auc_roc"]),
            "auc_roc_ci": [float(x) for x in metrics["auc_roc_ci"]],
            "auc_pr": float(metrics["auc_pr"]),
            "auc_pr_ci": [float(x) for x in metrics["auc_pr_ci"]],
            "brier": brier,
            "calibration": cal,
            "fold_aucs": [float(x) for x in fold_aucs],
        },
        "delong": {
            "auc_xgb": float(auc_xgb), "auc_lr": float(auc_lr),
            "diff": float(diff), "z": float(z_stat), "p": float(p_val)
        },
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
    ax.set_title(f"Top 20 Features - {model_name}")
    plt.tight_layout()
    fig.savefig(OUT1 / f"shap_bar_{model_name.lower().replace(' ', '_')}.pdf", dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  -> shap_bar saved")

    # Beeswarm plot
    fig, ax = plt.subplots(figsize=(10, 10))
    shap.summary_plot(shap_values, X, feature_names=features, max_display=20, show=False)
    plt.title(f"SHAP Beeswarm - {model_name}")
    plt.tight_layout()
    plt.savefig(OUT1 / f"shap_beeswarm_{model_name.lower().replace(' ', '_')}.pdf", dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  -> shap_beeswarm saved")

    # Andersen domain decomposition
    domain_shap = {}
    for i, feat in enumerate(features):
        domain = ANDERSEN_MAP.get(feat, "Other")
        domain_shap[domain] = domain_shap.get(domain, 0) + mean_abs_shap[i]

    total = sum(domain_shap.values())
    print(f"\n  Andersen Domain Decomposition ({model_name}):")
    for domain in ["Predisposing", "Enabling", "Need", "Dynamic", "Other"]:
        if domain in domain_shap:
            pct = domain_shap[domain] / total * 100
            print(f"    {domain}: {domain_shap[domain]:.4f} ({pct:.1f}%)")

    dominant = max(domain_shap, key=domain_shap.get)
    print(f"    -> Dominant domain: {dominant}")

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
    ax.set_title(f"Andersen Domain Decomposition - {model_name}")
    plt.tight_layout()
    fig.savefig(OUT1 / f"andersen_decomp_{model_name.lower().replace(' ', '_')}.pdf", dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  -> andersen_decomp saved")

    return domain_shap


# ══════════════════════════════════════════════════════════════════════
# Run T1 and T2 models
# ══════════════════════════════════════════════════════════════════════

print("=" * 60)
print("PHASE 3 COMPLETION: T1 + T2 Models + Trajectory Export")
print("=" * 60)

all_results = {}

# ── Load model_full results if available ──
full_results_path = OUT1 / "xgb_results_summary.json"
if full_results_path.exists():
    with open(full_results_path) as f:
        saved = json.load(f)
        if "full" in saved:
            all_results["full"] = saved["full"]
            print("\n[MODEL FULL] Loaded existing results from xgb_results_summary.json")

# ── Model T1: predict T1 dropout (DTP1->DTP2) ──
print("\n[MODEL T1] DTP1->DTP2 transition dropout")
df_t1 = df.dropna(subset=["t1_dropout"]).copy()
print(f"  T1 dropout prevalence: {df_t1['t1_dropout'].mean():.3f} (N={len(df_t1):,})")
clf_t1, shap_t1, X_t1, y_t1, res_t1 = train_model(
    df_t1, available, "t1_dropout", "Model T1", n_trials=200
)
domain_t1 = shap_analysis(clf_t1, shap_t1, X_t1, "Model T1", available)
all_results["t1"] = res_t1
all_results["t1"]["andersen_domains"] = {k: float(v) for k, v in domain_t1.items()}

# ── Model T2: predict T2 dropout (DTP2->DTP3, among DTP2 recipients) ──
print("\n[MODEL T2] DTP2->DTP3 transition dropout (among DTP2 recipients)")
df_t2 = df[df["vac_dpt2"] == 1].dropna(subset=["t2_dropout"]).copy()
df_t2["t2_dropout"] = df_t2["t2_dropout"].astype(int)
print(f"  T2 dropout prevalence: {df_t2['t2_dropout'].mean():.3f} (N={len(df_t2):,})")
clf_t2, shap_t2, X_t2, y_t2, res_t2 = train_model(
    df_t2, available, "t2_dropout", "Model T2", n_trials=200
)
domain_t2 = shap_analysis(clf_t2, shap_t2, X_t2, "Model T2", available)
all_results["t2"] = res_t2
all_results["t2"]["andersen_domains"] = {k: float(v) for k, v in domain_t2.items()}

# ── Save combined results ──
with open(OUT1 / "xgb_results_summary.json", "w") as f:
    json.dump(all_results, f, indent=2, default=str)
print(f"\n-> xgb_results_summary.json saved")


# ══════════════════════════════════════════════════════════════════════
# Hypothesis test: T1 vs T2 domain dominance
# ══════════════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("HYPOTHESIS TEST: T1 vs T2 Domain Dominance")
print("=" * 60)
print("Hypothesis: T1 dominated by Predisposing, T2 by Enabling/Need")
for model_name, domains in [("T1", domain_t1), ("T2", domain_t2)]:
    total = sum(domains.values())
    print(f"\n  {model_name}:")
    for d in ["Predisposing", "Enabling", "Need", "Dynamic"]:
        if d in domains:
            print(f"    {d}: {domains[d]/total*100:.1f}%")


# ══════════════════════════════════════════════════════════════════════
# Combined Andersen decomposition comparison figure
# ══════════════════════════════════════════════════════════════════════

# Load model_full domain decomposition from saved results or recalculate
domain_full = all_results.get("full", {}).get("andersen_domains", {})
if not domain_full:
    # Reload model_full and compute SHAP
    print("\n  Reloading Model Full for comparison figure...")
    clf_full_loaded = xgb.XGBClassifier()
    clf_full_loaded.load_model(str(OUT1 / "xgb_model_full.json"))
    df_full = df.dropna(subset=["vac_dropout"]).copy()
    X_full = df_full[available].copy()
    explainer_full = shap.TreeExplainer(clf_full_loaded)
    shap_full = explainer_full.shap_values(X_full)
    mean_abs_full = np.abs(shap_full).mean(axis=0)
    domain_full = {}
    for i, feat in enumerate(available):
        domain = ANDERSEN_MAP.get(feat, "Other")
        domain_full[domain] = domain_full.get(domain, 0) + float(mean_abs_full[i])
    all_results.setdefault("full", {})["andersen_domains"] = domain_full
    with open(OUT1 / "xgb_results_summary.json", "w") as f:
        json.dump(all_results, f, indent=2, default=str)

fig, axes = plt.subplots(1, 3, figsize=(18, 6))
domains_list = ["Predisposing", "Enabling", "Need", "Dynamic"]
colors = {"Predisposing": "#3498db", "Enabling": "#2ecc71", "Need": "#e74c3c", "Dynamic": "#f39c12"}

for ax, (name, domains) in zip(axes, [("Model T1\n(DTP1->DTP2)", domain_t1),
                                       ("Model T2\n(DTP2->DTP3)", domain_t2),
                                       ("Model Full\n(Overall Dropout)", domain_full)]):
    total = sum(domains.values())
    vals = [domains.get(d, 0) / total * 100 for d in domains_list]
    bar_colors = [colors[d] for d in domains_list]
    ax.bar(domains_list, vals, color=bar_colors)
    for i, v in enumerate(vals):
        ax.text(i, v + 0.5, f"{v:.1f}%", ha="center", fontsize=10)
    ax.set_ylabel("% of Total |SHAP|")
    ax.set_title(name, fontsize=12)
    ax.set_ylim(0, max(vals) * 1.25)
    ax.tick_params(axis="x", rotation=20)

plt.suptitle("Andersen Domain Decomposition Across Transition Models", fontsize=14, y=1.02)
plt.tight_layout()
fig.savefig(OUT1 / "andersen_decomp_comparison.pdf", dpi=300, bbox_inches="tight")
fig.savefig(OUT1 / "andersen_decomp_comparison.png", dpi=300, bbox_inches="tight")
plt.close()
print("  -> andersen_decomp_comparison.pdf saved")


# ══════════════════════════════════════════════════════════════════════
# 3.3 State Space Construction + Trajectory Export
# ══════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("3.3 State Space Construction + Trajectory Export")
print("=" * 60)

# Reload original data (before label encoding) for trajectory construction
df_orig = pd.read_parquet(PROC / "analytic_dtp1_received.parquet")

# Dynamic/temporal features for state vector
state_features = [
    "child_age_weeks", "doses_received", "dose_step",
    "last_dose_timely", "inter_dose_interval", "delay_accumulation",
    "community_dropout", "cluster_dtp_coverage",
]

# Static features that form part of the state
static_state = [f for f in available if ANDERSEN_MAP.get(f) in ["Predisposing", "Enabling", "Need"]]

# Create child_age_weeks
df_orig["child_age_weeks"] = df_orig["age_months"] * 4.345

# Build trajectory rows: each child has up to 2 dose steps (step 0 and step 1)
trajectories = []
for _, row in df_orig.iterrows():
    child_id = f"{int(row['v001'])}_{int(row['v002'])}_{int(row['v003'])}"
    base_state = {f: (float(row[f]) if pd.notna(row.get(f)) else None) for f in static_state if f in row.index}

    # Step 0: After DTP1 received -> deciding on DTP2
    state_0 = {**base_state}
    state_0["doses_received"] = 1
    state_0["dose_step"] = 0
    state_0["child_age_weeks"] = float(row.get("child_age_weeks", 0))
    state_0["last_dose_timely"] = float(row["dtp1_timely"]) if pd.notna(row.get("dtp1_timely")) else None
    state_0["inter_dose_interval"] = float(row["interval_birth_dtp1"]) if pd.notna(row.get("interval_birth_dtp1")) else None
    state_0["delay_accumulation"] = float(row["delay_dtp1"]) if pd.notna(row.get("delay_dtp1")) else 0.0
    state_0["community_dropout"] = float(row["community_dropout"]) if pd.notna(row.get("community_dropout")) else None
    state_0["cluster_dtp_coverage"] = float(row["cluster_dtp_coverage"]) if pd.notna(row.get("cluster_dtp_coverage")) else None

    got_dtp2 = row["vac_dpt2"] == 1

    # Infer action for step 0->1 (behaviour policy inference per CLAUDE.md)
    if got_dtp2:
        interval = row.get("interval_dtp1_dtp2")
        if pd.notna(interval) and interval <= 42:  # on time
            if row.get("v393") == 1:
                action_0 = 2  # CHW visit
            elif row.get("h1a", 0) >= 1:
                action_0 = 1  # SMS reminder
            else:
                action_0 = 1
        elif pd.notna(interval) and interval > 42:
            action_0 = 0  # late -> weak/no
        else:
            action_0 = 1
        reward_0 = 0.3  # next dose received
    else:
        action_0 = 0
        reward_0 = 0.0

    # Next state
    state_1 = {**base_state}
    state_1["doses_received"] = 2 if got_dtp2 else 1
    state_1["dose_step"] = 1
    interval_12 = row.get("interval_dtp1_dtp2")
    state_1["child_age_weeks"] = state_0["child_age_weeks"] + (
        float(interval_12) / 7 if pd.notna(interval_12) else 4.0
    )
    state_1["last_dose_timely"] = float(row["dtp2_timely"]) if pd.notna(row.get("dtp2_timely")) else None
    state_1["inter_dose_interval"] = float(interval_12) if pd.notna(interval_12) else None
    state_1["delay_accumulation"] = float(row["delay_dtp2"]) if pd.notna(row.get("delay_dtp2")) else state_0["delay_accumulation"]
    state_1["community_dropout"] = float(row["community_dropout"]) if pd.notna(row.get("community_dropout")) else None
    state_1["cluster_dtp_coverage"] = float(row["cluster_dtp_coverage"]) if pd.notna(row.get("cluster_dtp_coverage")) else None

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

    # Step 1: After DTP2 -> deciding on DTP3 (only if got DTP2)
    if got_dtp2:
        got_dtp3 = row["vac_dpt3"] == 1

        if got_dtp3:
            interval_23 = row.get("interval_dtp2_dtp3")
            if pd.notna(interval_23) and interval_23 <= 42:
                if row.get("v393") == 1:
                    action_1 = 2
                elif row.get("h69") == 41:
                    action_1 = 3  # campaign
                elif row.get("h1a", 0) >= 1:
                    action_1 = 1
                else:
                    action_1 = 1
            elif pd.notna(interval_23) and interval_23 > 42:
                action_1 = 0
            else:
                action_1 = 1
            reward_1 = 1.0  # DTP3 completed
        else:
            action_1 = 0
            reward_1 = 0.0

        state_2 = {**base_state}
        state_2["doses_received"] = 3 if got_dtp3 else 2
        state_2["dose_step"] = 2
        interval_23 = row.get("interval_dtp2_dtp3")
        state_2["child_age_weeks"] = state_1["child_age_weeks"] + (
            float(interval_23) / 7 if pd.notna(interval_23) else 4.0
        )
        state_2["last_dose_timely"] = float(row["dtp3_timely"]) if pd.notna(row.get("dtp3_timely")) else None
        state_2["inter_dose_interval"] = float(interval_23) if pd.notna(interval_23) else None
        state_2["delay_accumulation"] = float(row["delay_dtp3"]) if pd.notna(row.get("delay_dtp3")) else state_1["delay_accumulation"]
        state_2["community_dropout"] = float(row["community_dropout"]) if pd.notna(row.get("community_dropout")) else None
        state_2["cluster_dtp_coverage"] = float(row["cluster_dtp_coverage"]) if pd.notna(row.get("cluster_dtp_coverage")) else None

        trajectories.append({
            "child_id": child_id,
            "dose_step": 1,
            "state": json.dumps(state_1, default=str),
            "action": action_1,
            "reward": reward_1,
            "next_state": json.dumps(state_2, default=str),
            "done": 1,  # terminal after DTP3 decision
            "weight": float(row["wt"]),
        })

traj_df = pd.DataFrame(trajectories)
traj_df.to_csv(PROC / "trajectory_dataset.csv", index=False)
traj_df.to_csv(OUT1 / "trajectory_dataset.csv", index=False)
print(f"\n  Trajectory dataset: {len(traj_df):,} rows ({traj_df['child_id'].nunique():,} children)")
print(f"  Action distribution:")
print(traj_df["action"].value_counts().sort_index().to_string())
print(f"  Reward distribution:")
print(traj_df["reward"].value_counts().sort_index().to_string())

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
            "0": "No intervention (cost=0)",
            "1": "SMS reminder (cost=50)",
            "2": "CHW home visit (cost=500)",
            "3": "Facility recall + defaulter tracing (cost=1500)",
            "4": "Conditional incentive (cost=800)",
        },
        "costs": {"0": 0, "1": 50, "2": 500, "3": 1500, "4": 800},
    },
    "reward": {
        "completion_dtp3": 1.0,
        "next_dose_received": 0.3,
        "cost_lambda": 0.001,
        "formula": "R(s,a,s') = +1.0 (DTP3 completed) + 0.3 (next dose received) - lambda * cost(a)",
    },
    "behaviour_policy_inference": {
        "on_time_threshold_days": 42,
        "rules": [
            "Next dose ON TIME (<=42 days) + fieldworker visited (v393==1) -> a2",
            "Next dose ON TIME (<=42 days) + campaign (h69==41) -> a3",
            "Next dose ON TIME (<=42 days) + card present (h1a>=1) -> a1",
            "Next dose LATE (>42 days) -> a0",
            "Next dose NOT received -> a0",
        ],
    },
    "andersen_domain_mapping": {f: ANDERSEN_MAP.get(f, "Other") for f in static_state + state_features},
    "trajectory_schema": {
        "child_id": "Unique child identifier (v001_v002_v003)",
        "dose_step": "0 = after DTP1 (deciding DTP2), 1 = after DTP2 (deciding DTP3)",
        "state": "JSON dict of state features at current step",
        "action": "Inferred action (0-4)",
        "reward": "0.0 (dropout), 0.3 (next dose), 1.0 (DTP3 complete)",
        "next_state": "JSON dict of state features at next step",
        "done": "1 if terminal (dropout or after DTP3 decision)",
        "weight": "Survey weight (v005/1e6)",
    },
}

with open(OUT1 / "state_space_definition.json", "w") as f:
    json.dump(state_space_def, f, indent=2)
with open(PROC / "state_space_definition.json", "w") as f:
    json.dump(state_space_def, f, indent=2)
print(f"  -> state_space_definition.json saved")
print(f"  State dimension: {state_space_def['total_state_dim']}")

print("\n" + "=" * 60)
print("PHASE 3 COMPLETION: ALL DONE")
print("=" * 60)
