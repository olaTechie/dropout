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
