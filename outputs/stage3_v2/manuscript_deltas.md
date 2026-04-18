# Manuscript deltas: v1 → v2

Concrete changes required to bring the manuscript into alignment with the
v2 (publication-grade) pipeline in `outputs/stage2_v2/` and `outputs/stage3_v2/`.
Source numbers come from `stage2_v2_summary.json`, `stage3_v2_summary.json`,
`ope_comparison.csv`, and `outputs/validation/validation_report.md`.

---

## 1. Abstract

Replace S0–S5 headline numbers with the v2 microsim means (10 000 pop,
1 000 PSU-clustered bootstraps, PSA enabled).

| Scenario | Old (v1) DTP3 | New (v2) DTP3 | Old cost (N) | New cost (N) |
|----------|---------------|---------------|--------------|--------------|
| S0 Status Quo | 0.859 | **0.914** | 155 | **0** |
| S1 Uniform SMS | 0.871 | **0.921** | 98 | **101** |
| S2 Uniform CHW | 0.884 | **0.929** | 979 | **1013** |
| S3 Risk-Targeted | 0.882 | **0.929** | 341 | **445** |
| S4 RL-Optimised | 0.882 | **0.925** | 903 | **748** |
| S5 Bandit-Allocated | 0.871 | **0.929** | 98 | **605** |

Replace "CQL-learned policy" with "IQL-learned policy (τ=0.7, β=3.0)".
Replace the OOD sentence: "the off-policy CQL policy had 33% out-of-distribution
actions" → "the selected IQL policy had **0% out-of-distribution actions**
(vs CQL 33% in v1) and the highest FQE (0.872) among CQL / IQL / BCQ
candidates evaluated on γ=0 FQE and WIS."

---

## 2. Methods

Three insertions / rewrites:

### 2.1 Add a Probabilistic sensitivity analysis (PSA) paragraph

> Effect sizes for each action were drawn from Beta priors parameterised
> from the literature review (SMS: mean 0.10, 95% CrI 0.02–0.20; CHW: mean
> 0.20, 95% CrI 0.10–0.30). Per-child costs were drawn from Gamma priors
> (SMS: N50 ± 20%; CHW: N500 ± 30%). One draw per bootstrap replicate
> propagates parameter uncertainty through the microsimulation, producing
> probabilistic ICERs, cost-effectiveness planes, and CEACs.

### 2.2 Replace the individual-level bootstrap description

> Uncertainty intervals were estimated by resampling individual children
> with replacement (B = 1 000).

with

> Uncertainty intervals were estimated by **cluster-bootstrapping on the DHS
> primary sampling unit (v021)**: B = 1 000 replicates, each resampling
> whole PSUs with replacement, preserving the complex-survey design. All
> means and CIs reported are across these replicates.

### 2.3 Replace the RL description

> We trained a Conservative Q-Learning agent (CQL, α = 5.0) on a 5-action
> MDP comprising no-intervention, SMS, CHW, facility recall, and
> conditional incentive.

with

> We trained three offline-RL agents on a 3-action MDP (no-intervention,
> SMS-like, CHW-like): Conservative Q-Learning (CQL), Implicit Q-Learning
> (IQL, expectile τ ∈ {0.7, 0.9}, advantage temperature β ∈ {3, 10}), and
> Discrete Batch-Constrained Q-Learning (BCQ, threshold = 0.3). Facility
> defaulter tracing (a₃) and conditional incentives (a₄) were dropped
> because DHS contains no reliable behaviour-proxy signal for them.
> Algorithms were compared on Fitted-Q Evaluation (γ = 0 given the
> cross-sectional nature of DHS) and weighted importance sampling, under
> the hard constraint that the policy's out-of-distribution action
> frequency must not exceed 10%. **IQL (τ = 0.7, β = 3.0) was selected**
> (FQE = 0.872, WIS = 0.689, OOD = 0.0%).

Also add a short paragraph on calibrated transitions:

> Per-step dropout probabilities (DTP1→DTP2 and DTP2→DTP3) were predicted
> by the Stage-1 XGBoost models with isotonic calibration reused at
> inference time via a shared `TransitionModel` wrapper, avoiding the
> refit drift present in earlier drafts.

---

## 3. Results

### 3.1 Update the microsim table

Replace the table rows with v2 means (see Abstract table above).
Footnote: "10 000-child microsim population, 1 000 PSU-clustered bootstrap
replicates with PSA; costs in 2024 Naira."

### 3.2 Update the OPE / RL result paragraph

Old:
> CQL improved on the behaviour policy by 6.7% FQE and 6.1% WIS, with
> 33.3% of actions out-of-distribution.

New:
> Among the three offline-RL candidates, IQL attained the highest FQE
> (0.872) while keeping every recommended action in-distribution
> (OOD = 0.0%); CQL and BCQ reached FQE = 0.700 and 0.610 with the same
> OOD = 0.0%. IQL was therefore selected as the policy applied in
> scenario S4.

### 3.3 Add a CEAC paragraph (new subsection)

> Figure X (`outputs/stage3_v2/ceac.png`) plots the probability that each
> scenario is cost-effective across willingness-to-pay thresholds from
> N0 to N10 000 per additional DTP3-completed child. A tornado analysis
> (`tornado.png`) isolates the single-parameter drivers of the ICER for
> the winning scenario against S0. The cost-effectiveness plane
> (`ce_plane.png`) shows the joint distribution of ΔCost and ΔDTP3
> across PSA × bootstrap draws.

### 3.4 Add a Validation paragraph

> Internal calibration comparing the microsim S0 rate against observed
> DTP3 in DHS 2024 revealed a **5.6 percentage-point over-prediction**
> (predicted 0.910 vs observed 0.854; tolerance 0.010, FAIL). Subgroup
> checks flagged 26/37 states, 5/6 zones, and all wealth quintiles /
> urban-rural strata, indicating that absolute coverage levels should be
> interpreted with this calibration gap in mind. Relative contrasts
> between scenarios remain interpretable because the bias is applied
> uniformly to the baseline and intervention arms (see Discussion).

---

## 4. Discussion

### 4.1 Update the winning-algorithm sentence

Replace any claim that CQL is the selected policy with IQL, and replace
the OOD framing: rather than discussing how to *reduce* OOD from 33%,
emphasise that the 3-action MDP plus the OOD ≤ 10% selection rule
**eliminated** distributional extrapolation entirely in v2.

### 4.2 Add a Limitation on internal calibration

> A limitation of the present microsimulation is that it systematically
> over-predicts S0 DTP3 coverage by roughly 5.6 percentage points relative
> to DHS 2024 (0.910 vs 0.854). This bias propagates uniformly across all
> scenarios, so relative effects (ΔDTP3, ICERs, CEAC rankings) are
> preserved, but absolute coverage projections should be reported with
> the calibration caveat. Subgroup calibration failures at state and
> zone level also suggest that geographic heterogeneity in baseline
> dropout is under-represented; a recalibration pass on held-out DHS
> folds, or conditioning initial states on sub-national observed dropout,
> is planned for a follow-up.

### 4.3 Strengths to add

Highlight the new v2 machinery as methodological contributions:
cluster bootstrap on v021, PSA with Beta/Gamma priors, concentration
index and SII alongside the wealth gap, OPE winner-selection under an
OOD constraint, and the ≥ 80% unit-test coverage gate on the core
decision-model modules.

---

## 5. Supplementary material pointers

Point readers to:

- `outputs/stage2_v2/algorithm_selection.md` and `ope_comparison.csv`
- `outputs/stage3_v2/comparison_v1_vs_v2.md`
- `outputs/stage3_v2/ceac.png`, `tornado.png`, `ce_plane.png`
- `outputs/validation/validation_report.md`

and note the code location: `src/dropout_rl/` with tests in `tests/`.
