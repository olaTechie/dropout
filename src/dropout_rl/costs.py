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
