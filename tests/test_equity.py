"""Tests for dropout_rl.equity."""

import numpy as np
import pytest

from dropout_rl.equity import (
    concentration_index,
    slope_index_of_inequality,
    wealth_gap,
)


class TestWealthGap:
    def test_no_gap_when_uniform(self):
        y = np.ones(100)
        w = np.tile(np.arange(1, 6), 20)
        assert abs(wealth_gap(y, w)) < 1e-9

    def test_positive_gap_when_richest_higher(self):
        # Poorest all 0, richest all 1
        y = np.concatenate([np.zeros(20), np.ones(20)])
        w = np.concatenate([np.ones(20), np.full(20, 5)])
        gap = wealth_gap(y, w)
        assert gap == 1.0  # richest - poorest = 1 - 0


class TestConcentrationIndex:
    def test_zero_when_independent(self, rng):
        """CI ~ 0 when outcome independent of wealth."""
        n = 5000
        y = rng.binomial(1, 0.5, size=n).astype(float)
        w = rng.integers(1, 6, size=n).astype(float)
        ci = concentration_index(y, w)
        assert abs(ci) < 0.05

    def test_positive_when_concentrated_in_rich(self):
        """CI > 0 when outcome concentrated in higher wealth."""
        n = 1000
        w = np.tile(np.arange(1, 6), n // 5)
        # Outcome probability scales with wealth: 0.1 * w
        rng = np.random.default_rng(0)
        y = rng.binomial(1, 0.1 * w).astype(float)
        ci = concentration_index(y, w)
        assert ci > 0.1

    def test_negative_when_concentrated_in_poor(self):
        """CI < 0 when outcome concentrated in lower wealth."""
        n = 1000
        w = np.tile(np.arange(1, 6), n // 5)
        rng = np.random.default_rng(0)
        y = rng.binomial(1, 0.6 - 0.1 * w).astype(float)
        ci = concentration_index(y, w)
        assert ci < -0.1


class TestSlopeIndex:
    def test_zero_when_flat(self):
        y = np.full(100, 0.8)
        w = np.tile(np.arange(1, 6), 20)
        sii = slope_index_of_inequality(y, w)
        assert abs(sii) < 1e-6

    def test_matches_gap_sign(self, rng):
        """SII sign matches wealth gap sign on strong signal."""
        n = 500
        w = np.tile(np.arange(1, 6), n // 5)
        y = (w == 5).astype(float)  # Only richest completes
        sii = slope_index_of_inequality(y, w)
        assert sii > 0
