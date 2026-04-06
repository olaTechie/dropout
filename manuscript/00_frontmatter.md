# Frontmatter

## Suggested Titles

1. **Offline reinforcement learning for optimising sequential interventions to reduce DTP vaccine dropout in Nigeria: a prediction model study using the 2024 Demographic and Health Survey**

2. **Optimising the timing and targeting of interventions across the DTP vaccination schedule using offline reinforcement learning: a four-stage analytical framework applied to the Nigeria DHS 2024**

3. **Dynamic features outweigh static determinants in predicting DTP vaccination dropout: implications from machine learning and offline reinforcement learning using the Nigeria DHS 2024**

4. **From prediction to policy: a reinforcement learning framework for reducing DTP1-to-DTP3 vaccination dropout in Nigeria**

5. **Risk-targeted intervention achieves comparable outcomes to reinforcement learning-optimised policy for reducing DTP vaccination dropout in Nigeria: a microsimulation study**

---

## Authors

Uthman OA et al.

*Affiliations to be completed*

---

## Abstract

**Background**

The DTP1-to-DTP3 dropout rate is a key indicator of immunisation programme performance, reflecting failure to retain children who successfully initiated the vaccination schedule. In Nigeria, approximately 15% of children who receive DTP1 fail to complete the three-dose series, with marked geographical heterogeneity. Current interventions such as SMS reminders, community health worker visits, and defaulter tracing are typically deployed uniformly without considering optimal sequencing or personalisation across the schedule. No study has applied reinforcement learning to vaccination dropout.

**Methods and findings**

We analysed data from 3,194 children aged 12-23 months who received DTP1 in the Nigeria Demographic and Health Survey 2024. We developed a four-stage analytical framework: (1) transition-specific XGBoost prediction models with SHAP explainability organised by Andersen's Behavioural Model; (2) offline reinforcement learning using fitted Q-iteration and conservative Q-learning to learn optimal sequential intervention policies; (3) contextual multi-armed bandit allocation under budget constraints; and (4) microsimulation validation comparing six intervention scenarios. The overall DTP1-to-DTP3 dropout rate was 14.8%, with transition-specific dropout of 4.0% at DTP1-to-DTP2 and 3.9% at DTP2-to-DTP3. XGBoost models achieved AUC-ROC of 0.910 (95% CI: 0.885-0.932) for transition 1 and 0.943 (0.929-0.957) for transition 2. SHAP decomposition by Andersen domains revealed that dynamic temporal features, including inter-dose intervals and community dropout rates, dominated prediction at both transitions (35.9-59.0% of total SHAP importance), challenging the hypothesis that early dropout is driven by predisposing factors and late dropout by enabling factors. The conservative Q-learning policy achieved 6.7% improvement over the observed behaviour policy on fitted Q-evaluation. In microsimulation, risk-targeted intervention (top 30% risk receiving community health worker visits, remainder receiving SMS reminders) was the most cost-effective non-dominant strategy (DTP3 completion: 88.2%; ICER: 8,007 Naira per additional completion), while the reinforcement learning-optimised policy achieved equivalent DTP3 completion (88.2%) at higher cost. All intervention scenarios reduced the equity gap between poorest and richest quintiles.

**Conclusions**

This study demonstrates the first application of offline reinforcement learning to vaccination dropout, framing DTP series completion as a sequential decision problem. While the reinforcement learning policy did not clearly outperform well-designed static targeting in this two-transition setting, the framework provides a methodological foundation for sequential intervention optimisation in immunisation programmes. Risk-targeted deployment of community health worker visits to high-risk children, with SMS reminders for the remainder, offers the most cost-effective strategy for reducing dropout in Nigeria.

---

## Introduction

Vaccination dropout, defined as the failure to complete a multi-dose vaccine series after initiating it, represents a distinct programmatic challenge from both zero-dose children who never access immunisation services and missed opportunities for vaccination where children attend health facilities but are not vaccinated [1,2]. Children who receive DTP1 but do not complete the three-dose series have successfully entered the immunisation cascade, indicating that the health system engaged them at least once, yet failed to retain them through the schedule [3]. Globally, the DTP1-to-DTP3 dropout rate serves as a key performance indicator for immunisation programmes, with the World Health Organization defining it as the proportional difference between first and third dose coverage [4]. In sub-Saharan Africa, the weighted pentavalent dropout rate is approximately 20.9%, with Western Africa bearing the highest burden at 46.0% [5].

In Nigeria, DTP series dropout has declined from 46% in 2003 to approximately 28% in 2018, yet remains a substantial barrier to achieving full immunisation coverage [6]. National DTP3 coverage was estimated at 53.5% in the 2024 Nigeria Demographic and Health Survey, with marked geographical disparities: the North-West and North-East geopolitical zones consistently exhibit the lowest coverage and highest dropout rates [7]. Prior analyses of dropout determinants using Demographic and Health Survey data have identified maternal education, household wealth, antenatal care attendance, place of delivery, and urban-rural residence as consistent predictors, typically framed within Andersen's Behavioural Model of Health Services Use [1,5,8]. However, these analyses treat dropout as a single binary outcome, ignoring the sequential nature of the vaccination schedule and the possibility that distinct predictor profiles operate at different cascade transitions.

Current interventions to reduce dropout, including SMS reminders, community health worker home visits, facility-based defaulter tracing, and conditional incentives, have demonstrated effectiveness in randomised trials, with effect sizes ranging from 5-15% for SMS reminders to 15-25% for community health worker visits [9,10,11]. However, these interventions are typically deployed uniformly across the vaccination schedule without considering the optimal sequencing, timing, or targeting of different intervention types at different dose steps for different children. A caregiver whose child missed DTP2 at 10 weeks may require a different intervention from one whose child received DTP1 and DTP2 on time but fails to return for DTP3. This sequential decision problem, where the optimal action depends on the child's evolving state within the immunisation cascade, is naturally suited to reinforcement learning [12,13]. Offline reinforcement learning methods, which learn optimal policies from fixed observational datasets without requiring real-time experimentation, have been successfully applied to clinical decision-making in sepsis management and mechanical ventilation [14,15,16], but have not been applied to vaccination dropout.

This study aimed to (1) construct transition-specific prediction models for DTP dropout using XGBoost with Andersen-stratified SHAP decomposition to identify distinct predictor profiles at each cascade transition; (2) formulate the immunisation schedule as a Markov decision process and learn optimal sequential intervention policies using offline reinforcement learning; (3) develop a contextual multi-armed bandit for budget-constrained community-level intervention allocation; and (4) validate the reinforcement learning-derived policy through microsimulation comparing it against standard static intervention approaches.

---

## Introduction References

1. Uthman OA, Sambala EZ, et al. Systematic review of social determinants of childhood immunisation in low- and middle-income countries and equity impact analysis of childhood vaccination coverage in Nigeria. PLOS ONE. 2024;19(2):e0297326.
2. Sridhar S, Maleq N, Guillermet E, et al. A systematic literature review of missed opportunities for immunization in low- and middle-income countries. Vaccine. 2014;32(51):6870-6879.
3. Adedokun ST, et al. Zero-dose, under-immunized, and dropout children in Nigeria: the trend and its contributing factors over time. Vaccines. 2023;11(1):167.
4. World Health Organization/UNICEF. Immunisation Agenda 2030: A Global Strategy to Leave No One Behind. Geneva: WHO; 2020.
5. Tessema ZT, et al. Individual and community-level determinants of pentavalent vaccination dropouts among under-five children in sub-Saharan African countries: a multilevel analysis. BMC Public Health. 2024;24:456.
6. Adedokun ST, et al. Zero-dose, under-immunized, and dropout children in Nigeria. Vaccines. 2023;11(1):167.
7. Adeyinka DA, et al. Widening geographical inequities in DTP vaccination coverage and zero-dose prevalence across Nigeria (2018-2024). Vaccines. 2025;13(11):1135.
8. Andersen RM. Revisiting the behavioral model and access to medical care: does it matter? J Health Soc Behav. 1995;36(1):1-10.
9. Eze P, et al. Effect of mHealth interventions on childhood immunization in low- and middle-income countries: a meta-analysis. Hum Vaccin Immunother. 2021;17(2):507-515.
10. Brugha RF, Kevany JP. Maximizing immunization coverage through home visits: a controlled trial in an urban area of Ghana. Bull World Health Organ. 1996;74(5):517-524.
11. Banerjee AV, Duflo E, Glennerster R, et al. Improving immunisation coverage in rural India: clustered randomised controlled evaluation of immunisation campaigns with and without incentives. BMJ. 2010;340:c2220.
12. Ernst D, Geurts P, Wehenkel L. Tree-based batch mode reinforcement learning. J Mach Learn Res. 2005;6:503-556.
13. Kumar A, Zhou A, Tucker G, Levine S. Conservative Q-learning for offline reinforcement learning. Advances in Neural Information Processing Systems. 2020;33:1179-1191.
14. Komorowski M, Celi LA, Badawi O, et al. The Artificial Intelligence Clinician learns optimal treatment strategies for sepsis in intensive care. Nat Med. 2018;24(11):1716-1720.
15. Raghu A, Komorowski M, Celi LA, et al. Deep reinforcement learning for sepsis treatment. arXiv preprint. 2017;1711.09602.
16. Raghu A, Komorowski M, Singh S. Model-based reinforcement learning for sepsis treatment. arXiv preprint. 2018;1811.09602.
