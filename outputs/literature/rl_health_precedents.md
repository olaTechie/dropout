# Reinforcement Learning in Health: Precedents and Novelty Assessment

## Novelty Check: Has Offline RL Been Applied to Vaccination Dropout?

**Finding: NO direct precedent found.** After systematic searching across PubMed, Google Scholar, medRxiv, and bioRxiv, no study was identified that applies offline reinforcement learning specifically to vaccination dropout prevention or sequential childhood immunisation decision-making.

### What Exists

RL has been applied to:
1. **Epidemic control / vaccine allocation** — optimising population-level vaccine distribution during outbreaks (COVID-19, influenza), but NOT individual-level dose completion
2. **Clinical treatment optimisation** — sepsis management, mechanical ventilation, medication dosing
3. **Vaccination campaign logistics** — resource allocation for mass vaccination, not individual retention

### Gap Confirmed
The application of offline RL (specifically FQI + CQL) to individual-level DTP vaccination dropout prevention using DHS observational data represents a **novel contribution**.

---

## RL in Health: Key Precedents

### 1. Offline RL for Clinical Decision-Making

| Study | Year | Method | Domain | Key Finding |
|-------|------|--------|--------|-------------|
| Raghu et al. | 2017 | DQN, Dueling DQN | Sepsis treatment | RL policies reduced estimated mortality vs clinician policies |
| Komorowski et al. | 2018 | FQI | Sepsis (MIMIC-III) | AI Clinician: optimal IV fluid/vasopressor dosing |
| Wang et al. | 2025 | K-CQL | Mechanical ventilation | CQL-based ventilator management with ABG integration |
| Chen et al. | 2025 | OGSRL | General treatment | Offline guarded safe RL addressing OOD risks |
| Li et al. | 2025 | CQL | Sepsis | Offline safe RL with sparse rewards for sepsis |
| Nambiar et al. | 2025 | PROP-RL | Loop diuretics | Practical pipeline for offline RL in clinical workflow |
| Raghu et al. | 2022 | Various OPE | Healthcare model selection | Two-stage WIS→FQE approach for policy selection |

### 2. RL for Epidemic/Vaccination Control

| Study | Year | Method | Domain | Key Finding |
|-------|------|--------|--------|-------------|
| Yechezkel et al. | 2023 | PPO | COVID-19 vaccine allocation | Multi-city dynamic allocation reduced peak infections by 8% |
| Li et al. | 2025 | RL | COVID-19 interventions | Optimised NPI timing using UK data |
| Ohi et al. | 2025 | RL survey | Epidemic control | Comprehensive review of RL for infectious disease control |

### 3. Dynamic Treatment Regimes (DTR) — Methodological Precedents

| Study | Year | Method | Relevance |
|-------|------|--------|-----------|
| Chakraborty & Moodie | 2013 | Book: Statistical Methods for DTRs | Foundational text linking RL, causal inference, personalized medicine |
| Tsiatis et al. | 2020 | DTR textbook | Comprehensive DTR methodology with observational data |
| Zhang et al. | 2025 | Systematic review | DTRs using observational healthcare data; methods include Q-learning, A-learning, g-estimation |
| Luckett et al. | 2020 | V-learning | DTR estimation robust to model misspecification |

### Key DTR Findings
- DTRs have been applied extensively in **oncology, psychiatry, substance abuse, HIV** — but NOT childhood vaccination
- Observational data methods require: **exchangeability, consistency, positivity** assumptions
- Q-learning and A-learning are dominant estimation approaches
- **No vaccination/immunisation DTR study was found** — confirming novelty

---

## Methodological Implications for Our Study

### FQI + CQL Choice Justification
1. **FQI** is the foundational batch RL method (Komorowski et al. 2018 "AI Clinician" used FQI for sepsis)
2. **CQL** (Kumar et al. 2020) addresses the overestimation problem in offline RL by penalising Q-values for OOD actions — critical for healthcare safety
3. The combination is well-validated in clinical domains but novel for vaccination

### OPE Evaluation Strategy (from Raghu et al. 2022)
- **Primary**: FQE (Fitted Q Evaluation) — best ranking quality (Spearman's rho = 0.89)
- **Screening**: WIS (Weighted Importance Sampling) with policy softening (epsilon = 0.01)
- **Avoid**: WDR (Weighted Doubly Robust) — worse than simpler methods in practice
- **Two-stage approach**: WIS to prune candidates → FQE for final selection

### Safety Considerations
- OOD actions are the primary risk (Chen et al. 2025)
- CQL's conservative value estimation provides a natural safety margin
- Behaviour policy must be carefully estimated (DHS proxy inference adds uncertainty)

---

## Key References

1. Komorowski M, et al. (2018). The Artificial Intelligence Clinician learns optimal treatment strategies for sepsis. *Nature Medicine*, 24, 1716-1720.
2. Kumar A, et al. (2020). Conservative Q-Learning for Offline Reinforcement Learning. *NeurIPS 2020*.
3. Raghu A, et al. (2022). Model Selection for Offline RL: Practical Considerations for Healthcare Settings. *MLHC 2022*.
4. Chen et al. (2025). Offline Guarded Safe RL for Medical Treatment Optimization. *arXiv:2505.16242*.
5. Chakraborty B, Moodie EEM (2013). *Statistical Methods for Dynamic Treatment Regimes*. Springer.
6. Zhang et al. (2025). Methods in DTRs using observational healthcare data: A systematic review. *Computer Methods and Programs in Biomedicine*.
