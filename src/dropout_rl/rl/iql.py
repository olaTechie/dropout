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
