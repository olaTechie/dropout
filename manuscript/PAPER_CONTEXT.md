# PAPER_CONTEXT

## Study
**Title (working):** Reinforcement-Learning-Guided Sequential Intervention to Reduce
DTP1-to-DTP3 Vaccine Dropout in Nigeria: A Prediction, Policy Optimisation, and
Cost-Effectiveness Analysis

**Population:** Children 12–23 months who received DTP1 (DHS Nigeria 2024; NGKR8BFL),
with card-confirmed vaccination dates (h3 ∈ {1, 2, 3}). Youngest living child per
woman (b5 == 1).

**Sample size:** ~3,200 children (exact N from descriptives table).

**Study type:** Hybrid methodology — prediction model (TRIPOD-AI), offline RL + bandit
allocation (Gottesman 2019 reporting norms), economic evaluation with microsim + PSA
(CHEERS 2022).

**Target journal:** Vaccines (MDPI) — Article type.
**Reporting guidelines:** TRIPOD-AI, CHEERS 2022, Gottesman RL-health.
**Citation style:** MDPI numeric `[1]`; CSL file `assets/vaccines.csl`.
**Word budgets:** Abstract 200, Intro 600, Methods 2100, Results 1800,
Discussion 1000, Conclusions 150.

## Outputs map (all numeric claims must cite one of these)

| Stage | Path | Description |
|-------|------|-------------|
| 0 | outputs/stage0/descriptive_statistics_table.csv | Cohort descriptives |
| 0 | outputs/stage0/dropout_prevalence_by_state.png | State prevalence map |
| 0 | outputs/stage0/dropout_funnel_plot.png | Cascade funnel |
| 0 | outputs/stage0/local_moran_clusters_map.png | Spatial clusters |
| 1 | outputs/stage1/cascade_metrics.csv | AUROC/AUPRC/Brier/ECE |
| 1 | outputs/stage1/recalibration_log.md | Pre- vs post-calibration |
| 1 | outputs/stage1/roc_pr_model_{t1,t2}.pdf | ROC/PR curves |
| 1 | outputs/stage1/shap_bar_model_{t1,t2,full}.pdf | SHAP bar plots |
| 1 | outputs/stage1/andersen_decomp_comparison.png | Andersen decomposition |
| 2 | outputs/stage2/fqi_convergence.png | FQI convergence |
| 2 | outputs/stage2/cql_analysis.png | CQL α-sensitivity |
| 2 | outputs/stage2_v2/ope_comparison.csv | Off-policy evaluation |
| 2 | outputs/stage2/policy_lookup.csv | State→action lookup |
| 3 | outputs/stage3/lga_allocation.csv | Bandit LGA allocation |
| 3 | outputs/stage3/microsim_results.csv | v1 microsim (superseded) |
| 3v2 | outputs/stage3_v2/microsim_results.csv | v2 microsim (use this) |
| 3v2 | outputs/stage3_v2/ceac.{pdf,png} | Cost-effectiveness acceptability |
| 3v2 | outputs/stage3_v2/ce_plane.{pdf,png} | CE plane |
| 3v2 | outputs/stage3_v2/icer_distribution.csv | PSA ICER distribution |
| 3v2 | outputs/stage3_v2/tornado_data.csv | One-way sensitivity |
| 3v2 | outputs/stage3_v2/sensitivity_scenarios.csv | Scenario sensitivity |
| 3v2 | outputs/stage3_v2/stage3_v2_summary.json | Headline summary |
| val | outputs/validation/subgroup_{zone,state,wealth_quintile,urban_rural,maternal_education}.csv | Subgroup performance |
| lit | outputs/literature/dropout_literature_review.csv | Lit review table |
| lit | outputs/literature/intervention_effect_sizes.csv | Effect sizes from lit |

## Dashboard
URL: https://olatechie.github.io/dropout/
Source repo: https://github.com/olatechie/dropout
Modules: Story, Policy, Simulation, Explorer
Accessibility: WCAG AA + /story/transcript text fallback.

## Reference seed
Bibliography seed: manuscript/.archive/references.bib (~53 entries).
Target ≥50 unique after de-dup and augmentation.
