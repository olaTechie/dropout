"""Tests for dropout_rl.rl.common."""

import numpy as np
import pandas as pd
import pytest

from dropout_rl.rl.common import (
    build_mdp_dataset,
    infer_behaviour_policy_3action,
)


class TestBehaviourPolicyInference:
    def test_output_only_3_actions(self, synthetic_trajectory):
        # Construct realistic row features
        df = pd.DataFrame([
            {"next_dose_interval": 30, "v393": 1, "h69": 10, "h1a": 2, "next_received": 1},
            {"next_dose_interval": 30, "v393": 0, "h69": 41, "h1a": 1, "next_received": 1},
            {"next_dose_interval": 30, "v393": 0, "h69": 10, "h1a": 2, "next_received": 1},
            {"next_dose_interval": 60, "v393": 0, "h69": 10, "h1a": 0, "next_received": 1},
            {"next_dose_interval": 30, "v393": 0, "h69": 10, "h1a": 0, "next_received": 0},
        ])
        actions = infer_behaviour_policy_3action(df)
        assert set(actions) <= {0, 1, 2}

    def test_fieldworker_yields_a2(self):
        df = pd.DataFrame([
            {"next_dose_interval": 30, "v393": 1, "h69": 10, "h1a": 2, "next_received": 1},
        ])
        actions = infer_behaviour_policy_3action(df)
        assert actions[0] == 2

    def test_campaign_yields_a2(self):
        """Campaign vaccination maps to a2 in 3-action space (was a3 in 5-action)."""
        df = pd.DataFrame([
            {"next_dose_interval": 30, "v393": 0, "h69": 41, "h1a": 1, "next_received": 1},
        ])
        actions = infer_behaviour_policy_3action(df)
        assert actions[0] == 2

    def test_on_time_with_card_yields_a1(self):
        df = pd.DataFrame([
            {"next_dose_interval": 30, "v393": 0, "h69": 10, "h1a": 2, "next_received": 1},
        ])
        actions = infer_behaviour_policy_3action(df)
        assert actions[0] == 1

    def test_late_yields_a0(self):
        df = pd.DataFrame([
            {"next_dose_interval": 60, "v393": 0, "h69": 10, "h1a": 2, "next_received": 1},
        ])
        actions = infer_behaviour_policy_3action(df)
        assert actions[0] == 0

    def test_not_received_yields_a0(self):
        df = pd.DataFrame([
            {"next_dose_interval": 30, "v393": 1, "h69": 41, "h1a": 2, "next_received": 0},
        ])
        actions = infer_behaviour_policy_3action(df)
        assert actions[0] == 0


class TestBuildMDPDataset:
    def test_output_shapes(self, synthetic_trajectory):
        dataset = build_mdp_dataset(synthetic_trajectory, n_actions=3)
        assert "states" in dataset
        assert "actions" in dataset
        assert "rewards" in dataset
        assert "weights" in dataset
        n = len(synthetic_trajectory)
        assert dataset["actions"].shape == (n,)
        assert dataset["rewards"].shape == (n,)

    def test_actions_clipped_to_3_actions(self, synthetic_trajectory):
        # Inject an out-of-range action
        df = synthetic_trajectory.copy()
        df.loc[0, "action"] = 4  # a4 not in 3-action space
        dataset = build_mdp_dataset(df, n_actions=3)
        assert dataset["actions"].max() < 3

    def test_missing_columns_raises(self):
        import pandas as pd
        bad_df = pd.DataFrame({"action": [0, 1], "reward": [0.0, 0.3]})
        with pytest.raises(ValueError, match="Missing columns"):
            build_mdp_dataset(bad_df, n_actions=3)
