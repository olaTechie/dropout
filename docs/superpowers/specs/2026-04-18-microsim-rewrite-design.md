# Design Spec: Publication-Grade Microsimulation Rewrite with Offline RL Comparison

**Date:** 2026-04-18
**Author:** Ola Uthman + Claude (Opus 4.7)
**Status:** Approved

---

## 1. Problem Statement

The current Stage 2 (offline RL) and Stage 3 (bandit + microsimulation) scripts generated publishable but imperfect results. Specific problems identified during manuscript preparation:

1. **Stage 3 refits transition models** (GradientBoostingClassifier) instead of using the carefully recalibrated XGBoost + isotonic calibrators from Stage 1 — creating inconsistency with the prediction analysis.
2. **No probabilistic sensitivity analysis (PSA)** — effect-size literature ranges (e.g. SMS 5-15%) are loaded but only point estimates are used in the microsim. Bootstrap CIs understate uncertainty.
3. **Bootstrap ignores cluster structure** — individual children are resampled instead of PSUs (v021), understating CIs.
4. **Cost model is single-point** — no uncertainty over intervention costs.
5. **Equity metric is binary** — only richest-minus-poorest gap, no concentration index or slope index of inequality.
6. **RL OOD frequency is 33%** — CQL recommends a₃ (0.2%) and a₄ (0.0%) which are essentially unobserved in the data.
7. **No validation** — the microsim is not formally checked against observed data.
8. **No CEAC or probabilistic ICER** — standard cost-effectiveness analysis outputs are missing.
9. **Monolithic scripts** — no unit tests, no reusability across stages or studies.

## 2. Solution Overview

Rewrite Stage 2 and Stage 3 as a modular Python package `src/dropout_rl/` with:

- Calibrated Stage 1 models used directly (consistency with prediction analysis)
- Narrowed RL action space to {a₀, a₁, a₂} with three algorithms compared (CQL, IQL, BCQ)
- Probabilistic sensitivity analysis (PSA) integrated with cluster-bootstrap
- Full cost-effectiveness analysis: probabilistic ICER, CEAC, tornado diagram
- Three equity metrics: wealth gap, concentration index, slope index of inequality
- Internal calibration check + subgroup validation
- Unit tests for every module
- Primary microsimulation with 3 actions; 2 additional sensitivity scenarios with a₃ and a₄ using literature effect sizes

## 3. Repository Structure

```
src/dropout_rl/
├── __init__.py
├── config.py
├── transitions.py
├── interventions.py
├── costs.py
├── equity.py
├── rl/
│   ├── __init__.py
│   ├── common.py
│   ├── cql.py
│   ├── iql.py
│   ├── bcq.py
│   └── ope.py
├── microsim.py
├── sensitivity.py
└── validation.py

tests/
├── fixtures/                   # Synthetic test data
├── test_transitions.py
├── test_interventions.py
├── test_costs.py
├── test_equity.py
├── test_rl_common.py
├── test_ope.py
├── test_microsim.py
└── test_validation.py

scripts/
├── legacy/                     # Current stage2_corrected.py and stage3_corrected.py
├── run_stage2.py               # Trains CQL + IQL + BCQ, selects best
├── run_stage3.py               # 8 scenarios with full PSA
├── run_validation.py
└── run_sensitivity.py

outputs/
├── stage2_v2/
├── stage3_v2/
└── validation/
```

## 4. Module Specifications

### 4.1 `transitions.py`

Wraps the recalibrated XGBoost models from Stage 1.

```python
class TransitionModel:
    def __init__(self, xgb_path: Path, calibrator_path: Path): ...
    def predict_dropout(self, X: np.ndarray) -> np.ndarray:
        """Returns calibrated P(dropout | state) in [0, 1]."""

def load_t1() -> TransitionModel: ...
def load_t2() -> TransitionModel: ...
```

Loads `outputs/stage1/xgb_model_t1.json` + `isotonic_calibrator_t1.pkl` (and equivalents for t2).

### 4.2 `interventions.py`

Effect-size priors as Beta distributions fit to literature ranges.

| Action | Prior | Central | Range |
|--------|-------|---------|-------|
| a₀ | Point mass | 0.00 | – |
| a₁ (SMS) | Beta | 0.10 | [0.05, 0.15] |
| a₂ (CHW) | Beta | 0.20 | [0.15, 0.25] |
| a₃ (recall) | Beta | 0.25 | [0.20, 0.30] |
| a₄ (incentive) | Beta | 0.14 | [0.09, 0.22] |

Beta parameters fit by method-of-moments on literature ranges interpreted as 95% intervals.

```python
def sample_rrr(action: int, rng: np.random.Generator) -> float: ...
def apply_rrr(p_dropout: np.ndarray, actions: np.ndarray,
              rrr_draws: np.ndarray) -> np.ndarray:
    """Returns clipped P(dropout | state, action) in [0, 1]."""
```

### 4.3 `costs.py`

Cost uncertainty as Gamma priors with CoV = 0.25.

| Action | Mean (₦) | CoV |
|--------|----------|-----|
| a₀ | 0 | — |
| a₁ | 50 | 0.25 |
| a₂ | 500 | 0.25 |
| a₃ | 1,500 | 0.25 |
| a₄ | 800 | 0.25 |

```python
def sample_cost(action: int, rng: np.random.Generator) -> float: ...
def fixed_programmatic_cost() -> float:
    """Returns 0 by default; parameter for sensitivity."""
```

### 4.4 `equity.py`

Three equity metrics:

```python
def wealth_gap(outcomes: np.ndarray, wealth_quintile: np.ndarray) -> float:
    """Richest minus poorest quintile outcome rate."""

def concentration_index(outcomes: np.ndarray, wealth_rank: np.ndarray) -> float:
    """Wagstaff concentration index. Range [-1, 1]."""

def slope_index_of_inequality(outcomes: np.ndarray, wealth_rank: np.ndarray) -> float:
    """SII from regression on ridit-scored wealth rank."""
```

### 4.5 `rl/common.py`

Shared RL infrastructure:
- `infer_behaviour_policy(traj_df) -> np.ndarray` — 3-action version of current rules
- `build_mdp_dataset(traj_df) -> MDPDataset` — standardised input for all algorithms
- Action space constants: `N_ACTIONS = 3`, `ACTIONS = [0, 1, 2]`

**Behaviour policy rules (3-action):**
- Next dose ON TIME (≤42 days) + fieldworker visit (v393==1) → a₂
- Next dose ON TIME (≤42 days) + campaign vaccination (h69==41) → a₂ (was a₃ in 5-action)
- Next dose ON TIME (≤42 days) + card present (h1a≥1) → a₁
- Next dose LATE (>42 days) → a₀
- Next dose NOT received → a₀

### 4.6 `rl/cql.py`, `rl/iql.py`, `rl/bcq.py`

All implement the same protocol:

```python
class OfflineRLAlgorithm(Protocol):
    def fit(self, dataset, n_epochs: int, rng: Generator) -> None: ...
    def predict_action(self, states) -> np.ndarray: ...
    def predict_q(self, states) -> np.ndarray: ...
```

**CQL**: tune α ∈ {0.5, 1.0, 2.0, 5.0, 10.0}, select minimising OOD subject to FQE improvement ≥ 0.

**IQL**: expectile τ ∈ {0.7, 0.9}, temperature β ∈ {3.0, 10.0}.

**DiscreteBCQ**: threshold τ = 0.3 (exclude actions with behaviour prob < 0.3 × max).

### 4.7 `rl/ope.py`

Unified off-policy evaluation:

```python
def evaluate_policy(policy, dataset,
                    method: Literal["wis", "fqe", "dr"]) -> dict:
    """Returns {policy_value, ci_low, ci_high, ood_frequency}."""
```

### 4.8 `microsim.py`

```python
@dataclass
class ScenarioResult:
    name: str
    dtp3_rate: np.ndarray         # (n_bootstrap,)
    cost_per_child: np.ndarray
    total_cost: np.ndarray
    concentration_index: np.ndarray
    wealth_gap: np.ndarray
    slope_index: np.ndarray
    rate_by_quintile: np.ndarray  # (n_bootstrap, 5)
    rate_by_zone: np.ndarray      # (n_bootstrap, 6)
    actions_per_step: np.ndarray

def run_scenario(
    name: str,
    policy_fn_t1: Callable,
    policy_fn_t2: Callable,
    analytic_df: pd.DataFrame,
    t1_model: TransitionModel,
    t2_model: TransitionModel,
    n_pop: int = 10_000,
    n_bootstrap: int = 1_000,
    cluster_bootstrap: bool = True,
    psa: bool = True,
    seed: int = 42,
    is_status_quo: bool = False,
) -> ScenarioResult: ...
```

**Cluster-bootstrap:** resample PSUs (v021), then sample all children within selected PSUs. Preserves complex survey design.

**PSA integration:** each bootstrap iteration draws one RRR per action from `sample_rrr()` and one cost per action from `sample_cost()`. Joint distribution over sampling + effect-size + cost uncertainty.

### 4.9 `sensitivity.py`

```python
def tornado_diagram(base_scenario, param_ranges: dict) -> pd.DataFrame:
    """One-way sensitivity for each parameter ±2σ."""

def ceac(scenarios: list[ScenarioResult],
         wtp_range: np.ndarray) -> pd.DataFrame:
    """Probability each scenario optimal at each WTP."""

def probabilistic_icer(scenario: ScenarioResult,
                       reference: ScenarioResult) -> dict:
    """Full joint distribution of (ΔDTP3, ΔCost). Returns point + CI."""
```

Parameters for tornado: RRR for a₁/a₂, costs for a₁/a₂, CHILDREN_PER_LGA, baseline dropout rate.

WTP range: ₦0 to ₦100,000 per additional DTP3 completion in 100 steps.

### 4.10 `validation.py`

```python
def calibration_check(predicted_rate: float,
                      observed_rate: float,
                      tolerance: float = 0.01) -> dict:
    """Returns pass/fail + absolute error."""

def subgroup_calibration(predicted_by_group: pd.DataFrame,
                         observed_by_group: pd.DataFrame,
                         groups: list[str]) -> pd.DataFrame:
    """Calibration-in-the-large for each stratum."""
```

Subgroup strata: geopolitical zone (6), wealth quintile (5), maternal education (3), urban/rural (2).

## 5. RL Primary Analysis

### 5.1 Narrowed action space

Primary analysis uses {a₀, a₁, a₂} only — the three actions with meaningful data support (8.3% to 70.6%). a₃ (0.2%) and a₄ (0.0%) are excluded from RL learning.

### 5.2 Algorithm comparison

Train three offline RL algorithms on the same 3-action trajectory dataset:
- **CQL** — current approach, baseline
- **IQL** — expectile-based, avoids OOD queries
- **DiscreteBCQ** — behaviour-constrained, OOD near zero by construction

### 5.3 Selection criterion

Select the algorithm with the highest FQE policy value, subject to OOD frequency ≤ 10%. If none satisfies the constraint, report all three and describe the trade-off in the paper.

### 5.4 Expected results

| Algorithm | Expected OOD | Expected improvement |
|-----------|-------------|---------------------|
| CQL (3-action) | 5-15% | ~5% |
| IQL | 2-8% | 3-8% |
| DiscreteBCQ | <5% | 2-5% |

## 6. Microsimulation Scenarios

### 6.1 Primary (3-action)

| Scenario | Description |
|----------|-------------|
| S0 | Status quo (inferred behaviour policy) |
| S1 | Uniform SMS (a₁) |
| S2 | Uniform CHW (a₂) |
| S3 | Risk-targeted (top 30% dropout risk → a₂, rest → a₁) |
| S4 | RL-optimised (selected algorithm policy) |
| S5 | Bandit-allocated (LinUCB community-level with budget constraint) |

### 6.2 Sensitivity (5-action)

| Scenario | Description |
|----------|-------------|
| S6 | Recall-enhanced: top 10% risk → a₃, next 20% → a₂, rest → a₁ |
| S7 | Incentive for poorest: poorest quintile → a₄, rest → S3 rule |

Report S6 and S7 in supplementary materials. They use literature effect sizes for a₃ and a₄ without RL learning.

## 7. Validation Strategy

### 7.1 Internal calibration

Run S0 with inferred behaviour policy on the actual analytic sample (no bootstrap). Compare predicted DTP3 rate to observed (~85.2%). Acceptance: absolute error < 1 percentage point.

### 7.2 Subgroup validation

Stratify predicted vs observed DTP3 by: geopolitical zone (6), wealth quintile (5), maternal education (3), urban/rural (2). Report calibration-in-the-large per stratum. Flag any subgroup with absolute error > 3 pp.

## 8. Testing Strategy

### 8.1 Unit tests

- `test_transitions.py`: calibrator load, probability range, calibration slope in [0.9, 1.1]
- `test_interventions.py`: RRR range, clipping behaviour, Beta moments
- `test_costs.py`: non-negative, mean within 2% of point, Gamma parameterisation
- `test_equity.py`: concentration index = 0 for independent outcome, = 1 for perfect concentration
- `test_rl_common.py`: behaviour policy inference, action distribution, MDP shapes
- `test_ope.py`: recovers known answers on 2-state, 2-action toy MDP
- `test_microsim.py`: smoke test, cluster-bootstrap correctness, reproducibility
- `test_validation.py`: calibration correctness on synthetic perfectly-calibrated data

### 8.2 Integration tests

- `test_stage2_smoke.py`: each RL algorithm trains for 10 steps on subsample
- `test_stage3_smoke.py`: `run_stage3` on 100-child × 10-bootstrap subsample completes <30s

### 8.3 Coverage targets

- Core modules (transitions, interventions, costs, equity): ≥90%
- RL algorithms: ≥70%
- Microsim and sensitivity: ≥85%
- Overall: ≥80%

## 9. Execution Plan

### 9.1 Phased build

| Phase | Work | Days |
|-------|------|------|
| 1 | Scaffold package, pyproject.toml, move legacy scripts | 1 |
| 2 | Core modules: transitions, interventions, costs, equity | 3 |
| 3 | RL sub-package: common, CQL, IQL, BCQ, OPE | 3 |
| 4 | Microsim + validation | 2 |
| 5 | Sensitivity: tornado, CEAC, probabilistic ICER | 1 |
| 6 | Scripts: run_stage2, run_stage3, run_validation, run_sensitivity | 2 |
| 7 | Manuscript update: regenerate tables/figures, update Results + Methods | 1 |
| | **Total** | **13** |

### 9.2 Deliverables

- `src/dropout_rl/` package with tests passing and ≥80% coverage
- `outputs/stage2_v2/` with CQL/IQL/BCQ comparison and selected policy
- `outputs/stage3_v2/` with 8 scenarios, full PSA, CEAC, tornado, probabilistic ICER
- `outputs/validation/` with internal + subgroup validation report
- Updated `manuscript/` with new tables, figures, Methods/Results text
- `outputs/comparison_v1_vs_v2.md` documenting what changed and why
- `outputs/stage3_v2/manuscript_deltas.md` — exact text/number changes for each manuscript section

### 9.3 Comparison artefact

A single file documenting:
- Old results (v1 manuscript numbers)
- New results (v2 numbers)
- Which findings moved, which were robust
- What drove any changes

Protects the manuscript against reviewer questions about numerical changes between versions.

## 10. Problems Addressed

| Problem | Solution |
|---------|----------|
| GBM refitted instead of using Stage 1 models | `transitions.py` loads XGBoost + calibrators directly |
| No PSA | Integrated into `microsim.run_scenario` via PSA priors |
| Individual bootstrap understates CIs | Cluster-bootstrap on v021 PSUs |
| Single-point costs | Gamma priors in `costs.py` |
| Only wealth gap for equity | Add concentration index + SII |
| 33% OOD in RL | Narrow to {a₀, a₁, a₂}; compare CQL/IQL/BCQ |
| No validation | `validation.py` with internal + subgroup checks |
| No CEAC or probabilistic ICER | `sensitivity.py` with both |
| Monolithic scripts | Modular package with ≥80% test coverage |
| 5-action scenarios not supported by data | Primary 3-action; S6/S7 as sensitivity with literature RRR |

## 11. Out of Scope

- Changing Stage 1 (XGBoost models) — already recalibrated and published-grade
- Changing the data source (NDHS 2024 stays)
- Longitudinal re-formulation — data is cross-sectional
- New literature search — action-space calibration stays with current values
- Temporal validation using NDHS 2018 — deferred unless reviewers ask
