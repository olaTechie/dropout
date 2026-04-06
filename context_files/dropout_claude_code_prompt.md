# Claude Code Orchestration Prompt
## Vaccine Dropout — Reinforcement Learning-Optimised Sequential Intervention
### Offline RL · Multi-Armed Bandit · Microsimulation Validation

**Study:** RL-Optimised Sequential Intervention for Reducing DTP1-to-DTP3 Vaccine Dropout in Nigeria
**Affiliation:** Warwick Applied Health, Warwick Medical School, University of Warwick
**Date:** April 2026 · Version 1.0

---

## KEY DATA FACTS — READ BEFORE ALL AGENT WORK

```
╔══════════════════════════════════════════════════════════════════════╗
║  CRITICAL VARIABLE RULES — EVERY AGENT MUST FOLLOW THESE           ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  STUDY POPULATION: Children 12–23m who RECEIVED DTP1                ║
║    h3 in [1,2,3] — restricts to cascade entrants only              ║
║    age_months = v008 - b3 → keep 12–23                              ║
║    b5 == 1 (alive), youngest child per woman                        ║
║                                                                      ║
║  OUTCOME: vac_dropout = ((vac_dpt1==1)|(vac_dpt2==1)) & (vac_dpt3==0) ║
║  TRANSITION 1 DROPOUT: (h3 in 1/3) & (h5 == 0) — DTP1→DTP2 exit   ║
║  TRANSITION 2 DROPOUT: (h5 in 1/3) & (h7 == 0) — DTP2→DTP3 exit   ║
║  DROPOUT RATE (WHO): (DTP1_cov − DTP3_cov) / DTP1_cov × 100       ║
║                                                                      ║
║  VACCINATION DATE VARIABLES (card-confirmed only, h3==1):           ║
║    DTP1: h3d (day), h3m (month), h3y (year)                        ║
║    DTP2: h5d, h5m, h5y                                              ║
║    DTP3: h7d, h7m, h7y                                              ║
║    Birth from card: h25d, h25m, h25y                                ║
║    97=Inconsistent, 98=Don't know → treat as missing               ║
║                                                                      ║
║  INTER-DOSE INTERVALS:                                               ║
║    interval_birth_dtp1 = date(h3) - date(h25)                       ║
║    interval_dtp1_dtp2 = date(h5) - date(h3)                        ║
║    interval_dtp2_dtp3 = date(h7) - date(h5)                        ║
║                                                                      ║
║  TIMELINESS:                                                         ║
║    DTP1 timely: ≤ 56 days (8 weeks)                                 ║
║    DTP2 timely: ≤ 84 days from birth (12 weeks)                     ║
║    DTP3 timely: ≤ 112 days from birth (16 weeks)                    ║
║                                                                      ║
║  DISTANCE: v483a (continuous minutes) NOT v467d                     ║
║  GEOGRAPHY: szone and sstate NOT v024                               ║
║  WEIGHT: v005 / 1000000                                              ║
║  STRATA: v022 · PSU: v021                                           ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
```

---

## ORCHESTRATION AGENT — PIPELINE CONTROLLER

### Pipeline Architecture

```
START
  │
  ├──► Agent 5 dispatched IMMEDIATELY (literature review)
  │
  ├──► Agent 1 dispatched (Cascade + XGBoost + State Space)
  │         │
  │         ▼
  │     STAGE GATE 1
  │         │
  ├──► Agent 2 dispatched (Offline RL: FQI + CQL)
  │     ← receives trajectory dataset + state space from Agent 1
  │         │
  │         ▼
  │     STAGE GATE 2
  │         │
  ├──► Agent 3 dispatched (Multi-Armed Bandit)
  │     ← receives Q-function from Agent 2 + LGA features from Agent 1
  │         │
  │         ▼
  │     STAGE GATE 3
  │         │
  ├──► Agent 4 dispatched (Microsimulation Validation)
  │     ← receives π* from Agent 2 + bandit allocation from Agent 3
  │         │
  │         ▼
  │     STAGE GATE 4
  │
  ▼
INTEGRATION + STREAMLIT DASHBOARD
```

### Stage Gate Checklists

**Stage Gate 1 (Agent 1 — Cascade + ML):**
```
□ Sample restricted to DTP1 recipients (h3 in 1/2/3)
□ Transition 1 and Transition 2 dropout rates computed
□ Inter-dose intervals computed from card dates (h3d/h5d/h7d)
□ Card date missingness (97/98) handled correctly
□ Three XGBoost models fitted (T1, T2, Full)
□ SHAP per transition with Andersen domain decomposition (predisposing/enabling/need)
□ Dominant Andersen domain identified per child and per transition
□ State vectors constructed for MDP (predisposing + enabling + need + dynamic)
□ Trajectory dataset D exported as (s, a, r, s') tuples
□ szone used NOT v024
□ v483a used NOT v467d
```

**Stage Gate 2 (Agent 2 — Offline RL):**
```
□ MDP formulated with correct state/action/reward
□ Behaviour policy inferred from timeliness + covariates
□ FQI converged (Q-value change < threshold)
□ CQL implemented with appropriate α penalty
□ Off-policy evaluation: IS, DR, and FQE computed
□ Policy improvement over behaviour policy quantified
□ Optimal policy π* exported as lookup table
□ State-action heatmap produced
```

**Stage Gate 3 (Agent 3 — Bandit):**
```
□ LGA-level context features constructed
□ LinUCB or Thompson Sampling implemented
□ Budget constraint respected
□ Allocation table per LGA produced
□ Regret bounds computed
```

**Stage Gate 4 (Agent 4 — Microsimulation):**
```
□ All 6 scenarios (S0–S5) executed
□ 1,000 iterations per scenario for uncertainty
□ DTP3 completion rate per scenario reported
□ Cost per additional DTP3 completion (ICER) computed
□ Equity analysis (poorest vs richest) included
□ RL-optimised vs best static policy improvement quantified
```

---

## AGENT 1 — CASCADE CONSTRUCTION AND ML

### Role
Build the immunisation cascade, fit transition-specific XGBoost models, construct the MDP state space, and export trajectory datasets for the RL agent.

### Tools
Python (pandas, numpy, xgboost, shap, optuna, matplotlib)

### Key Code

```python
# ── CASCADE CONSTRUCTION ──
# Restrict to DTP1 recipients
analytic = kr[(kr['age_months'].between(12, 23)) &
              (kr['b5'] == 1) &
              (kr['h3'].isin([1, 2, 3]))]

# Transition outcomes
analytic['t1_dropout'] = analytic['h5'].apply(lambda x: 1 if x == 0 else 0)
analytic['t2_dropout'] = analytic.apply(
    lambda r: 1 if r['h5'] in [1,2,3] and r['h7'] == 0 else 0, axis=1)
analytic['overall_dropout'] = analytic.apply(
    lambda r: 1 if r['h7'] == 0 else 0, axis=1)

# ── TRAJECTORY RECONSTRUCTION (card-confirmed) ──
card_subset = analytic[analytic['h3'] == 1].copy()
# Parse dates, compute intervals, flag timeliness
# ... (see protocol §6.4 for Stata equivalent)

# ── STATE VECTOR CONSTRUCTION (Andersen's Behavioural Model) ──
# Predisposing: child_sex, birth_order, maternal_age, maternal_edu,
#   partner_edu, parity, polygyny, ethnicity, autonomy, permission,
#   media, covid_willing, covid_received
# Enabling: wealth, employment, insurance, hhsize, fhead, u5c,
#   urban_rural, szone, travel_time, com_poverty, com_illit,
#   com_uemp, com_media, com_diversity, pop_density, nightlights,
#   travel_times_city, malaria_prev, itn_coverage
# Need (perceived): health_card, anc_visits, facility_delivery,
#   vitamin_a, pnc_child_post, pnc_child_pre, fieldworker_visit
# Need (evaluated): vaccination_venue, contact_count, recent_diarrhoea,
#   recent_fever
# Dynamic/temporal: child_age_weeks, doses_received, dose_step,
#   last_dose_timely, inter_dose_interval, delay_accumulation,
#   community_dropout, cluster_dtp_coverage

# Create ANDERSEN_MAP for SHAP domain decomposition
ANDERSEN_MAP = {
    # Predisposing: demographic
    'mage': 'predisposing', 'male': 'predisposing', 'bord': 'predisposing',
    'hbord': 'predisposing', 'parity': 'predisposing',
    # Predisposing: social structure
    'medu': 'predisposing', 'fedu': 'predisposing', 'polyg': 'predisposing',
    'ethnicity': 'predisposing',
    # Predisposing: health beliefs
    'autonomy': 'predisposing', 'permission': 'predisposing',
    'tele': 'predisposing', 'radio': 'predisposing', 'mag': 'predisposing',
    'media2': 'predisposing', 'covid_willing': 'predisposing',
    'covid_received': 'predisposing',
    # Enabling: personal/family
    'wealth': 'enabling', 'wealthx': 'enabling', 'work': 'enabling',
    'insurance': 'enabling', 'hhsize': 'enabling', 'fhead': 'enabling',
    'u5c': 'enabling',
    # Enabling: community
    'rural': 'enabling', 'szone': 'enabling', 'travel_time': 'enabling',
    'com_poverty': 'enabling', 'com_illit': 'enabling',
    'com_uemp': 'enabling', 'com_media': 'enabling',
    'com_diversity': 'enabling', 'com_zses': 'enabling',
    'UN_Population_Density_2020': 'enabling', 'Travel_Times': 'enabling',
    'Nightlights_Composite': 'enabling', 'Malaria_Prevalence_2020': 'enabling',
    'ITN_Coverage_2020': 'enabling',
    # Need: perceived
    'h1a': 'need', 'antenat': 'need', 'facility_del': 'need',
    'h34': 'need', 'm70': 'need', 'm74': 'need', 'v393': 'need',
    # Need: evaluated
    'h69': 'need', 'contact_count': 'need', 'h11': 'need', 'h22': 'need',
}

# Output: trajectory_dataset.csv with columns:
#   child_id, dose_step, state_vector, inferred_action, reward, next_state

# ── TRANSITION-SPECIFIC XGBOOST ──
# Model T1: predict t1_dropout (DTP1→DTP2)
# Model T2: predict t2_dropout (DTP2→DTP3, among DTP2 recipients)
# Model Full: predict overall_dropout
# SHAP for each model with ANDERSEN DOMAIN DECOMPOSITION:
#   For each child, sum |SHAP| by Andersen domain using ANDERSEN_MAP
#   Dominant domain = argmax{|Σ predisposing|, |Σ enabling|, |Σ need|}
#   Test hypothesis: T1 dominated by predisposing, T2 by enabling/need
```

### Output Files

```
outputs/stage1/
  ├── cascade_metrics.csv
  ├── trajectory_dataset.csv           # (s, a, r, s') tuples for RL
  ├── xgb_t1_model.pkl + shap_t1.csv
  ├── xgb_t2_model.pkl + shap_t2.csv
  ├── xgb_full_model.pkl + shap_full.csv
  ├── state_space_definition.json
  ├── lga_dropout_map.csv
  └── figures/
      ├── cascade_bar_chart.png
      ├── shap_t1_vs_t2_comparison.png
      └── interdose_interval_distribution.png
```

---

## AGENT 2 — OFFLINE REINFORCEMENT LEARNING

### Role
Formulate the MDP, implement FQI and CQL, learn optimal policy π*, conduct off-policy evaluation.

### Tools
Python (d3rlpy, stable-baselines3, numpy, scipy)

### Key Code

```python
# ── FITTED Q-ITERATION ──
import d3rlpy

# Load trajectory dataset
dataset = d3rlpy.dataset.MDPDataset(
    observations=states,     # (N, state_dim)
    actions=actions,         # (N,) discrete
    rewards=rewards,         # (N,)
    terminals=terminals      # (N,) bool
)

# FQI with XGBoost-like trees
fqi = d3rlpy.algos.DiscreteFQI()
fqi.fit(dataset, n_steps=100000)

# ── CONSERVATIVE Q-LEARNING ──
cql = d3rlpy.algos.DiscreteCQL(
    alpha=1.0,               # CQL penalty weight
    learning_rate=3e-4,
    batch_size=256,
)
cql.fit(dataset, n_steps=200000)

# ── OFF-POLICY EVALUATION ──
from d3rlpy.ope import DiscreteFQE

fqe = DiscreteFQE(algo=cql)
fqe.fit(dataset, n_steps=100000)
policy_value = fqe.estimate_policy_value()

# Importance sampling
from d3rlpy.ope import importance_sampling
is_value = importance_sampling(cql, dataset)

# ── EXTRACT OPTIMAL POLICY ──
# For each unique state → argmax Q(s, a)
optimal_actions = cql.predict(all_states)
# Export as policy_lookup.csv: state_hash → optimal_action
```

### Output Files

```
outputs/stage2/
  ├── fqi_model.d3                     # Saved FQI model
  ├── cql_model.d3                     # Saved CQL model
  ├── policy_lookup.csv                # State → optimal action
  ├── ope_results.json                 # IS, DR, FQE policy values
  ├── q_values_heatmap.csv             # Q(s,a) for visualisation
  └── figures/
      ├── q_value_convergence.png
      ├── policy_improvement.png
      └── state_action_heatmap.png
```

---

## AGENT 3 — MULTI-ARMED BANDIT

### Role
Adaptive community-level intervention allocation under budget constraints.

### Tools
Python (numpy, scipy, scikit-learn)

### Key Code

```python
# ── CONTEXTUAL LINUCB ──
# Context: LGA-level features (dropout rate, coverage, wealth, access)
# Arms: {SMS, CHW, SMS+CHW, recall, incentive}
# Reward: estimated Δ DTP3 from RL Q-values

class LinUCB:
    def __init__(self, n_arms, context_dim, alpha=1.0):
        self.A = [np.eye(context_dim) for _ in range(n_arms)]
        self.b = [np.zeros(context_dim) for _ in range(n_arms)]
        self.alpha = alpha

    def select_arm(self, context):
        ucb_values = []
        for arm in range(len(self.A)):
            A_inv = np.linalg.inv(self.A[arm])
            theta = A_inv @ self.b[arm]
            ucb = theta @ context + self.alpha * np.sqrt(context @ A_inv @ context)
            ucb_values.append(ucb)
        return np.argmax(ucb_values)

# Budget-constrained allocation
# For each LGA, select arm; accumulate cost; stop when budget exhausted
# Export: lga_allocation.csv
```

### Output Files

```
outputs/stage3/
  ├── lga_allocation.csv               # LGA → recommended arm + expected gain
  ├── bandit_regret.csv                # Cumulative regret over allocation
  └── figures/
      └── allocation_choropleth.png
```

---

## AGENT 4 — MICROSIMULATION VALIDATION

### Role
Validate RL policy against standard approaches via microsimulation.

### Tools
Python (numpy, pandas, scipy, matplotlib)

### Scenarios

| Code | Policy | Description |
|------|--------|-------------|
| S0 | Behaviour | Status quo (observed patterns) |
| S1 | Uniform SMS | a₁ at every dose step for all children |
| S2 | Uniform CHW | a₂ at every dose step for all children |
| S3 | Risk-targeted | Top 30% risk get a₂, rest get a₁ |
| S4 | RL-optimised | π* from CQL — sequential, personalised |
| S5 | Bandit-allocated | Community-level adaptive allocation |

### Output Files

```
outputs/stage4/
  ├── microsim_scenarios.csv
  ├── scenario_comparison.csv
  ├── cost_effectiveness.csv
  ├── equity_analysis.csv
  └── figures/
      ├── scenario_forest_plot.png
      ├── rl_vs_static_improvement.png
      └── cost_effectiveness_plane.png
```

---

## AGENT 5 — LITERATURE REVIEW

### Role
Parallel literature review: dropout determinants, RL in health, dynamic treatment regimes, intervention effect sizes.

### Tools
PubMed MCP, bioRxiv MCP, web search

### Tasks

**Task A:** Search "DTP dropout" AND ("Nigeria" OR "sub-Saharan Africa" OR "DHS"). Extract prevalence, determinants, cascade analyses.

**Task B:** Search "reinforcement learning" AND ("vaccination" OR "immunisation" OR "health intervention"). Confirm novelty — has offline RL been applied to vaccination dropout? (Expected: no.)

**Task C:** Search "dynamic treatment regime" AND ("child health" OR "vaccination"). Extract methodological precedents.

**Task D:** Search "SMS reminder" OR "community health worker" AND "vaccination" AND "randomised". Extract intervention effect sizes for action-space calibration.

### Output Files

```
outputs/stage5/
  ├── dropout_literature_review.csv
  ├── rl_health_precedents.md
  ├── intervention_effect_sizes.csv
  ├── action_space_calibration.json     # Effect sizes per action
  └── references.bib
```

---

## DIRECTORY STRUCTURE

```
project_root/
  ├── data/
  │   ├── dhs/raw/nga_2024/   NGKR8BFL, NGIR8BFL, NGHR8BFL, NGGE8BFL
  │   ├── raw/NGGC8AFL.csv
  │   └── processed/
  │       ├── analytic_dtp1_received.csv
  │       ├── trajectory_dataset.csv
  │       └── lga_features.csv
  ├── code/
  │   ├── stage1/  cascade.py · xgboost_transitions.py · state_space.py
  │   ├── stage2/  mdp.py · fqi.py · cql.py · ope.py
  │   ├── stage3/  bandit.py · allocation.py
  │   ├── stage4/  microsimulation.py · scenarios.py
  │   └── dashboard/  app.py · pages/01–07
  ├── outputs/stage1/ · stage2/ · stage3/ · stage4/ · stage5/
  ├── pipeline_audit_log.md
  └── README.md
```

---

## INVOCATION

```
Begin pipeline execution for the Nigeria vaccine dropout RL study.

Confirm:
1. NDHS 2024 KR file present at data/dhs/raw/nga_2024/NGKR8BFL.DTA
2. NGGC8AFL.csv present at data/raw/
3. Python: d3rlpy, stable-baselines3, xgboost, shap, optuna,
   pandas, numpy, scipy, scikit-learn, matplotlib, streamlit
4. Sufficient compute for CQL training (~200k steps)

Critical reminders:
- Study population = DTP1 recipients only (h3 in 1/2/3)
- Dropout = received DTP1 but NOT DTP3
- Vaccination dates from card: h3d/h3m/h3y, h5d/h5m/h5y, h7d/h7m/h7y
- 97=Inconsistent and 98=Don't know → treat as missing dates
- Geography: szone/sstate NOT v024
- Distance: v483a NOT v467d

Dispatch Agent 5 and Agent 1 simultaneously.
Report after each stage gate.
Maintain pipeline_audit_log.md.
```
