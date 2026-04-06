# Results

## Study population and immunisation cascade

Of 4,898 children aged 12-23 months in the NDHS 2024, 3,194 (65.2%) had received at least one dose of DTP vaccine and formed the analytic sample. The survey-weighted overall DTP1-to-DTP3 dropout rate was 14.8%. Transition-specific dropout was 4.0% at DTP1-to-DTP2 (T1; approximately 128 children) and 3.9% at DTP2-to-DTP3 (T2; approximately 119 children among 3,023 DTP2 recipients).

The immunisation cascade showed substantial geographical heterogeneity across the six geopolitical zones (Figure 2, Table S1). The North Central zone had the highest WHO dropout rate (19.6%; DTP2 retention 92.5%, DTP3 retention 80.4%), followed by the North East (16.8%) and South East (14.1%). The South South zone had the lowest dropout rate (8.6%; DTP2 retention 96.8%, DTP3 retention 91.4%). DTP2 retention exceeded 92% in all zones, indicating that the majority of dropout occurred at the DTP2-to-DTP3 transition.

## Descriptive characteristics

Table 1 presents the baseline characteristics of the study population stratified by dropout status. Children who dropped out were more likely to reside in rural areas, belong to poorer wealth quintiles, and have mothers with no formal education compared with children who completed the DTP series. The North Central and North East zones contributed disproportionately to the dropout group. Among dynamic temporal features, children who dropped out had longer inter-dose intervals, greater delay accumulation, and resided in communities with higher cluster-level dropout rates, suggesting that temporal cascade dynamics are strongly associated with eventual dropout.

## Spatial analysis

The choropleth map of state-level dropout prevalence (Figure 3A) showed widespread geographical variation without a clear north-south gradient. The funnel plot (Figure 4) identified several states with dropout rates falling outside the 95% control limits, indicating statistically unusual prevalence beyond sampling variation. Global Moran's I for state-level dropout prevalence was not statistically significant, suggesting an absence of strong spatial clustering at the state level. The LISA analysis (Figure 3B) identified isolated spatial outliers but no Hot-Hot or Cold-Cold clusters. This absence of spatial clustering distinguishes dropout from raw DTP3 coverage, which clusters strongly in the northern zones, and suggests that dropout is a geographically diffuse phenomenon occurring wherever children enter the immunisation cascade.

## Transition-specific prediction models

### Model discrimination

XGBoost models achieved high discriminative performance at both cascade transitions (Table 2, Figure 6A-B). Model T1 (DTP1→DTP2 dropout) achieved an AUC-ROC of 0.910 (95% CI: 0.885-0.932) and AUC-PR of 0.299 (95% CI: 0.230-0.387). Model T2 (DTP2→DTP3 dropout) achieved a higher AUC-ROC of 0.943 (95% CI: 0.929-0.957) and AUC-PR of 0.548 (95% CI: 0.454-0.640). Both models significantly outperformed logistic regression baselines (DeLong test p < 1 × 10⁻⁹ for both). The lower AUC-PR values relative to AUC-ROC reflect the class imbalance in both outcomes (4.0% and 3.9% event rates respectively), with AUC-PR providing a more informative assessment of predictive performance on the minority class. Five-fold cluster-robust cross-validation showed stable discrimination across folds (T1 range: 0.885-0.935; T2 range: 0.924-0.969).

### Model calibration

After isotonic regression recalibration, both models showed near-ideal calibration (Figure 6C-D). For Model T1, the calibration slope improved from 0.874 to 0.959 and the intercept from -0.661 to -0.065, with Brier score improving from 0.036 to 0.032. For Model T2, the calibration slope improved from 1.596 to 0.969 and the intercept from 0.724 to -0.104, with Brier score improving from 0.027 to 0.026. The original T2 model was substantially overconfident (slope 1.596), and recalibration was essential before using predicted probabilities in downstream reinforcement learning analyses.

### Andersen domain SHAP decomposition

The Andersen-stratified SHAP decomposition revealed that dynamic temporal features dominated prediction at all three cascade transitions (Table 3, Figure 5). For Model T1, the dynamic domain contributed 35.9% of total SHAP importance (mean |SHAP| = 1.63), followed by need (27.1%, 1.24), enabling (19.7%, 0.90), and predisposing (17.3%, 0.79). For Model T2, dynamic dominance was even more pronounced at 59.0% (mean |SHAP| = 1.24), with need (19.7%, 0.41), enabling (11.2%, 0.23), and predisposing (10.1%, 0.21) contributing substantially less. For Model Full, dynamic features accounted for 52.1% (mean |SHAP| = 2.74).

This finding did not support the original hypothesis that T1 dropout would be dominated by predisposing factors (health beliefs, trust) and T2 dropout by enabling and need factors (access, cost, competing morbidity). Instead, temporal cascade features, particularly community-level dropout rates, cluster-level DTP3 coverage, inter-dose interval length, and delay accumulation, were the strongest predictors of dropout at both transitions. The top individual features within the dynamic domain included community dropout rate and cluster DTP3 coverage, which capture contextual peer effects, and inter-dose interval and delay accumulation, which capture the child's individual trajectory quality within the cascade.

## Offline reinforcement learning

### Behaviour policy and CQL-learned policy

The inferred behaviour policy from the DHS data was heavily concentrated on SMS reminders (70.6%) and no intervention (20.9%), with minimal use of CHW visits (8.3%), facility recall (0.2%), and no observed use of conditional incentives (0.0%). The CQL-learned policy (α = 5.0) shifted substantially from this distribution (Figure 7A), recommending CHW visits for 29.4% of state-action pairs, conditional incentives for 22.9%, no intervention for 20.0%, SMS for 17.3%, and facility recall for 10.4%. This shift reflects the CQL policy's assessment that more intensive interventions, particularly CHW visits and incentives, carry higher expected long-term value for DTP3 completion despite their greater cost.

### Off-policy evaluation

Both off-policy evaluation methods indicated that the CQL-learned policy outperformed the observed behaviour policy (Table 4). Weighted importance sampling estimated a policy improvement of 6.1%, and fitted Q-evaluation estimated 6.7%. The concordance between the two methods, which rely on different assumptions, strengthens confidence in the improvement estimate. However, 33.3% of CQL policy recommendations were for actions observed in fewer than 1% of training trajectories (primarily a₃ and a₄), indicating substantial extrapolation beyond the observational data. This out-of-distribution action frequency remained high despite the conservative penalty (α = 5.0), reflecting the fundamental limitation that facility recall and incentive interventions were essentially unobserved in the DHS data.

## Multi-armed bandit allocation

The LinUCB contextual bandit, operating across 1,140 communities with 19-dimensional context vectors, converged predominantly to SMS allocation (99.6% of communities), with only isolated communities receiving CHW, facility recall, or incentive allocations (S9 Figure). This convergence reflects the dominance of SMS in community-level cost-effectiveness: at ₦50 per child versus ₦500-₦1,500 for alternative interventions, SMS provides the highest expected return per unit cost when applied uniformly within communities. Budget sensitivity analysis showed identical allocation patterns across ₦250 million, ₦500 million, and ₦1 billion national budgets, as the SMS-dominated allocation cost only ₦184,550 nationally, well below all budget thresholds. The budget constraint became binding only when mandating CHW-level interventions, which would cost approximately ₦1.71 billion nationally.

## Microsimulation validation

### DTP3 completion rates

All five intervention scenarios improved DTP3 completion relative to the status quo (Table 5, Figure 8). The status quo (S0) achieved 85.9% DTP3 completion (95% CI: 85.2-86.6%). Uniform SMS (S1) and bandit-allocated (S5) interventions achieved 87.1% (86.4-87.7%), representing a 1.3 percentage point improvement. Uniform CHW (S2) achieved the highest completion at 88.4% (87.8-89.0%), a 2.5 percentage point improvement. Risk-targeted intervention (S3) and the RL-optimised policy (S4) both achieved 88.2% (87.6-88.8%), a 2.3 percentage point improvement.

### Cost-effectiveness

Two scenarios were dominant, achieving better outcomes at lower cost than the status quo: uniform SMS (S1; ICER = -₦4,591, cost per child ₦98 vs ₦155) and bandit-allocated (S5; ICER = -₦4,619, cost per child ₦98). Among non-dominant scenarios, risk-targeted intervention (S3) was the most cost-effective at ₦8,007 per additional DTP3 completion (cost per child ₦341). The RL-optimised policy (S4) had an ICER of ₦32,434 per additional DTP3 completion (cost per child ₦903), comparable to uniform CHW (S2; ICER = ₦32,742, cost per child ₦979). The RL policy achieved equivalent DTP3 improvement to risk-targeted intervention (+2.3 percentage points) but at 2.6 times the cost (₦903 vs ₦341), driven by the CQL policy's preference for higher-cost interventions (CHW 29.4%, incentive 22.9%).

### Equity analysis

All intervention scenarios reduced the equity gap between the poorest and richest wealth quintiles relative to the status quo (Table 5). The status quo equity gap was 7.8 percentage points (poorest 84.2%, richest 92.0%). The largest equity improvement was achieved by uniform CHW (S2; gap 6.6 pp) and risk-targeted (S3; gap 6.7 pp). The RL-optimised policy (S4; gap 6.8 pp) and uniform SMS (S1; gap 7.2 pp) also narrowed the gap. The a priori equity constraint, requiring that no intervention widen the poorest-richest gap, was satisfied by all scenarios.

### RL-optimised versus static policies

The RL-optimised policy (S4) achieved DTP3 completion equivalent to risk-targeted intervention (S3) and comparable to uniform CHW (S2), but did not clearly outperform these simpler static policies. This result reflects several factors: the conservative Q-learning penalty (α = 5.0) assigned 20% of children to no intervention to avoid recommending poorly-evidenced actions; the two-transition decision horizon (DTP1→DTP2→DTP3) provided limited scope for sequential advantage; the relative risk reductions across the five actions (10-25%) offered a narrow range for policy differentiation; and the behaviour policy was inferred rather than observed, introducing noise into the training data. The RL framework's primary contribution in this setting is methodological, demonstrating the feasibility of framing vaccination dropout as a sequential decision problem and applying offline reinforcement learning to DHS observational data, rather than achieving performance superiority over well-designed static targeting.
