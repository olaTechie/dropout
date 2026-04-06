# Figures, Tables, and Supplementary Materials

---

## Main Text Figures

### Figure 1. Four-stage analytical framework for optimising sequential interventions to reduce DTP vaccination dropout

**Source:** Schematic (to be created)

**Caption:** Schematic overview of the four-stage analytical framework. Stage 1 constructs the immunisation cascade, fits transition-specific XGBoost models with SHAP explainability organised by Andersen's Behavioural Model, and exports the trajectory dataset. Stage 2 formulates the Markov decision process and learns the optimal sequential intervention policy using fitted Q-iteration and conservative Q-learning. Stage 3 implements contextual multi-armed bandit allocation for community-level resource optimisation under budget constraints. Stage 4 validates the reinforcement learning-derived policy through microsimulation comparing six intervention scenarios. Arrows indicate data flow between stages. The literature review (not shown) ran in parallel with Stage 1, informing effect size calibration and validation standards across all stages.

---

### Figure 2. DTP immunisation cascade by geopolitical zone

**Source:** `outputs/stage1/cascade_by_zone.pdf`

**Caption:** DTP immunisation cascade showing retention from DTP1 to DTP2 (transition 1) and DTP2 to DTP3 (transition 2) by the six geopolitical zones of Nigeria, using the Nigeria Demographic and Health Survey 2024. All children in the analytic sample received DTP1 (100% by definition). Bar heights represent the proportion of DTP1 recipients who received each subsequent dose. The WHO dropout rate, defined as (DTP1 coverage − DTP3 coverage) / DTP1 coverage × 100, is annotated for each zone. The South South zone had the lowest dropout rate (8.6%) and the North Central zone the highest (19.6%). Error bars represent 95% confidence intervals incorporating survey weights.

---

### Figure 3. Spatial distribution of DTP dropout prevalence across Nigerian states

**Panel A:** `outputs/stage0/dropout_choropleth_map.pdf`
**Panel B:** `outputs/stage0/local_moran_clusters_map.pdf`

**Caption:** (A) Choropleth map of DTP1-to-DTP3 dropout prevalence by state, with darker shading indicating higher dropout rates. (B) Local Moran's I cluster map identifying spatial clusters and outliers: High-High (hot spots), Low-Low (cold spots), High-Low and Low-High (spatial outliers). Global Moran's I was computed using queen contiguity weights on state-level dropout rates. State boundaries from the GADM database (version 4.1). Survey-weighted prevalences were computed using NDHS 2024 sampling weights.

---

### Figure 4. Funnel plot of state-level DTP dropout prevalence

**Source:** `outputs/stage0/dropout_funnel_plot.pdf`

**Caption:** Funnel plot of DTP1-to-DTP3 dropout prevalence by state against sample size. The horizontal line represents the national weighted mean dropout rate (14.8%). Dashed blue lines represent 95% control limits and dotted red lines represent 99.7% control limits, derived from the binomial distribution. States falling outside the control limits exhibit statistically unusual dropout rates beyond what would be expected from sampling variation alone.

---

### Figure 5. SHAP Andersen domain decomposition comparison across cascade transitions

**Source:** `outputs/stage1/andersen_decomp_comparison.pdf`

**Caption:** Andersen domain decomposition of mean absolute SHAP values for the three transition-specific XGBoost models. For each model, the total absolute SHAP contribution was aggregated by Andersen domain: predisposing (16 features: demographics, social structure, health beliefs), enabling (20 features: personal resources, community resources, geospatial covariates), need (11 features: perceived and evaluated need), and dynamic (8 features: temporal cascade features including inter-dose intervals, delay accumulation, and community-level dropout rates). Dynamic features dominated all three models: T1 = 35.9%, T2 = 59.0%, Full = 52.1% of total SHAP importance. SHAP values were computed on the held-out test set using TreeExplainer.

---

### Figure 6. Model discrimination and calibration for transition-specific XGBoost models

**Panel A:** `outputs/stage1/roc_pr_model_t1.pdf`
**Panel B:** `outputs/stage1/roc_pr_model_t2.pdf`
**Panel C:** `outputs/stage1/calibration_model_t1_recalibrated.pdf`
**Panel D:** `outputs/stage1/calibration_model_t2_recalibrated.pdf`

**Caption:** Discrimination and calibration performance for the two transition-specific XGBoost models. (A) Receiver operating characteristic and precision-recall curves for Model T1 (DTP1→DTP2 dropout; AUC-ROC = 0.910, 95% CI: 0.885-0.932; AUC-PR = 0.299, 95% CI: 0.230-0.387). (B) ROC and PR curves for Model T2 (DTP2→DTP3 dropout; AUC-ROC = 0.943, 95% CI: 0.929-0.957; AUC-PR = 0.548, 95% CI: 0.454-0.640). (C) Calibration curves for Model T1 before (dashed) and after (solid) isotonic regression recalibration, with predicted probability histograms. (D) Calibration curves for Model T2 before and after recalibration. Both models significantly outperformed logistic regression (DeLong p < 1 × 10⁻⁹). Recalibration improved calibration slope from 0.874 to 0.959 (T1) and from 1.596 to 0.969 (T2).

---

### Figure 7. Conservative Q-learning policy analysis

**Panel A:** `outputs/stage2/cql_analysis.pdf`
**Panel B:** `outputs/stage2/q_values_by_action.pdf`

**Caption:** (A) Action distribution comparison between the inferred behaviour policy (observed in NDHS 2024 data) and the CQL-learned policy (α = 5.0). The behaviour policy is SMS-dominated (70.6%), while the CQL policy shifts toward community health worker visits (29.4%), conditional incentives (22.9%), and facility recall (10.4%). (B) Distribution of Q-values by action, showing the estimated long-term value of each intervention. Higher Q-values indicate actions with greater expected cumulative reward (DTP3 completion minus cost). The CQL penalty (α = 5.0) constrains Q-values for out-of-distribution actions, though 33.3% of policy recommendations are for actions observed in fewer than 1% of training trajectories.

---

### Figure 8. Microsimulation scenario comparison

**Source:** `outputs/stage3/microsim_scenarios.pdf`

**Caption:** Comparison of DTP3 completion rates across six microsimulation scenarios with 95% confidence intervals from 1,000 bootstrap iterations (synthetic population N = 10,000). S0 = status quo (observed behaviour policy); S1 = uniform SMS reminders; S2 = uniform community health worker visits; S3 = risk-targeted (top 30% risk receive CHW, remainder receive SMS); S4 = reinforcement learning-optimised sequential policy; S5 = bandit community-level allocation. Intervention effects were applied as relative risk reductions on transition-specific dropout probabilities. All scenarios improved DTP3 completion relative to the status quo (85.9%). S1 and S5 were dominant strategies (better outcomes at lower cost). S3 was the most cost-effective non-dominant strategy (ICER: ₦8,007 per additional DTP3 completion).

**Footnotes:** ICER = incremental cost-effectiveness ratio, computed relative to S0. A dominant scenario achieves higher DTP3 completion at lower total cost than S0. Effect sizes: a₁ = 10% relative risk reduction on dropout; a₂ = 20%; a₃ = 25%; a₄ = 14%.

---

## Main Text Tables

### Table 1. Characteristics of the study population by DTP dropout status

**Source:** `outputs/stage0/descriptive_statistics_table.csv`

**Caption:** Baseline characteristics of 3,194 children aged 12-23 months who received DTP1 in the Nigeria Demographic and Health Survey 2024, stratified by DTP dropout status (completer vs dropout). Continuous variables are presented as survey-weighted mean (standard deviation); categorical variables as survey-weighted count (percentage). P-values are from chi-squared tests (categorical), Welch's t-test (normally distributed continuous), or Kruskal-Wallis tests (non-normal continuous). All estimates incorporate NDHS 2024 sampling weights, stratification, and clustering.

**Footnotes:** DTP = diphtheria-tetanus-pertussis. Dropout defined as receipt of DTP1 but not DTP3. Variables organised by Andersen's Behavioural Model domains: predisposing (demographic, social structure, health beliefs), enabling (personal/family, community, geospatial), need (perceived, evaluated), and dynamic/temporal.

---

### Table 2. XGBoost model performance across cascade transitions

**Caption:** Discrimination and calibration metrics for the three transition-specific XGBoost gradient-boosted tree models predicting DTP vaccination dropout. Model T1 predicts DTP1-to-DTP2 dropout; Model T2 predicts DTP2-to-DTP3 dropout among DTP2 recipients; Model Full predicts overall DTP1-to-DTP3 dropout. AUC-ROC and AUC-PR are reported with 95% bootstrap confidence intervals (1,000 resamples). Calibration metrics are reported after isotonic regression recalibration, with original values in parentheses. DeLong test p-values compare XGBoost against logistic regression.

| Metric | Model T1 | Model T2 | Model Full |
|--------|----------|----------|------------|
| N | 3,194 | 3,023 | 3,194 |
| Event rate | 4.0% | 3.9% | 14.8% |
| AUC-ROC (95% CI) | 0.910 (0.885-0.932) | 0.943 (0.929-0.957) | — |
| AUC-PR (95% CI) | 0.299 (0.230-0.387) | 0.548 (0.454-0.640) | — |
| Brier score (recalibrated) | 0.032 (0.036) | 0.026 (0.027) | — |
| Calibration slope (recalibrated) | 0.959 (0.874) | 0.969 (1.596) | — |
| Calibration intercept (recalibrated) | -0.065 (-0.661) | -0.104 (0.724) | — |
| DeLong p (vs LR) | < 1 × 10⁻⁹ | < 1 × 10⁻⁹ | — |

**Footnotes:** AUC-ROC = area under the receiver operating characteristic curve. AUC-PR = area under the precision-recall curve. Calibration assessed using locally estimated scatterplot smoothing (Loess). Brier score decomposed using Spiegelhalter method. Isotonic regression used for post-hoc recalibration. Cross-validation used cluster-robust folds holding out entire primary sampling units. Model Full metrics not reported individually as it serves primarily as input for SHAP domain decomposition.

---

### Table 3. Andersen domain SHAP decomposition

**Caption:** Andersen-stratified SHAP decomposition showing the mean absolute SHAP contribution by domain for each XGBoost model. For each child, absolute SHAP values were summed within each Andersen domain. The dominant domain is the domain contributing the highest proportion of total SHAP importance. The original hypothesis predicted predisposing dominance at transition 1 (early exit) and enabling/need dominance at transition 2 (late exit).

| Domain (n features) | T1 mean |SHAP| (%) | T2 mean |SHAP| (%) | Full mean |SHAP| (%) |
|---------------------|----------------------|----------------------|------------------------|
| Predisposing (16) | 0.79 (17.3%) | 0.21 (10.1%) | 0.90 (17.1%) |
| Enabling (20) | 0.90 (19.7%) | 0.23 (11.2%) | 0.80 (15.2%) |
| Need (11) | 1.24 (27.1%) | 0.41 (19.7%) | 0.82 (15.6%) |
| Dynamic (8) | 1.63 (35.9%) | 1.24 (59.0%) | 2.74 (52.1%) |

**Footnotes:** SHAP = SHapley Additive exPlanations. Values computed on held-out test set using TreeExplainer. Predisposing: demographics, social structure, health beliefs. Enabling: personal/family resources, community resources, geospatial covariates. Need: perceived need (health system engagement) and evaluated need (competing morbidity). Dynamic: temporal cascade features (inter-dose intervals, delay accumulation, community dropout rates, child age, dose count).

---

### Table 4. Off-policy evaluation of the CQL-learned intervention policy

**Caption:** Off-policy evaluation metrics comparing the conservative Q-learning (CQL) policy against the inferred behaviour policy. Policy value represents the expected cumulative discounted reward. Policy improvement is expressed as both absolute and percentage difference. Out-of-distribution (OOD) action frequency is the proportion of policy recommendations for actions observed in fewer than 1% of training trajectories.

| Metric | Value |
|--------|-------|
| Behaviour policy value | 1.104 |
| WIS policy value | 1.171 |
| FQE policy value | 1.178 |
| WIS improvement | +6.1% |
| FQE improvement | +6.7% |
| OOD action frequency (CQL) | 33.3% |
| OOD action frequency (behaviour) | 0.2% |
| CQL α | 5.0 |
| Validation episodes | 1,569 |

**Footnotes:** WIS = weighted importance sampling (clipping ε = 0.1). FQE = fitted Q-evaluation. CQL = conservative Q-learning. OOD = out-of-distribution. Policy improvement calculated as (learned policy value − behaviour policy value) / behaviour policy value × 100. The CQL penalty α = 5.0 was selected as the most conservative setting from α ∈ {1.0, 2.0, 5.0}.

---

### Table 5. Microsimulation scenario comparison

**Caption:** DTP3 completion rates, costs, cost-effectiveness, and equity outcomes across six intervention scenarios from microsimulation with 1,000 bootstrap iterations (synthetic population N = 10,000). Intervention effects applied as relative risk reductions on transition-specific dropout probabilities using literature-informed central estimates.

| Scenario | DTP3 rate (95% CI) | Cost/child (₦) | ICER vs S0 (₦) | Equity gap (pp) |
|----------|-------------------|-----------------|-----------------|-----------------|
| S0: Status quo | 85.9 (85.2-86.6) | 155 | — | 7.8 |
| S1: Uniform SMS | 87.1 (86.4-87.7) | 98 | Dominant | 7.2 |
| S2: Uniform CHW | 88.4 (87.8-89.0) | 979 | 32,742 | 6.6 |
| S3: Risk-targeted | 88.2 (87.6-88.8) | 341 | 8,007 | 6.7 |
| S4: RL-optimised | 88.2 (87.5-88.8) | 903 | 32,434 | 6.8 |
| S5: Bandit-allocated | 87.1 (86.5-87.8) | 98 | Dominant | 7.3 |

**Footnotes:** ICER = incremental cost-effectiveness ratio (₦ per additional DTP3 completion relative to S0). Dominant = better outcomes at lower cost than S0. Equity gap = absolute difference in DTP3 completion between poorest and richest wealth quintiles (percentage points). S3 risk-targeted: top 30% predicted dropout risk receive CHW home visit (a₂); remainder receive SMS (a₁). S4 RL-optimised: CQL-learned policy (α = 5.0) assigns actions based on 55-dimensional state vector. S5 bandit: LinUCB community-level allocation (α = 1.0, 1,140 communities). Effect sizes: a₁ = 10% RRR, a₂ = 20% RRR, a₃ = 25% RRR, a₄ = 14% RRR on transition-specific dropout probability.

---

## Supplementary Materials

### S1 Table. Complete predictor variable specification with DHS codes and Andersen domain mapping

**Source:** `docs/reference/dropout_variables_parameters.md` (to be formatted as supplementary table)

**Caption:** Complete specification of all 55 predictor variables used in the XGBoost models and MDP state space, including DHS variable codes, data types, recoding rules, and Andersen domain classification. Variables are grouped by domain: predisposing (n = 16), enabling (n = 20), need (n = 11), and dynamic/temporal (n = 8).

---

### S2 Table. XGBoost hyperparameter search space and optimal values

**Caption:** Optuna hyperparameter optimisation search space (200 trials per model) and selected optimal values for Models T1, T2, and Full. Optimisation criterion: AUC-ROC under five-fold cluster-robust cross-validation.

---

### S3 Table. CQL sensitivity analysis across α values

**Source:** `outputs/stage2/cql_alpha_sensitivity.csv`

**Caption:** Sensitivity analysis of CQL conservatism penalty α showing policy action distribution, out-of-distribution action frequency, mean Q-value, and off-policy evaluation metrics for α ∈ {1.0, 2.0, 5.0}.

---

### S4 Table. LinUCB budget sensitivity analysis

**Source:** `outputs/stage3/stage3_summary.json` (budget_sensitivity section)

**Caption:** Budget sensitivity analysis for the contextual multi-armed bandit showing intervention allocation, total cost, and community coverage at three national budget levels (₦250M, ₦500M, ₦1B). Costs scaled by an estimated 3,000 children per local government area.

---

### S5 Figure. SHAP beeswarm plots for transition-specific models

**Panel A:** `outputs/stage1/shap_beeswarm_model_t1.pdf`
**Panel B:** `outputs/stage1/shap_beeswarm_model_t2.pdf`
**Panel C:** `outputs/stage1/shap_beeswarm_model_full.pdf`

**Caption:** SHAP beeswarm plots showing the distribution of SHAP values for the top 20 features in each transition-specific XGBoost model. Each dot represents one child in the test set. Horizontal position indicates the SHAP value (positive = increases predicted dropout probability; negative = decreases). Colour indicates the feature value (red = high, blue = low). (A) Model T1 (DTP1→DTP2 dropout). (B) Model T2 (DTP2→DTP3 dropout). (C) Model Full (overall dropout).

---

### S6 Figure. SHAP bar plots for individual Andersen domain models

**Panel A:** `outputs/stage1/shap_bar_model_t1.pdf`
**Panel B:** `outputs/stage1/shap_bar_model_t2.pdf`
**Panel C:** `outputs/stage1/shap_bar_model_full.pdf`

**Caption:** Global SHAP feature importance (mean absolute SHAP value) for the top 20 features in each transition-specific model. Features are coloured by Andersen domain: predisposing (blue), enabling (green), need (orange), dynamic (red).

---

### S7 Figure. FQI convergence and OPE comparison

**Panel A:** `outputs/stage2/fqi_convergence.pdf`
**Panel B:** `outputs/stage2/ope_comparison.pdf`

**Caption:** (A) Fitted Q-iteration convergence showing the change in Q-values (ΔQ) across iterations. FQI converged at iteration 2 using ExtraTrees with 200 estimators. (B) Off-policy evaluation comparison showing estimated policy values for the behaviour policy and CQL-learned policy under weighted importance sampling (WIS) and fitted Q-evaluation (FQE).

---

### S8 Figure. Bootstrap distributions of microsimulation outcomes

**Source:** `outputs/stage3/bootstrap_distributions.pdf`

**Caption:** Bootstrap distributions of DTP3 completion rates for each of the six microsimulation scenarios across 1,000 replications. Vertical dashed lines indicate the mean estimate. Distributions illustrate the uncertainty in scenario outcomes due to sampling variability.

---

### S9 Figure. Bandit community-level allocation map

**Source:** `outputs/stage3/bandit_allocation.pdf`

**Caption:** LinUCB contextual bandit allocation of intervention actions across 1,140 communities under the ₦500 million national budget constraint. Colours indicate the allocated action for each community. The bandit converged predominantly to SMS allocation (99.6% of communities), reflecting SMS dominance in cost-effectiveness at the community level.

---

### S10 Figure. DTP dropout prevalence by state (bar chart)

**Source:** `outputs/stage0/dropout_prevalence_by_state.pdf`

**Caption:** DTP1-to-DTP3 dropout prevalence by state, sorted in descending order. Survey-weighted estimates from the Nigeria Demographic and Health Survey 2024. National weighted mean indicated by vertical line.

---

### S11 Figure. Zonal analysis of dropout by wealth gradient

**Source:** `outputs/stage0/zonal_analysis.pdf`

**Caption:** DTP dropout rates by geopolitical zone stratified by wealth quintile, showing the interaction between geographic and socioeconomic determinants of dropout. Survey-weighted estimates from NDHS 2024.

---

### S12 Figure. Calibration curves before and after isotonic recalibration

**Panel A:** `outputs/stage1/calibration_model_t1_recalibrated.pdf`
**Panel B:** `outputs/stage1/calibration_model_t2_recalibrated.pdf`

**Caption:** Calibration curves for Models T1 and T2 before (dashed) and after (solid) isotonic regression recalibration, with Loess smoothing. Histograms show the distribution of predicted probabilities. Ideal calibration (slope = 1.0, intercept = 0.0) indicated by the diagonal line. Recalibration improved T1 slope from 0.874 to 0.959 and T2 slope from 1.596 to 0.969.

---

## Summary Counts

| Category | Count |
|----------|-------|
| Main text figures | 8 |
| Main text tables | 5 |
| Supplementary tables | 4 |
| Supplementary figures | 8 |
| **Total** | **25** |
