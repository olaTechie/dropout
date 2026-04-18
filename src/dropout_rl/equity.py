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
