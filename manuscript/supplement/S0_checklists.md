# Supplementary Material S0 — Reporting Checklists

## S0.1 TRIPOD-AI Checklist (Collins et al. 2024) [@ref17_collins2024tripod]

TRIPOD-AI (Transparent Reporting of a multivariable prediction model for Individual Prognosis Or Diagnosis — Artificial Intelligence) provides 22 items for reporting studies that develop or validate prediction models incorporating AI/ML methods.

| Item | Domain | Description | Section addressed | Notes |
|------|--------|-------------|-------------------|-------|
| 1 | Title | Identify the study as developing or validating a multivariable prediction model; specify the target population and outcome to be predicted | Title / §1 | Title specifies prediction of DTP1–DTP3 vaccine dropout in Nigeria; AI/ML framing stated |
| 2 | Abstract | Provide a structured summary including study design, setting, participants, sample size, predictors, outcome, statistical analysis, results, and conclusions | Abstract | Structured 4-beat abstract (background, methods, results, conclusions); AUROC, coverage gain, and ICER reported |
| 3 | Background and rationale | Explain the clinical/scientific background and rationale for developing or validating the prediction model, including references to existing models | §1 | Epidemiological burden of DTP dropout in Nigeria stated; gap in ML-RL integration motivated |
| 4 | Objectives | Specify the objectives including whether the study describes the development or validation of a prediction model (or both) | §1 | Three objectives stated: (i) ML prediction, (ii) offline RL policy, (iii) cost-effectiveness |
| 5 | Source of data | Describe the study design and data sources, including setting, location, dates, and rationale | §2.1 | NDHS 2024 (NGKR8BFL.dta, NGIR8BFL.dta); nationally representative; stratified two-stage cluster survey |
| 6 | Participants | Describe eligibility criteria and methods of participant selection; report numbers at each stage | §2.1 | Children 12–23 months, alive (b5==1), youngest per woman, card-confirmed DTP1 (h3∈{1,2,3}); N≈3,194; CONSORT-equivalent flow described |
| 7 | Outcome | Clearly define the outcome that is predicted by the prediction model, including how and when assessed | §2.2 | T1 dropout (h5==0 | h3∈{1,3}) and T2 dropout (h7==0 | h5∈{1,3}) defined with DHS variable precision |
| 8 | Predictors | Describe all predictors used in developing or validating the model, including method of measurement | §2.3 | 55 predictors catalogued across four Andersen domains; DHS variable codes given for all |
| 9 | Sample size | Explain how the sample size was arrived at | §2.1, §2.4 | Full analytic sample (N=3,194 T1; N=3,023 T2) used; no a-priori power calculation needed for secondary DHS analysis; event fractions reported |
| 10 | Missing data | Describe how missing data were handled | §2.1, §2.4 | Date codes 97/98 set to missing; XGBoost native handling of missing values used; imputation not required for tree models |
| 11 | Statistical analysis methods | Describe all aspects of the statistical analysis, including choice of model, hyperparameter tuning, and methods for internal validation | §2.4 | XGBoost; Bayesian hyperparameter search (Optuna, 200 trials); nested 5-fold cluster-robust CV; DeLong's test; isotonic recalibration |
| 12 | Development vs. validation | Specify the type of modelling: development only, validation only, or both; describe internal validation method | §2.4 | Development with internal validation via nested CV; no external validation dataset available |
| 13 | Model performance | Report model performance measures and their uncertainty (e.g., 95% CIs) | §3.1, Table 1 | AUROC, AUPRC, Brier score, ECE with 95% CIs from 1,000-iteration bootstrap/DeLong |
| 14 | Model specification | Present the full prediction model to allow predictions for individuals | §S1 (supplement), outputs/stage1/ | Calibrated model artefacts (isotonic_calibrator_t*.pkl) deposited at GitHub repository |
| 15 | Calibration | Report calibration of the model predictions | §2.4, §3.1, Figures S1–S4 | Calibration slope and Brier score pre- and post-isotonic recalibration; calibration curves in Figures S1–S4 |
| 16 | Uncertainty | Quantify uncertainty in model performance and predictions | §2.4, §3.1 | 1,000-iteration bootstrap CIs for all performance metrics; PSA (1,000 iterations) propagates prediction uncertainty through microsimulation |
| 17 | Explainability | Describe any methods used to explain or interpret the predictions of the model | §2.4, §3.1, Figures 2–3, Figure S12 | SHAP TreeExplainer; beeswarm and bar plots; Andersen-domain decomposition (Figure S12) |
| 18 | Limitations | Discuss any limitations of the study, including potential sources of bias | §4 | Cross-sectional DHS design; no external validation; proxy behaviour policy; partial observability |
| 19 | Interpretation | Discuss the results in context; give an overall interpretation of the results | §4 | Clinical and policy interpretation; comparison with prior Nigeria DTP literature |
| 20 | Implications | Discuss the potential implications for practice, policy, and future research | §4, §5 | Policy recommendations for NPHCDA; dashboard for operational use; future RL trial design recommended |
| 21 | Supplementary information | Provide additional information | §§S0–S3 | Four supplement sections: checklists, extended methods, parameter tables, figures and tables |
| 22 | Funding | Provide information about the funding source(s) and the role of the funders | Back matter | Funding and conflict-of-interest statement in back matter (§99) |

---

## S0.2 CHEERS 2022 Checklist (Husereau et al. 2022) [@ref36_husereau2022consolidated]

CHEERS 2022 (Consolidated Health Economic Evaluation Reporting Standards) provides 28 items for reporting health economic evaluations. This study reports a microsimulation cost-effectiveness analysis.

| Item | Domain | Description | Section addressed | Notes |
|------|--------|-------------|-------------------|-------|
| 1 | Title | Identify the study as an economic evaluation and specify the interventions being compared | Title / §1 | Title identifies RL-optimised intervention; economic evaluation framing in abstract and §1 |
| 2 | Abstract | Provide a structured summary including the economic perspective, comparators, key methods, base-case results, and funding | Abstract | Cost per DTP3 coverage gain, ICER versus status quo, and CEAC probability stated in abstract |
| 3 | Background and objectives | Give the context for the study, the study question, and its relevance to health policy or practice | §1 | Nigeria DTP3 coverage gap; economic case for targeted intervention; policy relevance to NPHCDA |
| 4 | Health economic analysis plan | Indicate whether a health economic analysis plan was developed and where available | §2.7 | PSA parameters pre-specified in CLAUDE.md protocol; microsimulation scenarios (S0–S5) defined prior to analysis |
| 5 | Study population | Describe characteristics of the study population (who) and subgroups analysed | §2.1, §3.4 | Children 12–23 months with card-confirmed DTP1 in Nigeria; subgroup analyses by zone, wealth, urban/rural, maternal education |
| 6 | Setting and location | Describe the setting and location for the study | §2.1 | Nigeria, nationally representative NDHS 2024; LGA-level allocation for bandit analysis |
| 7 | Comparators | Describe the interventions or strategies being compared and why chosen | §2.7 | Six scenarios: S0 (status quo), S1 (uniform SMS), S2 (uniform CHW), S3 (risk-targeted), S4 (RL-optimised), S5 (bandit-allocated) |
| 8 | Perspective | State the perspective of the study | §2.7 | Health system payer perspective (NPHCDA); societal costs not included |
| 9 | Time horizon | State the time horizon for the study and why appropriate | §2.7 | Two-step decision horizon (DTP1→DTP2→DTP3) consistent with childhood immunisation schedule |
| 10 | Discount rate | Report the discount rate(s) and rationale | §2.7 | Discount factor γ=0.95 applied within RL; economic outcomes are short-term (≤6 months per child) so discounting is minimal |
| 11 | Selection of outcomes | Describe what outcomes were used as the measure of benefit and why selected | §2.7 | DTP3 coverage (%) as primary outcome; cost per additional percentage-point of coverage as ICER; concentration index as equity outcome |
| 12 | Measurement of outcomes | Describe how the outcomes used to capture the benefits were measured | §2.7, §3.4 | Simulated from microsimulation (1,000 PSA iterations × 3,000 bootstrap cohort); DTP3 completion modelled via reward function |
| 13 | Valuation of outcomes | Describe the population and methods used to value the outcomes | §2.7 | Willingness-to-pay thresholds informed by Nigerian per-capita GDP benchmark (₦50,000/percentage-point base; Table S2.1) |
| 14 | Measurement and valuation of resources and costs | Describe how costs were valued | §2.5, §2.7, Table S2.1 | Unit costs (₦): a₁=50, a₂=500, a₃=1,500, a₄=800; sourced from NPHCDA estimates and CLAUDE.md; PSA ±25% |
| 15 | Currency, price date, and conversion | Report the currency, price date, and any conversion rates used | §2.7, Table S2.1 | 2026 Nigerian Naira; no currency conversion required |
| 16 | Rationale and description of model | If a model is used, describe in detail and why used | §2.7 | Discrete-event microsimulation with 3,000 bootstrap replicates; PSA on effect sizes, costs, and λ; RL policy applied as intervention |
| 17 | Analytics and assumptions | Describe all analytical methods supporting the evaluation | §2.5, §2.6, §2.7 | FQI/CQL policy learning; LinUCB bandit; microsimulation; IS/WIS/DR OPE; one-way tornado sensitivity |
| 18 | Characterising heterogeneity | Describe any methods used to characterise heterogeneity in costs and outcomes | §3.4, §S3.1 | Subgroup analyses by zone, wealth quintile, urban/rural, maternal education; Tables S1–S5; slope index of inequality |
| 19 | Characterising distributional effects | Describe how distributional effects were considered | §2.7, §3.4 | Concentration index; absolute wealth-quintile gap; slope index of inequality reported alongside ICER |
| 20 | Characterising uncertainty | Describe methods to characterise uncertainty | §2.7, §3.4 | PSA: 1,000 iterations; cost-effectiveness plane scatter; CEAC across ₦0–₦500,000/pp; tornado one-way sensitivity (top-10 parameters) |
| 21 | Approach to engagement with patients and others affected by the study | Describe any approaches to engage patients, service recipients, the public, carers, or family members | §2.8 | Open-access interactive dashboard with public-facing Story module; WCAG 2.1 AA accessibility; text transcript alternative |
| 22 | Study findings, limitations, and generalisability | Report key findings, limitations of the study, and generalisability | §3.4, §4 | ICER reported per scenario; limitations of DHS-derived microsimulation stated; generalisability to similar LMIC settings discussed |
| 23 | Source of funding | Describe how the study was funded and any role of the funder | Back matter | Funding statement in back matter (§99) |
| 24 | Conflicts of interest | Report authors' conflicts of interest | Back matter | Conflict-of-interest statement in back matter (§99) |
| 25 | Choice of model | Describe and justify the model chosen for the economic analysis | §2.7 | Microsimulation chosen over decision tree/Markov to capture individual-level heterogeneity and RL policy rollout |
| 26 | Assumptions | Describe all structural and other assumptions underpinning the model | §2.7, §4 | Constant effect sizes during PSA range; NPHCDA budget ceiling assumed; DHS 2024 as representative of current population |
| 27 | Data inputs | Report all data inputs including their sources and methods of synthesis | §2.3, §2.7, Table S2.1 | Effect sizes from meta-analyses (Table S2.1); costs from NPHCDA; population from NDHS 2024; geospatial from DHS GC dataset |
| 28 | Characterising structural uncertainty | Describe how structural uncertainty was addressed | §4 | Sensitivity analysis comparing FQI vs CQL policies; bandit vs MDP formulations; alternate reward weight specifications discussed |

---

## S0.3 Gottesman 2019 RL-in-Health Issue-Response Table [@ref30_gottesman2019guidelines]

Gottesman et al. (2019) identified seven methodological issues that must be addressed when applying reinforcement learning to healthcare. Each is addressed below.

| Issue | Description | How addressed in this study | Section |
|-------|-------------|----------------------------|---------|
| 1. Partial observability | In real health settings, the Markov state is typically not fully observed; unmeasured confounders and latent patient history violate the MDP assumption | Acknowledged as a key limitation. DHS data are cross-sectional; unmeasured time-varying confounders (e.g., outbreak events, stock-outs) cannot be captured. Recalibrated XGBoost risk scores (from §2.4) are used as a compact state representation to compress observable history into a probabilistic summary of latent dropout risk. This is documented in the limitations section | §2.5, §4 (limitations) |
| 2. Confounding | Observed actions in off-policy datasets may be confounded by unmeasured variables, biasing behaviour-policy estimates | DHS does not record interventions. Structured proxy-action inference rules (per CLAUDE.md) map observable DHS patterns — inter-dose intervals, fieldworker visit (v393), health card (h1a), vaccination venue (h69) — to the five-action space. CQL regularisation penalises extrapolation to out-of-distribution (state, action) pairs, limiting reliance on confounded behaviour-policy regions | §2.5, §S1.4 |
| 3. Reward specification | Misspecification of the reward function can lead to policies that optimise proxies rather than true outcomes | Reward weights are fully disclosed: R = 1.0·𝟙[DTP3] + 0.3·𝟙[next dose] − λ·cost, with λ=0.001. A probabilistic sensitivity analysis (PSA) sweeps λ over [0.0005, 0.002] and draws effect-size weights from normal distributions derived from LMIC meta-analyses. Reward weight rationale is given in §2.5 | §2.5, §2.7 |
| 4. Off-policy evaluation | Learning from historical data without the ability to interact with the environment makes it difficult to evaluate the learned policy reliably | Three OPE estimators are compared on 1,569 held-out episodes: importance sampling (IS), weighted importance sampling (WIS), and doubly-robust (DR). Estimator agreement is reported as the primary evidence for policy quality; disagreement is flagged as uncertainty | §2.5, §3.3, §S1.3 |
| 5. Distributional shift | The learned policy may recommend actions in regions of state space poorly supported by historical data | CQL's conservatism hyperparameter α is grid-searched; α=1.0 is selected as the base case with sensitivity reported in Figure S8. The LinUCB bandit (§2.6) is further constrained to the empirical support of LGA-level covariates. Out-of-distribution Q-values are suppressed by the CQL penalty | §2.5, §2.6, Figure S8 |
| 6. Safety and behaviour constraints | RL policies in healthcare must not recommend harmful or untested actions | The action space is restricted by design to five established, benign public-health interventions with documented safety profiles in LMIC settings: no intervention, SMS reminder, CHW home visit, facility recall with defaulter tracing, and conditional cash/in-kind incentive. No novel or potentially harmful treatments are included. All actions are currently deployed within Nigerian immunisation programmes | §2.5 |
| 7. Interpretability | Clinicians and policymakers require understanding of why a policy recommends specific actions | Full state-to-action policy lookup table published (outputs/stage2/policy_lookup.csv; Supplementary Table S6 / §S3). SHAP values from XGBoost risk models identify the most influential predictors at each dose step (Figures 2–3, S5–S6, S12). Andersen-domain SHAP decomposition summarises which factor domains drive recommendations (Figure S12) | §2.4, §2.5, §S3 |
