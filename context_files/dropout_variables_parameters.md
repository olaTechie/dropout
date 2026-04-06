# Variables, Parameters and Assumptions
## Vaccine Dropout in Nigeria — RL-Optimised Sequential Intervention
### Offline RL · Multi-Armed Bandit · Microsimulation

**Study:** RL-Optimised Sequential Intervention for Reducing DTP1-to-DTP3 Vaccine Dropout in Nigeria
**Affiliation:** Warwick Applied Health, Warwick Medical School, University of Warwick
**Date:** April 2026 · Version 1.0

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Outcome and Cascade Variables](#2-outcome-and-cascade-variables)
3. [MDP State Space Variables](#3-mdp-state-space-variables)
4. [MDP Action and Reward Definitions](#4-mdp-action-and-reward-definitions)
5. [Machine Learning Parameters](#5-machine-learning-parameters)
6. [Offline RL Parameters](#6-offline-rl-parameters)
7. [Multi-Armed Bandit Parameters](#7-multi-armed-bandit-parameters)
8. [Microsimulation Parameters](#8-microsimulation-parameters)
9. [Master Parameter Summary](#9-master-parameter-summary)
10. [References](#10-references)

---

## 1. Introduction

This document specifies all variables, parameters, and modelling assumptions for the four-stage Nigeria vaccine dropout study. The study frames DTP series completion as a Markov Decision Process and learns optimal sequential intervention policies using offline reinforcement learning.

**Key distinction from zero-dose and MOV studies:** The analytic sample is restricted to children who *received DTP1* — i.e. those who entered the immunisation cascade. Zero-dose children (h3 == 0) are excluded. This is a retention analysis, not an access analysis.

**Unique data asset:** NDHS 2024 vaccination card dates (`h3d/h3m/h3y`, `h5d/h5m/h5y`, `h7d/h7m/h7y`) enable reconstruction of temporal vaccination trajectories, inter-dose intervals, and timeliness — the raw material for MDP state transitions.

---

## 2. Outcome and Cascade Variables

### 2.1 Primary Outcome

| Item | Specification |
|------|---------------|
| Variable | `vac_dropout` |
| Definition | Received DTP1 but not DTP3 |
| Construction | `((vac_dpt1==1) \| (vac_dpt2==1)) & (vac_dpt3==0)` |
| WHO formula | `dropout_rate = (DTP1_cov − DTP3_cov) / DTP1_cov × 100` |

### 2.2 Transition-Specific Outcomes

| Transition | Definition | DHS construction |
|-----------|-----------|-----------------|
| T1 dropout | Received DTP1, not DTP2 | `(h3 in 1/3) & (h5 == 0)` |
| T2 dropout | Received DTP2, not DTP3 | `(h5 in 1/3) & (h7 == 0)` |
| Completer | Received DTP1, DTP2, and DTP3 | `(h3 in 1/3) & (h5 in 1/3) & (h7 in 1/3)` |

### 2.3 Vaccination Date Variables

| Variable | DHS code | Description | Valid if |
|----------|----------|-------------|---------|
| DTP1 day | `h3d` | Day of DTP1 vaccination | `h3 == 1` (card with date) |
| DTP1 month | `h3m` | Month | `h3 == 1` |
| DTP1 year | `h3y` | Year | `h3 == 1` |
| DTP2 day | `h5d` | Day of DTP2 vaccination | `h5 == 1` |
| DTP2 month | `h5m` | Month | `h5 == 1` |
| DTP2 year | `h5y` | Year | `h5 == 1` |
| DTP3 day | `h7d` | Day of DTP3 vaccination | `h7 == 1` |
| DTP3 month | `h7m` | Month | `h7 == 1` |
| DTP3 year | `h7y` | Year | `h7 == 1` |
| Birth day (card) | `h25d` | Day from vaccination card | Card seen |
| Birth month (card) | `h25m` | Month | Card seen |
| Birth year (card) | `h25y` | Year | Card seen |

**Missing date codes:** 97 = Inconsistent, 98 = Don't know → treat as missing.

### 2.4 Derived Temporal Variables

| Variable | Construction | Unit |
|----------|-------------|------|
| `interval_birth_dtp1` | `date(h3) − date(h25)` | Days |
| `interval_dtp1_dtp2` | `date(h5) − date(h3)` | Days |
| `interval_dtp2_dtp3` | `date(h7) − date(h5)` | Days |
| `dtp1_timely` | `interval_birth_dtp1 ≤ 56` | Binary |
| `dtp2_timely` | cumulative interval ≤ 84 days | Binary |
| `dtp3_timely` | cumulative interval ≤ 112 days | Binary |
| `delay_accumulation` | total days behind schedule | Days |

---

## 3. MDP State Space Variables — Organised by Andersen's Behavioural Model

Andersen's Behavioural Model of Health Services Use (Andersen, 1995) categorises determinants of utilisation into **predisposing** factors (characteristics existing prior to the care episode), **enabling** factors (resources that facilitate or impede use), and **need** factors (conditions generating the requirement for services). We extend this with a fourth domain — **dynamic/temporal** features — unique to the sequential MDP formulation, capturing the child's evolving state within the immunisation cascade.

The Andersen-stratified SHAP decomposition tests the hypothesis that:
- **T1 dropout** (early exit, DTP1→DTP2): dominated by predisposing factors (health beliefs, trust, education)
- **T2 dropout** (late exit, DTP2→DTP3): dominated by enabling factors (access, distance, cost) and need factors (competing health needs, lost card)

### 3.1 Predisposing Factors

**Demographic:**

| Feature | DHS code | Type | Recode | Andersen sub-domain |
|---------|----------|------|--------|---------------------|
| Maternal age | `v012` | Continuous | Also: 15–24/25–34/35–49 | Demographic |
| Child sex | `b4` | Binary | `male = b4 == 1` | Demographic |
| Birth order | `bord` | Continuous | Also: `hbord = bord > 4` | Demographic |
| Parity | `v201` | Continuous | Capped at 10 | Demographic |

**Social structure:**

| Feature | DHS code | Type | Recode | Andersen sub-domain |
|---------|----------|------|--------|---------------------|
| Maternal education | `v106` | Categorical | 0=none, 1=primary, 2=secondary+ | Social structure |
| Partner's education | `v701` | Categorical | 0=none, 1=primary, 2=secondary+ | Social structure |
| Polygyny | `v505` | Binary | `polyg = v505 > 0` | Social structure |
| Ethnicity | `v131` | Categorical | Major ethnic groups | Social structure |

**Health beliefs:**

| Feature | DHS code | Type | Recode | Andersen sub-domain |
|---------|----------|------|--------|---------------------|
| Decision autonomy | `v743a` | Categorical | Own health care decisions | Health beliefs |
| Permission barrier | `v467b` | Binary | 0=not problem, 1=big problem | Health beliefs |
| TV access | `v159` | Binary | `tele = v159 != 0` | Health beliefs |
| Radio access | `v158` | Binary | `radio = v158 != 0` | Health beliefs |
| Newspaper access | `v157` | Binary | `mag = v157 != 0` | Health beliefs |
| Any media | constructed | Binary | `anymatch(tele mag radio), val(1)` | Health beliefs |
| COVID vaccine willing | `s1112s` | Binary | Trust proxy (NDHS 2024 only) | Health beliefs |
| COVID vaccine received | `s1112p` | Binary | Trust proxy (NDHS 2024 only) | Health beliefs |

### 3.2 Enabling Factors

**Personal/family resources:**

| Feature | DHS code | Type | Recode | Andersen sub-domain |
|---------|----------|------|--------|---------------------|
| Wealth quintile | `v190` | Ordinal | 1–5 | Personal enabling |
| Wealth score | `v191` | Continuous | Factor score | Personal enabling |
| Employment | `v714` | Binary | 0/1 | Personal enabling |
| Health insurance | `v481` | Binary | 0/1 | Personal enabling |
| Household size | `v136` | Continuous | — | Family enabling |
| Female household head | `v151` | Binary | `fhead = v151 == 2` | Family enabling |
| Under-5 children | `v137` | Continuous | — | Family enabling |

**Community resources:**

| Feature | DHS code | Type | Construction | Andersen sub-domain |
|---------|----------|------|-------------|---------------------|
| Urban/rural | `v025` | Binary | `rural = v025 == 2` | Community enabling |
| Geopolitical zone | `szone` | Categorical | 6 zones | Community enabling |
| State | `sstate` | Categorical | 36 + FCT | Community enabling |
| Travel time | `v483a` | Continuous | Minutes to facility | Community enabling |
| Community poverty | constructed | Continuous | `(Σ poorest / N) × 100` | Community enabling |
| Community illiteracy | constructed | Continuous | `(Σ no education / N) × 100` | Community enabling |
| Community unemployment | constructed | Continuous | `(Σ not working / N) × 100` | Community enabling |
| Community media access | constructed | Continuous | `(Σ any media / N) × 100` | Community enabling |
| Ethnic diversity | constructed | Continuous | Herfindahl index | Community enabling |
| Community SES score | constructed | Quintiles | PCA composite | Community enabling |

**Geospatial enabling (NGGC8AFL.csv):**

| Feature | Column | Andersen sub-domain |
|---------|--------|---------------------|
| Population density | `UN_Population_Density_2020` | Community enabling |
| Travel times (to city) | `Travel_Times` | Community enabling |
| Nightlights | `Nightlights_Composite` | Community enabling |
| Malaria prevalence | `Malaria_Prevalence_2020` | Community enabling (competing burden) |
| ITN coverage | `ITN_Coverage_2020` | Community enabling |

### 3.3 Need Factors

**Perceived need** (caregiver's engagement with the health system):

| Feature | DHS code | Type | Recode | Andersen sub-domain |
|---------|----------|------|--------|---------------------|
| Health card possession | `h1a` | Ordinal | 0–8 | Perceived need |
| ANC visits | `m14` | Ordinal | 0=none; 1–3; 4+ | Perceived need |
| Facility delivery | `m15` | Binary | 21–46=facility | Perceived need |
| Vitamin A (child) | `h34` | Binary | 0/1 | Perceived need |
| PNC child (post-discharge) | `m70` | Binary | 0/1 | Perceived need |
| PNC child (pre-discharge) | `m74` | Binary | 0/1 | Perceived need |
| Fieldworker visit | `v393` | Binary | 0/1 | Perceived need |

**Evaluated need** (health system indicators):

| Feature | DHS code | Type | Recode | Andersen sub-domain |
|---------|----------|------|--------|---------------------|
| Vaccination venue | `h69` | Categorical | Public/private/NGO/campaign | Evaluated need |
| Contact count | constructed | Count | Sum of contact variables (0–6) | Evaluated need |
| Recent diarrhoea | `h11` | Binary | Had diarrhoea (competing need) | Evaluated need |
| Recent fever | `h22` | Binary | Had fever (competing need) | Evaluated need |

### 3.4 Dynamic/Temporal Features (MDP-Specific Extension)

These features evolve across dose steps and extend Andersen's static framework to capture the child's trajectory through the immunisation cascade:

| Feature | Type | Description | MDP role |
|---------|------|-------------|----------|
| `child_age_weeks` | Continuous | Age at current dose step | State transition timing |
| `doses_received` | Count (0–2) | DTP doses received so far | Cascade position |
| `dose_step` | Categorical (1/2) | Which transition | Decision epoch |
| `last_dose_timely` | Binary | Was previous dose on schedule? | Trajectory quality |
| `inter_dose_interval` | Continuous (days) | Days since last dose | Retention signal |
| `delay_accumulation` | Continuous (days) | Total days behind schedule | Cumulative risk |
| `community_dropout` | Continuous | Cluster-level dropout rate | Peer/contextual |
| `cluster_dtp_coverage` | Continuous | Cluster-level DTP3 coverage | Peer/contextual |

---

## 4. MDP Action and Reward Definitions

### 4.1 Action Space

| Action | Code | Description | Cost (₦) | Effect size |
|--------|------|-------------|----------|-------------|
| No intervention | a₀ | Status quo | 0 | Baseline |
| SMS reminder | a₁ | Text message before due date | 50 | +5–10% completion |
| CHW home visit | a₂ | Community health worker follow-up | 500 | +15–25% completion |
| Facility recall + tracing | a₃ | Active defaulter tracing | 1,500 | +20–30% completion |
| Conditional incentive | a₄ | Small cash/voucher for attendance | 800 | +10–20% completion |

Effect sizes from published RCTs (to be refined by Agent 5 literature review).

### 4.2 Behaviour Policy Inference

| Observed pattern | Inferred action |
|-----------------|----------------|
| Next dose ON TIME (≤ 2 weeks of schedule) | a₁ or a₂ (effective intervention) |
| Next dose LATE (> 2 weeks delayed) | a₀ or a₁ (weak/no intervention) |
| Next dose NOT received | a₀ (no effective intervention) |
| Fieldworker visited (`v393 == 1`) | More likely a₂ |
| Card present (`h1a ≥ 1`) | More likely a₁ (reminder system) |
| Vaccinated at campaign (`h69 == 41`) | More likely a₃ (outreach) |

### 4.3 Reward Function

```
R(s, a, s') = +1.0  if DTP3 completed (terminal reward)
            + +0.3  if next dose received (intermediate reward)
            − λ × cost(a)  (cost penalty)

where λ = cost penalty weight (tuned via sensitivity analysis)
Default λ = 0.001 (₦1 penalty per ₦1,000 spent)
```

---

## 5. Machine Learning Parameters (Stage 1)

### XGBoost for Transition-Specific Prediction

| Parameter | Search space | Method |
|-----------|-------------|--------|
| `max_depth` | 3–10 | Optuna (200 trials) |
| `learning_rate` | 0.01–0.30 | Optuna |
| `n_estimators` | 100–1000 | Optuna |
| `min_child_weight` | 1–10 | Optuna |
| `subsample` | 0.6–1.0 | Optuna |
| `colsample_bytree` | 0.6–1.0 | Optuna |

Three separate models: T1, T2, Full. AUC-ROC as primary metric.

---

## 6. Offline RL Parameters (Stage 2)

### 6.1 FQI Parameters

| Parameter | Value | Sensitivity |
|-----------|-------|-------------|
| Function approximator | XGBoost (tree-based) | Also test neural network |
| Number of iterations | 100 | 50–200 |
| Discount γ | 0.95 | 0.90–0.99 |
| Convergence threshold | ΔQ < 0.001 | — |

### 6.2 CQL Parameters

| Parameter | Value | Sensitivity |
|-----------|-------|-------------|
| CQL α (penalty weight) | 1.0 | 0.1–5.0 |
| Learning rate | 3e-4 | 1e-4–1e-3 |
| Batch size | 256 | 128–512 |
| Training steps | 200,000 | 100k–500k |
| Network architecture | 2 hidden layers × 256 | 128–512 |
| Discount γ | 0.95 | 0.90–0.99 |

### 6.3 Off-Policy Evaluation

| Method | Purpose |
|--------|---------|
| Importance Sampling (IS) | Unbiased but high variance |
| Doubly Robust (DR) | Lower variance, requires model |
| Fitted Q Evaluation (FQE) | Model-based, lower variance |

---

## 7. Multi-Armed Bandit Parameters (Stage 3)

| Parameter | Value | Sensitivity |
|-----------|-------|-------------|
| Algorithm | LinUCB | Also: Thompson Sampling |
| Context dimension | ~15 (LGA features) | — |
| Number of arms | 5 (action space) | — |
| Exploration parameter α | 1.0 | 0.5–2.0 |
| Budget constraint | ₦500M national | ₦250M–₦1B |
| Arm costs | a₀=0, a₁=50, a₂=500, a₃=1500, a₄=800 per child | — |

---

## 8. Microsimulation Parameters (Stage 4)

| Parameter | Value | Sensitivity |
|-----------|-------|-------------|
| Synthetic population N | 10,000 | 5,000–50,000 |
| Bootstrap iterations | 1,000 | — |
| Scenarios | 6 (S0–S5) | — |
| Transition model | Logistic from XGBoost probabilities | — |
| Cost perspective | Health system | — |
| Discount rate | 3% | 0%–5% |
| Equity constraint | RL must not widen poorest/richest gap | — |

---

## 9. Master Parameter Summary

| # | Parameter | Stage | Central value | Sensitivity range | Priority |
|---|-----------|-------|---------------|-------------------|----------|
| 1 | Dropout outcome | 1 | (DTP1+)&(DTP3−) | — | FIXED |
| 2 | Study population | 1 | DTP1 recipients only | — | FIXED |
| 3 | Card dates required for temporal | 1 | h3==1 subset | — | FIXED |
| 4 | Timeliness threshold DTP1 | 1 | ≤56 days | ±14 days | LOW |
| 5 | XGBoost max_depth | 1 | Tuned 3–10 | Optuna | MEDIUM |
| 6 | Discount γ | 2 | 0.95 | 0.90–0.99 | HIGH |
| 7 | CQL α | 2 | 1.0 | 0.1–5.0 | HIGH |
| 8 | CQL training steps | 2 | 200,000 | 100k–500k | MEDIUM |
| 9 | Cost penalty λ | 2 | 0.001 | 0.0001–0.01 | HIGH |
| 10 | SMS effect size | 2,4 | +7.5% | +5%–10% | HIGH |
| 11 | CHW effect size | 2,4 | +20% | +15%–25% | HIGH |
| 12 | Recall effect size | 2,4 | +25% | +20%–30% | HIGH |
| 13 | Incentive effect size | 2,4 | +15% | +10%–20% | HIGH |
| 14 | LinUCB α | 3 | 1.0 | 0.5–2.0 | MEDIUM |
| 15 | National budget | 3 | ₦500M | ₦250M–₦1B | HIGH |
| 16 | Microsim N | 4 | 10,000 | 5,000–50,000 | LOW |
| 17 | Bootstrap iterations | 4 | 1,000 | — | FIXED |

---

## 10. References

1. Andersen RM. Revisiting the behavioral model and access to medical care: does it matter? *JHSB*. 1995;36(1):1–10.
2. WHO/UNICEF. *Immunisation Agenda 2030*. Geneva: WHO; 2020.
2. NPC Nigeria and ICF. *Nigeria DHS 2024*. Abuja/Rockville: NPC/ICF; 2025.
3. Kumar A, Zhou A, Tucker G, Levine S. Conservative Q-learning for offline RL. *NeurIPS*. 2020.
4. Ernst D, Geurts P, Wehenkel L. Tree-based batch mode reinforcement learning. *JMLR*. 2005;6:503–556.
5. Li L, et al. A contextual-bandit approach to personalised recommendation. *WWW*. 2010.
6. Chen T, Guestrin C. XGBoost. *KDD*. 2016.
7. Lundberg SM, Lee SI. SHAP. *NeurIPS*. 2017.
8. ICF. *DHS Methodology*. Rockville: ICF; 2023.
9. NPHCDA. *NSIPSS 2018–2028*. Abuja: NPHCDA; 2018.
