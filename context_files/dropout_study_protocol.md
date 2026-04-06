# Study Protocol: Reinforcement Learning-Optimised Sequential Intervention Strategy for Reducing Vaccine Dropout in Nigeria

**A Markov Decision Process Framework Using Offline Reinforcement Learning, Multi-Armed Bandits, and Microsimulation Validation Applied to the Nigeria Demographic and Health Survey 2024**

---

## Table of Contents

1. [Background and Rationale](#1-background-and-rationale)
2. [Aims and Objectives](#2-aims-and-objectives)
3. [Theoretical Framework](#3-theoretical-framework)
4. [Study Design Overview](#4-study-design-overview)
5. [Data Sources](#5-data-sources)
6. [Stage 1 — Immunisation Cascade and State Space Construction](#6-stage-1--immunisation-cascade-and-state-space-construction)
7. [Stage 2 — Offline Reinforcement Learning](#7-stage-2--offline-reinforcement-learning)
8. [Stage 3 — Multi-Armed Bandit for Adaptive Allocation](#8-stage-3--multi-armed-bandit-for-adaptive-allocation)
9. [Stage 4 — Microsimulation Validation](#9-stage-4--microsimulation-validation)
10. [Stage 5 — Streamlit Dashboard](#10-stage-5--streamlit-dashboard)
11. [Integration Across Components](#11-integration-across-components)
12. [Ethical Considerations](#12-ethical-considerations)
13. [Limitations](#13-limitations)
14. [Dissemination Plan](#14-dissemination-plan)
15. [Timeline](#15-timeline)
16. [Team Roles](#16-team-roles)
17. [References](#17-references)

---

## 1. Background and Rationale

The DTP1-to-DTP3 dropout rate is a key indicator of immunisation programme performance. Children who receive DTP1 but fail to complete the three-dose series represent a distinct programmatic failure from zero-dose children (who never accessed services) and from missed opportunities (where children were at a facility but not vaccinated). Dropout children successfully initiated immunisation — the system engaged them — but failed to retain them through the schedule.

In Nigeria, while DTP1 coverage has reached approximately 67%, DTP3 coverage lags at approximately 56%, implying a dropout rate of roughly 16%. In the North-West and North-East geopolitical zones, dropout rates exceed 25%. The Nigeria EPI schedule requires DTP doses at 6, 10, and 14 weeks of age, with each return visit representing a decision point where caregivers either continue or exit the immunisation cascade.

Existing dropout interventions — SMS reminders, community health worker (CHW) follow-up, defaulter tracing — are typically deployed uniformly without considering the optimal sequencing, timing, or targeting of interventions across the schedule. A caregiver who misses DTP2 at 10 weeks may need a different intervention from one who received DTP1 and DTP2 on time but fails to return for DTP3. Moreover, the optimal intervention may depend on the child's characteristics, the inter-dose interval, and the community context.

This study frames vaccine dropout reduction as a sequential decision problem and applies reinforcement learning to learn the optimal intervention policy — not just *what* intervention to deliver, but *when* and *to whom* across the DTP schedule window.

---

## 2. Aims and Objectives

### Overall Aim

To develop and evaluate a reinforcement learning-optimised sequential intervention strategy for reducing DTP1-to-DTP3 vaccine dropout in Nigeria, using the Nigeria Demographic and Health Survey 2024 to construct the decision environment, learn optimal policies via offline RL, and validate through microsimulation.

### Specific Objectives

1. To construct an immunisation cascade for the DTP series in Nigeria, quantifying transition-specific dropout rates (DTP1→DTP2, DTP2→DTP3) and identifying distinct predictor profiles at each transition using XGBoost and SHAP (Stage 1).

2. To formulate the immunisation schedule as a Markov Decision Process (MDP) where states represent child age, current dose status, inter-dose interval, and household characteristics, and to learn optimal sequential intervention policies using offline reinforcement learning (fitted Q-iteration and conservative Q-learning) trained on vaccination trajectories inferred from NDHS 2024 (Stage 2).

3. To develop a contextual multi-armed bandit framework for adaptive intervention allocation across communities, enabling programmatic resource allocation that learns and adapts based on community-level dropout patterns (Stage 3).

4. To validate the RL-derived optimal policy through microsimulation on a synthetic population, comparing RL-optimised sequential intervention against standard approaches (uniform SMS, uniform CHW, random allocation) in terms of DTP3 completion, cost-effectiveness, and equity (Stage 4).

5. To deliver results through an interactive Streamlit dashboard enabling policy-makers to explore the immunisation cascade, optimal policy maps, and intervention simulation by state, zone, and population subgroup (Dashboard).

---

## 3. Theoretical Framework

### Andersen's Behavioural Model for Variable Selection

The predictor variables for the XGBoost models and MDP state space are organised according to Andersen's Behavioural Model of Health Services Use (Andersen, 1995), which categorises determinants of utilisation into three domains:

1. **Predisposing factors** — characteristics existing prior to the care episode: demographics (maternal age, child sex, birth order, parity), social structure (education, polygyny, ethnicity), and health beliefs (autonomy, media exposure, vaccine trust proxies)
2. **Enabling factors** — resources that facilitate or impede use: personal/family resources (wealth, employment, insurance, household composition) and community resources (urban/rural, geography, travel time, community-level composites, geospatial covariates)
3. **Need factors** — conditions generating the requirement for services: perceived need (health card possession, ANC engagement, facility delivery, fieldworker visits) and evaluated need (vaccination venue, contact count, competing morbidity)

We extend Andersen's static framework with a fourth domain — **dynamic/temporal features** — that captures the child's evolving state within the immunisation cascade (inter-dose intervals, timeliness, delay accumulation). This extension is necessary because dropout is a sequential process: the optimal intervention at DTP3 depends on what happened at DTP1 and DTP2.

### Immunisation as a Sequential Decision Process

```
IMMUNISATION CASCADE — DTP SERIES (Nigeria EPI Schedule)
══════════════════════════════════════════════════════════════════════

  Birth        6 weeks       10 weeks      14 weeks      12 months
  │            │              │              │              │
  ▼            ▼              ▼              ▼              ▼
  ┌──┐       ┌──────┐      ┌──────┐      ┌──────┐      ┌──────┐
  │  │──────►│ DTP1 │─────►│ DTP2 │─────►│ DTP3 │─────►│ FIC  │
  │  │       │ OPV1 │      │ OPV2 │      │ OPV3 │      │check │
  └──┘       └──┬───┘      └──┬───┘      └──┬───┘      └──────┘
                │              │              │
           ┌────▼────┐   ┌────▼────┐   ┌────▼────┐
           │ DROPOUT │   │ DROPOUT │   │ DROPOUT │
           │ T1→T2   │   │ T2→T3   │   │ after T3│
           │ ~12%    │   │ ~8%     │   │ (series │
           │         │   │         │   │  done)  │
           └─────────┘   └─────────┘   └─────────┘

  At each transition, the AGENT (health system) chooses an ACTION:
  ┌─────────────────────────────────────────────────────────────┐
  │  a₀ = No intervention (status quo)                          │
  │  a₁ = SMS reminder (low cost, low intensity)                │
  │  a₂ = CHW home visit (medium cost, medium intensity)        │
  │  a₃ = Facility recall + defaulter tracing (high cost, high) │
  │  a₄ = Conditional incentive (variable cost)                 │
  └─────────────────────────────────────────────────────────────┘

  The OPTIMAL POLICY π* maps:
  (child state) × (schedule position) → best action

  The RL agent learns π* from observed vaccination trajectories
  in NDHS 2024, optimising: DTP3 completion − λ × cost
```

### Why RL Rather Than Standard ML

Standard ML (XGBoost, logistic regression) predicts *who* will drop out — useful for targeting. But it does not address: *what intervention should be delivered at each dose step, conditional on what happened at prior steps?* This is a sequential decision problem where the optimal action at DTP2 depends on whether DTP1 was on time or delayed, whether an intervention was already deployed, and the child's evolving risk profile. Reinforcement learning naturally handles this temporal dependence.

### Offline RL Justification

We cannot run a live RL experiment (deploying interventions in real time and observing outcomes). Instead, we use **offline RL** — learning from a fixed dataset of observed vaccination trajectories. The DHS vaccination card dates provide rich temporal data: when each dose was received, how long the inter-dose intervals were, and which children eventually completed vs dropped out. This observed data serves as the "behaviour policy" from which the RL agent learns an improved policy.

---

## 4. Study Design Overview

```
STUDY DESIGN — FOUR-STAGE RL FRAMEWORK
══════════════════════════════════════════════════════════════════════

  ┌───────────────────────────────────────────────────────────────┐
  │                    NDHS 2024 KR FILE                          │
  │     Children 12–23 months with DTP1 received (h3 in 1/3)     │
  │                    n ≈ 4,000–5,000                           │
  └────────────────────────┬──────────────────────────────────────┘
                           │
           ┌───────────────┼───────────────┐
           ▼               │               │
  ┌─────────────┐         │               │
  │  STAGE 1    │         │               │
  │  CASCADE    │         │               │
  │  Transition-│         │               │
  │  specific   │         │               │
  │  XGBoost +  │         │               │
  │  SHAP       │         │               │
  └──────┬──────┘         │               │
         │                │               │
         ▼                │               │
  ┌─────────────┐         │               │
  │  STAGE 2    │         │               │
  │  OFFLINE RL │         │               │
  │  MDP + FQI  │◄────────┘               │
  │  + CQL      │                         │
  └──────┬──────┘                         │
         │                                │
         ▼                                │
  ┌─────────────┐                         │
  │  STAGE 3    │                         │
  │  MULTI-ARM  │                         │
  │  BANDIT     │◄────────────────────────┘
  │  Community  │
  │  allocation │
  └──────┬──────┘
         │
         ▼
  ┌─────────────┐
  │  STAGE 4    │
  │  MICRO-     │
  │  SIMULATION │
  │  Validation │
  └──────┬──────┘
         │
         ▼
  ┌─────────────────┐
  │   STREAMLIT     │
  │   DASHBOARD     │
  └─────────────────┘
```

---

## 5. Data Sources

### Primary Data

**Nigeria Demographic and Health Survey 2024 (NDHS 2024)** — Children's Recode (KR) file. The analytic sample is restricted to:
- Children aged 12–23 months (`age_months = v008 - b3`)
- Alive at survey (`b5 == 1`)
- **Received DTP1** (`h3` in [1, 2, 3]) — the dropout analysis requires entry into the cascade
- Youngest child per woman (`bysort caseid (bidx)`)

The critical advantage of DHS for this study is that vaccination card dates (`h3d/h3m/h3y`, `h5d/h5m/h5y`, `h7d/h7m/h7y`) allow reconstruction of the temporal vaccination trajectory for children with card-confirmed dates (`h3 == 1`, `h5 == 1`, `h7 == 1`).

### Supplementary Data

- **NGGC8AFL.csv:** DHS Geospatial Covariates (135 variables, 1,380 clusters)
- Individual Recode (IR), Household Recode (HR) — merged via `v001`/`v002`/`v003`

### Critical Variable Notes

| Issue | Specification |
|-------|---------------|
| Dropout outcome | `vac_dropout = ((vac_dpt1==1) \| (vac_dpt2==1)) & (vac_dpt3==0)` |
| Dropout rate (WHO) | `dropout_rate = (DTP1_coverage − DTP3_coverage) / DTP1_coverage × 100` |
| Transition 1 dropout | Received DTP1 but NOT DTP2: `(h3 in 1/3) & (h5 == 0)` |
| Transition 2 dropout | Received DTP2 but NOT DTP3: `(h5 in 1/3) & (h7 == 0)` |
| Inter-dose interval | Computed from card dates: `interval_12 = date(h5d,h5m,h5y) − date(h3d,h3m,h3y)` |
| Timeliness | DTP1 timely if received ≤ 8 weeks; DTP2 if ≤ 12 weeks; DTP3 if ≤ 16 weeks |
| Card-confirmed subset | `h3 == 1` (date on card) — required for temporal analysis |
| Age/weight/geography | Same as zero-dose and MOV studies: `v008−b3`, `v005/1000000`, `szone`/`sstate` |

---

## 6. Stage 1 — Immunisation Cascade and State Space Construction

### 6.1 Cascade Quantification

Compute the DTP immunisation cascade for Nigeria nationally and by geopolitical zone:

```
CASCADE METRICS:
  DTP1 coverage:    % children 12–23m who received DTP1
  DTP2 coverage:    % children 12–23m who received DTP2
  DTP3 coverage:    % children 12–23m who received DTP3

  Transition 1 retention: DTP2 / DTP1 × 100
  Transition 2 retention: DTP3 / DTP2 × 100
  Overall dropout rate:   (DTP1 − DTP3) / DTP1 × 100

  Timeliness cascade (card-confirmed only):
    DTP1 by 8 weeks   → DTP2 by 12 weeks   → DTP3 by 16 weeks
    (proportion timely at each step)
```

### 6.2 Predictor Variables Organised by Andersen's Behavioural Model

Andersen's Behavioural Model of Health Services Use (Andersen, 1995) categorises determinants of health service utilisation into three domains: **predisposing** factors (characteristics that exist prior to illness/need), **enabling** factors (resources that facilitate or impede use), and **need** factors (conditions that generate the requirement for services). We extend this with a fourth domain — **dynamic/temporal** features — that captures the evolving state of the child within the immunisation cascade. This extension is necessary because dropout is a sequential process: the predictors at the DTP2→DTP3 transition include information about what happened at the DTP1→DTP2 transition.

```
ANDERSEN'S BEHAVIOURAL MODEL ADAPTED FOR VACCINE DROPOUT
══════════════════════════════════════════════════════════════════════

  PREDISPOSING               ENABLING                 NEED
  (Who is the child/         (What resources           (What drives the
   caregiver?)                facilitate return?)       perceived need?)
  ──────────────────         ──────────────────        ──────────────────
  Demographics:              Personal/family:          Perceived need:
   v012  maternal age         v190  wealth              s1112s COVID willing
   b4    child sex            v191  wealth score        s1112p COVID received
   bord  birth order          v714  employment          h1a   health card
   v201  parity               v481  health insurance    m14   ANC visits
                              v136  household size      m15   facility delivery
  Social structure:           v151  HH head sex         h34   vitamin A
   v106  maternal edu                                   m70   PNC child
   v701  partner edu         Community:                 m74   PNC pre-discharge
   v505  polygyny             v025  urban/rural         v393  fieldworker visit
   v131  ethnicity            szone geopolitical zone
                              v483a travel time        Evaluated need:
  Health beliefs:             com_poverty               h69   vaccination venue
   v743a autonomy             com_illit                 contact_count
   v467b permission           com_media                 h11   recent diarrhoea
   media access               com_diversity             h22   recent fever
   v157-v159                  NGGC8AFL covariates

  ──────────────────────────────────────────────────────────────────
                           ↓
  DYNAMIC/TEMPORAL FEATURES (unique to sequential MDP formulation)
  ──────────────────────────────────────────────────────────────────
   child_age_weeks:     age at current dose step
   doses_received:      count of DTP doses so far (0–2)
   last_dose_timely:    was previous dose on schedule?
   inter_dose_interval: days since last dose
   delay_accumulation:  total days behind schedule
   dose_step:           which transition (1 or 2)
   community_dropout:   cluster-level dropout rate
   cluster_dtp_coverage: cluster-level DTP3 coverage
```

#### Predisposing Factors

| Variable | DHS code | Type | Recode | Andersen domain |
|----------|----------|------|--------|-----------------|
| Maternal age | `v012` | Continuous | Also: 15–24/25–34/35–49 | Predisposing: demographic |
| Child sex | `b4` | Binary | `male = b4 == 1` | Predisposing: demographic |
| Birth order | `bord` | Continuous | Also: `hbord = bord > 4` | Predisposing: demographic |
| Parity | `v201` | Continuous | Capped at 10 | Predisposing: demographic |
| Maternal education | `v106` | Categorical | 0=none, 1=primary, 2=secondary+ | Predisposing: social structure |
| Partner's education | `v701` | Categorical | 0=none, 1=primary, 2=secondary+ | Predisposing: social structure |
| Polygyny | `v505` | Binary | `polyg = v505 > 0` | Predisposing: social structure |
| Ethnicity | `v131` | Categorical | Major groups | Predisposing: social structure |
| Decision autonomy | `v743a` | Categorical | Own health care decisions | Predisposing: health beliefs |
| Permission barrier | `v467b` | Binary | 0=not problem, 1=big problem | Predisposing: health beliefs |
| TV access | `v159` | Binary | `tele = v159 != 0` | Predisposing: health beliefs |
| Radio access | `v158` | Binary | `radio = v158 != 0` | Predisposing: health beliefs |
| Newspaper access | `v157` | Binary | `mag = v157 != 0` | Predisposing: health beliefs |
| Any media | constructed | Binary | `anymatch(tele mag radio), val(1)` | Predisposing: health beliefs |
| COVID vaccine willing | `s1112s` | Binary | Trust proxy (NDHS 2024 only) | Predisposing: health beliefs |
| COVID vaccine received | `s1112p` | Binary | Trust proxy (NDHS 2024 only) | Predisposing: health beliefs |

#### Enabling Factors

**Personal/family enabling:**

| Variable | DHS code | Type | Recode | Andersen domain |
|----------|----------|------|--------|-----------------|
| Wealth quintile | `v190` | Ordinal | 1–5 | Enabling: personal |
| Wealth score | `v191` | Continuous | Factor score | Enabling: personal |
| Employment | `v714` | Binary | 0/1 | Enabling: personal |
| Health insurance | `v481` | Binary | 0/1 | Enabling: personal |
| Household size | `v136` | Continuous | — | Enabling: family |
| Female household head | `v151` | Binary | `fhead = v151 == 2` | Enabling: family |
| Under-5 children | `v137` | Continuous | — | Enabling: family |

**Community enabling:**

| Variable | DHS code | Type | Construction | Andersen domain |
|----------|----------|------|-------------|-----------------|
| Urban/rural | `v025` | Binary | `rural = v025 == 2` | Enabling: community |
| Geopolitical zone | `szone` | Categorical | 6 zones | Enabling: community |
| State | `sstate` | Categorical | 36 + FCT | Enabling: community |
| Travel time | `v483a` | Continuous | Minutes to facility | Enabling: community |
| Community poverty | constructed | Continuous | `(Σ poorest / N) × 100` | Enabling: community |
| Community illiteracy | constructed | Continuous | `(Σ no education / N) × 100` | Enabling: community |
| Community unemployment | constructed | Continuous | `(Σ not working / N) × 100` | Enabling: community |
| Community media access | constructed | Continuous | `(Σ any media / N) × 100` | Enabling: community |
| Ethnic diversity | constructed | Continuous | Herfindahl index | Enabling: community |
| Community SES score | constructed | Quintiles | PCA composite | Enabling: community |

**Geospatial enabling (NGGC8AFL.csv):**

| Variable | Column | Andersen domain |
|----------|--------|-----------------|
| Population density | `UN_Population_Density_2020` | Enabling: community |
| Travel times (to city) | `Travel_Times` | Enabling: community |
| Nightlights | `Nightlights_Composite` | Enabling: community |
| ITN coverage | `ITN_Coverage_2020` | Enabling: community |
| Malaria prevalence | `Malaria_Prevalence_2020` | Enabling: community (competing burden) |

#### Need Factors

**Perceived need** (caregiver's perception of the importance of vaccination):

| Variable | DHS code | Type | Recode | Andersen domain |
|----------|----------|------|--------|-----------------|
| Health card possession | `h1a` | Ordinal | 0–8 | Need: perceived |
| ANC visits | `m14` | Ordinal | 0=none; 1–3; 4+ | Need: perceived |
| Facility delivery | `m15` | Binary | 21–46=facility | Need: perceived |
| Vitamin A (child) | `h34` | Binary | 0/1 | Need: perceived |
| PNC child (post-discharge) | `m70` | Binary | 0/1 | Need: perceived |
| PNC child (pre-discharge) | `m74` | Binary | 0/1 | Need: perceived |
| Fieldworker visit | `v393` | Binary | 0/1 | Need: perceived |

**Evaluated need** (health system assessment of vaccination status):

| Variable | DHS code | Type | Recode | Andersen domain |
|----------|----------|------|--------|-----------------|
| Vaccination venue | `h69` | Categorical | Public/private/NGO/campaign | Need: evaluated |
| Contact count | constructed | Count | Sum of contact variables (0–6) | Need: evaluated |
| Recent diarrhoea | `h11` | Binary | Had diarrhoea (competing need) | Need: evaluated |
| Recent fever | `h22` | Binary | Had fever (competing need) | Need: evaluated |

#### Dynamic/Temporal Features (MDP-Specific Extension)

These features evolve across dose steps and are unique to the sequential RL formulation. They do not fit neatly into the static Andersen categories because they capture the child's *trajectory through the cascade* rather than baseline characteristics:

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

### 6.3 Transition-Specific XGBoost Models

Three separate XGBoost models, each predicting dropout at a specific cascade transition:

**Model T1:** Predicts P(dropout at DTP1→DTP2) among children who received DTP1.
**Model T2:** Predicts P(dropout at DTP2→DTP3) among children who received DTP2.
**Model Full:** Predicts P(overall dropout: DTP1 received, DTP3 not received).

All three models use the full Andersen-organised predictor set. SHAP analysis for each model reveals which Andersen domain dominates at which transition point. The hypothesis is:
- **T1 dropout** (early exit): dominated by **predisposing** factors (health beliefs, trust, education) — the caregiver decided not to return
- **T2 dropout** (late exit): dominated by **enabling** factors (access, distance, cost) and **need** factors (competing health needs, lost card) — the caregiver intended to return but was unable

This Andersen-stratified SHAP decomposition directly parallels the Three Delays decomposition used in the MOV study, providing a consistent analytical logic across the immunisation trilogy.

### 6.4 State Space Construction for MDP

The MDP state vector combines static Andersen features with dynamic temporal features:

```
STATE VECTOR s(t) at dose step t ∈ {DTP2_due, DTP3_due}:
  ┌──────────────────────────────────────────────────────────────┐
  │  PREDISPOSING (static):                                      │
  │    child_sex, birth_order, maternal_age, maternal_edu,       │
  │    partner_edu, autonomy, permission, media, ethnicity,      │
  │    covid_willing, covid_received                              │
  │                                                               │
  │  ENABLING (static):                                           │
  │    wealth, employment, insurance, urban_rural, szone,         │
  │    travel_time, com_poverty, com_illit, pop_density           │
  │                                                               │
  │  NEED (static):                                               │
  │    health_card, anc_visits, facility_delivery, vax_venue,     │
  │    vitamin_a, fieldworker_visit                                │
  │                                                               │
  │  DYNAMIC/TEMPORAL (evolving):                                  │
  │    child_age_weeks, doses_received, last_dose_timely,         │
  │    inter_dose_interval, delay_accumulation, dose_step,         │
  │    community_dropout, cluster_dtp_coverage                     │
  └──────────────────────────────────────────────────────────────┘
```

### 6.5 Trajectory Reconstruction

For children with card-confirmed vaccination dates, reconstruct the full temporal trajectory:

```stata
* Compute vaccination dates in CMC or days-since-birth
* DTP1 date
gen dtp1_date = mdy(h3m, h3d, h3y) if h3 == 1
* DTP2 date
gen dtp2_date = mdy(h5m, h5d, h5y) if h5 == 1
* DTP3 date
gen dtp3_date = mdy(h7m, h7d, h7y) if h7 == 1
* Birth date from card
gen birth_date_card = mdy(h25m, h25d, h25y)
* Inter-dose intervals (days)
gen interval_birth_dtp1 = dtp1_date - birth_date_card
gen interval_dtp1_dtp2 = dtp2_date - dtp1_date if dtp2_date != .
gen interval_dtp2_dtp3 = dtp3_date - dtp2_date if dtp3_date != .
* Timeliness flags
gen dtp1_timely = interval_birth_dtp1 <= 56  /* 8 weeks */
gen dtp2_timely = (interval_birth_dtp1 + interval_dtp1_dtp2) <= 84 if interval_dtp1_dtp2 != .
gen dtp3_timely = (interval_birth_dtp1 + interval_dtp1_dtp2 + interval_dtp2_dtp3) <= 112 if interval_dtp2_dtp3 != .
```

---

## 7. Stage 2 — Offline Reinforcement Learning

### 7.1 MDP Formulation

| MDP Element | Specification |
|-------------|---------------|
| **States** S | State vector s(t) as defined in §6.3. Discretised where necessary for tabular methods; continuous for neural fitted Q-iteration. |
| **Actions** A | {a₀: no intervention, a₁: SMS reminder, a₂: CHW home visit, a₃: facility recall + defaulter tracing, a₄: conditional incentive} |
| **Transitions** P(s'|s,a) | Learned from observed DHS trajectories. P(received next dose | current state, inferred action). |
| **Reward** R(s,a,s') | `R = +1.0 if DTP3 completed` + `+0.3 if next dose received` − `λ × cost(a)` where λ is the cost penalty weight. |
| **Discount** γ | 0.95 (values future doses, reflects preference for timely completion) |
| **Horizon** | 3 dose steps (DTP1→DTP2→DTP3) |

### 7.2 Inferring Actions from Observational Data

DHS does not record what interventions were deployed. We infer a proxy "behaviour policy" from observed patterns:

```
BEHAVIOUR POLICY INFERENCE:
  If child received next dose ON TIME (within 2 weeks of schedule):
    → inferred action = "effective intervention occurred" (a₁ or a₂)
  If child received next dose LATE (>2 weeks delayed):
    → inferred action = "weak intervention" (a₀ or a₁)
  If child DID NOT receive next dose:
    → inferred action = "no effective intervention" (a₀)

  Refinement using covariates:
    - If fieldworker visited (v393==1): more likely a₂ (CHW visit)
    - If has health card (h1a≥1): more likely a₁ (reminder system)
    - If vaccination at campaign (h69==41): more likely a₃ (outreach)
```

### 7.3 Offline RL Algorithms

**Fitted Q-Iteration (FQI):**

```python
# Batch RL algorithm
# 1. Collect dataset D = {(s_t, a_t, r_t, s_{t+1})} from DHS trajectories
# 2. Initialise Q̂_0 arbitrarily
# 3. For k = 1, ..., K:
#    For each (s, a, r, s') in D:
#      y = r + γ * max_a' Q̂_{k-1}(s', a')
#    Fit Q̂_k to minimise Σ (Q̂_k(s, a) - y)²
#    using gradient-boosted trees (XGBoost) as function approximator
```

**Conservative Q-Learning (CQL):**

```python
# CQL adds a penalty for Q-values on out-of-distribution actions
# This prevents the learned policy from recommending actions
# that were never observed in the data (critical for offline RL safety)
#
# CQL loss = standard Bellman error
#           + α * (E_π[Q(s,a)] - E_data[Q(s,a)])
#
# Implementation: d3rlpy.algos.CQL or d3rlpy.algos.DiscreteCQL
```

### 7.4 Policy Evaluation

**Off-Policy Evaluation (OPE):** Since we cannot deploy the learned policy in real time, we evaluate it using:
- **Importance Sampling (IS):** Re-weight observed trajectories by the ratio π_learned / π_behaviour
- **Doubly Robust (DR):** Combines IS with a direct method estimate for lower variance
- **FQE (Fitted Q Evaluation):** Learn Q-function under the target policy

### 7.5 Outputs

- Optimal policy π*: for each state, the recommended action
- Policy value estimate: expected DTP3 completion rate under π*
- Policy improvement over behaviour policy: Δ in DTP3 completion
- State-action heatmap: which actions are recommended for which child profiles

---

## 8. Stage 3 — Multi-Armed Bandit for Adaptive Allocation

### 8.1 Rationale

While the RL policy prescribes optimal individual-level actions, programme managers need community-level allocation decisions: given a fixed budget, which LGAs should receive which intervention packages? This is a contextual multi-armed bandit problem.

### 8.2 Formulation

```
CONTEXTUAL BANDIT:
  Context x:  LGA-level features (dropout rate, coverage, wealth,
              access, facility density, community composites)
  Arms K:     {SMS only, CHW only, SMS+CHW, facility recall, incentive}
  Reward:     Δ DTP3 coverage in LGA (estimated from RL policy simulation)
  Budget:     Total programme budget B (constraint)

  Algorithm: LinUCB (linear upper confidence bound)
  - Learns which arm (intervention package) works best in which context
  - Balances exploration (trying new allocations) vs exploitation
    (deploying what's known to work)
  - Respects budget constraint: allocates until B exhausted
```

### 8.3 Constraint Optimisation

```
MAXIMISE:  Σ_lga  E[DTP3_completion | x_lga, arm_lga]
SUBJECT TO: Σ_lga  cost(arm_lga) ≤ B
            arm_lga ∈ {SMS, CHW, SMS+CHW, recall, incentive}
```

Solved via linear programming relaxation with integer rounding, or via constrained Thompson Sampling.

---

## 9. Stage 4 — Microsimulation Validation

### 9.1 Design

Generate a synthetic population mirroring the NDHS 2024 DTP1-received sample. Simulate the vaccination schedule under different policies and compare outcomes.

### 9.2 Scenarios

| Scenario | Policy | Description |
|----------|--------|-------------|
| S0: Status quo | Behaviour policy | Observed intervention patterns from DHS |
| S1: Uniform SMS | a₁ for all at every step | SMS reminder to all children at each dose step |
| S2: Uniform CHW | a₂ for all at every step | CHW home visit for all children |
| S3: Risk-targeted | ML top 30% get a₂, rest get a₁ | Target CHW to highest-risk children (from Stage 1 XGBoost) |
| S4: RL-optimised | π* from Stage 2 | Sequential RL policy: different actions at different steps for different children |
| S5: Bandit-allocated | Stage 3 bandit | Community-level adaptive allocation |

### 9.3 Simulation Mechanics

```
FOR each synthetic child i (N = 10,000):
  Initialise: s₀ = (child features, DTP1 received, age = 6 weeks)

  FOR dose_step t in {DTP2_due, DTP3_due}:
    1. Select action a_t according to scenario policy
    2. Compute P(receive dose | s_t, a_t) from learned transition model
    3. Draw outcome: dose_received ~ Bernoulli(P)
    4. Compute reward: r_t
    5. Update state: s_{t+1}

  Record: DTP3 completed (yes/no), total cost, timeliness

Repeat 1,000 iterations for uncertainty.
```

### 9.4 Outcome Metrics

- DTP3 completion rate per scenario
- Incremental DTP3 completions vs status quo
- Total programme cost per scenario
- Cost per additional DTP3 completion (ICER)
- Equity: DTP3 completion ratio (poorest ÷ richest quintile)
- Timeliness: proportion completing DTP3 by 16 weeks
- Policy improvement: % gain of RL-optimised over best static policy

---

## 10. Stage 5 — Streamlit Dashboard

Seven interactive pages:

1. **Immunisation Cascade:** Bar chart showing DTP1→DTP2→DTP3 retention, filterable by zone, state, wealth, urban/rural
2. **Transition SHAP Explorer:** Separate SHAP plots for T1 and T2 dropout models — which predictors matter at each transition
3. **Timeliness Analysis:** Distribution of inter-dose intervals, identification of delayed children, delay accumulation patterns
4. **RL Policy Map:** Choropleth showing recommended action per LGA at each dose step; state-action heatmap
5. **Bandit Allocation:** Budget slider → optimal community-level allocation across LGAs with coverage projections
6. **Microsimulation Scenarios:** Side-by-side comparison of S0–S5, equity dashboard, cost-effectiveness plane
7. **Data Export:** Download cascade data, policy recommendations, and scenario results

---

## 11. Integration Across Components

```
INTEGRATION MAP
══════════════════════════════════════════════════════════════════════

  Stage 1 (Cascade + XGBoost)
    │
    ├──► Transition-specific dropout predictors ──► Dashboard (page 2)
    ├──► State space construction ─────────────────► Stage 2 (RL)
    ├──► Trajectory dataset D ─────────────────────► Stage 2 (RL)
    ├──► Cascade metrics ──────────────────────────► Dashboard (page 1)
    │
  Stage 2 (Offline RL)
    │
    ├──► Optimal policy π* ────────────────────────► Stage 4 (microsim S4)
    ├──► Q-function estimates ─────────────────────► Stage 3 (bandit rewards)
    ├──► Policy value estimates ───────────────────► Dashboard (page 4)
    │
  Stage 3 (Bandit)
    │
    ├──► LGA allocation ───────────────────────────► Stage 4 (microsim S5)
    ├──► Budget-optimal assignments ───────────────► Dashboard (page 5)
    │
  Stage 4 (Microsimulation)
    │
    ├──► Scenario comparison ──────────────────────► Dashboard (page 6)
    ├──► Cost-effectiveness ───────────────────────► Policy brief
```

---

## 12. Ethical Considerations

This study uses secondary analysis of anonymised, publicly available DHS data. No individual identifiers are present. The RL policy is learned offline and validated in simulation — no real-world deployment or human experimentation occurs. The study will be registered with the University of Warwick BSREC.

A specific ethical consideration for RL in health: the learned policy must not systematically disadvantage any population subgroup. We include an equity constraint in the microsimulation: the RL policy must not widen the DTP3 gap between the poorest and richest quintiles.

---

## 13. Limitations

1. **Observational data for RL:** The behaviour policy is inferred, not observed. We do not know what interventions (if any) were actually deployed to each child. The proxy inference from timeliness and covariate patterns is approximate.

2. **Card-confirmed dates only:** Inter-dose intervals can only be computed for children whose vaccinations were confirmed by card with dates (`h3 == 1`). Mother-reported vaccinations (`h3 == 2`) and marked-on-card without dates (`h3 == 3`) lack temporal information. This restricts the trajectory analysis to a subset.

3. **Cross-sectional data:** DHS captures a single point in time. We reconstruct trajectories from vaccination history, but we do not observe the decision process in real time. The RL framework treats the reconstructed trajectory as if it were a sequential process, which is an approximation.

4. **Action space simplification:** The five-action space (no intervention, SMS, CHW, recall, incentive) is a simplification. Real-world interventions are more nuanced and context-dependent.

5. **Off-policy evaluation uncertainty:** OPE methods (importance sampling, doubly robust) have high variance when the learned policy differs substantially from the behaviour policy.

---

## 14. Dissemination Plan

- **Primary manuscript:** Target journal — *Nature Machine Intelligence* or *The Lancet Digital Health*; secondary — *PLOS Digital Health* or *BMJ Global Health*
- **Data and code:** Full replication package on GitHub/Zenodo (CC-BY): Python RL pipeline (d3rlpy, stable-baselines3), XGBoost/SHAP, microsimulation, Streamlit dashboard
- **Policy brief:** For NPHCDA, Gavi, WHO AFRO — translating RL policy into operational guidance
- **Conference:** Machine Learning for Health (ML4H); GVIRF; Health Systems Research Symposium

---

## 15. Timeline

```
GANTT CHART (12-MONTH IMPLEMENTATION)
══════════════════════════════════════════════════════════════════════

  Activity                              Q1    Q2    Q3    Q4
  ────────────────────────────────────────────────────────────
  NDHS 2024 data access & extraction    ████
  Cascade construction + trajectory     ████
  Stage 1: Transition XGBoost + SHAP          ████
  Stage 2: MDP formulation + FQI/CQL         ████  ████
  Stage 2: Off-policy evaluation                    ████
  Stage 3: Bandit formulation                       ████
  Stage 4: Microsimulation development              ████
  Stage 4: Scenario runs + CEA                      ████  ██
  Streamlit dashboard                               ████  ██
  Sensitivity analyses                              ██    ████
  Manuscript drafting                                     ████
  Peer review & revision                                  ████
  ────────────────────────────────────────────────────────────
```

---

## 16. Team Roles

| Role | Responsibility |
|------|---------------|
| Principal Investigator (Ola Uthman) | Overall leadership, cascade analysis, manuscript writing |
| RL Specialist (TBC) | MDP formulation, FQI/CQL implementation, OPE |
| ML Engineer (TBC) | XGBoost/SHAP, state space construction, trajectory reconstruction |
| Health Economist (TBC) | Cost parameters, CEA, budget constraint optimisation |
| Nigerian Immunisation Expert (TBC) | Contextual validation, intervention feasibility, policy translation |
| Dashboard Developer (TBC) | Streamlit implementation |

---

## 17. References

1. Andersen RM. Revisiting the behavioral model and access to medical care: does it matter? *Journal of Health and Social Behavior*. 1995;36(1):1–10.
2. Sridhar S, Maleq N, Guillermet E, et al. A systematic literature review of missed opportunities for immunization in LMICs. *Vaccine*. 2014;32(51):6870–6879.
2. WHO/UNICEF. *Immunisation Agenda 2030*. Geneva: WHO; 2020.
3. Gavi. *Zero-Dose Learning Agenda*. Geneva: Gavi; 2022.
4. NPC Nigeria and ICF. *Nigeria DHS 2024*. Abuja/Rockville: NPC/ICF; 2025.
5. Levine E, Tsiatis AA, Schulte PJ. Dynamic treatment regimes. In: *Handbook of Missing Data Methodology*. Chapman & Hall/CRC; 2014.
6. Ernst D, Geurts P, Wehenkel L. Tree-based batch mode reinforcement learning. *JMLR*. 2005;6:503–556.
7. Kumar A, Zhou A, Tucker G, Levine S. Conservative Q-learning for offline reinforcement learning. *NeurIPS*. 2020.
8. Li L, Chu W, Langford J, Schapire RE. A contextual-bandit approach to personalized news article recommendation. *WWW*. 2010:661–670.
9. Chen T, Guestrin C. XGBoost: a scalable tree boosting system. *KDD*. 2016:785–794.
10. Lundberg SM, Lee SI. A unified approach to interpreting model predictions. *NeurIPS*. 2017;30.
11. NPHCDA. *NSIPSS 2018–2028*. Abuja: NPHCDA; 2018.
12. Sato Y, Takasaki Y. Offline reinforcement learning for public health: a tutorial. *Statistics in Medicine*. 2024;43(5):1012–1030.
13. ICF. *DHS Methodology*. Rockville: ICF; 2023.
14. NPC Nigeria and ICF. *Nigeria DHS 2018*. Abuja/Rockville: NPC/ICF; 2019.
