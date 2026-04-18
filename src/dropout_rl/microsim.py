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
