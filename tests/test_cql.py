"""Tests for dropout_rl.rl.cql."""

import numpy as np
import pytest

from dropout_rl.rl.cql import CQL


class TestCQL:
    def test_fit_smoke(self, rng):
        """Smoke test: CQL trains without error on toy dataset."""
        dataset = {
            "states": rng.standard_normal((200, 5)).astype(np.float32),
            "actions": rng.integers(0, 3, size=200),
            "rewards": rng.uniform(0, 1, size=200).astype(np.float32),
            "weights": np.ones(200, dtype=np.float32),
            "n_actions": 3,
        }
        cql = CQL(n_actions=3, alpha=1.0, n_iterations=10)
        cql.fit(dataset, rng=rng)
        actions = cql.predict_action(dataset["states"])
        assert actions.shape == (200,)
        assert actions.max() < 3

    def test_predict_q_shape(self, rng):
        dataset = {
            "states": rng.standard_normal((50, 5)).astype(np.float32),
            "actions": rng.integers(0, 3, size=50),
            "rewards": rng.uniform(0, 1, size=50).astype(np.float32),
            "weights": np.ones(50, dtype=np.float32),
            "n_actions": 3,
        }
        cql = CQL(n_actions=3, alpha=1.0, n_iterations=5)
        cql.fit(dataset, rng=rng)
        q = cql.predict_q(dataset["states"])
        assert q.shape == (50, 3)
