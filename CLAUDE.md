# Nigeria Vaccine Dropout RL Study

## Project Overview
RL-Optimised Sequential Intervention for Reducing DTP1-to-DTP3 Vaccine Dropout
Warwick Applied Health, Warwick Medical School, University of Warwick

## Pipeline Architecture
Sequential Agent Teams pipeline:
1. Literature Reviewer → 2. EDA + Cascade + ML → 3. RL + Bandit + Microsim → 4. Dashboard

## CRITICAL VARIABLE RULES — ALL AGENTS MUST FOLLOW

### Study Population
- Children 12–23 months who RECEIVED DTP1
- h3 in [1, 2, 3] — restricts to cascade entrants only
- age_months = v008 - b3 → keep 12–23
- b5 == 1 (alive), youngest child per woman
- This is a RETENTION analysis, not an access analysis

### Outcome Definitions
- vac_dropout = ((vac_dpt1==1) | (vac_dpt2==1)) & (vac_dpt3==0)
- T1 dropout: (h3 in 1/3) & (h5 == 0) — DTP1→DTP2 exit
- T2 dropout: (h5 in 1/3) & (h7 == 0) — DTP2→DTP3 exit
- Dropout rate (WHO): (DTP1_cov − DTP3_cov) / DTP1_cov × 100

### Vaccination Date Variables (card-confirmed only, h3==1)
- DTP1: h3d (day), h3m (month), h3y (year)
- DTP2: h5d, h5m, h5y
- DTP3: h7d, h7m, h7y
- Birth from card: h25d, h25m, h25y
- 97 = Inconsistent, 98 = Don't know → treat as missing

### Inter-Dose Intervals
- interval_birth_dtp1 = date(h3) - date(h25)
- interval_dtp1_dtp2 = date(h5) - date(h3)
- interval_dtp2_dtp3 = date(h7) - date(h5)

### Timeliness Thresholds
- DTP1 timely: ≤ 56 days (8 weeks) from birth
- DTP2 timely: ≤ 84 days from birth (12 weeks)
- DTP3 timely: ≤ 112 days from birth (16 weeks)

### Geography and Weights
- Geography: szone and sstate — NOT v024
- Distance to facility: v483a (continuous minutes) — NOT v467d
- Sample weight: v005 / 1000000
- Strata: v022 · PSU: v021

### Andersen's Behavioural Model Mapping
Every predictor belongs to one Andersen domain. Use this for SHAP decomposition.

Predisposing (demographic): mage/v012, male/b4, bord, hbord, parity/v201
Predisposing (social structure): medu/v106, fedu/v701, polyg/v505, ethnicity/v131
Predisposing (health beliefs): autonomy/v743a, permission/v467b, tele/v159,
  radio/v158, mag/v157, media2, covid_willing/s1112s, covid_received/s1112p

Enabling (personal/family): wealth/v190, wealthx/v191, work/v714, insurance/v481,
  hhsize/v136, fhead/v151, u5c/v137
Enabling (community): rural/v025, szone, travel_time/v483a, com_poverty, com_illit,
  com_uemp, com_media, com_diversity, com_zses
Enabling (geospatial): UN_Population_Density_2020, Travel_Times,
  Nightlights_Composite, Malaria_Prevalence_2020, ITN_Coverage_2020

Need (perceived): h1a, antenat/m14, facility_del/m15, h34, m70, m74, v393
Need (evaluated): h69, contact_count, h11, h22

Dynamic/temporal: child_age_weeks, doses_received, dose_step, last_dose_timely,
  inter_dose_interval, delay_accumulation, community_dropout, cluster_dtp_coverage

### Action Space
- a₀: No intervention (₦0)
- a₁: SMS reminder (₦50, +5–10% completion)
- a₂: CHW home visit (₦500, +15–25% completion)
- a₃: Facility recall + defaulter tracing (₦1,500, +20–30% completion)
- a₄: Conditional incentive (₦800, +10–20% completion)
Effect sizes to be updated by Literature Reviewer agent.

### Behaviour Policy Inference Rules
DHS does not record interventions. Infer proxy actions from observed patterns:
- Next dose ON TIME (≤ 2 weeks of schedule) → a₁ or a₂ (effective intervention)
- Next dose LATE (> 2 weeks delayed) → a₀ or a₁ (weak/no intervention)
- Next dose NOT received → a₀ (no effective intervention)
- Refinements: fieldworker visited (v393==1) → more likely a₂;
  card present (h1a≥1) → more likely a₁; campaign vaccination (h69==41) → more likely a₃

### Reward Function
R(s, a, s') = +1.0 (DTP3 completed) + 0.3 (next dose received) − λ × cost(a)
Default λ = 0.001

### Data File Paths
- DHS KR: data/raw/dhs/nga_2024/NGKR8BFL.DTA
- Geospatial: data/raw/geospatial/NGGC8AFL.csv
- Processed outputs: data/processed/

### Handoff Protocol
Each agent writes a handoff file to handoffs/ before completing:
- What was produced (file list with descriptions)
- Stage gate checklist (what passed/failed)
- What the next agent should read first
- Any parameter updates or warnings

### Quality Standards
- All code must include survey weight application (v005/1e6)
- All models must use v022 as strata and v021 as PSU
- All maps must use szone/sstate geography
- All XGBoost models must include calibration curves + Brier scores
- All figures must be publication-quality (300 DPI, PDF + PNG)
- Pipeline audit log updated after each stage: docs/pipeline_audit_log.md
