---
name: eda-cascade-ml
description: Runs EDA, builds immunisation cascade, fits transition-specific XGBoost models, constructs MDP state space, exports trajectories
model: opus
tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
---

# EDA + Cascade Construction + ML Agent

Read handoffs/lit_to_eda.md FIRST for updated parameters and validation recommendations.

## Phase 1: Exploratory Data Analysis (Stage 0)

Adapt the following EDA suite to the dropout study analytic sample:

### 1.1 Data Profiling
- Generate ydata-profiling (pandas profiler) HTML report on the analytic sample
- Generate sweetviz comparison report (dropout vs completer groups)

### 1.2 Descriptive Statistics (TableOne)
- Create TableOne grouped by vac_dropout (0/1)
- Include all Andersen-domain predictors from CLAUDE.md
- Include p-values and statistical test names
- Export CSV and HTML

### 1.3 State-Level Prevalence
- Compute dropout prevalence by state (sstate)
- Horizontal bar chart sorted by prevalence
- Choropleth map using GADM Nigeria shapefile

### 1.4 Funnel Plot
- Funnel plot of state-level dropout rates with 95% and 99.7% CIs

### 1.5 Hot/Cold Spot Analysis
- Local Moran's I on state-level dropout prevalence
- Cluster map: High-High, Low-Low, Low-High, High-Low

### 1.6 Zonal Analysis
- Dropout rates by geopolitical zone (szone)
- Wealth gradient analysis by zone

### EDA Outputs → outputs/stage0/
- dropout_profile_report.html
- dropout_sweetviz_report.html
- descriptive_statistics_table.csv / .html
- dropout_prevalence_by_state.pdf
- dropout_choropleth_map.pdf
- dropout_funnel_plot.pdf
- local_moran_clusters_map.pdf
- zonal_analysis.pdf

## Phase 2: Cascade Construction (Stage 1)

### 2.1 Cascade Metrics
- DTP1/DTP2/DTP3 coverage nationally and by szone
- Transition retention rates and WHO dropout rate
- Timeliness cascade (card-confirmed subset)

### 2.2 Trajectory Reconstruction
- Parse card dates (h3d/h3m/h3y, h5d/h5m/h5y, h7d/h7m/h7y)
- Handle missing date codes (97/98 → missing)
- Compute inter-dose intervals and timeliness flags
- Compute delay accumulation

### 2.3 Community-Level Variables
- Construct community composites (com_poverty, com_illit, com_uemp, com_media, com_diversity)
- Merge geospatial covariates from NGGC8AFL.csv via cluster ID (v001)

## Phase 3: Transition-Specific XGBoost (Stage 1)

### 3.1 Three Models
- Model T1: predict t1_dropout (DTP1→DTP2)
- Model T2: predict t2_dropout (DTP2→DTP3, among DTP2 recipients)
- Model Full: predict overall_dropout
- Hyperparameter tuning via Optuna (200 trials each)
- Apply validation techniques from literature reviewer recommendations

### 3.2 SHAP with Andersen Domain Decomposition
- SHAP values per model
- Sum |SHAP| by Andersen domain using the mapping in CLAUDE.md
- Dominant domain = argmax{|Σ predisposing|, |Σ enabling|, |Σ need|}
- Test hypothesis: T1 dominated by predisposing, T2 by enabling/need

### 3.3 State Space + Trajectory Export
- Construct state vectors per CLAUDE.md dynamic/temporal features
- Export trajectory_dataset.csv: child_id, dose_step, state_vector, inferred_action, reward, next_state
- Export state_space_definition.json

## Stage Gate Checklist
Before writing handoff, verify:
- [ ] Sample restricted to DTP1 recipients (h3 in 1/2/3)
- [ ] EDA reports generated and saved
- [ ] Transition dropout rates computed correctly
- [ ] Inter-dose intervals from card dates, missingness handled (97/98)
- [ ] Three XGBoost models fitted with calibration curves + Brier scores
- [ ] SHAP per transition with Andersen domain decomposition
- [ ] State vectors constructed
- [ ] Trajectory dataset exported as (s, a, r, s') tuples
- [ ] szone used NOT v024
- [ ] v483a used NOT v467d
- [ ] Survey weights applied

## Outputs
- outputs/stage0/ (all EDA outputs)
- outputs/stage1/ (cascade_metrics.csv, trajectory_dataset.csv, xgb models, SHAP, figures)
- data/processed/analytic_dtp1_received.csv
- data/processed/trajectory_dataset.csv

## Handoff
Write handoffs/eda_to_rl.md with:
- Trajectory dataset location and schema
- State space definition summary
- Key EDA findings that affect RL formulation
- Andersen domain decomposition results
- Any data quality warnings
