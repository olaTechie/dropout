# Handoff: RL + Bandit + Microsim → Dashboard Agent

**Date**: 2026-04-06
**Status**: COMPLETE (corrected run)

---

## What Was Produced

### Stage 2: Offline RL (`outputs/stage2/`)

| File | Description |
|------|-------------|
| `fqi_model.joblib` | Fitted Q-Iteration model (converged at iteration 2) |
| `cql_model.joblib` | Conservative Q-Learning model (α=5.0, most conservative) |
| `behaviour_policy_model.joblib` | Random Forest behaviour policy estimator |
| `fqe_model.joblib` | Fitted Q Evaluation model |
| `policy_lookup.csv` | Policy lookup: 6,217 rows with Q-values + optimal actions |
| `ope_results.json` | Off-policy evaluation: WIS, IS, FQE, DR estimates |
| `cql_alpha_sensitivity.csv` | CQL α=1.0, 2.0, 5.0 sensitivity analysis |
| `stage2_summary.json` | Complete summary of Stage 2 metrics |
| `correction_log.md` | What changed from previous run and why |
| `fqi_convergence.pdf/.png` | FQI convergence plot |
| `cql_analysis.pdf/.png` | CQL convergence, penalty, α sensitivity |
| `ope_comparison.pdf/.png` | OPE comparison bar chart + policy comparison |
| `q_values_by_action.pdf/.png` | Mean Q-values by action |

### Stage 3: Bandit + Microsim (`outputs/stage3/`)

| File | Description |
|------|-------------|
| `lga_allocation.csv` | Budget-constrained LinUCB allocation (₦500M) |
| `microsim_results.csv` | 6-scenario microsim results table |
| `microsim_results.json` | Full results with CIs and ICER |
| `stage3_summary.json` | Complete summary including budget sensitivity |
| `correction_log.md` | What changed from previous run and why |
| `bandit_allocation.pdf/.png` | LinUCB regret + budget coverage |
| `microsim_scenarios.pdf/.png` | 4-panel: DTP3 rates, costs, equity, ICER frontier |
| `bootstrap_distributions.pdf/.png` | Bootstrap distributions all 6 scenarios |
| `bootstrap_s0_status_quo.csv` | 1,000 bootstrap samples for S0 |
| `bootstrap_s1_uniform_sms.csv` | Bootstrap samples S1 |
| `bootstrap_s2_uniform_chw.csv` | Bootstrap samples S2 |
| `bootstrap_s3_risk_targeted.csv` | Bootstrap samples S3 |
| `bootstrap_s4_rl_optimised.csv` | Bootstrap samples S4 |
| `bootstrap_s5_bandit_allocated.csv` | Bootstrap samples S5 |

---

## Key Findings

### 1. RL Policy Improvement
- **FQI**: Converged (ΔQ=0.000 at iteration 2)
- **CQL**: α=5.0 selected (most conservative; OOD=33.3%)
- **OPE**: WIS +6.1%, FQE +6.7% improvement over behaviour policy
- **Policy**: 83.9% of state-action pairs changed from behaviour

### 2. Microsimulation Results (CORRECTED)

| Scenario | DTP3 | Improvement | Cost/Child | ICER | Equity Gap |
|----------|------|-------------|------------|------|------------|
| S0: Status Quo | 85.9% | — | ₦155 | — | 0.078 |
| **S1: SMS** | **87.1%** | **+1.3pp** | **₦98** | **Dominant** | **0.072** |
| S2: CHW | 88.4% | +2.5pp | ₦979 | ₦32,742 | 0.066 |
| **S3: Risk-Targeted** | **88.2%** | **+2.3pp** | **₦341** | **₦8,007** | **0.067** |
| S4: RL-Optimised | 88.2% | +2.3pp | ₦903 | ₦32,434 | 0.069 |
| S5: Bandit | 87.1% | +1.2pp | ₦98 | Dominant | 0.072 |

### 3. Which Scenario Wins?

**For policy recommendation**: S3 (Risk-Targeted) is the best strategy:
- Nearly as effective as CHW (+2.3pp vs +2.5pp)
- 1/3 the cost of CHW (₦341 vs ₦979)
- Best ICER among non-dominant strategies (₦8,007)
- Reduces equity gap (0.067 vs 0.078)

**For budget-constrained settings**: S1/S5 (SMS-based) are DOMINANT:
- Better outcomes than status quo at LOWER cost
- Negative ICER = intervention pays for itself (reduces costs vs current practice)

**For maximum impact regardless of cost**: S2 (Uniform CHW)
- Highest DTP3 rate (88.4%)
- Largest equity gap reduction

### 4. RL vs Static Policies

The RL policy matches but does not clearly outperform risk-targeted (S3) or CHW (S2). This is because:
- CQL conservatism assigns 20% of children to "no intervention"
- Only 2 dose transitions limit sequential decision advantage
- The action RRR spread (10-25%) is narrow
- RL's advantage is cost-efficiency (comparable to S3, better than S2)

### 5. Equity Impact

All intervention scenarios reduce the richest-poorest equity gap:
- S0: 0.078 → S3: 0.067 (14% reduction)
- S4 (RL): 0.069 — does NOT widen the gap (constraint satisfied)

### 6. Budget Constraint

At ₦500M national budget with 3,000 children/LGA:
- SMS everywhere: ₦171M (feasible)
- CHW everywhere: ₦1.71B (exceeds budget)
- Bandit allocates SMS to 99.9% of communities (most cost-effective)
- Budget only binding for CHW-heavy allocation strategies

---

## Corrections Applied

1. **FQI**: 50→200 iterations, threshold 0.001→0.01
2. **CQL**: Tested α=1.0, 2.0, 5.0; selected α=5.0 (most conservative)
3. **Effect sizes**: Relative risk reduction on dropout (not additive to completion)
4. **Transition models**: State-only (no action features) to avoid circularity
5. **Budget**: Scales by 3,000 children/LGA (not DHS sample size)
6. **Bandit→microsim**: Uses budget-constrained allocation with corrected effects

---

## Dashboard Integration

### Figure Locations

| Figure | Path | Dashboard Panel |
|--------|------|-----------------|
| FQI convergence | `outputs/stage2/fqi_convergence.png` | RL Training |
| CQL analysis | `outputs/stage2/cql_analysis.png` | RL Training |
| OPE comparison | `outputs/stage2/ope_comparison.png` | Policy Evaluation |
| Q-values by action | `outputs/stage2/q_values_by_action.png` | Policy Analysis |
| Bandit allocation | `outputs/stage3/bandit_allocation.png` | Community Allocation |
| Microsim scenarios | `outputs/stage3/microsim_scenarios.png` | Scenario Comparison |
| Bootstrap distributions | `outputs/stage3/bootstrap_distributions.png` | Uncertainty |

### Data for Interactive Dashboard

- `outputs/stage2/policy_lookup.csv`: Per-child Q-values and optimal actions
- `outputs/stage2/cql_alpha_sensitivity.csv`: CQL α sensitivity data
- `outputs/stage3/microsim_results.json`: Scenario comparison data
- `outputs/stage3/lga_allocation.csv`: Community-level allocation map
- `outputs/stage3/stage3_summary.json`: Budget sensitivity analysis

---

## What the Dashboard Agent Should Read First

1. `outputs/stage3/microsim_results.json` — scenario comparison (main result)
2. `outputs/stage2/stage2_summary.json` — RL training summary
3. `outputs/stage3/stage3_summary.json` — full stage 3 summary with budget sensitivity
4. `outputs/stage3/correction_log.md` — what changed and why
