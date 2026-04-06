# Agent Teams Scaffold Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform the current project directory into a git-tracked Agent Teams repo with CLAUDE.md, 4 agent definitions, full directory structure, and archived context files.

**Architecture:** Initialize git in the current working directory (`03_dropout`). Create all directories and files per the design spec. Move existing context files to `docs/reference/`. The old monolithic prompt is archived alongside the other reference docs.

**Tech Stack:** Git, Claude Code Agent Teams, Markdown, JSON

**Working directory:** `/Users/uthlekan/Library/CloudStorage/Dropbox/00Todo/00_ToReview/vacSeries/03_dropout`

---

### Task 1: Initialize Git and Create Directory Structure

**Files:**
- Create: `.gitignore`
- Create: `README.md`
- Create: all directories with `.gitkeep` placeholders

- [ ] **Step 1: Initialize git repo**

Run: `git init`
Expected: `Initialized empty Git repository in ...`

- [ ] **Step 2: Create `.gitignore`**

Create file `.gitignore`:

```
# DHS data — cannot be redistributed
data/raw/

# Large model files
outputs/stage1/*.pkl
outputs/stage2/*.d3

# Python
__pycache__/
*.pyc
.venv/
*.egg-info/

# EDA reports (large HTML)
outputs/stage0/*.html

# OS
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/
```

- [ ] **Step 3: Create full directory tree with `.gitkeep` files**

Run:
```bash
mkdir -p .claude/agents
mkdir -p data/raw/dhs/nga_2024
mkdir -p data/raw/geospatial
mkdir -p data/processed
mkdir -p code/stage0_eda
mkdir -p code/stage1_cascade_ml
mkdir -p code/stage2_rl
mkdir -p code/stage3_bandit_microsim
mkdir -p code/stage5_dashboard/pages
mkdir -p outputs/stage0
mkdir -p outputs/stage1/figures
mkdir -p outputs/stage2/figures
mkdir -p outputs/stage3/figures
mkdir -p outputs/literature
mkdir -p outputs/stage5_dashboard
mkdir -p handoffs
mkdir -p docs/reference
```

Then add `.gitkeep` to empty directories that need tracking:

```bash
for dir in data/processed code/stage0_eda code/stage1_cascade_ml code/stage2_rl code/stage3_bandit_microsim code/stage5_dashboard/pages outputs/stage0 outputs/stage1/figures outputs/stage2/figures outputs/stage3/figures outputs/literature outputs/stage5_dashboard handoffs; do
  touch "$dir/.gitkeep"
done
```

- [ ] **Step 4: Create `README.md`**

Create file `README.md`:

```markdown
# Nigeria Vaccine Dropout RL Study

**RL-Optimised Sequential Intervention for Reducing DTP1-to-DTP3 Vaccine Dropout in Nigeria**

Warwick Applied Health, Warwick Medical School, University of Warwick

## Overview

This project applies offline reinforcement learning to learn optimal sequential intervention policies for reducing DTP1-to-DTP3 vaccine dropout in Nigeria, using the Nigeria Demographic and Health Survey 2024.

## Pipeline

Sequential Agent Teams pipeline powered by Claude Code:

1. **Literature Reviewer** — searches academic literature for dropout determinants, RL precedents, intervention effect sizes, ML validation practices
2. **EDA + Cascade + ML** — exploratory data analysis, immunisation cascade construction, transition-specific XGBoost with SHAP/Andersen decomposition, MDP state space construction
3. **RL + Bandit + Microsimulation** — offline RL (FQI + CQL), multi-armed bandit allocation, microsimulation validation across 6 scenarios
4. **Dashboard Integration** — Streamlit dashboard with 8 pages, pipeline integration report

## Data Requirements

- NDHS 2024 KR file: `data/raw/dhs/nga_2024/NGKR8BFL.DTA`
- DHS Geospatial Covariates: `data/raw/geospatial/NGGC8AFL.csv`

Data files are not included in this repository (DHS licence restrictions). Place them in the paths above before running the pipeline.

## Running the Pipeline

1. Ensure Claude Code v2.1.32+ is installed
2. Place DHS data files in `data/raw/`
3. Open Claude Code in this directory
4. Paste the launch prompt from `docs/reference/launch_prompt.txt`

## Repository Structure

See `CLAUDE.md` for domain rules and variable definitions.
See `.claude/agents/` for agent role definitions.
See `handoffs/` for inter-agent contracts.

## Licence

Code: MIT. Data: Subject to DHS licence terms.
```

- [ ] **Step 5: Verify directory structure**

Run: `find . -type d | grep -v '.git/' | grep -v '__pycache__' | grep -v '.DS_Store' | sort`

Expected: all directories from the spec are present.

- [ ] **Step 6: Commit**

```bash
git add .gitignore README.md
git add */.gitkeep */*/.gitkeep */*/*/.gitkeep 2>/dev/null; true
git commit -m "chore: initialize repo with directory structure and gitignore"
```

---

### Task 2: Create CLAUDE.md

**Files:**
- Create: `CLAUDE.md`

- [ ] **Step 1: Create `CLAUDE.md`**

Create file `CLAUDE.md`:

```markdown
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
```

- [ ] **Step 2: Verify CLAUDE.md contains all required sections**

Run: `grep -c "^###" CLAUDE.md`
Expected: 14 (Study Population, Outcome Definitions, Vaccination Date Variables, Inter-Dose Intervals, Timeliness Thresholds, Geography and Weights, Andersen's Behavioural Model Mapping, Action Space, Behaviour Policy Inference Rules, Reward Function, Data File Paths, Handoff Protocol, Quality Standards — plus one `##` section header)

- [ ] **Step 3: Commit**

```bash
git add CLAUDE.md
git commit -m "feat: add CLAUDE.md with all domain rules and variable definitions"
```

---

### Task 3: Create Agent Definition — Literature Reviewer

**Files:**
- Create: `.claude/agents/literature-reviewer.md`

- [ ] **Step 1: Create `.claude/agents/literature-reviewer.md`**

Create file `.claude/agents/literature-reviewer.md`:

```markdown
---
name: literature-reviewer
description: Searches academic literature for dropout determinants, RL in health, intervention effect sizes, and latest ML validation practices
model: opus
tools:
  - Read
  - Write
  - Bash
  - Grep
  - Glob
  - WebSearch
  - WebFetch
  - mcp__claude_ai_bioRxiv__*
  - mcp__plugin_pubmed_PubMed__*
  - mcp__claude_ai_Scholar_Gateway__*
---

# Literature Reviewer

You are the first agent in a sequential pipeline. Your findings inform ALL downstream agents.

## Tasks

### Task A: Dropout Determinants
Search "DTP dropout" AND ("Nigeria" OR "sub-Saharan Africa" OR "DHS").
Extract: prevalence rates, determinants, cascade analyses, Andersen-model applications.

### Task B: RL in Health — Novelty Check
Search "reinforcement learning" AND ("vaccination" OR "immunisation" OR "health intervention").
Confirm novelty: has offline RL been applied to vaccination dropout?
Search "dynamic treatment regime" AND ("child health" OR "vaccination").
Extract methodological precedents.

### Task C: Intervention Effect Sizes
Search "SMS reminder" OR "community health worker" AND "vaccination" AND "randomised".
Extract effect sizes per action for action-space calibration.
UPDATE the effect sizes in outputs/literature/action_space_calibration.json.

### Task D: Latest ML Validation Practices
Search for current best practices in:
- XGBoost model validation (calibration curves, Brier scores, DeLong test)
- Offline RL evaluation metrics (beyond IS/DR/FQE)
- SHAP interpretation standards
Write recommendations to outputs/literature/ml_validation_recommendations.md.

## Outputs
Write all outputs to outputs/literature/:
- dropout_literature_review.csv
- rl_health_precedents.md
- intervention_effect_sizes.csv
- action_space_calibration.json
- ml_validation_recommendations.md
- references.bib

## Handoff
Write handoffs/lit_to_eda.md with:
- Updated effect sizes for action space (if different from CLAUDE.md defaults)
- Recommended validation techniques for downstream ML agents
- Key references the EDA agent should cite
- Any parameter updates discovered
```

- [ ] **Step 2: Commit**

```bash
git add .claude/agents/literature-reviewer.md
git commit -m "feat: add literature-reviewer agent definition"
```

---

### Task 4: Create Agent Definition — EDA + Cascade + ML

**Files:**
- Create: `.claude/agents/eda-cascade-ml.md`

- [ ] **Step 1: Create `.claude/agents/eda-cascade-ml.md`**

Create file `.claude/agents/eda-cascade-ml.md`:

```markdown
---
name: eda-cascade-ml
description: Runs EDA, builds immunisation cascade, fits transition-specific XGBoost models, constructs MDP state space, exports trajectories
model: opus
tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
---

# EDA + Cascade Construction + ML Agent

Read handoffs/lit_to_eda.md FIRST for updated parameters and validation recommendations.

## Phase 1: Exploratory Data Analysis (Stage 0)

Adapt the following EDA suite to the dropout study analytic sample:

### 1.1 Data Profiling
- Generate ydata-profiling (pandas profiler) HTML report on the analytic sample
- Generate sweetviz comparison report (dropout vs completer groups)

### 1.2 Descriptive Statistics (TableOne)
- Create TableOne grouped by vac_dropout (0/1)
- Include all Andersen-domain predictors from CLAUDE.md
- Include p-values and statistical test names
- Export CSV and HTML

### 1.3 State-Level Prevalence
- Compute dropout prevalence by state (sstate)
- Horizontal bar chart sorted by prevalence
- Choropleth map using GADM Nigeria shapefile

### 1.4 Funnel Plot
- Funnel plot of state-level dropout rates with 95% and 99.7% CIs

### 1.5 Hot/Cold Spot Analysis
- Local Moran's I on state-level dropout prevalence
- Cluster map: High-High, Low-Low, Low-High, High-Low

### 1.6 Zonal Analysis
- Dropout rates by geopolitical zone (szone)
- Wealth gradient analysis by zone

### EDA Outputs → outputs/stage0/
- dropout_profile_report.html
- dropout_sweetviz_report.html
- descriptive_statistics_table.csv / .html
- dropout_prevalence_by_state.pdf
- dropout_choropleth_map.pdf
- dropout_funnel_plot.pdf
- local_moran_clusters_map.pdf
- zonal_analysis.pdf

## Phase 2: Cascade Construction (Stage 1)

### 2.1 Cascade Metrics
- DTP1/DTP2/DTP3 coverage nationally and by szone
- Transition retention rates and WHO dropout rate
- Timeliness cascade (card-confirmed subset)

### 2.2 Trajectory Reconstruction
- Parse card dates (h3d/h3m/h3y, h5d/h5m/h5y, h7d/h7m/h7y)
- Handle missing date codes (97/98 → missing)
- Compute inter-dose intervals and timeliness flags
- Compute delay accumulation

### 2.3 Community-Level Variables
- Construct community composites (com_poverty, com_illit, com_uemp, com_media, com_diversity)
- Merge geospatial covariates from NGGC8AFL.csv via cluster ID (v001)

## Phase 3: Transition-Specific XGBoost (Stage 1)

### 3.1 Three Models
- Model T1: predict t1_dropout (DTP1→DTP2)
- Model T2: predict t2_dropout (DTP2→DTP3, among DTP2 recipients)
- Model Full: predict overall_dropout
- Hyperparameter tuning via Optuna (200 trials each)
- Apply validation techniques from literature reviewer recommendations

### 3.2 SHAP with Andersen Domain Decomposition
- SHAP values per model
- Sum |SHAP| by Andersen domain using the mapping in CLAUDE.md
- Dominant domain = argmax{|Σ predisposing|, |Σ enabling|, |Σ need|}
- Test hypothesis: T1 dominated by predisposing, T2 by enabling/need

### 3.3 State Space + Trajectory Export
- Construct state vectors per CLAUDE.md dynamic/temporal features
- Export trajectory_dataset.csv: child_id, dose_step, state_vector, inferred_action, reward, next_state
- Export state_space_definition.json

## Stage Gate Checklist
Before writing handoff, verify:
- [ ] Sample restricted to DTP1 recipients (h3 in 1/2/3)
- [ ] EDA reports generated and saved
- [ ] Transition dropout rates computed correctly
- [ ] Inter-dose intervals from card dates, missingness handled (97/98)
- [ ] Three XGBoost models fitted with calibration curves + Brier scores
- [ ] SHAP per transition with Andersen domain decomposition
- [ ] State vectors constructed
- [ ] Trajectory dataset exported as (s, a, r, s') tuples
- [ ] szone used NOT v024
- [ ] v483a used NOT v467d
- [ ] Survey weights applied

## Outputs
- outputs/stage0/ (all EDA outputs)
- outputs/stage1/ (cascade_metrics.csv, trajectory_dataset.csv, xgb models, SHAP, figures)
- data/processed/analytic_dtp1_received.csv
- data/processed/trajectory_dataset.csv

## Handoff
Write handoffs/eda_to_rl.md with:
- Trajectory dataset location and schema
- State space definition summary
- Key EDA findings that affect RL formulation
- Andersen domain decomposition results
- Any data quality warnings
```

- [ ] **Step 2: Commit**

```bash
git add .claude/agents/eda-cascade-ml.md
git commit -m "feat: add eda-cascade-ml agent definition"
```

---

### Task 5: Create Agent Definition — RL + Bandit + Microsimulation

**Files:**
- Create: `.claude/agents/rl-bandit-microsim.md`

- [ ] **Step 1: Create `.claude/agents/rl-bandit-microsim.md`**

Create file `.claude/agents/rl-bandit-microsim.md`:

```markdown
---
name: rl-bandit-microsim
description: Implements offline RL (FQI + CQL), multi-armed bandit allocation, and microsimulation validation
model: opus
tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
---

# RL + Bandit + Microsimulation Agent

Read handoffs/eda_to_rl.md FIRST. Load trajectory dataset and state space from Stage 1.

## Phase 1: Offline Reinforcement Learning (Stage 2)

### 1.1 MDP Formulation
- States: state vectors from Stage 1
- Actions: 5-action space per CLAUDE.md
- Transitions: learned from trajectory dataset
- Reward: per CLAUDE.md reward function
- Discount γ = 0.95

### 1.2 Behaviour Policy Inference
- Infer actions from timeliness patterns per CLAUDE.md Behaviour Policy Inference Rules
- Validate inferred action distribution is plausible

### 1.3 Fitted Q-Iteration
- d3rlpy MDPDataset from trajectory data
- FQI with tree-based function approximator
- Convergence check: ΔQ < 0.001

### 1.4 Conservative Q-Learning
- CQL with α=1.0 (sensitivity: 0.1–5.0)
- Training: 200k steps (sensitivity: 100k–500k)
- Learning rate: 3e-4

### 1.5 Off-Policy Evaluation
- Importance Sampling, Doubly Robust, FQE
- Apply any additional OPE methods recommended by literature reviewer

### 1.6 Policy Extraction
- For each unique state → argmax Q(s, a)
- Export policy_lookup.csv

## Phase 2: Multi-Armed Bandit (Stage 3)

### 2.1 LGA Context Features
- Aggregate child-level features to LGA level
- Merge with geospatial covariates

### 2.2 LinUCB Implementation
- Context: LGA features (~15 dimensions)
- Arms: 5 actions from CLAUDE.md
- Reward: estimated Δ DTP3 from Q-values
- α = 1.0 (sensitivity: 0.5–2.0)

### 2.3 Budget-Constrained Allocation
- National budget: ₦500M (sensitivity: ₦250M–₦1B)
- Per-arm costs from CLAUDE.md
- Export lga_allocation.csv

## Phase 3: Microsimulation Validation (Stage 4)

### 3.1 Synthetic Population
- N = 10,000 mirroring NDHS 2024 DTP1-received sample
- 1,000 bootstrap iterations

### 3.2 Six Scenarios
- S0: Status quo (behaviour policy)
- S1: Uniform SMS (a₁ all)
- S2: Uniform CHW (a₂ all)
- S3: Risk-targeted (top 30% risk → a₂, rest → a₁)
- S4: RL-optimised (π* from CQL)
- S5: Bandit-allocated (community-level)

### 3.3 Outcome Metrics
- DTP3 completion rate per scenario
- Cost per additional DTP3 completion (ICER)
- Equity: poorest vs richest quintile gap
- RL must NOT widen the equity gap

## Stage Gate Checklist
- [ ] FQI converged
- [ ] CQL trained, Q-values sensible
- [ ] OPE: IS, DR, FQE computed
- [ ] Policy improvement over behaviour quantified
- [ ] LinUCB allocation respects budget
- [ ] All 6 scenarios executed
- [ ] Equity constraint checked
- [ ] Cost-effectiveness computed

## Outputs
- outputs/stage2/ (models, policy_lookup, OPE, figures)
- outputs/stage3/ (lga_allocation, bandit_regret, microsim results, figures)

## Handoff
Write handoffs/rl_to_dashboard.md with:
- Policy lookup table location
- Microsim scenario results summary
- Key findings: which scenario wins, equity impact
- All figure locations for dashboard integration
```

- [ ] **Step 2: Commit**

```bash
git add .claude/agents/rl-bandit-microsim.md
git commit -m "feat: add rl-bandit-microsim agent definition"
```

---

### Task 6: Create Agent Definition — Dashboard Integration

**Files:**
- Create: `.claude/agents/dashboard-integration.md`

- [ ] **Step 1: Create `.claude/agents/dashboard-integration.md`**

Create file `.claude/agents/dashboard-integration.md`:

```markdown
---
name: dashboard-integration
description: Builds Streamlit dashboard from all upstream outputs and produces final integration report
model: opus
tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
---

# Dashboard + Integration Agent

Read ALL handoff files in handoffs/ FIRST. Then read outputs from all stages.

## Streamlit Dashboard (8 pages)

### Page 1: Immunisation Cascade
- Bar chart: DTP1→DTP2→DTP3 retention
- Filterable by zone, state, wealth, urban/rural
- Source: outputs/stage1/cascade_metrics.csv

### Page 2: EDA Explorer
- Embed profiling report link
- TableOne display
- Choropleth and cluster maps
- Source: outputs/stage0/

### Page 3: Transition SHAP Explorer
- SHAP plots for T1 and T2 models
- Andersen domain decomposition comparison
- Source: outputs/stage1/shap_*.csv

### Page 4: Timeliness Analysis
- Inter-dose interval distributions
- Delay accumulation patterns
- Source: outputs/stage1/

### Page 5: RL Policy Map
- Choropleth: recommended action per LGA at each dose step
- State-action heatmap
- Source: outputs/stage2/policy_lookup.csv, q_values_heatmap.csv

### Page 6: Bandit Allocation
- Budget slider → LGA allocation visualization
- Coverage projections
- Source: outputs/stage3/lga_allocation.csv

### Page 7: Microsimulation Scenarios
- Side-by-side S0–S5 comparison
- Equity dashboard
- Cost-effectiveness plane
- Source: outputs/stage3/

### Page 8: Data Export
- Download cascade data, policy recommendations, scenario results

## Integration Report
- Compile docs/pipeline_audit_log.md from all stage gate results
- Verify all outputs exist and are internally consistent
- Flag any cross-stage inconsistencies

## Code Location
- code/stage5_dashboard/app.py (main Streamlit app)
- code/stage5_dashboard/pages/ (one file per page)
```

- [ ] **Step 2: Commit**

```bash
git add .claude/agents/dashboard-integration.md
git commit -m "feat: add dashboard-integration agent definition"
```

---

### Task 7: Create Settings, Audit Log, and Launch Prompt

**Files:**
- Create: `.claude/settings.json`
- Create: `docs/pipeline_audit_log.md`
- Create: `docs/reference/launch_prompt.txt`

- [ ] **Step 1: Create `.claude/settings.json`**

Create file `.claude/settings.json`:

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

- [ ] **Step 2: Create `docs/pipeline_audit_log.md`**

Create file `docs/pipeline_audit_log.md`:

```markdown
# Pipeline Audit Log

## Literature Review (Agent 1)
- Status: pending
- Started:
- Completed:
- Handoff: handoffs/lit_to_eda.md
- Notes:

## EDA + Cascade + ML (Agent 2)
- Status: pending
- Started:
- Completed:
- Handoff: handoffs/eda_to_rl.md
- Notes:

## RL + Bandit + Microsim (Agent 3)
- Status: pending
- Started:
- Completed:
- Handoff: handoffs/rl_to_dashboard.md
- Notes:

## Dashboard + Integration (Agent 4)
- Status: pending
- Started:
- Completed:
- Notes:
```

- [ ] **Step 3: Create `docs/reference/launch_prompt.txt`**

Create file `docs/reference/launch_prompt.txt`:

```
Create an agent team for the Nigeria vaccine dropout RL pipeline.
Sequential execution — each agent completes before the next starts.

Spawn teammates in this order:
1. "literature-reviewer" using the literature-reviewer agent type
   — must complete and write handoffs/lit_to_eda.md before agent 2 starts
2. "eda-cascade-ml" using the eda-cascade-ml agent type
   — must complete and write handoffs/eda_to_rl.md before agent 3 starts
3. "rl-bandit-microsim" using the rl-bandit-microsim agent type
   — must complete and write handoffs/rl_to_dashboard.md before agent 4 starts
4. "dashboard-integration" using the dashboard-integration agent type

Use task dependencies (blockedBy) to enforce this sequence.
Require plan approval for agents 2 and 3 before they make changes.
All agents use Opus.

Before dispatching each agent, verify:
- Previous agent's handoff file exists
- Previous agent's stage gate checklist is complete
- Update docs/pipeline_audit_log.md with stage completion status

Data files are at:
- data/raw/dhs/nga_2024/NGKR8BFL.DTA
- data/raw/geospatial/NGGC8AFL.csv
```

- [ ] **Step 4: Commit**

```bash
git add .claude/settings.json docs/pipeline_audit_log.md docs/reference/launch_prompt.txt
git commit -m "feat: add settings, audit log template, and launch prompt"
```

---

### Task 8: Archive Context Files and Sample EDA

**Files:**
- Move: `context_files/dropout_study_protocol.md` → `docs/reference/dropout_study_protocol.md`
- Move: `context_files/dropout_variables_parameters.md` → `docs/reference/dropout_variables_parameters.md`
- Move: `context_files/dropout_concept_note.docx` → `docs/reference/dropout_concept_note.docx`
- Move: `context_files/dropout_claude_code_prompt.md` → `docs/reference/dropout_claude_code_prompt_ORIGINAL.md`
- Move: `context_files/sample EDA.py` → `docs/reference/sample_eda_anemia.py`

- [ ] **Step 1: Move all context files to docs/reference/**

Run:
```bash
cp context_files/dropout_study_protocol.md docs/reference/dropout_study_protocol.md
cp context_files/dropout_variables_parameters.md docs/reference/dropout_variables_parameters.md
cp context_files/dropout_concept_note.docx docs/reference/dropout_concept_note.docx
cp context_files/dropout_claude_code_prompt.md docs/reference/dropout_claude_code_prompt_ORIGINAL.md
cp "context_files/sample EDA.py" docs/reference/sample_eda_anemia.py
```

Note: Using `cp` not `mv` so originals are preserved until you verify. You can delete `context_files/` later if desired.

- [ ] **Step 2: Verify all files copied**

Run: `ls -la docs/reference/`

Expected: 6 files (launch_prompt.txt from Task 7 + 5 files just copied).

- [ ] **Step 3: Commit**

```bash
git add docs/reference/dropout_study_protocol.md docs/reference/dropout_variables_parameters.md docs/reference/dropout_concept_note.docx docs/reference/dropout_claude_code_prompt_ORIGINAL.md docs/reference/sample_eda_anemia.py
git commit -m "docs: archive original context files and sample EDA to docs/reference"
```

---

### Task 9: Move Design Spec and Plan Into Repo

**Files:**
- The spec and plan already exist under `docs/superpowers/` — commit them.

- [ ] **Step 1: Add spec and plan to git**

Run:
```bash
git add docs/superpowers/specs/2026-04-06-agent-teams-migration-design.md
git add docs/superpowers/plans/2026-04-06-agent-teams-scaffold.md
git commit -m "docs: add design spec and implementation plan"
```

---

### Task 10: Final Verification

- [ ] **Step 1: Verify repo structure matches spec**

Run:
```bash
echo "=== Directory structure ===" && find . -type d | grep -v '.git/' | grep -v '__pycache__' | grep -v '.DS_Store' | sort
echo ""
echo "=== Key files ===" && echo "CLAUDE.md:" && test -f CLAUDE.md && echo "  EXISTS" || echo "  MISSING"
echo ".claude/settings.json:" && test -f .claude/settings.json && echo "  EXISTS" || echo "  MISSING"
echo ".claude/agents/literature-reviewer.md:" && test -f .claude/agents/literature-reviewer.md && echo "  EXISTS" || echo "  MISSING"
echo ".claude/agents/eda-cascade-ml.md:" && test -f .claude/agents/eda-cascade-ml.md && echo "  EXISTS" || echo "  MISSING"
echo ".claude/agents/rl-bandit-microsim.md:" && test -f .claude/agents/rl-bandit-microsim.md && echo "  EXISTS" || echo "  MISSING"
echo ".claude/agents/dashboard-integration.md:" && test -f .claude/agents/dashboard-integration.md && echo "  EXISTS" || echo "  MISSING"
echo ".gitignore:" && test -f .gitignore && echo "  EXISTS" || echo "  MISSING"
echo "README.md:" && test -f README.md && echo "  EXISTS" || echo "  MISSING"
echo "docs/pipeline_audit_log.md:" && test -f docs/pipeline_audit_log.md && echo "  EXISTS" || echo "  MISSING"
echo "docs/reference/launch_prompt.txt:" && test -f docs/reference/launch_prompt.txt && echo "  EXISTS" || echo "  MISSING"
```

Expected: All files show EXISTS.

- [ ] **Step 2: Verify git log**

Run: `git log --oneline`

Expected output (newest first):
```
<hash> docs: add design spec and implementation plan
<hash> docs: archive original context files and sample EDA to docs/reference
<hash> feat: add settings, audit log template, and launch prompt
<hash> feat: add dashboard-integration agent definition
<hash> feat: add rl-bandit-microsim agent definition
<hash> feat: add eda-cascade-ml agent definition
<hash> feat: add literature-reviewer agent definition
<hash> feat: add CLAUDE.md with all domain rules and variable definitions
<hash> chore: initialize repo with directory structure and gitignore
```

- [ ] **Step 3: Verify CLAUDE.md is not gitignored**

Run: `git check-ignore CLAUDE.md; echo "exit: $?"`

Expected: exit code 1 (not ignored).

- [ ] **Step 4: Verify data/raw is gitignored**

Run: `git check-ignore data/raw/test.txt; echo "exit: $?"`

Expected: `data/raw/test.txt` printed, exit code 0 (ignored).
