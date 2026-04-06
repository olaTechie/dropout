# ML Validation Recommendations for Downstream Agents

Based on systematic literature review of current best practices (2024-2025).

---

## 1. XGBoost Model Validation

### Discrimination Metrics
- **AUC-ROC** with 95% CI via bootstrapping (1000+ resamples)
- **DeLong test** for comparing AUC between models (e.g., XGBoost vs logistic regression baseline)
  - R: `pROC::roc.test()`; Python: `scipy` + manual implementation or `delong_roc_test`
  - Report: AUC difference, 95% CI, p-value
- **AUC-PR** (Precision-Recall) — essential when outcome prevalence < 20% (dropout ~28% in Nigeria, so AUC-ROC is acceptable but AUC-PR adds value)

### Calibration Metrics (CRITICAL — vastly under-reported)
- **Calibration curve** (reliability diagram): Plot observed vs predicted probabilities in decile bins
  - Use Loess smoothing for continuous calibration assessment
  - Include histogram of predicted probabilities below the calibration plot
- **Brier score**: Mean squared error of probabilistic predictions
  - Decompose into: discrimination + calibration + uncertainty components (Spiegelhalter decomposition)
  - Report Brier score for both train and test sets
  - Note: lower is better; Brier includes both discrimination and calibration
- **Calibration slope and intercept** (Cox recalibration):
  - Slope = 1, Intercept = 0 indicates perfect calibration
  - Slope < 1 → overfitting; Slope > 1 → underfitting
- **Expected Calibration Error (ECE)**: Mean absolute difference between predicted and observed across bins
- **Integrated Calibration Index (ICI)**: Loess-based; more robust than ECE to binning choices
- **Hosmer-Lemeshow test**: Report but note limitations with large samples (overpowered)

### Calibration Correction
- If XGBoost probabilities are miscalibrated: apply **isotonic regression** (preferred over Platt scaling for tree-based models)
- Assess baseline calibration BEFORE applying correction — correction can worsen already-calibrated models
- Use **cross-validated calibration**: fit calibrator on training fold, evaluate on held-out fold

### Cross-Validation Strategy
- **Stratified 5-fold or 10-fold CV** preserving outcome prevalence
- Account for survey design: stratify folds by v022 (strata) where possible
- Report mean ± SD across folds for all metrics
- Consider **spatial cross-validation** (hold out entire clusters/states) to assess geographic generalisability

### Decision Curve Analysis (DCA)
- Plot net benefit curves across threshold probabilities
- Compare XGBoost against "treat all" and "treat none" strategies
- Identifies clinically useful range of the model

---

## 2. Offline RL Evaluation Metrics

### Primary: Fitted Q Evaluation (FQE)
- **Gold standard** for OPE in healthcare (Raghu et al. 2022)
- Spearman's rho = 0.89 for policy ranking quality
- Train separate Q-function on validation data for each candidate policy
- Hyperparameter: evaluation horizon H ≥ 10

### Screening: Weighted Importance Sampling (WIS)
- Use as **first-stage filter** before FQE (computationally cheaper)
- Apply **policy softening** (epsilon = 0.1) to reduce variance
- Avoid pure IS for deterministic policies (zero-weight problem)

### Recommended Two-Stage Approach
1. **Stage 1**: WIS to identify top quartile of candidate policies
2. **Stage 2**: FQE for final ranking of pruned candidates
3. This achieves comparable regret to full FQE at lower computational cost

### Methods to AVOID
- **WDR (Weighted Doubly Robust)**: Theoretically appealing but worse than WIS or FQE in practice — amplifies constituent estimation errors
- **Training Q-values or TD errors** as policy evaluation proxies: poor ranking quality (rho < 0.3)

### Additional Evaluation Approaches
- **Approximate Model (AM)**: Use only when computational resources are extremely limited; tends to underestimate policy value (rho = 0.66)
- **Per-decision IS**: Reduces variance vs trajectory IS but still high-variance for long horizons
- **Doubly Robust (DR)**: Standard DR combines IS + DM; useful but WDR variant should be avoided

### Validation Data Requirements
- Split observational data 50/50 for training/validation
- Minimum 1000 episodes (trajectories) in validation set
- Pre-specify all OPE hyperparameters — do NOT tune on validation data

### Safety Evaluation
- Track **out-of-distribution (OOD) action frequency**: how often does the learned policy recommend actions never seen in data for a given state?
- Report **CQL penalty magnitude**: larger penalties indicate more conservative (safer) policies
- Compare learned policy value against **behaviour policy value** (clinician baseline)
- Report **per-action frequency** of learned vs behaviour policy

---

## 3. SHAP Interpretation Standards

### Pre-requisites
- SHAP analysis should ONLY be performed AFTER model demonstrates adequate performance (discrimination + calibration)
- Address feature correlations before interpretation — highly correlated features can produce unstable SHAP values

### Required Plots (Minimum Set)
1. **Global bar plot**: Mean |SHAP| values for top 15-20 features → overall feature importance ranking
2. **Beeswarm plot**: SHAP values colored by feature value → shows direction of effects and non-linearities
3. **Top 5-8 individual scatter plots**: SHAP vs feature value for key predictors → reveals non-linear dose-response
4. **Waterfall plot**: For 2-3 selected individual cases → demonstrates model reasoning for specific predictions

### Andersen Model Decomposition
- Aggregate SHAP values by Andersen domain (Predisposing, Enabling, Need, Dynamic/Temporal)
- Report mean absolute SHAP contribution per domain
- This provides the theoretical-framework-level interpretation required for the paper

### Reporting Standards
- Report SHAP values from the **test set** (not training set)
- Specify whether explaining **predicted probabilities** or **log-odds** (probability scale preferred for clinical interpretability)
- Show SHAP distributions across **cross-validation folds** to demonstrate stability
- Acknowledge: "SHAP quantifies feature importance TO THE MODEL, not causal importance in the real world"

### Common Pitfalls to Avoid
- Do NOT interpret SHAP as causal effects
- Do NOT over-interpret in sparse data regions (check sample density)
- Do NOT aggregate SHAP across time points without explicit justification
- For binary classification: choose probability vs log-odds scale and be consistent throughout

### Interaction Detection
- Use SHAP scatter plots colored by second variable to identify interactions
- Wide vertical spread at fixed feature values → interaction effect
- Confirm interactions are stable across CV folds before reporting

---

## 4. Survey-Weighted ML Validation

### Special Considerations for DHS Data
- Apply survey weights (v005/1e6) in all performance calculations
- Use **survey-weighted Brier score**: weighted mean of squared errors
- Bootstrap CIs should use **survey-aware bootstrap** (resample PSUs within strata)
- Report **design-effect adjusted** sample sizes where relevant

### Cluster-Robust Evaluation
- DHS data has clustering (v021 = PSU) — observations within clusters are correlated
- Prefer **cluster-level cross-validation**: hold out entire clusters rather than individual observations
- This gives a more realistic estimate of model performance on new geographic areas

---

## Summary Checklist for Downstream ML Agent

### XGBoost Validation Minimum Requirements:
- [ ] AUC-ROC with 95% CI (bootstrap)
- [ ] AUC-PR
- [ ] DeLong test vs baseline model
- [ ] Calibration curve (Loess-smoothed) with histogram
- [ ] Brier score (with decomposition)
- [ ] Calibration slope and intercept
- [ ] Stratified k-fold CV (k=5 or 10)
- [ ] Survey weights applied in all metrics
- [ ] Decision curve analysis

### SHAP Interpretation Minimum Requirements:
- [ ] Global bar plot (top 15-20 features)
- [ ] Beeswarm plot
- [ ] Individual scatter plots (top 5-8 features)
- [ ] Waterfall plots (2-3 cases)
- [ ] Andersen domain decomposition
- [ ] Test set SHAP values only
- [ ] Cross-fold stability check

### Offline RL Evaluation Minimum Requirements:
- [ ] FQE (primary) with H ≥ 10
- [ ] WIS (screening) with epsilon = 0.1
- [ ] Two-stage selection approach
- [ ] OOD action frequency tracking
- [ ] Behaviour policy comparison
- [ ] Validation set ≥ 1000 episodes
- [ ] Pre-specified hyperparameters

---

## Key References

1. Van Calster B, et al. (2019). Calibration: the Achilles heel of predictive analytics. *BMC Medicine*, 17, 230.
2. Steyerberg EW, Vergouwe Y (2014). Towards better clinical prediction models: seven steps for development and an ABCD for validation. *Eur Heart J*, 35(29), 1925-1931.
3. Ponce-Bobadilla AV, et al. (2024). Practical guide to SHAP analysis. *Clinical and Translational Science*, 17(11), e70056.
4. Raghu A, et al. (2022). Model Selection for Offline RL: Practical Considerations for Healthcare Settings. *MLHC 2022*.
5. Huang Y, et al. (2020). A tutorial on calibration measurements and calibration models for clinical prediction models. *JAMIA*, 27(4), 621-633.
6. Alba AC, et al. (2017). Discrimination and calibration of clinical prediction models. *JAMA*, 318(14), 1377-1384.
7. Van Calster B, et al. (2023). Weighted Brier Score for risk prediction models with clinical utility consideration. *Statistics in Medicine*.
