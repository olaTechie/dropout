"""Microsimulation validation: internal calibration and subgroup checks."""

from __future__ import annotations

import numpy as np
import pandas as pd

from dropout_rl.config import CALIBRATION_TOLERANCE, SUBGROUP_CALIBRATION_FLAG


def calibration_check(
    predicted_rate: float,
    observed_rate: float,
    tolerance: float = CALIBRATION_TOLERANCE,
) -> dict:
    """Compare predicted vs observed S0 DTP3 rate.

    Parameters
    ----------
    predicted_rate : float
        DTP3 completion rate from S0 microsim.
    observed_rate : float
        Survey-weighted observed DTP3 completion rate.
    tolerance : float
        Pass threshold for absolute error.

    Returns
    -------
    dict with keys: passed, absolute_error, predicted, observed, tolerance.
    """
    abs_err = abs(predicted_rate - observed_rate)
    return {
        "passed": bool(abs_err <= tolerance),
        "absolute_error": float(abs_err),
        "predicted": float(predicted_rate),
        "observed": float(observed_rate),
        "tolerance": float(tolerance),
    }


def subgroup_calibration(
    predicted: pd.DataFrame,
    observed: pd.DataFrame,
    flag_threshold: float = SUBGROUP_CALIBRATION_FLAG,
    group_col: str = "group",
    rate_col: str = "rate",
) -> pd.DataFrame:
    """Per-stratum calibration check.

    Parameters
    ----------
    predicted, observed : pd.DataFrame
        Each has columns [group_col, rate_col].
    flag_threshold : float
        Subgroups with |predicted - observed| > flag_threshold are flagged.

    Returns
    -------
    pd.DataFrame with columns: group, predicted, observed, absolute_error, flagged.
    """
    merged = predicted.merge(observed, on=group_col, suffixes=("_pred", "_obs"))
    merged["absolute_error"] = (merged[f"{rate_col}_pred"] - merged[f"{rate_col}_obs"]).abs()
    merged["flagged"] = merged["absolute_error"] > flag_threshold
    return merged.rename(
        columns={
            f"{rate_col}_pred": "predicted",
            f"{rate_col}_obs": "observed",
        }
    )[[group_col, "predicted", "observed", "absolute_error", "flagged"]]
