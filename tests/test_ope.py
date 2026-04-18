"""Tests for dropout_rl.rl.ope using a toy 2-state 2-action MDP."""

import numpy as np
import pytest

from dropout_rl.rl.ope import (
    fqe_value,
    ood_frequency,
    wis_value,
)


def _toy_dataset(rng):
    """Two-state, two-action MDP where action 1 always yields reward 1.0."""
    n = 1000
    states = rng.standard_normal((n, 2)).astype(np.float32)
    # Behaviour policy: random
    actions = rng.integers(0, 2, size=n)
    # Reward: action 1 → 1.0, action 0 → 0.0
    rewards = actions.astype(np.float32)
    weights = np.ones(n, dtype=np.float32)
    return {
        "states": states,
        "actions": actions,
        "rewards": rewards,
        "weights": weights,
        "n_actions": 2,
    }


def _always_action_1(states):
    return np.ones(len(states), dtype=np.int64)


def _always_action_0(states):
    return np.zeros(len(states), dtype=np.int64)


class TestWIS:
    def test_recovers_known_value(self, rng):
        """π=always-1 under random behaviour: WIS ≈ 1.0."""
        dataset = _toy_dataset(rng)
        value = wis_value(
            target_policy=_always_action_1,
            dataset=dataset,
            behaviour_probs=np.full((len(dataset["actions"]), 2), 0.5),
            epsilon=0.1,
        )
        assert 0.8 < value < 1.2

    def test_low_value_for_action_0(self, rng):
        dataset = _toy_dataset(rng)
        value = wis_value(
            target_policy=_always_action_0,
            dataset=dataset,
            behaviour_probs=np.full((len(dataset["actions"]), 2), 0.5),
            epsilon=0.1,
        )
        assert value < 0.2


class TestFQE:
    def test_recovers_known_value(self, rng):
        """FQE for π=always-1: V ≈ 1.0."""
        dataset = _toy_dataset(rng)
        value = fqe_value(
            target_policy=_always_action_1,
            dataset=dataset,
            gamma=0.0,  # Immediate reward only
            n_iterations=50,
        )
        assert 0.8 < value < 1.2


class TestOODFrequency:
    def test_matching_behaviour_zero_ood(self, rng):
        dataset = _toy_dataset(rng)
        # Target = behaviour: zero OOD
        def target(states):
            # Same distribution as dataset actions
            return dataset["actions"][: len(states)]
        freq = ood_frequency(
            target_actions=dataset["actions"],
            behaviour_actions=dataset["actions"],
            min_behaviour_prob=0.01,
        )
        assert freq == 0.0

    def test_fully_ood_when_action_never_observed(self):
        # Behaviour: all 0s; target: all 1s
        behav = np.zeros(100, dtype=np.int64)
        target = np.ones(100, dtype=np.int64)
        freq = ood_frequency(target, behav, min_behaviour_prob=0.01)
        assert freq == 1.0


class TestFQEGammaGuard:
    def test_raises_for_positive_gamma_without_next_states(self, rng):
        from dropout_rl.rl.ope import fqe_value
        dataset = _toy_dataset(rng)
        def policy(s):
            return np.ones(len(s), dtype=np.int64)
        with pytest.raises(NotImplementedError, match="gamma"):
            fqe_value(target_policy=policy, dataset=dataset, gamma=0.95)
