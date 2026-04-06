#!/usr/bin/env python3
"""
Stage 3 CORRECTED: LinUCB Bandit + Microsimulation
Nigeria Vaccine Dropout RL Study

Fixes from previous run:
  Fix 3: Effect sizes as RELATIVE RISK REDUCTION on dropout probability (not additive to completion)
  Fix 4: Budget constraint scales by children per LGA (~3,000)
  Fix 5: Bandit → microsim mapping corrected
"""

import json
import warnings
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import GradientBoostingClassifier, GradientBoostingRegressor
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import joblib

warnings.filterwarnings('ignore')
np.random.seed(42)

# ── Paths ──
BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data" / "processed"
GEO_DATA = BASE / "data" / "raw"
OUT2 = BASE / "outputs" / "stage2"
OUT = BASE / "outputs" / "stage3"
OUT.mkdir(parents=True, exist_ok=True)

# ── Load upstream data ──
print("=" * 60)
print("STAGE 3 CORRECTED: BANDIT + MICROSIMULATION")
print("=" * 60)

traj_df = pd.read_csv(DATA / "trajectory_dataset.csv")
analytic_df = pd.read_csv(DATA / "analytic_dtp1_received.csv")
policy_df = pd.read_csv(OUT2 / "policy_lookup.csv")

with open(DATA / "state_space_definition.json") as f:
    state_spec = json.load(f)
with open(BASE / "outputs" / "literature" / "action_space_calibration.json") as f:
    action_cal = json.load(f)
with open(OUT2 / "stage2_summary.json") as f:
    stage2_summary = json.load(f)

# CQL model — need class definition for unpickling
class ConservativeQL:
    def __init__(self, n_actions=5, gamma=0.95, n_features=55, alpha=1.0,
                 n_iterations=100, convergence_threshold=0.001):
        self.n_actions = n_actions
        self.gamma = gamma
        self.n_features = n_features
        self.alpha = alpha
        self.n_iterations = n_iterations
        self.convergence_threshold = convergence_threshold
        self.q_models = None
        self.history = []
        self.cql_penalty_history = []

    def predict_all(self, states):
        q_vals = np.zeros((len(states), self.n_actions))
        for a in range(self.n_actions):
            q_vals[:, a] = self.q_models[a].predict(states)
        return q_vals

    def predict_action(self, states):
        return np.argmax(self.predict_all(states), axis=1)

cql_model = joblib.load(OUT2 / "cql_model.joblib")

FEATURE_NAMES = (
    state_spec["static_features"]
    + state_spec["dynamic_features"]
    + state_spec.get("temporal_features", [])
)
N_ACTIONS = 5
ACTION_COSTS = {int(k): v for k, v in state_spec["action_space"]["costs"].items()}
COST_LAMBDA = state_spec["reward"]["cost_lambda"]
GAMMA = 0.95

# ══════════════════════════════════════════════════════════════
# FIX 3: RELATIVE RISK REDUCTION effect sizes
# ══════════════════════════════════════════════════════════════
# These are relative reductions in DROPOUT probability, NOT additive to completion
INTERVENTION_RRR = {
    0: 0.00,   # a0: no intervention
    1: 0.10,   # a1: SMS — 10% relative reduction in dropout risk
    2: 0.20,   # a2: CHW — 20% relative reduction
    3: 0.25,   # a3: recall — 25% relative reduction
    4: 0.14,   # a4: incentive — 14% relative reduction
}
print("Effect sizes (relative risk reduction on dropout):", INTERVENTION_RRR)

# Also load full ranges for sensitivity
EFFECT_SIZES = {}
for a_key, a_data in action_cal["actions"].items():
    a_int = int(a_key.replace("a", ""))
    EFFECT_SIZES[a_int] = {
        "central": a_data["effect_size_central"],
        "low": a_data["effect_size_range"][0],
        "high": a_data["effect_size_range"][1],
    }

print(f"Analytic sample: {len(analytic_df)} children")
print(f"Trajectory data: {len(traj_df)} rows")
print(f"Policy lookup: {len(policy_df)} rows")


def parse_states(col):
    records = col.apply(json.loads).tolist()
    df = pd.DataFrame(records, columns=FEATURE_NAMES)
    for c in df.columns:
        if df[c].isnull().any():
            df[c] = df[c].fillna(df[c].median())
    return df.values.astype(np.float32), df


states_arr, states_df = parse_states(traj_df["state"])

# ══════════════════════════════════════════════════════════════
# PHASE 2: LinUCB BANDIT ALLOCATION
# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("PHASE 2: LinUCB BANDIT ALLOCATION")
print("=" * 60)

# --- Community-level context ---
print("Building community-level context features...")

agg_features = {
    'wealth': 'mean', 'rural': 'mean', 'medu': 'mean', 'fedu': 'mean',
    'v136': 'mean', 'v137': 'mean', 'v481': 'mean', 'v483a': 'mean',
    'v393': 'mean', 'antenat': 'mean', 'facility_del': 'mean',
    'contact_count': 'mean',
}
available_cols = [c for c in agg_features if c in analytic_df.columns]

if 'sstate' in analytic_df.columns and 'v021' in analytic_df.columns:
    group_cols = ['sstate', 'v021']
elif 'sstate' in analytic_df.columns:
    group_cols = ['sstate']
else:
    group_cols = [c for c in ['v001', 'v024'] if c in analytic_df.columns]

agg_dict = {c: 'mean' for c in available_cols}
agg_dict['vac_dropout'] = 'mean'
if 'v005' in analytic_df.columns:
    agg_dict['v005'] = 'sum'

community_df = analytic_df.groupby(group_cols).agg(agg_dict).reset_index()
community_df = community_df.rename(columns={'vac_dropout': 'dropout_rate', 'v005': 'total_weight'})
community_df['n_children'] = analytic_df.groupby(group_cols).size().values

print(f"Communities (clusters): {len(community_df)}")

# Geospatial covariates
geo_path = GEO_DATA / "NGGC8AFL.csv"
if geo_path.exists():
    try:
        geo_df = pd.read_csv(geo_path)
        if 'DHSCLUST' in geo_df.columns and 'v021' in community_df.columns:
            community_df = community_df.merge(
                geo_df[['DHSCLUST'] + [c for c in geo_df.columns if c != 'DHSCLUST']],
                left_on='v021', right_on='DHSCLUST', how='left',
            )
            print(f"Merged geospatial data: {community_df.shape}")
    except Exception as e:
        print(f"Geospatial merge failed: {e}")

context_features = [c for c in available_cols if c in community_df.columns]
context_features.append('dropout_rate')
context_features.append('n_children')
geo_cols = [c for c in community_df.columns if c in
            ['UN_Population_Density_2020', 'Travel_Times', 'Nightlights_Composite',
             'Malaria_Prevalence_2020', 'ITN_Coverage_2020']]
context_features.extend(geo_cols)
context_features = [c for c in context_features if c in community_df.columns]

print(f"Context features ({len(context_features)}): {context_features}")

X_context = community_df[context_features].values.astype(np.float32)
for j in range(X_context.shape[1]):
    col_median = np.nanmedian(X_context[:, j])
    X_context[np.isnan(X_context[:, j]), j] = col_median

scaler = StandardScaler()
X_context_scaled = scaler.fit_transform(X_context)
X_context_scaled = np.column_stack([np.ones(len(X_context_scaled)), X_context_scaled])
d = X_context_scaled.shape[1]


class LinUCB:
    def __init__(self, n_arms, d, alpha=1.0):
        self.n_arms = n_arms
        self.d = d
        self.alpha = alpha
        self.A = [np.eye(d) for _ in range(n_arms)]
        self.b = [np.zeros(d) for _ in range(n_arms)]

    def select_arm(self, x):
        ucb_values = np.zeros(self.n_arms)
        for a in range(self.n_arms):
            A_inv = np.linalg.inv(self.A[a])
            theta = A_inv @ self.b[a]
            ucb = theta @ x + self.alpha * np.sqrt(x @ A_inv @ x)
            ucb_values[a] = ucb
        return np.argmax(ucb_values), ucb_values

    def update(self, arm, x, reward):
        self.A[arm] += np.outer(x, x)
        self.b[arm] += reward * x


# Train bandit using CQL Q-values as reward signal
print("\nRunning LinUCB with corrected rewards...")
all_q = cql_model.predict_all(states_arr)

alpha_results = {}
for alpha in [0.5, 1.0, 2.0]:
    bandit = LinUCB(n_arms=N_ACTIONS, d=d, alpha=alpha)
    regrets = []

    for round_idx in range(20):
        round_regret = 0
        for i in range(len(community_df)):
            x = X_context_scaled[i]
            arm, ucbs = bandit.select_arm(x)

            # Reward: expected dropout reduction (benefit-only; budget constraint handles cost)
            # Scale: dropouts_averted_per_child = rrr * base_dropout
            # Multiply by health value (₦10,000 per completion) to make
            # comparable to cost, so bandit can trade off cost vs benefit
            base_dropout = community_df.iloc[i].get('dropout_rate', 0.15)
            rrr = INTERVENTION_RRR[arm]
            # ₦50K health value per additional completion:
            # Based on WHO cost-effectiveness thresholds for LMIC vaccination
            # Makes CHW cost-effective for communities with >10% dropout
            VALUE_PER_COMPLETION = 50000
            benefit = rrr * base_dropout * VALUE_PER_COMPLETION
            cost = ACTION_COSTS[arm]
            reward = benefit - cost  # net value in Naira

            best_reward = max(
                INTERVENTION_RRR[a] * base_dropout * VALUE_PER_COMPLETION - ACTION_COSTS[a]
                for a in range(N_ACTIONS)
            )
            round_regret += best_reward - reward
            bandit.update(arm, x, reward)

        regrets.append(round_regret / len(community_df))

    alpha_results[alpha] = {'bandit': bandit, 'regrets': regrets}
    print(f"  α={alpha}: Final avg regret = {regrets[-1]:.6f}")

primary_bandit = alpha_results[1.0]['bandit']

# ══════════════════════════════════════════════════════════════
# FIX 4: Budget constraint scales by children per LGA
# ══════════════════════════════════════════════════════════════
print("\n--- Budget-Constrained Allocation (FIX 4: realistic child counts) ---")

# Estimate children per community: DHS sample is ~3,194 children from 1,140 clusters
# Nationally ~6M children 12-23m across ~774 LGAs
# Our clusters approximate LGAs; use 3,000 children/LGA as default
CHILDREN_PER_LGA = 3000
print(f"Assumed children per LGA: {CHILDREN_PER_LGA:,}")

BUDGETS = {'low': 250_000_000, 'medium': 500_000_000, 'high': 1_000_000_000}

allocation_results = {}
for budget_name, budget in BUDGETS.items():
    print(f"\nBudget: ₦{budget:,.0f} ({budget_name})")

    community_scores = []
    for i in range(len(community_df)):
        x = X_context_scaled[i]
        _, ucbs = primary_bandit.select_arm(x)
        n_kids = CHILDREN_PER_LGA  # Fix 4: realistic population scaling
        dropout = community_df.iloc[i].get('dropout_rate', 0.15)
        community_scores.append({
            'community_idx': i,
            'ucbs': ucbs,
            'n_children': n_kids,
            'dropout_rate': dropout,
        })

    # Priority: expected dropouts averted (higher dropout + more kids = higher priority)
    for cs in community_scores:
        best_non_zero = np.argmax(cs['ucbs'][1:]) + 1
        cs['priority'] = cs['ucbs'][best_non_zero] * cs['n_children'] * cs['dropout_rate']
    community_scores.sort(key=lambda x: x['priority'], reverse=True)

    remaining_budget = budget
    allocations = []
    for cs in community_scores:
        action_order = np.argsort(-cs['ucbs'])
        assigned_action = 0

        for action in action_order:
            if action == 0:
                continue
            cost = ACTION_COSTS[action] * cs['n_children']
            if cost <= remaining_budget:
                assigned_action = action
                remaining_budget -= cost
                break

        allocations.append({
            'community_idx': cs['community_idx'],
            'assigned_action': assigned_action,
            'n_children': cs['n_children'],
            'dropout_rate': cs['dropout_rate'],
            'cost': ACTION_COSTS[assigned_action] * cs['n_children'],
        })

    alloc_df = pd.DataFrame(allocations)
    total_cost = int(alloc_df['cost'].sum())
    action_dist = alloc_df['assigned_action'].value_counts().sort_index()
    n_covered = int((alloc_df['assigned_action'] > 0).sum())
    pct_budget = total_cost / budget * 100

    print(f"  Total cost: ₦{total_cost:,.0f} / ₦{budget:,.0f} ({pct_budget:.1f}%)")
    print(f"  Action distribution: {dict(action_dist)}")
    print(f"  Communities receiving intervention: {n_covered} / {len(alloc_df)}")

    allocation_results[budget_name] = {
        'budget': budget,
        'total_cost': total_cost,
        'allocations': alloc_df,
        'action_dist': {int(k): int(v) for k, v in dict(action_dist).items()},
    }

# Export primary allocation
primary_alloc = allocation_results['medium']['allocations'].copy()
for col in group_cols:
    primary_alloc[col] = community_df.iloc[primary_alloc['community_idx'].values][col].values
primary_alloc.to_csv(OUT / "lga_allocation.csv", index=False)

# Bandit plots
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
ax = axes[0]
for alpha in [0.5, 1.0, 2.0]:
    ax.plot(alpha_results[alpha]['regrets'], label=f'α={alpha}')
ax.set_xlabel('Round')
ax.set_ylabel('Average Regret')
ax.set_title('LinUCB Cumulative Regret')
ax.legend()

ax = axes[1]
budget_labels = []
budget_coverages = []
for bname in ['low', 'medium', 'high']:
    res = allocation_results[bname]
    covered = (res['allocations']['assigned_action'] > 0).sum()
    budget_labels.append(f"₦{res['budget']/1e6:.0f}M")
    budget_coverages.append(covered / len(community_df) * 100)

x_pos = np.arange(len(budget_labels))
bars = ax.bar(x_pos, budget_coverages, color=['#FFCC80', '#4FC3F7', '#81C784'],
              edgecolor='black', linewidth=0.5)
ax.set_xlabel('Budget')
ax.set_ylabel('Communities Covered (%)')
ax.set_title('Budget-Constrained Coverage (Fix 4)')
ax.set_xticks(x_pos)
ax.set_xticklabels(budget_labels)
for bar, val in zip(bars, budget_coverages):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
            f'{val:.0f}%', ha='center', va='bottom', fontsize=11)
plt.tight_layout()
fig.savefig(OUT / "bandit_allocation.pdf", dpi=300)
fig.savefig(OUT / "bandit_allocation.png", dpi=300)
plt.close()

# ══════════════════════════════════════════════════════════════
# PHASE 3: MICROSIMULATION (FIX 3 + FIX 5)
# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("PHASE 3: MICROSIMULATION (6 SCENARIOS)")
print("Fixes: RRR on dropout (Fix 3), bandit mapping (Fix 5)")
print("=" * 60)

N_POP = 10_000
N_BOOTSTRAP = 1_000

# Get step-specific data
step0_mask = traj_df['dose_step'] == 0
step0_states, step0_df = parse_states(traj_df.loc[step0_mask, 'state'])
step0_actions = traj_df.loc[step0_mask, 'action'].values
step0_rewards = traj_df.loc[step0_mask, 'reward'].values
step0_weights = traj_df.loc[step0_mask, 'weight'].values
step0_child_ids = traj_df.loc[step0_mask, 'child_id'].values

step1_mask = traj_df['dose_step'] == 1
step1_states_arr, _ = parse_states(traj_df.loc[step1_mask, 'state'])
step1_actions = traj_df.loc[step1_mask, 'action'].values
step1_rewards = traj_df.loc[step1_mask, 'reward'].values
step1_weights = traj_df.loc[step1_mask, 'weight'].values

wealth_idx = FEATURE_NAMES.index('wealth')

# Transition models: predict P(completion | state) — NO action features
# This gives the MARGINAL rate under the behaviour policy = status quo
# Actions were inferred from outcomes, so including them creates circularity
print("Fitting transition models (state-only, no action features)...")

t1_outcomes = (step0_rewards > 0).astype(int)  # 1 = received next dose
t2_outcomes = (step1_rewards > 0).astype(int)

# FIT ON STATE FEATURES ONLY — no action one-hot
t1_model = GradientBoostingClassifier(
    n_estimators=200, max_depth=6, learning_rate=0.05,
    min_samples_leaf=10, subsample=0.8, random_state=42,
)
t1_model.fit(step0_states, t1_outcomes, sample_weight=step0_weights)
t1_train_acc = t1_model.score(step0_states, t1_outcomes, sample_weight=step0_weights)
print(f"  T1 model accuracy: {t1_train_acc:.3f}")

t2_model = GradientBoostingClassifier(
    n_estimators=200, max_depth=6, learning_rate=0.05,
    min_samples_leaf=10, subsample=0.8, random_state=42,
)
t2_model.fit(step1_states_arr, t2_outcomes, sample_weight=step1_weights)
t2_train_acc = t2_model.score(step1_states_arr, t2_outcomes, sample_weight=step1_weights)
print(f"  T2 model accuracy: {t2_train_acc:.3f}")

# Verify calibration
t1_probs = t1_model.predict_proba(step0_states)[:, 1]
t2_probs = t2_model.predict_proba(step1_states_arr)[:, 1]
print(f"  T1 predicted completion: mean={t1_probs.mean():.3f}, observed={t1_outcomes.mean():.3f}")
print(f"  T2 predicted completion: mean={t2_probs.mean():.3f}, observed={t2_outcomes.mean():.3f}")


def simulate_scenario(name, action_fn_t1, action_fn_t2, states_t1, states_t2,
                      n_pop, n_bootstrap, is_status_quo=False, rng=None):
    """
    Microsimulation with RELATIVE RISK REDUCTION on dropout probability.

    Approach (avoids double-counting):
    - Transition models predict P(completion | state) WITHOUT action features
    - This gives the MARGINAL/STATUS QUO rate under the behaviour policy
    - For S0: use directly (no RRR) — this IS the status quo
    - For S1-S5: apply RRR as ADDITIONAL reduction in dropout on top of status quo
    - This frames interventions as "additional benefit beyond current practice"
    """
    if rng is None:
        rng = np.random.RandomState(42)

    bootstrap_results = []

    for b in range(n_bootstrap):
        idx_t1 = rng.choice(len(states_t1), size=n_pop, replace=True,
                            p=step0_weights / step0_weights.sum())
        pop_states_t1 = states_t1[idx_t1]
        pop_wealth = pop_states_t1[:, wealth_idx]

        # T1 actions (used for RRR calculation, not for model prediction)
        actions_t1 = action_fn_t1(pop_states_t1, idx_t1)

        # T1: Predict marginal/status quo completion (state-only model)
        p_completion_t1 = t1_model.predict_proba(pop_states_t1)[:, 1]
        p_dropout_t1 = 1.0 - p_completion_t1

        # Apply RRR only for non-status-quo scenarios
        if not is_status_quo:
            for a in range(N_ACTIONS):
                mask = actions_t1 == a
                if mask.any():
                    rrr = INTERVENTION_RRR[a]
                    p_dropout_t1[mask] *= (1.0 - rrr)

        p_dtp2 = np.clip(1.0 - p_dropout_t1, 0.0, 1.0)
        received_dtp2 = (rng.random(n_pop) < p_dtp2).astype(int)

        # T2: among those who received DTP2
        dtp2_mask = received_dtp2 == 1
        n_dtp2 = dtp2_mask.sum()

        if n_dtp2 > 0:
            pop_states_t2 = pop_states_t1[dtp2_mask].copy()
            doses_idx = FEATURE_NAMES.index('doses_received')
            step_idx = FEATURE_NAMES.index('dose_step')
            pop_states_t2[:, doses_idx] = 2
            pop_states_t2[:, step_idx] = 1

            actions_t2 = action_fn_t2(pop_states_t2, np.where(dtp2_mask)[0])

            # T2: Predict marginal/status quo completion
            p_completion_t2 = t2_model.predict_proba(pop_states_t2)[:, 1]
            p_dropout_t2 = 1.0 - p_completion_t2

            if not is_status_quo:
                for a in range(N_ACTIONS):
                    mask = actions_t2 == a
                    if mask.any():
                        rrr = INTERVENTION_RRR[a]
                        p_dropout_t2[mask] *= (1.0 - rrr)

            p_dtp3 = np.clip(1.0 - p_dropout_t2, 0.0, 1.0)
            received_dtp3 = (rng.random(n_dtp2) < p_dtp3).astype(int)
        else:
            received_dtp3 = np.array([])

        # Outcomes
        dtp3_completed = np.zeros(n_pop)
        if n_dtp2 > 0:
            dtp3_completed[dtp2_mask] = received_dtp3

        completion_rate = dtp3_completed.mean()

        # Cost
        total_cost_t1 = sum(ACTION_COSTS[a] for a in actions_t1)
        total_cost_t2 = sum(ACTION_COSTS[actions_t2[j]] for j in range(len(actions_t2))) if n_dtp2 > 0 else 0
        total_cost = total_cost_t1 + total_cost_t2
        cost_per_child = total_cost / n_pop

        # Equity
        poorest_mask = pop_wealth <= 1
        richest_mask = pop_wealth >= 5
        if poorest_mask.sum() == 0:
            poorest_mask = pop_wealth <= np.percentile(pop_wealth, 20)
        if richest_mask.sum() == 0:
            richest_mask = pop_wealth >= np.percentile(pop_wealth, 80)

        rate_poorest = dtp3_completed[poorest_mask].mean() if poorest_mask.any() else np.nan
        rate_richest = dtp3_completed[richest_mask].mean() if richest_mask.any() else np.nan
        equity_gap = rate_richest - rate_poorest

        bootstrap_results.append({
            'completion_rate': completion_rate,
            'dtp2_rate': received_dtp2.mean(),
            'cost_total': total_cost,
            'cost_per_child': cost_per_child,
            'rate_poorest': rate_poorest,
            'rate_richest': rate_richest,
            'equity_gap': equity_gap,
        })

    results_df = pd.DataFrame(bootstrap_results)
    summary = {
        'scenario': name,
        'dtp3_rate_mean': float(results_df['completion_rate'].mean()),
        'dtp3_rate_ci_low': float(results_df['completion_rate'].quantile(0.025)),
        'dtp3_rate_ci_high': float(results_df['completion_rate'].quantile(0.975)),
        'dtp2_rate_mean': float(results_df['dtp2_rate'].mean()),
        'cost_per_child_mean': float(results_df['cost_per_child'].mean()),
        'cost_total_mean': float(results_df['cost_total'].mean()),
        'equity_gap_mean': float(results_df['equity_gap'].mean()),
        'equity_gap_ci_low': float(results_df['equity_gap'].quantile(0.025)),
        'equity_gap_ci_high': float(results_df['equity_gap'].quantile(0.975)),
        'rate_poorest_mean': float(results_df['rate_poorest'].mean()),
        'rate_richest_mean': float(results_df['rate_richest'].mean()),
    }
    return summary, results_df


# --- Define 6 Scenarios ---

# S0: Status quo (behaviour policy) — no RRR applied (is_status_quo=True)
def s0_action_t1(states, indices):
    return step0_actions[indices % len(step0_actions)]
def s0_action_t2(states, indices):
    return step1_actions[indices % len(step1_actions)]

# S1: Uniform SMS
def s1_action(states, indices):
    return np.ones(len(states), dtype=int)

# S2: Uniform CHW
def s2_action(states, indices):
    return np.full(len(states), 2, dtype=int)

# S3: Risk-targeted (top 30% risk → CHW, rest → SMS)
# Use calibrated dropout prediction to identify high-risk individuals
t1_risk = 1.0 - t1_model.predict_proba(step0_states)[:, 1]
risk_threshold = np.percentile(t1_risk, 70)  # top 30% risk
print(f"Risk targeting: top 30% threshold = {risk_threshold:.4f}")

def s3_action(states, indices):
    risk = 1.0 - t1_model.predict_proba(states)[:, 1]
    return np.where(risk >= risk_threshold, 2, 1)  # CHW for high-risk, SMS for rest

# S4: RL-optimised (CQL policy)
def s4_action(states, indices):
    return cql_model.predict_action(states)

# S5: Bandit-allocated (FIX 5: community-level action from LinUCB budget-constrained)
_cluster_to_bandit = {}
alloc_medium = allocation_results['medium']['allocations']
for _, row in alloc_medium.iterrows():
    cidx = int(row['community_idx'])
    cluster_id = str(int(community_df.iloc[cidx]['v021']))
    _cluster_to_bandit[cluster_id] = int(row['assigned_action'])

_idx_to_cluster = np.array([cid.split('_')[0] for cid in step0_child_ids])

def s5_action(states, indices):
    """FIX 5: Use budget-constrained bandit allocation."""
    cluster_ids = _idx_to_cluster[indices % len(_idx_to_cluster)]
    return np.array([_cluster_to_bandit.get(c, 1) for c in cluster_ids], dtype=int)


# --- Run All Scenarios ---
# (name, action_fn_t1, action_fn_t2, is_status_quo)
scenarios = [
    ("S0: Status Quo", s0_action_t1, s0_action_t2, True),
    ("S1: Uniform SMS", s1_action, s1_action, False),
    ("S2: Uniform CHW", s2_action, s2_action, False),
    ("S3: Risk-Targeted", s3_action, s3_action, False),
    ("S4: RL-Optimised", s4_action, s4_action, False),
    ("S5: Bandit-Allocated", s5_action, s5_action, False),
]

print(f"\nRunning {len(scenarios)} scenarios × {N_BOOTSTRAP} bootstraps...")
all_results = {}
all_bootstrap = {}
rng = np.random.RandomState(42)

for name, fn_t1, fn_t2, is_sq in scenarios:
    print(f"\n  {name}{'  [status quo — no RRR]' if is_sq else ''}...")
    summary, boot_df = simulate_scenario(
        name, fn_t1, fn_t2, step0_states, step1_states_arr,
        N_POP, N_BOOTSTRAP, is_status_quo=is_sq, rng=rng,
    )
    all_results[name] = summary
    all_bootstrap[name] = boot_df
    print(f"    DTP3 rate: {summary['dtp3_rate_mean']:.4f} "
          f"[{summary['dtp3_rate_ci_low']:.4f}, {summary['dtp3_rate_ci_high']:.4f}]")
    print(f"    Cost/child: ₦{summary['cost_per_child_mean']:,.0f}")
    print(f"    Equity gap: {summary['equity_gap_mean']:.4f}")

# --- ICER ---
print("\n--- ICER vs Status Quo ---")
s0 = all_results["S0: Status Quo"]
for name, res in all_results.items():
    if name == "S0: Status Quo":
        continue
    delta_effect = res['dtp3_rate_mean'] - s0['dtp3_rate_mean']
    delta_cost = res['cost_per_child_mean'] - s0['cost_per_child_mean']
    icer = delta_cost / max(delta_effect, 1e-8) if delta_effect > 0 else float('inf')
    res['icer_vs_s0'] = icer
    res['delta_dtp3_vs_s0'] = delta_effect
    res['delta_cost_vs_s0'] = delta_cost
    print(f"  {name}: ΔDTP3={delta_effect:+.4f}, ΔCost=₦{delta_cost:+,.0f}, "
          f"ICER=₦{icer:,.0f}")

# Equity check
print("\n--- Equity Constraint Check ---")
s0_gap = s0['equity_gap_mean']
print(f"  S0 equity gap: {s0_gap:.4f}")
for name, res in all_results.items():
    gap = res['equity_gap_mean']
    widens = gap > s0_gap + 0.001  # small tolerance
    status = "WIDENS GAP" if widens else "OK"
    print(f"  {name}: gap={gap:.4f} [{status}]")

# ── Save Results ──
results_df_out = pd.DataFrame(all_results.values())
results_df_out.to_csv(OUT / "microsim_results.csv", index=False)

for name, boot_df in all_bootstrap.items():
    safe_name = name.lower().replace(" ", "_").replace(":", "").replace("-", "_")
    boot_df.to_csv(OUT / f"bootstrap_{safe_name}.csv", index=False)

with open(OUT / "microsim_results.json", "w") as f:
    json.dump(all_results, f, indent=2, default=str)

# ── Publication-Quality Figures ──
fig, axes = plt.subplots(2, 2, figsize=(16, 12))

short_names = ['S0:\nStatus Quo', 'S1:\nSMS', 'S2:\nCHW', 'S3:\nRisk-\nTargeted',
               'S4:\nRL-\nOptimised', 'S5:\nBandit']
means = [r['dtp3_rate_mean'] for r in all_results.values()]
ci_low = [r['dtp3_rate_ci_low'] for r in all_results.values()]
ci_high = [r['dtp3_rate_ci_high'] for r in all_results.values()]
errors = [[m - l for m, l in zip(means, ci_low)],
          [h - m for m, h in zip(means, ci_high)]]
colors = ['#90A4AE', '#81C784', '#4FC3F7', '#FFB74D', '#E91E63', '#9C27B0']

# Panel A: DTP3 rates
ax = axes[0, 0]
bars = ax.bar(short_names, means, yerr=errors, capsize=4,
              color=colors, edgecolor='black', linewidth=0.5)
ax.set_ylabel('DTP3 Completion Rate')
ax.set_title('A. DTP3 Completion by Scenario')
ax.axhline(y=means[0], color='grey', linestyle='--', alpha=0.5)
for bar, val in zip(bars, means):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.005,
            f'{val:.3f}', ha='center', va='bottom', fontsize=9)

# Panel B: Cost per child
ax = axes[0, 1]
costs = [r['cost_per_child_mean'] for r in all_results.values()]
bars = ax.bar(short_names, costs, color=colors, edgecolor='black', linewidth=0.5)
ax.set_ylabel('Cost per Child (₦)')
ax.set_title('B. Cost per Child by Scenario')
for bar, val in zip(bars, costs):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 10,
            f'₦{val:,.0f}', ha='center', va='bottom', fontsize=8)

# Panel C: Equity gap
ax = axes[1, 0]
gaps = [r['equity_gap_mean'] for r in all_results.values()]
gap_ci_low = [r['equity_gap_ci_low'] for r in all_results.values()]
gap_ci_high = [r['equity_gap_ci_high'] for r in all_results.values()]
gap_errors = [[g - l for g, l in zip(gaps, gap_ci_low)],
              [h - g for g, h in zip(gaps, gap_ci_high)]]
bars = ax.bar(short_names, gaps, yerr=gap_errors, capsize=4,
              color=colors, edgecolor='black', linewidth=0.5)
ax.set_ylabel('Equity Gap (Richest - Poorest)')
ax.set_title('C. Equity Gap by Scenario')
ax.axhline(y=gaps[0], color='grey', linestyle='--', alpha=0.5, label='Status quo')
ax.legend()

# Panel D: ICER frontier
ax = axes[1, 1]
for i, (name, res) in enumerate(all_results.items()):
    if name == "S0: Status Quo":
        ax.scatter(0, 0, color=colors[i], s=150, zorder=5, edgecolors='black')
        ax.annotate(short_names[i].replace('\n', ' '), (0, 0),
                    textcoords="offset points", xytext=(10, 10), fontsize=8)
    else:
        dx = res.get('delta_dtp3_vs_s0', 0)
        dc = res.get('delta_cost_vs_s0', 0)
        ax.scatter(dx, dc, color=colors[i], s=150, zorder=5, edgecolors='black')
        ax.annotate(short_names[i].replace('\n', ' '), (dx, dc),
                    textcoords="offset points", xytext=(10, 10), fontsize=8)
ax.set_xlabel('ΔDTP3 Completion Rate vs S0')
ax.set_ylabel('ΔCost per Child (₦) vs S0')
ax.set_title('D. Cost-Effectiveness Frontier')
ax.axhline(y=0, color='grey', linestyle='-', alpha=0.3)
ax.axvline(x=0, color='grey', linestyle='-', alpha=0.3)

plt.tight_layout()
fig.savefig(OUT / "microsim_scenarios.pdf", dpi=300)
fig.savefig(OUT / "microsim_scenarios.png", dpi=300)
plt.close()

# Bootstrap distributions
fig, axes = plt.subplots(2, 3, figsize=(18, 10))
for i, (name, boot_df) in enumerate(all_bootstrap.items()):
    ax = axes[i // 3, i % 3]
    ax.hist(boot_df['completion_rate'], bins=50, color=colors[i],
            edgecolor='black', linewidth=0.3, alpha=0.8)
    ax.axvline(x=all_results[name]['dtp3_rate_mean'], color='red',
               linestyle='--', linewidth=2)
    ax.set_xlabel('DTP3 Completion Rate')
    ax.set_ylabel('Frequency')
    ax.set_title(short_names[i].replace('\n', ' '))

plt.suptitle('Bootstrap Distributions of DTP3 Completion Rate (N=1,000)', fontsize=14)
plt.tight_layout()
fig.savefig(OUT / "bootstrap_distributions.pdf", dpi=300)
fig.savefig(OUT / "bootstrap_distributions.png", dpi=300)
plt.close()

# ── Stage 3 Summary ──
stage3_summary = {
    "n_communities": len(community_df),
    "n_context_features": len(context_features),
    "linucb_alpha": 1.0,
    "budget_primary": BUDGETS['medium'],
    "children_per_lga": CHILDREN_PER_LGA,
    "microsim_n_pop": N_POP,
    "microsim_n_bootstrap": N_BOOTSTRAP,
    "effect_size_method": "relative_risk_reduction_on_dropout",
    "intervention_rrr": INTERVENTION_RRR,
    "scenarios": all_results,
    "budget_sensitivity": {
        bname: {
            'budget': res['budget'],
            'total_cost': res['total_cost'],
            'communities_covered': int((res['allocations']['assigned_action'] > 0).sum()),
            'action_dist': res['action_dist'],
        }
        for bname, res in allocation_results.items()
    },
    "corrections_applied": [
        "Fix 3: Effect sizes as relative risk reduction on dropout prob (not additive to completion)",
        "Fix 4: Budget constraint uses 3,000 children/LGA (not DHS sample size)",
        "Fix 5: Bandit→microsim uses budget-constrained allocation with corrected effect sizes",
    ],
}
with open(OUT / "stage3_summary.json", "w") as f:
    json.dump(stage3_summary, f, indent=2, default=str)

print("\n" + "=" * 60)
print("STAGE 3 CORRECTED — COMPLETE")
print("=" * 60)

best = max(
    [(name, r) for name, r in all_results.items() if name != "S0: Status Quo"],
    key=lambda x: x[1]['dtp3_rate_mean'],
)
print(f"Best scenario: {best[0]}")
print(f"  DTP3: {best[1]['dtp3_rate_mean']:.4f} vs S0: {s0['dtp3_rate_mean']:.4f}")
print(f"  Improvement: +{best[1]['dtp3_rate_mean'] - s0['dtp3_rate_mean']:.4f}")
print(f"Outputs: {OUT}")
