# Recalibration Log

**Date**: 2026-04-06
**Method**: Isotonic regression (sklearn.isotonic.IsotonicRegression)
**Approach**: 5-fold cluster-robust CV out-of-fold predictions → fit isotonic → evaluate

## Model T1
- N = 3,194, prevalence = 0.0401

| Metric | Original | Recalibrated |
|--------|----------|--------------|
| Calibration slope | 0.8736 | 0.9591 |
| Calibration intercept | -0.6613 | -0.0650 |
| Brier score | 0.0358 | 0.0319 |
| Reliability | 0.0031 | 0.0000 |

## Model T2
- N = 3,023, prevalence = 0.0394

| Metric | Original | Recalibrated |
|--------|----------|--------------|
| Calibration slope | 1.5955 | 0.9690 |
| Calibration intercept | 0.7245 | -0.1041 |
| Brier score | 0.0274 | 0.0255 |
| Reliability | 0.0011 | 0.0000 |

## Trajectory Dataset
- Total rows: 6,217
- Unique children: 3,138
- Actions changed from previous export: 0
- Note: Behaviour policy actions are inferred from observed DHS data (intervals, fieldworker visits, card presence), not from model predictions. The trajectory structure is unchanged; the calibration fix affects model risk predictions used downstream by the RL agent.

## Files Updated
- `outputs/stage1/xgb_results_summary.json` — recalibrated metrics added
- `outputs/stage1/isotonic_calibrator_t1.pkl` — T1 calibrator
- `outputs/stage1/isotonic_calibrator_t2.pkl` — T2 calibrator
- `outputs/stage1/calibration_model_t1_recalibrated.pdf` — T1 before/after figure
- `outputs/stage1/calibration_model_t2_recalibrated.pdf` — T2 before/after figure
- `data/processed/trajectory_dataset.csv` — re-exported
- `outputs/stage1/trajectory_dataset.csv` — re-exported
