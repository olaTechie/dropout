# Results Summary Notes
## Vaccine Dropout — RL-Optimised Sequential Intervention
**Study:** RL-Optimised Sequential Intervention for Reducing DTP1-to-DTP3 Vaccine Dropout in Nigeria
**Data:** NDHS 2024 | n = 3,194 children aged 12-23 months who received DTP1
**Date:** April 2026

---

## Stage 0: EDA Highlights

- **Analytic sample:** 3,194 children aged 12-23m who received DTP1 (h3 in 1/2/3), alive, youngest per woman
- **Overall dropout rate:** 14.8% (received DTP1 but not DTP3)
- **T1 dropout (DTP1→DTP2):** 4.0% (n≈128)
- **T2 dropout (DTP2→DTP3):** 3.9% (n≈119, among DTP2 recipients)
- Spatial analysis: state-level choropleth, funnel plot, Local Moran's I hot/cold spots generated
- Full EDA: ydata-profiling, sweetviz (dropout vs completer), TableOne with p-values

### Cascade by Geopolitical Zone

| Zone | DTP2 Retention | DTP3 Retention | WHO Dropout Rate |
|------|---------------|---------------|-----------------|
| North Central | 92.5% | 80.4% | 19.6% |
| North East | 94.6% | 83.2% | 16.8% |
| North West | 94.1% | 86.2% | 13.8% |
| South East | 98.1% | 85.9% | 14.1% |
| South South | 96.8% | 91.4% | 8.6% |
| South West | 94.6% | 87.0% | 13.0% |

North Central has highest dropout (19.6%), South South lowest (8.6%).

---

## Stage 1: XGBoost + SHAP

### Model Performance (3 models, 200 Optuna trials each, cluster-robust CV)

| Model | N | Prevalence | AUC-ROC (95% CI) | AUC-PR (95% CI) | Brier | Cal Slope |
|-------|---|-----------|-------------------|------------------|-------|-----------|
| T1 (DTP1→DTP2) | 3,194 | 4.0% | 0.910 (0.885-0.932) | 0.299 (0.230-0.387) | 0.032* | 0.96* |
| T2 (DTP2→DTP3) | 3,023 | 3.9% | 0.943 (0.929-0.957) | 0.548 (0.454-0.640) | 0.026* | 0.97* |
| Full (overall) | 3,194 | 14.8% | — | — | — | — |

*After isotonic recalibration (original T1 slope=0.87, T2 slope=1.60)*

All models significantly outperform logistic regression (DeLong p < 1e-9).

### Andersen Domain SHAP Decomposition (mean |SHAP| by domain)

| Domain | T1 | T2 | Full |
|--------|-----|-----|------|
| Predisposing | 0.79 | 0.21 | 0.90 |
| Enabling | 0.90 | 0.23 | 0.80 |
| Need | 1.24 | 0.41 | 0.82 |
| **Dynamic** | **1.63** | **1.24** | **2.74** |

**Key finding:** Dynamic/temporal features dominate ALL models (T1=35.9%, T2=59.0%, Full=52.1%). This does NOT support the original hypothesis that T1 is predisposing-dominated and T2 is enabling/need-dominated. Instead, timing features (delay accumulation, inter-dose intervals, community dropout rates) are the strongest predictors at both transitions.

**Implication for RL:** Dynamic state features should be primary policy signals — the child's trajectory matters more than static demographics.

---

## Stage 2: Offline RL

### MDP Setup
- **State space:** 55 dimensions (Andersen + dynamic features)
- **Actions:** 5 (a₀ no intervention, a₁ SMS, a₂ CHW, a₃ recall, a₄ incentive)
- **Trajectory:** 6,217 rows (3,138 children × up to 2 dose steps)
- **Reward:** +1.0 DTP3 completion, +0.3 next dose, −λ×cost (λ=0.001)

### Behaviour Policy (inferred from DHS)
| Action | Proportion |
|--------|-----------|
| a₀ No intervention | 20.9% |
| a₁ SMS | 70.6% |
| a₂ CHW | 8.3% |
| a₃ Facility recall | 0.2% |
| a₄ Incentive | 0.0% |

### CQL Policy (learned, α=5.0)
| Action | Proportion | Δ from behaviour |
|--------|-----------|-----------------|
| a₀ No intervention | ~21% | ≈ same |
| a₁ SMS | ~16% | ↓ from 71% |
| a₂ CHW | ~38% | ↑ from 8% |
| a₃ Facility recall | ~8% | ↑ from 0.2% |
| a₄ Incentive | ~20% | ↑ from 0% |

CQL shifts from SMS-dominant to a more diversified policy emphasising CHW visits and incentives.

### Off-Policy Evaluation
| Method | Policy Value | Improvement |
|--------|-------------|-------------|
| Behaviour (observed) | 1.104 | — |
| WIS estimate | 1.171 | **+6.1%** |
| FQE estimate | 1.178 | **+6.7%** |

Both OPE methods agree: CQL policy is ~6-7% better than status quo.

**Caveat:** 33.3% of CQL actions are out-of-distribution (a₃ + a₄ rarely/never observed). CQL with α=5.0 is the most conservative setting tested, but OOD remains high because a₃/a₄ were essentially unobserved in the DHS data.

---

## Stage 3: Bandit + Microsimulation

### LinUCB Bandit
- 1,140 communities, 19-dimensional context (sociodem + geospatial)
- Converges primarily to SMS — most cost-effective at community level
- Budget constraint binding at ₦500M for CHW-heavy allocations (universal CHW would cost ₦1.71B)

### Microsimulation (10,000 population × 1,000 bootstrap iterations)

Effect sizes applied as **relative risk reduction on dropout probability** (not additive to completion):

| Scenario | DTP3 Rate | Δ vs S0 | Cost/Child | ICER vs S0 | Equity Gap |
|----------|-----------|---------|------------|------------|------------|
| **S0: Status Quo** | **85.9%** | — | ₦155 | — | 7.8pp |
| **S1: Uniform SMS** | **87.1%** | +1.3pp | ₦98 | **Dominant** | 7.2pp |
| S2: Uniform CHW | 88.4% | +2.5pp | ₦979 | ₦32,742 | 6.6pp |
| **S3: Risk-Targeted** | **88.2%** | +2.3pp | ₦341 | **₦8,007** | 6.7pp |
| S4: RL-Optimised | 88.2% | +2.3pp | ₦903 | ₦32,434 | 6.9pp |
| S5: Bandit-Allocated | 87.1% | +1.2pp | ₦98 | Dominant | 7.3pp |

### Interpretation

1. **S1 and S5 are dominant strategies** — lower cost AND better outcomes than status quo
2. **S3 (risk-targeted) is most cost-effective non-dominant** — ICER ₦8,007/FIC, achieves 88.2% DTP3 at ₦341/child (vs ₦979 for universal CHW)
3. **S4 (RL) matches S3 on DTP3** (88.2%) but at much higher cost (₦903 vs ₦341) — RL does not clearly outperform well-designed static targeting
4. **All scenarios reduce the equity gap** — poorest/richest disparity narrows from 7.8pp (S0) to 6.6-7.3pp across all interventions. Equity constraint satisfied.
5. **S5 (bandit) performs modestly** — community-level allocation captures less individual variation than child-level targeting

### Why RL Doesn't Clearly Outperform

This is an important methodological finding, not a failure:
- **CQL conservatism:** α=5.0 assigns ~21% to "no intervention" to avoid OOD risk
- **Short horizon:** Only 2 dose transitions (DTP1→DTP2→DTP3) — limited scope for sequential advantage
- **Narrow effect size range:** 10-25% RRR across actions — not enough differentiation for RL to exploit
- **Inferred behaviour policy:** DHS doesn't record actual interventions — proxy inference adds noise
- The RL framework's value is in the **conceptual contribution** (framing dropout as sequential decision problem) and the **methodological novelty** (first offline RL for vaccination dropout), not raw performance superiority

---

## Cross-Stage Synthesis

| Finding | Evidence |
|---------|----------|
| Dynamic features matter most | SHAP: 36-59% of total importance across all models |
| SMS is the floor intervention | S1 dominant, S5 bandit converges to SMS |
| Risk-targeting is efficient | S3 achieves 92% of CHW benefit at 35% of cost |
| RL is novel but modest | +2.3pp over S0, matches S3, first offline RL for vax dropout |
| No equity harm | All scenarios narrow the poorest-richest gap |
| Calibration matters | T2 slope 1.60→0.97 after isotonic correction |

---

## Key Numbers for Abstract

- n = 3,194 DTP1 recipients aged 12-23m (NDHS 2024)
- Overall dropout rate: 14.8%
- T1 dropout: 4.0%, T2 dropout: 3.9%
- XGBoost AUC-ROC: T1=0.910, T2=0.943 (DeLong p<1e-9 vs LR)
- Dynamic features dominate SHAP: 36-59% across all models
- CQL policy improvement: +6.1% (WIS), +6.7% (FQE)
- Best scenario: S3 risk-targeted (88.2% DTP3, ICER ₦8,007/FIC)
- RL-optimised: 88.2% DTP3 (matches S3, first offline RL for vax dropout)
- Equity: all scenarios reduce poorest-richest gap (7.8pp → 6.6-7.3pp)
- Novelty: first application of offline RL to vaccination dropout

---

## Issues to Address in Full Manuscript

1. **Low event rates:** T1/T2 prevalence ~4% — AUC-PR more informative than AUC-ROC for imbalanced data
2. **Andersen hypothesis not supported:** Dynamic features dominate, not predisposing (T1) or enabling/need (T2) — reframe as finding
3. **RL vs static:** RL conceptual contribution > raw performance gain — discuss honestly
4. **OOD actions (33%):** a₃/a₄ essentially unobserved in DHS — CQL extrapolation has high uncertainty
5. **Inferred behaviour policy:** No ground truth on interventions — discuss as key limitation
6. **Card-confirmed dates:** Only ~30% of children have card dates for temporal analysis — selection bias
7. **Cross-sectional data:** Trajectories reconstructed retrospectively, not observed longitudinally
