"""Health equity metrics: wealth gap, concentration index, slope index of inequality.

All three metrics take binary or continuous outcomes and wealth quintile (1-5)
or wealth rank. Concentration index and SII are the standards in health
equity literature.

All public functions accept an optional ``weights`` parameter to support survey-
weighted estimates (per CLAUDE.md DHS survey weight requirement, e.g., ``v005/1e6``).
When ``weights`` is None, unweighted estimates are returned.
"""

from __future__ import annotations

import numpy as np


def wealth_gap(
    outcomes: np.ndarray,
    wealth_quintile: np.ndarray,
    weights: np.ndarray | None = None,
) -> float:
    """Richest minus poorest quintile outcome rate.

    Parameters
    ----------
    outcomes : np.ndarray of shape (n,)
        Individual outcomes (e.g., DTP3 completion 0/1).
    wealth_quintile : np.ndarray of shape (n,)
        Wealth quintile, values in {1, 2, 3, 4, 5}.
    weights : np.ndarray of shape (n,), optional
        Survey weights (e.g., DHS ``v005/1e6``). If None, unweighted means are used.

    Returns
    -------
    float
        Richest quintile rate minus poorest quintile rate.
    """
    y = np.asarray(outcomes, dtype=float)
    w = np.asarray(wealth_quintile)
    if len(y) != len(w):
        raise ValueError(f"Length mismatch: outcomes {len(y)}, wealth {len(w)}")

    poorest_mask = w == w.min()
    richest_mask = w == w.max()
    if not poorest_mask.any() or not richest_mask.any():
        return float("nan")

    if weights is not None:
        wts = np.asarray(weights, dtype=float)
        if len(wts) != len(y):
            raise ValueError(
                f"Length mismatch: outcomes {len(y)}, weights {len(wts)}"
            )
        poorest_mean = (y[poorest_mask] * wts[poorest_mask]).sum() / wts[poorest_mask].sum()
        richest_mean = (y[richest_mask] * wts[richest_mask]).sum() / wts[richest_mask].sum()
        return float(richest_mean - poorest_mean)

    return float(y[richest_mask].mean() - y[poorest_mask].mean())


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


def concentration_index(
    outcomes: np.ndarray,
    wealth: np.ndarray,
    weights: np.ndarray | None = None,
) -> float:
    """Wagstaff concentration index.

    CI = 2 * cov(y, R) / mean(y), where R is the ridit-scored wealth rank.
    Ranges in [-1, 1]: positive means outcome concentrated in richer; negative
    means concentrated in poorer; zero means perfect equity.

    Parameters
    ----------
    outcomes : np.ndarray of shape (n,)
    wealth : np.ndarray of shape (n,)
        Wealth score or quintile; ranks are computed internally.
    weights : np.ndarray of shape (n,), optional
        Survey weights. If None, unweighted covariance and mean are used.

    Returns
    -------
    float
        Concentration index in [-1, 1].
    """
    y = np.asarray(outcomes, dtype=float)
    w = np.asarray(wealth, dtype=float)
    if len(y) != len(w):
        raise ValueError(f"Length mismatch: outcomes {len(y)}, wealth {len(w)}")

    ranks = _ridit_rank(w)

    if weights is not None:
        wts = np.asarray(weights, dtype=float)
        if len(wts) != len(y):
            raise ValueError(
                f"Length mismatch: outcomes {len(y)}, weights {len(wts)}"
            )
        w_sum = wts.sum()
        y_mean_w = (y * wts).sum() / w_sum
        r_mean_w = (ranks * wts).sum() / w_sum
        if abs(y_mean_w) < 1e-12:
            return 0.0
        cov_yr = ((y - y_mean_w) * (ranks - r_mean_w) * wts).sum() / w_sum
        return float(2.0 * cov_yr / y_mean_w)

    if abs(y.mean()) < 1e-12:
        return 0.0

    cov_yr = np.cov(y, ranks, ddof=0)[0, 1]
    return float(2.0 * cov_yr / y.mean())


def slope_index_of_inequality(
    outcomes: np.ndarray,
    wealth: np.ndarray,
    weights: np.ndarray | None = None,
) -> float:
    """Slope Index of Inequality (SII).

    Linear regression of outcome on ridit-scored wealth rank. Interpretation:
    the difference in outcome between the hypothetical lowest-rank and
    highest-rank person.

    Parameters
    ----------
    outcomes : np.ndarray of shape (n,)
    wealth : np.ndarray of shape (n,)
    weights : np.ndarray of shape (n,), optional
        Survey weights. If None, unweighted OLS is used.

    Returns
    -------
    float
        SII: positive means advantage to richer, negative to poorer.
    """
    y = np.asarray(outcomes, dtype=float)
    w = np.asarray(wealth, dtype=float)
    if len(y) != len(w):
        raise ValueError(f"Length mismatch: outcomes {len(y)}, wealth {len(w)}")

    ranks = _ridit_rank(w)

    if weights is not None:
        wts = np.asarray(weights, dtype=float)
        if len(wts) != len(y):
            raise ValueError(
                f"Length mismatch: outcomes {len(y)}, weights {len(wts)}"
            )
        w_sum = wts.sum()
        r_mean_w = (ranks * wts).sum() / w_sum
        y_mean_w = (y * wts).sum() / w_sum
        denom = ((ranks - r_mean_w) ** 2 * wts).sum()
        if denom == 0:
            return 0.0
        slope = ((ranks - r_mean_w) * (y - y_mean_w) * wts).sum() / denom
        return float(slope)

    # Unweighted OLS slope
    r_mean = ranks.mean()
    y_mean = y.mean()
    denom = ((ranks - r_mean) ** 2).sum()
    if denom == 0:
        return 0.0
    slope = ((ranks - r_mean) * (y - y_mean)).sum() / denom
    return float(slope)
