"""Tests for dropout_rl.rl.bcq."""

import numpy as np
import pytest

from dropout_rl.rl.bcq import DiscreteBCQ


class TestDiscreteBCQ:
    def test_fit_smoke(self, rng):
        dataset = {
            "states": rng.standard_normal((200, 5)).astype(np.float32),
            "actions": rng.integers(0, 3, size=200),
            "rewards": rng.uniform(0, 1, size=200).astype(np.float32),
            "weights": np.ones(200, dtype=np.float32),
            "n_actions": 3,
        }
        bcq = DiscreteBCQ(n_actions=3, threshold=0.3, n_iterations=10)
        bcq.fit(dataset, rng=rng)
        actions = bcq.predict_action(dataset["states"])
        assert actions.shape == (200,)

    def test_respects_threshold(self, rng):
        """BCQ should not recommend actions with behaviour prob < threshold."""
        n = 500
        # Heavily skewed actions: 90% action 0, 10% action 1, 0% action 2
        actions = np.concatenate([np.zeros(450), np.ones(50)]).astype(np.int64)
        rng.shuffle(actions)
        dataset = {
            "states": rng.standard_normal((n, 5)).astype(np.float32),
            "actions": actions,
            "rewards": rng.uniform(0, 1, size=n).astype(np.float32),
            "weights": np.ones(n, dtype=np.float32),
            "n_actions": 3,
        }
        bcq = DiscreteBCQ(n_actions=3, threshold=0.3, n_iterations=20)
        bcq.fit(dataset, rng=rng)
        preds = bcq.predict_action(dataset["states"])
        # Action 2 (0% behaviour) should never be recommended
        assert (preds == 2).sum() == 0
