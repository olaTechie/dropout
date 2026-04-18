"""End-to-end smoke test: Stage 2 + Stage 3 on small subsample."""

import numpy as np
import pandas as pd
import pytest

from dropout_rl.microsim import run_scenario
from dropout_rl.rl.common import build_mdp_dataset
from dropout_rl.rl.cql import CQL


@pytest.mark.requires_data
def test_stage2_minimum_steps(real_analytic_data, rng):
    """Stage 2: CQL trains on 100 trajectory rows with feature alignment."""
    from dropout_rl.config import PROCESSED_DIR
    from dropout_rl.transitions import load_t1
    traj = pd.read_csv(PROCESSED_DIR / "trajectory_dataset.csv").head(100)
    t1 = load_t1()
    dataset = build_mdp_dataset(traj, n_actions=3, feature_names=t1.feature_names)
    cql = CQL(n_actions=3, alpha=1.0, n_iterations=5)
    cql.fit(dataset, rng=rng)
    actions = cql.predict_action(dataset["states"])
    assert actions.shape == (100,)


@pytest.mark.requires_data
def test_stage3_minimum_run(real_analytic_data):
    """Stage 3: one scenario on 100-child x 10-bootstrap subsample."""
    from dropout_rl.transitions import load_t1, load_t2
    t1 = load_t1()
    t2 = load_t2()

    def sms(X, idx):
        return np.ones(len(X), dtype=np.int64)

    result = run_scenario(
        name="smoke",
        policy_fn_t1=sms,
        policy_fn_t2=sms,
        analytic_df=real_analytic_data.head(100),
        t1_model=t1,
        t2_model=t2,
        n_pop=50,
        n_bootstrap=10,
        cluster_bootstrap=True,
        psa=True,
        seed=42,
        is_status_quo=False,
        feature_cols=t1.feature_names,
    )
    assert result.dtp3_rate.shape == (10,)
    assert (result.dtp3_rate >= 0).all()
    assert (result.dtp3_rate <= 1).all()
