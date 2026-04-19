# Captions

## Figure captions (main)

**Figure 1. Study flow and DTP cascade.**
Panel A presents a funnel diagram tracing the full sampling cascade: from all children aged 12–23 months in the 2024 Nigeria Demographic and Health Survey (NDHS) to the 3,194 DTP1-initiating children (card-confirmed, h3 ∈ {1, 2, 3}) retained for analysis, with attrition labelled at each exclusion step. Panel B shows DTP1-to-DTP3 retention disaggregated by the six geopolitical zones (North Central, North East, North West, South East, South South, South West), illustrating the WHO cascade dropout rate (DTP1 coverage − DTP3 coverage) / DTP1 coverage × 100 for each zone. South South records the lowest dropout (8.6%) and North Central the highest (19.6%). Data source: NDHS 2024 Children's Recode (NGKR8BFL); zone-level statistics from `outputs/stage1/cascade_metrics.csv`.

**Figure 2. Prediction performance and top-10 SHAP feature importance.**
A 2 × 2 panel figure. Panel A (top-left): receiver-operating-characteristic (ROC) and precision-recall (PR) curves for the T1 (DTP1→DTP2) XGBoost model after isotonic recalibration (AUROC 0.910, 95% CI 0.885–0.932; AUPRC 0.299). Panel B (top-right): ROC and PR curves for the T2 (DTP2→DTP3) model (AUROC 0.943, 95% CI 0.929–0.957; AUPRC 0.548). Panel C (bottom-left): SHAP mean-absolute-value bar chart for T1 — top-3 predictors are [PLEASE VERIFY: inspect shap_bar_model_t1.pdf]. Panel D (bottom-right): SHAP bar chart for T2 — top-3 predictors are [PLEASE VERIFY: inspect shap_bar_model_t2.pdf]. Both models were trained with cluster-robust 5-fold cross-validation and post-hoc isotonic recalibration. Data source: `outputs/stage1/xgb_results_summary.json`; curves from `outputs/stage1/roc_pr_model_t1.pdf` and `roc_pr_model_t2.pdf`.

**Figure 3. RL-optimised intervention allocation by state.**
A choropleth map of Nigeria's 37 states (36 states + FCT), shaded by the bandit-allocated intervention recommended for each local government area (LGA) community cluster. The five possible actions are: a₀ (no intervention, ₦0), a₁ (SMS reminder, ₦50), a₂ (community health worker home visit, ₦500), a₃ (facility recall and defaulter tracing, ₦1,500), and a₄ (conditional cash or in-kind incentive, ₦800). Allocation is aggregated to the state level for cartographic clarity; LGA-level recommendations (1,140 community clusters) are available in the supplementary policy lookup table (Table S6). Data source: `outputs/stage3/lga_allocation.csv`; state boundaries from GADM 4.1 shapefiles.

**Figure 4. Cost-effectiveness of RL-optimised scenarios.**
Panel A (Cost-Effectiveness Acceptability Curve, CEAC): probability that each scenario (S1–S5) is cost-effective relative to the status quo (S0) across a willingness-to-pay range of ₦0–₦100,000 per percentage-point increase in DTP3 coverage. At λ = ₦50,000, the RL-optimised scenario (S4) has probability 0.567 and Uniform SMS (S1) has probability 0.433. Panel B (Cost-Effectiveness Plane): 1,000 PSA bootstrap replicates plotted as incremental cost (₦ per child) versus incremental DTP3 coverage for each scenario versus S0, with the default willingness-to-pay threshold shown as a dashed line. Data source: `outputs/stage3_v2/ceac_data.csv`; microsimulation results from `outputs/stage3_v2/microsim_results.csv`. Default cost-effectiveness threshold: λ = ₦50,000 per percentage-point.

**Figure 5. Interactive Web Dashboard screenshots.**
Two screenshots from the interactive policy dashboard hosted at https://olatechie.github.io/dropout/. The left panel shows the Story module — a narrated walkthrough of the study's predict-optimise-simulate pipeline accessible via a transcript text fallback (WCAG AA compliant). The right panel shows the Policy module — a choropleth visualisation of recommended interventions filterable by state, zone, and wealth quintile. The full interactive dashboard (including Simulation and Explorer modules) is available online; source code at https://github.com/olatechie/dropout.

---

## Table captions (main)

### Table 1

**Table 1.** Baseline characteristics of Nigerian children aged 12-23 months who received DTP1 (DHS 2024), stratified by T1/T2 dropout status.

### Table 2

**Table 2.** Prediction-model discrimination and calibration for DTP1→DTP2 (T1) and DTP2→DTP3 (T2) transitions, with 95 % confidence intervals from 1,000-sample bootstrap. Brier score and calibration slope reported pre- and post-isotonic recalibration.

### Table 3

**Table 3.** Microsimulation results for scenarios S0–S5 with 1,000-iteration probabilistic sensitivity analysis. DTP3 coverage and cost per child reported as mean with 95 % bootstrap CI.

### Table 4

**Table 4.** One-way deterministic sensitivity of key parameters on DTP3 coverage (tornado analysis, top ten by absolute range).

---

## Supplementary figure captions

**Figure S1. Calibration T1 (pre-recalibration).** Calibration plot for the T1 (DTP1→DTP2) XGBoost model prior to isotonic recalibration. Observed event rates are plotted against mean predicted probabilities in decile bins, with a lowess smoother. The original calibration slope of 0.874 and intercept of −0.661 indicate moderate under-dispersion. Diagonal indicates perfect calibration. Brier score 0.0358. Data source: `outputs/stage1/calibration_model_t1.pdf`; metrics from `outputs/stage1/xgb_results_summary.json` (t1.metrics.calibration_original, t1.metrics.brier_original).

**Figure S2. Calibration T1 (post-recalibration).** Calibration plot for the T1 model after isotonic regression recalibration using 5-fold cluster-robust out-of-fold predictions. Calibration slope improved to 0.959 (from 0.874) and Brier score improved to 0.0319 (from 0.0358). Reliability term reduced to effectively zero. Data source: `outputs/stage1/calibration_model_t1_recalibrated.pdf`; metrics from `outputs/stage1/xgb_results_summary.json` (t1.metrics.calibration, t1.metrics.brier).

**Figure S3. Calibration T2 (pre-recalibration).** Calibration plot for the T2 (DTP2→DTP3) XGBoost model prior to isotonic recalibration. The original calibration slope of 1.596 and intercept of 0.724 indicate systematic over-dispersion — predicted probabilities are too extreme. Brier score 0.0274. Data source: `outputs/stage1/calibration_model_t2.pdf`; metrics from `outputs/stage1/xgb_results_summary.json` (t2.metrics.calibration_original, t2.metrics.brier_original).

**Figure S4. Calibration T2 (post-recalibration).** Calibration plot for the T2 model after isotonic regression recalibration. The slope of 1.596 was corrected to 0.969, and Brier score improved from 0.0274 to 0.0255. Reliability term reduced to effectively zero. Data source: `outputs/stage1/calibration_model_t2_recalibrated.pdf`; metrics from `outputs/stage1/xgb_results_summary.json` (t2.metrics.calibration, t2.metrics.brier).

**Figure S5. SHAP beeswarm T1.** SHAP beeswarm plot for the T1 (DTP1→DTP2) XGBoost model. Each dot represents one child, coloured by feature value (red = high, blue = low), ordered by mean absolute SHAP importance. Features with positive SHAP values increase the predicted dropout probability. Dynamic and need-domain features dominate the upper ranks. Data source: `outputs/stage1/shap_beeswarm_model_t1.pdf`; feature list from `outputs/stage1/xgb_results_summary.json` (t1.features).

**Figure S6. SHAP beeswarm T2.** SHAP beeswarm plot for the T2 (DTP2→DTP3) XGBoost model, structured identically to Figure S5. Dynamic-domain features (Andersen domain contribution 1.24) and need-domain features (0.41) account for the largest share of model variance. Enabling factors (0.23) make a smaller but meaningful contribution relative to T1 (Enabling contribution 0.90). Data source: `outputs/stage1/shap_beeswarm_model_t2.pdf`; Andersen contributions from `outputs/stage1/xgb_results_summary.json` (t2.andersen_domains).

**Figure S7. FQI convergence.** Convergence plot for the Fitted Q-Iteration (FQI) offline reinforcement-learning algorithm, showing Q-value norm or TD-error against training iteration. Convergence indicates that the policy has stabilised and further iterations do not materially change the action assignments. Data source: `outputs/stage2/fqi_convergence.png`.

**Figure S8. CQL α sensitivity.** Sensitivity of the Conservative Q-Learning (CQL) policy value to the conservatism parameter α, with α varied across a grid from near-zero to large values. Plots show mean policy value (WIS estimate) against α, identifying the α that maximises held-out policy value without excessive conservatism. Data source: `outputs/stage2/cql_analysis.png`.

**Figure S9. Off-policy evaluation comparison (FQE vs WIS vs OOD check).** Comparison of three policy evaluation estimators for the three trained offline RL algorithms (CQL, IQL, BCQ): Fitted Q-Evaluation (FQE) estimate, Weighted Importance Sampling (WIS) estimate, and out-of-distribution (OOD) action frequency. IQL achieves the highest FQE value (0.872) and WIS value (0.689) with 0.0% OOD actions, indicating it is the best-performing and most conservative algorithm. Data source: `outputs/stage2_v2/ope_comparison.csv`.

**Figure S10. Local Moran clusters of DTP dropout.** Bivariate Local Moran's I cluster map of DTP1-to-DTP3 dropout prevalence across Nigerian LGAs, identifying statistically significant spatial clusters (High-High, Low-Low) and spatial outliers (High-Low, Low-High) at p < 0.05 after FDR correction. North Central and North East zones show predominant High-High clustering. Data source: `outputs/stage0/local_moran_clusters_map.png`; spatial weights constructed from GADM 4.1 shapefiles with queen contiguity.

**Figure S11. State-level DTP dropout prevalence.** Choropleth map of WHO DTP1-to-DTP3 dropout rates for Nigeria's 37 states, stratified by colour quintile. States in the North Central and North East geopolitical zones show the highest dropout rates (>20%). Data source: `outputs/stage0/dropout_prevalence_by_state.png`; state-level rates derived from `outputs/stage1/cascade_metrics.csv`.

**Figure S12. Andersen-domain SHAP decomposition.** Stacked bar chart comparing summed mean-absolute SHAP contributions across the four Andersen model domains (Predisposing, Enabling, Need, Dynamic/Temporal) for Model T1, Model T2, and the combined full model. Dynamic/temporal features dominate both transition models (T1: 1.63; T2: 1.24; Full: 2.74). Need factors rank second overall. Data source: `outputs/stage1/andersen_decomp_comparison.png`; domain totals from `outputs/stage1/xgb_results_summary.json` (t1.andersen_domains, t2.andersen_domains, full.andersen_domains).

---

## Supplementary table captions

**Table S1. Subgroup prediction performance by geopolitical zone.** Observed DTP3 coverage versus model-predicted DTP3 coverage for each of the six geopolitical zones (North Central, North East, North West, South East, South South, South West), with absolute prediction error and a flag for zones where error exceeds an acceptable threshold. Data source: `outputs/validation/subgroup_zone.csv`.

**Table S2. Subgroup prediction performance by state.** Observed versus predicted DTP3 coverage for each of Nigeria's 37 states (coded by numeric sstate identifier), with absolute error and flagging. Data source: `outputs/validation/subgroup_state.csv`.

**Table S3. Subgroup prediction performance by wealth quintile.** Observed versus predicted DTP3 coverage stratified by household wealth quintile (1 = poorest to 5 = richest), with absolute error and flagging. Data source: `outputs/validation/subgroup_wealth_quintile.csv`.

**Table S4. Subgroup prediction performance by urban/rural residence.** Observed versus predicted DTP3 coverage for urban (0) and rural (1) children, with absolute error and flagging. Data source: `outputs/validation/subgroup_urban_rural.csv`.

**Table S5. Subgroup prediction performance by maternal education.** Observed versus predicted DTP3 coverage stratified by maternal education level (0 = no education; 1 = primary; 2 = secondary; 3 = higher), with absolute error and flagging. Data source: `outputs/validation/subgroup_maternal_education.csv`.

**Table S6. Reinforcement-learning policy lookup (first 50 of 1,140 community clusters).** The first 50 rows of the full LGA-level intervention allocation table, listing community_idx, recommended assigned_action (a₀–a₄), n_children (per cluster), observed dropout_rate, estimated cost (₦), state code (sstate), and PSU identifier (v021). The complete 1,140-row table is available in `outputs/stage3/lga_allocation.csv`.

**Table S7. Model-input parameter table (effect sizes, costs, PSA ranges).** Literature-derived effect sizes (relative risk reductions) for each intervention action (a₁–a₄), unit costs, and the probability distributions used in the probabilistic sensitivity analysis (PSA). Ranges varied ±25% from base-case values in the one-way tornado analysis. Data source: `outputs/literature/intervention_effect_sizes.csv`; PSA ranges from `outputs/stage3_v2/tornado_data.csv`.

**Table S8. Reproducibility parameter table (software versions, seeds, hyperparameters).** Full specification of software environment (Python version, key package versions), random seeds, XGBoost hyperparameters selected by Bayesian optimisation (Optuna, 200 trials), RL hyperparameters, and microsimulation parameters to enable independent replication.

**Table S9. TRIPOD-AI reporting checklist.** Item-by-item completion of the TRIPOD-AI transparent reporting checklist [@collins2024tripod] for the two dropout prediction models (T1 and T2), with page/section cross-references.

**Table S10. CHEERS 2022 reporting checklist.** Item-by-item completion of the Consolidated Health Economic Evaluation Reporting Standards 2022 (CHEERS 2022) checklist for the microsimulation cost-effectiveness analysis, with page/section cross-references.

**Table S11. Gottesman 2019 RL-in-health issue-response table.** Structured response to the 13 key issues identified by Gottesman et al. (2019) for reporting reinforcement learning in healthcare, covering MDP specification, behaviour policy, off-policy evaluation, distributional shift, and deployment considerations.
