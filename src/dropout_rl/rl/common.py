"""Shared infrastructure for offline RL algorithms.

Behaviour policy inference, MDP dataset construction, action space constants.
Used by CQL, IQL, and BCQ implementations.
"""

from __future__ import annotations

import json
from typing import Literal

import numpy as np
import pandas as pd

from dropout_rl.config import ACTIONS_PRIMARY, N_ACTIONS_PRIMARY


ON_TIME_THRESHOLD_DAYS = 42


def infer_behaviour_policy_3action(df: pd.DataFrame) -> np.ndarray:
    """Infer behaviour policy action from observed DHS features.

    Rules (in priority order):
    1. Next dose NOT received → a0 (no effective intervention)
    2. Next dose LATE (>42 days) → a0 (weak/no intervention)
    3. Next dose ON TIME + fieldworker visit (v393==1) → a2 (CHW)
    4. Next dose ON TIME + campaign vaccination (h69==41) → a2 (maps to CHW in 3-action)
    5. Next dose ON TIME + card present (h1a>=1) → a1 (SMS)
    6. Otherwise → a0

    Parameters
    ----------
    df : pd.DataFrame with columns:
        next_dose_interval, v393, h69, h1a, next_received

    Returns
    -------
    np.ndarray of shape (len(df),) with values in {0, 1, 2}.
    """
    required = {"next_dose_interval", "v393", "h69", "h1a", "next_received"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    n = len(df)
    actions = np.zeros(n, dtype=np.int64)

    interval = df["next_dose_interval"].to_numpy()
    v393 = df["v393"].to_numpy()
    h69 = df["h69"].to_numpy()
    h1a = df["h1a"].to_numpy()
    received = df["next_received"].to_numpy()

    on_time = (received == 1) & (interval <= ON_TIME_THRESHOLD_DAYS)

    actions[on_time & (h1a >= 1)] = 1  # SMS
    actions[on_time & (h69 == 41)] = 2  # campaign → a2
    actions[on_time & (v393 == 1)] = 2  # fieldworker → a2
    # late and not received default to 0

    return actions


def build_mdp_dataset(
    traj_df: pd.DataFrame,
    n_actions: Literal[3, 5] = 3,
) -> dict:
    """Build MDP dataset dict from trajectory dataframe.

    Parameters
    ----------
    traj_df : pd.DataFrame
        Must contain columns: state (JSON string), action, reward, weight.
    n_actions : int
        Target action space size. Actions ≥ n_actions are clipped to n_actions-1
        (i.e., a3/a4 → a2 when narrowing to 3 actions).

    Returns
    -------
    dict with keys: states, actions, rewards, weights, n_actions.
    """
    actions = traj_df["action"].to_numpy().astype(np.int64)
    actions = np.clip(actions, 0, n_actions - 1)

    # Parse state JSON
    states_list = []
    for s in traj_df["state"]:
        parsed = json.loads(s)
        states_list.append(list(parsed.values()))
    # Build uniform array — pad if necessary
    max_len = max(len(s) for s in states_list)
    states = np.zeros((len(states_list), max_len), dtype=np.float32)
    for i, s in enumerate(states_list):
        states[i, : len(s)] = s

    return {
        "states": states,
        "actions": actions,
        "rewards": traj_df["reward"].to_numpy().astype(np.float32),
        "weights": traj_df["weight"].to_numpy().astype(np.float32),
        "n_actions": n_actions,
    }
