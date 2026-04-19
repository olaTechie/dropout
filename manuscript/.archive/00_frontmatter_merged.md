# Frontmatter (Merged Opus + Sonnet)

## Title

Optimising the timing and targeting of interventions to reduce DTP vaccination dropout using offline reinforcement learning: a four-stage analytical framework applied to the Nigeria DHS 2024

## Authors

Uthman OA et al.

*Affiliations to be completed*

---

## Abstract

### Background

Nigeria accounts for the largest absolute burden of under-vaccinated children globally, with persistent dropout between DTP1 and DTP3 remaining a critical barrier to full immunisation coverage despite improving trends. Conventional dropout interventions — SMS reminders, community health worker visits, defaulter tracing — are deployed uniformly without considering optimal sequencing or personalisation across the vaccination schedule. No study has applied reinforcement learning to vaccination dropout. We applied a four-stage analytical framework to identify which children to target, with which intervention, and at which dose transition, using nationally representative survey data.

### Methods and Findings

We analysed 3,194 children aged 12–23 months who had received DTP1 in the Nigeria Demographic and Health Survey 2024. The overall DTP1-to-DTP3 dropout rate was 14.8%, with geographic heterogeneity ranging from 8.6% (South South) to 19.6% (North Central). Transition-specific XGBoost models, trained with 200-trial Bayesian hyperparameter optimisation and cluster-robust cross-validation, achieved AUC-ROC of 0.910 (95% CI: 0.885–0.932) for DTP1-to-DTP2 dropout and 0.943 (0.929–0.957) for DTP2-to-DTP3 dropout, significantly outperforming logistic regression (DeLong p < 1 × 10⁻⁹). Contrary to the hypothesis that static sociodemographic factors would dominate, SHAP decomposition by Andersen's Behavioural Model revealed that dynamic temporal features — inter-dose intervals, delay accumulation, community dropout rates — accounted for 35.9% and 59.0% of total feature importance at transitions 1 and 2, respectively. A conservative Q-learning offline reinforcement learning policy (α = 5.0) achieved 6.1–6.7% improvement over the observed behaviour policy. In microsimulation (10,000 children, 1,000 bootstrap iterations), risk-targeted allocation was the most cost-effective non-dominant strategy (DTP3: 88.2%, ICER: ₦8,007 per additional completion), capturing 92% of the gain from universal community health worker deployment at 35% of the cost. The reinforcement learning-optimised policy achieved equivalent DTP3 completion (88.2%) at 2.6 times the cost (₦903 vs ₦341 per child). All scenarios reduced the poorest-to-richest equity gap from 7.8 to 6.6–7.3 percentage points.

### Conclusions

Dynamic vaccination trajectory features — not static demographics — are the strongest predictors of dropout at both dose transitions, supporting trajectory-responsive intervention design. Risk-targeted allocation guided by machine-learning risk scores is the most cost-effective strategy for Nigeria. Offline reinforcement learning provides a novel framework for sequential intervention optimisation in immunisation, though it did not outperform static targeting over a two-transition horizon. Applications to longer vaccine schedules with prospective intervention data may better demonstrate the sequential advantage of reinforcement learning.

---

## Introduction

Vaccination dropout, defined as the failure to complete a multi-dose vaccine series after initiating it, represents a distinct programmatic challenge from both zero-dose children who never access immunisation services and missed opportunities for vaccination where children attend health facilities but are not vaccinated [1,2]. Children who receive DTP1 but do not complete the three-dose series have successfully entered the immunisation cascade, indicating that the health system engaged them at least once, yet failed to retain them through the schedule [3]. Globally, the DTP1-to-DTP3 dropout rate serves as a key performance indicator for immunisation programmes, with the World Health Organization defining it as the proportional difference between first and third dose coverage [4]. In sub-Saharan Africa, the weighted pentavalent dropout rate is approximately 20.9%, with Western Africa bearing the highest burden at 46.0% [5].

In Nigeria, DTP series dropout has declined from 46% in 2003 to approximately 28% in 2018, yet remains a substantial barrier to achieving full immunisation coverage [6]. National DTP3 coverage was estimated at 53.5% in the 2024 Nigeria Demographic and Health Survey, with marked geographical disparities: the North-West and North-East geopolitical zones consistently exhibit the lowest coverage and highest dropout rates [7]. Prior analyses of dropout determinants using Demographic and Health Survey data have identified maternal education, household wealth, antenatal care attendance, place of delivery, and urban-rural residence as consistent predictors, typically framed within Andersen's Behavioural Model of Health Services Use [1,5,8]. However, these analyses treat dropout as a single binary outcome, ignoring the sequential nature of the vaccination schedule and the possibility that distinct predictor profiles operate at different cascade transitions.

Current interventions to reduce dropout, including SMS reminders, community health worker home visits, facility-based defaulter tracing, and conditional incentives, have demonstrated effectiveness in randomised trials, with effect sizes ranging from 5–15% for SMS reminders to 15–25% for community health worker visits [9,10,11]. However, these interventions are typically deployed uniformly across the vaccination schedule without considering the optimal sequencing, timing, or targeting of different intervention types at different dose steps for different children. A caregiver whose child missed DTP2 at 10 weeks may require a different intervention from one whose child received DTP1 and DTP2 on time but fails to return for DTP3. This sequential decision problem, where the optimal action depends on the child's evolving state within the immunisation cascade, is naturally suited to reinforcement learning [12,13]. Offline reinforcement learning methods, which learn optimal policies from fixed observational datasets without requiring real-time experimentation, have been successfully applied to clinical decision-making in sepsis management and mechanical ventilation [14,15,16], but have not been applied to vaccination dropout.

This study aimed to (1) construct transition-specific prediction models for DTP dropout using XGBoost with Andersen-stratified SHAP decomposition to identify distinct predictor profiles at each cascade transition; (2) formulate the immunisation schedule as a Markov decision process and learn optimal sequential intervention policies using offline reinforcement learning; (3) develop a contextual multi-armed bandit for budget-constrained community-level intervention allocation; and (4) validate the reinforcement learning-derived policy through microsimulation comparing it against standard static intervention approaches.

---

## Introduction References

1. Uthman OA, Sambala EZ, et al. PLOS ONE. 2024;19(2):e0297326.
2. Sridhar S, Maleq N, Guillermet E, et al. Vaccine. 2014;32(51):6870-6879.
3. Adedokun ST, et al. Vaccines. 2023;11(1):167.
4. WHO/UNICEF. Immunisation Agenda 2030. Geneva: WHO; 2020.
5. Tessema ZT, et al. BMC Public Health. 2024;24:456.
6. Adedokun ST, et al. Vaccines. 2023;11(1):167.
7. Adeyinka DA, et al. Vaccines. 2025;13(11):1135.
8. Andersen RM. J Health Soc Behav. 1995;36(1):1-10.
9. Eze P, et al. Hum Vaccin Immunother. 2021;17(2):507-515.
10. Brugha RF, Kevany JP. Bull World Health Organ. 1996;74(5):517-524.
11. Banerjee AV, Duflo E, et al. BMJ. 2010;340:c2220.
12. Ernst D, Geurts P, Wehenkel L. J Mach Learn Res. 2005;6:503-556.
13. Kumar A, Zhou A, Tucker G, Levine S. NeurIPS. 2020;33:1179-1191.
14. Komorowski M, Celi LA, et al. Nat Med. 2018;24(11):1716-1720.
15. Raghu A, Komorowski M, et al. arXiv:1711.09602. 2017.
16. Raghu A, Komorowski M, Singh S. arXiv:1811.09602. 2018.
