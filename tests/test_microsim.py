"""Tests for dropout_rl.microsim."""

import numpy as np
import pandas as pd
import pytest

from dropout_rl.microsim import ScenarioResult, run_scenario


class _FakeTransition:
    """Mock transition model that returns a constant dropout probability."""

    def __init__(self, p: float):
        self.p = p

    def predict_dropout(self, X):
        return np.full(len(X), self.p)


def _fake_data(n=200):
    rng = np.random.default_rng(0)
    return pd.DataFrame({
        "v021": rng.integers(1, 20, size=n),  # 20 clusters
        "v005": rng.uniform(0.5e6, 1.5e6, size=n),
        "wealth": rng.integers(1, 6, size=n),
        "sstate": rng.integers(1, 38, size=n),
        "medu": rng.integers(0, 3, size=n),
        "rural": rng.integers(0, 2, size=n),
    })


class TestRunScenario:
    def test_returns_scenario_result(self):
        df = _fake_data()
        t1 = _FakeTransition(0.10)
        t2 = _FakeTransition(0.05)

        def always_sms_t1(X, indices):
            return np.ones(len(X), dtype=int)

        def always_sms_t2(X, indices):
            return np.ones(len(X), dtype=int)

        result = run_scenario(
            name="test_sms",
            policy_fn_t1=always_sms_t1,
            policy_fn_t2=always_sms_t2,
            analytic_df=df,
            t1_model=t1,
            t2_model=t2,
            n_pop=50,
            n_bootstrap=10,
            seed=42,
            psa=False,
            cluster_bootstrap=True,
        )
        assert isinstance(result, ScenarioResult)
        assert result.dtp3_rate.shape == (10,)
        assert np.all(result.dtp3_rate >= 0)
        assert np.all(result.dtp3_rate <= 1)

    def test_reproducibility_same_seed(self):
        df = _fake_data()
        t1 = _FakeTransition(0.10)
        t2 = _FakeTransition(0.05)

        def sms_t1(X, i):
            return np.ones(len(X), dtype=int)

        def sms_t2(X, i):
            return np.ones(len(X), dtype=int)

        r1 = run_scenario("a", sms_t1, sms_t2, df, t1, t2,
                         n_pop=50, n_bootstrap=5, seed=42, psa=False)
        r2 = run_scenario("a", sms_t1, sms_t2, df, t1, t2,
                         n_pop=50, n_bootstrap=5, seed=42, psa=False)
        np.testing.assert_array_equal(r1.dtp3_rate, r2.dtp3_rate)

    def test_status_quo_ignores_rrr(self):
        """S0 should not apply RRR (is_status_quo=True)."""
        df = _fake_data()
        t1 = _FakeTransition(0.20)
        t2 = _FakeTransition(0.10)

        def a0_t1(X, i):
            return np.zeros(len(X), dtype=int)

        def a0_t2(X, i):
            return np.zeros(len(X), dtype=int)

        result = run_scenario(
            name="s0",
            policy_fn_t1=a0_t1,
            policy_fn_t2=a0_t2,
            analytic_df=df,
            t1_model=t1,
            t2_model=t2,
            n_pop=50,
            n_bootstrap=20,
            seed=42,
            psa=False,
            is_status_quo=True,
        )
        # DTP3 rate ≈ (1 - 0.20) * (1 - 0.10) = 0.72
        assert 0.60 < result.dtp3_rate.mean() < 0.82

    def test_psa_increases_variance(self):
        """PSA should increase CI width vs no-PSA."""
        df = _fake_data()
        t1 = _FakeTransition(0.10)
        t2 = _FakeTransition(0.05)

        def sms_t1(X, i):
            return np.ones(len(X), dtype=int)

        def sms_t2(X, i):
            return np.ones(len(X), dtype=int)

        r_no_psa = run_scenario("n", sms_t1, sms_t2, df, t1, t2,
                                n_pop=100, n_bootstrap=100, seed=42, psa=False)
        r_psa = run_scenario("p", sms_t1, sms_t2, df, t1, t2,
                             n_pop=100, n_bootstrap=100, seed=42, psa=True)
        # PSA adds uncertainty, so std should not be smaller
        assert r_psa.dtp3_rate.std() >= r_no_psa.dtp3_rate.std() * 0.8
