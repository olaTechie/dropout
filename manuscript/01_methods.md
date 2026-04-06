# Methods

This study is reported following the Transparent Reporting of a multivariable prediction model for Individual Prognosis or Diagnosis — Artificial Intelligence (TRIPOD+AI) guideline [17], with extensions for the reinforcement learning and microsimulation components.

## Study design and data source

We conducted a secondary analysis of the Nigeria Demographic and Health Survey 2024 (NDHS 2024), a nationally representative cross-sectional household survey conducted by the National Population Commission with technical support from ICF International [18]. The NDHS used a stratified two-stage cluster sampling design, with enumeration areas as primary sampling units and households as secondary units. Interview and examination data were collected using standardised questionnaires. We used the Children's Recode (KR) file, which contains vaccination history and health information for children born in the five years preceding the survey, linked to maternal and household characteristics from the Individual Recode (IR) and Household Recode (HR) files. Geospatial covariates were obtained from the DHS Geospatial Covariate dataset (NGGC8AFL.csv), providing cluster-level environmental and infrastructure variables [19].

## Study population

The analytic sample comprised children aged 12-23 months at the time of the survey (age in months calculated as v008 − b3, where v008 is the date of interview in century month code and b3 is the child's date of birth), who were alive at the time of the survey (b5 = 1), restricted to the youngest child per woman to avoid within-mother correlation. Critically, the sample was further restricted to children who had received at least one dose of DTP vaccine (h3 ∈ {1, 2, 3}, where 1 = vaccination date on card, 2 = reported by mother, 3 = marked on card without date). This restriction defines the study as a retention analysis of cascade entrants rather than an access analysis: zero-dose children who never received DTP1 were excluded.

## Outcome definitions

The primary outcome was DTP vaccination dropout, defined as receipt of DTP1 but failure to receive DTP3: vac_dropout = ((vac_dpt1 = 1) | (vac_dpt2 = 1)) & (vac_dpt3 = 0). The WHO dropout rate was calculated as (DTP1 coverage − DTP3 coverage) / DTP1 coverage × 100 [4]. Two transition-specific outcomes were defined for the cascade analysis: transition 1 (T1) dropout, representing failure to progress from DTP1 to DTP2 ((h3 ∈ {1, 3}) & (h5 = 0)); and transition 2 (T2) dropout, representing failure to progress from DTP2 to DTP3 among DTP2 recipients ((h5 ∈ {1, 3}) & (h7 = 0)).

## Predictor variables

Predictor variables were organised according to Andersen's Behavioural Model of Health Services Use [20], which categorises determinants of health service utilisation into predisposing factors, enabling factors, and need factors. We extended this framework with a fourth domain of dynamic temporal features unique to the sequential decision formulation.

### Predisposing factors

Predisposing variables included demographic characteristics (maternal age [v012], child sex [b4, coded as male = 1], birth order [bord], parity [v201]), social structural variables (maternal education [v106, coded as none/primary/secondary+], partner's education [v701], polygynous union [v505 > 0], ethnicity [v131]), and health belief proxies (decision-making autonomy [v743a], permission barrier to healthcare [v467b], media access [television v159, radio v158, newspaper v157, any media composite], COVID-19 vaccine willingness [s1112s] and receipt [s1112p] as trust proxies). In total, 16 predisposing features were included.

### Enabling factors

Enabling variables comprised personal and family resources (wealth quintile [v190], wealth factor score [v191], current employment [v714], health insurance coverage [v481], household size [v136], female household head [v151 = 2], number of under-five children [v137]) and community-level resources (urban-rural residence [v025], geopolitical zone [szone, not v024], travel time to nearest health facility [v483a, in minutes, not v467d]). Community composite variables were constructed by aggregating individual-level data to the cluster level: community poverty rate, community illiteracy rate, community unemployment rate, community media access, ethnic diversity (Herfindahl index), and community socioeconomic status score (principal components analysis composite) [1]. Geospatial covariates from the DHS Geospatial Covariate dataset included population density (UN Population Density 2020), travel time to nearest city, nightlight intensity composite, malaria prevalence (Plasmodium falciparum rate 2020), and insecticide-treated net coverage (2020) [19]. In total, 20 enabling features were included.

### Need factors

Need variables comprised perceived need indicators reflecting the caregiver's engagement with the health system (health card possession [h1a], number of antenatal care visits [m14, coded as none/1-3/4+], facility delivery [m15, coded as facility if delivery code 21-46], child vitamin A supplementation [h34], postnatal care for the child post-discharge [m70] and pre-discharge [m74], fieldworker visit in preceding 12 months [v393]) and evaluated need indicators reflecting health system assessment (vaccination venue [h69, coded as public/private/NGO/campaign], contact count [sum of six binary contact indicators, range 0-6], recent diarrhoea [h11], recent fever [h22]). In total, 11 need features were included.

### Dynamic temporal features

Eight dynamic features captured the child's evolving state within the immunisation cascade: child age in weeks at the current dose step, number of DTP doses received (0-2), dose step indicator (transition 1 or 2), whether the previous dose was received on schedule, inter-dose interval in days (computed from vaccination card dates: h3d/h3m/h3y for DTP1, h5d/h5m/h5y for DTP2, h7d/h7m/h7y for DTP3), cumulative delay accumulation in days behind schedule, cluster-level dropout rate, and cluster-level DTP3 coverage. Inter-dose intervals were computed only for children with card-confirmed vaccination dates (h3 = 1 for DTP1, h5 = 1 for DTP2, h7 = 1 for DTP3). Date values of 97 (inconsistent) or 98 (don't know) were treated as missing. Timeliness was defined as DTP1 receipt by 56 days (8 weeks), DTP2 by 84 days (12 weeks), and DTP3 by 112 days (16 weeks) from birth, consistent with the Nigeria Expanded Programme on Immunization schedule [21].

## Analytical framework

The study employed a four-stage analytical framework (Figure 1).

### Stage 1: Transition-specific prediction models

Three separate XGBoost gradient-boosted tree classifiers [22] were trained to predict dropout at each cascade transition: Model T1 predicted DTP1-to-DTP2 dropout among all DTP1 recipients (n = 3,194); Model T2 predicted DTP2-to-DTP3 dropout among DTP2 recipients (n = 3,023); and Model Full predicted overall dropout (DTP1 received, DTP3 not received) among all DTP1 recipients (n = 3,194). All 55 predictor features (16 predisposing, 20 enabling, 11 need, 8 dynamic) were included in each model.

#### Hyperparameter optimisation

Hyperparameters were tuned using Optuna [23] with 200 trials per model, optimising AUC-ROC under five-fold cross-validation. The search space comprised: maximum tree depth (3-10), learning rate (0.01-0.30), number of estimators (100-1,000), minimum child weight (1-10), subsample ratio (0.6-1.0), column sample by tree (0.6-1.0), gamma regularisation (0-5), L1 regularisation alpha (1e-8 to 1.0, log-uniform), and L2 regularisation lambda (1e-8 to 1.0, log-uniform). Class imbalance was addressed using scale_pos_weight. The optimal hyperparameters for Model T1 were: max_depth = 8, learning_rate = 0.011, n_estimators = 427, min_child_weight = 2, subsample = 0.83, colsample_bytree = 0.76, gamma = 2.77, scale_pos_weight = 4.90. For Model T2: max_depth = 4, learning_rate = 0.015, n_estimators = 167, min_child_weight = 1, subsample = 0.74, colsample_bytree = 0.63, gamma = 0.28, scale_pos_weight = 1.39.

#### Model validation

Model discrimination was assessed using the area under the receiver operating characteristic curve (AUC-ROC) and area under the precision-recall curve (AUC-PR), with 95% confidence intervals estimated using 1,000 bootstrap resamples [24]. The DeLong test [25] was used to compare XGBoost discrimination against a logistic regression baseline. Model calibration was assessed using calibration curves (locally estimated scatterplot smoothing), calibration slope and intercept (ideal: slope = 1.0, intercept = 0.0), and Brier score with Spiegelhalter decomposition into reliability, resolution, and uncertainty components [26]. Isotonic regression recalibration was applied post-hoc to correct miscalibrated predictions [27]. Five-fold cross-validation used cluster-robust folds, holding out entire primary sampling units (v021) to prevent information leakage between training and validation sets within the same community.

#### SHAP explainability and Andersen domain decomposition

SHapley Additive exPlanations (SHAP) values were computed for all test observations using TreeExplainer [28]. For each child, the sum of absolute SHAP values was computed separately for each Andersen domain (predisposing, enabling, need, dynamic) using the domain mapping. The dominant domain for each child was assigned as the domain with the largest total SHAP contribution. This Andersen-stratified SHAP decomposition tested the hypothesis that T1 dropout (early exit) is dominated by predisposing factors (health beliefs, trust, education) while T2 dropout (late exit) is dominated by enabling factors (access, distance, cost) and need factors (competing health needs) [1,5].

### Stage 2: Offline reinforcement learning

#### Markov decision process formulation

The DTP immunisation schedule was formulated as a Markov decision process (MDP) with the following components. The state space S comprised the 55-dimensional state vector described above (47 static Andersen features plus 8 dynamic temporal features). The action space A comprised five discrete actions: a₀ = no intervention (cost ₦0), a₁ = SMS reminder (₦50), a₂ = community health worker home visit (₦500), a₃ = facility recall with defaulter tracing (₦1,500), and a₄ = conditional incentive (₦800). Action costs were informed by published estimates from Nigeria and comparable sub-Saharan African settings [9,10,11,29]. The transition function P(s'|s, a) was learned from the observed trajectory dataset. The reward function was defined as R(s, a, s') = +1.0 if DTP3 was completed (terminal reward) + 0.3 if the next dose was received (intermediate reward) − λ × cost(a), where λ = 0.001 was the cost penalty weight. The discount factor was γ = 0.95. The decision horizon comprised two transitions (DTP1→DTP2 and DTP2→DTP3).

#### Trajectory reconstruction and behaviour policy inference

Vaccination trajectories were reconstructed from the DHS data to create a dataset of (state, action, reward, next state) tuples. Since the DHS does not record which interventions were deployed to each child, a proxy behaviour policy was inferred from observed patterns: children who received their next dose on time (within 42 days of the previous dose) with evidence of a fieldworker visit (v393 = 1) were assigned action a₂ (CHW); those on time with vaccination at a campaign site (h69 = 41) were assigned a₃ (recall); those on time with a health card present (h1a ≥ 1) were assigned a₁ (SMS); those who received their next dose late (>42 days) were assigned a₀ (no effective intervention); and those who did not receive their next dose were assigned a₀. This yielded 6,217 trajectory rows from 3,138 children across up to two dose steps, with an inferred action distribution of 70.6% SMS, 20.9% no intervention, 8.3% CHW, 0.2% facility recall, and 0.0% incentive.

#### Fitted Q-iteration

Fitted Q-iteration (FQI) [30] was implemented as a batch reinforcement learning algorithm using ExtraTrees (200 trees, max_depth = 10) as the function approximator. The algorithm iteratively updated Q-value estimates by fitting the function approximator to Bellman backup targets: y = r + γ × max_{a'} Q̂_{k-1}(s', a'). Convergence was defined as ΔQ < 0.01 between successive iterations, with a maximum of 200 iterations. FQI converged at iteration 2, reflecting the capacity of tree-based approximators to perfectly fit Q-targets with sufficient depth.

#### Conservative Q-learning

Conservative Q-learning (CQL) [31] was implemented to address the distributional shift problem inherent in offline reinforcement learning, where the learned policy may recommend actions that were rarely or never observed in the training data. CQL adds a penalty term to the standard Bellman loss that minimises Q-values for out-of-distribution actions: L_CQL = L_Bellman + α × (E_π[Q(s,a)] − E_data[Q(s,a)]), where α controls the conservatism penalty. CQL was trained for 80 iterations using a neural network with two hidden layers of 256 units each. Three values of α were tested (1.0, 2.0, 5.0); α = 5.0 was selected as the most conservative setting, though no value achieved the target of <15% out-of-distribution action frequency due to the fundamental sparsity of actions a₃ and a₄ in the observational data.

#### Off-policy evaluation

Since the learned policy could not be deployed in real time, it was evaluated using two off-policy evaluation methods [32]. Weighted importance sampling (WIS) re-weighted observed trajectories by the ratio of the learned policy probability to the behaviour policy probability, with a clipping threshold ε = 0.1 to limit variance. Fitted Q-evaluation (FQE) learned a separate Q-function under the target policy using the same trajectory data. The doubly robust estimator was also computed but results from WIS and FQE are reported as primary. Out-of-distribution action frequency was tracked as the proportion of policy recommendations for actions observed in fewer than 1% of training trajectories. Validation used 1,569 episodes.

### Stage 3: Multi-armed bandit and microsimulation

#### Contextual multi-armed bandit

A contextual linear upper confidence bound (LinUCB) bandit [33] was implemented for community-level intervention allocation under budget constraints. The context vector comprised 19 LGA-level features aggregated from child-level data (mean dropout rate, mean wealth, urbanisation rate, facility access, and geospatial covariates). The five intervention actions served as arms. The expected reward for each arm in each community was estimated as the predicted improvement in DTP3 completion derived from the Q-function. The exploration parameter was α = 1.0. The national budget constraint was ₦500 million, with costs scaled by an estimated 3,000 children per LGA (1,140 LGAs nationally), such that universal CHW deployment (₦500 × 3,000 × 1,140 = ₦1.71 billion) exceeded the budget. Budget sensitivity analyses tested ₦250 million and ₦1 billion.

#### Microsimulation

A synthetic population of 10,000 children was generated to mirror the NDHS 2024 DTP1-received sample distribution. For each child, baseline transition probabilities (P(DTP2|DTP1) and P(DTP3|DTP2)) were estimated from the recalibrated XGBoost models T1 and T2. Six intervention scenarios were simulated:

- **S0 (Status quo):** the observed behaviour policy was applied
- **S1 (Uniform SMS):** action a₁ at every dose step for all children
- **S2 (Uniform CHW):** action a₂ at every dose step for all children
- **S3 (Risk-targeted):** children in the top 30% of predicted dropout risk received a₂ (CHW); the remainder received a₁ (SMS)
- **S4 (RL-optimised):** the CQL-learned policy π* assigned actions based on each child's state vector
- **S5 (Bandit-allocated):** the LinUCB community-level allocation was applied to all children in each community

Intervention effects were applied as relative risk reductions on the transition-specific dropout probability, using central estimates from the literature-informed action space calibration [9,10,11,29]: a₁ = 10% relative reduction, a₂ = 20%, a₃ = 25%, a₄ = 14%. This approach ensured that children with low baseline dropout probability received proportionally smaller absolute benefit, avoiding ceiling effects. Each scenario was replicated 1,000 times using bootstrap resampling to generate 95% confidence intervals.

#### Cost-effectiveness and equity analysis

The incremental cost-effectiveness ratio (ICER) was computed as the difference in total programme cost divided by the difference in DTP3 completions relative to S0 (status quo). A scenario was considered dominant if it achieved higher DTP3 completion at lower cost than S0. Equity was assessed as the absolute difference in DTP3 completion rate between the poorest and richest wealth quintiles. The a priori equity constraint required that no intervention scenario widen this gap relative to the status quo.

## Survey design and statistical analysis

All analyses incorporated the complex survey design of the NDHS 2024 using sampling weights (v005/1,000,000), stratification (v022), and primary sampling unit clustering (v021) [18]. Descriptive statistics were reported as weighted proportions with 95% confidence intervals. Group comparisons in the descriptive table used chi-squared tests for categorical variables, Welch's t-test for continuous variables, and Kruskal-Wallis tests for non-normally distributed continuous variables. Spatial autocorrelation of state-level dropout prevalence was assessed using Global Moran's I with queen contiguity weights and local indicators of spatial association (LISA) [34].

## Software

All analyses were conducted in Python 3.11 using XGBoost 2.0 [22], Optuna 3.5 [23], SHAP 0.44 [28], scikit-learn 1.4, NumPy 1.26, pandas 2.1, geopandas 0.14, matplotlib 3.8, Plotly 5.18, PySAL 24.1 [34], tableone 0.9, ydata-profiling 4.6, and Streamlit 1.31. The complete analytical pipeline, including all code, agent definitions, and intermediate outputs, is available on GitHub [PLEASE VERIFY: repository URL to be added upon submission].

---

## Methods References

17. Collins GS, Moons KGM, Dhiman P, et al. TRIPOD+AI statement: updated guidance for reporting clinical prediction models that use regression or machine learning methods. BMJ. 2024;385:e078378.
18. National Population Commission (NPC) Nigeria and ICF. Nigeria Demographic and Health Survey 2024. Abuja/Rockville: NPC/ICF; 2025.
19. ICF. The DHS Program Geospatial Covariates Dataset. Rockville: ICF; 2023.
20. Andersen RM. Revisiting the behavioral model and access to medical care: does it matter? J Health Soc Behav. 1995;36(1):1-10.
21. National Primary Health Care Development Agency (NPHCDA). National Strategic Immunisation Plan and Schedule of Services 2018-2028. Abuja: NPHCDA; 2018.
22. Chen T, Guestrin C. XGBoost: a scalable tree boosting system. In: Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining. 2016:785-794.
23. Akiba T, Sano S, Yanase T, et al. Optuna: a next-generation hyperparameter optimization framework. In: Proceedings of the 25th ACM SIGKDD International Conference on Knowledge Discovery and Data Mining. 2019:2623-2631.
24. Efron B, Tibshirani RJ. An Introduction to the Bootstrap. New York: Chapman and Hall/CRC; 1993.
25. DeLong ER, DeLong DM, Clarke-Pearce DL. Comparing the areas under two or more correlated receiver operating characteristic curves: a nonparametric approach. Biometrics. 1988;44(3):837-845.
26. Spiegelhalter DJ. Probabilistic prediction in patient management and clinical trials. Stat Med. 1986;5(5):421-433.
27. Niculescu-Mizil A, Caruana R. Predicting good probabilities with supervised learning. In: Proceedings of the 22nd International Conference on Machine Learning. 2005:625-632.
28. Lundberg SM, Lee SI. A unified approach to interpreting model predictions. In: Advances in Neural Information Processing Systems. 2017;30:4765-4774.
29. Banerjee AV, Duflo E, Glennerster R, et al. Improving immunisation coverage in rural India: clustered randomised controlled evaluation of immunisation campaigns with and without incentives. BMJ. 2010;340:c2220.
30. Ernst D, Geurts P, Wehenkel L. Tree-based batch mode reinforcement learning. J Mach Learn Res. 2005;6:503-556.
31. Kumar A, Zhou A, Tucker G, Levine S. Conservative Q-learning for offline reinforcement learning. In: Advances in Neural Information Processing Systems. 2020;33:1179-1191.
32. Raghu A, Komorowski M, Singh S. Model selection for offline reinforcement learning: practical considerations for healthcare settings. In: Machine Learning for Healthcare Conference. 2022.
33. Li L, Chu W, Langford J, Schapire RE. A contextual-bandit approach to personalized news article recommendation. In: Proceedings of the 19th International Conference on World Wide Web. 2010:661-670.
34. Anselin L. Local indicators of spatial association — LISA. Geogr Anal. 1995;27(2):93-115.
