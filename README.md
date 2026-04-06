# Nigeria Vaccine Dropout RL Study

**RL-Optimised Sequential Intervention for Reducing DTP1-to-DTP3 Vaccine Dropout in Nigeria**

Warwick Applied Health, Warwick Medical School, University of Warwick

## Overview

This project applies offline reinforcement learning to learn optimal sequential intervention policies for reducing DTP1-to-DTP3 vaccine dropout in Nigeria, using the Nigeria Demographic and Health Survey 2024.

## Pipeline

Sequential Agent Teams pipeline powered by Claude Code:

1. **Literature Reviewer** — searches academic literature for dropout determinants, RL precedents, intervention effect sizes, ML validation practices
2. **EDA + Cascade + ML** — exploratory data analysis, immunisation cascade construction, transition-specific XGBoost with SHAP/Andersen decomposition, MDP state space construction
3. **RL + Bandit + Microsimulation** — offline RL (FQI + CQL), multi-armed bandit allocation, microsimulation validation across 6 scenarios
4. **Dashboard Integration** — Streamlit dashboard with 8 pages, pipeline integration report

## Data Requirements

- NDHS 2024 KR file: `data/raw/dhs/nga_2024/NGKR8BFL.DTA`
- DHS Geospatial Covariates: `data/raw/geospatial/NGGC8AFL.csv`

Data files are not included in this repository (DHS licence restrictions). Place them in the paths above before running the pipeline.

## Running the Pipeline

1. Ensure Claude Code v2.1.32+ is installed
2. Place DHS data files in `data/raw/`
3. Open Claude Code in this directory
4. Paste the launch prompt from `docs/reference/launch_prompt.txt`

## Repository Structure

See `CLAUDE.md` for domain rules and variable definitions.
See `.claude/agents/` for agent role definitions.
See `handoffs/` for inter-agent contracts.

## Licence

Code: MIT. Data: Subject to DHS licence terms.
