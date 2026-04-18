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
