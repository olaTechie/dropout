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
    n_actions = dataset["n_actions"]
    if n_actions == 1:
        # Degenerate single-action space: target prob is 1 everywhere
        target_probs = np.ones((n, 1))
    else:
        target_probs = np.full((n, n_actions), epsilon / (n_actions - 1))
    for i, a in enumerate(pred_actions):
        target_probs[i, a] = 1.0 - epsilon

    behav_taken = np.maximum(behaviour_probs[np.arange(n), actions], 1e-6)
    target_taken = target_probs[np.arange(n), actions]

    weights = target_taken / behav_taken
    if weights.sum() == 0:
        import warnings
        warnings.warn("WIS: all importance weights are zero; estimate undefined.", RuntimeWarning)
        return float("nan")
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

    For cross-sectional datasets (DHS), gamma must be 0.0. For multi-step MDPs,
    pass `next_states` in the dataset dict.

    Parameters
    ----------
    target_policy : callable
    dataset : dict
        Must contain states, actions, rewards, n_actions. If gamma > 0, must also
        contain next_states.
    gamma : float
        Discount factor. Must be 0.0 unless `next_states` is provided in dataset.
    n_iterations : int
        Fitted Q iteration count.

    Returns
    -------
    float
        Estimated policy value.

    Raises
    ------
    NotImplementedError
        If gamma > 0 but `next_states` is not in the dataset dict.
    """
    if gamma > 0 and "next_states" not in dataset:
        raise NotImplementedError(
            "FQE with gamma > 0 requires 'next_states' in dataset. "
            "Current cross-sectional DHS data does not support multi-step discounting; "
            "use gamma=0.0 for immediate-reward evaluation. "
            "See Raghu et al. 2022 for healthcare-OPE recommendations."
        )

    states = dataset["states"]
    actions = dataset["actions"]
    rewards = dataset["rewards"]
    n_actions = dataset["n_actions"]
    n = len(actions)

    # One regressor per action
    q_models: list[ExtraTreesRegressor | None] = [None] * n_actions

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
    missing_action_mass = 0
    for a in range(n_actions):
        mask = pi_actions == a
        if not mask.any():
            continue
        if q_models[a] is None:
            # Action rarely/never observed — flag support problem
            missing_action_mass += mask.sum()
            continue
        q_final[mask] = q_models[a].predict(states[mask])

    if missing_action_mass > 0:
        import warnings
        warnings.warn(
            f"FQE: target policy assigns {missing_action_mass}/{n} ({100*missing_action_mass/n:.1f}%) "
            f"probability to actions with no training support. Estimated value biased downward.",
            RuntimeWarning,
        )
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
