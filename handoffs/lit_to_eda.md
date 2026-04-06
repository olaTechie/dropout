# Handoff: Literature Reviewer → EDA + Cascade + ML Agent

**Date**: 2026-04-06
**Status**: COMPLETE

---

## What Was Produced

| File | Description |
|------|-------------|
| `outputs/literature/dropout_literature_review.csv` | 8 key studies on DTP dropout determinants in Nigeria/SSA with prevalence rates, effect sizes, Andersen domains |
| `outputs/literature/rl_health_precedents.md` | Comprehensive novelty check + RL health precedents; confirms NO prior offline RL for vaccination dropout |
| `outputs/literature/intervention_effect_sizes.csv` | 17 rows of effect size data across 5 action types from RCTs and meta-analyses |
| `outputs/literature/action_space_calibration.json` | Updated action-space parameters with evidence-based effect sizes |
| `outputs/literature/ml_validation_recommendations.md` | Full validation checklist for XGBoost, offline RL (OPE), and SHAP interpretation |
| `outputs/literature/references.bib` | BibTeX file with 30+ references across all four tasks |

---

## Stage Gate Checklist

- [x] Task A: Dropout determinants — identified 8 key studies with AORs and prevalence rates
- [x] Task B: RL novelty — CONFIRMED: no offline RL applied to vaccination dropout
- [x] Task C: Intervention effect sizes — extracted from 6+ RCTs and 3 meta-analyses
- [x] Task D: ML validation — comprehensive recommendations written with specific metrics and thresholds
- [x] All outputs written to `outputs/literature/`
- [x] References compiled in BibTeX format
- [x] Action space calibration JSON updated with evidence-based ranges

---

## Updated Effect Sizes for Action Space

Changes from CLAUDE.md defaults:

| Action | CLAUDE.md Default | Literature Update | Source |
|--------|-------------------|-------------------|--------|
| a₁ SMS reminder | +5-10% | **+5-15%** (upper bound increased) | Eze et al. 2021 meta-analysis: RR=1.39 in low-income settings |
| a₂ CHW home visit | +15-25% | +15-25% (confirmed) | Ghana trial +25pp; Meta-analysis OR=3.31 for access enhancement |
| a₃ Facility recall | +20-30% | +20-30% (confirmed) | Indonesia RCT HR=1.50; Cochrane review OR=1.48 |
| a₄ Conditional incentive | +10-20% | **+9-22%** (range widened) | New Incentives Nigeria RCT +9-18pp; Banerjee India +22pp |

**Key finding**: SMS reminders are significantly MORE effective in low-income countries (RR=1.39) vs upper-middle-income (RR=1.01). Nigeria falls in the low-income category, so the upper bound should be 15%.

---

## Recommended Validation Techniques for Downstream ML Agents

### XGBoost Agent Must Include:
1. **AUC-ROC + AUC-PR** with bootstrap 95% CIs
2. **DeLong test** comparing XGBoost vs logistic regression baseline
3. **Calibration curve** (Loess-smoothed) with predicted probability histogram
4. **Brier score** with Spiegelhalter decomposition
5. **Calibration slope + intercept** (target: slope=1, intercept=0)
6. **Isotonic regression** for calibration correction if needed (preferred over Platt scaling for tree-based models)
7. **Survey-weighted metrics** using v005/1e6
8. **Cluster-robust CV**: hold out entire PSUs (v021) for more realistic generalisability
9. **Decision curve analysis** for clinical utility

### SHAP Agent Must Include:
1. Global bar plot + Beeswarm plot + Scatter plots for top features
2. **Andersen domain decomposition**: aggregate SHAP by Predisposing/Enabling/Need/Dynamic
3. Test-set SHAP values only; specify probability vs log-odds scale
4. Cross-fold stability check

### RL Agent Must Include:
1. **Two-stage OPE**: WIS (screening, epsilon=0.1) → FQE (final, H≥10)
2. **Avoid WDR** — worse than simpler methods in practice
3. OOD action frequency tracking
4. Behaviour vs learned policy comparison
5. Minimum 1000 validation episodes

---

## Key References the EDA Agent Should Cite

### Dropout Determinants
- Uthman et al. (2024) — Nigeria DHS equity analysis (primary framing paper)
- Tessema et al. (2024) — SSA multilevel analysis (multinational context)
- Adedokun et al. (2023) — Nigeria dropout trends 2003-2018

### Andersen Model
- The EDA agent should map ALL predictors to Andersen domains as specified in CLAUDE.md
- Key finding: individual-level factors dominate (29% PCV) over community-level (1.2% PCV)

### Nigeria-Specific Estimates to Reference
- Basic vaccination coverage: 31% (2018 NDHS)
- DTP3 coverage: ~53.5% (2024 NDHS)
- Dropout rate: 28% (2018), declined from 46% (2003)
- Zero-dose: 19% (2018 NDHS)

---

## Parameter Updates and Warnings

### Parameters Updated
1. **a₁ upper bound**: 10% → 15% (low-income subgroup evidence)
2. **a₄ range**: 10-20% → 9-22% (Nigeria-specific RCT + India RCT)
3. All changes reflected in `action_space_calibration.json`

### Warnings for Downstream Agents
1. **Survey weights are critical**: 2018 NDHS used complex survey design; all analyses must use v005/1e6 with v022 strata and v021 PSU
2. **Calibration is under-reported**: Only 36% of published prediction models report calibration — our study MUST include it
3. **SHAP ≠ causation**: SHAP values reflect model importance, not causal effects — frame carefully in paper
4. **OOD risk in RL**: Conservative Q-Learning (CQL) is essential because DHS data has limited action coverage — behaviour policy is inferred, not observed
5. **Geographic heterogeneity**: North-West and North-East zones have markedly different vaccination dynamics — consider zone-stratified analyses

---

## What the EDA Agent Should Read First

1. `CLAUDE.md` — all variable definitions and study population rules
2. `outputs/literature/action_space_calibration.json` — updated effect sizes
3. `outputs/literature/ml_validation_recommendations.md` — validation checklist
4. `outputs/literature/dropout_literature_review.csv` — prevalence benchmarks to validate against
