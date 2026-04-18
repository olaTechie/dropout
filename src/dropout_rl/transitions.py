"""Wraps Stage 1 XGBoost models with isotonic calibrators.

This module is the single source of truth for dropout-probability predictions
throughout Stages 2 and 3. It replaces the old practice of refitting
GradientBoostingClassifier models, which created inconsistency with the
published prediction analysis.
"""

from __future__ import annotations

from dataclasses import dataclass

import joblib
import numpy as np
import xgboost as xgb

from dropout_rl.config import STAGE1_DIR


@dataclass
class TransitionModel:
    """Calibrated transition model for a single dose step.

    Attributes
    ----------
    xgb_model : xgb.Booster
        Trained XGBoost booster predicting P(next dose received).
    calibrator : sklearn.isotonic.IsotonicRegression
        Isotonic regression calibrator fit on out-of-fold predictions.
    feature_names : list[str]
        Ordered feature names matching training.
    """

    xgb_model: xgb.Booster
    calibrator: object
    feature_names: list[str]

    def predict_dropout(self, X: np.ndarray) -> np.ndarray:
        """Predict calibrated P(dropout | state).

        Parameters
        ----------
        X : np.ndarray of shape (n, n_features)
            State feature matrix.

        Returns
        -------
        np.ndarray of shape (n,)
            Calibrated P(dropout) in [0, 1].
        """
        feature_names = self.xgb_model.feature_names
        dmat = xgb.DMatrix(
            np.asarray(X, dtype=np.float32),
            feature_names=feature_names,
        )
        raw_completion = self.xgb_model.predict(dmat)
        # XGBoost models predict P(dropout) directly (trained on dropout label)
        calibrated = self.calibrator.transform(raw_completion)
        return np.clip(calibrated, 0.0, 1.0)


def _load(xgb_name: str, calibrator_name: str) -> TransitionModel:
    xgb_path = STAGE1_DIR / xgb_name
    cal_path = STAGE1_DIR / calibrator_name
    if not xgb_path.exists():
        raise FileNotFoundError(f"XGBoost model not found: {xgb_path}")
    if not cal_path.exists():
        raise FileNotFoundError(f"Calibrator not found: {cal_path}")

    booster = xgb.Booster()
    booster.load_model(str(xgb_path))
    calibrator = joblib.load(cal_path)

    # The booster is the authoritative source for feature names.
    feature_names = list(booster.feature_names) if booster.feature_names else []

    return TransitionModel(
        xgb_model=booster,
        calibrator=calibrator,
        feature_names=feature_names,
    )


def load_t1() -> TransitionModel:
    """Load the DTP1→DTP2 transition model."""
    return _load("xgb_model_t1.json", "isotonic_calibrator_t1.pkl")


def load_t2() -> TransitionModel:
    """Load the DTP2→DTP3 transition model."""
    return _load("xgb_model_t2.json", "isotonic_calibrator_t2.pkl")
