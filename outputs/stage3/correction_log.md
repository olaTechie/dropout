# Stage 3 Correction Log

**Date**: 2026-04-06
**Script**: scripts/stage3_corrected.py

## What Changed

### Fix 3: Effect Sizes — Relative Risk Reduction (CRITICAL)

**Before**: Effect sizes applied ADDITIVELY to completion probability:
```python
p_dtp2[mask] = np.minimum(p_dtp2[mask] + boost, 1.0)
# E.g., if baseline completion = 0.90 and SMS applied:
# p_dtp2 = 0.90 + 0.10 = 1.00  → 100% (wrong!)
```
Result: S1-S4 all hit 99.9-100% DTP3 completion.

**After**: Three-part fix:
1. Transition models trained WITHOUT action features (state-only) to avoid double-counting
   - Actions were inferred from outcomes, creating circularity if used as predictors
2. Status quo (S0) uses model predictions directly — no RRR applied
3. Intervention scenarios (S1-S5) apply RRR as additional reduction on status quo dropout:
```python
p_dropout = 1.0 - t_model.predict_proba(states)[:, 1]  # status quo dropout
p_dropout_adjusted = p_dropout * (1.0 - INTERVENTION_RRR[action])
# E.g., if baseline dropout = 10% and SMS (10% RRR):
# adjusted = 0.10 * 0.90 = 0.09 = 9% dropout → 91% completion (realistic!)
```

**Intervention RRR values** (central estimates from literature review):
| Action | RRR | Meaning |
|--------|-----|---------|
| a0: No intervention | 0% | No additional effect |
| a1: SMS reminder | 10% | 10% relative reduction in dropout |
| a2: CHW home visit | 20% | 20% relative reduction |
| a3: Facility recall | 25% | 25% relative reduction |
| a4: Incentive | 14% | 14% relative reduction |

### Fix 4: Budget Constraint Scaling

**Before**: Budget allocated per CLUSTER (DHS sample unit, ~3 children each).
- Total cost: ₦184K for 1,140 clusters → never binding

**After**: Budget allocated per LGA with realistic child populations.
- Assumed 3,000 children per LGA (based on ~6M nationally / ~774 LGAs)
- SMS everywhere: 1,140 × 3,000 × ₦50 = ₦171M (within ₦500M)
- CHW everywhere: 1,140 × 3,000 × ₦500 = ₦1.71B (exceeds ₦500M)
- Budget constraint is binding for CHW-heavy allocations

**Result**: The ₦500M budget allows universal SMS but constrains CHW to ~333 LGAs. However, the bandit correctly identifies SMS as more cost-effective for most communities (SMS has higher benefit-to-cost ratio for communities with <10% dropout), so the budget is not fully utilized. This is a legitimate finding, not a bug.

### Fix 5: Bandit → Microsim Mapping

**Before**: S5 (bandit) produced WORSE results than S0 (87.7% vs 90.3%).
- Raw bandit arm selection used without budget constraint
- Additive effect sizes caused inconsistencies

**After**: S5 uses the budget-constrained allocation from the primary bandit (₦500M).
- Each child receives the action assigned to their community
- Effect sizes applied as RRR (Fix 3)
- S5 result (87.1%) is between S0 (85.9%) and S2 (88.4%), as expected

## Corrected Results Summary

| Scenario | DTP3 Rate | 95% CI | Cost/Child | Equity Gap | ICER vs S0 |
|----------|-----------|--------|------------|------------|------------|
| S0: Status Quo | 85.9% | [85.2, 86.6] | ₦155 | 0.078 | — |
| S1: Uniform SMS | 87.1% | [86.4, 87.7] | ₦98 | 0.072 | ₦-4,591 (dominant) |
| S2: Uniform CHW | 88.4% | [87.8, 89.0] | ₦979 | 0.066 | ₦32,742 |
| S3: Risk-Targeted | 88.2% | [87.6, 88.8] | ₦341 | 0.067 | ₦8,007 |
| S4: RL-Optimised | 88.2% | [87.6, 88.8] | ₦903 | 0.069 | ₦32,434 |
| S5: Bandit-Allocated | 87.1% | [86.5, 87.8] | ₦98 | 0.072 | ₦-4,619 (dominant) |

**Key findings**:
1. No scenario hits 100% — all improvements are modest and realistic
2. All scenarios reduce equity gap vs S0
3. S1 (SMS) and S5 (bandit-SMS) are DOMINANT: better outcomes at LOWER cost than S0
4. S3 (risk-targeted) is the most cost-effective non-SMS strategy: ICER ₦8,007
5. S4 (RL) matches S3 in effectiveness but costs ~2.7× more
6. S2 (CHW) provides the highest DTP3 rate but at the highest cost

## Why RL Does NOT Outperform All Static Policies

The CQL policy (α=5.0) assigns:
- 20% to a0 (no intervention): RRR = 0%
- 17% to a1 (SMS): RRR = 10%
- 29% to a2 (CHW): RRR = 20%
- 10% to a3 (recall): RRR = 25%
- 23% to a4 (incentive): RRR = 14%
- **Average RRR = 13.1%**

Uniform CHW (S2) gives 20% RRR to everyone. The RL's average RRR is lower because:
1. CQL conservatism assigns 20% to a0 (no intervention)
2. Only 2 dose transitions (short horizon) limits sequential advantage
3. The RRR spread across actions (10-25%) is narrow

The RL's advantage would be more pronounced with:
- Longer horizons (more doses, longer follow-up)
- Wider action space (more differentiated interventions)
- Randomized trial data (vs inferred behaviour policy)
