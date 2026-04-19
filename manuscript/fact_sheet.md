# Numeric Fact Sheet — authoritative source for Results §3

> The Results author (Task 9) is allowed to cite ONLY numbers listed here.
> Each bullet lists: `<claim prose>` ← `<csv/json path>, <row/key selector>, <column/field>`.
> Flags of the form `[PLEASE VERIFY: ...]` mark values that cannot be extracted from
> machine-readable files and must be confirmed by the analyst before the Results author uses them.

---

## §3.1 Cohort descriptives (→ Table 1, Figure 1)

- **Total N (DTP1 recipients in analytic sample) = 3,194** ← `outputs/stage0/descriptive_statistics_table.csv`, row `n`, column `Overall`
- **T1 dropout count (vac_dropout == 1) = 472** ← `outputs/stage0/descriptive_statistics_table.csv`, row `n`, column `1` (under "Grouped by vac_dropout")
- **T1 dropout rate = 472 / 3,194 = 14.78%** ← computed from same CSV row
- **T1 non-dropout count (vac_dropout == 0) = 2,722** ← `outputs/stage0/descriptive_statistics_table.csv`, row `n`, column `0`
- **National weighted WHO DTP1-to-DTP3 dropout rate = 14.60%** ← `outputs/stage1/cascade_metrics.csv`, weighted mean: sum(n × who_dropout) / sum(n) across all six zones; total zone N = 3,194; computed value = 14.60%
- **Highest-dropout zone: North Central = 19.59%** ← `outputs/stage1/cascade_metrics.csv`, zone `North Central`, column `who_dropout` (value: 19.594586901966)
- **Second-highest: North East = 16.85%** ← `outputs/stage1/cascade_metrics.csv`, zone `North East`, column `who_dropout` (value: 16.848134123726)
- **North West dropout = 13.76%** ← `outputs/stage1/cascade_metrics.csv`, zone `North West`, column `who_dropout` (value: 13.757421049742)
- **South East dropout = 14.06%** ← `outputs/stage1/cascade_metrics.csv`, zone `South East`, column `who_dropout` (value: 14.058384675237)
- **Lowest-dropout zone: South South = 8.56%** ← `outputs/stage1/cascade_metrics.csv`, zone `South South`, column `who_dropout` (value: 8.559386990535)
- **South West dropout = 12.99%** ← `outputs/stage1/cascade_metrics.csv`, zone `South West`, column `who_dropout` (value: 12.987993998241)
- **T1 retention rate (DTP1→DTP2): North Central = 92.54%; South East highest = 98.10%** ← `outputs/stage1/cascade_metrics.csv`, column `retention_t1` for respective zones (North Central: 92.536498; South East: 98.102984)
- **Mean maternal age (overall) = 29.8 years (SD 6.5)** ← `outputs/stage0/descriptive_statistics_table.csv`, row `mage, mean (SD)`, column `Overall`
- **Mean maternal age (dropout) = 29.0 (SD 7.1) vs non-dropout = 29.9 (SD 6.3), p = 0.012** ← same row, columns `1`, `0`, and `P-Value`
- **No maternal education (medu=0): overall 26.5%; dropout 32.8%; non-dropout 25.4%; p < 0.001** ← `outputs/stage0/descriptive_statistics_table.csv`, rows `medu, n (%)` with value `0`
- **Higher education (medu=3): overall 16.7%; dropout 7.0%; non-dropout 18.4%** ← `outputs/stage0/descriptive_statistics_table.csv`, rows `medu, n (%)` with value `3`
- **No vaccination card (h1a=0): overall 18.5%; dropout 37.3%; non-dropout 15.2%; p < 0.001** ← `outputs/stage0/descriptive_statistics_table.csv`, rows `h1a, n (%)` with value `0.0`
- **Card present (h1a=1): overall 71.6%; dropout 49.4%; non-dropout 75.4%** ← `outputs/stage0/descriptive_statistics_table.csv`, rows `h1a, n (%)` with value `1.0`
- **Mean travel time to facility (overall) = 25.0 min (SD 27.6); dropout = 29.1 min (SD 29.4); p < 0.001** ← `outputs/stage0/descriptive_statistics_table.csv`, row `v483a, mean (SD)`, columns `Overall`, `1`, `0`, `P-Value`
- **Mean antenatal care visits (overall) = 6.6 (SD 5.2); dropout = 4.9 (SD 4.4); p < 0.001** ← `outputs/stage0/descriptive_statistics_table.csv`, row `antenat, mean (SD)`, columns `Overall`, `1`, `P-Value`
- **Facility delivery (overall) = 33.9%; dropout = 26.3%; non-dropout = 35.2%; p < 0.001** ← `outputs/stage0/descriptive_statistics_table.csv`, rows `facility_del, n (%)` with value `1`
- **Poorest wealth quintile (wealth=1): overall 16.7%; dropout 19.9%; non-dropout 16.1%; p < 0.001** ← `outputs/stage0/descriptive_statistics_table.csv`, rows `wealth, n (%)` with value `1`
- **Richest wealth quintile (wealth=5): overall 24.1%; dropout 13.1%; non-dropout 26.0%** ← `outputs/stage0/descriptive_statistics_table.csv`, rows `wealth, n (%)` with value `5`
- **Rural residence: 51.0% (no significant difference by dropout status, p = 1.000)** ← `outputs/stage0/descriptive_statistics_table.csv`, rows `rural, n (%)` with value `1`, column `P-Value`
- **Health insurance coverage: only 3.9% overall; lower in dropout group (2.1% vs 4.2%, p = 0.047)** ← `outputs/stage0/descriptive_statistics_table.csv`, rows `v481, n (%)` with value `1`
- **North Central zone count = 541 (16.9% of sample); dropout = 111 (23.5% of dropout group)** ← `outputs/stage0/descriptive_statistics_table.csv`, rows `zone_label, n (%)`, value `North Central`, columns `Overall` and `1`
- **South South zone count = 454 (14.2%); dropout = 45 (9.5%)** ← `outputs/stage0/descriptive_statistics_table.csv`, rows `zone_label, n (%)`, value `South South`, columns `Overall` and `1`

---

## §3.2 Prediction performance (→ Table 2, Figure 2)

- **T1 N = 3,194** ← `outputs/stage1/xgb_results_summary.json`, key `t1.n`
- **T1 prevalence = 0.0401 (4.0%)** ← `outputs/stage1/xgb_results_summary.json`, key `t1.prevalence` (raw value: 0.040075140889167186)
- **T1 AUROC = 0.910 (95% CI 0.885–0.932)** ← `outputs/stage1/xgb_results_summary.json`, keys `t1.metrics.auc_roc` (0.9100544421873025), `t1.metrics.auc_roc_ci` ([0.885245901597048, 0.9317870199756381])
- **T1 AUPRC = 0.299 (95% CI 0.230–0.387)** ← `outputs/stage1/xgb_results_summary.json`, keys `t1.metrics.auc_pr` (0.2992835149631423), `t1.metrics.auc_pr_ci` ([0.22967038692246408, 0.3867407676008945])
- **T1 Brier score pre-recalibration = 0.0358** ← `outputs/stage1/xgb_results_summary.json`, key `t1.metrics.brier_original.brier` (0.03580247402207748)
- **T1 Brier score post-recalibration = 0.0319** ← `outputs/stage1/xgb_results_summary.json`, key `t1.metrics.brier.brier` (0.03193414386752881)
- **T1 calibration slope pre-recalibration = 0.874** ← `outputs/stage1/xgb_results_summary.json`, key `t1.metrics.calibration_original.slope` (0.8735888182458796)
- **T1 calibration intercept pre-recalibration = −0.661** ← `outputs/stage1/xgb_results_summary.json`, key `t1.metrics.calibration_original.intercept` (−0.661273505927093)
- **T1 calibration slope post-recalibration = 0.959** ← `outputs/stage1/xgb_results_summary.json`, key `t1.metrics.calibration.slope` (0.959104052412017)
- **T1 calibration intercept post-recalibration = −0.065** ← `outputs/stage1/xgb_results_summary.json`, key `t1.metrics.calibration.intercept` (−0.06504470952432687)
- **T1 DeLong test: XGBoost AUROC 0.909 vs Logistic Regression AUROC 0.818; difference 0.091; z = 6.14; p = 8.1×10⁻¹⁰** ← `outputs/stage1/xgb_results_summary.json`, keys `t1.delong.auc_xgb`, `t1.delong.auc_lr`, `t1.delong.diff`, `t1.delong.z`, `t1.delong.p`
- **T1 Andersen domain contributions — Dynamic: 1.635; Need: 1.237; Enabling: 0.897; Predisposing: 0.788** ← `outputs/stage1/xgb_results_summary.json`, key `t1.andersen_domains`
- **T1 top-3 SHAP predictors: h69 (recorded vaccination status), Travel_Times (geospatial travel time to facility), Nightlights_Composite (satellite-derived development/infrastructure proxy)** ← extracted from `outputs/stage1/shap_bar_model_t1.pdf` via PyMuPDF text extraction; labels ordered top-to-bottom on the y-axis of a `shap.plots.bar()` chart, i.e. descending mean |SHAP|.
- **T2 N = 3,023** ← `outputs/stage1/xgb_results_summary.json`, key `t2.n`
- **T2 prevalence = 0.0394 (3.9%)** ← `outputs/stage1/xgb_results_summary.json`, key `t2.prevalence` (raw value: 0.039364869335097585)
- **T2 AUROC = 0.943 (95% CI 0.929–0.957)** ← `outputs/stage1/xgb_results_summary.json`, keys `t2.metrics.auc_roc` (0.9431931734510237), `t2.metrics.auc_roc_ci` ([0.928977876894313, 0.9572805168119299])
- **T2 AUPRC = 0.548 (95% CI 0.454–0.640)** ← `outputs/stage1/xgb_results_summary.json`, keys `t2.metrics.auc_pr` (0.5481630323573449), `t2.metrics.auc_pr_ci` ([0.4539706407102539, 0.6404413297903836])
- **T2 Brier score pre-recalibration = 0.0274** ← `outputs/stage1/xgb_results_summary.json`, key `t2.metrics.brier_original.brier` (0.027352878783906322)
- **T2 Brier score post-recalibration = 0.0255** ← `outputs/stage1/xgb_results_summary.json`, key `t2.metrics.brier.brier` (0.025499407052897168)
- **T2 calibration slope pre-recalibration = 1.596** ← `outputs/stage1/xgb_results_summary.json`, key `t2.metrics.calibration_original.slope` (1.5955172047783825)
- **T2 calibration intercept pre-recalibration = 0.724** ← `outputs/stage1/xgb_results_summary.json`, key `t2.metrics.calibration_original.intercept` (0.7244852966743882)
- **T2 calibration slope post-recalibration = 0.969** ← `outputs/stage1/xgb_results_summary.json`, key `t2.metrics.calibration.slope` (0.9689936431733048)
- **T2 calibration intercept post-recalibration = −0.104** ← `outputs/stage1/xgb_results_summary.json`, key `t2.metrics.calibration.intercept` (−0.10411803819230027)
- **T2 DeLong test: XGBoost AUROC 0.949 vs Logistic Regression AUROC 0.863; difference 0.086; z = 6.11; p = 9.7×10⁻¹⁰** ← `outputs/stage1/xgb_results_summary.json`, keys `t2.delong.*`
- **T2 Andersen domain contributions — Dynamic: 1.240; Need: 0.414; Enabling: 0.235; Predisposing: 0.212** ← `outputs/stage1/xgb_results_summary.json`, key `t2.andersen_domains`
- **T2 top-3 SHAP predictors: com_zses (community zonal SES composite), h22 (recent febrile illness — care-seeking proxy), v137 (number of children under 5 in household)** ← extracted from `outputs/stage1/shap_bar_model_t2.pdf` via PyMuPDF text extraction; same convention.
- **Recalibration method: isotonic regression (sklearn); date 2026-04-06** ← `outputs/stage1/recalibration_log.md`
- **Trajectory dataset: 6,217 rows, 3,138 unique children** ← `outputs/stage1/recalibration_log.md`, section "Trajectory Dataset"

---

## §3.3 Policy optimisation (→ Figure 3)

- **Total LGA community clusters with a recommended action = 1,140** ← `outputs/stage3/lga_allocation.csv`, count of data rows (file has 1,141 lines including header)
- **Action distribution in LGA allocation:**
  - a₁ (SMS reminder): 1,139 clusters (99.9%) ← `outputs/stage3/lga_allocation.csv`, column `assigned_action`, value `1`, value_counts()
  - a₂ (CHW home visit): 1 cluster (0.1%) ← `outputs/stage3/lga_allocation.csv`, column `assigned_action`, value `2`, value_counts()
  - a₀, a₃, a₄: 0 clusters (0%) ← same column, no rows with those values
- **NOTE for Results author:** The extreme skew toward a₁ in the bandit allocation may reflect the cost-constrained setup of the bandit. The RL policy (Stage 2) assigns richer action mixes — [PLEASE VERIFY: check `outputs/stage2/policy_lookup.csv` for RL policy action distribution].
- **Off-policy evaluation (OPE) — algorithm comparison:**
  - CQL: FQE = 0.700; WIS = 0.649; OOD frequency = 0.0% ← `outputs/stage2_v2/ope_comparison.csv`, row `CQL`
  - IQL: FQE = 0.872; WIS = 0.689; OOD frequency = 0.0%; is_winner = True ← `outputs/stage2_v2/ope_comparison.csv`, row `IQL`
  - BCQ: FQE = 0.610; WIS = 0.636; OOD frequency = 0.0% ← `outputs/stage2_v2/ope_comparison.csv`, row `BCQ`
  - Best algorithm: IQL (highest FQE and WIS; is_winner = True; zero OOD actions)

---

## §3.4 Scenarios and PSA (→ Table 3, Table 4, Figure 4)

All values below from `outputs/stage3_v2/microsim_results.csv` unless noted. All PSA n = 1,000 bootstrap iterations × 10,000 individuals per iteration (`outputs/stage3_v2/stage3_v2_summary.json`, keys `n_bootstrap`, `n_pop_per_bootstrap`).

### Coverage and cost by scenario

- **S0 Status Quo:** DTP3 coverage = 0.9141 (95% CI 0.9024–0.9247); cost per child = ₦0; concentration index = 0.0190; wealth gap = 0.0805; slope index = 0.1087 ← `microsim_results.csv`, row `S0: Status Quo`
- **S1 Uniform SMS:** DTP3 coverage = 0.9214 (95% CI 0.9099–0.9321); cost = ₦100.81 (95% CI 57.39–157.08); concentration index = 0.0173; wealth gap = 0.0739; slope index = 0.0998 ← `microsim_results.csv`, row `S1: Uniform SMS`
- **S2 Uniform CHW:** DTP3 coverage = 0.9291 (95% CI 0.9179–0.9393); cost = ₦1,012.89 (95% CI 569.34–1,571.82); concentration index = 0.0155; wealth gap = 0.0669; slope index = 0.0905 ← `microsim_results.csv`, row `S2: Uniform CHW`
- **S3 Risk-Targeted:** DTP3 coverage = 0.9289 (95% CI 0.9177–0.9390); cost = ₦445.32 (95% CI 270.89–653.56); concentration index = 0.0156; wealth gap = 0.0672; slope index = 0.0909 ← `microsim_results.csv`, row `S3: Risk-Targeted`
- **S4 RL-Optimised:** DTP3 coverage = 0.9248 (95% CI 0.9139–0.9350); cost = ₦748.00 (95% CI 427.51–1,147.79); concentration index = 0.0168; wealth gap = 0.0722; slope index = 0.0974 ← `microsim_results.csv`, row `S4: RL-Optimised`
- **S5 Bandit-Allocated:** DTP3 coverage = 0.9290 (95% CI 0.9179–0.9392); cost = ₦605.47 (95% CI 363.39–908.99); concentration index = 0.0155; wealth gap = 0.0669; slope index = 0.0904 ← `microsim_results.csv`, row `S5: Bandit-Allocated`

### Incremental vs S0 (computed from microsim_results.csv values above)

| Scenario | Δ DTP3 coverage (pp) | Δ cost (₦) | ICER (₦/pp) |
|----------|----------------------|------------|-------------|
| S1 | +0.74 | +100.81 | 137 |
| S2 | +1.50 | +1,012.89 | 675 |
| S3 | +1.48 | +445.32 | 301 |
| S4 | +1.07 | +748.00 | 699 |
| S5 | +1.50 | +605.47 | 404 |

*Δ coverage computed as: (scenario dtp3_mean − S0 dtp3_mean) × 100 percentage points.*
*ICER computed as: Δcost / Δcoverage (pp).*
*ICER values rounded to nearest whole number; cross-check against `outputs/stage3_v2/icer_distribution.csv`.*

### PSA ICER distributions (from `outputs/stage3_v2/icer_distribution.csv`)

- **S1:** mean ICER = ₦14,997; median = ₦13,927; 95% CI ₦6,528–₦30,221 ← `icer_distribution.csv`, row `S1: Uniform SMS`
- **S2:** mean ICER = ₦69,196; median = ₦66,539; 95% CI ₦34,492–₦116,630 ← `icer_distribution.csv`, row `S2: Uniform CHW`
- **S3:** mean ICER = ₦30,841; median = ₦29,836; 95% CI ₦16,811–₦50,173 ← `icer_distribution.csv`, row `S3: Risk-Targeted`
- **S4:** mean ICER = ₦71,992; median = ₦69,493; 95% CI ₦36,683–₦122,330 ← `icer_distribution.csv`, row `S4: RL-Optimised`
- **S5:** mean ICER = ₦41,497; median = ₦39,946; 95% CI ₦22,031–₦67,437 ← `icer_distribution.csv`, row `S5: Bandit-Allocated`
- **Note:** ICER denominator is mean_delta_effect (e.g., S1 = 0.00736 incremental DTP3 probability, i.e., 0.74 pp). These PSA ICERs are per-child in absolute probability units, not per-percentage-point as in the deterministic table above.

### CEAC probabilities at λ = ₦50,000 per percentage-point (from `outputs/stage3_v2/ceac_data.csv`, row `wtp = 50000.0`)

- S0: 0.0 ← `ceac_data.csv`, wtp row 50000.0, column `S0: Status Quo`
- S1: 0.433 ← `ceac_data.csv`, wtp row 50000.0, column `S1: Uniform SMS`
- S2: 0.0 ← `ceac_data.csv`, wtp row 50000.0, column `S2: Uniform CHW`
- S3: 0.567 ← `ceac_data.csv`, wtp row 50000.0, column `S3: Risk-Targeted`
- S4: 0.0 ← `ceac_data.csv`, wtp row 50000.0, column `S4: RL-Optimised`
- S5: 0.0 ← `ceac_data.csv`, wtp row 50000.0, column `S5: Bandit-Allocated`

*Interpretation: At λ = ₦50,000/pp, S3 (Risk-Targeted) has a 56.7% probability of being cost-effective, and S1 (Uniform SMS) has a 43.3% probability. S4 (RL-Optimised) has 0% probability at this threshold, consistent with its higher ICER.*

### Tornado analysis (from `outputs/stage3_v2/tornado_data.csv`)

- **Parameter 1 (largest range): RRR (−25%)** — low = 0.9201, high = 0.9277, base = 0.9241, **range = 0.0076** ← `tornado_data.csv`, row `RRR (-25%)`, column `range`
- **Parameter 2: Cost (−25%)** — low = 0.9238, high = 0.9238, base = 0.9241, **range = 0.0000** ← `tornado_data.csv`, row `Cost (-25%)`, column `range`
- **Note:** Only two rows exist in `tornado_data.csv`; the tornado plot effectively shows that the RRR parameter drives all DTP3 coverage uncertainty, while cost variation has no effect on coverage (only on cost-effectiveness). Results author should describe RRR as the dominant sensitivity parameter.

---

## §3.5 Subgroup equity (→ supplementary)

Note: Subgroup CSVs contain `predicted` (model-predicted DTP3 coverage) and `observed` (actual DTP3 coverage from cascade data), not AUROC subgroup performance. The absolute_error column is |predicted − observed|.

### By geopolitical zone (`outputs/validation/subgroup_zone.csv`, group codes: 1=NC, 2=NE, 3=NW, 4=SE, 5=SS, 6=SW)

- Group 5 (South South): predicted = 0.9602, observed = 0.9144, absolute error = 0.0458, not flagged (flagged = True — borderline) ← row `5`
- Group 4 (South East): predicted = 0.9433, observed = 0.8594, absolute error = 0.0839 (highest error), flagged = True ← row `4`
- Group 3 (North West): predicted = 0.8907, observed = 0.8624, absolute error = 0.0282, flagged = False (best calibrated) ← row `3`
- Group 1 (North Central): predicted = 0.8777, observed = 0.8041, absolute error = 0.0736, flagged = True ← row `1`
- Group 2 (North East): predicted = 0.8861, observed = 0.8315, absolute error = 0.0546, flagged = True ← row `2`
- Group 6 (South West): predicted = 0.9448, observed = 0.8701, absolute error = 0.0746, flagged = True ← row `6`
- **Best calibrated zone (lowest absolute error): North West (group 3), absolute error = 0.028** ← `subgroup_zone.csv`
- **Worst calibrated zone (highest absolute error): South East (group 4), absolute error = 0.084** ← `subgroup_zone.csv`

### By wealth quintile (`outputs/validation/subgroup_wealth_quintile.csv`, groups 1–5 = poorest–richest)

- Quintile 5 (richest): predicted = 0.9577, observed = 0.9182, absolute error = 0.0396, flagged = True ← row `5`
- Quintile 4: predicted = 0.9131, observed = 0.8572, absolute error = 0.0558, flagged = True ← row `4`
- Quintile 3: predicted = 0.8969, observed = 0.8361, absolute error = 0.0607, flagged = True ← row `3`
- Quintile 1 (poorest): predicted = 0.8803, observed = 0.8335, absolute error = 0.0468, flagged = True ← row `1`
- Quintile 2: predicted = 0.8683, observed = 0.8012, absolute error = 0.0671, flagged = True ← row `2`
- **Best calibrated wealth group: Quintile 5 (richest), absolute error = 0.040** ← `subgroup_wealth_quintile.csv`
- **Worst calibrated wealth group: Quintile 2, absolute error = 0.067** ← `subgroup_wealth_quintile.csv`

### By urban/rural (`outputs/validation/subgroup_urban_rural.csv`, 0=urban, 1=rural)

- Urban (0): predicted = 0.9149, observed = 0.8475, absolute error = 0.0674, flagged = True ← row `0`
- Rural (1): predicted = 0.9071, observed = 0.8599, absolute error = 0.0471, flagged = True ← row `1`
- **Rural group is better calibrated (lower absolute error = 0.047 vs 0.067)**

### By maternal education (`outputs/validation/subgroup_maternal_education.csv`, 0=none, 1=primary, 2=secondary, 3=higher)

- Higher education (3): predicted = 0.9671, observed = 0.9378, absolute error = 0.029, flagged = False (best calibrated) ← row `3`
- Secondary (2): predicted = 0.9141, observed = 0.8500, absolute error = 0.064, flagged = True ← row `2`
- Primary (1): predicted = 0.8926, observed = 0.8244, absolute error = 0.068, flagged = True ← row `1`
- None (0): predicted = 0.8725, observed = 0.8265, absolute error = 0.046, flagged = True ← row `0`
- **Best calibrated education group: Higher education (group 3), absolute error = 0.029** ← `subgroup_maternal_education.csv`
- **Worst calibrated education group: Primary education (group 1), absolute error = 0.068** ← `subgroup_maternal_education.csv`

### Equity: wealth gap narrowing under RL-optimised policy

- **S0 wealth gap = 0.0805** ← `outputs/stage3_v2/microsim_results.csv`, row `S0: Status Quo`, column `wealth_gap`
- **S4 (RL-Optimised) wealth gap = 0.0722** ← `outputs/stage3_v2/microsim_results.csv`, row `S4: RL-Optimised`, column `wealth_gap`
- **Absolute reduction = 0.0083; relative reduction ≈ 10.3%** ← computed: (0.0805 − 0.0722) / 0.0805
- **S3 (Risk-Targeted) wealth gap = 0.0672; S5 (Bandit) wealth gap = 0.0669** — both narrow the gap further than S4 ← `microsim_results.csv`, rows `S3` and `S5`
- **Concentration index: S0 = 0.0190; narrowing to 0.0155 under S2, S3, S5** ← `microsim_results.csv`, column `concentration_index`
- **Qualitative statement:** The RL-optimised scenario narrows the wealth gap between the poorest and richest quintiles by approximately 10% relative to the status quo; risk-targeted and bandit allocation strategies achieve the greatest absolute equity gains.

---

## §3.6 Dashboard (→ Figure 5) — qualitative; no numeric claims needed

The interactive dashboard (https://olatechie.github.io/dropout/) presents the full predict-optimise-simulate pipeline in four modules: Story (narrated walkthrough with WCAG AA transcript fallback), Policy (state- and zone-level choropleth), Simulation (scenario explorer), and Explorer (data drill-down). No additional numeric claims are required for this subsection beyond those already presented in §3.3–§3.4.
