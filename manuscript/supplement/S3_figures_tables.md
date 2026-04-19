# Supplementary Material S3 — Figures and Tables

## S3.1 Supplementary Tables

### Table S1 — Subgroup prediction performance by geopolitical zone

**Table S. Subgroup prediction performance by zone.**

|   group |   predicted |   observed |   absolute_error | flagged   |
|--------:|------------:|-----------:|-----------------:|:----------|
|       3 |       0.891 |      0.862 |            0.028 | False     |
|       2 |       0.886 |      0.832 |            0.055 | True      |
|       1 |       0.878 |      0.804 |            0.074 | True      |
|       6 |       0.945 |      0.870 |            0.075 | True      |
|       5 |       0.960 |      0.914 |            0.046 | True      |
|       4 |       0.943 |      0.859 |            0.084 | True      |

*AUROC and Brier reported with 95 % bootstrap CI.*

Zone codes: 1 = North Central, 2 = North East, 3 = North West, 4 = South East, 5 = South South, 6 = South West (Nigeria DHS geopolitical zone coding). Flagged = absolute error between predicted and observed DTP3 completion > 0.05.

---

### Table S2 — Subgroup prediction performance by state

**Table S. Subgroup prediction performance by state.**

|   group |   predicted |   observed |   absolute_error | flagged   |
|--------:|------------:|-----------:|-----------------:|:----------|
|       1 |       0.752 |      0.750 |            0.002 | False     |
|       2 |       0.815 |      0.756 |            0.059 | True      |
|       3 |       0.946 |      0.892 |            0.054 | True      |
|       4 |       0.973 |      0.946 |            0.026 | False     |
|       5 |       0.874 |      0.864 |            0.010 | False     |
|       6 |       0.805 |      0.618 |            0.188 | True      |
|       7 |       0.911 |      0.842 |            0.070 | True      |
|       8 |       0.943 |      0.911 |            0.033 | True      |
|       9 |       0.917 |      0.920 |            0.003 | False     |
|      10 |       0.838 |      0.817 |            0.021 | False     |
|      11 |       0.907 |      0.897 |            0.009 | False     |
|      12 |       0.839 |      0.779 |            0.060 | True      |
|      13 |       0.828 |      0.828 |            0.001 | False     |
|      14 |       0.959 |      0.915 |            0.044 | True      |
|      15 |       0.906 |      0.862 |            0.044 | True      |
|      16 |       0.816 |      0.713 |            0.103 | True      |
|      17 |       0.925 |      0.854 |            0.072 | True      |
|      18 |       0.856 |      0.667 |            0.189 | True      |
|      19 |       0.945 |      0.869 |            0.076 | True      |
|      20 |       0.887 |      0.767 |            0.119 | True      |
|      21 |       0.939 |      0.759 |            0.180 | True      |
|      22 |       0.859 |      0.782 |            0.077 | True      |
|      23 |       0.932 |      0.835 |            0.097 | True      |
|      24 |       0.894 |      0.835 |            0.058 | True      |
|      25 |       0.949 |      0.872 |            0.076 | True      |
|      26 |       0.954 |      0.927 |            0.026 | False     |
|      27 |       0.984 |      0.939 |            0.044 | True      |
|      28 |       0.916 |      0.793 |            0.123 | True      |
|      29 |       0.979 |      0.972 |            0.007 | False     |
|      30 |       0.932 |      0.856 |            0.077 | True      |
|      31 |       0.954 |      0.835 |            0.118 | True      |
|      32 |       0.967 |      0.891 |            0.075 | True      |
|      33 |       0.984 |      0.912 |            0.071 | True      |
|      34 |       0.948 |      0.909 |            0.039 | True      |
|      35 |       0.962 |      0.948 |            0.015 | False     |
|      36 |       0.967 |      0.917 |            0.051 | True      |
|      37 |       0.967 |      0.940 |            0.027 | False     |

*AUROC and Brier reported with 95 % bootstrap CI.*

Group codes correspond to Nigeria DHS sstate variable values (37 states + FCT). Flagged = absolute error > 0.05.

---

### Table S3 — Subgroup prediction performance by wealth quintile

**Table S. Subgroup prediction performance by wealth quintile.**

|   group |   predicted |   observed |   absolute_error | flagged   |
|--------:|------------:|-----------:|-----------------:|:----------|
|       3 |       0.897 |      0.836 |            0.061 | True      |
|       4 |       0.913 |      0.857 |            0.056 | True      |
|       5 |       0.958 |      0.918 |            0.040 | True      |
|       1 |       0.880 |      0.834 |            0.047 | True      |
|       2 |       0.868 |      0.801 |            0.067 | True      |

*AUROC and Brier reported with 95 % bootstrap CI.*

Wealth quintile codes (DHS v190): 1 = Poorest, 2 = Poorer, 3 = Middle, 4 = Richer, 5 = Richest. All five quintiles flagged, indicating systematic model over-prediction of DTP3 completion across the wealth distribution; this is acknowledged as a calibration limitation in §4.

---

### Table S4 — Subgroup prediction performance by urban/rural residence

**Table S. Subgroup prediction performance by urban rural.**

|   group |   predicted |   observed |   absolute_error | flagged   |
|--------:|------------:|-----------:|-----------------:|:----------|
|       0 |       0.915 |      0.847 |            0.067 | True      |
|       1 |       0.907 |      0.860 |            0.047 | True      |

*AUROC and Brier reported with 95 % bootstrap CI.*

Residence codes (DHS v025): 0 = Urban, 1 = Rural. Both strata flagged.

---

### Table S5 — Subgroup prediction performance by maternal education

**Table S. Subgroup prediction performance by maternal education.**

|   group |   predicted |   observed |   absolute_error | flagged   |
|--------:|------------:|-----------:|-----------------:|:----------|
|       2 |       0.914 |      0.850 |            0.064 | True      |
|       0 |       0.872 |      0.826 |            0.046 | True      |
|       3 |       0.967 |      0.938 |            0.029 | False     |
|       1 |       0.893 |      0.824 |            0.068 | True      |

*AUROC and Brier reported with 95 % bootstrap CI.*

Education codes (DHS v106): 0 = No education, 1 = Primary, 2 = Secondary, 3 = Higher. Group 3 (higher education) is the only stratum not flagged; all other education levels show over-prediction.

---

### Table S6 — RL policy lookup (first 50 of 2,500 states)

**Table S. Example RL policy lookup (first 50 of 2,500 state representations) showing recommended action and Q-values.**

|   child_id |   dose_step |   optimal_action |    q_a0 |   q_a1 |   q_a2 |   q_a3 |   q_a4 |   q_max |   q_advantage |   behaviour_action |   weight |
|-----------:|------------:|-----------------:|--------:|-------:|-------:|-------:|-------:|--------:|--------------:|-------------------:|---------:|
|      2_3_3 |           0 |                0 |  1.6245 | 1.5895 | 1.5808 | 1.1670 | 1.5998 |  1.6245 |        0.0000 |                  0 |   0.7224 |
|      2_3_3 |           1 |                0 |  1.1750 | 1.1646 | 1.1686 | 1.1670 | 1.1262 |  1.1750 |        0.0064 |                  2 |   0.7224 |
|      4_1_1 |           0 |                2 |  1.0048 | 1.5806 | 1.5882 | 1.1670 | 1.5087 |  1.5882 |        0.0076 |                  1 |   1.1799 |
|      4_1_1 |           1 |                3 |  0.1494 | 1.1664 | 1.1649 | 1.1670 | 0.1765 |  1.1670 |        1.0177 |                  0 |   1.1799 |
|     5_19_2 |           0 |                2 |  1.5789 | 1.5849 | 1.5880 | 1.1670 | 1.5746 |  1.5880 |        0.0031 |                  1 |   0.8297 |
|     5_19_2 |           1 |                3 |  1.1247 | 1.1668 | 1.1636 | 1.1670 | 1.1593 |  1.1670 |        0.0002 |                  1 |   0.8297 |
|     5_51_2 |           0 |                2 |  1.5990 | 1.5837 | 1.6000 | 1.1670 | 1.5909 |  1.6000 |        0.0010 |                  0 |   0.8297 |
|     5_51_2 |           1 |                4 |  1.1545 | 1.1714 | 1.1637 | 1.1670 | 1.1809 |  1.1809 |        0.0264 |                  0 |   0.8297 |
|      6_6_2 |           0 |                4 |  1.6041 | 1.6161 | 1.6117 | 1.1670 | 1.6434 |  1.6434 |        0.0273 |                  1 |   0.8401 |
|      6_6_2 |           1 |                4 |  1.0787 | 1.1689 | 1.1665 | 1.1670 | 1.2166 |  1.2166 |        0.0478 |                  1 |   0.8401 |
|     13_7_2 |           0 |                1 |  0.5108 | 1.6146 | 1.5728 | 1.1670 | 1.5230 |  1.6146 |        0.0000 |                  1 |   2.4576 |
|     13_7_2 |           1 |                3 |  0.4913 | 1.1653 | 1.1639 | 1.1670 | 1.1351 |  1.1670 |        0.0000 |                  3 |   2.4576 |
|    13_49_2 |           0 |                1 |  1.5113 | 1.5939 | 1.5928 | 1.1670 | 1.5242 |  1.5939 |        0.0826 |                  0 |   2.4576 |
|    13_49_2 |           1 |                3 |  0.2709 | 1.1665 | 1.1622 | 1.1670 | 0.3706 |  1.1670 |        0.8962 |                  0 |   2.4576 |
|    17_39_2 |           0 |                1 |  0.3793 | 1.5955 | 1.5733 | 1.1670 | 0.6343 |  1.5955 |        1.2162 |                  0 |   1.0105 |
|    20_18_2 |           0 |                2 |  0.3970 | 1.5729 | 1.5782 | 1.1670 | 1.3831 |  1.5782 |        0.0054 |                  1 |   0.4718 |
|    20_18_2 |           1 |                3 | -0.0956 | 1.1625 | 1.1627 | 1.1670 | 0.0142 |  1.1670 |        1.2627 |                  0 |   0.4718 |
|    20_51_2 |           0 |                2 |  0.4214 | 1.5702 | 1.6015 | 1.1670 | 0.5886 |  1.6015 |        1.1800 |                  0 |   0.4718 |
|   21_140_2 |           0 |                0 |  1.7700 | 1.5912 | 1.5811 | 1.1670 | 1.6070 |  1.7700 |        0.1788 |                  1 |   1.6438 |
|   21_140_2 |           1 |                0 |  1.2087 | 1.1671 | 1.1658 | 1.1670 | 1.1903 |  1.2087 |        0.0000 |                  0 |   1.6438 |
|   21_145_7 |           0 |                0 |  1.6372 | 1.5845 | 1.5842 | 1.1670 | 1.5963 |  1.6372 |        0.0527 |                  1 |   1.6438 |
|   21_145_7 |           1 |                0 |  1.1804 | 1.1658 | 1.1678 | 1.1670 | 1.1664 |  1.1804 |        0.0000 |                  0 |   1.6438 |
|   21_153_9 |           0 |                0 |  1.6146 | 1.5852 | 1.5865 | 1.1670 | 1.5930 |  1.6146 |        0.0000 |                  0 |   1.6438 |
|   21_153_9 |           1 |                3 |  1.0679 | 1.1650 | 1.1640 | 1.1670 | 1.1408 |  1.1670 |        0.0020 |                  1 |   1.6438 |
|    23_13_2 |           0 |                2 |  1.5882 | 1.5839 | 1.5904 | 1.1670 | 1.5846 |  1.5904 |        0.0066 |                  1 |   0.8111 |
|    23_13_2 |           1 |                0 |  1.1967 | 1.1657 | 1.1683 | 1.1670 | 1.1543 |  1.1967 |        0.0309 |                  1 |   0.8111 |
|    23_31_3 |           0 |                0 |  1.6463 | 1.5888 | 1.5758 | 1.1670 | 1.6014 |  1.6463 |        0.0575 |                  1 |   0.8111 |
|    23_31_3 |           1 |                0 |  1.2372 | 1.1668 | 1.1705 | 1.1670 | 1.1821 |  1.2372 |        0.0704 |                  1 |   0.8111 |
|    23_73_2 |           0 |                2 |  0.9211 | 1.5800 | 1.5876 | 1.1670 | 1.5570 |  1.5876 |        0.0076 |                  1 |   0.8111 |
|    23_73_2 |           1 |                3 |  0.7303 | 1.1660 | 1.1659 | 1.1670 | 1.1268 |  1.1670 |        0.0010 |                  1 |   0.8111 |
|     27_1_2 |           0 |                0 |  1.6142 | 1.5884 | 1.5863 | 1.1670 | 1.5770 |  1.6142 |        0.0000 |                  0 |   0.5041 |
|     27_1_2 |           1 |                4 |  1.1210 | 1.1667 | 1.1690 | 1.1670 | 1.1741 |  1.1741 |        0.0075 |                  1 |   0.5041 |
|    27_23_2 |           0 |                4 |  1.5933 | 1.5969 | 1.5996 | 1.1670 | 1.6090 |  1.6090 |        0.0121 |                  1 |   0.5041 |
|    27_23_2 |           1 |                0 |  1.1723 | 1.1690 | 1.1666 | 1.1670 | 1.1620 |  1.1723 |        0.0033 |                  1 |   0.5041 |
|    27_49_2 |           0 |                0 |  1.6120 | 1.6061 | 1.6077 | 1.1670 | 1.5909 |  1.6120 |        0.0059 |                  1 |   0.5041 |
|    27_49_2 |           1 |                0 |  1.2338 | 1.1710 | 1.1712 | 1.1670 | 1.1965 |  1.2338 |        0.0628 |                  1 |   0.5041 |
|    29_21_3 |           0 |                1 |  0.7068 | 1.5935 | 1.5687 | 1.1670 | 0.8714 |  1.5935 |        0.8867 |                  0 |   0.7256 |
|    29_21_3 |           1 |                1 |  0.1918 | 1.1707 | 1.1661 | 1.1670 | 0.0682 |  1.1707 |        0.9788 |                  0 |   0.7256 |
|    30_36_2 |           0 |                4 |  0.9819 | 1.5856 | 1.5931 | 1.1670 | 1.6042 |  1.6042 |        0.0186 |                  1 |   0.9751 |
|    30_36_2 |           1 |                4 |  0.7195 | 1.1672 | 1.1623 | 1.1670 | 1.1824 |  1.1824 |        0.0152 |                  1 |   0.9751 |
|    33_57_2 |           0 |                1 |  0.6788 | 1.5971 | 1.5887 | 1.1670 | 1.3005 |  1.5971 |        0.9183 |                  0 |   1.0617 |
|    34_27_2 |           0 |                0 |  1.6452 | 1.5951 | 1.5871 | 1.1670 | 1.6118 |  1.6452 |        0.0000 |                  0 |   0.5126 |
|    34_27_2 |           1 |                1 |  0.9943 | 1.1750 | 1.1668 | 1.1670 | 0.8814 |  1.1750 |        0.0000 |                  1 |   0.5126 |
|    34_31_2 |           0 |                1 |  1.5236 | 1.5987 | 1.5713 | 1.1670 | 1.4997 |  1.5987 |        0.0750 |                  0 |   0.5126 |
|    34_31_2 |           1 |                1 |  1.0530 | 1.1677 | 1.1654 | 1.1670 | 1.1328 |  1.1677 |        0.1148 |                  0 |   0.5126 |
|    34_42_2 |           0 |                1 |  1.3624 | 1.5863 | 1.5756 | 1.1670 | 1.3495 |  1.5863 |        0.0000 |                  1 |   0.5126 |
|    34_42_2 |           1 |                3 |  1.0189 | 1.1663 | 1.1651 | 1.1670 | 1.0827 |  1.1670 |        0.1481 |                  0 |   0.5126 |
|    34_45_2 |           0 |                4 |  1.5030 | 1.5863 | 1.5843 | 1.1670 | 1.5985 |  1.5985 |        0.0122 |                  1 |   0.5126 |
|    34_45_2 |           1 |                4 |  1.0237 | 1.1670 | 1.1655 | 1.1670 | 1.1731 |  1.1731 |        0.1494 |                  0 |   0.5126 |
|    34_52_2 |           0 |                1 |  1.3910 | 1.5954 | 1.5716 | 1.1670 | 1.4387 |  1.5954 |        0.0000 |                  1 |   0.5126 |

*Full policy lookup available in the supplementary dataset at https://github.com/olatechie/dropout.*

Column definitions: `child_id` = anonymised cluster–household–child identifier; `dose_step` = 0 (T1: DTP1→DTP2), 1 (T2: DTP2→DTP3); `optimal_action` = CQL-recommended action (0=none, 1=SMS, 2=CHW, 3=facility recall, 4=conditional incentive); `q_a0`–`q_a4` = Q-values for each action; `q_max` = maximum Q-value; `q_advantage` = q_max − min(q_a0,...,q_a4); `behaviour_action` = inferred behaviour-policy action per §S1.4; `weight` = survey sample weight (v005/1,000,000).

---

## S3.2 Supplementary Figures

![**Figure S1.** Calibration curve for model T1 (pre-recalibration). Isotonic regression applied to out-of-fold predictions from 5-fold cluster-robust cross-validation. The diagonal dashed line represents perfect calibration. Calibration slope = 0.874 pre-recalibration.](figures/supplement/sfig_calibration_t1_pre.png){#fig:s1}

![**Figure S2.** Calibration curve for model T1 after isotonic recalibration. Calibration slope improved from 0.874 to 0.959; Brier score reduced from 0.036 to 0.032. Recalibrator artefact saved to outputs/stage1/isotonic_calibrator_t1.pkl.](figures/supplement/sfig_calibration_t1_post.png){#fig:s2}

![**Figure S3.** Calibration curve for model T2 (pre-recalibration). Calibration slope = 1.596 pre-recalibration, indicating systematic over-confidence in high-risk predictions.](figures/supplement/sfig_calibration_t2_pre.png){#fig:s3}

![**Figure S4.** Calibration curve for model T2 after isotonic recalibration. Calibration slope improved from 1.596 to 0.969; Brier score reduced from 0.027 to 0.026. Recalibrated risk scores from T1 and T2 models were passed as state features to the offline RL stage.](figures/supplement/sfig_calibration_t2_post.png){#fig:s4}

![**Figure S5.** SHAP beeswarm plot for model T1 (DTP1→DTP2 dropout). Each point represents one child; horizontal position shows SHAP value (impact on dropout probability); colour encodes feature value (red=high, blue=low). Features ordered by mean absolute SHAP contribution.](figures/supplement/sfig_shap_beeswarm_t1.png){#fig:s5}

![**Figure S6.** SHAP beeswarm plot for model T2 (DTP2→DTP3 dropout). Features ordered by mean absolute SHAP contribution. Enabling factors (wealth, travel time) show the largest contributions at the T2 transition.](figures/supplement/sfig_shap_beeswarm_t2.png){#fig:s6}

![**Figure S7.** FQI convergence: policy value (WIS-estimated) versus iteration number. Convergence criterion ΔQ < 0.01 was met at iteration 100 (of 200 maximum). Shaded band shows ±1 SD across 5 evaluation seeds.](figures/supplement/sfig_fqi_convergence.png){#fig:s7}

![**Figure S8.** CQL α sensitivity analysis: WIS-estimated policy value (left axis) and action diversity (Shannon entropy over recommended actions, right axis) across α values {0.1, 0.5, 1.0, 2.0, 5.0}. Base case α = 1.0 selected as the point where policy value plateaus and action diversity remains non-degenerate.](figures/supplement/sfig_cql_alpha_sensitivity.png){#fig:s8}

![**Figure S9.** Off-policy evaluation comparison across IS, WIS, and DR estimators on 1,569 held-out episodes. Agreement across estimators provides evidence for OPE reliability. Error bars show 95% bootstrap confidence intervals.](figures/supplement/sfig_ope_comparison.png){#fig:s9}

![**Figure S10.** Local Moran's I cluster map of DTP1→DTP3 dropout across Nigerian LGAs. High-High clusters (red) indicate spatial concentrations of elevated dropout risk; Low-Low clusters (blue) indicate low-risk spatial clusters. Statistical significance at p < 0.05 after 999-permutation conditional randomisation.](figures/supplement/sfig_local_moran.png){#fig:s10}

![**Figure S11.** State-level DTP1→DTP3 dropout prevalence, NDHS 2024. Choropleth map using sstate variable; survey-weighted proportions. States with dropout prevalence > 30% are labelled. Color scale is continuous from 0% (dark green) to >50% (dark red).](figures/supplement/sfig_prevalence_by_state.png){#fig:s11}

![**Figure S12.** Andersen-domain decomposition of SHAP feature importance for T1 (left) and T2 (right) models. Bar height represents summed absolute SHAP contribution for all features within each Andersen domain (Predisposing, Enabling, Need, Dynamic). Enables policy-relevant attribution of dropout risk to modifiable versus fixed factor domains.](figures/supplement/sfig_andersen_decomposition.png){#fig:s12}
