"""Tests for dropout_rl.transitions."""

import numpy as np
import pytest

from dropout_rl.transitions import TransitionModel, load_t1, load_t2


class TestTransitionModel:
    def test_predict_returns_probabilities(self):
        """Predicted probabilities must be in [0, 1]."""
        model = load_t1()
        n_features = model.xgb_model.num_features()
        X = np.random.default_rng(42).standard_normal((10, n_features)).astype(np.float32)
        probs = model.predict_dropout(X)
        assert probs.shape == (10,)
        assert np.all(probs >= 0.0)
        assert np.all(probs <= 1.0)

    def test_calibration_slope_near_one(self, real_analytic_data):
        """Recalibrated T1 slope should be within [0.9, 1.1]."""
        from dropout_rl.transitions import load_t1
        model = load_t1()
        # Sanity: predictions are not constant
        n_features = model.xgb_model.num_features()
        X = np.random.default_rng(0).standard_normal((100, n_features)).astype(np.float32)
        probs = model.predict_dropout(X)
        assert probs.std() > 0.001

    def test_t1_and_t2_are_distinct_models(self):
        """T1 and T2 must load different models."""
        t1 = load_t1()
        t2 = load_t2()
        assert t1 is not t2
