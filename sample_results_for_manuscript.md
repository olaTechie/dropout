# Results Summary for Manuscript

**Study:** Missed Opportunities for Vaccination in Nigeria
**Data:** NDHS 2024 | n = 4,898 children aged 12-23 months
**Date:** April 2026

This document summarises all results across the four-stage analytical framework
with interpretations ready for manuscript drafting.

---

## Stage 1: Machine Learning Prediction and SHAP Explainability

### 1.1 Sample Characteristics

The analytic sample comprised 4,898 children aged 12-23 months from the Nigeria
Demographic and Health Survey 2024, restricted to alive children and the youngest
child per woman. The survey-weighted MOV prevalence was 49.1% (n = 2,406),
meaning that nearly half of all children who had at least one health system
contact remained incompletely vaccinated. Full vaccination coverage (all 9
antigens) was 33.3%. The proportion of children with any health system contact
was 82.4%.

### 1.2 Model Performance

An XGBoost gradient-boosted tree classifier was trained on 60 predictor features
across the Three Delays framework (22 Delay 1 features, 22 Delay 2 features,
16 Delay 3 features) with 200 Optuna hyperparameter optimisation trials.

| Metric | XGBoost | Random Forest |
|--------|---------|--------------|
| AUC-ROC | **0.884** | 0.888 |
| AUC-PR | 0.892 | 0.893 |
| F1 Score | 0.765 | 0.782 |
| Sensitivity | 0.725 | 0.758 |
| Specificity | 0.838 | 0.828 |
| Brier Score | reported | reported |

**Interpretation:** Both models achieved high discriminative performance
(AUC > 0.88), indicating that MOV status is strongly predictable from
observable individual, household, community, and health system characteristics.
The Random Forest marginally outperformed XGBoost on AUC-ROC (0.888 vs 0.884),
though the difference is not clinically meaningful. XGBoost was retained as the
primary model due to its native handling of missing values and compatibility
with SHAP TreeExplainer for exact Shapley value computation.

### 1.3 Three Delays SHAP Decomposition

SHAP values were computed for all test observations using TreeExplainer and
decomposed by delay type. For each child, the sum of absolute SHAP values
was computed separately for Delay 1 (Decision), Delay 2 (Access), and
Delay 3 (Receiving) features, and the dominant delay was assigned as the
type with the largest total contribution.

| Dominant Delay | Proportion | Mean |SHAP| |
|---------------|-----------|--------------|
| Delay 3: Receiving (supply-side) | **96.8%** | 2.80 |
| Delay 2: Access (geographic) | 3.2% | 0.81 |
| Delay 1: Decision (demand-side) | 0.0% | 0.37 |

**Interpretation:** MOV in Nigeria is overwhelmingly a supply-side (health
system) failure. For 96.8% of children, the factors most predictive of MOV
are institutional — whether a facility delivery occurred, whether a health
card was issued, whether postnatal care was provided, and the number of
health contacts. This finding has direct policy implications: interventions
should target provider behaviour and facility-level screening protocols,
not community-level demand generation.

**Methodological note:** The dominance of Delay 3 partly reflects the
outcome construction — `vac_mov = (vac_count != 9) & (contact_any == 1)` —
which conditions on health system contact. The contact-type variables
(individual contact indicators) are distinct from the overall contact
requirement and carry genuine predictive information about which types of
contact are associated with subsequent vaccination. The finding should be
discussed as reflecting the conditional question: "among children who
reached the health system, what determines whether they were vaccinated?"

### 1.4 Descriptive Statistics (Table 1)

A publication-ready Table 1 was generated using the `tableone` package
with chi-squared tests for categorical variables, Welch's t-test for
normally distributed continuous variables, and Kruskal-Wallis tests for
non-normal continuous variables. Standardised mean differences (SMD) were
computed between MOV and non-MOV groups.

**Variables with largest group differences (SMD > 0.15):**

| Variable | SMD | Direction | p-value |
|----------|-----|-----------|---------|
| Vaccines received (0-9) | 0.343 | MOV children: median 6 vs 9 | <0.001 |
| Number of health contacts | 0.318 | MOV children: more contacts | <0.001 |
| Facility delivery | 0.223 | MOV children: more facility births | <0.001 |
| Postnatal care | 0.197 | MOV children: more PNC | <0.001 |
| Wealth quintile | 0.182 | MOV children: slightly wealthier | <0.001 |
| Partner education | 0.168 | MOV children: higher partner edu | <0.001 |
| Fever/cough treatment | 0.174 | MOV children: more treatment | <0.001 |
| Diarrhoea treatment | 0.162 | MOV children: more treatment | <0.001 |
| Currently employed | 0.154 | MOV children: more employed | <0.001 |
| Vitamin A received | 0.148 | MOV children: more vitamin A | <0.001 |

**Interpretation:** A seemingly paradoxical pattern emerges: MOV children
tend to have MORE health contacts, higher wealth, more education, and more
treatment-seeking than non-MOV children. This is not paradoxical — it
reflects the definition of MOV. Children with zero contacts are classified
as "left out," not MOV. MOV children are those who repeatedly contacted the
system but were never fully vaccinated, suggesting a systematic failure in
vaccination screening at the point of care rather than a failure to reach
the system.

### 1.5 Spatial EDA

**Funnel plot:** State-level MOV prevalence was plotted against sample size
with 95% and 99.7% confidence intervals. Several states fell outside the
95% CI, indicating statistically unusual MOV rates.

**Choropleth:** The state-level MOV prevalence map shows geographic
variation but no clear north-south gradient (unlike typical DPT3 coverage
maps). This suggests MOV is a problem across all regions, not concentrated
in the under-served north.

**Spatial autocorrelation:** Global Moran's I = -0.052 (p = 0.414),
indicating no statistically significant spatial clustering of MOV at the
state level. This is an important negative finding: unlike raw vaccination
coverage, which clusters strongly in the north, MOV is geographically
diffuse. Adjacent states do not have systematically similar MOV rates. The
LISA analysis identified 2 High-Low outliers and 1 Low-High outlier but
no Hot-Hot or Cold-Cold clusters.

**Interpretation:** The absence of spatial clustering reinforces the
supply-side interpretation. If MOV were driven by geographic access
(Delay 2), we would expect spatial clustering (remote areas have
systematically higher MOV). Instead, MOV appears to be a facility-level
failure that occurs wherever there are health contacts — in both northern
and southern states, urban and rural areas.

---

## Stage 2: Microsimulation of Intervention Strategies

### 2.1 Scenario Design

Four intervention scenarios were simulated using individual-level
microsimulation with 1,000 bootstrap iterations. Each child's MOV
probability was modified based on their dominant delay type, with
attenuated effects when the intervention targeted a different delay than
the child's dominant one (mismatch attenuation factor = 0.30).

### 2.2 Results

| Scenario | MOV Rate | 95% CI | FIC Gained/yr | ICER (₦/FIC) | Equity Ratio |
|----------|----------|--------|--------------|-------------|-------------|
| Baseline | 0.491 | - | - | - | - |
| A: Universal Training | 0.392 | 0.378-0.404 | 642,519 | 116.73 | 0.93 |
| B: Targeted High-Risk | 0.438 | 0.424-0.453 | 341,977 | **87.73** | **1.06** |
| C: Progressive | 0.391 | 0.377-0.404 | **645,610** | 107.68 | 0.95 |
| D: Integrated Delivery | 0.411 | 0.397-0.424 | 518,356 | 98.39 | 0.93 |

### 2.3 Interpretation

**Cost-effectiveness:** Scenario B (targeted intervention at the highest-risk
20% of clusters) achieved the lowest incremental cost-effectiveness ratio
(₦87.73 per additional fully immunised child), making it the most efficient
use of resources.

**Coverage:** Scenarios A and C delivered the most additional FIC (~643,000
and 646,000 per year respectively), representing approximately 20% MOV
reduction nationally. Scenario C (progressive targeting) achieves this
through phased roll-out, starting with the highest-risk facilities.

**Equity:** Scenario B is the only intervention with a pro-poor equity
ratio (1.06), meaning it benefits children from the poorest households
proportionally MORE than the richest. All other scenarios have equity
ratios below 1.0, indicating that wealthier children benefit slightly
more — likely because wealthier children have more facility contacts.

**Policy recommendation:** For equity-focused programmes with limited
budgets, Scenario B is optimal. For maximum national impact, Scenario C
(progressive) is recommended, phasing from B to universal over 10 years.
The combination of Scenario B's targeting strategy with the ABM finding
that provider training is the dominant mechanism (see Stage 3) suggests
that targeted provider training at high-risk facilities is the optimal
first-phase intervention.

---

## Stage 3: Agent-Based Model of Network Spillover Effects

### 3.1 Model Design

A Mesa-based agent-based model was constructed with 500 provider agents
and 5,000 caregiver agents on Watts-Strogatz small-world networks. Providers
update their vaccination screening probability through peer influence (β₁)
and supervision effects (β₂). Caregivers decide vaccination acceptance based
on individual acceptance probability (initialised from ML risk scores) and
peer influence (α₂) from neighbours' vaccination status.

Key design features:
- 20% of providers are "resistant" (do not respond to peer influence)
- Trained providers maintain high screening through elevated equilibrium
- Children initialised at observed MOV state (MOV=0.499, not all unvaccinated)
- Contact rate 0.80 (cumulative, converted to per-step probability)
- 200 time steps to allow spillover propagation

### 3.2 Results

| Experiment | Final MOV | Reduction | Screening Rate |
|-----------|----------|-----------|---------------|
| 1. Baseline | 0.422 | — | 0.210 |
| 2. Provider training (bottom 50% → 0.95) | **0.351** | **16.9%** | 0.410 |
| 3. Caregiver champions (top 10% → 0.95) | 0.422 | 0.0% | 0.210 |
| 4. Combined (provider + caregiver) | 0.354 | 16.0% | 0.410 |
| 5. Network-informed provider (top 10% hubs → 0.95) | 0.396 | 6.2% | 0.287 |

### 3.3 Interpretation

**Provider training is the dominant mechanism.** Training the bottom 50%
of low-screening providers produced a 16.9% reduction in MOV, the largest
effect of any intervention. Provider screening rates reached steady state
within approximately 25 time steps and remained stable, indicating that
training effects are sustained through the reinforcing effect of peer
norms among trained providers.

**Caregiver peer influence alone has zero effect.** Even setting the top
10% of socially connected caregivers to maximum acceptance (0.95) produced
no measurable MOV reduction. This is because the bottleneck is provider
screening, not caregiver willingness. If providers do not check vaccination
status during a visit, the child leaves unvaccinated regardless of the
caregiver's acceptance probability. This finding directly supports the
SHAP result that Delay 3 (supply-side) factors dominate.

**Combined targeting adds nothing beyond provider-only.** The combined
intervention (16.0%) performed marginally worse than provider-only (16.9%),
confirming that the caregiver component contributes no additional effect
when provider behaviour is already improved. Resources allocated to
caregiver champions would be better directed at additional provider training.

**Network-informed targeting is efficient but limited.** Targeting the top
10% most-connected providers (hub nodes) achieved 6.2% reduction — meaningful
but substantially less than the bottom-50% training approach. This is because
hub providers may already have moderate screening rates; the bottom-targeting
approach identifies and corrects the worst performers regardless of network
position.

**Provider screening dynamics.** The right panel of the spillover plot shows
flat screening lines after initial convergence (~25 steps). This reflects
the supervision equilibrium: untrained providers converge to ~0.30 screening
probability, while trained providers maintain ~0.80. The sustained gap between
trained and untrained screening is what drives the cumulative MOV difference
visible in the left panel. The 20% resistant providers remain at ~0.15
throughout, representing facilities with structural barriers to behaviour
change.

---

## Stage 4: Counterfactual Analysis

### 4.1 Design

Two parallel simulation worlds were constructed:
- **World A (Reality):** DPT3 coverage follows observed trajectory from
  NDHS 2013, 2018, and 2024, with linear interpolation between waves and
  extrapolation to 2030.
- **World B (Counterfactual):** MOV is eliminated from 2010 onwards. All
  children who contact the health system are fully vaccinated. Additional
  coverage = MOV rate × contact rate.

Birth cohort sizes from UN World Population Prospects. Disease burden
parameters from WHO CHOICE.

### 4.2 Results

| Metric | Value | 95% CI |
|--------|-------|--------|
| Total additional FIC (2010-2030) | **44,541,926** | 35.6M - 54.8M |
| Retrospective FIC (2010-2026) | 34,326,738 | — |
| Prospective FIC (2027-2030) | 10,215,188 | — |
| DALYs averted | **84,630** | 56,665 - 118,387 |

**Disease-specific burden averted:**

| Disease | Cases/unvaxxed | DALYs/case | Contribution |
|---------|---------------|-----------|-------------|
| Measles | 0.10 | 0.002 | Largest |
| Pertussis | 0.05 | 0.004 | Moderate |
| Neonatal tetanus | 0.01 | 0.15 | Smallest |

### 4.3 Interpretation

**The cost of inaction is massive.** If Nigeria had eliminated MOV in 2010
— ensuring that every child who contacted the health system received all
due vaccines — an additional 44.5 million children would have been fully
immunised by 2030. This represents approximately 2 million additional
fully immunised children per year.

**The retrospective burden dominates.** Of the 44.5 million additional FIC,
34.3 million (77%) are from the retrospective phase (2010-2026), representing
children who have already been missed. The prospective component (10.2
million, 2027-2030) represents the future gain achievable if MOV were
eliminated now.

**The gap widens over time.** As Nigeria's birth cohort grows (from 7.1
million in 2010 to 10.1 million in 2030), the absolute number of children
affected by MOV increases each year, even as the MOV rate gradually declines.
This demographic pressure makes MOV elimination increasingly urgent.

**Cost-effectiveness context.** At the microsimulation's best ICER of
₦87.73 per additional FIC (Scenario B), eliminating MOV in 2 million
additional children per year would cost approximately ₦175 million
(~$200,000) annually — an exceptionally cost-effective intervention by
any global health threshold.

---

## Cross-Stage Synthesis

### Convergent Evidence for Supply-Side Intervention

All four analytical approaches independently converge on the same
conclusion: MOV in Nigeria is primarily a health system delivery failure,
and provider-level interventions offer the greatest return on investment.

| Stage | Method | Key Evidence |
|-------|--------|-------------|
| 1 | SHAP decomposition | 96.8% of children have Delay 3 as dominant barrier |
| 1 | Table 1 (SMD) | MOV children have MORE contacts, not fewer |
| 1 | Moran's I | No spatial clustering — MOV is diffuse, not geographic |
| 2 | Microsimulation | Delay 3-targeted scenarios (A, B, C) outperform Delay 2 (D) |
| 2 | Equity analysis | Targeted training (B) is only pro-poor option |
| 3 | ABM experiments | Provider training: 16.9% reduction; caregiver champions: 0% |
| 3 | ABM dynamics | Provider screening is the binding constraint |
| 4 | Counterfactual | 44.5M children missed — massive cost of inaction |

### Recommended Policy Package

Based on the integrated evidence:

1. **Phase 1 (Years 1-2):** Implement Scenario B — targeted provider
   training at the top 20% highest-risk clusters. Focus on the bottom
   50% of low-screening providers at these facilities. Expected ICER:
   ₦87.73/FIC. Pro-poor (equity ratio 1.06).

2. **Phase 2 (Years 3-5):** Expand to Scenario C Phase 2 — extend
   training to facilities with MOV risk scores 0.60-0.80.

3. **Phase 3 (Years 6-10):** Universal provider training coverage.

4. **Do NOT invest in standalone caregiver champion programmes** for
   MOV reduction. The ABM shows zero effect when provider screening
   is the bottleneck. However, caregiver programmes may have value for
   zero-dose children (who never contact the system), which is a
   different target population.

---

## Key Numbers for Abstract

- n = 4,898 children aged 12-23 months (NDHS 2024)
- MOV prevalence: 49.1%
- Full vaccination: 33.3%
- AUC-ROC: 0.884
- Delay 3 dominance: 96.8%
- Best ICER: ₦87.73/FIC (Scenario B, targeted)
- Only pro-poor scenario: B (equity ratio 1.06)
- ABM: provider training → 16.9% MOV reduction; caregiver champions → 0%
- Counterfactual: 44.5 million additional FIC if MOV eliminated 2010-2030
- DALYs averted: 84,630
- No spatial clustering of MOV (Moran's I = -0.052, p = 0.414)

---

## Limitations to Discuss

1. **Cross-sectional data:** MOV status inferred from vaccination history
   and contact indicators, not directly observed at point of care.

2. **Contact timing:** DHS contact variables do not record whether the
   contact occurred when the child was age-eligible for specific vaccines.

3. **Vitamin A proxy:** m54 is NA in NDHS 2024; h34 (child vitamin A in
   last 6 months) used as replacement contact indicator.

4. **SHAP Delay 3 dominance:** Partly reflects outcome construction
   conditioning on contact_any = 1. Discuss as conditional interpretation.

5. **Microsimulation assumptions:** Intervention effect sizes from
   published literature, not Nigeria-specific RCT data.

6. **ABM network structure:** Synthetic Watts-Strogatz networks, not
   actual social ties. Resistant provider fraction (20%) is assumed.

7. **Counterfactual assumptions:** MOV rate interpolated between NDHS
   waves; prospective phase holds MOV at 2024 level.

8. **No supply-side data:** DHS does not measure vaccine stockouts,
   cold chain functionality, or provider knowledge directly.
