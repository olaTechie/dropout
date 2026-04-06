#!/usr/bin/env python3
"""
Stage 2: Offline Reinforcement Learning — FQI + CQL + OPE + Policy Extraction
Nigeria Vaccine Dropout RL Study
"""

import json
import warnings
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.ensemble import ExtraTreesRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

warnings.filterwarnings('ignore')
np.random.seed(42)

# ── Paths ──
BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data" / "processed"
OUT = BASE / "outputs" / "stage2"
OUT.mkdir(parents=True, exist_ok=True)

# ── Load Data ──
print("=" * 60)
print("STAGE 2: OFFLINE REINFORCEMENT LEARNING")
print("=" * 60)

traj_df = pd.read_csv(DATA / "trajectory_dataset.csv")
with open(DATA / "state_space_definition.json") as f:
    state_spec = json.load(f)

with open(BASE / "outputs" / "literature" / "action_space_calibration.json") as f:
    action_cal = json.load(f)

FEATURE_NAMES = state_spec["static_features"] + state_spec["dynamic_features"] + state_spec.get("temporal_features", [])
N_FEATURES = len(FEATURE_NAMES)
N_ACTIONS = 5
GAMMA = 0.95
ACTION_COSTS = {int(k): v for k, v in state_spec["action_space"]["costs"].items()}
COST_LAMBDA = state_spec["reward"]["cost_lambda"]

print(f"Trajectory rows: {len(traj_df)}")
print(f"State dim: {N_FEATURES}")
print(f"Actions: {N_ACTIONS}")

# ── Parse State Vectors ──
def parse_states(col):
    """Parse JSON state strings to numpy array, handling nulls."""
    records = col.apply(json.loads).tolist()
    df = pd.DataFrame(records, columns=FEATURE_NAMES)
    # Fill nulls with median (conservative)
    for c in df.columns:
        if df[c].isnull().any():
            df[c] = df[c].fillna(df[c].median())
    return df.values.astype(np.float32)

print("\nParsing state vectors...")
states = parse_states(traj_df["state"])
next_states = parse_states(traj_df["next_state"])
actions = traj_df["action"].values.astype(np.int32)
rewards = traj_df["reward"].values.astype(np.float32)
dones = traj_df["done"].values.astype(np.int32)
weights = traj_df["weight"].values.astype(np.float32)
child_ids = traj_df["child_id"].values

print(f"States shape: {states.shape}")
print(f"Action distribution: {np.bincount(actions, minlength=N_ACTIONS)}")
print(f"Reward distribution: unique={np.unique(rewards)}")

# ── Train/Validation Split (by child_id, 50/50 per lit review) ──
unique_children = np.unique(child_ids)
np.random.shuffle(unique_children)
split_idx = len(unique_children) // 2
train_children = set(unique_children[:split_idx])
val_children = set(unique_children[split_idx:])

train_mask = np.array([cid in train_children for cid in child_ids])
val_mask = ~train_mask

print(f"\nTrain episodes: {sum(train_mask)} rows ({len(train_children)} children)")
print(f"Val episodes: {sum(val_mask)} rows ({len(val_children)} children)")

s_train, a_train, r_train, ns_train, d_train, w_train = (
    states[train_mask], actions[train_mask], rewards[train_mask],
    next_states[train_mask], dones[train_mask], weights[train_mask]
)
s_val, a_val, r_val, ns_val, d_val, w_val = (
    states[val_mask], actions[val_mask], rewards[val_mask],
    next_states[val_mask], dones[val_mask], weights[val_mask]
)

# ══════════════════════════════════════════════════════════════
# PHASE 1.1: FITTED Q-ITERATION (FQI)
# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("PHASE 1.1: FITTED Q-ITERATION")
print("=" * 60)

class FittedQIteration:
    """Tree-based FQI with per-action regressors."""

    def __init__(self, n_actions, gamma, n_features, n_iterations=50,
                 convergence_threshold=0.001):
        self.n_actions = n_actions
        self.gamma = gamma
        self.n_features = n_features
        self.n_iterations = n_iterations
        self.convergence_threshold = convergence_threshold
        self.q_models = None
        self.history = []

    def fit(self, states, actions, rewards, next_states, dones, sample_weight=None):
        n = len(states)
        # Initialize Q-targets as immediate rewards
        q_targets = rewards.copy()

        for iteration in range(self.n_iterations):
            # Fit per-action regressors
            new_models = []
            for a in range(self.n_actions):
                mask = actions == a
                if mask.sum() < 5:
                    # Too few samples for this action — use global model
                    model = ExtraTreesRegressor(
                        n_estimators=100, max_depth=10,
                        min_samples_leaf=5, n_jobs=-1, random_state=42
                    )
                    model.fit(states, q_targets, sample_weight=sample_weight)
                else:
                    model = ExtraTreesRegressor(
                        n_estimators=100, max_depth=10,
                        min_samples_leaf=5, n_jobs=-1, random_state=42
                    )
                    w = sample_weight[mask] if sample_weight is not None else None
                    model.fit(states[mask], q_targets[mask], sample_weight=w)
                new_models.append(model)

            self.q_models = new_models

            # Compute new targets: r + gamma * max_a' Q(s', a') * (1 - done)
            q_next = self.predict_all(next_states)  # (n, n_actions)
            max_q_next = np.max(q_next, axis=1)
            new_targets = rewards + self.gamma * max_q_next * (1 - dones)

            # Check convergence
            delta = np.mean(np.abs(new_targets - q_targets))
            self.history.append(delta)
            q_targets = new_targets

            if iteration % 10 == 0 or delta < self.convergence_threshold:
                print(f"  Iteration {iteration+1}: ΔQ = {delta:.6f}")

            if delta < self.convergence_threshold:
                print(f"  ✓ Converged at iteration {iteration+1}")
                break

        return self

    def predict_all(self, states):
        """Predict Q(s, a) for all actions."""
        q_vals = np.zeros((len(states), self.n_actions))
        for a in range(self.n_actions):
            q_vals[:, a] = self.q_models[a].predict(states)
        return q_vals

    def predict_action(self, states):
        """Return optimal action for each state."""
        q_vals = self.predict_all(states)
        return np.argmax(q_vals, axis=1)


# Train FQI
fqi = FittedQIteration(
    n_actions=N_ACTIONS, gamma=GAMMA, n_features=N_FEATURES,
    n_iterations=50, convergence_threshold=0.001
)
fqi.fit(s_train, a_train, r_train, ns_train, d_train, sample_weight=w_train)

# Plot convergence
fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(range(1, len(fqi.history)+1), fqi.history, 'b-o', markersize=3)
ax.axhline(y=0.001, color='r', linestyle='--', label='Convergence threshold (0.001)')
ax.set_xlabel('Iteration')
ax.set_ylabel('Mean |ΔQ|')
ax.set_title('Fitted Q-Iteration Convergence')
ax.legend()
ax.set_yscale('log')
plt.tight_layout()
fig.savefig(OUT / "fqi_convergence.pdf", dpi=300)
fig.savefig(OUT / "fqi_convergence.png", dpi=300)
plt.close()

# FQI Q-values on validation
fqi_q_val = fqi.predict_all(s_val)
fqi_policy_val = np.argmax(fqi_q_val, axis=1)
print(f"\nFQI policy action distribution (val):")
for a in range(N_ACTIONS):
    pct = (fqi_policy_val == a).sum() / len(fqi_policy_val) * 100
    print(f"  a{a}: {(fqi_policy_val == a).sum()} ({pct:.1f}%)")

# ══════════════════════════════════════════════════════════════
# PHASE 1.2: CONSERVATIVE Q-LEARNING (CQL)
# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("PHASE 1.2: CONSERVATIVE Q-LEARNING")
print("=" * 60)

class ConservativeQL:
    """
    CQL implemented on top of FQI.
    Adds a conservative penalty that pushes down Q-values for
    out-of-distribution actions.

    CQL loss = FQI loss + α * [E_a~uniform[Q(s,a)] - E_a~data[Q(s,a)]]
    """

    def __init__(self, n_actions, gamma, n_features, alpha=1.0,
                 n_iterations=80, convergence_threshold=0.001):
        self.n_actions = n_actions
        self.gamma = gamma
        self.n_features = n_features
        self.alpha = alpha
        self.n_iterations = n_iterations
        self.convergence_threshold = convergence_threshold
        self.q_models = None
        self.history = []
        self.cql_penalty_history = []

    def fit(self, states, actions, rewards, next_states, dones, sample_weight=None):
        n = len(states)
        q_targets = rewards.copy()

        for iteration in range(self.n_iterations):
            # Step 1: Standard FQI fitting
            new_models = []
            for a in range(self.n_actions):
                mask = actions == a
                model = GradientBoostingRegressor(
                    n_estimators=100, max_depth=6,
                    learning_rate=0.1, min_samples_leaf=10,
                    subsample=0.8, random_state=42
                )
                if mask.sum() < 5:
                    model.fit(states, q_targets, sample_weight=sample_weight)
                else:
                    w = sample_weight[mask] if sample_weight is not None else None
                    model.fit(states[mask], q_targets[mask], sample_weight=w)
                new_models.append(model)

            self.q_models = new_models

            # Step 2: Compute Q-values for all state-action pairs
            q_all = self.predict_all(states)  # (n, n_actions)

            # Step 3: CQL conservative penalty
            # E_uniform[Q(s,a)] - mean over all actions
            q_uniform_mean = np.mean(q_all, axis=1)  # logsumexp approximation
            # E_data[Q(s,a)] - Q for the actions actually taken
            q_data = q_all[np.arange(n), actions]
            # CQL penalty: push down OOD Q-values
            cql_penalty = np.mean(q_uniform_mean - q_data)
            self.cql_penalty_history.append(cql_penalty)

            # Step 4: Adjusted targets with CQL regularization
            q_next = self.predict_all(next_states)
            max_q_next = np.max(q_next, axis=1)
            # Apply penalty to targets: lower Q for unseen actions
            new_targets = rewards + self.gamma * max_q_next * (1 - dones)
            # Subtract alpha * penalty from the target for conservative estimation
            conservative_adjustment = self.alpha * cql_penalty
            new_targets = new_targets - conservative_adjustment

            delta = np.mean(np.abs(new_targets - q_targets))
            self.history.append(delta)
            q_targets = new_targets

            if iteration % 10 == 0 or delta < self.convergence_threshold:
                print(f"  Iter {iteration+1}: ΔQ={delta:.6f}, CQL penalty={cql_penalty:.4f}")

            if delta < self.convergence_threshold and iteration > 10:
                print(f"  ✓ Converged at iteration {iteration+1}")
                break

        return self

    def predict_all(self, states):
        q_vals = np.zeros((len(states), self.n_actions))
        for a in range(self.n_actions):
            q_vals[:, a] = self.q_models[a].predict(states)
        return q_vals

    def predict_action(self, states):
        q_vals = self.predict_all(states)
        return np.argmax(q_vals, axis=1)


# CQL α sensitivity analysis
cql_alpha_results = {}
for alpha in [0.1, 0.5, 1.0, 2.0, 5.0]:
    print(f"\n--- CQL α = {alpha} ---")
    cql = ConservativeQL(
        n_actions=N_ACTIONS, gamma=GAMMA, n_features=N_FEATURES,
        alpha=alpha, n_iterations=80
    )
    cql.fit(s_train, a_train, r_train, ns_train, d_train, sample_weight=w_train)

    q_val = cql.predict_all(s_val)
    policy = np.argmax(q_val, axis=1)
    action_dist = np.bincount(policy, minlength=N_ACTIONS) / len(policy) * 100

    # OOD frequency: actions 3 and 4 (rarely/never observed in data)
    ood_freq = action_dist[3] + action_dist[4]

    cql_alpha_results[alpha] = {
        'model': cql,
        'q_values': q_val,
        'policy': policy,
        'action_dist': action_dist,
        'ood_freq': ood_freq,
        'mean_q': np.mean(q_val),
        'final_penalty': cql.cql_penalty_history[-1] if cql.cql_penalty_history else 0,
    }
    print(f"  Action dist: {action_dist.round(1)}")
    print(f"  OOD freq (a3+a4): {ood_freq:.1f}%")
    print(f"  Mean Q: {np.mean(q_val):.4f}")

# Select primary CQL model (α=1.0 as default)
PRIMARY_ALPHA = 1.0
cql_primary = cql_alpha_results[PRIMARY_ALPHA]['model']
cql_q_val = cql_alpha_results[PRIMARY_ALPHA]['q_values']
cql_policy_val = cql_alpha_results[PRIMARY_ALPHA]['policy']

print(f"\n=== PRIMARY CQL (α={PRIMARY_ALPHA}) ===")
print(f"Policy action distribution (val):")
for a in range(N_ACTIONS):
    pct = (cql_policy_val == a).sum() / len(cql_policy_val) * 100
    print(f"  a{a}: {(cql_policy_val == a).sum()} ({pct:.1f}%)")

# Save CQL convergence + alpha sensitivity plots
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# Convergence
ax = axes[0]
ax.plot(range(1, len(cql_primary.history)+1), cql_primary.history, 'b-o', markersize=2)
ax.axhline(y=0.001, color='r', linestyle='--', alpha=0.5)
ax.set_xlabel('Iteration')
ax.set_ylabel('Mean |ΔQ|')
ax.set_title(f'CQL Convergence (α={PRIMARY_ALPHA})')
ax.set_yscale('log')

# CQL penalty over iterations
ax = axes[1]
ax.plot(range(1, len(cql_primary.cql_penalty_history)+1),
        cql_primary.cql_penalty_history, 'g-o', markersize=2)
ax.set_xlabel('Iteration')
ax.set_ylabel('CQL Penalty')
ax.set_title('CQL Conservative Penalty')

# Alpha sensitivity
ax = axes[2]
alphas = sorted(cql_alpha_results.keys())
ood_freqs = [cql_alpha_results[a]['ood_freq'] for a in alphas]
mean_qs = [cql_alpha_results[a]['mean_q'] for a in alphas]
ax.plot(alphas, ood_freqs, 'ro-', label='OOD freq (a3+a4) %')
ax2 = ax.twinx()
ax2.plot(alphas, mean_qs, 'bs-', label='Mean Q-value')
ax.set_xlabel('CQL α')
ax.set_ylabel('OOD Action Frequency (%)', color='r')
ax2.set_ylabel('Mean Q-value', color='b')
ax.set_title('CQL α Sensitivity')
ax.legend(loc='upper left')
ax2.legend(loc='upper right')

plt.tight_layout()
fig.savefig(OUT / "cql_analysis.pdf", dpi=300)
fig.savefig(OUT / "cql_analysis.png", dpi=300)
plt.close()

# ══════════════════════════════════════════════════════════════
# PHASE 1.3: OFF-POLICY EVALUATION
# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("PHASE 1.3: OFF-POLICY EVALUATION")
print("=" * 60)

# --- Behaviour policy estimation ---
# Estimate behaviour policy π_b(a|s) using a probabilistic model
from sklearn.ensemble import RandomForestClassifier

print("Fitting behaviour policy model...")
behav_model = RandomForestClassifier(
    n_estimators=200, max_depth=10, min_samples_leaf=5,
    n_jobs=-1, random_state=42
)
behav_model.fit(s_train, a_train, sample_weight=w_train)
pi_b_probs_val = behav_model.predict_proba(s_val)  # (n_val, n_classes)
# Align columns with action indices
behav_classes = behav_model.classes_
pi_b_full = np.zeros((len(s_val), N_ACTIONS))
for i, cls in enumerate(behav_classes):
    pi_b_full[:, cls] = pi_b_probs_val[:, i]
# Add epsilon smoothing (policy softening per lit review)
EPSILON = 0.1
pi_b_full = (1 - EPSILON) * pi_b_full + EPSILON / N_ACTIONS
# Normalize
pi_b_full = pi_b_full / pi_b_full.sum(axis=1, keepdims=True)

print(f"Behaviour policy accuracy: {behav_model.score(s_val, a_val):.3f}")

# --- Evaluation policy (CQL) as deterministic ---
def eval_policy_probs(q_values, temperature=0.01):
    """Softmax policy from Q-values (near-deterministic)."""
    q_shifted = q_values - q_values.max(axis=1, keepdims=True)
    exp_q = np.exp(q_shifted / temperature)
    return exp_q / exp_q.sum(axis=1, keepdims=True)

pi_e_probs = eval_policy_probs(cql_q_val)

# Group validation data by child episodes
val_child_ids = child_ids[val_mask]
val_episodes = {}
for i in range(len(s_val)):
    cid = val_child_ids[i]
    if cid not in val_episodes:
        val_episodes[cid] = []
    val_episodes[cid].append(i)

print(f"Validation episodes: {len(val_episodes)}")

# --- 1. Weighted Importance Sampling (WIS) ---
print("\n--- Weighted Importance Sampling (WIS) ---")

episode_returns = []
episode_weights_is = []

for cid, indices in val_episodes.items():
    G = 0.0
    rho = 1.0  # importance ratio
    for t, idx in enumerate(indices):
        a = a_val[idx]
        r = r_val[idx]
        G += (GAMMA ** t) * r
        # π_e(a|s) / π_b(a|s)
        pi_e_a = pi_e_probs[idx, a]
        pi_b_a = pi_b_full[idx, a]
        rho *= pi_e_a / max(pi_b_a, 1e-8)

    episode_returns.append(G)
    episode_weights_is.append(rho)

episode_returns = np.array(episode_returns)
episode_weights_is = np.array(episode_weights_is)

# Clip extreme weights
clip_threshold = np.percentile(episode_weights_is, 99)
episode_weights_is_clipped = np.clip(episode_weights_is, 0, clip_threshold)

# WIS estimator
wis_numerator = np.sum(episode_weights_is_clipped * episode_returns)
wis_denominator = np.sum(episode_weights_is_clipped)
V_wis = wis_numerator / max(wis_denominator, 1e-8)

# Behaviour policy value (just average returns)
V_behav = np.mean(episode_returns)

# Standard IS
V_is = np.mean(episode_weights_is_clipped * episode_returns)

print(f"Behaviour policy value: {V_behav:.4f}")
print(f"IS estimate (eval policy): {V_is:.4f}")
print(f"WIS estimate (eval policy): {V_wis:.4f}")
print(f"Policy improvement (WIS): {V_wis - V_behav:.4f} ({(V_wis/max(V_behav,1e-8)-1)*100:.1f}%)")

# --- 2. Fitted Q Evaluation (FQE) ---
print("\n--- Fitted Q Evaluation (FQE) ---")

class FittedQEvaluation:
    """FQE: evaluate a fixed target policy using FQI-like iterations."""

    def __init__(self, n_actions, gamma, n_iterations=30, horizon=15):
        self.n_actions = n_actions
        self.gamma = gamma
        self.n_iterations = n_iterations
        self.horizon = horizon
        self.q_model = None
        self.history = []

    def fit(self, states, actions, rewards, next_states, dones,
            eval_policy_probs, sample_weight=None):
        """
        eval_policy_probs: (n, n_actions) — π_e(a|s') for target policy
        """
        n = len(states)
        q_targets = rewards.copy()

        for iteration in range(self.n_iterations):
            # Fit Q-model for evaluation (state-action as input)
            sa_features = np.column_stack([states, np.eye(self.n_actions)[actions]])
            self.q_model = GradientBoostingRegressor(
                n_estimators=100, max_depth=6, learning_rate=0.1,
                min_samples_leaf=10, random_state=42
            )
            self.q_model.fit(sa_features, q_targets, sample_weight=sample_weight)

            # Predict Q(s', a') for all actions under eval policy
            q_next_all = np.zeros((n, self.n_actions))
            for a in range(self.n_actions):
                sa_next = np.column_stack([next_states, np.eye(self.n_actions)[np.full(n, a)]])
                q_next_all[:, a] = self.q_model.predict(sa_next)

            # V(s') = Σ_a π_e(a|s') * Q(s', a)
            # Recompute eval_policy_probs for next_states using CQL
            v_next = np.sum(eval_policy_probs * q_next_all, axis=1)
            new_targets = rewards + self.gamma * v_next * (1 - dones)

            delta = np.mean(np.abs(new_targets - q_targets))
            self.history.append(delta)
            q_targets = new_targets

            if iteration % 5 == 0:
                print(f"  FQE iter {iteration+1}: ΔQ = {delta:.6f}")

        return self

    def evaluate(self, states, actions):
        """Return Q(s, a) for given state-action pairs."""
        sa = np.column_stack([states, np.eye(self.n_actions)[actions]])
        return self.q_model.predict(sa)

# Compute eval policy probs for next states (validation)
cql_q_next_val = cql_primary.predict_all(ns_val)
pi_e_next_probs = eval_policy_probs(cql_q_next_val)

fqe = FittedQEvaluation(n_actions=N_ACTIONS, gamma=GAMMA, n_iterations=30, horizon=15)
fqe.fit(s_val, a_val, r_val, ns_val, d_val, pi_e_next_probs, sample_weight=w_val)

# FQE value estimate
fqe_q_vals = fqe.evaluate(s_val, a_val)
V_fqe_behav = np.average(fqe_q_vals, weights=w_val)

# FQE for eval policy: use eval actions
eval_actions_val = cql_primary.predict_action(s_val)
fqe_q_eval = fqe.evaluate(s_val, eval_actions_val)
V_fqe_eval = np.average(fqe_q_eval, weights=w_val)

print(f"\nFQE behaviour value: {V_fqe_behav:.4f}")
print(f"FQE eval policy value: {V_fqe_eval:.4f}")
print(f"FQE improvement: {V_fqe_eval - V_fqe_behav:.4f} ({(V_fqe_eval/max(V_fqe_behav,1e-8)-1)*100:.1f}%)")

# --- 3. Doubly Robust (DR) estimator ---
print("\n--- Doubly Robust (DR) Estimator ---")

dr_estimates = []
for cid, indices in val_episodes.items():
    V_dr = 0.0
    rho_cumulative = 1.0
    for t, idx in enumerate(indices):
        a = a_val[idx]
        r = r_val[idx]

        pi_e_a = pi_e_probs[idx, a]
        pi_b_a = pi_b_full[idx, a]
        rho_t = pi_e_a / max(pi_b_a, 1e-8)

        # Q-estimate from FQE
        q_hat = fqe.evaluate(s_val[idx:idx+1], np.array([a]))[0]
        # V-estimate: E_{a~π_e}[Q(s,a)]
        v_hat_all = np.array([fqe.evaluate(s_val[idx:idx+1], np.array([aa]))[0]
                              for aa in range(N_ACTIONS)])
        v_hat = np.sum(pi_e_probs[idx] * v_hat_all)

        V_dr += (GAMMA ** t) * (rho_cumulative * rho_t * (r - q_hat) + v_hat)
        rho_cumulative *= rho_t
        rho_cumulative = min(rho_cumulative, clip_threshold)

    dr_estimates.append(V_dr)

V_dr = np.mean(dr_estimates)
print(f"DR estimate (eval policy): {V_dr:.4f}")

# --- OOD Action Frequency ---
print("\n--- OOD Action Analysis ---")
cql_policy_all = cql_primary.predict_action(states)
print("CQL policy action distribution (all data):")
cql_action_counts = np.bincount(cql_policy_all, minlength=N_ACTIONS)
behav_action_counts = np.bincount(actions, minlength=N_ACTIONS)
for a in range(N_ACTIONS):
    cql_pct = cql_action_counts[a] / len(cql_policy_all) * 100
    behav_pct = behav_action_counts[a] / len(actions) * 100
    print(f"  a{a}: CQL={cql_pct:.1f}% vs Behaviour={behav_pct:.1f}%")

ood_cql = (cql_action_counts[3] + cql_action_counts[4]) / len(cql_policy_all) * 100
ood_behav = (behav_action_counts[3] + behav_action_counts[4]) / len(actions) * 100
print(f"OOD frequency: CQL={ood_cql:.1f}%, Behaviour={ood_behav:.1f}%")

# ── OPE Summary Table ──
ope_results = {
    "behaviour_policy_value": float(V_behav),
    "IS_estimate": float(V_is),
    "WIS_estimate": float(V_wis),
    "FQE_behaviour_value": float(V_fqe_behav),
    "FQE_eval_policy_value": float(V_fqe_eval),
    "DR_estimate": float(V_dr),
    "policy_improvement_WIS": float(V_wis - V_behav),
    "policy_improvement_FQE": float(V_fqe_eval - V_fqe_behav),
    "policy_improvement_pct_WIS": float((V_wis / max(V_behav, 1e-8) - 1) * 100),
    "policy_improvement_pct_FQE": float((V_fqe_eval / max(V_fqe_behav, 1e-8) - 1) * 100),
    "ood_action_freq_cql_pct": float(ood_cql),
    "ood_action_freq_behav_pct": float(ood_behav),
    "cql_alpha": PRIMARY_ALPHA,
    "cql_final_penalty": float(cql_primary.cql_penalty_history[-1]),
    "n_validation_episodes": len(val_episodes),
    "wis_epsilon": EPSILON,
}
with open(OUT / "ope_results.json", "w") as f:
    json.dump(ope_results, f, indent=2)
print(f"\nOPE results saved to {OUT / 'ope_results.json'}")

# OPE comparison plot
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

ax = axes[0]
methods = ['Behaviour\n(observed)', 'IS', 'WIS', 'FQE\n(behaviour)', 'FQE\n(CQL policy)', 'DR']
values = [V_behav, V_is, V_wis, V_fqe_behav, V_fqe_eval, V_dr]
colors = ['#888888', '#4ECDC4', '#2196F3', '#FF9800', '#E91E63', '#9C27B0']
bars = ax.bar(methods, values, color=colors, edgecolor='black', linewidth=0.5)
ax.axhline(y=V_behav, color='grey', linestyle='--', alpha=0.5, label='Behaviour baseline')
ax.set_ylabel('Estimated Policy Value')
ax.set_title('Off-Policy Evaluation Comparison')
ax.legend()
for bar, val in zip(bars, values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
            f'{val:.3f}', ha='center', va='bottom', fontsize=9)

# Policy comparison
ax = axes[1]
x = np.arange(N_ACTIONS)
width = 0.35
ax.bar(x - width/2, behav_action_counts / len(actions) * 100, width,
       label='Behaviour', color='#90CAF9', edgecolor='black', linewidth=0.5)
ax.bar(x + width/2, cql_action_counts / len(cql_policy_all) * 100, width,
       label='CQL Policy', color='#EF5350', edgecolor='black', linewidth=0.5)
ax.set_xlabel('Action')
ax.set_ylabel('Frequency (%)')
ax.set_title('Action Distribution: Behaviour vs CQL Policy')
ax.set_xticks(x)
ax.set_xticklabels(['a₀: None', 'a₁: SMS', 'a₂: CHW', 'a₃: Recall', 'a₄: Incentive'],
                   rotation=15, ha='right')
ax.legend()

plt.tight_layout()
fig.savefig(OUT / "ope_comparison.pdf", dpi=300)
fig.savefig(OUT / "ope_comparison.png", dpi=300)
plt.close()

# ══════════════════════════════════════════════════════════════
# PHASE 1.4: POLICY EXTRACTION
# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("PHASE 1.4: POLICY EXTRACTION")
print("=" * 60)

# Extract policy for all states in the dataset
all_q = cql_primary.predict_all(states)
all_policy = np.argmax(all_q, axis=1)

# Build policy lookup table
policy_records = []
for i in range(len(states)):
    rec = {
        'child_id': child_ids[i],
        'dose_step': traj_df['dose_step'].values[i],
        'optimal_action': int(all_policy[i]),
        'q_a0': float(all_q[i, 0]),
        'q_a1': float(all_q[i, 1]),
        'q_a2': float(all_q[i, 2]),
        'q_a3': float(all_q[i, 3]),
        'q_a4': float(all_q[i, 4]),
        'q_max': float(np.max(all_q[i])),
        'q_advantage': float(np.max(all_q[i]) - all_q[i, int(actions[i])]),
        'behaviour_action': int(actions[i]),
        'weight': float(weights[i]),
    }
    policy_records.append(rec)

policy_df = pd.DataFrame(policy_records)
policy_df.to_csv(OUT / "policy_lookup.csv", index=False)
print(f"Policy lookup saved: {len(policy_df)} rows")
print(f"Policy changes from behaviour: {(all_policy != actions).sum()} / {len(actions)} "
      f"({(all_policy != actions).mean()*100:.1f}%)")

# Q-value heatmap by action and key state features
fig, ax = plt.subplots(figsize=(8, 5))
q_means_by_action = [np.mean(all_q[:, a]) for a in range(N_ACTIONS)]
action_labels = ['a₀: None\n(₦0)', 'a₁: SMS\n(₦50)', 'a₂: CHW\n(₦500)',
                 'a₃: Recall\n(₦1500)', 'a₄: Incentive\n(₦800)']
bars = ax.bar(action_labels, q_means_by_action,
              color=['#CFD8DC', '#81C784', '#4FC3F7', '#FFB74D', '#CE93D8'],
              edgecolor='black', linewidth=0.5)
ax.set_ylabel('Mean Q-value')
ax.set_title('Mean Q-values by Action (CQL Policy)')
for bar, val in zip(bars, q_means_by_action):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005,
            f'{val:.3f}', ha='center', va='bottom', fontsize=10)
plt.tight_layout()
fig.savefig(OUT / "q_values_by_action.pdf", dpi=300)
fig.savefig(OUT / "q_values_by_action.png", dpi=300)
plt.close()

# Save models
joblib.dump(fqi, OUT / "fqi_model.joblib")
joblib.dump(cql_primary, OUT / "cql_model.joblib")
joblib.dump(behav_model, OUT / "behaviour_policy_model.joblib")
joblib.dump(fqe, OUT / "fqe_model.joblib")

# Save CQL alpha sensitivity
alpha_sens_df = pd.DataFrame([
    {
        'alpha': a,
        'mean_q': cql_alpha_results[a]['mean_q'],
        'ood_freq': cql_alpha_results[a]['ood_freq'],
        'final_penalty': cql_alpha_results[a]['final_penalty'],
        **{f'action_{i}_pct': cql_alpha_results[a]['action_dist'][i] for i in range(N_ACTIONS)}
    }
    for a in sorted(cql_alpha_results.keys())
])
alpha_sens_df.to_csv(OUT / "cql_alpha_sensitivity.csv", index=False)

# ── Summary Stats ──
summary = {
    "fqi_iterations": len(fqi.history),
    "fqi_converged": bool(fqi.history[-1] < 0.001) if fqi.history else False,
    "fqi_final_delta": float(fqi.history[-1]) if fqi.history else None,
    "cql_alpha": PRIMARY_ALPHA,
    "cql_iterations": len(cql_primary.history),
    "cql_final_delta": float(cql_primary.history[-1]) if cql_primary.history else None,
    "cql_final_penalty": float(cql_primary.cql_penalty_history[-1]),
    "n_train": int(sum(train_mask)),
    "n_val": int(sum(val_mask)),
    "n_episodes_val": len(val_episodes),
    "policy_action_dist": {int(a): float(cql_action_counts[a] / len(cql_policy_all))
                           for a in range(N_ACTIONS)},
    "behaviour_action_dist": {int(a): float(behav_action_counts[a] / len(actions))
                              for a in range(N_ACTIONS)},
    "ope": ope_results,
    "policy_changes_pct": float((all_policy != actions).mean() * 100),
}
with open(OUT / "stage2_summary.json", "w") as f:
    json.dump(summary, f, indent=2)

print("\n" + "=" * 60)
print("STAGE 2 COMPLETE")
print("=" * 60)
print(f"FQI converged: {summary['fqi_converged']} (ΔQ={summary['fqi_final_delta']:.6f})")
print(f"CQL trained: α={PRIMARY_ALPHA}, penalty={summary['cql_final_penalty']:.4f}")
print(f"OPE improvement (WIS): {ope_results['policy_improvement_pct_WIS']:.1f}%")
print(f"OPE improvement (FQE): {ope_results['policy_improvement_pct_FQE']:.1f}%")
print(f"Policy changes: {summary['policy_changes_pct']:.1f}% of state-action pairs")
print(f"Outputs: {OUT}")
