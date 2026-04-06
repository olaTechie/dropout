# Pipeline Audit Log

## Literature Review (Agent 1)
- Status: COMPLETE
- Started: 2026-04-06
- Completed: 2026-04-06
- Handoff: handoffs/lit_to_eda.md
- Notes: Novelty confirmed (no prior offline RL for vax dropout). Effect sizes updated: a₁ SMS upper bound → 15%, a₄ incentive → 9-22%. 30+ references compiled. Full ML validation checklist produced.

## EDA + Cascade + ML (Agent 2)
- Status: COMPLETE
- Started: 2026-04-06
- Completed: 2026-04-06
- Handoff: handoffs/eda_to_rl.md
- Notes: N=3,194 DTP1 recipients. Overall dropout 14.8%. Three XGBoost models fitted (Full, T1, T2) with Optuna tuning (200 trials), cluster-robust CV, SHAP + Andersen decomposition. Model T2 best discriminator (AUC-ROC=0.943). Dynamic features dominate all models (35-59% SHAP). Trajectory dataset exported: 6,217 rows, 55-dim state space, 5-action space. All stage gate checks passed.

## RL + Bandit + Microsim (Agent 3)
- Status: COMPLETE
- Started: 2026-04-06
- Completed: 2026-04-06
- Handoff: handoffs/rl_to_dashboard.md
- Notes: FQI (50 iter, ExtraTrees) + CQL (α=1.0, GBR, 80 iter). CQL policy shifts from SMS-dominant (70.6%) to CHW-heavy (38.2%) + incentives (19.5%). OPE: WIS +9.5%, FQE +6.9% improvement over behaviour. LinUCB bandit on 1,140 communities with 19-dim context (12 sociodem + 5 geospatial). 6 microsim scenarios (10K pop × 1,000 bootstrap): S1 (SMS) dominates on ICER, S4 (RL) achieves 99.7% DTP3 without widening equity gap. S5 (bandit) fails equity constraint. All stage gate checks passed.

## Dashboard + Integration (Agent 4)
- Status: COMPLETE
- Started: 2026-04-06
- Completed: 2026-04-06
- Handoff: N/A (terminal stage)
- Notes: 8-page Streamlit dashboard built at code/stage5_dashboard/. Pages: (1) Immunisation Cascade with zone filtering, (2) EDA Explorer with choropleth/funnel/Moran maps, (3) SHAP Explorer with Andersen decomposition and model performance, (4) Timeliness Analysis, (5) RL Policy Map with CQL vs behaviour comparison and OPE metrics, (6) Bandit Allocation with budget sensitivity, (7) Microsimulation with 6-scenario comparison/equity/CE plane, (8) Data Export for all pipeline outputs. Cross-stage consistency verified: N=3,194 consistent across all stages, dropout rate 14.8% confirmed, CQL improvement +6.9-9.5% matches OPE results, microsim S5 equity failure flagged.

---

## Cross-Stage Consistency Verification

| Check | Status | Detail |
|-------|--------|--------|
| Sample size N=3,194 | PASS | Consistent in EDA (stage0), ML (stage1), trajectory (stage1→2) |
| Dropout prevalence 14.8% | PASS | Confirmed in descriptive stats and cascade metrics |
| T1 dropout ~4.0%, T2 ~3.9% | PASS | Consistent between EDA handoff and XGBoost model prevalences |
| Trajectory rows = 6,217 | PASS | Matches policy_lookup.csv (6,217 rows) |
| Action space 5 actions (a0-a4) | PASS | Consistent across state_space_definition.json, trajectory, policy_lookup |
| CQL policy improvement 7-10% | PASS | WIS=+9.5%, FQE=+6.9% — both in ope_results.json and handoff |
| Microsim S0 baseline 90.3% DTP3 | PASS | matches microsim_results.json (0.9035) |
| S5 equity gap widening | PASS | 7.2% > S0 baseline 5.1% — flagged correctly |
| Survey weights applied | PASS | All XGBoost metrics survey-weighted; trajectory has weight column |
| szone used (not v024) | PASS | Cascade metrics use zone (szone-based), confirmed in EDA handoff |
| Andersen dynamic dominance | PASS | T1=35.9%, T2=59.0%, Full=52.1% — consistent across handoff and xgb_results_summary.json |
| Literature effect sizes used | PASS | SMS +5-15%, CHW +15-25%, Facility +20-30%, Incentive +9-22% — reflected in microsim |

### Files Verified Present

**Stage 0 (EDA)**: 14 files — all present
**Stage 1 (Cascade+ML)**: 27 files — all present
**Stage 2 (Offline RL)**: 17 files — all present
**Stage 3 (Bandit+Microsim)**: 17 files — all present
**Literature**: 6 files — all present

**Total pipeline outputs**: 81 files across 5 output directories
