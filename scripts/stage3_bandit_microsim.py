#!/usr/bin/env python3
"""
Stage 3: Multi-Armed Bandit (LinUCB) + Microsimulation Validation
Nigeria Vaccine Dropout RL Study
"""

import json
import warnings
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.preprocessing import StandardScaler
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
GEO_DATA = BASE / "data" / "raw"
OUT2 = BASE / "outputs" / "stage2"
OUT = BASE / "outputs" / "stage3"
OUT.mkdir(parents=True, exist_ok=True)

# ── Load upstream data ──
print("=" * 60)
print("STAGE 3: BANDIT ALLOCATION + MICROSIMULATION")
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
with open(OUT2 / "ope_results.json") as f:
    ope_results = json.load(f)

# CQL class definition needed for unpickling
from sklearn.ensemble import GradientBoostingRegressor as _GBR

class ConservativeQL:
    """CQL stub for deserialization."""
    def __init__(self, n_actions=5, gamma=0.95, n_features=55, alpha=1.0,
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

    def predict_all(self, states):
        q_vals = np.zeros((len(states), self.n_actions))
        for a in range(self.n_actions):
            q_vals[:, a] = self.q_models[a].predict(states)
        return q_vals

    def predict_action(self, states):
        q_vals = self.predict_all(states)
        return np.argmax(q_vals, axis=1)

cql_model = joblib.load(OUT2 / "cql_model.joblib")

FEATURE_NAMES = state_spec["static_features"] + state_spec["dynamic_features"] + state_spec.get("temporal_features", [])
N_ACTIONS = 5
ACTION_COSTS = {int(k): v for k, v in state_spec["action_space"]["costs"].items()}
COST_LAMBDA = state_spec["reward"]["cost_lambda"]
GAMMA = 0.95

# Effect sizes from literature
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

# ── Parse states ──
def parse_states(col):
    records = col.apply(json.loads).tolist()
    df = pd.DataFrame(records, columns=FEATURE_NAMES)
    for c in df.columns:
        if df[c].isnull().any():
            df[c] = df[c].fillna(df[c].median())
    return df.values.astype(np.float32), df

states_arr, states_df = parse_states(traj_df["state"])

# ══════════════════════════════════════════════════════════════
# PHASE 2: MULTI-ARMED BANDIT (LinUCB)
# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("PHASE 2: LinUCB BANDIT ALLOCATION")
print("=" * 60)

# --- 2.1 Build LGA-level context features ---
# Use analytic_df to aggregate child-level features to community level
# Since we don't have explicit LGA codes, use cluster (v021) as proxy
# Group by sstate + v021 for community-level aggregation

print("Building community-level context features...")

# Features to aggregate
agg_features = {
    'wealth': 'mean',
    'rural': 'mean',
    'medu': 'mean',
    'fedu': 'mean',
    'v136': 'mean',  # household size
    'v137': 'mean',  # under-5 children
    'v481': 'mean',  # insurance
    'v483a': 'mean',  # travel time
    'v393': 'mean',  # fieldworker visit
    'antenat': 'mean',  # antenatal visits
    'facility_del': 'mean',  # facility delivery
    'contact_count': 'mean',  # health contacts
}

# Check which columns exist
available_cols = [c for c in agg_features.keys() if c in analytic_df.columns]
print(f"Available aggregation columns: {len(available_cols)}")

# Identify community grouping columns
if 'sstate' in analytic_df.columns and 'v021' in analytic_df.columns:
    group_cols = ['sstate', 'v021']
elif 'sstate' in analytic_df.columns:
    group_cols = ['sstate']
else:
    # Fallback: use first few columns as identifiers
    group_cols = [c for c in ['v001', 'v024'] if c in analytic_df.columns]

print(f"Grouping by: {group_cols}")

# Compute community features
agg_dict = {c: 'mean' for c in available_cols}
agg_dict['vac_dropout'] = 'mean'  # community dropout rate
if 'v005' in analytic_df.columns:
    agg_dict['v005'] = 'sum'  # total weight

community_df = analytic_df.groupby(group_cols).agg(agg_dict).reset_index()
community_df = community_df.rename(columns={'vac_dropout': 'dropout_rate', 'v005': 'total_weight'})
community_df['n_children'] = analytic_df.groupby(group_cols).size().values

print(f"Communities (clusters): {len(community_df)}")

# Try to load geospatial covariates
geo_path = GEO_DATA / "NGGC8AFL.csv"
if geo_path.exists():
    try:
        geo_df = pd.read_csv(geo_path)
        print(f"Geospatial covariates loaded: {geo_df.shape}")
        # Merge on cluster ID if possible
        if 'DHSCLUST' in geo_df.columns and 'v021' in community_df.columns:
            community_df = community_df.merge(
                geo_df[['DHSCLUST'] + [c for c in geo_df.columns if c != 'DHSCLUST']],
                left_on='v021', right_on='DHSCLUST', how='left'
            )
            print(f"Merged geospatial data: {community_df.shape}")
    except Exception as e:
        print(f"Geospatial merge failed: {e}")

# Prepare context matrix for LinUCB
context_features = [c for c in available_cols if c in community_df.columns]
context_features.append('dropout_rate')
context_features.append('n_children')

# Add geospatial if available
geo_cols = [c for c in community_df.columns if c in
            ['UN_Population_Density_2020', 'Travel_Times', 'Nightlights_Composite',
             'Malaria_Prevalence_2020', 'ITN_Coverage_2020']]
context_features.extend(geo_cols)
context_features = [c for c in context_features if c in community_df.columns]

print(f"Context features ({len(context_features)}): {context_features}")

X_context = community_df[context_features].values.astype(np.float32)
# Fill NaNs
for j in range(X_context.shape[1]):
    col_median = np.nanmedian(X_context[:, j])
    X_context[np.isnan(X_context[:, j]), j] = col_median

scaler = StandardScaler()
X_context_scaled = scaler.fit_transform(X_context)

# Add bias term
X_context_scaled = np.column_stack([np.ones(len(X_context_scaled)), X_context_scaled])
d = X_context_scaled.shape[1]  # context dimension

print(f"Context matrix: {X_context_scaled.shape}")

# --- 2.2 LinUCB Implementation ---
class LinUCB:
    """Contextual bandit with LinUCB (disjoint model)."""

    def __init__(self, n_arms, d, alpha=1.0):
        self.n_arms = n_arms
        self.d = d
        self.alpha = alpha
        # Per-arm parameters
        self.A = [np.eye(d) for _ in range(n_arms)]  # d×d matrix
        self.b = [np.zeros(d) for _ in range(n_arms)]  # d vector
        self.history = []

    def select_arm(self, x):
        """Select arm with highest UCB for context x."""
        ucb_values = np.zeros(self.n_arms)
        for a in range(self.n_arms):
            A_inv = np.linalg.inv(self.A[a])
            theta = A_inv @ self.b[a]
            ucb = theta @ x + self.alpha * np.sqrt(x @ A_inv @ x)
            ucb_values[a] = ucb
        return np.argmax(ucb_values), ucb_values

    def update(self, arm, x, reward):
        """Update parameters for chosen arm."""
        self.A[arm] += np.outer(x, x)
        self.b[arm] += reward * x

    def get_theta(self, arm):
        A_inv = np.linalg.inv(self.A[arm])
        return A_inv @ self.b[arm]


# Estimate reward per arm per community using CQL Q-values
# For each community, compute average CQL Q-values
print("\nComputing community-level rewards from CQL Q-values...")

# Map children to communities
child_community_map = {}
if 'v021' in analytic_df.columns and 'sstate' in analytic_df.columns:
    for idx, row in analytic_df.iterrows():
        key = (int(row['sstate']), int(row['v021']))
        child_community_map[idx] = key

# Compute Q-values for all trajectory states
all_q = cql_model.predict_all(states_arr)
traj_communities = []
for i, row in traj_df.iterrows():
    cid_parts = str(row['child_id']).split('_')
    if len(cid_parts) >= 2:
        traj_communities.append(int(cid_parts[0]))  # v001 ≈ cluster
    else:
        traj_communities.append(0)

# Run LinUCB with simulated feedback
print("\nRunning LinUCB...")
alpha_results = {}
for alpha in [0.5, 1.0, 2.0]:
    bandit = LinUCB(n_arms=N_ACTIONS, d=d, alpha=alpha)
    regrets = []
    selections = []

    # Multiple rounds over communities
    for round_idx in range(20):
        round_regret = 0
        for i in range(len(community_df)):
            x = X_context_scaled[i]
            arm, ucbs = bandit.select_arm(x)
            selections.append(arm)

            # Reward: estimated effect size * (1 - current dropout) - cost penalty
            base_dropout = community_df.iloc[i]['dropout_rate'] if 'dropout_rate' in community_df.columns else 0.15
            effect = EFFECT_SIZES[arm]['central']
            reward = effect * (1 - base_dropout) - COST_LAMBDA * ACTION_COSTS[arm]

            # Best possible reward (oracle)
            best_reward = max(
                EFFECT_SIZES[a]['central'] * (1 - base_dropout) - COST_LAMBDA * ACTION_COSTS[a]
                for a in range(N_ACTIONS)
            )
            round_regret += best_reward - reward
            bandit.update(arm, x, reward)

        regrets.append(round_regret / len(community_df))

    alpha_results[alpha] = {
        'bandit': bandit,
        'regrets': regrets,
        'selections': selections,
    }
    print(f"  α={alpha}: Final avg regret = {regrets[-1]:.6f}")

# Select primary bandit (α=1.0)
primary_bandit = alpha_results[1.0]['bandit']

# --- 2.3 Budget-Constrained Allocation ---
print("\n--- Budget-Constrained Allocation ---")

BUDGETS = {'low': 250_000_000, 'medium': 500_000_000, 'high': 1_000_000_000}

allocation_results = {}
for budget_name, budget in BUDGETS.items():
    print(f"\nBudget: ₦{budget:,.0f} ({budget_name})")

    # For each community, rank actions by UCB value
    allocations = []
    total_cost = 0

    # Score all communities
    community_scores = []
    for i in range(len(community_df)):
        x = X_context_scaled[i]
        _, ucbs = primary_bandit.select_arm(x)
        n_kids = community_df.iloc[i]['n_children']
        dropout = community_df.iloc[i].get('dropout_rate', 0.15)
        community_scores.append({
            'community_idx': i,
            'ucbs': ucbs,
            'n_children': n_kids,
            'dropout_rate': dropout,
        })

    # Greedy allocation: prioritize communities with highest expected benefit
    # Sort by expected improvement (UCB of best non-zero action * n_children * dropout)
    for cs in community_scores:
        best_non_zero = np.argmax(cs['ucbs'][1:]) + 1  # exclude a0
        cs['priority'] = cs['ucbs'][best_non_zero] * cs['n_children'] * cs['dropout_rate']
    community_scores.sort(key=lambda x: x['priority'], reverse=True)

    remaining_budget = budget
    for cs in community_scores:
        # Try actions from most effective to least
        action_order = np.argsort(-cs['ucbs'])
        assigned_action = 0  # default: no intervention

        for action in action_order:
            if action == 0:
                continue
            cost = ACTION_COSTS[action] * cs['n_children']
            if cost <= remaining_budget:
                assigned_action = action
                remaining_budget -= cost
                total_cost += cost
                break

        allocations.append({
            'community_idx': cs['community_idx'],
            'assigned_action': assigned_action,
            'n_children': cs['n_children'],
            'dropout_rate': cs['dropout_rate'],
            'cost': ACTION_COSTS[assigned_action] * cs['n_children'],
        })

    alloc_df = pd.DataFrame(allocations)
    action_dist = alloc_df['assigned_action'].value_counts().sort_index()
    print(f"  Total cost: ₦{total_cost:,.0f} / ₦{budget:,.0f} ({total_cost/budget*100:.1f}%)")
    print(f"  Action distribution: {dict(action_dist)}")
    print(f"  Communities covered: {(alloc_df['assigned_action'] > 0).sum()} / {len(alloc_df)}")

    allocation_results[budget_name] = {
        'budget': budget,
        'total_cost': total_cost,
        'allocations': alloc_df,
        'action_dist': dict(action_dist),
    }

# Export primary allocation (₦500M)
primary_alloc = allocation_results['medium']['allocations'].copy()
# Add community identifiers
for col in group_cols:
    primary_alloc[col] = community_df.iloc[primary_alloc['community_idx'].values][col].values
primary_alloc.to_csv(OUT / "lga_allocation.csv", index=False)
print(f"\nPrimary allocation saved: {OUT / 'lga_allocation.csv'}")

# Bandit regret plot
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
budget_costs_pct = []
for bname in ['low', 'medium', 'high']:
    res = allocation_results[bname]
    covered = (res['allocations']['assigned_action'] > 0).sum()
    budget_labels.append(f"₦{res['budget']/1e6:.0f}M")
    budget_coverages.append(covered / len(community_df) * 100)
    budget_costs_pct.append(res['total_cost'] / res['budget'] * 100)

x = np.arange(len(budget_labels))
bars = ax.bar(x, budget_coverages, color=['#FFCC80', '#4FC3F7', '#81C784'],
              edgecolor='black', linewidth=0.5)
ax.set_xlabel('Budget')
ax.set_ylabel('Communities Covered (%)')
ax.set_title('Budget-Constrained Coverage')
ax.set_xticks(x)
ax.set_xticklabels(budget_labels)
for bar, val in zip(bars, budget_coverages):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
            f'{val:.0f}%', ha='center', va='bottom', fontsize=11)

plt.tight_layout()
fig.savefig(OUT / "bandit_allocation.pdf", dpi=300)
fig.savefig(OUT / "bandit_allocation.png", dpi=300)
plt.close()


# ══════════════════════════════════════════════════════════════
# PHASE 3: MICROSIMULATION VALIDATION
# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("PHASE 3: MICROSIMULATION (6 SCENARIOS)")
print("=" * 60)

# --- 3.1 Synthetic Population ---
N_POP = 10_000
N_BOOTSTRAP = 1_000

print(f"Generating synthetic population: N={N_POP}")

# Sample with replacement from actual data, weighted by survey weights
sample_weights_norm = analytic_df['v005'].values / analytic_df['v005'].sum() if 'v005' in analytic_df.columns else None

# Get state vectors for step 0 (DTP1 → DTP2 decision)
step0_mask = traj_df['dose_step'] == 0
step0_states, step0_df = parse_states(traj_df.loc[step0_mask, 'state'])
step0_actions = traj_df.loc[step0_mask, 'action'].values
step0_rewards = traj_df.loc[step0_mask, 'reward'].values
step0_dones = traj_df.loc[step0_mask, 'done'].values
step0_weights = traj_df.loc[step0_mask, 'weight'].values
step0_child_ids = traj_df.loc[step0_mask, 'child_id'].values

# Wealth quintile for equity analysis
wealth_idx = FEATURE_NAMES.index('wealth')

print(f"Step 0 records: {len(step0_states)}")

# Build transition model from observed data
# P(next_dose_received | state, action) — logistic model
from sklearn.ensemble import GradientBoostingClassifier

# For T1: did child receive DTP2?
t1_outcomes = (step0_rewards > 0).astype(int)  # reward > 0 means next dose received

# For T2: did child receive DTP3? (among those who got DTP2)
step1_mask = traj_df['dose_step'] == 1
step1_states_arr, _ = parse_states(traj_df.loc[step1_mask, 'state'])
step1_actions = traj_df.loc[step1_mask, 'action'].values
step1_rewards = traj_df.loc[step1_mask, 'reward'].values
step1_weights = traj_df.loc[step1_mask, 'weight'].values
t2_outcomes = (step1_rewards > 0).astype(int)

print("Fitting transition models...")

# T1 transition model: P(DTP2 | state, action)
t1_features = np.column_stack([step0_states, np.eye(N_ACTIONS)[step0_actions]])
t1_model = GradientBoostingClassifier(
    n_estimators=100, max_depth=6, learning_rate=0.1,
    min_samples_leaf=10, random_state=42
)
t1_model.fit(t1_features, t1_outcomes, sample_weight=step0_weights)
print(f"  T1 model accuracy: {t1_model.score(t1_features, t1_outcomes, sample_weight=step0_weights):.3f}")

# T2 transition model: P(DTP3 | state, action)
t2_features = np.column_stack([step1_states_arr, np.eye(N_ACTIONS)[step1_actions]])
t2_model = GradientBoostingClassifier(
    n_estimators=100, max_depth=6, learning_rate=0.1,
    min_samples_leaf=10, random_state=42
)
t2_model.fit(t2_features, t2_outcomes, sample_weight=step1_weights)
print(f"  T2 model accuracy: {t2_model.score(t2_features, t2_outcomes, sample_weight=step1_weights):.3f}")


def simulate_scenario(name, action_fn_t1, action_fn_t2, states_t1, states_t2,
                      n_pop, n_bootstrap, rng=None):
    """
    Run microsimulation for a given action assignment policy.

    action_fn_t1(states, indices) → array of actions for T1
    action_fn_t2(states, indices) → array of actions for T2
    """
    if rng is None:
        rng = np.random.RandomState(42)

    bootstrap_results = []

    for b in range(n_bootstrap):
        # Sample synthetic population
        idx_t1 = rng.choice(len(states_t1), size=n_pop, replace=True,
                            p=step0_weights / step0_weights.sum())
        pop_states_t1 = states_t1[idx_t1]
        pop_wealth = pop_states_t1[:, wealth_idx]

        # Assign T1 actions
        actions_t1 = action_fn_t1(pop_states_t1, idx_t1)

        # Simulate T1 outcomes
        features_t1 = np.column_stack([pop_states_t1, np.eye(N_ACTIONS)[actions_t1]])
        p_dtp2 = t1_model.predict_proba(features_t1)[:, 1]

        # Apply effect size adjustment (multiplicative on baseline probability)
        for a in range(N_ACTIONS):
            mask = actions_t1 == a
            if mask.any():
                boost = EFFECT_SIZES[a]['central']
                # Additive boost capped at 1.0
                p_dtp2[mask] = np.minimum(p_dtp2[mask] + boost, 1.0)

        received_dtp2 = (rng.random(n_pop) < p_dtp2).astype(int)

        # T2: among those who received DTP2
        dtp2_mask = received_dtp2 == 1
        n_dtp2 = dtp2_mask.sum()

        if n_dtp2 > 0:
            # Map to step1 states (approximate: use corresponding step1 if available)
            # For simplicity, use the same base states with updated dynamic features
            pop_states_t2 = pop_states_t1[dtp2_mask].copy()
            # Update dynamic features
            doses_idx = FEATURE_NAMES.index('doses_received')
            step_idx = FEATURE_NAMES.index('dose_step')
            pop_states_t2[:, doses_idx] = 2  # received DTP2
            pop_states_t2[:, step_idx] = 1

            actions_t2 = action_fn_t2(pop_states_t2, np.where(dtp2_mask)[0])
            features_t2 = np.column_stack([pop_states_t2, np.eye(N_ACTIONS)[actions_t2]])
            p_dtp3 = t2_model.predict_proba(features_t2)[:, 1]

            for a in range(N_ACTIONS):
                mask = actions_t2 == a
                if mask.any():
                    boost = EFFECT_SIZES[a]['central']
                    p_dtp3[mask] = np.minimum(p_dtp3[mask] + boost, 1.0)

            received_dtp3 = (rng.random(n_dtp2) < p_dtp3).astype(int)
        else:
            received_dtp3 = np.array([])

        # Compute outcomes
        dtp3_completed = np.zeros(n_pop)
        if n_dtp2 > 0:
            dtp3_completed[dtp2_mask] = received_dtp3

        completion_rate = dtp3_completed.mean()

        # Cost
        total_cost_t1 = sum(ACTION_COSTS[a] for a in actions_t1)
        total_cost_t2 = sum(ACTION_COSTS[actions_t2[j]] for j in range(len(actions_t2))) if n_dtp2 > 0 else 0
        total_cost = total_cost_t1 + total_cost_t2
        cost_per_child = total_cost / n_pop

        # Equity: poorest quintile (wealth==1) vs richest (wealth==5)
        poorest_mask = pop_wealth <= 1
        richest_mask = pop_wealth >= 5
        # Handle case where quintile boundaries differ
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
        'dtp3_rate_mean': results_df['completion_rate'].mean(),
        'dtp3_rate_ci_low': results_df['completion_rate'].quantile(0.025),
        'dtp3_rate_ci_high': results_df['completion_rate'].quantile(0.975),
        'dtp2_rate_mean': results_df['dtp2_rate'].mean(),
        'cost_per_child_mean': results_df['cost_per_child'].mean(),
        'cost_total_mean': results_df['cost_total'].mean(),
        'equity_gap_mean': results_df['equity_gap'].mean(),
        'equity_gap_ci_low': results_df['equity_gap'].quantile(0.025),
        'equity_gap_ci_high': results_df['equity_gap'].quantile(0.975),
        'rate_poorest_mean': results_df['rate_poorest'].mean(),
        'rate_richest_mean': results_df['rate_richest'].mean(),
    }
    return summary, results_df


# --- 3.2 Define 6 Scenarios ---

# S0: Status quo (behaviour policy — use observed actions)
def s0_action_t1(states, indices):
    return step0_actions[indices % len(step0_actions)]
def s0_action_t2(states, indices):
    return step1_actions[indices % len(step1_actions)]

# S1: Uniform SMS (a₁ for all)
def s1_action(states, indices):
    return np.ones(len(states), dtype=int)

# S2: Uniform CHW (a₂ for all)
def s2_action(states, indices):
    return np.full(len(states), 2, dtype=int)

# S3: Risk-targeted (top 30% risk → a₂, rest → a₁)
# Use CQL Q-values to identify risk: lower Q(s, a0) = higher risk
q_all_step0 = cql_model.predict_all(step0_states)
risk_scores = -q_all_step0[:, 0]  # negative Q(s, a0) as risk proxy
risk_threshold = np.percentile(risk_scores, 70)  # top 30%

def s3_action(states, indices):
    q_vals = cql_model.predict_all(states)
    risk = -q_vals[:, 0]
    actions = np.where(risk >= risk_threshold, 2, 1)  # CHW for high-risk, SMS for rest
    return actions

# S4: RL-optimised (π* from CQL)
def s4_action(states, indices):
    return cql_model.predict_action(states)

# S5: Bandit-allocated (community-level action from LinUCB)
# Pre-compute cluster → bandit action mapping (O(1) lookup)
_cluster_to_bandit = {}
for i in range(len(community_df)):
    x = X_context_scaled[i]
    arm, _ = primary_bandit.select_arm(x)
    cluster_id = str(int(community_df.iloc[i]['v021']))
    _cluster_to_bandit[cluster_id] = arm

# Pre-compute child index → cluster_id string for fast lookup
_idx_to_cluster = np.array([cid.split('_')[0] for cid in step0_child_ids])

def s5_action(states, indices):
    cluster_ids = _idx_to_cluster[indices % len(_idx_to_cluster)]
    return np.array([_cluster_to_bandit.get(c, 1) for c in cluster_ids], dtype=int)

# --- 3.3 Run All Scenarios ---
scenarios = [
    ("S0: Status Quo", s0_action_t1, s0_action_t2),
    ("S1: Uniform SMS", s1_action, s1_action),
    ("S2: Uniform CHW", s2_action, s2_action),
    ("S3: Risk-Targeted", s3_action, s3_action),
    ("S4: RL-Optimised", s4_action, s4_action),
    ("S5: Bandit-Allocated", s5_action, s5_action),
]

print(f"\nRunning {len(scenarios)} scenarios × {N_BOOTSTRAP} bootstrap iterations...")
all_results = {}
all_bootstrap = {}
rng = np.random.RandomState(42)

for name, fn_t1, fn_t2 in scenarios:
    print(f"\n  {name}...")
    summary, boot_df = simulate_scenario(
        name, fn_t1, fn_t2, step0_states, step1_states_arr,
        N_POP, N_BOOTSTRAP, rng
    )
    all_results[name] = summary
    all_bootstrap[name] = boot_df
    print(f"    DTP3 rate: {summary['dtp3_rate_mean']:.3f} "
          f"[{summary['dtp3_rate_ci_low']:.3f}, {summary['dtp3_rate_ci_high']:.3f}]")
    print(f"    Cost/child: ₦{summary['cost_per_child_mean']:,.0f}")
    print(f"    Equity gap: {summary['equity_gap_mean']:.3f} "
          f"[{summary['equity_gap_ci_low']:.3f}, {summary['equity_gap_ci_high']:.3f}]")

# --- ICER Computation ---
print("\n--- Incremental Cost-Effectiveness Ratios (ICER) ---")
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
    print(f"  {name}: ΔDTP3={delta_effect:+.3f}, ΔCost=₦{delta_cost:+,.0f}, "
          f"ICER=₦{icer:,.0f}/additional completion")

# Equity constraint check
print("\n--- Equity Constraint Check ---")
s0_gap = s0['equity_gap_mean']
print(f"  S0 equity gap (richest - poorest): {s0_gap:.3f}")
for name, res in all_results.items():
    gap = res['equity_gap_mean']
    widens = gap > s0_gap
    status = "❌ WIDENS GAP" if widens else "✓ Does not widen gap"
    print(f"  {name}: gap={gap:.3f} {status}")

# ── Save Results ──
results_df = pd.DataFrame(all_results.values())
results_df.to_csv(OUT / "microsim_results.csv", index=False)

# Save detailed bootstrap results
for name, boot_df in all_bootstrap.items():
    safe_name = name.lower().replace(" ", "_").replace(":", "").replace("-", "_")
    boot_df.to_csv(OUT / f"bootstrap_{safe_name}.csv", index=False)

with open(OUT / "microsim_results.json", "w") as f:
    json.dump(all_results, f, indent=2, default=str)

# ── Publication-Quality Figures ──

# Figure 1: DTP3 completion rates by scenario
fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# Panel A: DTP3 completion rates
ax = axes[0, 0]
scenario_names = [r['scenario'] for r in all_results.values()]
short_names = ['S0:\nStatus Quo', 'S1:\nSMS', 'S2:\nCHW', 'S3:\nRisk-\nTargeted',
               'S4:\nRL-\nOptimised', 'S5:\nBandit']
means = [r['dtp3_rate_mean'] for r in all_results.values()]
ci_low = [r['dtp3_rate_ci_low'] for r in all_results.values()]
ci_high = [r['dtp3_rate_ci_high'] for r in all_results.values()]
errors = [[m - l for m, l in zip(means, ci_low)],
          [h - m for m, h in zip(means, ci_high)]]
colors = ['#90A4AE', '#81C784', '#4FC3F7', '#FFB74D', '#E91E63', '#9C27B0']
bars = ax.bar(short_names, means, yerr=errors, capsize=4,
              color=colors, edgecolor='black', linewidth=0.5)
ax.set_ylabel('DTP3 Completion Rate')
ax.set_title('A. DTP3 Completion by Scenario')
ax.axhline(y=means[0], color='grey', linestyle='--', alpha=0.5)
for bar, val in zip(bars, means):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
            f'{val:.3f}', ha='center', va='bottom', fontsize=9)

# Panel B: Cost per child
ax = axes[0, 1]
costs = [r['cost_per_child_mean'] for r in all_results.values()]
bars = ax.bar(short_names, costs, color=colors, edgecolor='black', linewidth=0.5)
ax.set_ylabel('Cost per Child (₦)')
ax.set_title('B. Cost per Child by Scenario')
for bar, val in zip(bars, costs):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 10,
            f'₦{val:,.0f}', ha='center', va='bottom', fontsize=8)

# Panel C: Equity gap (richest - poorest)
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
ax.axhline(y=gaps[0], color='grey', linestyle='--', alpha=0.5, label='Status quo gap')
ax.legend()

# Panel D: ICER efficiency frontier
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

# Figure 2: Bootstrap distributions
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
    "microsim_n_pop": N_POP,
    "microsim_n_bootstrap": N_BOOTSTRAP,
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
}
with open(OUT / "stage3_summary.json", "w") as f:
    json.dump(stage3_summary, f, indent=2, default=str)

print("\n" + "=" * 60)
print("STAGE 3 COMPLETE")
print("=" * 60)

# Find best scenario
best = max(
    [(name, r) for name, r in all_results.items() if name != "S0: Status Quo"],
    key=lambda x: x[1]['dtp3_rate_mean']
)
print(f"Best scenario: {best[0]}")
print(f"  DTP3 rate: {best[1]['dtp3_rate_mean']:.3f} vs S0: {s0['dtp3_rate_mean']:.3f}")
print(f"  Improvement: {best[1]['dtp3_rate_mean'] - s0['dtp3_rate_mean']:.3f}")
print(f"Outputs: {OUT}")
