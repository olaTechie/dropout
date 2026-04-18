"""Shared test fixtures."""

import numpy as np
import pandas as pd
import pytest

from dropout_rl.config import PROCESSED_DIR, STAGE1_DIR


@pytest.fixture
def rng():
    """Deterministic random generator."""
    return np.random.default_rng(42)


@pytest.fixture
def synthetic_trajectory():
    """Small synthetic trajectory dataset for unit tests."""
    rng = np.random.default_rng(42)
    n = 200
    return pd.DataFrame({
        "child_id": [f"C{i//2:03d}_{i%2}" for i in range(n)],
        "dose_step": [i % 2 for i in range(n)],
        "action": rng.integers(0, 3, size=n),
        "reward": rng.choice([0.0, 0.3, 1.0], size=n),
        "weight": rng.uniform(0.5, 1.5, size=n),
        "state": ['{"wealth": 3, "rural": 0, "doses_received": 1}'] * n,
    })


@pytest.fixture
def real_analytic_data():
    """Real analytic data — skipped if not present."""
    path = PROCESSED_DIR / "analytic_dtp1_received.parquet"
    if not path.exists():
        pytest.skip("DHS data not available")
    return pd.read_parquet(path)
