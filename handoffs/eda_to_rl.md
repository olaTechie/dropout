# Handoff: EDA + Cascade + ML → RL + Bandit + Microsim Agent

**Date**: 2026-04-06
**Status**: COMPLETE

---

## What Was Produced

### Stage 0: EDA Outputs (`outputs/stage0/`)

| File | Description |
|------|-------------|
| `descriptive_statistics_table.csv` | TableOne grouped by vac_dropout with p-values |
| `dropout_prevalence_by_state.pdf` | Horizontal bar chart of dropout by sstate |
| `dropout_choropleth_map.pdf/.png` | Choropleth map using GADM Nigeria shapefile |
| `dropout_funnel_plot.pdf/.png` | Funnel plot with 95%/99.7% CIs |
| `local_moran_clusters_map.pdf/.png` | Local Moran's I cluster map (HH/LL/LH/HL) |
| `zonal_analysis.pdf/.png` | Dropout rates by geopolitical zone + wealth gradient |

### Stage 1: Cascade + ML Outputs (`outputs/stage1/`)

| File | Description |
|------|-------------|
| `cascade_metrics.csv` | DTP1/DTP2/DTP3 coverage and dropout rates by zone |
| `cascade_and_intervals.pdf` | Cascade funnel + inter-dose interval distributions |
| `cascade_by_zone.pdf` | Cascade by geopolitical zone |
| `xgb_model_full.json` | XGBoost model: overall dropout prediction |
| `xgb_model_t1.json` | XGBoost model: T1 (DTP1→DTP2) dropout |
| `xgb_model_t2.json` | XGBoost model: T2 (DTP2→DTP3) dropout |
| `xgb_results_summary.json` | All model metrics, params, Andersen decomposition |
| `roc_pr_model_full.pdf` | ROC + PR curves for Model Full |
| `roc_pr_model_t1.pdf` | ROC + PR curves for Model T1 |
| `roc_pr_model_t2.pdf` | ROC + PR curves for Model T2 |
| `calibration_model_full.pdf` | Calibration curve + histogram for Model Full |
| `calibration_model_t1.pdf` | Calibration curve + histogram for Model T1 |
| `calibration_model_t2.pdf` | Calibration curve + histogram for Model T2 |
| `shap_bar_model_full.pdf` | Top-20 SHAP feature importance bar chart (Full) |
| `shap_bar_model_t1.pdf` | Top-20 SHAP feature importance bar chart (T1) |
| `shap_bar_model_t2.pdf` | Top-20 SHAP feature importance bar chart (T2) |
| `shap_beeswarm_model_full.pdf` | SHAP beeswarm plot (Full) |
| `shap_beeswarm_model_t1.pdf` | SHAP beeswarm plot (T1) |
| `shap_beeswarm_model_t2.pdf` | SHAP beeswarm plot (T2) |
| `andersen_decomp_model_full.pdf` | Andersen domain decomposition (Full) |
| `andersen_decomp_model_t1.pdf` | Andersen domain decomposition (T1) |
| `andersen_decomp_model_t2.pdf` | Andersen domain decomposition (T2) |
| `andersen_decomp_comparison.pdf/.png` | Side-by-side comparison of all 3 models |
| `trajectory_dataset.csv` | Trajectory dataset (s, a, r, s') for RL |
| `state_space_definition.json` | State space, action space, reward definitions |

### Processed Data (`data/processed/`)

| File | Description |
|------|-------------|
| `analytic_dtp1_received.csv/.parquet` | Analytic sample: 3,194 children (DTP1 recipients, 12-23 months) |
| `trajectory_dataset.csv` | 6,217 trajectory rows (3,138 unique children, 2 dose steps) |
| `state_space_definition.json` | Complete state/action/reward specification for RL agent |

---

## Key EDA Findings Affecting RL Formulation

### 1. Study Population
- **N = 3,194** DTP1 recipients aged 12-23 months
- **Overall dropout prevalence**: 14.8% (vac_dropout)
- **T1 dropout** (DTP1→DTP2): 4.0% — very low, hard to predict
- **T2 dropout** (DTP2→DTP3): 3.9% among DTP2 recipients

### 2. Cascade Metrics by Zone

| Zone | DTP1→DTP2 Retention | DTP2→DTP3 Retention | WHO Dropout Rate |
|------|---------------------|---------------------|------------------|
| North Central | 92.5% | 86.9% | 19.6% |
| North East | 94.6% | 87.9% | 16.8% |
| North West | 94.1% | 91.7% | 13.8% |
| South East | 98.1% | 87.6% | 14.1% |
| South South | 96.8% | 94.5% | 8.6% |
| South West | 94.6% | 92.0% | 13.0% |

**Key insight**: South South has lowest dropout (8.6%); North Central has highest (19.6%). DTP2→DTP3 transition is the more problematic step in all zones.

### 3. Geographic Heterogeneity
- Strong spatial clustering confirmed by Local Moran's I
- North-South divide is significant
- Consider zone-stratified RL policies

---

## XGBoost Model Performance

### Model T1 (DTP1→DTP2)
- **AUC-ROC**: 0.9101 (95% CI: 0.8852-0.9318)
- **AUC-PR**: 0.2993 (95% CI: 0.2297-0.3867)
- **Brier score**: 0.0358
- **Calibration**: slope=0.874, intercept=-0.661
- **DeLong test vs LR**: p=8.1e-10 (XGBoost significantly better)
- **Low AUC-PR** reflects the very low prevalence (4.0%)

### Model T2 (DTP2→DTP3)
- **AUC-ROC**: 0.9432 (95% CI: 0.9290-0.9573)
- **AUC-PR**: 0.5482 (95% CI: 0.4540-0.6404)
- **Brier score**: 0.0274
- **Calibration**: slope=1.596, intercept=0.724
- **DeLong test vs LR**: p=9.7e-10 (XGBoost significantly better)
- **Best discriminating model** of the three

### Validation Notes
- All metrics computed with survey weights (v005/1e6)
- Cluster-robust CV using GroupKFold on PSU (v021), 5 folds
- SHAP values computed on test/validation folds only
- Bootstrap 95% CIs with 1,000 resamples
- All models significantly outperform logistic regression baseline

---

## Andersen Domain Decomposition Results

| Domain | Model T1 | Model T2 | Model Full |
|--------|----------|----------|------------|
| Predisposing | 17.3% | 10.1% | 17.1% |
| Enabling | 19.7% | 11.2% | 15.2% |
| Need | 27.1% | 19.7% | 15.6% |
| **Dynamic** | **35.9%** | **59.0%** | **52.1%** |

### Hypothesis Test Results
- **Hypothesis**: T1 dominated by Predisposing, T2 by Enabling/Need
- **Finding**: Both T1 and T2 are dominated by **Dynamic** features (timing, dose history, community coverage)
- T1 has more balanced distribution across domains (Predisposing 17.3%, Need 27.1%)
- T2 is heavily dominated by Dynamic features (59.0%), suggesting timing/delay accumulation drives late-cascade dropout
- **Implication for RL**: Dynamic state features (especially delay_accumulation, community_dropout, cluster_dtp_coverage) should be primary signals for policy learning

---

## Trajectory Dataset Schema

**File**: `data/processed/trajectory_dataset.csv` (6,217 rows, 3,138 children)

| Column | Type | Description |
|--------|------|-------------|
| child_id | str | `{v001}_{v002}_{v003}` — unique child identifier |
| dose_step | int | 0 = after DTP1 (deciding DTP2), 1 = after DTP2 (deciding DTP3) |
| state | JSON str | Dict of 55 state features (47 static + 8 dynamic) |
| action | int | Inferred action: 0=none, 1=SMS, 2=CHW, 3=facility recall, 4=incentive |
| reward | float | 0.0 (dropout), 0.3 (next dose received), 1.0 (DTP3 completed) |
| next_state | JSON str | State features at next step |
| done | int | 1 if terminal (dropout or after DTP3 decision) |
| weight | float | Survey weight (v005/1e6) |

### Action Distribution
| Action | Count | % |
|--------|-------|---|
| 0 (No intervention) | 1,301 | 20.9% |
| 1 (SMS reminder) | 4,389 | 70.6% |
| 2 (CHW home visit) | 517 | 8.3% |
| 3 (Facility recall) | 10 | 0.2% |
| 4 (Incentive) | 0 | 0.0% |

### Reward Distribution
| Reward | Count | % |
|--------|-------|---|
| 0.0 (dropout) | 484 | 7.8% |
| 0.3 (next dose) | 3,023 | 48.6% |
| 1.0 (completed) | 2,710 | 43.6% |

---

## State Space Definition Summary

- **Total state dimension**: 55 features
  - 47 static (Andersen: 16 Predisposing, 20 Enabling, 11 Need)
  - 8 dynamic/temporal (child_age_weeks, doses_received, dose_step, etc.)
- **Action space**: 5 actions (a0-a4) with costs ₦0-₦1,500
- **Reward**: R(s,a,s') = +1.0 (DTP3) + 0.3 (next dose) - 0.001 × cost(a)
- **Full specification**: `data/processed/state_space_definition.json`

---

## What the RL Agent Should Read First

1. `data/processed/trajectory_dataset.csv` — the (s, a, r, s') tuples
2. `data/processed/state_space_definition.json` — state/action/reward definitions
3. `outputs/stage1/xgb_results_summary.json` — model metrics + Andersen decomposition
4. `outputs/literature/action_space_calibration.json` — updated effect sizes from lit review
5. `outputs/literature/ml_validation_recommendations.md` — OPE validation checklist

---

## Data Quality Warnings

1. **Low T1/T2 prevalence**: Both ~4%, causing class imbalance. RL reward signal may be sparse.
2. **Action a3/a4 never observed**: Facility recall is rare (0.2%), incentives absent (0%). Conservative Q-Learning (CQL) essential for out-of-distribution action safety.
3. **Behaviour policy is inferred**: No ground truth on actual interventions. Proxy actions derived from timing + card/fieldworker indicators. RL agent should use conservative OOD handling.
4. **Missing inter-dose intervals**: ~30% of children lack card-confirmed dates. State features for these have imputed/missing values.
5. **T2 calibration**: Model T2 has slope=1.596 (over-confident in extremes). Consider isotonic recalibration if using predicted probabilities as RL features.
6. **Survey weights included**: Each trajectory row has a `weight` column. RL agent should incorporate these in importance-weighted sampling.

---

## Stage Gate Checklist

- [x] Sample restricted to DTP1 recipients (h3 in 1/2/3) — N=3,194
- [x] EDA reports generated and saved to outputs/stage0/
- [x] Transition dropout rates computed correctly (T1=4.0%, T2=3.9%)
- [x] Inter-dose intervals from card dates, missingness handled (97/98)
- [x] Three XGBoost models fitted with calibration curves + Brier scores
- [x] SHAP per transition with Andersen domain decomposition
- [x] State vectors constructed (55 dimensions)
- [x] Trajectory dataset exported as (s, a, r, s') tuples — 6,217 rows
- [x] szone used NOT v024
- [x] v483a used NOT v467d
- [x] Survey weights applied (v005/1e6)
- [x] Cluster-robust CV using GroupKFold on v021 (PSU)
- [x] Bootstrap 95% CIs for AUC-ROC and AUC-PR
- [x] DeLong test comparing XGBoost vs logistic regression baseline
