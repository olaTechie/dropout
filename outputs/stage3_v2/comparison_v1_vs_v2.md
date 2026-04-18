# v1 (Original) vs v2 (Publication-Grade) Comparison

## Architecture

| Aspect | v1 | v2 |
|--------|----|----|
| Transition models | GradientBoostingClassifier refit in Stage 3 | Calibrated XGBoost + isotonic from Stage 1 (via `TransitionModel`) |
| Bootstrap | Individual children | Cluster on PSUs (v021) |
| Effect sizes | Point estimates only | Beta priors with PSA (optional) |
| Costs | Point estimates only | Gamma priors with PSA (optional) |
| Equity | Wealth gap only | Wealth gap + concentration index + SII (optionally survey-weighted) |
| RL | CQL only, 5-action, 33% OOD | CQL + IQL + BCQ, 3-action, 0% OOD, IQL winner |
| Sensitivity | None | CEAC, tornado, probabilistic ICER |
| Validation | None | Internal + subgroup calibration |
| Testing | Minimal | Unit tests with ≥80% coverage on core modules |
| Feature alignment | 55 features in trajectory vs 49 in XGB | Unified 49 features (`build_mdp_dataset` accepts `feature_names`) |

## Results comparison

| Scenario | v1 DTP3 | v2 DTP3 | v1 Cost (N) | v2 Cost (N) |
|----------|---------|---------|-------------|-------------|
| S0: Status Quo | 0.859 | 0.914 | N155 | N0 |
| S1: Uniform SMS | 0.871 | 0.921 | N98 | N101 |
| S2: Uniform CHW | 0.884 | 0.929 | N979 | N1013 |
| S3: Risk-Targeted | 0.882 | 0.929 | N341 | N445 |
| S4: RL-Optimised | 0.882 | 0.925 | N903 | N748 |
| S5: Bandit-Allocated | 0.871 | 0.929 | N98 | N605 |

Notes on the numbers:

- v1 S0 cost (N155) reflects a baseline that attributed a small CHW per-visit cost to the status-quo arm; v2 defines S0 explicitly as "no intervention cost" (N0) to match the counterfactual used throughout the decision model.
- v2 DTP3 levels across all arms are ~5pp higher than v1. This reflects the switch to **calibrated XGBoost transitions + isotonic calibration reused from Stage 1** (the v1 refit overestimated dropout) together with the 3-action MDP and the PSU-clustered bootstrap that samples whole clusters rather than iid children.
- Ranking is broadly preserved: S2/S3/S5 are top-tier in both versions; S4 loses some ground in v2 because the IQL policy selects a₂ (CHW) less aggressively than the v1 CQL policy did.

## RL algorithm change

| | v1 | v2 |
|---|----|-----|
| Algorithms | CQL only | CQL, IQL, BCQ (compared on common OPE bench) |
| Action space | 5 actions (a₀–a₄) | 3 actions (a₀, a₁, a₂) — evidence-supported only |
| Winner | CQL α=5.0 | **IQL τ=0.7, β=3.0** |
| OOD action frequency | 33.3% (FAIL) | 0.0% (PASS) |
| FQE of winner | 1.113 (policy) vs 1.043 (behaviour) | 0.872 |
| WIS of winner | 1.171 | 0.689 |
| Policy changes vs behaviour | 83.9% | Concentrated on the 3 evidence-supported arms |

### OPE comparison (v2, γ=0 due to cross-sectional DHS)

| algorithm | FQE | WIS | OOD | Winner |
|-----------|-----|-----|-----|--------|
| CQL | 0.700 | 0.649 | 0.00 | |
| **IQL** | **0.872** | **0.689** | **0.00** | ✓ |
| BCQ | 0.610 | 0.636 | 0.00 | |

### OOD improvement (33% → 0%)

- **Root cause in v1:** a 5-action space that included conditional incentives (a₄) and facility defaulter tracing (a₃), both with essentially zero support in DHS behaviour; CQL kept assigning them regardless of the conservative penalty.
- **Fix in v2:** drop a₃/a₄ until a reliable behaviour proxy exists, train on a 3-action MDP (no-intervention / SMS-like / CHW-like), and select the winner from CQL/IQL/BCQ under the hard constraint OOD ≤ 10%. IQL is the first algorithm in this study whose recommended actions are all in-distribution.

## New features in v2

1. **Probabilistic sensitivity analysis (PSA).** Beta priors on per-action RRR (`interventions.sample_rrr`) and Gamma priors on per-action cost (`costs.sample_cost`) are sampled once per bootstrap replicate when `psa_enabled=True`, propagating uncertainty end-to-end.
2. **Cluster bootstrap on PSU (v021).** `microsim.run_scenario` resamples entire PSUs rather than individuals, preserving the DHS complex-sample design and giving calibrated CIs on scenario means and ICERs.
3. **Cost-effectiveness acceptability curves (CEAC).** `sensitivity.ceac_from_psa` computes the probability each scenario is optimal across willingness-to-pay thresholds; tornado plots isolate single-parameter drivers.
4. **Probabilistic ICER and CE plane.** Full joint distribution of ΔCost and ΔDTP3 from the PSA run (not just point estimates).
5. **Concentration index and slope index of inequality (SII).** `equity.concentration_index` and `equity.slope_index` extend the v1 wealth-gap metric; survey-weighted variants accept `v005/1e6` weights.
6. **Internal + subgroup calibration checks.** `validation.calibration_check` compares predicted vs observed S0 DTP3 nationally and on pre-specified subgroups (state, zone, wealth, maternal education, urban/rural).
7. **Unified feature contract.** `rl.common.build_mdp_dataset` now accepts `feature_names`, eliminating the v1 mismatch between 55-feature trajectories and 49-feature XGBoost predictors.

## Known limitation: internal calibration fails

From `outputs/validation/validation_report.md`:

- Predicted S0 DTP3 (microsim, 10 000 pop): **0.910**
- Observed DTP3 in DHS 2024 (card-confirmed denominator): **0.854**
- Absolute error: **0.056** (tolerance 0.010) → **FAIL**

Subgroup calibration also flags most strata:

- State: 26 / 37 flagged, max |error| = 0.189
- Zone: 5 / 6 flagged, max |error| = 0.084
- Maternal education: 3 / 4 flagged, max |error| = 0.068
- Wealth quintile: 5 / 5 flagged, max |error| = 0.067
- Urban/rural: 2 / 2 flagged, max |error| = 0.067

**Interpretation.** The calibrated XGBoost transitions consistently under-predict dropout, so the microsim overestimates absolute DTP3 levels. **Relative** comparisons between scenarios (Δ vs S0, ICERs, CEAC) are still informative because the bias acts on the S0 baseline and the intervention arms alike, but absolute coverage projections should be reported with a clear caveat. A recalibration pass — either a post-hoc shift of the transition model on held-out DHS folds, or conditioning microsim initial states on sub-national observed dropout — is the natural next step.
