## 2. Materials and Methods

### 2.1 Data Source and Study Population

We conducted a secondary analysis of the 2024 Nigeria Demographic and Health Survey (NDHS 2024), a nationally representative, stratified two-stage cluster household survey implemented by the National Population Commission with technical support from ICF International [@ref18_npc2025ndhs]. Children's vaccination histories, health records, and maternal characteristics were drawn from the Children's Recode (NGKR8BFL.dta), Individual Recode (NGIR8BFL.dta), and Household Recode (NGHR8BFL.dta) files, with cluster-level geospatial covariates from the DHS Geospatial Covariate dataset (NGGC8AFL.csv) [@ref19_icf2023geostat].

The analytic sample was restricted to children aged 12–23 months at the time of the survey (age_months = v008 − b3, where v008 is the interview date in century-month code and b3 is the child's birth date), who were alive (b5 == 1) and identified as the youngest child per woman. Crucially, the cohort was further restricted to children with card-confirmed DTP1 vaccination records (h3 ∈ {1, 2, 3}), thereby defining the study as a **retention analysis** of cascade entrants rather than an access analysis: children who never received DTP1 were excluded by design. Date values coded 97 (inconsistent) or 98 (don't know) were treated as missing. This yielded an analytic sample of approximately 3,194 DTP1-initiating children (exact N in Table 1).

All analyses incorporated the complex survey design using sampling weights (v005/1,000,000), stratification variable v022, and primary sampling unit v021. Geographic coding used szone (geopolitical zone) and sstate — not v024 — consistent with the DHS Nigeria sampling frame. Ethical approval was granted by ICF's Institutional Review Board and the Nigeria National Health Research Ethics Committee (NHREC); all data were de-identified. No additional ethics review was required for this secondary analysis.

### 2.2 Outcome Definitions

Two transition-specific dropout outcomes were defined to model the DTP cascade as a sequential process:

- **T1 dropout**: children with card-confirmed DTP1 (h3 ∈ {1, 3}) who did not subsequently receive DTP2 (h5 == 0), representing exit at the first transition.
- **T2 dropout**: children with card-confirmed DTP2 (h5 ∈ {1, 3}) who did not subsequently receive DTP3 (h7 == 0), representing exit at the second transition.

As a secondary national-level outcome, the WHO cascade dropout rate was computed as (DTP1 coverage − DTP3 coverage) / DTP1 coverage × 100 [@ref4_who2020ia2030; @ref50_wuenic2024]. This formulation was applied to the DTP1-initiating cohort, and explicitly excludes access failure (no DTP1 received) from the denominator — a distinction critical for targeting retention-focused interventions.

Inter-dose intervals were derived from card-confirmed vaccination dates (DTP1: h3d/h3m/h3y; DTP2: h5d/h5m/h5y; DTP3: h7d/h7m/h7y; birth: h25d/h25m/h25y). Timeliness was defined as DTP1 receipt by 56 days (8 weeks) from birth, DTP2 by 84 days (12 weeks), and DTP3 by 112 days (16 weeks), consistent with the Nigeria Expanded Programme on Immunization schedule [@ref21_nphcda2018nsipss].

### 2.3 Predictors and Conceptual Framework

All 55 predictor variables were organised within Andersen's Behavioural Model of Health Services Use [@ref8_andersen1995revisiting], which distinguishes predisposing, enabling, and need domains. We extended this framework with a dynamic/temporal domain capturing the child's evolving state within the immunisation cascade.

**Predisposing factors** (n = 16) encompassed demographic characteristics (maternal age [v012], child sex [b4], birth order [bord], highest birth order [hbord], parity [v201]), social structural variables (maternal education [v106], partner's education [v701], polygynous union [v505], ethnicity [v131]), and health belief proxies including decision-making autonomy (v743a), permission barrier to seeking care (v467b), media access (television [v159], radio [v158], newspaper/magazine [v157], any-media composite [media2]), COVID-19 vaccine willingness (s1112s), and COVID-19 vaccine receipt as a healthcare-trust proxy (s1112p).

**Enabling factors** (n = 20) included personal and family resources (wealth quintile [v190], wealth factor score [v191], maternal employment [v714], health insurance [v481], household size [v136], female head of household [v151], number of under-five children [v137]), and community resources (rural residence [v025], geopolitical zone [szone], travel time to the nearest health facility in continuous minutes [v483a — not the categorical v467d]). Community-level composites were constructed by aggregating individual data to the cluster: poverty rate, illiteracy rate, unemployment rate, media saturation, ethnic diversity index, and zonal socioeconomic status score (com_*). Geospatial covariates from the DHS Geospatial Covariate dataset included UN Population Density 2020, OpenStreetMap-derived travel times, Nightlights Composite (VIIRS), Malaria Prevalence 2020, and ITN Coverage 2020 [@ref19_icf2023geostat; @worldpop2020; @malariaatlas2020].

**Need factors** (n = 11) comprised perceived need indicators — health card possession (h1a), antenatal care visits (m14), facility delivery (m15), child fever (h22), diarrhoea symptoms (h34), postnatal care (m70, m74), and fieldworker visit in the preceding 12 months (v393) — and evaluated need indicators — vaccination venue (h69), contact count, recent illness (h11).

**Dynamic/temporal features** (n = 8) captured the child's state within the cascade at each dose step: child age in weeks, doses received (0–2), dose step (T1 or T2), timeliness of the previous dose (last_dose_timely), inter-dose interval in days, cumulative delay accumulation, cluster-level community dropout rate, and cluster DTP3 coverage.

### 2.4 Prediction Modelling

We trained separate binary XGBoost gradient-boosted classifiers [@ref22_chen2016xgboost] to predict T1 dropout (n = 3,194) and T2 dropout (n = 3,023). XGBoost was selected for its handling of mixed variable types, built-in regularisation, and demonstrated performance in health survey prediction tasks. This analysis is reported in accordance with TRIPOD-AI guidance [@ref17_collins2024tripod]; a summary checklist is provided in Supplementary Table S0.1.

**Hyperparameter optimisation** used Bayesian search (Optuna) with 200 trials per model under nested 5-fold stratified cross-validation: outer folds estimated generalisation performance, inner folds tuned max_depth, learning_rate, n_estimators, subsample, colsample_bytree, gamma, reg_alpha, reg_lambda, and scale_pos_weight. Class imbalance — T1 dropout prevalence 4.0%, T2 prevalence 3.9% (recalibration log, 2026-04-06) — was addressed via scale_pos_weight. Cluster-robust folds held out entire primary sampling units (v021) to prevent information leakage between spatially proximate children.

**Performance metrics** included AUROC, AUPRC, Brier score, and expected calibration error (ECE), each with 95% confidence intervals from 1,000-iteration DeLong/bootstrap resampling [@ref24_delong1988comparing]. XGBoost discrimination was benchmarked against logistic regression using DeLong's test for correlated AUROCs.

**Post-hoc recalibration** was applied via isotonic regression [@ref27_niculescu2005predicting] using 5-fold cluster-robust out-of-fold predictions as the calibrator-fit input. For T1, isotonic recalibration improved the calibration slope from 0.874 to 0.959 and reduced Brier score from 0.036 to 0.032; for T2, slope improved from 1.596 to 0.969 and Brier score decreased from 0.027 to 0.026 (outputs/stage1/recalibration_log.md). Calibrator artefacts were saved to outputs/stage1/isotonic_calibrator_t1.pkl and outputs/stage1/isotonic_calibrator_t2.pkl. Recalibrated risk scores were passed as state features to the downstream RL stage.

**Explainability** was conducted via SHAP TreeExplainer [@ref28_lundberg2017unified], generating per-child feature attributions. Top-10 beeswarm and bar summaries are reported per transition in the main figures; Andersen-domain decomposition of summed absolute SHAP contributions is reported as Supplementary Figure S3.

### 2.5 MDP Formulation and Offline Reinforcement Learning

We formulated sequential dropout-prevention intervention as a finite-horizon Markov Decision Process (MDP) [@ref12_ernst2005treebased], following the reporting framework for RL in health of Gottesman et al. (2019) [@ref30_gottesman2019guidelines].

**State** *s* comprised the full 55-dimensional feature vector described in §2.3, augmented with recalibrated T1 and T2 risk scores from §2.4.

**Action space** (five discrete actions, per CLAUDE.md):
- *a₀*: No intervention (₦0)
- *a₁*: SMS reminder (₦50; literature effect +5–10% completion)
- *a₂*: CHW home visit (₦500; +15–25% completion)
- *a₃*: Facility recall and defaulter tracing (₦1,500; +20–30% completion)
- *a₄*: Conditional cash or in-kind incentive (₦800; +10–20% completion)

Effect-size ranges were informed by LMIC evidence for mHealth reminders [@ref9_eze2021mhealth; @ref49_cochrane2018reminder], CHW outreach [@ref11_banerjee2010improving], and conditional transfer programmes [PLEASE VERIFY: citation for a₄ CCT effect size from outputs/literature/intervention_effect_sizes.csv]; a structured literature review is reported in Supplementary Table S1.1.

**Reward function**: R(s, a, s') = 1.0·𝟙[DTP3 completed] + 0.3·𝟙[next dose received] − λ·cost(a), with default λ = 0.001. Discount factor γ = 0.95 over the two-step decision horizon (T1, T2).

**Behaviour-policy inference**: Because DHS does not record interventions, proxy actions were inferred from observed patterns. Children whose next dose arrived on time (≤2 weeks of schedule) with a fieldworker visit (v393 == 1) were assigned *a₂*; those on time at a campaign site (h69 == 41) were assigned *a₃*; those on time with a health card present (h1a ≥ 1) were assigned *a₁*; children receiving a late dose (>2 weeks delayed) were assigned *a₀* or *a₁*; children not receiving the next dose were assigned *a₀*. A complete rule table is provided in Supplementary §S1.4. This yielded 6,217 trajectory rows from 3,138 children.

**Policy learning** employed two offline RL algorithms. Fitted Q-Iteration (FQI) [@ref12_ernst2005treebased] used ExtraTrees as the function approximator, iteratively fitting Bellman backup targets until convergence (ΔQ < 0.01) or 200 iterations. Conservative Q-Learning (CQL) [@ref13_kumar2020conservative] penalises out-of-distribution Q-values via a conservatism parameter α, which was grid-searched and is reported in Supplementary Figure S5. Off-policy evaluation used importance sampling (IS), weighted importance sampling (WIS), and doubly robust (DR) estimators [@ref32_jiang2016doubly], evaluated on 1,569 held-out episodes.

**Gottesman seven-limitation checklist** [@ref30_gottesman2019guidelines]: (i) *Partial observability* — DHS observations are cross-sectional; unmeasured time-varying confounders are acknowledged in limitations; (ii) *Confounding* — behaviour-policy inference applies structured rules to proxy unobserved interventions from observed DHS variables (v393, h1a, h69, inter-dose intervals); (iii) *Reward specification* — fixed reward weights are disclosed and a probabilistic sensitivity analysis (PSA) sweeps λ over [0.0005, 0.002]; (iv) *Off-policy evaluation* — IS, WIS, and DR estimators all reported; (v) *Distributional shift* — CQL regularisation constrains learned policies toward the data support; (vi) *Safety* — the action space is restricted to established, benign public-health interventions with documented safety profiles; (vii) *Interpretability* — the full state-to-action policy lookup table is published at outputs/stage2/policy_lookup.csv. The completed checklist is provided in Supplementary §S0.3.

### 2.6 Contextual Bandit for LGA-Level Allocation

A Linear Upper Confidence Bound (LinUCB) contextual bandit [@ref33_li2010contextual] was implemented for budget-constrained allocation of the five actions across Nigeria's 774 local government areas (LGAs). The context vector comprised 19 LGA-level aggregates of covariates in §2.3 — including mean dropout risk, mean wealth index, urbanisation rate, facility travel time, and the geospatial covariates — plus ML-derived risk scores and community dropout rates as priors from the trained Q-function.

Budget constraints were based on per-action unit costs and NPHCDA 2025 budget ceilings [PLEASE VERIFY: NPHCDA 2025 ceiling reference], with a national envelope of ₦500 million (sensitivity analyses at ₦250 million and ₦1 billion). A bandit formulation was preferred over direct application of the sequential RL policy at the LGA level because it handles population-level contextual heterogeneity in one decision step, circumventing partial observability that complicates child-level MDP rollouts at aggregate scale, while using Q-function priors as warm-start reward estimates.

### 2.7 Microsimulation and Probabilistic Sensitivity Analysis

A synthetic child-level cohort of 3,000 bootstrap replicates drawn from the NDHS 2024 DTP1-initiating sample was simulated under six pre-specified scenarios:

- **S0**: Status quo — observed behaviour policy, no additional intervention;
- **S1**: Uniform SMS — *a₁* applied at every dose step for all children;
- **S2**: Uniform CHW — *a₂* applied at every dose step for all children;
- **S3**: Risk-targeted — children in the top decile of ML-predicted dropout risk receive *a₂*; remainder receive *a₁*;
- **S4**: RL-optimised — the CQL-learned sequential policy π* from §2.5 assigns actions based on each child's state vector;
- **S5**: Bandit-allocated — LinUCB LGA-level allocation from §2.6 applied to all children within each LGA.

Each scenario was iterated 1,000 times for the probabilistic sensitivity analysis (PSA), drawing intervention effect sizes from normal distributions on the log-odds scale with standard deviations derived from LMIC meta-analyses (outputs/literature/intervention_effect_sizes.csv), costs from uniform ±25% around base values, and λ from [0.0005, 0.002].

**Primary outcomes** were: (a) DTP3 coverage (%); (b) cost per child in 2026 Nigerian Naira; (c) incremental cost-effectiveness ratio (ICER) versus S0, expressed as ₦ per additional percentage-point of DTP3 coverage; (d) cost-effectiveness acceptability curves (CEAC) across willingness-to-pay thresholds from ₦0 to ₦500,000 per percentage-point gain; (e) cost-effectiveness plane scatter. One-way tornado sensitivity was conducted across the top-10 parameters by ICER range. **Equity outcomes** included the concentration index, absolute wealth-quintile gap in DTP3 completion, and the slope index of inequality.

This analysis is reported in accordance with CHEERS 2022 [@ref36_husereau2022consolidated]; a completed checklist is provided in Supplementary §S0.2.

### 2.8 Interactive Web Dashboard

To support policy translation and public engagement, we developed an open-access interactive web dashboard providing a comprehensive visualisation of model inputs, predictions, RL-optimised policies, and microsimulation outcomes. The dashboard (Figure 5) is accessible at https://olatechie.github.io/dropout/ and comprises four modules: **Story** (a cinematic narrative tracing the DTP cascade from DTP1 initiation to DTP3 completion or dropout, with annotated maps and temporal animations); **Policy** (a choropleth map of RL-recommended intervention actions by LGA, with drill-down to individual state summaries); **Simulation** (a user-controlled scenario explorer enabling on-the-fly cost-effectiveness comparison across all six microsimulation scenarios); and **Explorer** (interactive subgroup and covariate filters for disaggregated analysis by zone, wealth quintile, maternal education, and urban–rural residence). Accessibility conforms to WCAG 2.1 Level AA; a full text alternative is available at /story/transcript for readers who prefer non-interactive access. Source code is openly released under the MIT licence at https://github.com/olatechie/dropout.

### 2.9 Reporting Standards, Software, and Reproducibility

This study is reported in compliance with three methodological frameworks: TRIPOD-AI for the prediction models [@ref17_collins2024tripod], CHEERS 2022 for the economic evaluation [@ref36_husereau2022consolidated], and the Gottesman et al. RL-in-health guidelines for the offline reinforcement learning components [@ref30_gottesman2019guidelines]. Completed checklists for all three frameworks are provided in Supplementary Materials (§§S0.1–S0.3).

All analyses were conducted in Python 3.11 with pandas, scikit-learn, xgboost, shap, geopandas, matplotlib, and statsmodels; full version numbers are listed in Supplementary Table S2.2. The random seed was fixed at 42 throughout; 5-fold cluster-robust cross-validation was used for all model evaluation; 1,000-iteration bootstrap and PSA were used for all uncertainty quantification. Code, derived artefacts, and the interactive dashboard are openly available at https://github.com/olatechie/dropout.
