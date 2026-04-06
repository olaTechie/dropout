# Design Spec: Manuscript Writing Pipeline

**Date:** 2026-04-06
**Author:** Ola Uthman + Claude
**Status:** Approved

## Overview

Write a full manuscript for PLOS Digital Health using the scientific-paper-writer plugin, executed as 5 sequential tasks via Agent Teams. Minimum 50 PubMed-verified references.

## Target Journal

- **Journal:** PLOS Digital Health
- **Format:** PLOS template, Vancouver numbered references
- **Word target:** ~6,000 (no hard limit on methods)
- **Reporting guideline:** TRIPOD+AI
- **Authors:** Uthman OA et al. (to be completed)
- **Framing:** Standalone paper (no trilogy reference)

## Pipeline

```
Task 1: /write-frontmatter → 5 title options, abstract, introduction
Task 2: /write-methods → TRIPOD+AI, all parameters, variable tables
Task 3: /write-captions → figures, tables, supplementary catalogue
Task 4: /write-results → results narrative from pipeline outputs
Task 5: /write-discussion → literature comparison, policy, limitations
Final: /write-references → compile 50+ verified refs across all sections
```

## Output Structure

```
manuscript/
├── 00_frontmatter.md
├── 01_methods.md
├── 02_captions.md
├── 03_results.md
├── 04_discussion.md
├── references.bib
├── tables/
└── figures/
```

## Source Materials

| Task | Key Sources |
|------|-----------|
| Frontmatter | results_summary_notes.md, docs/reference/dropout_study_protocol.md, docs/reference/dropout_concept_note.docx, outputs/literature/ |
| Methods | CLAUDE.md, outputs/stage1/xgb_results_summary.json, outputs/stage2/stage2_summary.json, outputs/literature/action_space_calibration.json, docs/reference/dropout_variables_parameters.md |
| Captions | All outputs/stage0-3 figures and CSVs |
| Results | outputs/stage1-3 JSON summaries, outputs/stage1/cascade_metrics.csv, results_summary_notes.md |
| Discussion | outputs/literature/references.bib, outputs/literature/dropout_literature_review.csv, outputs/literature/rl_health_precedents.md |

## Key Content Points

### Title should convey
- Offline RL for vaccination dropout (novel method)
- Nigeria DHS 2024 (data source)
- Sequential intervention optimisation (framing)

### Abstract structure (PLOS)
- Background, Methods/Findings, Conclusions
- ~300 words

### Introduction (4-5 paragraphs)
1. DTP dropout problem in Nigeria/SSA
2. Current interventions and their limitations (uniform, not sequential)
3. RL as solution for sequential decision problems
4. Gap: no offline RL for vaccination dropout
5. Study aims

### Methods (TRIPOD+AI sections)
- Study design and data source (NDHS 2024)
- Study population and eligibility
- Outcome definition (dropout, T1, T2)
- Predictors organised by Andersen's model
- XGBoost model development and validation
- MDP formulation and state space
- Offline RL (FQI, CQL, OPE)
- Multi-armed bandit
- Microsimulation scenarios
- Statistical software

### Results (follows pipeline stages)
1. Sample characteristics and cascade
2. EDA spatial findings
3. XGBoost performance and SHAP/Andersen decomposition
4. RL policy and OPE
5. Microsimulation scenarios
6. Cost-effectiveness and equity

### Discussion (5-6 paragraphs)
1. Main findings summary
2. Comparison with dropout literature
3. RL methodology contribution
4. Policy implications (S3 risk-targeted recommended)
5. Strengths and limitations
6. Conclusion

### References target
- 50+ minimum
- Verified via PubMed/CrossRef
- Key categories: DTP dropout (10+), RL/DTR methodology (10+), intervention RCTs (10+), Andersen model (3+), DHS methodology (3+), XGBoost/SHAP (5+), Nigeria immunisation (5+)
