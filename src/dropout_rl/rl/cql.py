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
