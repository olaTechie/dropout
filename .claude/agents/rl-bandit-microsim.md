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
