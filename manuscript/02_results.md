## 3. Results

### 3.1 Cohort Characteristics

The analytic cohort comprised 3,194 children aged 12–23 months with card-confirmed DTP1 vaccination from the 2024 Nigeria Demographic and Health Survey, constituting a retention analysis of cascade entrants rather than an access analysis (Table 1, Figure 1). The cohort was approximately equally split by sex (50.1% male) and 51.0% resided in rural areas, with no rural–urban difference by dropout status (p = 1.000). Maternal age averaged 29.8 years (SD 6.5); dropout children were born to slightly younger mothers (29.0 vs 29.9 years; p = 0.012).

Wealth distribution differed markedly by dropout status (p < 0.001): the richest quintile comprised 26.0% of non-dropout children but only 13.1% of dropout children, while the poorest quintile accounted for 19.9% of dropout children versus 16.1% of non-dropout children. No maternal education was reported in 32.8% of dropout children versus 25.4% of non-dropout children, while higher education was present in 18.4% of non-dropout but only 7.0% of dropout children (p < 0.001). Health insurance was low overall (3.9%) and lower still in the dropout group (2.1% vs 4.2%; p = 0.047). Absence of a vaccination card (h1a = 0) was markedly more common among dropout children (37.3% vs 15.2%; p < 0.001), mean antenatal visits were lower (4.9 vs 6.9; p < 0.001), and mean travel time to facility was longer (29.1 vs 24.3 min; p < 0.001).

The national weighted WHO DTP1-to-DTP3 dropout rate was 14.60% (Figure 1A). Subnational variation was pronounced: North Central recorded the highest dropout rate (19.59%), followed by North East (16.85%), South East (14.06%), North West (13.76%), and South West (12.99%); South South recorded the lowest (8.56%). North Central contributed 16.9% of the sample (n = 541) but 23.5% of dropout events (n = 111), while South South contributed 14.2% of the sample (n = 454) but only 9.5% of dropout events (n = 45). The zone-stratified cascade (Figure 1B) shows T1 retention ranging from 92.5% in North Central to 98.1% in South East.

---

### 3.2 Prediction-Model Performance

Two transition-specific XGBoost classifiers were developed and evaluated separately for the DTP1→DTP2 (T1) and DTP2→DTP3 (T2) dropout steps, following TRIPOD-AI reporting standards, under cluster-robust 5-fold cross-validation with 1,000-iteration bootstrap confidence intervals (Table 2, Figure 2).

**T1 model (DTP1→DTP2; n = 3,194; prevalence = 4.0%):** Discrimination was good: AUROC = 0.910 (95% CI 0.885–0.932); AUPRC = 0.299 (95% CI 0.230–0.387). XGBoost substantially outperformed logistic regression (AUROC 0.910 vs 0.818; DeLong difference 0.091; z = 6.14; p = 8.1×10⁻¹⁰). Isotonic recalibration improved the calibration slope from 0.874 to 0.959 and the Brier score from 0.0358 to 0.0319. Andersen-domain SHAP decomposition identified dynamic/temporal features as the dominant predictor domain (summed mean-absolute SHAP contribution 1.635), followed by need factors (1.237), enabling factors (0.897), and predisposing factors (0.788), indicating that cascade-timing dynamics are more predictive of T1 exit than fixed socioeconomic characteristics.

[PLEASE VERIFY: top-3 SHAP feature labels from Figure 2 panel C — inspect `outputs/stage1/shap_bar_model_t1.pdf`.]

**T2 model (DTP2→DTP3; n = 3,023; prevalence = 3.9%):** Discrimination was excellent: AUROC = 0.943 (95% CI 0.929–0.957); AUPRC = 0.548 (95% CI 0.454–0.640). XGBoost again outperformed logistic regression (AUROC 0.943 vs 0.863; DeLong difference 0.086; z = 6.11; p = 9.7×10⁻¹⁰). The T2 model required substantially more recalibration: the pre-recalibration slope of 1.596 indicated systematic over-dispersion of predicted probabilities, which was corrected to 0.969 after isotonic regression; the Brier score improved from 0.0274 to 0.0255. Andersen-domain decomposition showed dynamic/temporal features again dominant (1.240), with need (0.414), enabling (0.235), and predisposing (0.212) contributing progressively less — the enabling-domain contribution was substantially smaller than at T1 (0.235 vs 0.897), suggesting that structural access barriers are more salient at the first dropout step than at the second.

[PLEASE VERIFY: top-3 SHAP feature labels from Figure 2 panel D — inspect `outputs/stage1/shap_bar_model_t2.pdf`.]

The trajectory dataset used for RL training comprised 6,217 rows from 3,138 unique children, derived from the recalibrated risk scores passed forward from Stage 1.

---

### 3.3 RL-Optimised Policy and LGA-Level Allocation

**Off-policy evaluation:** Three offline RL algorithms were evaluated against held-out episodes using Fitted Q-Evaluation (FQE) and Weighted Importance Sampling (WIS) estimators. Implicit Q-Learning (IQL) achieved the highest FQE value (0.872) and WIS value (0.689) with zero out-of-distribution (OOD) actions, identifying it as the best-performing and most conservative algorithm. Conservative Q-Learning (CQL) returned FQE = 0.700 and WIS = 0.649, and BCQ returned FQE = 0.610 and WIS = 0.636. All three algorithms recorded 0.0% OOD actions, confirming that the learned policies operated exclusively within the support of the observed behaviour policy. The full state-to-action policy lookup for the winning IQL algorithm is available at `outputs/stage2/policy_lookup.csv`.

**LGA-level bandit allocation:** The LinUCB contextual bandit allocated recommended actions across 1,140 community clusters spanning Nigeria's 774 local government areas (Figure 3). Under the cost-constrained allocation, action a₁ (SMS reminder, ₦50) was recommended in almost all clusters: 1,139 of 1,140 clusters (99.9%), with a single cluster assigned action a₂ (CHW home visit, ₦500). Actions a₀, a₃, and a₄ received no allocations. This extreme concentration reflects the bandit's preference for the cheapest intervention once expected marginal gain is discounted by NPHCDA budget ceilings: under a national envelope of ₦500 million, the per-cluster cost advantage of SMS overwhelms the modest incremental effectiveness of more intensive strategies at the population level.

It is important to note that the near-uniform SMS allocation arises from the budget-constrained single-step bandit formulation and does not represent the full action diversity of the sequential IQL policy. The choropleth in Figure 3 displays modal action per state from the RL policy; geographic heterogeneity is evident, with more intensive interventions concentrated in higher-burden northern states.

[PLEASE VERIFY: OPE values for IS and DR estimators, if available beyond FQE and WIS, from `outputs/stage2_v2/ope_comparison.csv`.]

---

### 3.4 Microsimulation and Cost-Effectiveness

Six scenarios were simulated across 1,000 PSA iterations of 10,000 children each (Table 3, Table 4, Figure 4). Status-quo DTP3 coverage (S0) was 0.9141 (95% CI 0.9024–0.9247) at zero incremental cost.

**Coverage and cost:** Uniform CHW (S2), risk-targeted (S3), and bandit-allocated (S5) achieved comparable peak coverage gains (approximately +1.50 pp over S0) at costs of ₦1,012.89, ₦445.32, and ₦605.47 per child, respectively. Uniform SMS (S1) yielded a smaller gain (+0.74 pp) at the lowest cost (₦100.81). The RL-optimised scenario (S4) produced intermediate coverage (0.9248; 95% CI 0.9139–0.9350; Δ = +1.07 pp) at ₦748.00 per child (95% CI ₦427.51–₦1,147.79).

**ICERs:** Deterministic ICERs versus S0 were: S1 = ₦137/pp, S3 = ₦301/pp, S5 = ₦404/pp, S2 = ₦675/pp, and S4 = ₦699/pp. Risk-targeting (S3) thus achieved the most favourable ICER among the high-coverage scenarios.

**PSA distributions:** PSA ICER distributions confirmed the ordering under uncertainty. S3 had a mean ICER of ₦30,841 (95% CI ₦16,811–₦50,173); S4 had a mean ICER of ₦71,992 (95% CI ₦36,683–₦122,330), and S1 had a mean ICER of ₦14,997 (95% CI ₦6,528–₦30,221).

**CEAC:** At a willingness-to-pay of λ = ₦50,000 per percentage-point DTP3 gain, the risk-targeted scenario (S3) had the highest cost-effectiveness probability (56.7%), and Uniform SMS (S1) was cost-effective with probability 43.3%. At this threshold, the RL-optimised scenario (S4) had a cost-effectiveness probability of 0%, consistent with its PSA ICER distribution exceeding ₦50,000/pp throughout. S2 and S5 likewise returned 0% probability at this threshold. The RL policy's value proposition depends on willingness-to-pay thresholds above approximately ₦70,000/pp, where its state-adaptive action diversity may deliver equity and coverage benefits unavailable to simpler strategies.

**Tornado:** One-way sensitivity analysis confirmed that the relative risk reduction (RRR) parameter was the dominant source of coverage uncertainty (range = 0.0076), while ±25% cost variation had no effect on coverage (range = 0.0000; Table 4), confirming that coverage outcomes are driven entirely by intervention efficacy rather than cost inputs.

---

### 3.5 Subgroup Equity

Subgroup calibration was assessed by comparing model-predicted against observed DTP3 coverage across zones, wealth quintiles, urban/rural strata, and maternal education groups (supplementary Tables S1–S5).

**By geopolitical zone:** Calibration error varied from 0.028 in North West (best; not flagged) to 0.084 in South East (worst; flagged), with North Central (0.074), South West (0.075), North East (0.055), and South South (0.046) all flagged. The model generalised best to higher-burden northern zones where training-data density was greatest.

**By wealth quintile:** All five strata were flagged. The richest quintile (Q5) was best calibrated (absolute error = 0.040) and Q2 (second-poorest) was worst (absolute error = 0.067). The RL-optimised scenario (S4) narrowed the absolute wealth-quintile gap in DTP3 completion from 0.0805 (S0) to 0.0722 — an absolute reduction of approximately 0.008, equivalent to a ~10% relative reduction. Risk-targeted (S3) and bandit-allocated (S5) strategies achieved greater absolute equity gains (wealth gaps of 0.0672 and 0.0669, respectively), though the RL policy's advantage lies in state-adaptive sequencing. The concentration index narrowed from 0.0190 (S0) to 0.0155 under S2, S3, and S5.

**By urban/rural residence:** Rural children were better calibrated (absolute error = 0.047) than urban children (absolute error = 0.067), despite no bivariate urban–rural difference in dropout status.

**By maternal education:** Children of mothers with higher education were best calibrated (absolute error = 0.029; not flagged) and children of mothers with primary education were worst (absolute error = 0.068; flagged), likely reflecting the secondary-education majority in training data (45.4% of cohort).

---

### 3.6 Interactive Web Dashboard

We have presented a dashboard including advanced data visualisation tools to facilitate a more detailed exploration of trends, patterns, and relationships within the dropout cascade and the RL-optimised intervention allocation. This innovative tool is accessible at https://olatechie.github.io/dropout/ (see Figure 5). The application features a Story module that narrates the DTP cascade cinematically, a Policy module showing choropleth allocation of recommended interventions by state and zone, a Simulation module for user-controlled scenario exploration with on-the-fly cost-effectiveness comparison, and an Explorer module for interactive subgroup and covariate filtering. The Story module includes annotated maps and temporal animations tracing the cascade from DTP1 initiation to DTP3 completion or dropout. A text transcript at /story/transcript provides a full text alternative for readers who prefer non-interactive access, in compliance with WCAG 2.1 Level AA standards.

---

### 3.7 Summary

Taken together, these results establish three headline findings. First, cascade-specific XGBoost prediction models discriminated well at both dropout transitions (T1: AUROC 0.910; T2: AUROC 0.943), with isotonic recalibration substantially correcting the T2 model's pre-recalibration over-dispersion (slope 1.596 → 0.969). Second, the RL-optimised scenario increased simulated DTP3 coverage by 1.07 percentage points over the status quo, but at a higher ICER (₦699/pp) than the risk-targeted strategy (₦301/pp) at the reference willingness-to-pay threshold, where S3 dominated with a 56.7% cost-effectiveness probability versus 0% for S4. Third, the RL-optimised policy narrowed the absolute wealth-quintile gap in DTP3 completion by approximately 10%, demonstrating that data-driven allocation can advance equity alongside coverage goals. The implications of these findings for NPHCDA programme design and the Immunisation Agenda 2030 are discussed in Section 4.
