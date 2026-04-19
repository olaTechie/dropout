# MDPI *Vaccines* Manuscript — Hybrid Methodology Paper (Design Spec)

**Date:** 2026-04-19
**Project:** Nigeria Vaccine Dropout RL Study (03_dropout)
**Target venue:** *Vaccines* (MDPI), Article type
**Framing:** Hybrid methodology paper — prediction (TRIPOD-AI) + economic evaluation (CHEERS 2022) + offline RL (custom reporting)
**Writer delegation:** One fresh **Sonnet 4.6** subagent per task; Opus orchestrates + reviews between tasks
**Driving plugin:** `scientific-paper-writer@1.0.1`

---

## 1. Goals

1. Produce a submission-ready MDPI *Vaccines* Article: `manuscript.docx` + `manuscript_supplement.docx`, both with **embedded** figures and tables (not file links).
2. Cover all three methodological threads of the study in equal depth: DTP1→DTP2 / DTP2→DTP3 dropout prediction, offline RL (FQI + CQL + OPE) + contextual bandit allocation, microsimulation with PSA.
3. Include a new **Interactive Web Dashboard** subsection in both Methods and Results, referencing the live site `https://olatechie.github.io/dropout/`.
4. Supplementary materials: TRIPOD-AI + CHEERS checklists, online-only figures/tables, full model-input parameter table, reproducibility parameters.
5. Minimum **50 unique references** across Introduction, Methods, and Discussion, in MDPI numeric style.
6. Archive prior manuscript content (`./manuscript/*` as of 2026-04-06) to `./manuscript/.archive/` — keep `references.bib` as seed for the new reference list.

## 2. Non-goals

- Not running new experiments — all numbers come from existing `outputs/` artifacts (stage0/stage1/stage2/stage2_v2/stage3/stage3_v2/validation/literature).
- Not changing any analytical code (stage scripts are frozen).
- Not manually writing Sonnet-quality prose in Opus; Opus orchestrates + verifies quantitatively but does not draft.
- Not submitting to any journal other than MDPI *Vaccines* in this plan (journal-specific formatting can diverge later if retargeted).

## 3. Constraints and assumptions

**Stated in brief:**
- Archive all of `./manuscript/` to `./manuscript/.archive/` before starting new drafts.
- Sonnet agent writes; TDD-style per-section review by Opus.
- Must use `scientific-paper-writer` skills (`write-frontmatter`, `write-methods`, `generate-figures`, `write-captions`, `write-results`, `write-discussion`, `write-references`, `export-manuscript`).
- Figures and tables must be **embedded** in the final `.docx` — not linked.
- Dashboard URL: `https://olatechie.github.io/dropout/`.
- ≥50 references.
- Prepare online-only supplementary figures, tables, and a model-input parameter list.
- New "dashboard" subsection required in Methods and in Results, modelled on the sample text below.

**MDPI *Vaccines* Article assumptions (to be verified against the live template when added to `assets/`):**
- ~200-word unstructured abstract (structured allowed but unstructured is default).
- No hard word cap; target ~5,800 words main text.
- No reference cap.
- Numeric in-text citations `[1]`; MDPI-ACS reference-list style.
- 3–10 keywords; target 5–7.
- Required sections: Introduction, Materials and Methods, Results, Discussion, **Conclusions** (separate short section), then back matter (Author Contributions, Funding, Institutional Review Board Statement, Informed Consent Statement, Data Availability Statement, Conflicts of Interest, Supplementary Materials).
- Supplementary cross-referenced as Figure S1, Table S1, etc.

**Sample text pattern (from brief) — the dashboard subsections must match this voice:**

> Methods: *"To facilitate an in-depth exploration of data, we developed an interactive web dashboard, designed to provide a comprehensive exploration and visualization of the data."*
> Results: *"We have presented a dashboard including advanced data visualization tools, to facilitate a more detailed exploration of trends, patterns, and relationships within our dataset. This innovative tool is accessible at \[URL\]. The app features …"*

## 4. Reporting standards

Named explicitly in the manuscript's Methods §3.9 *Reporting Standards, Software, and Reproducibility* subsection and listed in the supplement with completed checklists:

1. **TRIPOD-AI** (Collins et al. 2024) — applied to the prediction-model components (§3.4).
2. **CHEERS 2022** (Husereau et al. 2022) — applied to the microsimulation + PSA (§3.7).
3. **RL-health reporting norms** — Gottesman et al. 2019 (*Nat Med*), Liu et al. 2022 — applied to the offline-RL components (§3.5–3.6). No single consensus checklist exists yet; we list the Gottesman "seven deadly sins" explicitly in the supplement and note how each is addressed.

## 5. Title and abstract

- **Working title (placeholder, Sonnet drafts 3 alternatives in Task 1):**
  *"Reinforcement-Learning-Guided Sequential Intervention to Reduce DTP1-to-DTP3 Vaccine Dropout in Nigeria: A Prediction, Policy Optimisation, and Cost-Effectiveness Analysis."*
- **Running title:** *"RL-guided DTP dropout reduction in Nigeria"* (≤50 characters).
- **Abstract:** 200 words, unstructured, four implicit beats (Background → Methods → Results → Implications). Includes the three headline numbers: DTP1→DTP3 dropout rate; best-model AUROC at T1 and T2; incremental DTP3 coverage + ICER of RL-optimised vs status-quo.
- **Keywords:** 5–7 drawn from {DTP vaccination, immunisation dropout, Nigeria, reinforcement learning, microsimulation, cost-effectiveness, Andersen model, DHS, prediction model, health equity}.

## 6. Manuscript skeleton (~5,800 words)

| § | Heading | Words | Notes |
|---|---------|-------|-------|
| 1 | Introduction | 600 | Burden → dropout specifically → gap (no RL-guided allocation in LMIC immunisation) → aim → 3-bullet contributions |
| 2 | Materials and Methods | 2,100 | See §6.1 |
| 3 | Results | 1,800 | See §6.2 |
| 4 | Discussion | 1,000 | Principal findings; comparison with literature (≥15 refs); strengths; limitations; policy implications; future work |
| 5 | Conclusions | 150 | Separate short section per MDPI norm |
|   | Back matter | n/a | Author Contributions, Funding, IRB Statement, Informed Consent, Data Availability (DHS + repo + dashboard URL), Conflicts of Interest, Supplementary Materials |
|   | **Abstract** | 200 | Placed before Introduction in submission |

### 6.1 Materials and Methods subsections

| # | Subsection | Words | Key content |
|---|-----------|-------|-------------|
| 3.1 | Data source and study population | 220 | DHS 2024 NGKR8BFL/IR/HR; h3∈{1,2,3}; children 12–23 months; youngest child per woman (b5==1); survey weights v005/1e6; strata v022; PSU v021 |
| 3.2 | Outcome definitions | 160 | T1 dropout (h3∈{1,3} & h5==0); T2 dropout (h5∈{1,3} & h7==0); WHO cascade definition |
| 3.3 | Predictors and Andersen mapping | 260 | Predisposing / Enabling / Need / Dynamic; full list per CLAUDE.md; geospatial covariates (UN density, travel times, nightlights, malaria, ITN) |
| 3.4 | Prediction modelling | 380 | **TRIPOD-AI subsection.** XGBoost; nested 5-fold stratified CV; isotonic recalibration; metrics AUROC/AUPRC/Brier/ECE with 95%CI via 1000-sample bootstrap; SHAP |
| 3.5 | MDP formulation and offline RL | 360 | States (see CLAUDE.md dynamic vars); 5-action space (a₀–a₄); reward R=1.0·DTP3+0.3·next_dose−λ·cost; behaviour-policy inference rules; FQI and CQL; off-policy evaluation (IS, WIS, DR) |
| 3.6 | Contextual bandit for LGA allocation | 140 | LinUCB over LGA features; cost-constrained allocation |
| 3.7 | Microsimulation and PSA | 400 | **CHEERS subsection.** S0–S5 scenarios; 1,000 bootstrap replicates; ICER and CEAC; tornado one-way; λ=₦50,000/child willingness-to-pay |
| 3.8 | **Interactive Web Dashboard** | 120 | New subsection per brief — sample-text voice; modules (Story, Policy, Simulation, Explorer); URL; accessibility (transcript fallback); open-source repo |
| 3.9 | Reporting standards, software, reproducibility | 60 | TRIPOD-AI + CHEERS + Gottesman; software versions; seeds; repo link |

### 6.2 Results subsections

| # | Subsection | Words | Display items |
|---|-----------|-------|---------------|
| 4.1 | Cohort descriptives | 260 | Table 1; Fig 1 |
| 4.2 | Prediction performance | 340 | Table 2; Fig 2 |
| 4.3 | RL-optimised policy and LGA allocation | 320 | Fig 3 |
| 4.4 | Microsimulation scenarios and PSA | 400 | Table 3; Table 4; Fig 4 |
| 4.5 | Subgroup equity | 220 | Supplementary tables + forest plot (S-fig) |
| 4.6 | **Interactive Dashboard** | 140 | Fig 5; URL; sample-text voice |
| 4.7 | Summary | 120 | Transition to Discussion |

## 7. Display items (main)

### 7.1 Main figures (5) — all **embedded** in `.docx` via `![…](path){#fig:X}` pandoc syntax

| Fig | Title (working) | Sources | Build notes |
|-----|-----------------|---------|-------------|
| 1 | Study flow and DTP cascade | `outputs/stage0/dropout_funnel_plot.png` + `outputs/stage1/cascade_by_zone.png` | 2-panel composite, 300 DPI; PDF + PNG output |
| 2 | Model performance and top-10 SHAP predictors (T1 and T2) | `outputs/stage1/roc_pr_model_t1.pdf`, `roc_pr_model_t2.pdf`, `shap_bar_model_t1.pdf`, `shap_bar_model_t2.pdf` | 2×2 panel |
| 3 | RL-optimised LGA allocation of interventions | `outputs/stage3/lga_allocation.csv` + `data/shapefiles/gadm/gadm41_NGA_2.shp` | Choropleth of recommended action per LGA |
| 4 | Cost-effectiveness acceptability curve and CE plane | `outputs/stage3_v2/ceac.pdf` + `ce_plane.pdf` | Side-by-side panel |
| 5 | Interactive dashboard screenshots | `https://olatechie.github.io/dropout/` | Playwright screenshot — story hero + policy dashboard, side-by-side; saved to `manuscript/figures/fig5_dashboard.png`. Manual-capture fallback documented in `scripts/build_manuscript.py` |

### 7.2 Main tables (4) — all pandoc-rendered Word-native tables, embedded

| Tab | Title (working) | Source | Build notes |
|-----|-----------------|--------|-------------|
| 1 | Cohort descriptives by T1/T2 dropout status | `outputs/stage0/descriptive_statistics_table.csv` | If needed, re-weight with v005/1e6; otherwise use as-is |
| 2 | Prediction-model performance (AUROC, AUPRC, Brier, ECE, 95 % CI) | `outputs/stage1/cascade_metrics.csv` + `recalibration_log.md` | Include pre- and post-recalibration |
| 3 | Microsimulation scenarios S0–S5: DTP3 coverage, cost, ICER vs S0, CE probability at λ=₦50,000/child | `outputs/stage3_v2/microsim_results.csv` + `icer_distribution.csv` | PSA-based 95 % CIs |
| 4 | One-way sensitivity (tornado data) | `outputs/stage3_v2/tornado_data.csv` | Top 10 parameters by ICER range |

## 8. Supplementary materials (`manuscript_supplement.docx`)

Ordered contents, all embedded:

1. **S0 Reporting checklists** — TRIPOD-AI table, CHEERS 2022 table, Gottesman RL-health checklist.
2. **S1 Extended methods** — FQI + CQL algorithm boxes; OPE estimators formulae; behaviour-policy inference rules (full table); microsim state-transition pseudocode.
3. **S2 Parameter tables** —
   - S2.1 **Model-input parameter table**: all literature-derived effect sizes, intervention costs (with source + year + 2026 NGN), PSA prior distributions, WTP thresholds, discount rate, time horizon.
   - S2.2 **Reproducibility parameter table**: seeds, CV folds, XGBoost hyperparams, FQI/CQL hyperparams, bootstrap N, software versions (Python, xgboost, scikit-learn, pandas, statsmodels, shap).
4. **S3 Supplementary figures and tables** —
   - S3.1 Tables: full descriptives (all covariates); per-state cascade metrics; per-zone calibration metrics; subgroup performance (by zone, state, wealth quintile, urban-rural, maternal education); policy lookup (state representation → recommended action + Q-value).
   - S3.2 Figures: calibration curves T1/T2 pre- and post-recalibration; SHAP beeswarms T1/T2/full; FQI convergence; CQL α-sensitivity; OPE comparison; bootstrap distributions S0–S5; subgroup forest plots; local Moran cluster map; prevalence-by-state map; Andersen-domain decomposition comparison.

## 9. References (≥50)

- **Seed:** `manuscript/.archive/references.bib` (current ~53 entries; audit for duplicates / obsolescence during Task 6).
- **Augmentation:** `scientific-paper-writer:write-references` skill in Task 6 surfaces uncited claims flagged during Tasks 1–5 and proposes new references drawn from `outputs/literature/dropout_literature_review.csv`, `outputs/literature/intervention_effect_sizes.csv`, plus targeted PubMed / bioRxiv searches. Sonnet returns a diff (additions/removals) — Opus approves.
- **Style:** MDPI numeric `[1]` in text; reference list in MDPI format via `assets/vaccines.csl` (from Zotero's official CSL repository).
- **Target mix:** ≥15 in Introduction, ≥10 in Methods (method citations — XGBoost, SHAP, FQI, CQL, OPE estimators, LinUCB, CHEERS, TRIPOD-AI, Andersen model), ≥20 in Discussion (comparison with dropout literature, RL-health applications, immunisation policy evidence). Minimum 50 unique.

## 10. Architecture — writing pipeline

**Task sequence (Opus orchestrates; one fresh Sonnet 4.6 subagent per task):**

| # | Task | Skill | Brief payload Opus curates | Opus review gate |
|---|------|-------|----------------------------|------------------|
| 0 | Archive existing manuscript | (shell) | `git mv manuscript/* manuscript/.archive/` | `.archive/` populated; `references.bib` preserved |
| 1 | Frontmatter (title, abstract, introduction, keywords) | `write-frontmatter` | Burden stats, 3-bullet contributions, sample title, intro cite hooks | 3 title alternatives; abstract = 200±10w; intro ≥15 refs hooks |
| 2 | Methods (inc. TRIPOD-AI, CHEERS, and Dashboard subsections) | `write-methods` | CLAUDE.md rules, stage1/2/3 READMEs, sample-dashboard text, Gottesman/Collins/Husereau citations | All 9 subsections present; 2,100±150w; ≥10 method citation hooks |
| 3 | Main figures + captions + results collator | `generate-figures` + `write-captions` | All CSV paths, existing stage PNG/PDFs, Playwright script for dashboard screenshot | All 5 figures + 4 tables generated to `manuscript/figures/` and `manuscript/tables/`; captions + numeric fact sheet produced |
| 4 | Results (inc. Dashboard paragraph) | `write-results` | Task-3 numeric fact sheet, captions, sample-dashboard text | 7 subsections; every number traceable to a CSV cell; 1,800±150w |
| 5 | Discussion | `write-discussion` | Task-4 results, top-20 lit refs from `outputs/literature/`, Gottesman RL-health limitations list | ≥20 refs; Gottesman items addressed; 1,000±100w |
| 6 | References (≥50, MDPI numeric) | `write-references` | `.archive/references.bib` + new refs flagged in Tasks 1–5 | Count ≥50, no duplicates, all in-text `[n]` resolved |
| 7 | Export to `.docx` (main + supplement, embedded fig/tab) | `export-manuscript` | Pandoc command, MDPI `reference.docx`, `vaccines.csl` | Both `.docx` render without errors; figures and tables visible inline; all `[@ref]` resolved |
| 8 | GitHub Pages landing (bonus) | (shell) | Link list | `docs/manuscript/index.html` lists `.docx`, `.bib`, figures, dashboard |

**Review gate criteria (applied by Opus between every task):**

1. **Numeric accuracy** — every quantitative claim traced to a CSV cell, CI interval, or JSON summary.
2. **Citation hooks** — every factual claim has a `[@key]` placeholder; no bare assertions.
3. **Checklist coverage** — TRIPOD-AI items addressed in §3.4; CHEERS items addressed in §3.7; Gottesman items addressed in §3.5 and discussion.
4. **Word budget** — each section within ±10% of target.
5. **Voice + MDPI style** — present tense for methods/results generally acceptable in MDPI; passive voice fine; no emojis; numbered section headings.

If any gate fails, Sonnet subagent is re-dispatched with diff instructions; maximum 2 revision loops per task before Opus escalates.

## 11. Assembly toolchain

Single entrypoint: `scripts/build_manuscript.py`.

```
build_manuscript.py
├── regenerate_main_figures()        # reads outputs/ CSVs → manuscript/figures/*.{png,pdf}
├── capture_dashboard_screenshot()   # Playwright → manuscript/figures/fig5_dashboard.png
├── render_main_tables()             # CSVs → Markdown tables via pandas.to_markdown
├── concat_markdown()                # sections in order → build/manuscript.md
├── pandoc_main()                    # pandoc --reference-doc=assets/mdpi_reference.docx
│                                    #        --citeproc --bibliography=manuscript/references.bib
│                                    #        --csl=assets/vaccines.csl
│                                    #        -o manuscript/manuscript.docx build/manuscript.md
├── concat_supplement()              # supplement sections → build/supplement.md
└── pandoc_supplement()              # same pandoc call → manuscript/manuscript_supplement.docx
```

- **Template:** `assets/mdpi_reference.docx` — download the MDPI *Vaccines* template once; if unavailable the plan creates a minimal MDPI-style `reference.docx` (Palatino Linotype 10pt, numbered headings) and documents the swap.
- **CSL:** `assets/vaccines.csl` — fetched from the Zotero CSL repository's `mdpi` variant.
- **Figures embedded:** pandoc inlines `![caption](figures/figX.png){#fig:X width=\\textwidth}` into the docx so reviewers see the images without opening separate files.
- **Tables embedded:** pandoc renders pipe-tables as Word-native tables (not images); captions use `Table: …` syntax with identifiers.

## 12. File layout (after implementation)

```
manuscript/
├── .archive/                       # pre-2026-04-19 content
│   ├── 00_frontmatter.md .. 04_discussion.md
│   ├── references.bib              # seed for new bib
│   ├── manuscript_full.docx
│   ├── figures/, tables/
│   └── sonnet_abstract_results.md
├── 00_frontmatter.md               # title + abstract + intro + keywords
├── 01_methods.md
├── 02_results.md                   # captions embedded + results prose
├── 03_discussion.md
├── 04_conclusions.md
├── 99_backmatter.md
├── references.bib
├── supplement/
│   ├── S0_checklists.md
│   ├── S1_methods_extended.md
│   ├── S2_parameter_tables.md
│   └── S3_figures_tables.md
├── figures/
│   ├── fig1.png / fig1.pdf
│   ├── fig2.png / fig2.pdf
│   ├── fig3.png / fig3.pdf
│   ├── fig4.png / fig4.pdf
│   ├── fig5_dashboard.png
│   └── supplement/ (S-figures)
├── tables/
│   ├── tab1.md .. tab4.md
│   └── supplement/ (S-tables)
├── manuscript.docx                 # pandoc output — embedded fig+tab
└── manuscript_supplement.docx      # pandoc output — embedded fig+tab
assets/
├── mdpi_reference.docx
└── vaccines.csl
scripts/
└── build_manuscript.py
docs/
└── manuscript/
    └── index.html                  # GitHub Pages landing (bonus task 8)
```

## 13. Acceptance criteria

The plan is complete when:

- `manuscript/manuscript.docx` opens in Word with all 5 main figures and 4 main tables rendered inline (not as broken links).
- `manuscript/manuscript_supplement.docx` opens in Word with all supplementary items rendered inline, including the model-input parameter table.
- `manuscript/references.bib` contains ≥50 unique entries; every `[n]` citation in the main text resolves.
- Methods §3.8 and Results §4.6 contain the Interactive Dashboard subsections in the sample-text voice, referencing `https://olatechie.github.io/dropout/`.
- TRIPOD-AI + CHEERS + Gottesman checklists are present in the supplement, filled in.
- All content previously in `manuscript/` is preserved in `manuscript/.archive/`.
- `scripts/build_manuscript.py` is idempotent — running it regenerates both `.docx` artifacts from source CSVs, markdown, and the dashboard screenshot without manual steps.
- Opus has confirmed numeric accuracy (every claim traceable to a source CSV cell), citation completeness, and word-budget adherence for all sections.

## 14. Out-of-scope for this spec

- Journal-specific resubmission formatting beyond MDPI *Vaccines* initial submission.
- Response-to-reviewer letters (future spec after first-round reviews arrive).
- Press-release or plain-language-summary variants.
- Translation to other languages.
- Updating the live dashboard or cinematic website — the manuscript references whatever is deployed at submission time.
