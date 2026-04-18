"""Tests for dropout_rl.interventions."""

import numpy as np
import pytest

from dropout_rl.interventions import (
    apply_rrr,
    beta_params_from_range,
    sample_rrr,
    sample_rrr_batch,
)


class TestBetaParams:
    def test_central_in_range(self):
        """Central estimate is the mean."""
        a, b = beta_params_from_range(central=0.10, low=0.05, high=0.15)
        mean = a / (a + b)
        assert abs(mean - 0.10) < 0.005

    def test_95_interval_approx(self):
        """95% interval approximately matches [low, high]."""
        from scipy import stats
        a, b = beta_params_from_range(central=0.10, low=0.05, high=0.15)
        q_low = stats.beta.ppf(0.025, a, b)
        q_high = stats.beta.ppf(0.975, a, b)
        # Approximate match — Beta may not perfectly reproduce asymmetric ranges
        assert 0.02 < q_low < 0.08
        assert 0.12 < q_high < 0.18


class TestSampleRRR:
    def test_action_0_returns_zero(self, rng):
        for _ in range(100):
            assert sample_rrr(0, rng) == 0.0

    def test_action_1_has_correct_mean(self, rng):
        draws = np.array([sample_rrr(1, rng) for _ in range(5000)])
        assert abs(draws.mean() - 0.10) < 0.01
        assert draws.min() >= 0.0
        assert draws.max() <= 1.0

    def test_action_2_has_correct_mean(self, rng):
        draws = np.array([sample_rrr(2, rng) for _ in range(5000)])
        assert abs(draws.mean() - 0.20) < 0.015

    def test_invalid_action_raises(self, rng):
        with pytest.raises(ValueError):
            sample_rrr(99, rng)


class TestApplyRRR:
    def test_zero_action_leaves_input_unchanged(self):
        p = np.array([0.1, 0.2, 0.3])
        actions = np.array([0, 0, 0])
        rrr_draws = np.array([0.0, 0.10, 0.20])
        result = apply_rrr(p, actions, rrr_draws)
        np.testing.assert_array_almost_equal(result, p)

    def test_nonzero_action_reduces_dropout(self):
        p = np.array([0.10])
        actions = np.array([1])
        rrr_draws = np.array([0.0, 0.10, 0.20, 0.25, 0.14])
        result = apply_rrr(p, actions, rrr_draws)
        # p * (1 - 0.10) = 0.09
        assert abs(result[0] - 0.09) < 1e-9

    def test_result_clipped_to_unit_interval(self):
        p = np.array([0.5, 1.5])  # 1.5 is invalid but test clipping
        actions = np.array([1, 1])
        rrr_draws = np.array([0.0, 0.1, 0.2])
        result = apply_rrr(p, actions, rrr_draws)
        assert np.all(result >= 0.0)
        assert np.all(result <= 1.0)


class TestSampleRRRBatch:
    def test_shape(self, rng):
        draws = sample_rrr_batch(n_actions=3, rng=rng)
        assert draws.shape == (3,)
        assert draws[0] == 0.0
