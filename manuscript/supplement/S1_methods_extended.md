# Supplementary Material S1 — Extended Methods

## S1.1 Fitted Q-Iteration (FQI)

Fitted Q-Iteration (FQI) is a batch offline reinforcement learning algorithm that learns an action-value function Q(s, a) from a fixed dataset of transitions without further environment interaction [@ref12_ernst2005treebased]. Starting from Q₀(s, a) = 0, FQI iterates Bellman backup targets: at each iteration k, the Bellman target for each observed transition (s_i, a_i, r_i, s'_i) is computed as target_i = r_i + γ · max_{a'} Q_{k−1}(s'_i, a'), and Q_k is fitted by regressing a function approximator on these targets. We used ExtraTrees as the function approximator, which provides stable regression under sparse and noisy off-policy data, handles mixed variable types without preprocessing, and is computationally efficient for datasets of the size derived from the NDHS 2024 DTP1-initiating cohort (6,217 trajectory rows). Convergence was declared when the maximum change in Q-values across all observed (s, a) pairs fell below ΔQ < 0.01 or 200 iterations were completed (actual convergence at 100 iterations; Table S2.2).

```text
Input:  dataset D = {(s_i, a_i, r_i, s'_i)},
        max iterations N, function class F, discount γ, threshold ε
Initialize Q_0(s, a) = 0  ∀(s, a)
for k = 1 to N do
    for each (s_i, a_i, r_i, s'_i) in D do
        target_i ← r_i + γ · max_{a'} Q_{k-1}(s'_i, a')
    end for
    Q_k ← argmin_{f ∈ F} Σ_i (f(s_i, a_i) − target_i)²
    if max_{(s,a)} |Q_k(s,a) − Q_{k-1}(s,a)| < ε then
        break
    end if
end for
Return Q_N
Derive policy: π*(s) = argmax_{a} Q_N(s, a)
```

---

## S1.2 Conservative Q-Learning (CQL)

Conservative Q-Learning (CQL) is an offline RL algorithm designed to address distributional shift: the risk that a Q-function trained on historical data assigns spuriously high values to state–action pairs that were rarely or never observed under the behaviour policy [@ref13_kumar2020conservative]. CQL augments the standard Bellman error with a conservative regularisation term that penalises the soft-maximum of Q-values across all actions (which would be inflated in OOD regions) and rewards the Q-value under the behaviour policy (which is supported by data). The conservatism hyperparameter α controls the trade-off between policy optimisation and data-support constraint: larger α pushes the learned policy closer to the behaviour policy, while α→0 recovers standard Q-learning. We grid-searched α ∈ {0.1, 0.5, 1.0, 2.0, 5.0} and selected α=1.0 as the base case; α-sensitivity on WIS-estimated policy value and action diversity is reported in Supplementary Figure S8.

The CQL objective is:

$$
\mathcal{L}_{\text{CQL}}(\theta) = \mathcal{L}_{\text{Bellman}}(\theta) + \alpha \cdot \mathbb{E}_{s \sim \mathcal{D}}\!\left[\log \sum_{a} \exp Q_\theta(s,a) - \mathbb{E}_{a \sim \hat{\pi}_\beta(a|s)}\!\left[Q_\theta(s,a)\right]\right]
$$

where $\mathcal{L}_{\text{Bellman}}(\theta)$ is the standard mean-squared Bellman error, $\hat{\pi}_\beta(a|s)$ is the estimated behaviour policy derived from the DHS proxy-action inference rules (§S1.4), and the log-sum-exp term approximates the Q-value of the softmax policy over all actions.

```text
Input:  dataset D, behaviour policy estimate π_β, α, learning rate η, γ
Initialize Q_θ randomly
for each training step t do
    Sample batch B = {(s_i, a_i, r_i, s'_i)} from D
    Compute Bellman targets: y_i ← r_i + γ · max_{a'} Q_θ(s'_i, a')
    L_Bellman ← (1/|B|) Σ_i (Q_θ(s_i, a_i) − y_i)²
    L_CQL ← (1/|B|) Σ_i [log Σ_{a} exp Q_θ(s_i, a)
                           − Σ_{a} π_β(a|s_i) · Q_θ(s_i, a)]
    L_total ← L_Bellman + α · L_CQL
    θ ← θ − η · ∇_θ L_total
end for
Return π*(s) = argmax_{a} Q_θ(s, a)
```

---

## S1.3 Off-Policy Evaluation Estimators

Off-policy evaluation (OPE) estimates the expected return of a learned policy π̂ using data collected under a different behaviour policy π_β, without additional environment interaction. Three estimators were applied to 1,569 held-out trajectory episodes drawn from children not used in policy training.

### Importance Sampling (IS)

IS reweights observed returns by the likelihood ratio between the learned and behaviour policies:

$$
\hat{V}_{\text{IS}}(\hat{\pi}) = \frac{1}{N} \sum_{i=1}^{N} \left(\prod_{t=0}^{T_i} \frac{\hat{\pi}(a_{i,t} \mid s_{i,t})}{\pi_\beta(a_{i,t} \mid s_{i,t})}\right) \sum_{t=0}^{T_i} \gamma^t r_{i,t}
$$

IS is unbiased when the behaviour policy is correctly specified but can have high variance when importance weights are extreme (rare in our two-step horizon).

### Weighted Importance Sampling (WIS)

WIS self-normalises by the sum of per-trajectory importance weights, reducing variance at the cost of introducing bias:

$$
\hat{V}_{\text{WIS}}(\hat{\pi}) = \frac{\sum_{i=1}^{N} w_i \sum_{t=0}^{T_i} \gamma^t r_{i,t}}{\sum_{i=1}^{N} w_i}, \quad w_i = \prod_{t=0}^{T_i} \frac{\hat{\pi}(a_{i,t} \mid s_{i,t})}{\pi_\beta(a_{i,t} \mid s_{i,t})}
$$

### Doubly-Robust (DR)

The DR estimator combines IS with a learned Q-function to reduce variance while maintaining consistency when either the importance weights or the Q-function model is correctly specified [@ref32_jiang2016doubly]:

$$
\hat{V}_{\text{DR}}(\hat{\pi}) = \hat{V}_{\text{IS}} - \frac{1}{N} \sum_{i=1}^{N} \left(\rho_i \hat{Q}(s_i, a_i) - \hat{V}(s_i)\right)
$$

where $\rho_i = \hat{\pi}(a_i \mid s_i) / \pi_\beta(a_i \mid s_i)$ is the per-step importance weight and $\hat{V}(s_i) = \sum_a \hat{\pi}(a \mid s_i) \hat{Q}(s_i, a)$ is the policy value estimate. Agreement across IS, WIS, and DR is presented as the primary evidence for OPE reliability; estimator comparison is shown in Supplementary Figure S9.

---

## S1.4 Behaviour-Policy Inference Rules (full)

The NDHS 2024 does not record which, if any, vaccination-promotion interventions a child's household received. Proxy behaviour-policy actions are therefore inferred from observable DHS patterns according to the following structured rules, grounded in the assumptions stated in §2.5 and CLAUDE.md.

The behaviour policy $\hat{\pi}_\beta(a \mid s)$ is estimated from the inferred action frequencies within clusters (v021), smoothed by a uniform Dirichlet prior to prevent zero probabilities. A complete cross-tabulation of inferred action assignments by zone and dose step is available in the repository at `outputs/stage2/behaviour_policy_summary.csv`.

| DHS condition | Inferred action | Confidence | Rationale |
|---------------|-----------------|------------|-----------|
| Next dose received ≤ 2 weeks after scheduled date AND fieldworker visit (v393 == 1) | a₂: CHW home visit | High | Active outreach most consistent with on-time receipt combined with documented CHW contact |
| Next dose received ≤ 2 weeks after scheduled date AND campaign vaccination (h69 == 41) | a₃: Facility recall / defaulter tracing | High | Campaign-mode vaccination typically involves systematic defaulter tracing |
| Next dose received ≤ 2 weeks after scheduled date AND health card present (h1a ≥ 1) AND no fieldworker visit | a₁: SMS reminder | High | Card possession enables message-driven self-attendance; no active outreach recorded |
| Next dose received 2–4 weeks late | a₁: SMS reminder or a₀: No intervention | Medium | Modest delay consistent with reminder effect or passive follow-up; split 50/50 if no further information |
| Next dose received > 4 weeks late | a₀: No intervention | High | Extended delay inconsistent with effective active intervention |
| Next dose not received (dropout) | a₀: No intervention | Highest | Failure to attend any subsequent appointment indicates absence of effective intervention |
| Any of above AND fieldworker visit (v393 == 1) | Upweight a₂ by factor 2 | Modifier | v393 is the closest available DHS proxy for active CHW outreach |
| Any of above AND health card present (h1a ≥ 1) | Upweight a₁ by factor 1.5 | Modifier | Card possession enables reminder-based attendance |
| Any of above AND campaign vaccination venue (h69 == 41) | Upweight a₃ by factor 2 | Modifier | Campaign venue indicates systematic recall effort |

*Note: Conditional incentive (a₄) is not assigned from DHS proxies because no DHS variable reliably distinguishes incentive-receiving visits from routine attendance. a₄ assignment in the training data is therefore treated as unobserved and excluded from behaviour-policy estimation; this is acknowledged as a limitation.*
