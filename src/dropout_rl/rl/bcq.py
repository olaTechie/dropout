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
