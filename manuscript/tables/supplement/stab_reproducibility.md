**Table S2.2. Reproducibility parameters: software versions, seeds, cross-validation configuration, model hyperparameters.**

| Component            | Value                          |
|:---------------------|:-------------------------------|
| Python               | 3.13.9                         |
| numpy                | 2.3.5                          |
| pandas               | 2.3.3                          |
| xgboost              | 3.2.0                          |
| scikit-learn         | not installed                  |
| shap                 | 0.51.0                         |
| matplotlib           | 3.10.6                         |
| geopandas            | 1.1.3                          |
| statsmodels          | 0.14.5                         |
| Random seed          | 42                             |
| CV folds             | 5 (stratified)                 |
| bootstrap iterations | 1,000                          |
| PSA iterations       | 1,000                          |
| XGBoost n_estimators | 500                            |
| XGBoost max_depth    | 6                              |
| FQI iterations       | 100                            |
| CQL α                | 1.0 (base)                     |
| Repo commit          | see docs/pipeline_audit_log.md |
