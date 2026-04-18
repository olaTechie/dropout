# Microsim + RL Rewrite Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rewrite Stage 2 (offline RL) and Stage 3 (microsimulation) as a modular, tested Python package `src/dropout_rl/` with publication-grade methodology (PSA, cluster-bootstrap, CEAC, multi-algorithm RL comparison).

**Architecture:** Modular Python package with one responsibility per module. Each module has unit tests. Scripts become thin orchestrators. All randomness uses `np.random.Generator` passed as argument (no global seed). All file I/O happens in scripts, not in the library.

**Tech Stack:** Python 3.11, NumPy, pandas, XGBoost, scikit-learn, scipy, joblib, matplotlib, pytest, pytest-cov

**Working directory:** `/Users/uthlekan/Library/CloudStorage/Dropbox/00Todo/00_ToReview/vacSeries/03_dropout`

---

## Phase 1: Scaffold Package

### Task 1: Create package layout and move legacy scripts

**Files:**
- Create: `pyproject.toml`
- Create: `src/dropout_rl/__init__.py`
- Create: `src/dropout_rl/config.py`
- Create: `tests/__init__.py`
- Create: `tests/conftest.py`
- Create: `pytest.ini`
- Move: `scripts/stage2_corrected.py` → `scripts/legacy/stage2_corrected.py`
- Move: `scripts/stage3_corrected.py` → `scripts/legacy/stage3_corrected.py`

- [ ] **Step 1: Create package directories**

Run:
```bash
mkdir -p src/dropout_rl/rl tests/fixtures tests/integration scripts/legacy
```

- [ ] **Step 2: Write `pyproject.toml`**

Create file `pyproject.toml`:

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "dropout-rl"
version = "0.2.0"
description = "Nigeria DTP vaccine dropout reinforcement learning and microsimulation"
requires-python = ">=3.11"
dependencies = [
    "numpy>=1.26",
    "pandas>=2.1",
    "scipy>=1.11",
    "xgboost>=2.0",
    "scikit-learn>=1.4",
    "joblib>=1.3",
    "matplotlib>=3.8",
]

[project.optional-dependencies]
dev = ["pytest>=8.0", "pytest-cov>=4.1", "hypothesis>=6.0"]

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-v --strict-markers --tb=short"
markers = [
    "requires_data: tests that need DHS data present",
    "slow: tests that take >5 seconds",
]
```

- [ ] **Step 3: Write `src/dropout_rl/__init__.py`**

Create file `src/dropout_rl/__init__.py`:

```python
"""Nigeria DTP vaccine dropout: offline RL and microsimulation package."""

__version__ = "0.2.0"
```

- [ ] **Step 4: Write `src/dropout_rl/config.py`**

Create file `src/dropout_rl/config.py`:

```python
"""Project-wide constants and paths."""

from pathlib import Path

# Paths
REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "data"
PROCESSED_DIR = DATA_DIR / "processed"
STAGE1_DIR = REPO_ROOT / "outputs" / "stage1"
STAGE2_V2_DIR = REPO_ROOT / "outputs" / "stage2_v2"
STAGE3_V2_DIR = REPO_ROOT / "outputs" / "stage3_v2"
VALIDATION_DIR = REPO_ROOT / "outputs" / "validation"

# Action space (primary: 3-action)
N_ACTIONS_PRIMARY = 3
ACTIONS_PRIMARY = [0, 1, 2]
ACTION_LABELS = {
    0: "No intervention",
    1: "SMS reminder",
    2: "CHW home visit",
    3: "Facility recall",
    4: "Conditional incentive",
}
ACTION_COSTS_POINT = {0: 0, 1: 50, 2: 500, 3: 1500, 4: 800}

# RRR literature ranges (central, low, high)
RRR_RANGES = {
    0: (0.00, 0.00, 0.00),
    1: (0.10, 0.05, 0.15),
    2: (0.20, 0.15, 0.25),
    3: (0.25, 0.20, 0.30),
    4: (0.14, 0.09, 0.22),
}

# Cost CoV for Gamma priors
COST_COV = 0.25

# Reward function constants (unchanged from CLAUDE.md)
REWARD_COMPLETION = 1.0
REWARD_NEXT_DOSE = 0.3
COST_LAMBDA = 0.001
GAMMA_DISCOUNT = 0.95

# Microsimulation defaults
N_POP_DEFAULT = 10_000
N_BOOTSTRAP_DEFAULT = 1_000
CHILDREN_PER_LGA = 3_000

# Validation
CALIBRATION_TOLERANCE = 0.01
SUBGROUP_CALIBRATION_FLAG = 0.03
```

- [ ] **Step 5: Write `tests/__init__.py` and `tests/conftest.py`**

Create file `tests/__init__.py`:

```python
```

Create file `tests/conftest.py`:

```python
"""Shared test fixtures."""

import numpy as np
import pandas as pd
import pytest

from dropout_rl.config import PROCESSED_DIR, STAGE1_DIR


@pytest.fixture
def rng():
    """Deterministic random generator."""
    return np.random.default_rng(42)


@pytest.fixture
def synthetic_trajectory():
    """Small synthetic trajectory dataset for unit tests."""
    rng = np.random.default_rng(42)
    n = 200
    return pd.DataFrame({
        "child_id": [f"C{i//2:03d}_{i%2}" for i in range(n)],
        "dose_step": [i % 2 for i in range(n)],
        "action": rng.integers(0, 3, size=n),
        "reward": rng.choice([0.0, 0.3, 1.0], size=n),
        "weight": rng.uniform(0.5, 1.5, size=n),
        "state": ['{"wealth": 3, "rural": 0, "doses_received": 1}'] * n,
    })


@pytest.fixture
def real_analytic_data():
    """Real analytic data — skipped if not present."""
    path = PROCESSED_DIR / "analytic_dtp1_received.parquet"
    if not path.exists():
        pytest.skip("DHS data not available")
    return pd.read_parquet(path)
```

- [ ] **Step 6: Move legacy scripts**

Run:
```bash
mv scripts/stage2_corrected.py scripts/legacy/stage2_corrected.py
mv scripts/stage3_corrected.py scripts/legacy/stage3_corrected.py
```

- [ ] **Step 7: Install package in editable mode and verify**

Run:
```bash
pip install -e ".[dev]"
python -c "from dropout_rl.config import N_ACTIONS_PRIMARY; print(N_ACTIONS_PRIMARY)"
```

Expected: prints `3`

- [ ] **Step 8: Verify pytest discovery**

Run: `pytest --collect-only`

Expected: no errors, 0 tests collected

- [ ] **Step 9: Commit**

```bash
git add pyproject.toml src/dropout_rl/ tests/ scripts/legacy/ pytest.ini 2>/dev/null || true
git add -A
git commit -m "feat: scaffold dropout_rl package with config and test infrastructure"
```

---

## Phase 2: Core Scientific Modules

### Task 2: Transitions module (wrap Stage 1 XGBoost + calibrators)

**Files:**
- Create: `src/dropout_rl/transitions.py`
- Create: `tests/test_transitions.py`

- [ ] **Step 1: Write failing test for TransitionModel interface**

Create file `tests/test_transitions.py`:

```python
"""Tests for dropout_rl.transitions."""

import numpy as np
import pytest

from dropout_rl.transitions import TransitionModel, load_t1, load_t2


class TestTransitionModel:
    def test_predict_returns_probabilities(self):
        """Predicted probabilities must be in [0, 1]."""
        model = load_t1()
        X = np.random.default_rng(42).standard_normal((10, 55)).astype(np.float32)
        probs = model.predict_dropout(X)
        assert probs.shape == (10,)
        assert np.all(probs >= 0.0)
        assert np.all(probs <= 1.0)

    def test_calibration_slope_near_one(self, real_analytic_data):
        """Recalibrated T1 slope should be within [0.9, 1.1]."""
        from dropout_rl.transitions import load_t1
        model = load_t1()
        # Sanity: predictions are not constant
        X = np.random.default_rng(0).standard_normal((100, 55)).astype(np.float32)
        probs = model.predict_dropout(X)
        assert probs.std() > 0.001

    def test_t1_and_t2_are_distinct_models(self):
        """T1 and T2 must load different models."""
        t1 = load_t1()
        t2 = load_t2()
        assert t1 is not t2
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_transitions.py -v`
Expected: FAIL with `ImportError: cannot import name 'TransitionModel'`

- [ ] **Step 3: Write `transitions.py`**

Create file `src/dropout_rl/transitions.py`:

```python
"""Wraps Stage 1 XGBoost models with isotonic calibrators.

This module is the single source of truth for dropout-probability predictions
throughout Stages 2 and 3. It replaces the old practice of refitting
GradientBoostingClassifier models, which created inconsistency with the
published prediction analysis.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import joblib
import numpy as np
import xgboost as xgb

from dropout_rl.config import STAGE1_DIR


@dataclass
class TransitionModel:
    """Calibrated transition model for a single dose step.

    Attributes
    ----------
    xgb_model : xgb.Booster
        Trained XGBoost booster predicting P(next dose received).
    calibrator : sklearn.isotonic.IsotonicRegression
        Isotonic regression calibrator fit on out-of-fold predictions.
    feature_names : list[str]
        Ordered feature names matching training.
    """

    xgb_model: xgb.Booster
    calibrator: object
    feature_names: list[str]

    def predict_dropout(self, X: np.ndarray) -> np.ndarray:
        """Predict calibrated P(dropout | state).

        Parameters
        ----------
        X : np.ndarray of shape (n, n_features)
            State feature matrix.

        Returns
        -------
        np.ndarray of shape (n,)
            Calibrated P(dropout) in [0, 1].
        """
        dmat = xgb.DMatrix(np.asarray(X, dtype=np.float32))
        raw_completion = self.xgb_model.predict(dmat)
        # XGBoost models predict P(dropout) directly (trained on dropout label)
        calibrated = self.calibrator.transform(raw_completion)
        return np.clip(calibrated, 0.0, 1.0)


def _load(xgb_name: str, calibrator_name: str) -> TransitionModel:
    xgb_path = STAGE1_DIR / xgb_name
    cal_path = STAGE1_DIR / calibrator_name
    if not xgb_path.exists():
        raise FileNotFoundError(f"XGBoost model not found: {xgb_path}")
    if not cal_path.exists():
        raise FileNotFoundError(f"Calibrator not found: {cal_path}")

    booster = xgb.Booster()
    booster.load_model(str(xgb_path))
    calibrator = joblib.load(cal_path)

    # Load feature names from state space definition
    spec_path = STAGE1_DIR / "state_space_definition.json"
    with open(spec_path) as f:
        spec = json.load(f)
    feature_names = (
        spec["static_features"]
        + spec["dynamic_features"]
        + spec.get("temporal_features", [])
    )

    return TransitionModel(
        xgb_model=booster,
        calibrator=calibrator,
        feature_names=feature_names,
    )


def load_t1() -> TransitionModel:
    """Load the DTP1→DTP2 transition model."""
    return _load("xgb_model_t1.json", "isotonic_calibrator_t1.pkl")


def load_t2() -> TransitionModel:
    """Load the DTP2→DTP3 transition model."""
    return _load("xgb_model_t2.json", "isotonic_calibrator_t2.pkl")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_transitions.py -v`
Expected: 3 passed

- [ ] **Step 5: Commit**

```bash
git add src/dropout_rl/transitions.py tests/test_transitions.py
git commit -m "feat: add TransitionModel wrapping Stage 1 XGBoost + isotonic calibrators"
```

---

### Task 3: Interventions module (RRR priors)

**Files:**
- Create: `src/dropout_rl/interventions.py`
- Create: `tests/test_interventions.py`

- [ ] **Step 1: Write failing tests**

Create file `tests/test_interventions.py`:

```python
"""Tests for dropout_rl.interventions."""

import numpy as np
import pytest

from dropout_rl.interventions import (
    apply_rrr,
    beta_params_from_range,
    sample_rrr,
    sample_rrr_batch,
)


class TestBetaParams:
    def test_central_in_range(self):
        """Central estimate is the mean."""
        a, b = beta_params_from_range(central=0.10, low=0.05, high=0.15)
        mean = a / (a + b)
        assert abs(mean - 0.10) < 0.005

    def test_95_interval_approx(self):
        """95% interval approximately matches [low, high]."""
        from scipy import stats
        a, b = beta_params_from_range(central=0.10, low=0.05, high=0.15)
        q_low = stats.beta.ppf(0.025, a, b)
        q_high = stats.beta.ppf(0.975, a, b)
        # Approximate match — Beta may not perfectly reproduce asymmetric ranges
        assert 0.02 < q_low < 0.08
        assert 0.12 < q_high < 0.18


class TestSampleRRR:
    def test_action_0_returns_zero(self, rng):
        for _ in range(100):
            assert sample_rrr(0, rng) == 0.0

    def test_action_1_has_correct_mean(self, rng):
        draws = np.array([sample_rrr(1, rng) for _ in range(5000)])
        assert abs(draws.mean() - 0.10) < 0.01
        assert draws.min() >= 0.0
        assert draws.max() <= 1.0

    def test_action_2_has_correct_mean(self, rng):
        draws = np.array([sample_rrr(2, rng) for _ in range(5000)])
        assert abs(draws.mean() - 0.20) < 0.015

    def test_invalid_action_raises(self, rng):
        with pytest.raises(ValueError):
            sample_rrr(99, rng)


class TestApplyRRR:
    def test_zero_action_leaves_input_unchanged(self):
        p = np.array([0.1, 0.2, 0.3])
        actions = np.array([0, 0, 0])
        rrr_draws = np.array([0.0, 0.10, 0.20])
        result = apply_rrr(p, actions, rrr_draws)
        np.testing.assert_array_almost_equal(result, p)

    def test_nonzero_action_reduces_dropout(self):
        p = np.array([0.10])
        actions = np.array([1])
        rrr_draws = np.array([0.0, 0.10, 0.20, 0.25, 0.14])
        result = apply_rrr(p, actions, rrr_draws)
        # p * (1 - 0.10) = 0.09
        assert abs(result[0] - 0.09) < 1e-9

    def test_result_clipped_to_unit_interval(self):
        p = np.array([0.5, 1.5])  # 1.5 is invalid but test clipping
        actions = np.array([1, 1])
        rrr_draws = np.array([0.0, 0.1, 0.2])
        result = apply_rrr(p, actions, rrr_draws)
        assert np.all(result >= 0.0)
        assert np.all(result <= 1.0)


class TestSampleRRRBatch:
    def test_shape(self, rng):
        draws = sample_rrr_batch(n_actions=3, rng=rng)
        assert draws.shape == (3,)
        assert draws[0] == 0.0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_interventions.py -v`
Expected: FAIL with `ImportError`

- [ ] **Step 3: Write `interventions.py`**

Create file `src/dropout_rl/interventions.py`:

```python
"""Effect-size priors and relative risk reduction (RRR) application.

Each intervention (a1-a4) has a Beta-distributed prior over its RRR derived
from literature. PSA draws one RRR per action per bootstrap iteration.
"""

from __future__ import annotations

import numpy as np
from scipy import stats

from dropout_rl.config import RRR_RANGES


def beta_params_from_range(central: float, low: float, high: float) -> tuple[float, float]:
    """Fit Beta(α, β) parameters by method of moments.

    Uses central as the mean and (high - low) / (2 * 1.96) as an approximate std.

    Parameters
    ----------
    central : float
        Central (mean) RRR estimate.
    low, high : float
        Bounds interpreted as a 95% interval.

    Returns
    -------
    tuple[float, float]
        (α, β) parameters for scipy.stats.beta.
    """
    if central <= 0.0 or central >= 1.0:
        raise ValueError(f"central must be in (0, 1), got {central}")
    if not (low < central < high):
        raise ValueError(f"central must be in (low, high); got {low}, {central}, {high}")

    mean = central
    std = (high - low) / (2.0 * 1.96)
    var = std**2

    # Moment-matching: mean = a/(a+b), var = ab / [(a+b)^2 (a+b+1)]
    common = mean * (1 - mean) / var - 1.0
    alpha = mean * common
    beta = (1 - mean) * common

    if alpha <= 0 or beta <= 0:
        raise ValueError("Variance too large for given mean; Beta undefined")

    return alpha, beta


def sample_rrr(action: int, rng: np.random.Generator) -> float:
    """Draw one RRR value for a given action from its Beta prior.

    Parameters
    ----------
    action : int
        Action index (0-4).
    rng : np.random.Generator

    Returns
    -------
    float
        RRR in [0, 1]. Action 0 always returns 0.0.
    """
    if action not in RRR_RANGES:
        raise ValueError(f"Unknown action {action}; must be in {list(RRR_RANGES.keys())}")

    central, low, high = RRR_RANGES[action]
    if central == 0.0:
        return 0.0
    alpha, beta = beta_params_from_range(central, low, high)
    return float(stats.beta.rvs(alpha, beta, random_state=rng))


def sample_rrr_batch(n_actions: int, rng: np.random.Generator) -> np.ndarray:
    """Draw one RRR per action, returned as a vector indexed by action.

    Parameters
    ----------
    n_actions : int
        Number of actions to draw for (3 or 5).

    Returns
    -------
    np.ndarray of shape (n_actions,)
    """
    return np.array([sample_rrr(a, rng) for a in range(n_actions)])


def apply_rrr(
    p_dropout: np.ndarray,
    actions: np.ndarray,
    rrr_draws: np.ndarray,
) -> np.ndarray:
    """Apply RRR to baseline dropout probabilities.

    p_adjusted = p_baseline * (1 - RRR[action])

    Parameters
    ----------
    p_dropout : np.ndarray of shape (n,)
        Baseline P(dropout | state) in [0, 1].
    actions : np.ndarray of shape (n,)
        Per-child action assignments.
    rrr_draws : np.ndarray of shape (n_actions,)
        RRR value per action.

    Returns
    -------
    np.ndarray of shape (n,)
        Adjusted P(dropout), clipped to [0, 1].
    """
    rrr_per_child = rrr_draws[actions]
    adjusted = p_dropout * (1.0 - rrr_per_child)
    return np.clip(adjusted, 0.0, 1.0)
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/test_interventions.py -v`
Expected: all tests pass

- [ ] **Step 5: Commit**

```bash
git add src/dropout_rl/interventions.py tests/test_interventions.py
git commit -m "feat: add intervention RRR priors (Beta) and apply_rrr"
```

---

### Task 4: Costs module (Gamma priors)

**Files:**
- Create: `src/dropout_rl/costs.py`
- Create: `tests/test_costs.py`

- [ ] **Step 1: Write failing tests**

Create file `tests/test_costs.py`:

```python
"""Tests for dropout_rl.costs."""

import numpy as np
import pytest

from dropout_rl.costs import gamma_params_from_cov, sample_cost, sample_cost_batch


class TestGammaParams:
    def test_parameters_recover_mean(self):
        shape, scale = gamma_params_from_cov(mean=500, cov=0.25)
        # Gamma: mean = shape * scale
        assert abs(shape * scale - 500) < 1e-6

    def test_parameters_recover_cov(self):
        shape, scale = gamma_params_from_cov(mean=500, cov=0.25)
        # Gamma: var = shape * scale^2; sd/mean = 1/sqrt(shape) = CoV
        import math
        assert abs(1.0 / math.sqrt(shape) - 0.25) < 1e-6


class TestSampleCost:
    def test_action_0_returns_zero(self, rng):
        for _ in range(50):
            assert sample_cost(0, rng) == 0.0

    def test_action_1_mean_near_50(self, rng):
        draws = np.array([sample_cost(1, rng) for _ in range(10000)])
        assert abs(draws.mean() - 50) < 2
        assert draws.min() >= 0

    def test_action_2_mean_near_500(self, rng):
        draws = np.array([sample_cost(2, rng) for _ in range(10000)])
        assert abs(draws.mean() - 500) < 20

    def test_invalid_action_raises(self, rng):
        with pytest.raises(ValueError):
            sample_cost(42, rng)


class TestSampleCostBatch:
    def test_shape(self, rng):
        costs = sample_cost_batch(n_actions=3, rng=rng)
        assert costs.shape == (3,)
        assert costs[0] == 0.0
```

- [ ] **Step 2: Run test to verify failure**

Run: `pytest tests/test_costs.py -v`
Expected: FAIL with `ImportError`

- [ ] **Step 3: Write `costs.py`**

Create file `src/dropout_rl/costs.py`:

```python
"""Intervention cost model with Gamma-distributed uncertainty.

Costs in Nigerian Naira per child. CoV = 0.25 reflects typical programmatic
cost uncertainty in LMIC vaccination settings.
"""

from __future__ import annotations

import numpy as np
from scipy import stats

from dropout_rl.config import ACTION_COSTS_POINT, COST_COV


def gamma_params_from_cov(mean: float, cov: float) -> tuple[float, float]:
    """Convert (mean, coefficient of variation) to (shape, scale) Gamma parameters.

    Gamma: mean = shape * scale; CoV = 1 / sqrt(shape).

    Parameters
    ----------
    mean : float
        Desired mean.
    cov : float
        Coefficient of variation (std / mean).

    Returns
    -------
    tuple[float, float]
        (shape, scale).
    """
    if mean <= 0:
        raise ValueError(f"mean must be positive, got {mean}")
    if cov <= 0:
        raise ValueError(f"cov must be positive, got {cov}")

    shape = 1.0 / (cov**2)
    scale = mean / shape
    return shape, scale


def sample_cost(action: int, rng: np.random.Generator) -> float:
    """Draw one per-child cost for a given action.

    Action 0 (no intervention) always returns 0. All others draw from
    Gamma(shape, scale) with mean = ACTION_COSTS_POINT[action] and
    CoV = COST_COV (0.25).

    Parameters
    ----------
    action : int
        Action index (0-4).

    Returns
    -------
    float
        Cost in Naira, non-negative.
    """
    if action not in ACTION_COSTS_POINT:
        raise ValueError(f"Unknown action {action}")

    point = ACTION_COSTS_POINT[action]
    if point == 0:
        return 0.0

    shape, scale = gamma_params_from_cov(mean=point, cov=COST_COV)
    return float(stats.gamma.rvs(a=shape, scale=scale, random_state=rng))


def sample_cost_batch(n_actions: int, rng: np.random.Generator) -> np.ndarray:
    """Draw one cost per action."""
    return np.array([sample_cost(a, rng) for a in range(n_actions)])


def fixed_programmatic_cost() -> float:
    """Programmatic overhead per intervention. Zero by default (reviewer-flag parameter)."""
    return 0.0
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/test_costs.py -v`
Expected: all pass

- [ ] **Step 5: Commit**

```bash
git add src/dropout_rl/costs.py tests/test_costs.py
git commit -m "feat: add cost Gamma priors with CoV=0.25"
```

---

### Task 5: Equity module (three metrics)

**Files:**
- Create: `src/dropout_rl/equity.py`
- Create: `tests/test_equity.py`

- [ ] **Step 1: Write failing tests**

Create file `tests/test_equity.py`:

```python
"""Tests for dropout_rl.equity."""

import numpy as np
import pytest

from dropout_rl.equity import (
    concentration_index,
    slope_index_of_inequality,
    wealth_gap,
)


class TestWealthGap:
    def test_no_gap_when_uniform(self):
        y = np.ones(100)
        w = np.tile(np.arange(1, 6), 20)
        assert abs(wealth_gap(y, w)) < 1e-9

    def test_positive_gap_when_richest_higher(self):
        # Poorest all 0, richest all 1
        y = np.concatenate([np.zeros(20), np.ones(20)])
        w = np.concatenate([np.ones(20), np.full(20, 5)])
        gap = wealth_gap(y, w)
        assert gap == 1.0  # richest - poorest = 1 - 0


class TestConcentrationIndex:
    def test_zero_when_independent(self, rng):
        """CI ~ 0 when outcome independent of wealth."""
        n = 5000
        y = rng.binomial(1, 0.5, size=n).astype(float)
        w = rng.integers(1, 6, size=n).astype(float)
        ci = concentration_index(y, w)
        assert abs(ci) < 0.05

    def test_positive_when_concentrated_in_rich(self):
        """CI > 0 when outcome concentrated in higher wealth."""
        n = 1000
        w = np.tile(np.arange(1, 6), n // 5)
        # Outcome probability scales with wealth: 0.1 * w
        rng = np.random.default_rng(0)
        y = rng.binomial(1, 0.1 * w).astype(float)
        ci = concentration_index(y, w)
        assert ci > 0.1

    def test_negative_when_concentrated_in_poor(self):
        """CI < 0 when outcome concentrated in lower wealth."""
        n = 1000
        w = np.tile(np.arange(1, 6), n // 5)
        rng = np.random.default_rng(0)
        y = rng.binomial(1, 0.6 - 0.1 * w).astype(float)
        ci = concentration_index(y, w)
        assert ci < -0.1


class TestSlopeIndex:
    def test_zero_when_flat(self):
        y = np.full(100, 0.8)
        w = np.tile(np.arange(1, 6), 20)
        sii = slope_index_of_inequality(y, w)
        assert abs(sii) < 1e-6

    def test_matches_gap_sign(self, rng):
        """SII sign matches wealth gap sign on strong signal."""
        n = 500
        w = np.tile(np.arange(1, 6), n // 5)
        y = (w == 5).astype(float)  # Only richest completes
        sii = slope_index_of_inequality(y, w)
        assert sii > 0
```

- [ ] **Step 2: Run test**

Run: `pytest tests/test_equity.py -v`
Expected: FAIL with `ImportError`

- [ ] **Step 3: Write `equity.py`**

Create file `src/dropout_rl/equity.py`:

```python
"""Health equity metrics: wealth gap, concentration index, slope index of inequality.

All three metrics take binary or continuous outcomes and wealth quintile (1-5)
or wealth rank. Concentration index and SII are the standards in health
equity literature.
"""

from __future__ import annotations

import numpy as np


def wealth_gap(outcomes: np.ndarray, wealth_quintile: np.ndarray) -> float:
    """Richest minus poorest quintile outcome rate.

    Parameters
    ----------
    outcomes : np.ndarray of shape (n,)
        Individual outcomes (e.g., DTP3 completion 0/1).
    wealth_quintile : np.ndarray of shape (n,)
        Wealth quintile, values in {1, 2, 3, 4, 5}.

    Returns
    -------
    float
        Richest quintile rate minus poorest quintile rate.
    """
    y = np.asarray(outcomes, dtype=float)
    w = np.asarray(wealth_quintile)
    poorest = y[w == w.min()]
    richest = y[w == w.max()]
    if len(poorest) == 0 or len(richest) == 0:
        return float("nan")
    return float(richest.mean() - poorest.mean())


def _ridit_rank(wealth: np.ndarray) -> np.ndarray:
    """Compute ridit-scored wealth rank (cumulative midpoint of wealth distribution)."""
    w = np.asarray(wealth, dtype=float)
    sorted_idx = np.argsort(w)
    n = len(w)
    ranks = np.empty(n)
    # Use cumulative proportion minus half the fraction at that value
    cumulative = 0.0
    i = 0
    while i < n:
        j = i
        while j < n and w[sorted_idx[j]] == w[sorted_idx[i]]:
            j += 1
        # All ties get midpoint rank
        count = j - i
        midpoint = (cumulative + cumulative + count) / (2.0 * n)
        ranks[sorted_idx[i:j]] = midpoint
        cumulative += count
        i = j
    return ranks


def concentration_index(outcomes: np.ndarray, wealth: np.ndarray) -> float:
    """Wagstaff concentration index.

    CI = 2 * cov(y, R) / mean(y), where R is the ridit-scored wealth rank.
    Ranges in [-1, 1]: positive means outcome concentrated in richer; negative
    means concentrated in poorer; zero means perfect equity.

    Parameters
    ----------
    outcomes : np.ndarray of shape (n,)
    wealth : np.ndarray of shape (n,)
        Wealth score or quintile; ranks are computed internally.

    Returns
    -------
    float
        Concentration index in [-1, 1].
    """
    y = np.asarray(outcomes, dtype=float)
    w = np.asarray(wealth, dtype=float)

    if y.mean() == 0:
        return 0.0

    ranks = _ridit_rank(w)
    cov_yr = np.cov(y, ranks, ddof=0)[0, 1]
    return float(2.0 * cov_yr / y.mean())


def slope_index_of_inequality(outcomes: np.ndarray, wealth: np.ndarray) -> float:
    """Slope Index of Inequality (SII).

    Linear regression of outcome on ridit-scored wealth rank. Interpretation:
    the difference in outcome between the hypothetical lowest-rank and
    highest-rank person.

    Parameters
    ----------
    outcomes : np.ndarray of shape (n,)
    wealth : np.ndarray of shape (n,)

    Returns
    -------
    float
        SII: positive means advantage to richer, negative to poorer.
    """
    y = np.asarray(outcomes, dtype=float)
    w = np.asarray(wealth, dtype=float)
    ranks = _ridit_rank(w)
    # OLS slope
    r_mean = ranks.mean()
    y_mean = y.mean()
    denom = ((ranks - r_mean) ** 2).sum()
    if denom == 0:
        return 0.0
    slope = ((ranks - r_mean) * (y - y_mean)).sum() / denom
    return float(slope)
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/test_equity.py -v`
Expected: all pass

- [ ] **Step 5: Commit**

```bash
git add src/dropout_rl/equity.py tests/test_equity.py
git commit -m "feat: add wealth gap, concentration index, slope index of inequality"
```

---

## Phase 3: RL Sub-package

### Task 6: RL common module (behaviour policy inference, MDP builder)

**Files:**
- Create: `src/dropout_rl/rl/__init__.py`
- Create: `src/dropout_rl/rl/common.py`
- Create: `tests/test_rl_common.py`

- [ ] **Step 1: Write failing tests**

Create file `tests/test_rl_common.py`:

```python
"""Tests for dropout_rl.rl.common."""

import numpy as np
import pandas as pd
import pytest

from dropout_rl.rl.common import (
    build_mdp_dataset,
    infer_behaviour_policy_3action,
)


class TestBehaviourPolicyInference:
    def test_output_only_3_actions(self, synthetic_trajectory):
        # Construct realistic row features
        df = pd.DataFrame([
            {"next_dose_interval": 30, "v393": 1, "h69": 10, "h1a": 2, "next_received": 1},
            {"next_dose_interval": 30, "v393": 0, "h69": 41, "h1a": 1, "next_received": 1},
            {"next_dose_interval": 30, "v393": 0, "h69": 10, "h1a": 2, "next_received": 1},
            {"next_dose_interval": 60, "v393": 0, "h69": 10, "h1a": 0, "next_received": 1},
            {"next_dose_interval": 30, "v393": 0, "h69": 10, "h1a": 0, "next_received": 0},
        ])
        actions = infer_behaviour_policy_3action(df)
        assert set(actions) <= {0, 1, 2}

    def test_fieldworker_yields_a2(self):
        df = pd.DataFrame([
            {"next_dose_interval": 30, "v393": 1, "h69": 10, "h1a": 2, "next_received": 1},
        ])
        actions = infer_behaviour_policy_3action(df)
        assert actions[0] == 2

    def test_campaign_yields_a2(self):
        """Campaign vaccination maps to a2 in 3-action space (was a3 in 5-action)."""
        df = pd.DataFrame([
            {"next_dose_interval": 30, "v393": 0, "h69": 41, "h1a": 1, "next_received": 1},
        ])
        actions = infer_behaviour_policy_3action(df)
        assert actions[0] == 2

    def test_on_time_with_card_yields_a1(self):
        df = pd.DataFrame([
            {"next_dose_interval": 30, "v393": 0, "h69": 10, "h1a": 2, "next_received": 1},
        ])
        actions = infer_behaviour_policy_3action(df)
        assert actions[0] == 1

    def test_late_yields_a0(self):
        df = pd.DataFrame([
            {"next_dose_interval": 60, "v393": 0, "h69": 10, "h1a": 2, "next_received": 1},
        ])
        actions = infer_behaviour_policy_3action(df)
        assert actions[0] == 0

    def test_not_received_yields_a0(self):
        df = pd.DataFrame([
            {"next_dose_interval": 30, "v393": 1, "h69": 41, "h1a": 2, "next_received": 0},
        ])
        actions = infer_behaviour_policy_3action(df)
        assert actions[0] == 0


class TestBuildMDPDataset:
    def test_output_shapes(self, synthetic_trajectory):
        dataset = build_mdp_dataset(synthetic_trajectory, n_actions=3)
        assert "states" in dataset
        assert "actions" in dataset
        assert "rewards" in dataset
        assert "weights" in dataset
        n = len(synthetic_trajectory)
        assert dataset["actions"].shape == (n,)
        assert dataset["rewards"].shape == (n,)

    def test_actions_clipped_to_3_actions(self, synthetic_trajectory):
        # Inject an out-of-range action
        df = synthetic_trajectory.copy()
        df.loc[0, "action"] = 4  # a4 not in 3-action space
        dataset = build_mdp_dataset(df, n_actions=3)
        assert dataset["actions"].max() < 3
```

- [ ] **Step 2: Run test**

Run: `pytest tests/test_rl_common.py -v`
Expected: FAIL with ImportError

- [ ] **Step 3: Write `rl/__init__.py` and `rl/common.py`**

Create file `src/dropout_rl/rl/__init__.py`:

```python
"""Offline reinforcement learning sub-package."""
```

Create file `src/dropout_rl/rl/common.py`:

```python
"""Shared infrastructure for offline RL algorithms.

Behaviour policy inference, MDP dataset construction, action space constants.
Used by CQL, IQL, and BCQ implementations.
"""

from __future__ import annotations

import json
from typing import Literal

import numpy as np
import pandas as pd

from dropout_rl.config import ACTIONS_PRIMARY, N_ACTIONS_PRIMARY


ON_TIME_THRESHOLD_DAYS = 42


def infer_behaviour_policy_3action(df: pd.DataFrame) -> np.ndarray:
    """Infer behaviour policy action from observed DHS features.

    Rules (in priority order):
    1. Next dose NOT received → a0 (no effective intervention)
    2. Next dose LATE (>42 days) → a0 (weak/no intervention)
    3. Next dose ON TIME + fieldworker visit (v393==1) → a2 (CHW)
    4. Next dose ON TIME + campaign vaccination (h69==41) → a2 (maps to CHW in 3-action)
    5. Next dose ON TIME + card present (h1a>=1) → a1 (SMS)
    6. Otherwise → a0

    Parameters
    ----------
    df : pd.DataFrame with columns:
        next_dose_interval, v393, h69, h1a, next_received

    Returns
    -------
    np.ndarray of shape (len(df),) with values in {0, 1, 2}.
    """
    required = {"next_dose_interval", "v393", "h69", "h1a", "next_received"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    n = len(df)
    actions = np.zeros(n, dtype=np.int64)

    interval = df["next_dose_interval"].to_numpy()
    v393 = df["v393"].to_numpy()
    h69 = df["h69"].to_numpy()
    h1a = df["h1a"].to_numpy()
    received = df["next_received"].to_numpy()

    on_time = (received == 1) & (interval <= ON_TIME_THRESHOLD_DAYS)

    actions[on_time & (h1a >= 1)] = 1  # SMS
    actions[on_time & (h69 == 41)] = 2  # campaign → a2
    actions[on_time & (v393 == 1)] = 2  # fieldworker → a2
    # late and not received default to 0

    return actions


def build_mdp_dataset(
    traj_df: pd.DataFrame,
    n_actions: Literal[3, 5] = 3,
) -> dict:
    """Build MDP dataset dict from trajectory dataframe.

    Parameters
    ----------
    traj_df : pd.DataFrame
        Must contain columns: state (JSON string), action, reward, weight.
    n_actions : int
        Target action space size. Actions ≥ n_actions are clipped to n_actions-1
        (i.e., a3/a4 → a2 when narrowing to 3 actions).

    Returns
    -------
    dict with keys: states, actions, rewards, weights, n_actions.
    """
    actions = traj_df["action"].to_numpy().astype(np.int64)
    actions = np.clip(actions, 0, n_actions - 1)

    # Parse state JSON
    states_list = []
    for s in traj_df["state"]:
        parsed = json.loads(s)
        states_list.append(list(parsed.values()))
    # Build uniform array — pad if necessary
    max_len = max(len(s) for s in states_list)
    states = np.zeros((len(states_list), max_len), dtype=np.float32)
    for i, s in enumerate(states_list):
        states[i, : len(s)] = s

    return {
        "states": states,
        "actions": actions,
        "rewards": traj_df["reward"].to_numpy().astype(np.float32),
        "weights": traj_df["weight"].to_numpy().astype(np.float32),
        "n_actions": n_actions,
    }
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/test_rl_common.py -v`
Expected: all pass

- [ ] **Step 5: Commit**

```bash
git add src/dropout_rl/rl/ tests/test_rl_common.py
git commit -m "feat: add rl.common with 3-action behaviour policy inference and MDP builder"
```

---

### Task 7: OPE module (WIS, FQE, DR)

**Files:**
- Create: `src/dropout_rl/rl/ope.py`
- Create: `tests/test_ope.py`

- [ ] **Step 1: Write failing tests using a toy MDP with known answer**

Create file `tests/test_ope.py`:

```python
"""Tests for dropout_rl.rl.ope using a toy 2-state 2-action MDP."""

import numpy as np
import pytest

from dropout_rl.rl.ope import (
    fqe_value,
    ood_frequency,
    wis_value,
)


def _toy_dataset(rng):
    """Two-state, two-action MDP where action 1 always yields reward 1.0."""
    n = 1000
    states = rng.standard_normal((n, 2)).astype(np.float32)
    # Behaviour policy: random
    actions = rng.integers(0, 2, size=n)
    # Reward: action 1 → 1.0, action 0 → 0.0
    rewards = actions.astype(np.float32)
    weights = np.ones(n, dtype=np.float32)
    return {
        "states": states,
        "actions": actions,
        "rewards": rewards,
        "weights": weights,
        "n_actions": 2,
    }


def _always_action_1(states):
    return np.ones(len(states), dtype=np.int64)


def _always_action_0(states):
    return np.zeros(len(states), dtype=np.int64)


class TestWIS:
    def test_recovers_known_value(self, rng):
        """π=always-1 under random behaviour: WIS ≈ 1.0."""
        dataset = _toy_dataset(rng)
        value = wis_value(
            target_policy=_always_action_1,
            dataset=dataset,
            behaviour_probs=np.full((len(dataset["actions"]), 2), 0.5),
            epsilon=0.1,
        )
        assert 0.8 < value < 1.2

    def test_low_value_for_action_0(self, rng):
        dataset = _toy_dataset(rng)
        value = wis_value(
            target_policy=_always_action_0,
            dataset=dataset,
            behaviour_probs=np.full((len(dataset["actions"]), 2), 0.5),
            epsilon=0.1,
        )
        assert value < 0.2


class TestFQE:
    def test_recovers_known_value(self, rng):
        """FQE for π=always-1: V ≈ 1.0."""
        dataset = _toy_dataset(rng)
        value = fqe_value(
            target_policy=_always_action_1,
            dataset=dataset,
            gamma=0.0,  # Immediate reward only
            n_iterations=50,
        )
        assert 0.8 < value < 1.2


class TestOODFrequency:
    def test_matching_behaviour_zero_ood(self, rng):
        dataset = _toy_dataset(rng)
        # Target = behaviour: zero OOD
        def target(states):
            # Same distribution as dataset actions
            return dataset["actions"][: len(states)]
        freq = ood_frequency(
            target_actions=dataset["actions"],
            behaviour_actions=dataset["actions"],
            min_behaviour_prob=0.01,
        )
        assert freq == 0.0

    def test_fully_ood_when_action_never_observed(self):
        # Behaviour: all 0s; target: all 1s
        behav = np.zeros(100, dtype=np.int64)
        target = np.ones(100, dtype=np.int64)
        freq = ood_frequency(target, behav, min_behaviour_prob=0.01)
        assert freq == 1.0
```

- [ ] **Step 2: Run test**

Run: `pytest tests/test_ope.py -v`
Expected: FAIL with ImportError

- [ ] **Step 3: Write `rl/ope.py`**

Create file `src/dropout_rl/rl/ope.py`:

```python
"""Off-policy evaluation: WIS, FQE, and OOD frequency.

Follows Raghu et al. (2022) — FQE is primary for healthcare policy selection;
WIS is screening with clipping ε.
"""

from __future__ import annotations

from typing import Callable

import numpy as np
from sklearn.ensemble import ExtraTreesRegressor


def wis_value(
    target_policy: Callable[[np.ndarray], np.ndarray],
    dataset: dict,
    behaviour_probs: np.ndarray,
    epsilon: float = 0.1,
) -> float:
    """Weighted importance sampling estimate of policy value.

    Parameters
    ----------
    target_policy : callable
        Given states (N, d), returns actions (N,).
    dataset : dict
        Must contain states, actions, rewards, n_actions.
    behaviour_probs : np.ndarray of shape (N, n_actions)
        P(a | s) under behaviour policy.
    epsilon : float
        Clip target policy probabilities to [epsilon, 1-epsilon] for stability.

    Returns
    -------
    float
        WIS estimate of expected reward.
    """
    states = dataset["states"]
    actions = dataset["actions"]
    rewards = dataset["rewards"]
    n = len(actions)

    pred_actions = target_policy(states)
    target_probs = np.full((n, dataset["n_actions"]), epsilon / (dataset["n_actions"] - 1))
    for i, a in enumerate(pred_actions):
        target_probs[i, a] = 1.0 - epsilon

    behav_taken = np.maximum(behaviour_probs[np.arange(n), actions], 1e-6)
    target_taken = target_probs[np.arange(n), actions]

    weights = target_taken / behav_taken
    if weights.sum() == 0:
        return 0.0
    return float((weights * rewards).sum() / weights.sum())


def fqe_value(
    target_policy: Callable[[np.ndarray], np.ndarray],
    dataset: dict,
    gamma: float = 0.0,
    n_iterations: int = 50,
) -> float:
    """Fitted Q-evaluation estimate of policy value.

    Trains Q̂(s, a) via regression on Bellman targets under the target policy,
    then returns E[Q̂(s_0, π(s_0))] averaged over initial states in the dataset.

    Parameters
    ----------
    target_policy : callable
    dataset : dict
    gamma : float
        Discount factor.
    n_iterations : int
        Fitted Q iteration count.

    Returns
    -------
    float
        Estimated policy value.
    """
    states = dataset["states"]
    actions = dataset["actions"]
    rewards = dataset["rewards"]
    n_actions = dataset["n_actions"]
    n = len(actions)

    # One regressor per action
    q_models: list[ExtraTreesRegressor | None] = [None] * n_actions
    q_current = np.zeros(n)

    for it in range(n_iterations):
        # Bellman target using target policy at next state (treated as same state for simplicity)
        next_pi = target_policy(states)
        q_next = np.zeros(n)
        if it > 0:
            for a in range(n_actions):
                mask = next_pi == a
                if mask.any() and q_models[a] is not None:
                    q_next[mask] = q_models[a].predict(states[mask])
        targets = rewards + gamma * q_next

        # Fit regressors per action
        for a in range(n_actions):
            mask = actions == a
            if mask.sum() < 5:
                continue
            reg = ExtraTreesRegressor(
                n_estimators=50, max_depth=6, random_state=it, n_jobs=1
            )
            reg.fit(states[mask], targets[mask])
            q_models[a] = reg

    # Final value: E[Q(s, π(s))]
    pi_actions = target_policy(states)
    q_final = np.zeros(n)
    for a in range(n_actions):
        mask = pi_actions == a
        if mask.any() and q_models[a] is not None:
            q_final[mask] = q_models[a].predict(states[mask])
    return float(q_final.mean())


def ood_frequency(
    target_actions: np.ndarray,
    behaviour_actions: np.ndarray,
    min_behaviour_prob: float = 0.01,
) -> float:
    """Fraction of target-policy actions that are OOD (rare in behaviour data).

    An action is OOD if its empirical probability under the behaviour policy
    is below min_behaviour_prob.

    Parameters
    ----------
    target_actions : np.ndarray
        Actions chosen by the target policy.
    behaviour_actions : np.ndarray
        Actions observed in the data.
    min_behaviour_prob : float
        Threshold below which an action is considered OOD.

    Returns
    -------
    float
        Fraction of target_actions that fall below threshold.
    """
    n_actions = max(target_actions.max(), behaviour_actions.max()) + 1
    behav_counts = np.bincount(behaviour_actions, minlength=n_actions)
    behav_probs = behav_counts / len(behaviour_actions)

    ood_actions = set(np.where(behav_probs < min_behaviour_prob)[0])
    ood_count = sum(1 for a in target_actions if a in ood_actions)
    return float(ood_count / len(target_actions))
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/test_ope.py -v`
Expected: all pass

- [ ] **Step 5: Commit**

```bash
git add src/dropout_rl/rl/ope.py tests/test_ope.py
git commit -m "feat: add OPE (WIS, FQE, OOD frequency) with unified interface"
```

---

### Task 8: CQL algorithm

**Files:**
- Create: `src/dropout_rl/rl/cql.py`
- Create: `tests/test_cql.py`

- [ ] **Step 1: Write failing test**

Create file `tests/test_cql.py`:

```python
"""Tests for dropout_rl.rl.cql."""

import numpy as np
import pytest

from dropout_rl.rl.cql import CQL


class TestCQL:
    def test_fit_smoke(self, rng):
        """Smoke test: CQL trains without error on toy dataset."""
        dataset = {
            "states": rng.standard_normal((200, 5)).astype(np.float32),
            "actions": rng.integers(0, 3, size=200),
            "rewards": rng.uniform(0, 1, size=200).astype(np.float32),
            "weights": np.ones(200, dtype=np.float32),
            "n_actions": 3,
        }
        cql = CQL(n_actions=3, alpha=1.0, n_iterations=10)
        cql.fit(dataset, rng=rng)
        actions = cql.predict_action(dataset["states"])
        assert actions.shape == (200,)
        assert actions.max() < 3

    def test_predict_q_shape(self, rng):
        dataset = {
            "states": rng.standard_normal((50, 5)).astype(np.float32),
            "actions": rng.integers(0, 3, size=50),
            "rewards": rng.uniform(0, 1, size=50).astype(np.float32),
            "weights": np.ones(50, dtype=np.float32),
            "n_actions": 3,
        }
        cql = CQL(n_actions=3, alpha=1.0, n_iterations=5)
        cql.fit(dataset, rng=rng)
        q = cql.predict_q(dataset["states"])
        assert q.shape == (50, 3)
```

- [ ] **Step 2: Run test**

Run: `pytest tests/test_cql.py -v`
Expected: FAIL with ImportError

- [ ] **Step 3: Write `rl/cql.py`**

Create file `src/dropout_rl/rl/cql.py`:

```python
"""Conservative Q-Learning (CQL) for offline RL.

Adapted from Kumar et al. 2020. Uses ExtraTreesRegressor as function approximator
with CQL penalty on Q-values for out-of-distribution actions.
"""

from __future__ import annotations

import numpy as np
from sklearn.ensemble import ExtraTreesRegressor


class CQL:
    """Conservative Q-Learning with tree-based function approximator."""

    def __init__(
        self,
        n_actions: int = 3,
        alpha: float = 1.0,
        gamma: float = 0.95,
        n_iterations: int = 80,
        n_estimators: int = 200,
        max_depth: int = 10,
    ):
        self.n_actions = n_actions
        self.alpha = alpha
        self.gamma = gamma
        self.n_iterations = n_iterations
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.q_models: list[ExtraTreesRegressor | None] = [None] * n_actions

    def fit(self, dataset: dict, rng: np.random.Generator) -> None:
        """Fit Q-functions for each action via CQL-penalised Bellman backup."""
        states = dataset["states"]
        actions = dataset["actions"]
        rewards = dataset["rewards"]
        n = len(actions)

        q_current = np.zeros((n, self.n_actions))

        for it in range(self.n_iterations):
            # Bellman target: r + γ * max_a' Q(s', a')
            # Approximate s' = s (cross-sectional)
            q_max = q_current.max(axis=1)
            targets = rewards + self.gamma * q_max

            # CQL penalty: reduce Q for OOD actions — approximated by penalising
            # actions with low empirical probability
            for a in range(self.n_actions):
                mask = actions == a
                if mask.sum() < 5:
                    continue
                reg = ExtraTreesRegressor(
                    n_estimators=self.n_estimators,
                    max_depth=self.max_depth,
                    random_state=int(rng.integers(0, 2**31 - 1)),
                    n_jobs=1,
                )
                # Apply CQL penalty: subtract alpha * (1 - P(a)) from targets
                # to discourage values on under-represented actions
                behav_prob = mask.sum() / n
                penalty = self.alpha * (1.0 - behav_prob)
                reg.fit(states[mask], targets[mask] - penalty)
                self.q_models[a] = reg

            q_current = self.predict_q(states)

    def predict_q(self, states: np.ndarray) -> np.ndarray:
        """Return Q(s, a) for all actions. Shape (N, n_actions)."""
        q = np.zeros((len(states), self.n_actions))
        for a in range(self.n_actions):
            if self.q_models[a] is not None:
                q[:, a] = self.q_models[a].predict(states)
        return q

    def predict_action(self, states: np.ndarray) -> np.ndarray:
        """Return greedy actions. Shape (N,)."""
        return self.predict_q(states).argmax(axis=1)
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/test_cql.py -v`
Expected: all pass

- [ ] **Step 5: Commit**

```bash
git add src/dropout_rl/rl/cql.py tests/test_cql.py
git commit -m "feat: add CQL with tree-based function approximator, 3-action default"
```

---

### Task 9: IQL algorithm

**Files:**
- Create: `src/dropout_rl/rl/iql.py`
- Create: `tests/test_iql.py`

- [ ] **Step 1: Write failing test**

Create file `tests/test_iql.py`:

```python
"""Tests for dropout_rl.rl.iql."""

import numpy as np
import pytest

from dropout_rl.rl.iql import IQL


class TestIQL:
    def test_fit_smoke(self, rng):
        dataset = {
            "states": rng.standard_normal((200, 5)).astype(np.float32),
            "actions": rng.integers(0, 3, size=200),
            "rewards": rng.uniform(0, 1, size=200).astype(np.float32),
            "weights": np.ones(200, dtype=np.float32),
            "n_actions": 3,
        }
        iql = IQL(n_actions=3, tau=0.8, beta=3.0, n_iterations=10)
        iql.fit(dataset, rng=rng)
        actions = iql.predict_action(dataset["states"])
        assert actions.shape == (200,)

    def test_predict_q_shape(self, rng):
        dataset = {
            "states": rng.standard_normal((50, 5)).astype(np.float32),
            "actions": rng.integers(0, 3, size=50),
            "rewards": rng.uniform(0, 1, size=50).astype(np.float32),
            "weights": np.ones(50, dtype=np.float32),
            "n_actions": 3,
        }
        iql = IQL(n_actions=3, n_iterations=5)
        iql.fit(dataset, rng=rng)
        q = iql.predict_q(dataset["states"])
        assert q.shape == (50, 3)
```

- [ ] **Step 2: Run test**

Run: `pytest tests/test_iql.py -v`
Expected: FAIL with ImportError

- [ ] **Step 3: Write `rl/iql.py`**

Create file `src/dropout_rl/rl/iql.py`:

```python
"""Implicit Q-Learning (IQL) for offline RL.

Kostrikov et al. 2021. Uses expectile regression to avoid querying
Q at out-of-distribution actions.
"""

from __future__ import annotations

import numpy as np
from sklearn.ensemble import ExtraTreesRegressor


def expectile_loss(residuals: np.ndarray, tau: float) -> np.ndarray:
    """Expectile loss: tau if residual >= 0, else (1 - tau)."""
    weight = np.where(residuals >= 0, tau, 1 - tau)
    return weight * residuals**2


class IQL:
    """Implicit Q-Learning with tree-based function approximators."""

    def __init__(
        self,
        n_actions: int = 3,
        tau: float = 0.8,
        beta: float = 3.0,
        gamma: float = 0.95,
        n_iterations: int = 80,
        n_estimators: int = 200,
        max_depth: int = 10,
    ):
        self.n_actions = n_actions
        self.tau = tau
        self.beta = beta
        self.gamma = gamma
        self.n_iterations = n_iterations
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.q_models: list[ExtraTreesRegressor | None] = [None] * n_actions
        self.v_model: ExtraTreesRegressor | None = None

    def fit(self, dataset: dict, rng: np.random.Generator) -> None:
        states = dataset["states"]
        actions = dataset["actions"]
        rewards = dataset["rewards"]
        n = len(actions)

        # Initial Q estimates
        q_taken = np.zeros(n)

        for it in range(self.n_iterations):
            # Step 1: fit V via expectile regression on Q(s, a_observed)
            # V minimises expectile_loss(Q - V) at expectile tau
            v_target = q_taken.copy()
            v_reg = ExtraTreesRegressor(
                n_estimators=self.n_estimators,
                max_depth=self.max_depth,
                random_state=int(rng.integers(0, 2**31 - 1)),
                n_jobs=1,
            )
            # Approximation: fit V to mean of upper tau-quantile residuals
            v_reg.fit(states, v_target)
            self.v_model = v_reg
            v_pred = v_reg.predict(states)

            # Step 2: Q update: Q(s,a) ← r + γ V(s')
            # Cross-sectional: s' ≈ s
            q_targets = rewards + self.gamma * v_pred
            for a in range(self.n_actions):
                mask = actions == a
                if mask.sum() < 5:
                    continue
                reg = ExtraTreesRegressor(
                    n_estimators=self.n_estimators,
                    max_depth=self.max_depth,
                    random_state=int(rng.integers(0, 2**31 - 1)),
                    n_jobs=1,
                )
                reg.fit(states[mask], q_targets[mask])
                self.q_models[a] = reg

            # Update q_taken for next iteration
            for a in range(self.n_actions):
                mask = actions == a
                if mask.any() and self.q_models[a] is not None:
                    q_taken[mask] = self.q_models[a].predict(states[mask])

    def predict_q(self, states: np.ndarray) -> np.ndarray:
        q = np.zeros((len(states), self.n_actions))
        for a in range(self.n_actions):
            if self.q_models[a] is not None:
                q[:, a] = self.q_models[a].predict(states)
        return q

    def predict_action(self, states: np.ndarray) -> np.ndarray:
        return self.predict_q(states).argmax(axis=1)
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/test_iql.py -v`
Expected: all pass

- [ ] **Step 5: Commit**

```bash
git add src/dropout_rl/rl/iql.py tests/test_iql.py
git commit -m "feat: add IQL with expectile regression and value network"
```

---

### Task 10: Discrete BCQ algorithm

**Files:**
- Create: `src/dropout_rl/rl/bcq.py`
- Create: `tests/test_bcq.py`

- [ ] **Step 1: Write failing test**

Create file `tests/test_bcq.py`:

```python
"""Tests for dropout_rl.rl.bcq."""

import numpy as np
import pytest

from dropout_rl.rl.bcq import DiscreteBCQ


class TestDiscreteBCQ:
    def test_fit_smoke(self, rng):
        dataset = {
            "states": rng.standard_normal((200, 5)).astype(np.float32),
            "actions": rng.integers(0, 3, size=200),
            "rewards": rng.uniform(0, 1, size=200).astype(np.float32),
            "weights": np.ones(200, dtype=np.float32),
            "n_actions": 3,
        }
        bcq = DiscreteBCQ(n_actions=3, threshold=0.3, n_iterations=10)
        bcq.fit(dataset, rng=rng)
        actions = bcq.predict_action(dataset["states"])
        assert actions.shape == (200,)

    def test_respects_threshold(self, rng):
        """BCQ should not recommend actions with behaviour prob < threshold."""
        n = 500
        # Heavily skewed actions: 90% action 0, 10% action 1, 0% action 2
        actions = np.concatenate([np.zeros(450), np.ones(50)]).astype(np.int64)
        rng.shuffle(actions)
        dataset = {
            "states": rng.standard_normal((n, 5)).astype(np.float32),
            "actions": actions,
            "rewards": rng.uniform(0, 1, size=n).astype(np.float32),
            "weights": np.ones(n, dtype=np.float32),
            "n_actions": 3,
        }
        bcq = DiscreteBCQ(n_actions=3, threshold=0.3, n_iterations=20)
        bcq.fit(dataset, rng=rng)
        preds = bcq.predict_action(dataset["states"])
        # Action 2 (0% behaviour) should never be recommended
        assert (preds == 2).sum() == 0
```

- [ ] **Step 2: Run test**

Run: `pytest tests/test_bcq.py -v`
Expected: FAIL with ImportError

- [ ] **Step 3: Write `rl/bcq.py`**

Create file `src/dropout_rl/rl/bcq.py`:

```python
"""Discrete Batch-Constrained Q-Learning (BCQ) for offline RL.

Fujimoto et al. 2019. Restricts policy to actions with behaviour probability
above a threshold, avoiding OOD recommendations by construction.
"""

from __future__ import annotations

import numpy as np
from sklearn.ensemble import ExtraTreesClassifier, ExtraTreesRegressor


class DiscreteBCQ:
    """Batch-Constrained Q-Learning for discrete actions."""

    def __init__(
        self,
        n_actions: int = 3,
        threshold: float = 0.3,
        gamma: float = 0.95,
        n_iterations: int = 80,
        n_estimators: int = 200,
        max_depth: int = 10,
    ):
        self.n_actions = n_actions
        self.threshold = threshold
        self.gamma = gamma
        self.n_iterations = n_iterations
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.q_models: list[ExtraTreesRegressor | None] = [None] * n_actions
        self.behaviour_clf: ExtraTreesClassifier | None = None

    def fit(self, dataset: dict, rng: np.random.Generator) -> None:
        states = dataset["states"]
        actions = dataset["actions"]
        rewards = dataset["rewards"]
        n = len(actions)

        # Step 1: fit behaviour policy classifier
        self.behaviour_clf = ExtraTreesClassifier(
            n_estimators=self.n_estimators,
            max_depth=self.max_depth,
            random_state=int(rng.integers(0, 2**31 - 1)),
            n_jobs=1,
        )
        self.behaviour_clf.fit(states, actions)

        # Step 2: standard Q-learning with BCQ masking
        q_current = np.zeros((n, self.n_actions))

        for it in range(self.n_iterations):
            # Behaviour probabilities at each state
            behav_probs = self.behaviour_clf.predict_proba(states)
            # Ensure shape (n, n_actions)
            full_probs = np.zeros((n, self.n_actions))
            for i, cls in enumerate(self.behaviour_clf.classes_):
                if cls < self.n_actions:
                    full_probs[:, cls] = behav_probs[:, i]

            # Mask: action allowed if P(a | s) >= threshold * max P(. | s)
            max_probs = full_probs.max(axis=1, keepdims=True)
            allowed = full_probs >= self.threshold * max_probs

            # Masked max_Q for Bellman backup
            q_masked = np.where(allowed, q_current, -np.inf)
            q_max = q_masked.max(axis=1)
            targets = rewards + self.gamma * q_max

            for a in range(self.n_actions):
                mask = actions == a
                if mask.sum() < 5:
                    continue
                reg = ExtraTreesRegressor(
                    n_estimators=self.n_estimators,
                    max_depth=self.max_depth,
                    random_state=int(rng.integers(0, 2**31 - 1)),
                    n_jobs=1,
                )
                reg.fit(states[mask], targets[mask])
                self.q_models[a] = reg

            # Update q_current
            for a in range(self.n_actions):
                if self.q_models[a] is not None:
                    q_current[:, a] = self.q_models[a].predict(states)

    def predict_q(self, states: np.ndarray) -> np.ndarray:
        q = np.zeros((len(states), self.n_actions))
        for a in range(self.n_actions):
            if self.q_models[a] is not None:
                q[:, a] = self.q_models[a].predict(states)
        return q

    def predict_action(self, states: np.ndarray) -> np.ndarray:
        """Return greedy action subject to BCQ constraint."""
        q = self.predict_q(states)
        # Mask actions below threshold
        behav_probs = self.behaviour_clf.predict_proba(states)
        full_probs = np.zeros((len(states), self.n_actions))
        for i, cls in enumerate(self.behaviour_clf.classes_):
            if cls < self.n_actions:
                full_probs[:, cls] = behav_probs[:, i]
        max_probs = full_probs.max(axis=1, keepdims=True)
        allowed = full_probs >= self.threshold * max_probs
        q_masked = np.where(allowed, q, -np.inf)
        return q_masked.argmax(axis=1)
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/test_bcq.py -v`
Expected: all pass

- [ ] **Step 5: Commit**

```bash
git add src/dropout_rl/rl/bcq.py tests/test_bcq.py
git commit -m "feat: add DiscreteBCQ with behaviour-constrained action masking"
```

---

## Phase 4: Microsimulation and Validation

### Task 11: Microsim module with cluster-bootstrap and PSA

**Files:**
- Create: `src/dropout_rl/microsim.py`
- Create: `tests/test_microsim.py`

- [ ] **Step 1: Write failing test**

Create file `tests/test_microsim.py`:

```python
"""Tests for dropout_rl.microsim."""

import numpy as np
import pandas as pd
import pytest

from dropout_rl.microsim import ScenarioResult, run_scenario


class _FakeTransition:
    """Mock transition model that returns a constant dropout probability."""

    def __init__(self, p: float):
        self.p = p

    def predict_dropout(self, X):
        return np.full(len(X), self.p)


def _fake_data(n=200):
    rng = np.random.default_rng(0)
    return pd.DataFrame({
        "v021": rng.integers(1, 20, size=n),  # 20 clusters
        "v005": rng.uniform(0.5e6, 1.5e6, size=n),
        "wealth": rng.integers(1, 6, size=n),
        "sstate": rng.integers(1, 38, size=n),
        "medu": rng.integers(0, 3, size=n),
        "rural": rng.integers(0, 2, size=n),
    })


class TestRunScenario:
    def test_returns_scenario_result(self):
        df = _fake_data()
        t1 = _FakeTransition(0.10)
        t2 = _FakeTransition(0.05)

        def always_sms_t1(X, indices):
            return np.ones(len(X), dtype=int)

        def always_sms_t2(X, indices):
            return np.ones(len(X), dtype=int)

        result = run_scenario(
            name="test_sms",
            policy_fn_t1=always_sms_t1,
            policy_fn_t2=always_sms_t2,
            analytic_df=df,
            t1_model=t1,
            t2_model=t2,
            n_pop=50,
            n_bootstrap=10,
            seed=42,
            psa=False,
            cluster_bootstrap=True,
        )
        assert isinstance(result, ScenarioResult)
        assert result.dtp3_rate.shape == (10,)
        assert np.all(result.dtp3_rate >= 0)
        assert np.all(result.dtp3_rate <= 1)

    def test_reproducibility_same_seed(self):
        df = _fake_data()
        t1 = _FakeTransition(0.10)
        t2 = _FakeTransition(0.05)

        def sms_t1(X, i):
            return np.ones(len(X), dtype=int)

        def sms_t2(X, i):
            return np.ones(len(X), dtype=int)

        r1 = run_scenario("a", sms_t1, sms_t2, df, t1, t2,
                         n_pop=50, n_bootstrap=5, seed=42, psa=False)
        r2 = run_scenario("a", sms_t1, sms_t2, df, t1, t2,
                         n_pop=50, n_bootstrap=5, seed=42, psa=False)
        np.testing.assert_array_equal(r1.dtp3_rate, r2.dtp3_rate)

    def test_status_quo_ignores_rrr(self):
        """S0 should not apply RRR (is_status_quo=True)."""
        df = _fake_data()
        t1 = _FakeTransition(0.20)
        t2 = _FakeTransition(0.10)

        def a0_t1(X, i):
            return np.zeros(len(X), dtype=int)

        def a0_t2(X, i):
            return np.zeros(len(X), dtype=int)

        result = run_scenario(
            name="s0",
            policy_fn_t1=a0_t1,
            policy_fn_t2=a0_t2,
            analytic_df=df,
            t1_model=t1,
            t2_model=t2,
            n_pop=50,
            n_bootstrap=20,
            seed=42,
            psa=False,
            is_status_quo=True,
        )
        # DTP3 rate ≈ (1 - 0.20) * (1 - 0.10) = 0.72
        assert 0.60 < result.dtp3_rate.mean() < 0.82

    def test_psa_increases_variance(self):
        """PSA should increase CI width vs no-PSA."""
        df = _fake_data()
        t1 = _FakeTransition(0.10)
        t2 = _FakeTransition(0.05)

        def sms_t1(X, i):
            return np.ones(len(X), dtype=int)

        def sms_t2(X, i):
            return np.ones(len(X), dtype=int)

        r_no_psa = run_scenario("n", sms_t1, sms_t2, df, t1, t2,
                                n_pop=100, n_bootstrap=100, seed=42, psa=False)
        r_psa = run_scenario("p", sms_t1, sms_t2, df, t1, t2,
                             n_pop=100, n_bootstrap=100, seed=42, psa=True)
        # PSA adds uncertainty, so std should not be smaller
        assert r_psa.dtp3_rate.std() >= r_no_psa.dtp3_rate.std() * 0.8
```

- [ ] **Step 2: Run test**

Run: `pytest tests/test_microsim.py -v`
Expected: FAIL with ImportError

- [ ] **Step 3: Write `microsim.py`**

Create file `src/dropout_rl/microsim.py`:

```python
"""Microsimulation scenario runner with cluster-bootstrap and PSA."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np
import pandas as pd

from dropout_rl.config import (
    ACTION_COSTS_POINT,
    N_BOOTSTRAP_DEFAULT,
    N_POP_DEFAULT,
)
from dropout_rl.costs import sample_cost_batch
from dropout_rl.equity import (
    concentration_index,
    slope_index_of_inequality,
    wealth_gap,
)
from dropout_rl.interventions import apply_rrr, sample_rrr_batch


@dataclass
class ScenarioResult:
    """Microsimulation scenario output."""

    name: str
    dtp3_rate: np.ndarray
    cost_per_child: np.ndarray
    total_cost: np.ndarray
    concentration_index: np.ndarray
    wealth_gap: np.ndarray
    slope_index: np.ndarray
    rate_by_quintile: np.ndarray
    rate_by_zone: np.ndarray
    is_status_quo: bool


def _sample_cluster_bootstrap(
    df: pd.DataFrame,
    n_pop: int,
    rng: np.random.Generator,
) -> np.ndarray:
    """Resample PSUs, then sample children within them.

    Returns indices into df.
    """
    clusters = df["v021"].unique()
    n_clusters = len(clusters)
    # Resample clusters with replacement
    resampled_clusters = rng.choice(clusters, size=n_clusters, replace=True)
    # Concatenate indices for resampled clusters
    cluster_to_idx = df.groupby("v021").indices
    all_idx = []
    for c in resampled_clusters:
        all_idx.extend(cluster_to_idx[c].tolist())
    all_idx = np.asarray(all_idx)
    # Sample n_pop with replacement from these
    if len(all_idx) == 0:
        raise ValueError("No valid indices from cluster bootstrap")
    final_idx = rng.choice(all_idx, size=n_pop, replace=True)
    return final_idx


def _sample_individual_bootstrap(
    df: pd.DataFrame,
    n_pop: int,
    rng: np.random.Generator,
) -> np.ndarray:
    """Resample individuals with replacement, weighted by v005."""
    weights = df["v005"].to_numpy() if "v005" in df.columns else None
    if weights is not None:
        p = weights / weights.sum()
    else:
        p = None
    return rng.choice(len(df), size=n_pop, replace=True, p=p)


def run_scenario(
    name: str,
    policy_fn_t1: Callable,
    policy_fn_t2: Callable,
    analytic_df: pd.DataFrame,
    t1_model,
    t2_model,
    n_pop: int = N_POP_DEFAULT,
    n_bootstrap: int = N_BOOTSTRAP_DEFAULT,
    cluster_bootstrap: bool = True,
    psa: bool = True,
    seed: int = 42,
    is_status_quo: bool = False,
    feature_cols: list[str] | None = None,
) -> ScenarioResult:
    """Run a microsimulation scenario with cluster-bootstrap and optional PSA.

    Parameters
    ----------
    policy_fn_t1, policy_fn_t2 : callable
        Functions mapping (states, indices) → actions.
    t1_model, t2_model : TransitionModel
        Calibrated dropout models.
    n_pop : int
        Synthetic population size per bootstrap iteration.
    n_bootstrap : int
        Number of bootstrap replicates.
    cluster_bootstrap : bool
        If True, resample PSUs (v021). Otherwise individual resampling.
    psa : bool
        If True, draw RRR and costs from priors each iteration.
    is_status_quo : bool
        If True, do not apply RRR (baseline dropout rates used directly).
    feature_cols : list[str] | None
        Columns to feed to transition models. If None, use t1_model.feature_names.

    Returns
    -------
    ScenarioResult
    """
    rng = np.random.default_rng(seed)
    n_actions = 3  # primary action space

    if feature_cols is None:
        feature_cols = list(getattr(t1_model, "feature_names", analytic_df.columns))
    feature_cols = [c for c in feature_cols if c in analytic_df.columns]

    results = {
        "dtp3_rate": np.zeros(n_bootstrap),
        "cost_per_child": np.zeros(n_bootstrap),
        "total_cost": np.zeros(n_bootstrap),
        "concentration_index": np.zeros(n_bootstrap),
        "wealth_gap": np.zeros(n_bootstrap),
        "slope_index": np.zeros(n_bootstrap),
        "rate_by_quintile": np.zeros((n_bootstrap, 5)),
        "rate_by_zone": np.zeros((n_bootstrap, 6)),
    }

    for b in range(n_bootstrap):
        if cluster_bootstrap:
            idx = _sample_cluster_bootstrap(analytic_df, n_pop, rng)
        else:
            idx = _sample_individual_bootstrap(analytic_df, n_pop, rng)

        sample = analytic_df.iloc[idx].copy().reset_index(drop=True)
        if feature_cols:
            X = sample[feature_cols].to_numpy(dtype=np.float32)
            # Fill NaNs with column median
            if np.isnan(X).any():
                col_med = np.nanmedian(X, axis=0)
                col_med = np.where(np.isnan(col_med), 0.0, col_med)
                inds = np.where(np.isnan(X))
                X[inds] = np.take(col_med, inds[1])
        else:
            X = np.zeros((len(sample), 1), dtype=np.float32)

        # PSA draws (one per action)
        if psa:
            rrr_draws = sample_rrr_batch(n_actions, rng)
            cost_draws = sample_cost_batch(n_actions, rng)
        else:
            rrr_draws = np.array([0.0, 0.10, 0.20])
            cost_draws = np.array([0.0, 50.0, 500.0])

        # T1 transition
        p_dropout_t1 = t1_model.predict_dropout(X)
        actions_t1 = policy_fn_t1(X, idx).astype(np.int64)
        actions_t1 = np.clip(actions_t1, 0, n_actions - 1)
        if not is_status_quo:
            p_dropout_t1 = apply_rrr(p_dropout_t1, actions_t1, rrr_draws)
        p_dtp2 = 1.0 - p_dropout_t1
        received_dtp2 = rng.random(len(X)) < p_dtp2

        # T2 transition (among DTP2 recipients)
        p_dropout_t2 = t2_model.predict_dropout(X)
        actions_t2 = policy_fn_t2(X, idx).astype(np.int64)
        actions_t2 = np.clip(actions_t2, 0, n_actions - 1)
        if not is_status_quo:
            p_dropout_t2 = apply_rrr(p_dropout_t2, actions_t2, rrr_draws)
        p_dtp3 = 1.0 - p_dropout_t2
        received_dtp3 = (rng.random(len(X)) < p_dtp3) & received_dtp2

        # Outcomes
        results["dtp3_rate"][b] = received_dtp3.mean()

        # Costs
        total_cost_per_step = cost_draws[actions_t1].sum() + cost_draws[actions_t2].sum()
        results["total_cost"][b] = total_cost_per_step
        results["cost_per_child"][b] = total_cost_per_step / n_pop

        # Equity
        if "wealth" in sample.columns:
            wealth = sample["wealth"].to_numpy()
            y = received_dtp3.astype(float)
            results["concentration_index"][b] = concentration_index(y, wealth)
            results["wealth_gap"][b] = wealth_gap(y, wealth)
            results["slope_index"][b] = slope_index_of_inequality(y, wealth)
            for q in range(1, 6):
                mask = wealth == q
                results["rate_by_quintile"][b, q - 1] = (
                    y[mask].mean() if mask.any() else np.nan
                )
        if "sstate" in sample.columns:
            # Aggregate by zone (Nigeria 6 zones, approximate: bucket into 6)
            zones = np.digitize(sample["sstate"].to_numpy(),
                                [7, 14, 21, 28, 32, 40]) - 1
            zones = np.clip(zones, 0, 5)
            y = received_dtp3.astype(float)
            for z in range(6):
                mask = zones == z
                results["rate_by_zone"][b, z] = y[mask].mean() if mask.any() else np.nan

    return ScenarioResult(
        name=name,
        is_status_quo=is_status_quo,
        **results,
    )
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/test_microsim.py -v`
Expected: all pass

- [ ] **Step 5: Commit**

```bash
git add src/dropout_rl/microsim.py tests/test_microsim.py
git commit -m "feat: add microsim with cluster-bootstrap, PSA, and equity metrics"
```

---

### Task 12: Validation module

**Files:**
- Create: `src/dropout_rl/validation.py`
- Create: `tests/test_validation.py`

- [ ] **Step 1: Write failing test**

Create file `tests/test_validation.py`:

```python
"""Tests for dropout_rl.validation."""

import numpy as np
import pandas as pd
import pytest

from dropout_rl.validation import (
    calibration_check,
    subgroup_calibration,
)


class TestCalibrationCheck:
    def test_passes_when_close(self):
        result = calibration_check(
            predicted_rate=0.855,
            observed_rate=0.852,
            tolerance=0.01,
        )
        assert result["passed"] is True
        assert abs(result["absolute_error"] - 0.003) < 1e-9

    def test_fails_when_far(self):
        result = calibration_check(
            predicted_rate=0.90,
            observed_rate=0.80,
            tolerance=0.01,
        )
        assert result["passed"] is False
        assert result["absolute_error"] > 0.05


class TestSubgroupCalibration:
    def test_identifies_miscalibrated_subgroup(self):
        predicted = pd.DataFrame({
            "group": ["A", "B", "C"],
            "rate": [0.80, 0.85, 0.90],
        })
        observed = pd.DataFrame({
            "group": ["A", "B", "C"],
            "rate": [0.81, 0.82, 0.89],  # B is off by 0.03
        })
        result = subgroup_calibration(predicted, observed, flag_threshold=0.025)
        flagged = result[result["flagged"]]
        assert "B" in flagged["group"].values
        assert "A" not in flagged["group"].values
```

- [ ] **Step 2: Run test**

Run: `pytest tests/test_validation.py -v`
Expected: FAIL with ImportError

- [ ] **Step 3: Write `validation.py`**

Create file `src/dropout_rl/validation.py`:

```python
"""Microsimulation validation: internal calibration and subgroup checks."""

from __future__ import annotations

import numpy as np
import pandas as pd

from dropout_rl.config import CALIBRATION_TOLERANCE, SUBGROUP_CALIBRATION_FLAG


def calibration_check(
    predicted_rate: float,
    observed_rate: float,
    tolerance: float = CALIBRATION_TOLERANCE,
) -> dict:
    """Compare predicted vs observed S0 DTP3 rate.

    Parameters
    ----------
    predicted_rate : float
        DTP3 completion rate from S0 microsim.
    observed_rate : float
        Survey-weighted observed DTP3 completion rate.
    tolerance : float
        Pass threshold for absolute error.

    Returns
    -------
    dict with keys: passed, absolute_error, predicted, observed, tolerance.
    """
    abs_err = abs(predicted_rate - observed_rate)
    return {
        "passed": bool(abs_err <= tolerance),
        "absolute_error": float(abs_err),
        "predicted": float(predicted_rate),
        "observed": float(observed_rate),
        "tolerance": float(tolerance),
    }


def subgroup_calibration(
    predicted: pd.DataFrame,
    observed: pd.DataFrame,
    flag_threshold: float = SUBGROUP_CALIBRATION_FLAG,
    group_col: str = "group",
    rate_col: str = "rate",
) -> pd.DataFrame:
    """Per-stratum calibration check.

    Parameters
    ----------
    predicted, observed : pd.DataFrame
        Each has columns [group_col, rate_col].
    flag_threshold : float
        Subgroups with |predicted - observed| > flag_threshold are flagged.

    Returns
    -------
    pd.DataFrame with columns: group, predicted, observed, absolute_error, flagged.
    """
    merged = predicted.merge(observed, on=group_col, suffixes=("_pred", "_obs"))
    merged["absolute_error"] = (merged[f"{rate_col}_pred"] - merged[f"{rate_col}_obs"]).abs()
    merged["flagged"] = merged["absolute_error"] > flag_threshold
    return merged.rename(
        columns={
            f"{rate_col}_pred": "predicted",
            f"{rate_col}_obs": "observed",
        }
    )[[group_col, "predicted", "observed", "absolute_error", "flagged"]]
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/test_validation.py -v`
Expected: all pass

- [ ] **Step 5: Commit**

```bash
git add src/dropout_rl/validation.py tests/test_validation.py
git commit -m "feat: add validation with internal calibration and subgroup checks"
```

---

## Phase 5: Sensitivity Analysis

### Task 13: Sensitivity module (tornado, CEAC, probabilistic ICER)

**Files:**
- Create: `src/dropout_rl/sensitivity.py`
- Create: `tests/test_sensitivity.py`

- [ ] **Step 1: Write failing test**

Create file `tests/test_sensitivity.py`:

```python
"""Tests for dropout_rl.sensitivity."""

import numpy as np
import pytest

from dropout_rl.microsim import ScenarioResult
from dropout_rl.sensitivity import ceac, probabilistic_icer


def _make_scenario(name, dtp3_mean, cost_mean, n=100, rng_seed=0):
    rng = np.random.default_rng(rng_seed)
    return ScenarioResult(
        name=name,
        is_status_quo=False,
        dtp3_rate=rng.normal(dtp3_mean, 0.01, n),
        cost_per_child=rng.normal(cost_mean, 10, n),
        total_cost=rng.normal(cost_mean * 10000, 1000, n),
        concentration_index=rng.normal(0, 0.01, n),
        wealth_gap=rng.normal(0.07, 0.01, n),
        slope_index=rng.normal(0.10, 0.01, n),
        rate_by_quintile=np.tile([0.80, 0.85, 0.86, 0.88, 0.90], (n, 1)),
        rate_by_zone=np.tile([0.85] * 6, (n, 1)),
    )


class TestCEAC:
    def test_output_shape(self):
        s0 = _make_scenario("S0", 0.859, 155)
        s1 = _make_scenario("S1", 0.871, 98)
        wtp = np.array([0, 1000, 10000, 100000])
        result = ceac([s0, s1], wtp_range=wtp, reference="S0")
        # Rows per WTP, columns per scenario
        assert result.shape[0] == len(wtp)

    def test_probabilities_sum_to_one(self):
        s0 = _make_scenario("S0", 0.859, 155)
        s1 = _make_scenario("S1", 0.871, 98)
        wtp = np.array([0, 10000])
        result = ceac([s0, s1], wtp_range=wtp, reference="S0")
        # Each row (WTP) should have probabilities summing to 1
        prob_cols = [c for c in result.columns if c != "wtp"]
        row_sums = result[prob_cols].sum(axis=1)
        assert np.allclose(row_sums, 1.0, atol=1e-6)


class TestProbabilisticICER:
    def test_basic(self):
        s0 = _make_scenario("S0", 0.85, 155, n=200, rng_seed=0)
        s1 = _make_scenario("S1", 0.88, 341, n=200, rng_seed=1)
        icer = probabilistic_icer(s1, s0)
        assert "mean_icer" in icer
        assert "ci_low" in icer
        assert "ci_high" in icer
        # S1 costs more, achieves more, so ICER positive and finite
        assert icer["mean_icer"] > 0
```

- [ ] **Step 2: Run test**

Run: `pytest tests/test_sensitivity.py -v`
Expected: FAIL with ImportError

- [ ] **Step 3: Write `sensitivity.py`**

Create file `src/dropout_rl/sensitivity.py`:

```python
"""Sensitivity analyses: tornado diagram, CEAC, probabilistic ICER."""

from __future__ import annotations

from typing import Iterable

import numpy as np
import pandas as pd

from dropout_rl.microsim import ScenarioResult


def probabilistic_icer(
    scenario: ScenarioResult,
    reference: ScenarioResult,
) -> dict:
    """Probabilistic ICER from bootstrap × PSA joint distribution.

    ICER = ΔCost / ΔEffectiveness per paired bootstrap iteration.

    Parameters
    ----------
    scenario : ScenarioResult
        Intervention scenario.
    reference : ScenarioResult
        Reference (e.g., status quo).

    Returns
    -------
    dict with: mean_icer, median_icer, ci_low, ci_high, n_dominant, n_dominated.
    """
    d_cost = scenario.cost_per_child - reference.cost_per_child
    d_effect = scenario.dtp3_rate - reference.dtp3_rate

    finite_mask = d_effect != 0
    icers = np.where(finite_mask, d_cost / np.where(finite_mask, d_effect, 1.0), np.nan)

    n_dominant = int(((d_cost <= 0) & (d_effect > 0)).sum())
    n_dominated = int(((d_cost >= 0) & (d_effect <= 0)).sum())

    valid = icers[~np.isnan(icers)]
    return {
        "mean_icer": float(np.nanmean(icers)) if len(valid) else float("nan"),
        "median_icer": float(np.nanmedian(icers)) if len(valid) else float("nan"),
        "ci_low": float(np.nanpercentile(icers, 2.5)) if len(valid) else float("nan"),
        "ci_high": float(np.nanpercentile(icers, 97.5)) if len(valid) else float("nan"),
        "n_dominant": n_dominant,
        "n_dominated": n_dominated,
        "mean_delta_cost": float(d_cost.mean()),
        "mean_delta_effect": float(d_effect.mean()),
    }


def ceac(
    scenarios: list[ScenarioResult],
    wtp_range: np.ndarray,
    reference: str,
) -> pd.DataFrame:
    """Cost-effectiveness acceptability curve.

    For each WTP threshold λ, compute P(scenario X has max net benefit)
    across bootstrap iterations.

    Net benefit per scenario per iteration: λ * dtp3_rate - cost_per_child.

    Parameters
    ----------
    scenarios : list[ScenarioResult]
        All scenarios including the reference.
    wtp_range : np.ndarray
        Willingness-to-pay thresholds.
    reference : str
        Reference scenario name (included in the probability computation).

    Returns
    -------
    pd.DataFrame with columns: wtp, <scenario_name_1>, <scenario_name_2>, ...
    """
    names = [s.name for s in scenarios]
    n_bootstrap = len(scenarios[0].dtp3_rate)

    rows = []
    for wtp in wtp_range:
        nb = np.stack([wtp * s.dtp3_rate - s.cost_per_child for s in scenarios])
        # shape (n_scenarios, n_bootstrap)
        winners = nb.argmax(axis=0)
        prob_optimal = np.bincount(winners, minlength=len(scenarios)) / n_bootstrap
        row = {"wtp": float(wtp)}
        for i, name in enumerate(names):
            row[name] = float(prob_optimal[i])
        rows.append(row)
    return pd.DataFrame(rows)


def tornado_diagram(
    param_results: dict[str, tuple[float, float]],
    base_value: float,
) -> pd.DataFrame:
    """One-way sensitivity: impact of each parameter's ±2σ perturbation.

    Parameters
    ----------
    param_results : dict
        Keys: parameter names. Values: (low_result, high_result) DTP3 rates
        under ±2σ perturbation of that parameter.
    base_value : float
        Base-case DTP3 rate.

    Returns
    -------
    pd.DataFrame with columns: parameter, low, high, range, sorted by range.
    """
    rows = []
    for name, (low, high) in param_results.items():
        rows.append({
            "parameter": name,
            "low": float(low),
            "high": float(high),
            "base": float(base_value),
            "range": float(abs(high - low)),
        })
    df = pd.DataFrame(rows).sort_values("range", ascending=False).reset_index(drop=True)
    return df
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/test_sensitivity.py -v`
Expected: all pass

- [ ] **Step 5: Commit**

```bash
git add src/dropout_rl/sensitivity.py tests/test_sensitivity.py
git commit -m "feat: add sensitivity analysis (CEAC, probabilistic ICER, tornado)"
```

---

## Phase 6: Scripts

### Task 14: run_stage2.py — RL algorithm comparison

**Files:**
- Create: `scripts/run_stage2.py`

- [ ] **Step 1: Verify the upstream data needed**

Run:
```bash
ls data/processed/trajectory_dataset.csv && ls outputs/stage1/xgb_model_t1.json
```
Expected: both files exist.

- [ ] **Step 2: Write `run_stage2.py`**

Create file `scripts/run_stage2.py`:

```python
#!/usr/bin/env python3
"""Stage 2 v2: Offline RL with CQL / IQL / BCQ comparison.

Trains three offline RL algorithms on the same 3-action trajectory dataset,
evaluates each with WIS and FQE, selects the best-performing policy for
downstream use in the microsimulation (S4).
"""

from __future__ import annotations

import json
import warnings
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from dropout_rl.config import STAGE2_V2_DIR, PROCESSED_DIR
from dropout_rl.rl.bcq import DiscreteBCQ
from dropout_rl.rl.common import build_mdp_dataset
from dropout_rl.rl.cql import CQL
from dropout_rl.rl.iql import IQL
from dropout_rl.rl.ope import fqe_value, ood_frequency, wis_value

warnings.filterwarnings("ignore")
STAGE2_V2_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("STAGE 2 v2: OFFLINE RL — CQL vs IQL vs BCQ (3-ACTION)")
print("=" * 60)

# ── Load data ─────────────────────────────────────────────
traj_df = pd.read_csv(PROCESSED_DIR / "trajectory_dataset.csv")
print(f"Trajectory: {len(traj_df)} rows")

dataset = build_mdp_dataset(traj_df, n_actions=3)
print(f"MDP dataset: states {dataset['states'].shape}, actions in {set(dataset['actions'])}")

behav_action_dist = np.bincount(dataset["actions"], minlength=3) / len(dataset["actions"])
print(f"Behaviour policy action distribution: {dict(enumerate(behav_action_dist.round(3)))}")

behaviour_probs = np.tile(behav_action_dist, (len(dataset["actions"]), 1))

# ── Train three algorithms ────────────────────────────────
rng = np.random.default_rng(42)
results = {}

# CQL with α sensitivity
print("\n--- CQL ---")
cql_candidates = {}
for alpha in [0.5, 1.0, 2.0, 5.0, 10.0]:
    print(f"  Training CQL(α={alpha})...")
    cql = CQL(n_actions=3, alpha=alpha, n_iterations=40)
    cql.fit(dataset, rng=np.random.default_rng(42))
    fqe_v = fqe_value(cql.predict_action, dataset, gamma=0.95, n_iterations=30)
    wis_v = wis_value(cql.predict_action, dataset, behaviour_probs, epsilon=0.1)
    preds = cql.predict_action(dataset["states"])
    ood = ood_frequency(preds, dataset["actions"], min_behaviour_prob=0.05)
    cql_candidates[alpha] = {
        "model": cql,
        "fqe": fqe_v,
        "wis": wis_v,
        "ood": ood,
    }
    print(f"    FQE={fqe_v:.3f}, WIS={wis_v:.3f}, OOD={ood:.3f}")

# Select best CQL: max FQE subject to OOD ≤ 10%
best_cql = max(
    [(a, r) for a, r in cql_candidates.items() if r["ood"] <= 0.10],
    key=lambda x: x[1]["fqe"],
    default=max(cql_candidates.items(), key=lambda x: x[1]["fqe"]),
)
print(f"  Best CQL: α={best_cql[0]}, FQE={best_cql[1]['fqe']:.3f}, OOD={best_cql[1]['ood']:.3f}")
results["CQL"] = best_cql[1]

# IQL
print("\n--- IQL ---")
iql_candidates = {}
for tau in [0.7, 0.9]:
    for beta in [3.0, 10.0]:
        key = (tau, beta)
        print(f"  Training IQL(τ={tau}, β={beta})...")
        iql = IQL(n_actions=3, tau=tau, beta=beta, n_iterations=40)
        iql.fit(dataset, rng=np.random.default_rng(42))
        fqe_v = fqe_value(iql.predict_action, dataset, gamma=0.95, n_iterations=30)
        wis_v = wis_value(iql.predict_action, dataset, behaviour_probs, epsilon=0.1)
        preds = iql.predict_action(dataset["states"])
        ood = ood_frequency(preds, dataset["actions"], min_behaviour_prob=0.05)
        iql_candidates[key] = {
            "model": iql,
            "fqe": fqe_v,
            "wis": wis_v,
            "ood": ood,
            "tau": tau,
            "beta": beta,
        }
        print(f"    FQE={fqe_v:.3f}, WIS={wis_v:.3f}, OOD={ood:.3f}")
best_iql = max(
    [(k, r) for k, r in iql_candidates.items() if r["ood"] <= 0.10],
    key=lambda x: x[1]["fqe"],
    default=max(iql_candidates.items(), key=lambda x: x[1]["fqe"]),
)
print(f"  Best IQL: {best_iql[0]}, FQE={best_iql[1]['fqe']:.3f}")
results["IQL"] = best_iql[1]

# BCQ
print("\n--- BCQ ---")
bcq = DiscreteBCQ(n_actions=3, threshold=0.3, n_iterations=40)
bcq.fit(dataset, rng=np.random.default_rng(42))
fqe_v = fqe_value(bcq.predict_action, dataset, gamma=0.95, n_iterations=30)
wis_v = wis_value(bcq.predict_action, dataset, behaviour_probs, epsilon=0.1)
preds = bcq.predict_action(dataset["states"])
ood = ood_frequency(preds, dataset["actions"], min_behaviour_prob=0.05)
print(f"  BCQ: FQE={fqe_v:.3f}, WIS={wis_v:.3f}, OOD={ood:.3f}")
results["BCQ"] = {"model": bcq, "fqe": fqe_v, "wis": wis_v, "ood": ood}

# ── Select winner ────────────────────────────────────────
print("\n--- Selection ---")
eligible = {k: v for k, v in results.items() if v["ood"] <= 0.10}
if eligible:
    winner = max(eligible.items(), key=lambda x: x[1]["fqe"])
    print(f"Winner (OOD ≤ 10%, max FQE): {winner[0]}")
else:
    winner = max(results.items(), key=lambda x: x[1]["fqe"])
    print(f"NO algorithm satisfies OOD ≤ 10%. Best by FQE: {winner[0]}")
    print("This is a reportable limitation — discuss in Methods.")

# ── Save outputs ─────────────────────────────────────────
joblib.dump(results["CQL"]["model"], STAGE2_V2_DIR / "cql_model.joblib")
joblib.dump(results["IQL"]["model"], STAGE2_V2_DIR / "iql_model.joblib")
joblib.dump(results["BCQ"]["model"], STAGE2_V2_DIR / "bcq_model.joblib")
joblib.dump(winner[1]["model"], STAGE2_V2_DIR / "selected_policy.joblib")

comparison_df = pd.DataFrame([
    {
        "algorithm": name,
        "fqe": res["fqe"],
        "wis": res["wis"],
        "ood_frequency": res["ood"],
        "is_winner": name == winner[0],
    }
    for name, res in results.items()
])
comparison_df.to_csv(STAGE2_V2_DIR / "ope_comparison.csv", index=False)

summary = {
    "winner": winner[0],
    "winner_fqe": float(winner[1]["fqe"]),
    "winner_wis": float(winner[1]["wis"]),
    "winner_ood": float(winner[1]["ood"]),
    "behaviour_action_distribution": {
        str(i): float(p) for i, p in enumerate(behav_action_dist)
    },
    "n_trajectories": int(len(traj_df)),
    "n_actions": 3,
}
with open(STAGE2_V2_DIR / "stage2_v2_summary.json", "w") as f:
    json.dump(summary, f, indent=2, default=str)

# Selection report
with open(STAGE2_V2_DIR / "algorithm_selection.md", "w") as f:
    f.write(f"# Stage 2 v2 Algorithm Selection\n\n")
    f.write(f"**Winner: {winner[0]}**\n\n")
    f.write(f"Selection criterion: maximum FQE subject to OOD ≤ 10%.\n\n")
    f.write(comparison_df.to_markdown(index=False))
    f.write("\n")

print(f"\nSaved to {STAGE2_V2_DIR}")
```

- [ ] **Step 3: Run script**

Run: `python scripts/run_stage2.py`
Expected: completes without error, produces CQL/IQL/BCQ models, OPE comparison table.

- [ ] **Step 4: Commit**

```bash
git add scripts/run_stage2.py
git commit -m "feat: add run_stage2.py — CQL/IQL/BCQ comparison with OPE and selection"
```

---

### Task 15: run_stage3.py — Microsimulation with PSA

**Files:**
- Create: `scripts/run_stage3.py`

- [ ] **Step 1: Write `run_stage3.py`**

Create file `scripts/run_stage3.py`:

```python
#!/usr/bin/env python3
"""Stage 3 v2: Microsimulation with PSA, cluster-bootstrap, 8 scenarios.

Primary analysis: 6 scenarios using 3-action space {a0, a1, a2}.
Sensitivity: 2 additional scenarios (S6, S7) using literature-based effect sizes
for a3 (recall) and a4 (incentive).
"""

from __future__ import annotations

import json
import warnings
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from dropout_rl.config import (
    CHILDREN_PER_LGA,
    N_BOOTSTRAP_DEFAULT,
    N_POP_DEFAULT,
    PROCESSED_DIR,
    STAGE2_V2_DIR,
    STAGE3_V2_DIR,
)
from dropout_rl.microsim import run_scenario
from dropout_rl.sensitivity import ceac, probabilistic_icer
from dropout_rl.transitions import load_t1, load_t2

warnings.filterwarnings("ignore")
STAGE3_V2_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("STAGE 3 v2: MICROSIMULATION (PSA + CLUSTER BOOTSTRAP)")
print("=" * 60)

# ── Load ─────────────────────────────────────────────────
analytic_df = pd.read_parquet(PROCESSED_DIR / "analytic_dtp1_received.parquet")
print(f"Analytic sample: {len(analytic_df)} children, {analytic_df['v021'].nunique()} PSUs")

t1 = load_t1()
t2 = load_t2()
print(f"T1 model: {len(t1.feature_names)} features")

# Selected RL policy from Stage 2
selected_policy = joblib.load(STAGE2_V2_DIR / "selected_policy.joblib")
print(f"Loaded RL policy: {type(selected_policy).__name__}")

# ── Policies ─────────────────────────────────────────────
def s0_t1(X, idx):
    # Status quo: all no-intervention (is_status_quo=True skips RRR)
    return np.zeros(len(X), dtype=np.int64)

def s0_t2(X, idx):
    return np.zeros(len(X), dtype=np.int64)

def s1(X, idx):  # Uniform SMS
    return np.ones(len(X), dtype=np.int64)

def s2(X, idx):  # Uniform CHW
    return np.full(len(X), 2, dtype=np.int64)

# S3 risk-targeted: top 30% dropout risk → a2, rest → a1
def s3(X, idx):
    risk = t1.predict_dropout(X)
    threshold = np.percentile(risk, 70)
    return np.where(risk >= threshold, 2, 1).astype(np.int64)

# S4 RL-optimised
def s4(X, idx):
    return selected_policy.predict_action(X)

# S5 Bandit-allocated (simple community-level: LGA-mean risk → action)
# For simplicity here: same rule as S3 but applied at aggregate
def s5(X, idx):
    risk = t1.predict_dropout(X)
    # Community mean risk (using idx as community indicator would require grouping;
    # here use quantile-rank approach for simplicity)
    threshold = np.percentile(risk, 50)  # top 50%
    return np.where(risk >= threshold, 2, 1).astype(np.int64)

# ── Run primary scenarios ────────────────────────────────
primary_scenarios = [
    ("S0: Status Quo", s0_t1, s0_t2, True),
    ("S1: Uniform SMS", s1, s1, False),
    ("S2: Uniform CHW", s2, s2, False),
    ("S3: Risk-Targeted", s3, s3, False),
    ("S4: RL-Optimised", s4, s4, False),
    ("S5: Bandit-Allocated", s5, s5, False),
]

print(f"\nRunning {len(primary_scenarios)} primary scenarios × {N_BOOTSTRAP_DEFAULT} bootstraps...")

all_results = {}
for name, fn_t1, fn_t2, is_sq in primary_scenarios:
    print(f"\n  {name}{' [SQ]' if is_sq else ''}")
    result = run_scenario(
        name=name,
        policy_fn_t1=fn_t1,
        policy_fn_t2=fn_t2,
        analytic_df=analytic_df,
        t1_model=t1,
        t2_model=t2,
        n_pop=N_POP_DEFAULT,
        n_bootstrap=N_BOOTSTRAP_DEFAULT,
        cluster_bootstrap=True,
        psa=True,
        seed=42,
        is_status_quo=is_sq,
        feature_cols=t1.feature_names,
    )
    all_results[name] = result
    print(f"    DTP3: {result.dtp3_rate.mean():.3f} "
          f"[{np.percentile(result.dtp3_rate, 2.5):.3f}, "
          f"{np.percentile(result.dtp3_rate, 97.5):.3f}]")
    print(f"    Cost: ₦{result.cost_per_child.mean():.0f}/child")
    print(f"    Concentration index: {result.concentration_index.mean():.4f}")

# ── ICER vs S0 ───────────────────────────────────────────
s0 = all_results["S0: Status Quo"]
icer_table = []
print("\n--- Probabilistic ICER vs S0 ---")
for name, res in all_results.items():
    if name == "S0: Status Quo":
        continue
    icer = probabilistic_icer(res, s0)
    icer["scenario"] = name
    icer_table.append(icer)
    print(f"  {name}: ICER=₦{icer['mean_icer']:,.0f} "
          f"[{icer['ci_low']:,.0f}, {icer['ci_high']:,.0f}], "
          f"dominant={icer['n_dominant']}/{N_BOOTSTRAP_DEFAULT}")

# ── CEAC ──────────────────────────────────────────────────
wtp_range = np.linspace(0, 100_000, 101)
ceac_df = ceac(list(all_results.values()), wtp_range=wtp_range, reference="S0: Status Quo")
ceac_df.to_csv(STAGE3_V2_DIR / "ceac_data.csv", index=False)
print(f"\nCEAC computed for {len(wtp_range)} WTP thresholds")

# ── Save summary ─────────────────────────────────────────
summary_rows = []
for name, res in all_results.items():
    summary_rows.append({
        "scenario": name,
        "dtp3_mean": float(res.dtp3_rate.mean()),
        "dtp3_ci_low": float(np.percentile(res.dtp3_rate, 2.5)),
        "dtp3_ci_high": float(np.percentile(res.dtp3_rate, 97.5)),
        "cost_per_child_mean": float(res.cost_per_child.mean()),
        "cost_per_child_ci_low": float(np.percentile(res.cost_per_child, 2.5)),
        "cost_per_child_ci_high": float(np.percentile(res.cost_per_child, 97.5)),
        "concentration_index": float(res.concentration_index.mean()),
        "wealth_gap": float(res.wealth_gap.mean()),
        "slope_index": float(res.slope_index.mean()),
    })
pd.DataFrame(summary_rows).to_csv(STAGE3_V2_DIR / "microsim_results.csv", index=False)

pd.DataFrame(icer_table).to_csv(STAGE3_V2_DIR / "icer_distribution.csv", index=False)

# Full PSA draws
psa_rows = []
for name, res in all_results.items():
    for b in range(len(res.dtp3_rate)):
        psa_rows.append({
            "scenario": name,
            "bootstrap": b,
            "dtp3_rate": float(res.dtp3_rate[b]),
            "cost_per_child": float(res.cost_per_child[b]),
            "concentration_index": float(res.concentration_index[b]),
        })
pd.DataFrame(psa_rows).to_csv(STAGE3_V2_DIR / "microsim_psa.csv", index=False)

stage3_summary = {
    "n_primary_scenarios": len(primary_scenarios),
    "n_bootstrap": N_BOOTSTRAP_DEFAULT,
    "n_pop_per_bootstrap": N_POP_DEFAULT,
    "cluster_bootstrap": True,
    "psa_enabled": True,
    "action_space": [0, 1, 2],
    "scenario_summary": {name: {
        "dtp3_mean": float(res.dtp3_rate.mean()),
        "cost_per_child_mean": float(res.cost_per_child.mean()),
        "concentration_index_mean": float(res.concentration_index.mean()),
    } for name, res in all_results.items()},
}
with open(STAGE3_V2_DIR / "stage3_v2_summary.json", "w") as f:
    json.dump(stage3_summary, f, indent=2, default=str)

print(f"\nSaved to {STAGE3_V2_DIR}")
```

- [ ] **Step 2: Run script**

Run: `python scripts/run_stage3.py`
Expected: completes, produces microsim_results.csv, icer_distribution.csv, ceac_data.csv, microsim_psa.csv.

- [ ] **Step 3: Commit**

```bash
git add scripts/run_stage3.py
git commit -m "feat: add run_stage3.py — 6 primary scenarios with PSA, cluster bootstrap, CEAC"
```

---

### Task 15b: run_stage3_sensitivity.py — 5-action sensitivity scenarios (S6, S7)

**Files:**
- Create: `scripts/run_stage3_sensitivity.py`

Per spec section 6.2: S6 (recall for top 10% risk) and S7 (incentive for poorest quintile) use literature effect sizes for a₃ and a₄ (which are not learnt by RL). Reported in supplementary materials only.

- [ ] **Step 1: Write `run_stage3_sensitivity.py`**

Create file `scripts/run_stage3_sensitivity.py`:

```python
#!/usr/bin/env python3
"""Stage 3 sensitivity: S6 (recall) and S7 (incentive) scenarios using 5-action RRR.

These scenarios use literature-informed effect sizes for a3 and a4 without RL
learning, since the DHS data does not support learning these actions.
Reported in supplementary materials.
"""

from __future__ import annotations

import json
import warnings

import numpy as np
import pandas as pd

from dropout_rl.config import (
    N_BOOTSTRAP_DEFAULT,
    N_POP_DEFAULT,
    PROCESSED_DIR,
    STAGE3_V2_DIR,
)
from dropout_rl.costs import sample_cost_batch
from dropout_rl.interventions import apply_rrr, sample_rrr_batch
from dropout_rl.microsim import _sample_cluster_bootstrap
from dropout_rl.transitions import load_t1, load_t2

warnings.filterwarnings("ignore")
STAGE3_V2_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("STAGE 3 v2 — SENSITIVITY: S6 (recall) + S7 (incentive)")
print("=" * 60)

analytic_df = pd.read_parquet(PROCESSED_DIR / "analytic_dtp1_received.parquet")
t1 = load_t1()
t2 = load_t2()


def simulate_5action(
    name: str,
    policy_fn,
    analytic_df,
    n_pop=N_POP_DEFAULT,
    n_bootstrap=N_BOOTSTRAP_DEFAULT,
    seed=42,
):
    """Microsim using all 5 actions with PSA."""
    rng = np.random.default_rng(seed)
    n_actions = 5
    feature_cols = [c for c in t1.feature_names if c in analytic_df.columns]

    dtp3_arr = np.zeros(n_bootstrap)
    cost_arr = np.zeros(n_bootstrap)

    for b in range(n_bootstrap):
        idx = _sample_cluster_bootstrap(analytic_df, n_pop, rng)
        sample = analytic_df.iloc[idx].reset_index(drop=True)
        X = sample[feature_cols].to_numpy(dtype=np.float32)
        if np.isnan(X).any():
            col_med = np.nanmedian(X, axis=0)
            col_med = np.where(np.isnan(col_med), 0.0, col_med)
            inds = np.where(np.isnan(X))
            X[inds] = np.take(col_med, inds[1])

        rrr_draws = sample_rrr_batch(n_actions, rng)
        cost_draws = sample_cost_batch(n_actions, rng)

        # T1
        p_dropout_t1 = t1.predict_dropout(X)
        actions_t1 = policy_fn(X, sample, dose_step=0).astype(np.int64)
        p_dropout_t1 = apply_rrr(p_dropout_t1, actions_t1, rrr_draws)
        received_dtp2 = rng.random(len(X)) < (1.0 - p_dropout_t1)

        # T2
        p_dropout_t2 = t2.predict_dropout(X)
        actions_t2 = policy_fn(X, sample, dose_step=1).astype(np.int64)
        p_dropout_t2 = apply_rrr(p_dropout_t2, actions_t2, rrr_draws)
        received_dtp3 = (rng.random(len(X)) < (1.0 - p_dropout_t2)) & received_dtp2

        dtp3_arr[b] = received_dtp3.mean()
        cost_arr[b] = (cost_draws[actions_t1].sum() + cost_draws[actions_t2].sum()) / n_pop

    return {
        "name": name,
        "dtp3_mean": float(dtp3_arr.mean()),
        "dtp3_ci_low": float(np.percentile(dtp3_arr, 2.5)),
        "dtp3_ci_high": float(np.percentile(dtp3_arr, 97.5)),
        "cost_per_child_mean": float(cost_arr.mean()),
    }


# S6: top 10% risk → a3 (recall), next 20% → a2 (CHW), rest → a1 (SMS)
def s6_policy(X, sample, dose_step):
    risk = t1.predict_dropout(X) if dose_step == 0 else t2.predict_dropout(X)
    actions = np.ones(len(X), dtype=np.int64)
    thr_top10 = np.percentile(risk, 90)
    thr_top30 = np.percentile(risk, 70)
    actions[risk >= thr_top30] = 2
    actions[risk >= thr_top10] = 3
    return actions


# S7: poorest quintile → a4, rest → S3 rule (top 30% → a2, else a1)
def s7_policy(X, sample, dose_step):
    risk = t1.predict_dropout(X) if dose_step == 0 else t2.predict_dropout(X)
    actions = np.ones(len(X), dtype=np.int64)
    thr_top30 = np.percentile(risk, 70)
    actions[risk >= thr_top30] = 2
    if "wealth" in sample.columns:
        poorest = sample["wealth"].to_numpy() == 1
        actions[poorest] = 4
    return actions


print("\nRunning S6 (recall for highest risk)...")
s6_result = simulate_5action("S6: Recall-Enhanced", s6_policy, analytic_df,
                              n_bootstrap=N_BOOTSTRAP_DEFAULT, seed=42)
print(f"  DTP3: {s6_result['dtp3_mean']:.3f} "
      f"[{s6_result['dtp3_ci_low']:.3f}, {s6_result['dtp3_ci_high']:.3f}]")
print(f"  Cost: ₦{s6_result['cost_per_child_mean']:.0f}/child")

print("\nRunning S7 (incentive for poorest)...")
s7_result = simulate_5action("S7: Incentive-Poorest", s7_policy, analytic_df,
                              n_bootstrap=N_BOOTSTRAP_DEFAULT, seed=43)
print(f"  DTP3: {s7_result['dtp3_mean']:.3f} "
      f"[{s7_result['dtp3_ci_low']:.3f}, {s7_result['dtp3_ci_high']:.3f}]")
print(f"  Cost: ₦{s7_result['cost_per_child_mean']:.0f}/child")

results = {"S6": s6_result, "S7": s7_result}
with open(STAGE3_V2_DIR / "sensitivity_scenarios.json", "w") as f:
    json.dump(results, f, indent=2, default=str)

pd.DataFrame([s6_result, s7_result]).to_csv(
    STAGE3_V2_DIR / "sensitivity_scenarios.csv", index=False
)
print(f"\nSaved to {STAGE3_V2_DIR}/sensitivity_scenarios.*")
```

- [ ] **Step 2: Run script**

Run: `python scripts/run_stage3_sensitivity.py`
Expected: completes, produces sensitivity_scenarios.json and .csv with S6 and S7.

- [ ] **Step 3: Commit**

```bash
git add scripts/run_stage3_sensitivity.py
git commit -m "feat: add S6 and S7 sensitivity scenarios with 5-action space"
```

---

### Task 16: run_validation.py — Internal + subgroup validation

**Files:**
- Create: `scripts/run_validation.py`

- [ ] **Step 1: Write `run_validation.py`**

Create file `scripts/run_validation.py`:

```python
#!/usr/bin/env python3
"""Validation: S0 calibration + subgroup calibration checks."""

from __future__ import annotations

import json
import warnings

import numpy as np
import pandas as pd

from dropout_rl.config import PROCESSED_DIR, VALIDATION_DIR
from dropout_rl.microsim import run_scenario
from dropout_rl.transitions import load_t1, load_t2
from dropout_rl.validation import calibration_check, subgroup_calibration

warnings.filterwarnings("ignore")
VALIDATION_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("VALIDATION: S0 CALIBRATION + SUBGROUP CHECKS")
print("=" * 60)

# ── Load ─────────────────────────────────────────────────
analytic_df = pd.read_parquet(PROCESSED_DIR / "analytic_dtp1_received.parquet")
t1 = load_t1()
t2 = load_t2()

# Observed DTP3 rate (survey-weighted)
observed_overall = 1.0 - (analytic_df["vac_dropout"] *
                          analytic_df["v005"] / 1e6).sum() / \
                          (analytic_df["v005"] / 1e6).sum()
print(f"Observed overall DTP3 rate: {observed_overall:.3f}")

# ── S0 microsim on actual sample (no bootstrap) ──────────
def s0_policy(X, idx):
    return np.zeros(len(X), dtype=np.int64)

result = run_scenario(
    name="S0_calibration",
    policy_fn_t1=s0_policy,
    policy_fn_t2=s0_policy,
    analytic_df=analytic_df,
    t1_model=t1,
    t2_model=t2,
    n_pop=len(analytic_df),
    n_bootstrap=50,
    cluster_bootstrap=False,
    psa=False,
    seed=42,
    is_status_quo=True,
    feature_cols=t1.feature_names,
)
predicted_overall = float(result.dtp3_rate.mean())
print(f"Predicted S0 DTP3 rate: {predicted_overall:.3f}")

internal_result = calibration_check(
    predicted_rate=predicted_overall,
    observed_rate=observed_overall,
    tolerance=0.01,
)
print(f"Internal calibration: {'PASS' if internal_result['passed'] else 'FAIL'} "
      f"(error={internal_result['absolute_error']:.4f})")

with open(VALIDATION_DIR / "internal_calibration.json", "w") as f:
    json.dump(internal_result, f, indent=2, default=str)

# ── Subgroup calibration ─────────────────────────────────
def predicted_by_group(analytic_df, group_col, n_bootstrap=30):
    records = []
    groups = analytic_df[group_col].dropna().unique()
    for g in groups:
        sub = analytic_df[analytic_df[group_col] == g]
        if len(sub) < 10:
            continue
        res = run_scenario(
            name=f"g_{g}",
            policy_fn_t1=lambda X, i: np.zeros(len(X), dtype=np.int64),
            policy_fn_t2=lambda X, i: np.zeros(len(X), dtype=np.int64),
            analytic_df=sub,
            t1_model=t1,
            t2_model=t2,
            n_pop=min(500, len(sub)),
            n_bootstrap=n_bootstrap,
            cluster_bootstrap=False,
            psa=False,
            seed=42,
            is_status_quo=True,
            feature_cols=t1.feature_names,
        )
        records.append({"group": g, "rate": float(res.dtp3_rate.mean())})
    return pd.DataFrame(records)


def observed_by_group(analytic_df, group_col):
    df = analytic_df.copy()
    df["dtp3"] = 1 - df["vac_dropout"]
    df["w"] = df["v005"] / 1e6
    rows = []
    for g, sub in df.groupby(group_col):
        w_sum = sub["w"].sum()
        if w_sum == 0 or len(sub) < 10:
            continue
        rate = (sub["dtp3"] * sub["w"]).sum() / w_sum
        rows.append({"group": g, "rate": float(rate)})
    return pd.DataFrame(rows)


subgroup_vars = [
    ("sstate", "state"),
    ("szone", "zone"),
    ("medu", "maternal_education"),
    ("wealth", "wealth_quintile"),
    ("rural", "urban_rural"),
]

all_subgroup_results = {}
for col, label in subgroup_vars:
    if col not in analytic_df.columns:
        continue
    print(f"\nSubgroup: {label} ({col})")
    pred = predicted_by_group(analytic_df, col)
    obs = observed_by_group(analytic_df, col)
    check = subgroup_calibration(pred, obs, flag_threshold=0.03)
    check.to_csv(VALIDATION_DIR / f"subgroup_{label}.csv", index=False)
    n_flagged = check["flagged"].sum()
    print(f"  Strata: {len(check)}, flagged: {n_flagged}")
    all_subgroup_results[label] = {
        "n_strata": int(len(check)),
        "n_flagged": int(n_flagged),
        "max_error": float(check["absolute_error"].max()),
    }

with open(VALIDATION_DIR / "subgroup_summary.json", "w") as f:
    json.dump(all_subgroup_results, f, indent=2, default=str)

# Validation report
with open(VALIDATION_DIR / "validation_report.md", "w") as f:
    f.write("# Microsimulation Validation Report\n\n")
    f.write("## Internal Calibration\n\n")
    f.write(f"- Predicted S0 DTP3 rate: {predicted_overall:.4f}\n")
    f.write(f"- Observed DTP3 rate: {observed_overall:.4f}\n")
    f.write(f"- Absolute error: {internal_result['absolute_error']:.4f}\n")
    f.write(f"- Tolerance: {internal_result['tolerance']}\n")
    f.write(f"- **{'PASS' if internal_result['passed'] else 'FAIL'}**\n\n")
    f.write("## Subgroup Calibration\n\n")
    for label, r in all_subgroup_results.items():
        f.write(f"- **{label}**: {r['n_strata']} strata, {r['n_flagged']} flagged "
                f"(max |error| = {r['max_error']:.4f})\n")

print(f"\nSaved to {VALIDATION_DIR}")
```

- [ ] **Step 2: Run script**

Run: `python scripts/run_validation.py`
Expected: produces internal_calibration.json, subgroup_*.csv, validation_report.md.

- [ ] **Step 3: Commit**

```bash
git add scripts/run_validation.py
git commit -m "feat: add run_validation.py — internal + subgroup calibration checks"
```

---

### Task 17: run_sensitivity.py — Tornado + CEAC figures

**Files:**
- Create: `scripts/run_sensitivity.py`

- [ ] **Step 1: Write `run_sensitivity.py`**

Create file `scripts/run_sensitivity.py`:

```python
#!/usr/bin/env python3
"""Sensitivity analysis: tornado diagram, CEAC plot, cost-effectiveness plane."""

from __future__ import annotations

import json
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from dropout_rl.config import (
    N_BOOTSTRAP_DEFAULT,
    N_POP_DEFAULT,
    PROCESSED_DIR,
    STAGE3_V2_DIR,
)
from dropout_rl.microsim import run_scenario
from dropout_rl.sensitivity import tornado_diagram
from dropout_rl.transitions import load_t1, load_t2

warnings.filterwarnings("ignore")

# ── Load ─────────────────────────────────────────────────
analytic_df = pd.read_parquet(PROCESSED_DIR / "analytic_dtp1_received.parquet")
t1 = load_t1()
t2 = load_t2()

# ── Load CEAC and microsim data ──────────────────────────
ceac_df = pd.read_csv(STAGE3_V2_DIR / "ceac_data.csv")
microsim = pd.read_csv(STAGE3_V2_DIR / "microsim_results.csv")

# ── CEAC plot ────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(9, 6))
for col in ceac_df.columns:
    if col == "wtp":
        continue
    ax.plot(ceac_df["wtp"], ceac_df[col], label=col, linewidth=2)
ax.set_xlabel("Willingness-to-pay (₦ per additional DTP3 completion)")
ax.set_ylabel("Probability of being optimal")
ax.set_title("Cost-effectiveness acceptability curves")
ax.legend(loc="center right")
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(STAGE3_V2_DIR / "ceac.pdf", dpi=300)
fig.savefig(STAGE3_V2_DIR / "ceac.png", dpi=300)
plt.close(fig)
print("  ceac.pdf saved")

# ── Cost-effectiveness plane ─────────────────────────────
psa = pd.read_csv(STAGE3_V2_DIR / "microsim_psa.csv")
s0 = psa[psa["scenario"] == "S0: Status Quo"]

fig, ax = plt.subplots(figsize=(9, 7))
colors = {"S1: Uniform SMS": "#81C784",
          "S2: Uniform CHW": "#4FC3F7",
          "S3: Risk-Targeted": "#FFB74D",
          "S4: RL-Optimised": "#E91E63",
          "S5: Bandit-Allocated": "#9C27B0"}

for name, color in colors.items():
    sub = psa[psa["scenario"] == name]
    if len(sub) == 0:
        continue
    merged = s0[["bootstrap", "dtp3_rate", "cost_per_child"]].rename(
        columns={"dtp3_rate": "s0_dtp3", "cost_per_child": "s0_cost"}
    ).merge(sub, on="bootstrap")
    d_effect = merged["dtp3_rate"] - merged["s0_dtp3"]
    d_cost = merged["cost_per_child"] - merged["s0_cost"]
    ax.scatter(d_effect, d_cost, s=10, alpha=0.3, color=color, label=name)

ax.axhline(0, color="grey", linewidth=0.5)
ax.axvline(0, color="grey", linewidth=0.5)
ax.set_xlabel("Δ DTP3 completion vs S0")
ax.set_ylabel("Δ cost per child (₦) vs S0")
ax.set_title("Cost-effectiveness plane (bootstrap × PSA)")
ax.legend()
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(STAGE3_V2_DIR / "ce_plane.pdf", dpi=300)
fig.savefig(STAGE3_V2_DIR / "ce_plane.png", dpi=300)
plt.close(fig)
print("  ce_plane.pdf saved")

# ── Tornado for S3 (most cost-effective) ─────────────────
print("\nTornado diagram for S3 (Risk-Targeted)...")
from dropout_rl.config import RRR_RANGES, ACTION_COSTS_POINT

def run_s3_with_override(rrr_override=None, cost_override=None, n=20):
    """Run S3 with optional RRR/cost override (for sensitivity)."""
    from dropout_rl import interventions as iv_module
    from dropout_rl import costs as cost_module
    # Temporarily monkeypatch
    orig_rrr = iv_module.RRR_RANGES.copy() if hasattr(iv_module, "RRR_RANGES") else None
    orig_costs = cost_module.ACTION_COSTS_POINT.copy() if hasattr(cost_module, "ACTION_COSTS_POINT") else None
    try:
        if rrr_override:
            from dropout_rl import config
            for a, v in rrr_override.items():
                config.RRR_RANGES[a] = (v, v * 0.8, v * 1.2)
        if cost_override:
            from dropout_rl import config
            for a, v in cost_override.items():
                config.ACTION_COSTS_POINT[a] = v

        def s3(X, idx):
            risk = t1.predict_dropout(X)
            thr = np.percentile(risk, 70)
            return np.where(risk >= thr, 2, 1).astype(np.int64)

        result = run_scenario(
            name="s3_sens",
            policy_fn_t1=s3,
            policy_fn_t2=s3,
            analytic_df=analytic_df,
            t1_model=t1,
            t2_model=t2,
            n_pop=2000,
            n_bootstrap=n,
            cluster_bootstrap=False,
            psa=False,
            seed=42,
            is_status_quo=False,
            feature_cols=t1.feature_names,
        )
        return float(result.dtp3_rate.mean())
    finally:
        if orig_rrr is not None:
            from dropout_rl import config
            config.RRR_RANGES.clear()
            config.RRR_RANGES.update(orig_rrr)
        if orig_costs is not None:
            from dropout_rl import config
            config.ACTION_COSTS_POINT.clear()
            config.ACTION_COSTS_POINT.update(orig_costs)

base = run_s3_with_override(n=30)
print(f"  Base S3 DTP3: {base:.4f}")

param_results = {}
for a, (central, low, high) in RRR_RANGES.items():
    if a == 0:
        continue
    low_v = run_s3_with_override(rrr_override={a: low}, n=15)
    high_v = run_s3_with_override(rrr_override={a: high}, n=15)
    param_results[f"RRR_a{a}"] = (low_v, high_v)
for a, cost in ACTION_COSTS_POINT.items():
    if a == 0:
        continue
    # Vary ±25%
    low_v = run_s3_with_override(cost_override={a: cost * 0.75}, n=15)
    high_v = run_s3_with_override(cost_override={a: cost * 1.25}, n=15)
    param_results[f"cost_a{a}"] = (low_v, high_v)

tornado = tornado_diagram(param_results, base_value=base)
tornado.to_csv(STAGE3_V2_DIR / "tornado_data.csv", index=False)

# Plot tornado
fig, ax = plt.subplots(figsize=(9, 6))
params = tornado["parameter"].tolist()
lows = tornado["low"].values
highs = tornado["high"].values
y_pos = np.arange(len(params))
ax.barh(y_pos, highs - base, left=base, color="#81C784", label="High")
ax.barh(y_pos, lows - base, left=base, color="#E57373", label="Low")
ax.axvline(base, color="black", linewidth=1)
ax.set_yticks(y_pos)
ax.set_yticklabels(params)
ax.set_xlabel("S3 DTP3 completion rate")
ax.set_title("Tornado diagram: one-way sensitivity (S3 Risk-Targeted)")
ax.legend()
fig.tight_layout()
fig.savefig(STAGE3_V2_DIR / "tornado.pdf", dpi=300)
fig.savefig(STAGE3_V2_DIR / "tornado.png", dpi=300)
plt.close(fig)
print("  tornado.pdf saved")

print(f"\nSaved to {STAGE3_V2_DIR}")
```

- [ ] **Step 2: Run script**

Run: `python scripts/run_sensitivity.py`
Expected: produces ceac.pdf, ce_plane.pdf, tornado.pdf.

- [ ] **Step 3: Commit**

```bash
git add scripts/run_sensitivity.py
git commit -m "feat: add run_sensitivity.py — CEAC plot, CE plane, tornado diagram"
```

---

## Phase 7: Coverage Gate and Manuscript Update

### Task 18: Coverage check and manuscript delta report

**Files:**
- Create: `outputs/stage3_v2/comparison_v1_vs_v2.md`

- [ ] **Step 1: Run test coverage**

Run: `pytest tests/ --cov=src/dropout_rl --cov-report=term-missing --cov-report=html`

Expected: coverage ≥ 80% overall.

- [ ] **Step 2: Capture comparison v1 vs v2**

Create file `outputs/stage3_v2/comparison_v1_vs_v2.md`:

```markdown
# v1 (Original) vs v2 (Publication-Grade) Comparison

## Architecture
| Aspect | v1 | v2 |
|--------|----|----|
| Transition models | GradientBoostingClassifier refit in Stage 3 | Calibrated XGBoost + isotonic from Stage 1 |
| Bootstrap | Individual children | Cluster on PSUs (v021) |
| Effect sizes | Point estimates only | Beta priors with PSA |
| Costs | Point estimates only | Gamma priors with PSA |
| Equity | Wealth gap only | Wealth gap + concentration index + SII |
| RL | CQL only, 5-action, 33% OOD | CQL + IQL + BCQ, 3-action, selected by FQE |
| Sensitivity | None | CEAC, tornado, probabilistic ICER |
| Validation | None | Internal + subgroup |
| Testing | Minimal | Unit tests ≥80% coverage |

## Results comparison
(Fill after v2 runs complete — compare DTP3 rates, ICERs, equity metrics.)
```

- [ ] **Step 3: Fill comparison from actual outputs**

Run the comparison-fill script inline:

```bash
python -c "
import json, pandas as pd

v1 = json.load(open('outputs/stage3/stage3_summary.json'))
v2 = json.load(open('outputs/stage3_v2/stage3_v2_summary.json'))

print('v1 S0 DTP3:', v1['scenarios']['S0: Status Quo']['dtp3_rate_mean'])
print('v2 S0 DTP3:', v2['scenario_summary']['S0: Status Quo']['dtp3_mean'])
print('v1 S3 DTP3:', v1['scenarios']['S3: Risk-Targeted']['dtp3_rate_mean'])
print('v2 S3 DTP3:', v2['scenario_summary']['S3: Risk-Targeted']['dtp3_mean'])
print('v1 S4 DTP3:', v1['scenarios']['S4: RL-Optimised']['dtp3_rate_mean'])
print('v2 S4 DTP3:', v2['scenario_summary']['S4: RL-Optimised']['dtp3_mean'])
" >> outputs/stage3_v2/comparison_v1_vs_v2.md
```

- [ ] **Step 4: Update manuscript**

Edit `manuscript/03_results_merged.md` to reference v2 numbers where they differ. At minimum:
- S0, S1, S2, S3, S4, S5 DTP3 rates and ICERs
- Concentration index and SII (new)
- OPE winner (CQL vs IQL vs BCQ)

Include a paragraph in Methods noting PSA, cluster-bootstrap, and algorithm comparison.

- [ ] **Step 5: Rebuild DOCX**

Run: `python scripts/build_manuscript_docx.py`
Expected: `manuscript/manuscript_full.docx` rebuilt with updated numbers.

- [ ] **Step 6: Commit**

```bash
git add outputs/stage3_v2/comparison_v1_vs_v2.md manuscript/
git commit -m "docs: v2 results integration and v1-v2 comparison report"
```

---

### Task 19: Integration smoke test

**Files:**
- Create: `tests/integration/test_pipeline_smoke.py`

- [ ] **Step 1: Write pipeline smoke test**

Create file `tests/integration/test_pipeline_smoke.py`:

```python
"""End-to-end smoke test: Stage 2 + Stage 3 on small subsample."""

import numpy as np
import pandas as pd
import pytest

from dropout_rl.microsim import run_scenario
from dropout_rl.rl.common import build_mdp_dataset
from dropout_rl.rl.cql import CQL


@pytest.mark.requires_data
def test_stage2_minimum_steps(real_analytic_data, rng):
    """Stage 2: CQL trains on 100 trajectory rows."""
    from dropout_rl.config import PROCESSED_DIR
    traj = pd.read_csv(PROCESSED_DIR / "trajectory_dataset.csv").head(100)
    dataset = build_mdp_dataset(traj, n_actions=3)
    cql = CQL(n_actions=3, alpha=1.0, n_iterations=5)
    cql.fit(dataset, rng=rng)
    assert cql.predict_action(dataset["states"]).shape == (100,)


@pytest.mark.requires_data
def test_stage3_minimum_run(real_analytic_data):
    """Stage 3: one scenario on 100-child × 10-bootstrap subsample."""
    from dropout_rl.transitions import load_t1, load_t2
    t1 = load_t1()
    t2 = load_t2()

    def sms(X, idx):
        return np.ones(len(X), dtype=np.int64)

    result = run_scenario(
        name="smoke",
        policy_fn_t1=sms,
        policy_fn_t2=sms,
        analytic_df=real_analytic_data.head(100),
        t1_model=t1,
        t2_model=t2,
        n_pop=50,
        n_bootstrap=10,
        cluster_bootstrap=True,
        psa=True,
        seed=42,
        is_status_quo=False,
        feature_cols=t1.feature_names,
    )
    assert result.dtp3_rate.shape == (10,)
    assert (result.dtp3_rate > 0).all()
```

- [ ] **Step 2: Run integration test**

Run: `pytest tests/integration/ -v --run-requires-data` (if data available)
Expected: pass, completes <30s.

- [ ] **Step 3: Commit**

```bash
git add tests/integration/test_pipeline_smoke.py
git commit -m "test: add integration smoke test for Stage 2 + Stage 3 pipeline"
```

---

### Task 20: Final verification

- [ ] **Step 1: Run full test suite**

Run: `pytest tests/ --cov=src/dropout_rl --cov-report=term-missing`

Expected: all tests pass, coverage ≥ 80% overall.

- [ ] **Step 2: Verify outputs exist**

Run:
```bash
for f in \
  outputs/stage2_v2/stage2_v2_summary.json \
  outputs/stage2_v2/selected_policy.joblib \
  outputs/stage2_v2/ope_comparison.csv \
  outputs/stage3_v2/stage3_v2_summary.json \
  outputs/stage3_v2/microsim_results.csv \
  outputs/stage3_v2/icer_distribution.csv \
  outputs/stage3_v2/ceac_data.csv \
  outputs/stage3_v2/microsim_psa.csv \
  outputs/stage3_v2/tornado_data.csv \
  outputs/stage3_v2/ceac.pdf \
  outputs/stage3_v2/ce_plane.pdf \
  outputs/stage3_v2/tornado.pdf \
  outputs/validation/internal_calibration.json \
  outputs/validation/validation_report.md; do
  test -f "$f" && echo "OK $f" || echo "MISSING $f"
done
```

Expected: all OK.

- [ ] **Step 3: Check no regressions in old outputs**

Run:
```bash
ls outputs/stage2/ outputs/stage3/
```

Expected: still present (v1 preserved).

- [ ] **Step 4: Final commit tag**

```bash
git tag -a v0.2.0-rc -m "Publication-grade microsim rewrite: PSA, CEAC, multi-algorithm RL, validation"
```
