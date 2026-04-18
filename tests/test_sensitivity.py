"""Tests for dropout_rl.sensitivity."""

import numpy as np
import pytest

from dropout_rl.microsim import ScenarioResult
from dropout_rl.sensitivity import ceac, probabilistic_icer


def _make_scenario(name, dtp3_mean, cost_mean, n=100, rng_seed=0):
    rng = np.random.default_rng(rng_seed)
    return ScenarioResult(
        name=name,
        is_status_quo=False,
        dtp3_rate=rng.normal(dtp3_mean, 0.01, n),
        cost_per_child=rng.normal(cost_mean, 10, n),
        total_cost=rng.normal(cost_mean * 10000, 1000, n),
        concentration_index=rng.normal(0, 0.01, n),
        wealth_gap=rng.normal(0.07, 0.01, n),
        slope_index=rng.normal(0.10, 0.01, n),
        rate_by_quintile=np.tile([0.80, 0.85, 0.86, 0.88, 0.90], (n, 1)),
        rate_by_zone=np.tile([0.85] * 6, (n, 1)),
    )


class TestCEAC:
    def test_output_shape(self):
        s0 = _make_scenario("S0", 0.859, 155)
        s1 = _make_scenario("S1", 0.871, 98)
        wtp = np.array([0, 1000, 10000, 100000])
        result = ceac([s0, s1], wtp_range=wtp, reference="S0")
        # Rows per WTP, columns per scenario
        assert result.shape[0] == len(wtp)

    def test_probabilities_sum_to_one(self):
        s0 = _make_scenario("S0", 0.859, 155)
        s1 = _make_scenario("S1", 0.871, 98)
        wtp = np.array([0, 10000])
        result = ceac([s0, s1], wtp_range=wtp, reference="S0")
        # Each row (WTP) should have probabilities summing to 1
        prob_cols = [c for c in result.columns if c != "wtp"]
        row_sums = result[prob_cols].sum(axis=1)
        assert np.allclose(row_sums, 1.0, atol=1e-6)


class TestProbabilisticICER:
    def test_basic(self):
        s0 = _make_scenario("S0", 0.85, 155, n=200, rng_seed=0)
        s1 = _make_scenario("S1", 0.88, 341, n=200, rng_seed=1)
        icer = probabilistic_icer(s1, s0)
        assert "mean_icer" in icer
        assert "ci_low" in icer
        assert "ci_high" in icer
        # S1 costs more, achieves more, so ICER positive and finite
        assert icer["mean_icer"] > 0
