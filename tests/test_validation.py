"""Tests for dropout_rl.validation."""

import numpy as np
import pandas as pd
import pytest

from dropout_rl.validation import (
    calibration_check,
    subgroup_calibration,
)


class TestCalibrationCheck:
    def test_passes_when_close(self):
        result = calibration_check(
            predicted_rate=0.855,
            observed_rate=0.852,
            tolerance=0.01,
        )
        assert result["passed"] is True
        assert abs(result["absolute_error"] - 0.003) < 1e-9

    def test_fails_when_far(self):
        result = calibration_check(
            predicted_rate=0.90,
            observed_rate=0.80,
            tolerance=0.01,
        )
        assert result["passed"] is False
        assert result["absolute_error"] > 0.05


class TestSubgroupCalibration:
    def test_identifies_miscalibrated_subgroup(self):
        predicted = pd.DataFrame({
            "group": ["A", "B", "C"],
            "rate": [0.80, 0.85, 0.90],
        })
        observed = pd.DataFrame({
            "group": ["A", "B", "C"],
            "rate": [0.81, 0.82, 0.89],  # B is off by 0.03
        })
        result = subgroup_calibration(predicted, observed, flag_threshold=0.025)
        flagged = result[result["flagged"]]
        assert "B" in flagged["group"].values
        assert "A" not in flagged["group"].values
