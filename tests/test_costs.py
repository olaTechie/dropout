"""Tests for dropout_rl.costs."""

import numpy as np
import pytest

from dropout_rl.costs import gamma_params_from_cov, sample_cost, sample_cost_batch


class TestGammaParams:
    def test_parameters_recover_mean(self):
        shape, scale = gamma_params_from_cov(mean=500, cov=0.25)
        # Gamma: mean = shape * scale
        assert abs(shape * scale - 500) < 1e-6

    def test_parameters_recover_cov(self):
        shape, scale = gamma_params_from_cov(mean=500, cov=0.25)
        # Gamma: var = shape * scale^2; sd/mean = 1/sqrt(shape) = CoV
        import math
        assert abs(1.0 / math.sqrt(shape) - 0.25) < 1e-6


class TestSampleCost:
    def test_action_0_returns_zero(self, rng):
        for _ in range(50):
            assert sample_cost(0, rng) == 0.0

    def test_action_1_mean_near_50(self, rng):
        draws = np.array([sample_cost(1, rng) for _ in range(10000)])
        assert abs(draws.mean() - 50) < 2
        assert draws.min() >= 0

    def test_action_2_mean_near_500(self, rng):
        draws = np.array([sample_cost(2, rng) for _ in range(10000)])
        assert abs(draws.mean() - 500) < 20

    def test_invalid_action_raises(self, rng):
        with pytest.raises(ValueError):
            sample_cost(42, rng)


class TestSampleCostBatch:
    def test_shape(self, rng):
        costs = sample_cost_batch(n_actions=3, rng=rng)
        assert costs.shape == (3,)
        assert costs[0] == 0.0
