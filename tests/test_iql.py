"""Tests for dropout_rl.rl.iql."""

import numpy as np
import pytest

from dropout_rl.rl.iql import IQL


class TestIQL:
    def test_fit_smoke(self, rng):
        dataset = {
            "states": rng.standard_normal((200, 5)).astype(np.float32),
            "actions": rng.integers(0, 3, size=200),
            "rewards": rng.uniform(0, 1, size=200).astype(np.float32),
            "weights": np.ones(200, dtype=np.float32),
            "n_actions": 3,
        }
        iql = IQL(n_actions=3, tau=0.8, beta=3.0, n_iterations=10)
        iql.fit(dataset, rng=rng)
        actions = iql.predict_action(dataset["states"])
        assert actions.shape == (200,)

    def test_predict_q_shape(self, rng):
        dataset = {
            "states": rng.standard_normal((50, 5)).astype(np.float32),
            "actions": rng.integers(0, 3, size=50),
            "rewards": rng.uniform(0, 1, size=50).astype(np.float32),
            "weights": np.ones(50, dtype=np.float32),
            "n_actions": 3,
        }
        iql = IQL(n_actions=3, n_iterations=5)
        iql.fit(dataset, rng=rng)
        q = iql.predict_q(dataset["states"])
        assert q.shape == (50, 3)
