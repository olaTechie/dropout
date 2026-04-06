---
name: dashboard-integration
description: Builds Streamlit dashboard from all upstream outputs and produces final integration report
model: opus
tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
---

# Dashboard + Integration Agent

Read ALL handoff files in handoffs/ FIRST. Then read outputs from all stages.

## Streamlit Dashboard (8 pages)

### Page 1: Immunisation Cascade
- Bar chart: DTP1→DTP2→DTP3 retention
- Filterable by zone, state, wealth, urban/rural
- Source: outputs/stage1/cascade_metrics.csv

### Page 2: EDA Explorer
- Embed profiling report link
- TableOne display
- Choropleth and cluster maps
- Source: outputs/stage0/

### Page 3: Transition SHAP Explorer
- SHAP plots for T1 and T2 models
- Andersen domain decomposition comparison
- Source: outputs/stage1/shap_*.csv

### Page 4: Timeliness Analysis
- Inter-dose interval distributions
- Delay accumulation patterns
- Source: outputs/stage1/

### Page 5: RL Policy Map
- Choropleth: recommended action per LGA at each dose step
- State-action heatmap
- Source: outputs/stage2/policy_lookup.csv, q_values_heatmap.csv

### Page 6: Bandit Allocation
- Budget slider → LGA allocation visualization
- Coverage projections
- Source: outputs/stage3/lga_allocation.csv

### Page 7: Microsimulation Scenarios
- Side-by-side S0–S5 comparison
- Equity dashboard
- Cost-effectiveness plane
- Source: outputs/stage3/

### Page 8: Data Export
- Download cascade data, policy recommendations, scenario results

## Integration Report
- Compile docs/pipeline_audit_log.md from all stage gate results
- Verify all outputs exist and are internally consistent
- Flag any cross-stage inconsistencies

## Code Location
- code/stage5_dashboard/app.py (main Streamlit app)
- code/stage5_dashboard/pages/ (one file per page)
