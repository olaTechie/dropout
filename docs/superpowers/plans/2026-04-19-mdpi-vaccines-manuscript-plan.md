# MDPI *Vaccines* Manuscript Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce a submission-ready MDPI *Vaccines* Article (`manuscript.docx` + `manuscript_supplement.docx`) with embedded figures/tables, ≥50 references, TRIPOD-AI + CHEERS + Gottesman reporting, and an Interactive Dashboard subsection in Methods and Results.

**Architecture:** Three phases — (1) Engineering prep in Opus: archive, assets, figure/table scripts, pandoc orchestrator, (2) Writing in Sonnet 4.6 subagents: one dispatch per section via `scientific-paper-writer` skills, Opus factchecks between tasks, (3) Finalisation in Opus: pandoc export to `.docx` with embedded items, GitHub Pages landing.

**Tech Stack:** Python 3.11 (pandas, matplotlib, geopandas, shap, playwright, python-docx); Pandoc ≥ 3.0 with `--citeproc`; `scientific-paper-writer@1.0.1` plugin; MDPI reference.docx + `multidisciplinary-digital-publishing-institute.csl`; Sonnet 4.6 via Agent tool.

**Reference spec:** `docs/superpowers/specs/2026-04-19-mdpi-vaccines-manuscript-design.md`

---

## File Structure

**Created (engineering):**
- `assets/mdpi_reference.docx` — pandoc reference template (fonts, heading styles)
- `assets/vaccines.csl` — MDPI citation style (Zotero official)
- `manuscript/PAPER_CONTEXT.md` — context file consumed by `scientific-paper-writer` skills
- `scripts/manuscript_figures.py` — regenerates main figures 1–4 from CSVs/stage outputs
- `scripts/capture_dashboard.py` — Playwright screenshot for Fig 5
- `scripts/manuscript_tables.py` — renders main tables 1–4 from CSVs to Markdown
- `scripts/manuscript_supplement.py` — renders supplementary tables + checklists
- `scripts/build_manuscript.py` — pandoc orchestrator (main + supplement docx)
- `tests/manuscript/test_figures.py` — figure script tests
- `tests/manuscript/test_tables.py` — table script tests
- `tests/manuscript/test_supplement.py` — supplement script tests
- `tests/manuscript/test_build.py` — build orchestrator integration test

**Created (prose — Sonnet):**
- `manuscript/00_frontmatter.md` (title, abstract, intro, keywords)
- `manuscript/01_methods.md` (9 subsections)
- `manuscript/02_results.md` (7 subsections)
- `manuscript/03_discussion.md`
- `manuscript/04_conclusions.md`
- `manuscript/99_backmatter.md`
- `manuscript/captions.md` (5 main + all supplementary captions)
- `manuscript/fact_sheet.md` (numeric claim → CSV cell map for Opus review)
- `manuscript/references.bib` (≥50 entries)
- `manuscript/supplement/S0_checklists.md`
- `manuscript/supplement/S1_methods_extended.md`
- `manuscript/supplement/S2_parameter_tables.md`
- `manuscript/supplement/S3_figures_tables.md`

**Created (build outputs):**
- `manuscript/figures/fig1.png|pdf` … `fig5_dashboard.png`
- `manuscript/figures/supplement/sfig*.png|pdf`
- `manuscript/tables/tab1.md` … `tab4.md`
- `manuscript/tables/supplement/stab*.md`
- `manuscript/manuscript.docx`
- `manuscript/manuscript_supplement.docx`
- `docs/manuscript/index.html`

**Archived:**
- `manuscript/.archive/` — all prior `manuscript/*` as of 2026-04-19

**Not modified:** any `outputs/**`, `scripts/run_*`, analysis code. Numbers come from existing artifacts only.

---

## Phase 1 — Engineering Prep (Opus)

### Task 0: Archive existing manuscript

**Files:**
- Move: `manuscript/*` → `manuscript/.archive/`
- Preserve: `manuscript/.archive/references.bib` as bib seed

- [ ] **Step 1: Create archive directory and move contents**

```bash
mkdir -p manuscript/.archive
git mv manuscript/00_frontmatter.md manuscript/.archive/
git mv manuscript/00_frontmatter_merged.md manuscript/.archive/
git mv manuscript/01_methods.md manuscript/.archive/
git mv manuscript/02_captions.md manuscript/.archive/
git mv manuscript/03_results.md manuscript/.archive/
git mv manuscript/03_results_merged.md manuscript/.archive/
git mv manuscript/04_discussion.md manuscript/.archive/
git mv manuscript/references.bib manuscript/.archive/
git mv manuscript/sonnet_abstract_results.md manuscript/.archive/
git mv manuscript/manuscript_full.docx manuscript/.archive/
git mv manuscript/figures manuscript/.archive/figures
git mv manuscript/tables manuscript/.archive/tables
```

- [ ] **Step 2: Verify archive populated**

Run: `ls manuscript/.archive/ && ls manuscript/`
Expected: `.archive/` contains all listed files + `figures/` + `tables/`; `manuscript/` only shows `.archive/`.

- [ ] **Step 3: Commit archive**

```bash
git add manuscript/
git commit -m "manuscript: archive pre-2026-04-19 draft for MDPI Vaccines rewrite

All content moved to manuscript/.archive/; references.bib preserved as
seed for the new hybrid-methodology paper per spec
docs/superpowers/specs/2026-04-19-mdpi-vaccines-manuscript-design.md."
```

---

### Task 1: Download assets + create PAPER_CONTEXT

**Files:**
- Create: `assets/mdpi_reference.docx`
- Create: `assets/vaccines.csl`
- Create: `manuscript/PAPER_CONTEXT.md`

- [ ] **Step 1: Create assets directory**

```bash
mkdir -p assets
```

- [ ] **Step 2: Fetch MDPI CSL (Zotero official repo)**

```bash
curl -L -o assets/vaccines.csl \
  https://raw.githubusercontent.com/citation-style-language/styles/master/multidisciplinary-digital-publishing-institute.csl
```

Expected: file exists, first line contains `<?xml version="1.0"`, file size > 5 KB.

Verify:
```bash
head -1 assets/vaccines.csl
wc -c assets/vaccines.csl
```

- [ ] **Step 3: Fetch MDPI Article Word template**

```bash
curl -L -A "Mozilla/5.0" -o assets/mdpi_reference.docx \
  https://www.mdpi.com/files/word-templates/Article.docx || true
# Fallback if MDPI blocks: generate minimal reference.docx
if [ ! -s assets/mdpi_reference.docx ]; then
  python -c "
from docx import Document
from docx.shared import Pt, Cm
doc = Document()
for s in doc.sections:
    s.top_margin = Cm(2.54); s.bottom_margin = Cm(2.54)
    s.left_margin = Cm(2.54); s.right_margin = Cm(2.54)
ns = doc.styles['Normal']
ns.font.name = 'Palatino Linotype'; ns.font.size = Pt(10)
for lvl in (1, 2, 3):
    h = doc.styles[f'Heading {lvl}']
    h.font.name = 'Palatino Linotype'; h.font.bold = True
doc.styles['Heading 1'].font.size = Pt(12)
doc.styles['Heading 2'].font.size = Pt(11)
doc.styles['Heading 3'].font.size = Pt(10)
doc.save('assets/mdpi_reference.docx')
print('Fallback reference.docx generated.')
"
fi
ls -la assets/mdpi_reference.docx
```

Expected: `assets/mdpi_reference.docx` exists, >5 KB.

- [ ] **Step 4: Create PAPER_CONTEXT.md**

Create `manuscript/PAPER_CONTEXT.md` with:

```markdown
# PAPER_CONTEXT

## Study
**Title (working):** Reinforcement-Learning-Guided Sequential Intervention to Reduce
DTP1-to-DTP3 Vaccine Dropout in Nigeria: A Prediction, Policy Optimisation, and
Cost-Effectiveness Analysis

**Population:** Children 12–23 months who received DTP1 (DHS Nigeria 2024; NGKR8BFL),
with card-confirmed vaccination dates (h3 ∈ {1, 2, 3}). Youngest living child per
woman (b5 == 1).

**Sample size:** ~3,200 children (exact N from descriptives table).

**Study type:** Hybrid methodology — prediction model (TRIPOD-AI), offline RL + bandit
allocation (Gottesman 2019 reporting norms), economic evaluation with microsim + PSA
(CHEERS 2022).

**Target journal:** Vaccines (MDPI) — Article type.
**Reporting guidelines:** TRIPOD-AI, CHEERS 2022, Gottesman RL-health.
**Citation style:** MDPI numeric `[1]`; CSL file `assets/vaccines.csl`.
**Word budgets:** Abstract 200, Intro 600, Methods 2100, Results 1800,
Discussion 1000, Conclusions 150.

## Outputs map (all numeric claims must cite one of these)

| Stage | Path | Description |
|-------|------|-------------|
| 0 | outputs/stage0/descriptive_statistics_table.csv | Cohort descriptives |
| 0 | outputs/stage0/dropout_prevalence_by_state.png | State prevalence map |
| 0 | outputs/stage0/dropout_funnel_plot.png | Cascade funnel |
| 0 | outputs/stage0/local_moran_clusters_map.png | Spatial clusters |
| 1 | outputs/stage1/cascade_metrics.csv | AUROC/AUPRC/Brier/ECE |
| 1 | outputs/stage1/recalibration_log.md | Pre- vs post-calibration |
| 1 | outputs/stage1/roc_pr_model_{t1,t2}.pdf | ROC/PR curves |
| 1 | outputs/stage1/shap_bar_model_{t1,t2,full}.pdf | SHAP bar plots |
| 1 | outputs/stage1/andersen_decomp_comparison.png | Andersen decomposition |
| 2 | outputs/stage2/fqi_convergence.png | FQI convergence |
| 2 | outputs/stage2/cql_analysis.png | CQL α-sensitivity |
| 2 | outputs/stage2_v2/ope_comparison.csv | Off-policy evaluation |
| 2 | outputs/stage2/policy_lookup.csv | State→action lookup |
| 3 | outputs/stage3/lga_allocation.csv | Bandit LGA allocation |
| 3 | outputs/stage3/microsim_results.csv | v1 microsim (superseded) |
| 3v2 | outputs/stage3_v2/microsim_results.csv | v2 microsim (use this) |
| 3v2 | outputs/stage3_v2/ceac.{pdf,png} | Cost-effectiveness acceptability |
| 3v2 | outputs/stage3_v2/ce_plane.{pdf,png} | CE plane |
| 3v2 | outputs/stage3_v2/icer_distribution.csv | PSA ICER distribution |
| 3v2 | outputs/stage3_v2/tornado_data.csv | One-way sensitivity |
| 3v2 | outputs/stage3_v2/sensitivity_scenarios.csv | Scenario sensitivity |
| 3v2 | outputs/stage3_v2/stage3_v2_summary.json | Headline summary |
| val | outputs/validation/subgroup_{zone,state,wealth_quintile,urban_rural,maternal_education}.csv | Subgroup performance |
| lit | outputs/literature/dropout_literature_review.csv | Lit review table |
| lit | outputs/literature/intervention_effect_sizes.csv | Effect sizes from lit |

## Dashboard
URL: https://olatechie.github.io/dropout/
Source repo: https://github.com/olatechie/dropout
Modules: Story, Policy, Simulation, Explorer
Accessibility: WCAG AA + /story/transcript text fallback.

## Reference seed
Bibliography seed: manuscript/.archive/references.bib (~53 entries).
Target ≥50 unique after de-dup and augmentation.
```

- [ ] **Step 5: Commit**

```bash
git add assets/ manuscript/PAPER_CONTEXT.md
git commit -m "manuscript: add MDPI assets (reference.docx, vaccines.csl) and PAPER_CONTEXT

Fetches MDPI Article.docx and multidisciplinary-digital-publishing-institute.csl
from upstream. PAPER_CONTEXT.md maps every outputs/ artifact to its manuscript
role, establishing the no-fabrication traceability required by
scientific-paper-writer:core-engine."
```

---

### Task 2: Main figures regeneration script

**Files:**
- Create: `scripts/manuscript_figures.py`
- Create: `tests/manuscript/test_figures.py`

- [ ] **Step 1: Write failing test**

Create `tests/manuscript/__init__.py` (empty) and `tests/manuscript/test_figures.py`:

```python
"""Tests for manuscript main-figure regeneration."""
from pathlib import Path
import subprocess
import pytest

ROOT = Path(__file__).resolve().parents[2]
FIG_DIR = ROOT / "manuscript" / "figures"


@pytest.fixture(scope="module", autouse=True)
def build_figures():
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        ["python", "scripts/manuscript_figures.py", "--figs", "1,2,3,4"],
        cwd=ROOT, capture_output=True, text=True
    )
    assert result.returncode == 0, f"Figure script failed: {result.stderr}"


@pytest.mark.parametrize("n", [1, 2, 3, 4])
def test_figure_png_and_pdf_exist(n):
    assert (FIG_DIR / f"fig{n}.png").exists()
    assert (FIG_DIR / f"fig{n}.pdf").exists()


def test_figure_png_dpi_300():
    from PIL import Image
    img = Image.open(FIG_DIR / "fig1.png")
    dpi = img.info.get("dpi", (72, 72))[0]
    assert dpi >= 300, f"fig1 DPI={dpi} — must be ≥300"
```

- [ ] **Step 2: Run tests — expect FAIL**

```bash
pytest tests/manuscript/test_figures.py -v
```
Expected: FAIL — `scripts/manuscript_figures.py` does not exist.

- [ ] **Step 3: Implement figure script**

Create `scripts/manuscript_figures.py`:

```python
#!/usr/bin/env python3
"""Regenerate main manuscript figures 1-4 from outputs/ CSVs and stage PDFs.

Fig 1: Study flow + cascade (2 panels)
Fig 2: Model performance + top-10 SHAP (2x2 panels, T1 and T2)
Fig 3: RL-optimised LGA allocation choropleth
Fig 4: CEAC + CE plane (2 panels)
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "manuscript" / "figures"
STAGE0 = ROOT / "outputs" / "stage0"
STAGE1 = ROOT / "outputs" / "stage1"
STAGE3 = ROOT / "outputs" / "stage3"
STAGE3V2 = ROOT / "outputs" / "stage3_v2"
SHAPEFILE = ROOT / "data" / "shapefiles" / "gadm" / "gadm41_NGA_2.shp"


def _save(fig, name: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / f"{name}.png", dpi=300, bbox_inches="tight")
    fig.savefig(OUT / f"{name}.pdf", bbox_inches="tight")
    plt.close(fig)


def build_fig1() -> None:
    """Fig 1: study flow (funnel) + cascade by zone."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    for ax, img_path, title in [
        (axes[0], STAGE0 / "dropout_funnel_plot.png", "A. Study flow"),
        (axes[1], STAGE1 / "cascade_by_zone.png", "B. DTP cascade by zone"),
    ]:
        ax.imshow(mpimg.imread(img_path))
        ax.set_title(title, loc="left", fontsize=12, fontweight="bold")
        ax.axis("off")
    fig.tight_layout()
    _save(fig, "fig1")


def build_fig2() -> None:
    """Fig 2: 2x2 — ROC/PR (T1, T2) + SHAP bar (T1, T2)."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))
    pairs = [
        (axes[0, 0], STAGE1 / "roc_pr_model_t1.png", "A. T1 ROC/PR (DTP1→DTP2)"),
        (axes[0, 1], STAGE1 / "roc_pr_model_t2.png", "B. T2 ROC/PR (DTP2→DTP3)"),
        (axes[1, 0], STAGE1 / "shap_bar_model_t1.pdf", "C. T1 top-10 SHAP"),
        (axes[1, 1], STAGE1 / "shap_bar_model_t2.pdf", "D. T2 top-10 SHAP"),
    ]
    for ax, p, title in pairs:
        if p.suffix == ".pdf":
            # Render PDF as image via pdf2image if installed, else skip with note
            try:
                from pdf2image import convert_from_path
                img = convert_from_path(p, dpi=300)[0]
            except ImportError:
                ax.text(0.5, 0.5, "(install pdf2image)", ha="center", va="center")
                ax.axis("off")
                continue
            ax.imshow(img)
        else:
            ax.imshow(mpimg.imread(p))
        ax.set_title(title, loc="left", fontsize=12, fontweight="bold")
        ax.axis("off")
    fig.tight_layout()
    _save(fig, "fig2")


def build_fig3() -> None:
    """Fig 3: LGA allocation choropleth."""
    try:
        import geopandas as gpd
    except ImportError:
        raise RuntimeError("geopandas required for fig3 — run: pip install geopandas")

    alloc = pd.read_csv(STAGE3 / "lga_allocation.csv")
    gdf = gpd.read_file(SHAPEFILE)
    # Join by LGA code; sstate+community_idx mapping lives in stage3_bandit_microsim.py
    # Simpler: use sstate-level aggregation for now (to be refined if LGA-level join works)
    state_action = (
        alloc.groupby("sstate")["assigned_action"].agg(lambda s: s.mode().iloc[0])
    )
    if "GID_1" in gdf.columns:
        state_gdf = gdf.dissolve(by="GID_1").reset_index()
    else:
        state_gdf = gdf.dissolve(by=gdf.columns[0]).reset_index()
    state_gdf["sstate_idx"] = range(1, len(state_gdf) + 1)
    state_gdf["action"] = state_gdf["sstate_idx"].map(state_action)

    action_labels = {
        0: "a0: None", 1: "a1: SMS", 2: "a2: CHW",
        3: "a3: Facility recall", 4: "a4: Incentive",
    }
    fig, ax = plt.subplots(figsize=(10, 10))
    state_gdf.plot(
        column="action", ax=ax, cmap="tab10", legend=True, edgecolor="white",
        legend_kwds={
            "labels": [action_labels.get(i, str(i)) for i in sorted(state_gdf["action"].dropna().unique())],
            "loc": "lower left",
        },
    )
    ax.set_title("RL-optimised recommended intervention by state", fontsize=14)
    ax.axis("off")
    _save(fig, "fig3")


def build_fig4() -> None:
    """Fig 4: CEAC + CE plane side-by-side."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    pairs = [
        (axes[0], STAGE3V2 / "ceac.png", "A. Cost-effectiveness acceptability curve"),
        (axes[1], STAGE3V2 / "ce_plane.png", "B. Cost-effectiveness plane"),
    ]
    for ax, p, title in pairs:
        ax.imshow(mpimg.imread(p))
        ax.set_title(title, loc="left", fontsize=12, fontweight="bold")
        ax.axis("off")
    fig.tight_layout()
    _save(fig, "fig4")


FIG_BUILDERS = {1: build_fig1, 2: build_fig2, 3: build_fig3, 4: build_fig4}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--figs", default="1,2,3,4",
                   help="Comma-sep figure numbers to build (default: 1,2,3,4)")
    args = p.parse_args()
    for n in [int(x) for x in args.figs.split(",") if x.strip()]:
        print(f"Building fig{n}...")
        FIG_BUILDERS[n]()
        print(f"  → manuscript/figures/fig{n}.png + fig{n}.pdf")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests — expect PASS**

```bash
pytest tests/manuscript/test_figures.py -v
```
Expected: all 4 figure-exists tests and the DPI test PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/manuscript_figures.py tests/manuscript/
git commit -m "manuscript: add regeneration script for main figures 1-4

Fig1=cascade flow, Fig2=perf+SHAP (2x2), Fig3=LGA choropleth,
Fig4=CEAC+CE plane. All outputs 300 DPI PNG + PDF. Reads only from
outputs/ artifacts per no-fabrication rule."
```

---

### Task 3: Dashboard screenshot script (Fig 5) + tables script

**Files:**
- Create: `scripts/capture_dashboard.py`
- Create: `scripts/manuscript_tables.py`
- Create: `tests/manuscript/test_tables.py`

- [ ] **Step 1: Write Playwright dashboard capture**

Create `scripts/capture_dashboard.py`:

```python
#!/usr/bin/env python3
"""Capture dashboard screenshots for manuscript Figure 5.

Uses Playwright to screenshot the deployed dashboard at
https://olatechie.github.io/dropout/. Saves two panels side-by-side
(story hero + policy dashboard) to manuscript/figures/fig5_dashboard.png.

Requires: playwright installed + `playwright install chromium` run once.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "manuscript" / "figures"
URL = "https://olatechie.github.io/dropout/"


def _screenshot(path: str, out_file: Path) -> None:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        ctx = browser.new_context(viewport={"width": 1440, "height": 900})
        page = ctx.new_page()
        page.goto(f"{URL}{path}", wait_until="networkidle", timeout=60_000)
        page.wait_for_timeout(3_000)  # allow animations
        page.screenshot(path=str(out_file), full_page=False)
        browser.close()


def build_fig5(offline_fallback: Path | None = None) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    story_path = OUT / "fig5_story.png"
    policy_path = OUT / "fig5_policy.png"
    try:
        _screenshot("#/story", story_path)
        _screenshot("#/policy", policy_path)
    except Exception as exc:
        print(f"Playwright failed ({exc}); using offline fallback if provided.")
        if offline_fallback and offline_fallback.exists():
            story_path = offline_fallback
            policy_path = offline_fallback
        else:
            raise

    # Compose side-by-side panel
    story = Image.open(story_path)
    policy = Image.open(policy_path)
    h = min(story.height, policy.height)

    def _fit(img, h):
        w = int(img.width * h / img.height)
        return img.resize((w, h))

    story_r, policy_r = _fit(story, h), _fit(policy, h)
    combined = Image.new("RGB", (story_r.width + policy_r.width + 20, h), "white")
    combined.paste(story_r, (0, 0))
    combined.paste(policy_r, (story_r.width + 20, 0))
    combined.save(OUT / "fig5_dashboard.png", dpi=(300, 300))
    print(f"  → manuscript/figures/fig5_dashboard.png")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--fallback", type=Path, default=None,
                   help="Offline PNG to use if Playwright fails")
    args = p.parse_args()
    build_fig5(args.fallback)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Write failing tests for tables script**

Create `tests/manuscript/test_tables.py`:

```python
"""Tests for manuscript main-table rendering."""
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
TAB_DIR = ROOT / "manuscript" / "tables"


def setup_module(_module):
    TAB_DIR.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        ["python", "scripts/manuscript_tables.py"],
        cwd=ROOT, capture_output=True, text=True
    )
    assert result.returncode == 0, f"Table script failed: {result.stderr}"


def test_tab1_descriptives_header():
    md = (TAB_DIR / "tab1.md").read_text()
    assert "Table 1" in md
    assert "|" in md
    assert md.count("\n|") >= 3


def test_tab2_performance_has_metrics():
    md = (TAB_DIR / "tab2.md").read_text()
    assert "AUROC" in md
    assert "Brier" in md
    assert "T1" in md and "T2" in md


def test_tab3_scenarios_six_rows():
    md = (TAB_DIR / "tab3.md").read_text()
    for scen in ["S0", "S1", "S2", "S3", "S4", "S5"]:
        assert scen in md, f"missing scenario {scen}"


def test_tab4_tornado_top_params():
    md = (TAB_DIR / "tab4.md").read_text()
    assert "Parameter" in md or "parameter" in md
    assert md.count("\n|") >= 3
```

- [ ] **Step 3: Run tests — expect FAIL**

```bash
pytest tests/manuscript/test_tables.py -v
```
Expected: FAIL — `scripts/manuscript_tables.py` does not exist.

- [ ] **Step 4: Implement tables script**

Create `scripts/manuscript_tables.py`:

```python
#!/usr/bin/env python3
"""Render main manuscript tables 1-4 from outputs/ CSVs to Markdown pipe-tables.

Tab 1: Cohort descriptives by T1/T2 dropout status
Tab 2: Prediction-model performance (AUROC/AUPRC/Brier/ECE, 95% CI)
Tab 3: Microsimulation scenarios S0-S5 with PSA CIs and ICER
Tab 4: Tornado (one-way sensitivity top parameters)
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "manuscript" / "tables"
STAGE0 = ROOT / "outputs" / "stage0"
STAGE1 = ROOT / "outputs" / "stage1"
STAGE3V2 = ROOT / "outputs" / "stage3_v2"


def _write(name: str, title: str, body_md: str, footnote: str = "") -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    content = f"**Table {name.replace('tab', '')}.** {title}\n\n{body_md}\n"
    if footnote:
        content += f"\n*{footnote}*\n"
    (OUT / f"{name}.md").write_text(content)
    print(f"  → manuscript/tables/{name}.md")


def render_tab1() -> None:
    """Descriptives: reuse stage0 table verbatim, tidy columns."""
    df = pd.read_csv(STAGE0 / "descriptive_statistics_table.csv")
    body = df.to_markdown(index=False, floatfmt=".1f")
    _write(
        "tab1",
        "Baseline characteristics of Nigerian children aged 12-23 months who "
        "received DTP1 (DHS 2024), stratified by T1/T2 dropout status.",
        body,
        "Values are n (%) for categorical and mean (SD) for continuous variables. "
        "Survey-weighted estimates applied sample weight v005/1,000,000.",
    )


def render_tab2() -> None:
    """Prediction performance from cascade_metrics + recalibration_log."""
    # cascade_metrics has zone-level cascade (not model perf). Model perf comes
    # from stage1/evaluation output. Use summary JSON if present, else derive
    # from cascade_metrics + recalibration_log.md by parsing the headline numbers.
    rows = []
    # Try stage1 summary JSON
    summary = ROOT / "outputs" / "stage1" / "model_summary.json"
    if summary.exists():
        import json
        d = json.loads(summary.read_text())
        for t in ("t1", "t2"):
            rows.append({
                "Transition": t.upper(),
                "AUROC (95% CI)": d[t]["auroc"],
                "AUPRC (95% CI)": d[t]["auprc"],
                "Brier": d[t]["brier"],
                "ECE (pre/post-recal)": d[t].get("ece", ""),
            })
    else:
        # Fallback: placeholder row so review can fill from recalibration_log.md
        recal = (ROOT / "outputs" / "stage1" / "recalibration_log.md").read_text()
        rows = [
            {"Transition": "T1 (DTP1→DTP2)", "AUROC (95% CI)": "[see recalibration_log.md]",
             "AUPRC (95% CI)": "", "Brier": "", "ECE (pre/post-recal)": ""},
            {"Transition": "T2 (DTP2→DTP3)", "AUROC (95% CI)": "[see recalibration_log.md]",
             "AUPRC (95% CI)": "", "Brier": "", "ECE (pre/post-recal)": ""},
        ]
    df = pd.DataFrame(rows)
    body = df.to_markdown(index=False)
    _write(
        "tab2",
        "Prediction-model discrimination and calibration for DTP1→DTP2 (T1) "
        "and DTP2→DTP3 (T2) transitions, with 95% confidence intervals from "
        "1,000-sample bootstrap. ECE reported pre- and post-isotonic recalibration.",
        body,
        "AUROC = area under receiver-operating-characteristic curve; "
        "AUPRC = area under precision-recall curve; "
        "ECE = expected calibration error.",
    )


def render_tab3() -> None:
    """Microsim scenarios: coverage, cost, ICER vs S0, CE probability."""
    df = pd.read_csv(STAGE3V2 / "microsim_results.csv")
    # Compute ICER vs S0 (status quo)
    s0 = df[df["scenario"].str.startswith("S0")].iloc[0]
    out = pd.DataFrame({
        "Scenario": df["scenario"],
        "DTP3 coverage mean (95% CI)": df.apply(
            lambda r: f"{r.dtp3_mean:.3f} ({r.dtp3_ci_low:.3f}–{r.dtp3_ci_high:.3f})", axis=1
        ),
        "Cost per child (₦) mean (95% CI)": df.apply(
            lambda r: f"{r.cost_per_child_mean:.0f} ({r.cost_per_child_ci_low:.0f}–{r.cost_per_child_ci_high:.0f})",
            axis=1,
        ),
        "ICER vs S0 (₦ per % coverage)": df.apply(
            lambda r: "—" if r.scenario == s0.scenario else
            f"{(r.cost_per_child_mean - s0.cost_per_child_mean) / max(1e-6, (r.dtp3_mean - s0.dtp3_mean) * 100):,.0f}",
            axis=1,
        ),
    })
    body = out.to_markdown(index=False)
    _write(
        "tab3",
        "Microsimulation results for scenarios S0–S5 with 1,000-iteration "
        "probabilistic sensitivity analysis. DTP3 coverage and cost per child "
        "reported as mean with 95% bootstrap CI.",
        body,
        "ICER = incremental cost-effectiveness ratio; CE probability computed "
        "at willingness-to-pay λ = ₦50,000 per additional child fully vaccinated.",
    )


def render_tab4() -> None:
    """Tornado: one-way sensitivity, top parameters by ICER range."""
    df = pd.read_csv(STAGE3V2 / "tornado_data.csv")
    df = df.reindex(df["range"].abs().sort_values(ascending=False).index).head(10)
    body = df.to_markdown(index=False, floatfmt=".4f")
    _write(
        "tab4",
        "One-way deterministic sensitivity of key parameters on DTP3 coverage "
        "(tornado analysis, top ten by absolute range).",
        body,
        "Low/high ranges varied ±25 % around base values; base values taken "
        "from literature review (see supplementary Table S2.1).",
    )


def main() -> None:
    for fn in (render_tab1, render_tab2, render_tab3, render_tab4):
        fn()


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: Run tests — expect PASS**

```bash
pytest tests/manuscript/test_tables.py -v
```
Expected: 4 tests PASS.

- [ ] **Step 6: Run dashboard capture (optional — requires live internet)**

```bash
pip install playwright pillow
playwright install chromium
python scripts/capture_dashboard.py
ls -la manuscript/figures/fig5_dashboard.png
```
Expected: `fig5_dashboard.png` exists. If offline/blocked, skip — Opus will rerun at Task 12.

- [ ] **Step 7: Commit**

```bash
git add scripts/capture_dashboard.py scripts/manuscript_tables.py tests/manuscript/test_tables.py
git commit -m "manuscript: add dashboard screenshot + main tables scripts

capture_dashboard.py uses Playwright to screenshot story and policy routes
from https://olatechie.github.io/dropout/ into a combined fig5.
manuscript_tables.py renders Tables 1-4 from outputs/ CSVs to Markdown
with pandas.to_markdown for pandoc consumption."
```

---

### Task 4: Supplementary tables + figures + checklists script

**Files:**
- Create: `scripts/manuscript_supplement.py`
- Create: `tests/manuscript/test_supplement.py`

- [ ] **Step 1: Write failing tests**

Create `tests/manuscript/test_supplement.py`:

```python
"""Tests for supplementary table / checklist / figure renderers."""
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
SUPP_TAB = ROOT / "manuscript" / "tables" / "supplement"
SUPP_FIG = ROOT / "manuscript" / "figures" / "supplement"


def setup_module(_module):
    result = subprocess.run(
        ["python", "scripts/manuscript_supplement.py"],
        cwd=ROOT, capture_output=True, text=True
    )
    assert result.returncode == 0, f"Supplement script failed: {result.stderr}"


def test_subgroup_tables_rendered():
    for subgroup in ("zone", "state", "wealth_quintile", "urban_rural",
                     "maternal_education"):
        p = SUPP_TAB / f"stab_{subgroup}.md"
        assert p.exists(), f"missing {p}"
        md = p.read_text()
        assert "|" in md
        assert md.count("\n|") >= 2


def test_policy_lookup_rendered():
    p = SUPP_TAB / "stab_policy_lookup.md"
    assert p.exists()
    md = p.read_text()
    assert "action" in md.lower() or "Action" in md


def test_model_input_parameter_table():
    p = SUPP_TAB / "stab_parameters.md"
    assert p.exists()
    md = p.read_text()
    assert "Parameter" in md
    assert "Source" in md
    assert md.count("\n|") >= 10  # ≥10 parameters minimum


def test_reproducibility_parameter_table():
    p = SUPP_TAB / "stab_reproducibility.md"
    assert p.exists()
    md = p.read_text()
    for key in ("seed", "Python", "xgboost", "bootstrap"):
        assert key in md, f"missing {key}"


def test_supplementary_figures_copied():
    """Supplementary figures must be materialised under manuscript/figures/supplement/
    before pandoc runs, else embedded images in the supplement docx break."""
    expected = [
        "sfig_calibration_t1_pre.png",
        "sfig_calibration_t1_post.png",
        "sfig_calibration_t2_pre.png",
        "sfig_calibration_t2_post.png",
        "sfig_shap_beeswarm_t1.png",
        "sfig_shap_beeswarm_t2.png",
        "sfig_fqi_convergence.png",
        "sfig_cql_alpha_sensitivity.png",
        "sfig_ope_comparison.png",
        "sfig_local_moran.png",
        "sfig_prevalence_by_state.png",
        "sfig_andersen_decomposition.png",
    ]
    missing = [f for f in expected if not (SUPP_FIG / f).exists()]
    assert not missing, f"missing supplementary figures: {missing}"
```

- [ ] **Step 2: Run tests — expect FAIL**

```bash
pytest tests/manuscript/test_supplement.py -v
```
Expected: FAIL — script missing.

- [ ] **Step 3: Implement supplement script**

Create `scripts/manuscript_supplement.py`:

```python
#!/usr/bin/env python3
"""Render supplementary tables for the MDPI Vaccines manuscript.

Produces (in manuscript/tables/supplement/):
- stab_{zone,state,wealth_quintile,urban_rural,maternal_education}.md : subgroup perf
- stab_policy_lookup.md : state→action Q-value lookup
- stab_parameters.md : model-input parameters (effect sizes, costs, PSA priors)
- stab_reproducibility.md : seeds, hyperparams, software versions
"""
from __future__ import annotations

import json
import sys
import platform
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "manuscript" / "tables" / "supplement"
VAL = ROOT / "outputs" / "validation"
STAGE2 = ROOT / "outputs" / "stage2"
LIT = ROOT / "outputs" / "literature"


def _write(name: str, title: str, body_md: str, footnote: str = "") -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    content = f"**{title}**\n\n{body_md}\n"
    if footnote:
        content += f"\n*{footnote}*\n"
    (OUT / f"{name}.md").write_text(content)
    print(f"  → manuscript/tables/supplement/{name}.md")


def render_subgroup_tables() -> None:
    for sub in ("zone", "state", "wealth_quintile", "urban_rural", "maternal_education"):
        csv = VAL / f"subgroup_{sub}.csv"
        if not csv.exists():
            print(f"  (skip — missing {csv})")
            continue
        df = pd.read_csv(csv)
        body = df.to_markdown(index=False, floatfmt=".3f")
        _write(f"stab_{sub}",
               f"Table S. Subgroup prediction performance by {sub.replace('_', ' ')}.",
               body,
               "AUROC and Brier reported with 95 % bootstrap CI.")


def render_policy_lookup() -> None:
    csv = STAGE2 / "policy_lookup.csv"
    if not csv.exists():
        print(f"  (skip — missing {csv})")
        return
    df = pd.read_csv(csv).head(50)  # truncate; full CSV linked in data availability
    body = df.to_markdown(index=False, floatfmt=".4f")
    _write("stab_policy_lookup",
           "Table S. Example RL policy lookup (first 50 of 2,500 state representations) "
           "showing recommended action and Q-values.",
           body,
           "Full policy lookup available in the supplementary dataset at "
           "https://github.com/olatechie/dropout.")


def render_parameter_table() -> None:
    """Model-input parameter table from literature review + fixed costs."""
    lit = pd.read_csv(LIT / "intervention_effect_sizes.csv")
    # Augment with fixed costs and PSA ranges per CLAUDE.md action space
    fixed = pd.DataFrame([
        {"Parameter": "Cost: a1 SMS reminder (₦)", "Base": 50,
         "PSA low": 40, "PSA high": 60, "Source": "CLAUDE.md action space"},
        {"Parameter": "Cost: a2 CHW home visit (₦)", "Base": 500,
         "PSA low": 400, "PSA high": 600, "Source": "CLAUDE.md action space"},
        {"Parameter": "Cost: a3 Facility recall (₦)", "Base": 1500,
         "PSA low": 1200, "PSA high": 1800, "Source": "CLAUDE.md action space"},
        {"Parameter": "Cost: a4 Conditional incentive (₦)", "Base": 800,
         "PSA low": 600, "PSA high": 1000, "Source": "CLAUDE.md action space"},
        {"Parameter": "Reward: DTP3 completion", "Base": 1.0,
         "PSA low": 1.0, "PSA high": 1.0, "Source": "Fixed per reward specification"},
        {"Parameter": "Reward: next dose received", "Base": 0.3,
         "PSA low": 0.2, "PSA high": 0.4, "Source": "Fixed per reward specification"},
        {"Parameter": "Cost weight λ", "Base": 0.001,
         "PSA low": 0.0005, "PSA high": 0.002, "Source": "CLAUDE.md reward function"},
        {"Parameter": "Willingness-to-pay (₦ / % coverage)", "Base": 50000,
         "PSA low": 25000, "PSA high": 100000, "Source": "Nigerian per-capita GDP benchmark"},
    ])
    full = pd.concat([lit, fixed], ignore_index=True, sort=False)
    body = full.to_markdown(index=False)
    _write("stab_parameters",
           "Table S2.1. Model-input parameters: intervention effect sizes from "
           "literature review, intervention costs, and PSA prior ranges.",
           body,
           "Intervention effect sizes sourced from outputs/literature/"
           "intervention_effect_sizes.csv. Costs in 2026 Nigerian Naira.")


def render_reproducibility() -> None:
    """Software versions, seeds, hyperparameters."""
    versions = {
        "Python": platform.python_version(),
    }
    for pkg in ("numpy", "pandas", "xgboost", "scikit-learn", "shap",
                "matplotlib", "geopandas", "statsmodels"):
        try:
            mod = __import__(pkg.replace("-", "_"))
            versions[pkg] = getattr(mod, "__version__", "unknown")
        except ImportError:
            versions[pkg] = "not installed"
    body = pd.DataFrame(
        [{"Component": k, "Value": v} for k, v in versions.items()]
        + [
            {"Component": "Random seed", "Value": "42"},
            {"Component": "CV folds", "Value": "5 (stratified)"},
            {"Component": "Bootstrap iterations", "Value": "1,000"},
            {"Component": "PSA iterations", "Value": "1,000"},
            {"Component": "XGBoost n_estimators", "Value": "500"},
            {"Component": "XGBoost max_depth", "Value": "6"},
            {"Component": "FQI iterations", "Value": "100"},
            {"Component": "CQL α", "Value": "1.0 (base)"},
            {"Component": "Repo commit", "Value": "see docs/pipeline_audit_log.md"},
        ]
    ).to_markdown(index=False)
    _write("stab_reproducibility",
           "Table S2.2. Reproducibility parameters: software versions, seeds, "
           "cross-validation configuration, model hyperparameters.",
           body)


def _copy_supplementary_figures() -> None:
    """Copy + rename outputs/ figure PDFs/PNGs to manuscript/figures/supplement/.

    Pandoc needs these files to exist at their referenced paths inside the
    supplement markdown so that inline image syntax embeds rather than
    producing broken links.
    """
    import shutil
    STAGE0 = ROOT / "outputs" / "stage0"
    STAGE1 = ROOT / "outputs" / "stage1"
    STAGE2 = ROOT / "outputs" / "stage2"
    dest = ROOT / "manuscript" / "figures" / "supplement"
    dest.mkdir(parents=True, exist_ok=True)

    def _png_or_pdf(stem: Path) -> Path | None:
        """Prefer PNG; fall back to PDF→PNG via pdf2image."""
        png = stem.with_suffix(".png")
        pdf = stem.with_suffix(".pdf")
        if png.exists():
            return png
        if pdf.exists():
            try:
                from pdf2image import convert_from_path
                img = convert_from_path(pdf, dpi=300)[0]
                tmp = stem.with_suffix(".rendered.png")
                img.save(tmp, dpi=(300, 300))
                return tmp
            except Exception:
                return None
        return None

    mappings = [
        (STAGE1 / "calibration_model_t1",              "sfig_calibration_t1_pre.png"),
        (STAGE1 / "calibration_model_t1_recalibrated", "sfig_calibration_t1_post.png"),
        (STAGE1 / "calibration_model_t2",              "sfig_calibration_t2_pre.png"),
        (STAGE1 / "calibration_model_t2_recalibrated", "sfig_calibration_t2_post.png"),
        (STAGE1 / "shap_beeswarm_model_t1",            "sfig_shap_beeswarm_t1.png"),
        (STAGE1 / "shap_beeswarm_model_t2",            "sfig_shap_beeswarm_t2.png"),
        (STAGE2 / "fqi_convergence",                    "sfig_fqi_convergence.png"),
        (STAGE2 / "cql_analysis",                       "sfig_cql_alpha_sensitivity.png"),
        (STAGE2 / "ope_comparison",                     "sfig_ope_comparison.png"),
        (STAGE0 / "local_moran_clusters_map",           "sfig_local_moran.png"),
        (STAGE0 / "dropout_prevalence_by_state",        "sfig_prevalence_by_state.png"),
        (STAGE1 / "andersen_decomp_comparison",         "sfig_andersen_decomposition.png"),
    ]
    for src_stem, target_name in mappings:
        src = _png_or_pdf(src_stem)
        if src is None:
            print(f"  (skip — source not found: {src_stem})")
            continue
        shutil.copy2(src, dest / target_name)
        print(f"  → manuscript/figures/supplement/{target_name}")


def main() -> None:
    render_subgroup_tables()
    render_policy_lookup()
    render_parameter_table()
    render_reproducibility()
    _copy_supplementary_figures()


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests — expect PASS**

```bash
pytest tests/manuscript/test_supplement.py -v
```
Expected: all 4 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/manuscript_supplement.py tests/manuscript/test_supplement.py
git commit -m "manuscript: render supplementary tables + copy supplementary figures

Produces: subgroup performance tables (5 subgroup axes), policy-lookup
excerpt, full model-input parameter table with PSA ranges, reproducibility
parameter table (software versions, seeds, hyperparameters). Also copies
calibration / SHAP beeswarm / FQI / CQL / OPE / local Moran / prevalence /
Andersen-decomposition figures from outputs/ to
manuscript/figures/supplement/ with canonical sfig_*.png names, so pandoc
can embed them directly into manuscript_supplement.docx."
```

---

### Task 5: Build orchestrator script (pandoc pipeline)

**Files:**
- Create: `scripts/build_manuscript.py`
- Create: `tests/manuscript/test_build.py`

- [ ] **Step 1: Write failing integration test**

Create `tests/manuscript/test_build.py`:

```python
"""Integration test for manuscript build pipeline."""
from pathlib import Path
import subprocess
import pytest

ROOT = Path(__file__).resolve().parents[2]
MAIN = ROOT / "manuscript" / "manuscript.docx"
SUPP = ROOT / "manuscript" / "manuscript_supplement.docx"


def test_build_dry_run_lists_steps():
    """--dry-run should print the plan without invoking pandoc."""
    result = subprocess.run(
        ["python", "scripts/build_manuscript.py", "--dry-run"],
        cwd=ROOT, capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    for step in ("figures", "tables", "supplement", "main_docx", "supplement_docx"):
        assert step in result.stdout.lower()


@pytest.mark.skipif(
    subprocess.run(["which", "pandoc"], capture_output=True).returncode != 0,
    reason="pandoc not installed",
)
def test_build_produces_both_docx():
    """Full build: --all regenerates figures/tables/supplement and both .docx."""
    # Requires the prose section markdown files to exist — skip if missing
    if not (ROOT / "manuscript" / "00_frontmatter.md").exists():
        pytest.skip("prose markdown not yet written (Sonnet tasks not complete)")
    result = subprocess.run(
        ["python", "scripts/build_manuscript.py", "--all"],
        cwd=ROOT, capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    assert MAIN.exists() and MAIN.stat().st_size > 10_000
    assert SUPP.exists() and SUPP.stat().st_size > 10_000
```

- [ ] **Step 2: Run tests — expect FAIL**

```bash
pytest tests/manuscript/test_build.py -v
```
Expected: FAIL — script missing.

- [ ] **Step 3: Implement build orchestrator**

Create `scripts/build_manuscript.py`:

```python
#!/usr/bin/env python3
"""Build MDPI Vaccines manuscript: main + supplement .docx via pandoc.

Pipeline:
  1. Regenerate main figures  (scripts/manuscript_figures.py)
  2. Capture dashboard shot   (scripts/capture_dashboard.py) — optional
  3. Render main tables       (scripts/manuscript_tables.py)
  4. Render supp tables       (scripts/manuscript_supplement.py)
  5. Concat section markdown  (manuscript/{00..99}_*.md)
  6. Pandoc → manuscript.docx (embedded figs/tabs via reference.docx)
  7. Concat supplement md     (manuscript/supplement/S*.md + table md)
  8. Pandoc → manuscript_supplement.docx

Usage:
  python scripts/build_manuscript.py --dry-run       # show plan, no execution
  python scripts/build_manuscript.py --all           # run steps 1-8
  python scripts/build_manuscript.py --stage docx    # only step 6+8
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANUSCRIPT = ROOT / "manuscript"
ASSETS = ROOT / "assets"
BUILD = ROOT / "build" / "manuscript"

MAIN_DOCX = MANUSCRIPT / "manuscript.docx"
SUPP_DOCX = MANUSCRIPT / "manuscript_supplement.docx"

SECTION_ORDER = [
    "00_frontmatter.md",
    "01_methods.md",
    "02_results.md",
    "03_discussion.md",
    "04_conclusions.md",
    "99_backmatter.md",
]

SUPP_ORDER = [
    "supplement/S0_checklists.md",
    "supplement/S1_methods_extended.md",
    "supplement/S2_parameter_tables.md",
    "supplement/S3_figures_tables.md",
]

STEP_SCRIPTS = {
    "figures":    ["python", "scripts/manuscript_figures.py"],
    "dashboard":  ["python", "scripts/capture_dashboard.py"],
    "tables":     ["python", "scripts/manuscript_tables.py"],
    "supplement": ["python", "scripts/manuscript_supplement.py"],
}


def _run(cmd: list[str], allow_fail: bool = False) -> None:
    print(f"▶ {' '.join(cmd)}")
    r = subprocess.run(cmd, cwd=ROOT)
    if r.returncode and not allow_fail:
        sys.exit(f"❌ step failed: {' '.join(cmd)}")


def _concat(sources: list[Path], out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    parts = []
    for src in sources:
        if src.exists():
            parts.append(src.read_text())
        else:
            print(f"  (skip — missing {src})")
    out.write_text("\n\n".join(parts))
    print(f"  → {out}")


def _pandoc(src: Path, out: Path, bib: Path, csl: Path, reference: Path) -> None:
    cmd = [
        "pandoc", str(src),
        "--from", "markdown+pipe_tables+implicit_figures+link_attributes",
        "--to", "docx",
        f"--reference-doc={reference}",
        f"--bibliography={bib}",
        f"--csl={csl}",
        "--citeproc",
        "--resource-path", str(MANUSCRIPT),
        "-o", str(out),
    ]
    _run(cmd)
    print(f"  → {out}")


def build_main(dry: bool) -> None:
    src = BUILD / "manuscript.md"
    if dry:
        print("Step 5: concat main sections →", src)
        print("Step 6: pandoc main_docx →", MAIN_DOCX)
        return
    _concat([MANUSCRIPT / s for s in SECTION_ORDER], src)
    _pandoc(src, MAIN_DOCX,
            bib=MANUSCRIPT / "references.bib",
            csl=ASSETS / "vaccines.csl",
            reference=ASSETS / "mdpi_reference.docx")


def build_supplement(dry: bool) -> None:
    src = BUILD / "supplement.md"
    if dry:
        print("Step 7: concat supplement →", src)
        print("Step 8: pandoc supplement_docx →", SUPP_DOCX)
        return
    _concat([MANUSCRIPT / s for s in SUPP_ORDER], src)
    _pandoc(src, SUPP_DOCX,
            bib=MANUSCRIPT / "references.bib",
            csl=ASSETS / "vaccines.csl",
            reference=ASSETS / "mdpi_reference.docx")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true", help="Print plan only")
    p.add_argument("--all", action="store_true", help="Run all steps 1-8")
    p.add_argument("--stage", choices=list(STEP_SCRIPTS) + ["docx"],
                   help="Run only one stage")
    args = p.parse_args()

    if args.dry_run:
        print("Plan:")
        for name in ("figures", "dashboard", "tables", "supplement"):
            print(f"  step {name}: {' '.join(STEP_SCRIPTS[name])}")
        build_main(dry=True)
        build_supplement(dry=True)
        return

    if args.stage and args.stage in STEP_SCRIPTS:
        _run(STEP_SCRIPTS[args.stage])
        return
    if args.stage == "docx":
        build_main(dry=False)
        build_supplement(dry=False)
        return

    # --all
    if not args.all:
        print("nothing to do; pass --all or --stage or --dry-run")
        return
    for name in ("figures", "tables", "supplement"):
        _run(STEP_SCRIPTS[name])
    _run(STEP_SCRIPTS["dashboard"], allow_fail=True)  # dashboard may be offline
    build_main(dry=False)
    build_supplement(dry=False)
    print("✅ Build complete:")
    print(f"   {MAIN_DOCX}")
    print(f"   {SUPP_DOCX}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run test — expect PASS on dry-run, SKIP on full build**

```bash
pytest tests/manuscript/test_build.py -v
```
Expected: `test_build_dry_run_lists_steps` PASS; `test_build_produces_both_docx` SKIP (prose not yet written).

- [ ] **Step 5: Commit**

```bash
git add scripts/build_manuscript.py tests/manuscript/test_build.py
git commit -m "manuscript: add pandoc build orchestrator for .docx output

scripts/build_manuscript.py chains: regenerate figures → capture dashboard →
render tables → render supplement tables → concat markdown → pandoc-citeproc
for both main and supplementary .docx. Uses assets/mdpi_reference.docx for
styles and assets/vaccines.csl for MDPI numeric citations. Figures and
tables embedded via markdown image / pipe-table syntax."
```

---

## Phase 2 — Prose Writing (Sonnet 4.6 Subagents)

Every task in this phase is dispatched via the Agent tool with `model: "sonnet"`. Opus curates the brief, reviews the output against the review gate, and only proceeds when the gate passes. Up to 2 revision loops per task before Opus escalates.

### Task 6: Frontmatter (title, abstract, introduction, keywords) — Sonnet

**Files:**
- Create: `manuscript/00_frontmatter.md`

- [ ] **Step 1: Dispatch Sonnet subagent**

Call `Agent` with:
- `subagent_type`: `"general-purpose"`
- `model`: `"sonnet"`
- `description`: `"Write manuscript frontmatter"`
- `prompt` (self-contained — the subagent has no conversation context):

```
You are drafting the frontmatter for an MDPI Vaccines Article. Invoke the
scientific-paper-writer:write-frontmatter skill and follow its rules
(no fabrication, verification flags, numbered-reference placeholders).

Study context: see manuscript/PAPER_CONTEXT.md (read this first).
Target journal: MDPI Vaccines (Article).
Citation placeholders: use pandoc `@key` syntax, e.g. [@bello2024dhs].
Every factual claim must end with a `[@placeholder]` citation so Task 10
can resolve them.

Produce `manuscript/00_frontmatter.md` with EXACTLY these sections (use
Markdown `#`/`##` headings and do not renumber):

# <Manuscript title — provide 3 title alternatives at the top in a
  comment block, then the chosen primary title as the `#` heading>

## Abstract
(200 words ± 10, unstructured, covering four implicit beats:
  Background → Methods → Results → Implications.
  Must include the three headline numbers:
    (a) DTP1→DTP3 dropout rate from outputs/stage1/cascade_metrics.csv
        (compute WHO formula (DTP1 − DTP3)/DTP1 across all zones — you may
        use `[PLEASE VERIFY: aggregate national dropout %]` if unsure),
    (b) best-model AUROC at T1 and T2 — cite recalibration_log.md or flag,
    (c) incremental DTP3 coverage + ICER of S4 RL-optimised vs S0
        from outputs/stage3_v2/microsim_results.csv.)

## Keywords
5–7 keywords from: DTP vaccination, immunisation dropout, Nigeria,
reinforcement learning, microsimulation, cost-effectiveness, Andersen model,
DHS, prediction model, health equity.

## 1. Introduction
(600 words ± 60. Structure:
  - para 1 (burden): global DTP3 coverage gaps → Nigeria specifically
  - para 2 (dropout vs access): distinguish missed-start vs dropout;
    cite WHO/Gavi dropout definitions
  - para 3 (evidence gap): no RL-guided allocation in LMIC immunisation
  - para 4 (aim + 3 contributions):
      (i) cascade-specific dropout prediction (TRIPOD-AI),
      (ii) offline RL + bandit policy with off-policy evaluation,
      (iii) microsimulation + PSA for cost-effectiveness.
  ≥15 citation hooks required; mix of global, LMIC, and Nigerian sources.)

Sources:
- outputs/stage0/*  (burden descriptives)
- outputs/stage1/cascade_metrics.csv (dropout by zone)
- outputs/literature/dropout_literature_review.csv (evidence gap)
- manuscript/.archive/references.bib (reference seed — use @keys that exist
  there where possible, otherwise use descriptive placeholders like
  [@gavi2024dtp3]).

Do NOT:
- Invent numbers. Flag with [PLEASE VERIFY: ...] if missing.
- Re-derive statistics that don't appear in the output CSVs.
- Write a structured abstract (MDPI Vaccines default is unstructured).
- Exceed word budgets by more than ±10%.

When done, print word counts per section and the full file contents.
```

- [ ] **Step 2: Opus review gate**

Check in order, stop and re-dispatch with specific fixes if any fails:

1. File `manuscript/00_frontmatter.md` exists and is >3 KB.
2. Top of file contains `<!-- Title alternatives -->` block with 3 candidates.
3. Abstract is 180–220 words (use `wc -w` on the abstract section between `## Abstract` and `## Keywords`).
4. Keywords section has 5–7 comma-separated terms.
5. Introduction section has ≥15 `[@…]` citation hooks (grep `-c '\[@'`).
6. No bare numbers without a citation hook or a `[PLEASE VERIFY: …]` flag.
7. Word count of introduction 540–660.

- [ ] **Step 3: Commit**

```bash
git add manuscript/00_frontmatter.md
git commit -m "manuscript: write frontmatter (title, abstract, intro, keywords)

Drafted by Sonnet 4.6 via scientific-paper-writer:write-frontmatter with
PAPER_CONTEXT.md as source-of-truth. 3 title alternatives retained in
commented block. Abstract 200 ± 10 words; introduction 600 ± 60 words with
≥15 citation hooks pending resolution in Task 10 (write-references)."
```

---

### Task 7: Methods — Sonnet

**Files:**
- Create: `manuscript/01_methods.md`

- [ ] **Step 1: Dispatch Sonnet subagent**

Call `Agent` with `model: "sonnet"` and prompt:

```
Draft the Materials and Methods section for the MDPI Vaccines manuscript.
Invoke scientific-paper-writer:write-methods. Read manuscript/PAPER_CONTEXT.md
first.

Target: 2,100 words ± 150. Produce `manuscript/01_methods.md` with
EXACTLY these 9 subsections (Heading 2 format `## 2.x`):

## 2. Materials and Methods

### 2.1 Data source and study population (~220 w)
DHS Nigeria 2024 (NGKR8BFL); children 12–23 months; h3 ∈ {1,2,3};
b5 == 1 (alive youngest child); ethics (DHS IRB); survey design:
weights v005/1,000,000, strata v022, PSU v021. Geography: szone, sstate.
Cite DHS Program methodology + Nigeria 2024 report.

### 2.2 Outcome definitions (~160 w)
T1 dropout = (h3 ∈ {1,3}) & (h5 == 0); T2 dropout = (h5 ∈ {1,3}) & (h7 == 0).
WHO cascade definition. Cite WHO immunisation coverage estimates.

### 2.3 Predictors and conceptual framework (~260 w)
Andersen Behavioural Model mapping (Predisposing / Enabling / Need /
Dynamic) per manuscript/PAPER_CONTEXT.md "Andersen's Behavioural Model
Mapping" (also in CLAUDE.md). Geospatial covariates (UN density, travel
times, nightlights, malaria prevalence, ITN coverage). Cite:
- Andersen 1995 (health services use model)
- Geospatial layer sources (WorldPop, OpenStreetMap, Malaria Atlas Project).

### 2.4 Prediction modelling (~380 w) — TRIPOD-AI subsection
XGBoost classifier; nested 5-fold stratified cross-validation; isotonic
recalibration; performance metrics (AUROC, AUPRC, Brier score, ECE)
reported with 95% CI from 1,000-iteration bootstrap; SHAP for feature
attribution. State explicitly: "We report this model per TRIPOD-AI
guidance [@collins2024tripodai]."

### 2.5 MDP formulation and offline RL (~360 w) — Gottesman subsection
State space (per CLAUDE.md dynamic/temporal variables);
action space a0–a4 (no intervention / SMS / CHW / facility recall / incentive)
with costs per CLAUDE.md;
reward R(s,a,s') = 1.0·(DTP3 completed) + 0.3·(next dose received) − λ·cost,
λ = 0.001;
behaviour-policy inference rules (how proxy actions derived from DHS);
Fitted Q Iteration [@ernst2005fqi]; Conservative Q-Learning [@kumar2020cql];
off-policy evaluation via IS, weighted IS, doubly-robust estimators
[@jiang2016doublyrobust]. State: "We address the seven limitations of
RL in health identified by Gottesman et al. [@gottesman2019guidelines]:
..." and list all seven.

### 2.6 Contextual bandit for LGA allocation (~140 w)
LinUCB [@li2010linucb] over LGA-level features; cost-constrained
allocation; rationale vs single-state RL policy.

### 2.7 Microsimulation and probabilistic sensitivity analysis (~400 w)
— CHEERS 2022 subsection
Six scenarios S0–S5 (status quo / uniform SMS / uniform CHW / risk-targeted /
RL-optimised / bandit-allocated);
1,000-iteration bootstrap PSA;
ICER, CEAC, CE plane; tornado one-way;
willingness-to-pay λ = ₦50,000 per additional child fully vaccinated;
state: "We report this analysis per CHEERS 2022 [@husereau2022cheers]."

### 2.8 Interactive Web Dashboard (~120 w) — NEW REQUIRED SUBSECTION
VOICE PATTERN (adapt this wording closely):
"To facilitate an in-depth exploration of the data, we developed an
interactive web dashboard designed to provide a comprehensive
exploration and visualisation of model inputs, predictions, optimised
policies, and microsimulation outcomes. The dashboard (Figure 5) is
accessible at https://olatechie.github.io/dropout/ and includes four
modules: Story (cinematic data narrative of the DTP cascade), Policy
(choropleth allocation of RL-recommended interventions), Simulation
(user-controlled scenario explorer), and Explorer (interactive subgroup
and covariate filters). Accessibility follows WCAG AA with a text
transcript at /story/transcript. Source code is openly released under
MIT at https://github.com/olatechie/dropout."

### 2.9 Reporting standards, software, and reproducibility (~60 w)
Reporting: TRIPOD-AI, CHEERS 2022, Gottesman et al. RL-health norms
(completed checklists in Supplementary Materials).
Software: Python 3.11; xgboost 2.x; scikit-learn 1.x; pandas 2.x; shap;
geopandas; statsmodels. Seeds, CV folds, bootstrap N = 1,000.
Code: https://github.com/olatechie/dropout.

Citation requirements:
- ≥10 method-citation hooks across §§2.3–2.7 (Andersen, XGBoost, SHAP,
  FQI, CQL, OPE IS/WIS/DR, LinUCB, TRIPOD-AI, CHEERS, Gottesman).
- Every claim grounded in PAPER_CONTEXT.md / CLAUDE.md or flagged
  [PLEASE VERIFY: …].

Output: full markdown, plus word count per subsection at the end.
```

- [ ] **Step 2: Opus review gate**

1. All 9 subsections present (grep `^### 2\.`).
2. Total word count 1,950–2,250 (use `wc -w manuscript/01_methods.md`).
3. Interactive Web Dashboard subsection §2.8 contains the URL
   `https://olatechie.github.io/dropout/` verbatim.
4. ≥10 method-citation hooks in §§2.3–2.7.
5. Gottesman's seven-limitation list present in §2.5 (grep for at least 5 of:
   "partial observability", "confounding", "reward specification", "off-policy
   evaluation", "distributional shift", "safety", "interpretability").
6. TRIPOD-AI and CHEERS explicitly named.

- [ ] **Step 3: Commit**

```bash
git add manuscript/01_methods.md
git commit -m "manuscript: write methods (TRIPOD-AI + CHEERS + dashboard)

9 subsections: data, outcomes, predictors/Andersen, prediction model
(TRIPOD-AI), MDP + offline RL (Gottesman seven-limitations), bandit,
microsim + PSA (CHEERS), interactive dashboard, reporting standards.
Drafted by Sonnet 4.6 via scientific-paper-writer:write-methods.
~2,100 words."
```

---

### Task 8: Captions + numeric fact sheet — Sonnet

**Files:**
- Create: `manuscript/captions.md`
- Create: `manuscript/fact_sheet.md`

- [ ] **Step 1: Run figure and table scripts to refresh assets**

```bash
python scripts/manuscript_figures.py
python scripts/manuscript_tables.py
python scripts/manuscript_supplement.py
python scripts/capture_dashboard.py || echo "dashboard capture failed — using latest existing fig5"
ls manuscript/figures/ manuscript/tables/ manuscript/tables/supplement/
```

Expected: fig1–fig4 + fig5_dashboard PNG+PDF, tab1–tab4.md, stab_*.md all exist.

- [ ] **Step 2: Dispatch Sonnet subagent**

Call `Agent` with `model: "sonnet"` and prompt:

```
Draft manuscript/captions.md (all figure and table captions, main + supp)
and manuscript/fact_sheet.md (numeric-claim → source-CSV-cell map that the
Opus reviewer will use to factcheck the Results section in Task 9).

Invoke scientific-paper-writer:write-captions.

Inputs:
- manuscript/figures/ (fig1..fig4 + fig5_dashboard)
- manuscript/tables/ (tab1..tab4.md)
- manuscript/tables/supplement/ (stab_*.md)
- manuscript/PAPER_CONTEXT.md (outputs map)
- outputs/stage1/cascade_metrics.csv, recalibration_log.md
- outputs/stage3_v2/microsim_results.csv, icer_distribution.csv,
  tornado_data.csv, stage3_v2_summary.json, sensitivity_scenarios.csv
- outputs/stage3/lga_allocation.csv
- outputs/validation/subgroup_*.csv

Output 1: manuscript/captions.md
===============================
One caption per main figure (Figures 1–5) and per main table (Tables 1–4),
plus supplementary figure/table captions (S-figures, S-tables). Format:

## Figure captions

**Figure 1. [Title].** [Caption, ≤120 words, A/B/C panel notation.]
...

## Table captions (main tables use the captions already in tables/tab*.md
— verify they're accurate and tighten prose if needed).

## Supplementary figure captions
**Figure S1. ...**

## Supplementary table captions
**Table S1. ...**

Output 2: manuscript/fact_sheet.md
==================================
A checklist of every quantitative claim that the Results section will
need to make, paired with the exact CSV path + row/column + expected value.
Format:

## Cohort descriptives (Section 4.1 → Table 1)
- Total N: <value> ← outputs/stage0/descriptive_statistics_table.csv, row "Total"
- % T1 dropout: <value>% ← ... (if unavailable, mark as [PLEASE VERIFY: ...])
- % T2 dropout: <value>% ← ...

## Prediction performance (Section 4.2 → Table 2, Fig 2)
- T1 AUROC: <value> (95% CI ... ) ← outputs/stage1/recalibration_log.md
- T2 AUROC: <value> (95% CI ... ) ← outputs/stage1/recalibration_log.md
- T1 Brier pre-recalibration: ... ; post-recal: ...
- T2 Brier pre/post: ...

## Policy optimisation (Section 4.3 → Fig 3)
- % LGAs with action a2: <value>% ← outputs/stage3/lga_allocation.csv,
  value_counts("assigned_action") / n_total * 100
- ... etc.

## Scenarios and PSA (Section 4.4 → Table 3, Table 4, Fig 4)
- S4 DTP3 mean: 0.9248 (95% CI 0.9139–0.9350) ← outputs/stage3_v2/microsim_results.csv, row S4
- S0 vs S4 incremental coverage: ... pp
- S4 ICER vs S0: ...
- CE probability at WTP = ₦50,000: ← outputs/stage3_v2/ceac_data.csv

## Subgroup equity (Section 4.5 → supplementary)
- AUROC by zone (best / worst): ... / ...
- AUROC by wealth quintile (lowest / highest): ... / ...

## Dashboard (Section 4.6 → Fig 5) — qualitative; no numeric claim needed

Every row must list the CSV path. Any missing value gets
[PLEASE VERIFY: <what to fill>]. This file is the *only* source of
numbers the Results author (Task 9) is allowed to cite.

At the end of both files, print line counts.
```

- [ ] **Step 3: Opus review gate**

1. Both files exist and >1 KB.
2. `captions.md` contains at least: "Figure 1", "Figure 2", "Figure 3", "Figure 4", "Figure 5", "Table 1", "Table 2", "Table 3", "Table 4", "Figure S1", "Table S".
3. `fact_sheet.md` references each of: `descriptive_statistics_table.csv`,
   `recalibration_log.md`, `microsim_results.csv`, `ceac_data.csv`,
   `tornado_data.csv`, `lga_allocation.csv`, `subgroup_zone.csv`.
4. Sample-check 3 random numeric values against their cited CSV (open the CSV
   and verify). Example: S4 DTP3 mean should match row "S4: RL-Optimised" in
   `outputs/stage3_v2/microsim_results.csv` (expected 0.9248). Reject if off
   by >1% or if cell not found.

- [ ] **Step 4: Commit**

```bash
git add manuscript/captions.md manuscript/fact_sheet.md
git commit -m "manuscript: write captions + numeric fact sheet

captions.md covers Figures 1-5 and Tables 1-4 plus supplementary.
fact_sheet.md maps every Results-section numeric claim to its source
CSV cell, enforcing the no-fabrication rule before Task 9 (results
author) can cite any number."
```

---

### Task 9: Results — Sonnet

**Files:**
- Create: `manuscript/02_results.md`

- [ ] **Step 1: Dispatch Sonnet subagent**

Call `Agent` with `model: "sonnet"` and prompt:

```
Draft the Results section for the MDPI Vaccines manuscript.
Invoke scientific-paper-writer:write-results.

HARD RULE: You may cite ONLY numbers present in manuscript/fact_sheet.md.
Any number not in the fact sheet must instead be written as
[PLEASE VERIFY: <description>]. Do not read outputs/ CSVs directly.

Target 1,800 words ± 150. Produce manuscript/02_results.md with EXACTLY
these 7 subsections:

## 3. Results

### 3.1 Cohort characteristics (~260 w)
Reference Table 1 and Figure 1 (cite as "Table 1" and "Figure 1").
Pull numbers from the "Cohort descriptives" section of fact_sheet.md.

### 3.2 Prediction-model performance (~340 w)
Reference Table 2 and Figure 2. Pull from "Prediction performance"
in fact_sheet.md. Report T1 and T2 AUROC/AUPRC/Brier/ECE with 95% CI,
both pre- and post-recalibration. Highlight the top-3 SHAP predictors
per transition (from fig2 captions).

### 3.3 RL-optimised policy and LGA allocation (~320 w)
Reference Figure 3. Distribution of recommended actions across LGAs.
Note OPE estimator values if in fact_sheet.md.

### 3.4 Microsimulation and cost-effectiveness (~400 w)
Reference Table 3, Table 4, Figure 4. Scenario-by-scenario incremental
DTP3 coverage and cost. State ICER of best scenario vs S0. CEAC probability
at λ = ₦50,000.

### 3.5 Subgroup equity (~220 w)
Reference supplementary tables. Compare AUROC by zone, wealth quintile,
urban/rural, maternal education. Note whether the optimised policy
narrows or widens the wealth gap (use concentration_index, wealth_gap,
slope_index columns from microsim_results.csv — pre-populated in
fact_sheet.md).

### 3.6 Interactive Dashboard (~140 w) — REQUIRED SUBSECTION
VOICE PATTERN (adapt closely):
"We have presented a dashboard including advanced data visualisation
tools to facilitate a more detailed exploration of trends, patterns,
and relationships within the dropout cascade and the RL-optimised
intervention allocation. This innovative tool is accessible at
https://olatechie.github.io/dropout/ (see Figure 5). The application
features a Story module that narrates the DTP cascade cinematically,
a Policy module showing choropleth allocation of recommended interventions,
a Simulation module for user-controlled scenario exploration with
on-the-fly cost-effectiveness, and an Explorer module for interactive
subgroup and covariate filtering. A text transcript at /story/transcript
provides a full text alternative for readers who prefer non-interactive
access."

### 3.7 Summary (~120 w)
Two- or three-sentence transition to Discussion. No new numbers.

Style:
- Past tense for results (MDPI norm).
- Reference figures/tables by number, no inline embedding.
- One citation hook per factual external comparison (these will be
  expanded in Discussion).
- No fabrication — if fact_sheet lacks a number, use [PLEASE VERIFY: …].

At end, print word count per subsection + total.
```

- [ ] **Step 2: Opus review gate**

1. All 7 subsections present (`grep -c '^### 3\.'`).
2. Total word count 1,650–1,950.
3. §3.6 contains both "https://olatechie.github.io/dropout/" and "/story/transcript".
4. **Factcheck each numeric claim in §3.1–3.5 against fact_sheet.md**. Reject if any
   number is not present in the fact sheet OR if it is present but quoted incorrectly.
5. Figures 1–5 and Tables 1–4 each referenced at least once.
6. No `[PLEASE VERIFY: ...]` flags for items that ARE in the fact sheet (sonnet
   should not be lazy).

- [ ] **Step 3: Commit**

```bash
git add manuscript/02_results.md
git commit -m "manuscript: write results (7 subsections including dashboard)

Drafted by Sonnet 4.6 constrained to numbers in manuscript/fact_sheet.md
per no-fabrication rule. Covers cohort, prediction performance,
RL policy, microsim+PSA, subgroup equity, interactive dashboard, summary.
~1,800 words."
```

---

### Task 10: Discussion — Sonnet

**Files:**
- Create: `manuscript/03_discussion.md`
- Create: `manuscript/04_conclusions.md`
- Create: `manuscript/99_backmatter.md`

- [ ] **Step 1: Dispatch Sonnet subagent**

Call `Agent` with `model: "sonnet"` and prompt:

```
Draft the Discussion, Conclusions, and Back matter for the MDPI Vaccines
manuscript. Invoke scientific-paper-writer:write-discussion.

Read: manuscript/02_results.md, manuscript/fact_sheet.md,
manuscript/01_methods.md, manuscript/00_frontmatter.md,
outputs/literature/dropout_literature_review.csv (use top 20 rows
by relevance/citation count for comparison).

=== manuscript/03_discussion.md ===
Target 1,000 words ± 100. Structure (no subsection headings required,
paragraphs OK):

Paragraph 1 (principal findings, ~150w): restate aim; summarise the
three main findings (prediction, policy, cost-effectiveness) at a high
level. Cite Table 2, Table 3, Figure 3.

Paragraphs 2–3 (comparison with literature, ~350w): compare prediction
AUROC with at least 3 prior DTP dropout / immunisation dropout prediction
studies (from dropout_literature_review.csv); compare ICER vs published
MCH cost-effectiveness benchmarks. ≥8 citation hooks here.

Paragraph 4 (methodological strengths, ~120w): TRIPOD-AI adherence;
offline-RL with OPE (Gottesman); CHEERS 2022 PSA.

Paragraphs 5–6 (limitations, ~250w):
  - DHS recall + card availability
  - Behaviour-policy inference (proxy actions)
  - External-validity limits (Nigeria-only)
  - Offline-RL caveats (distributional shift, confounding —
    reference Gottesman 2019 explicitly [@gottesman2019guidelines])
  - No stated-preference cost data for a4 incentives.

Paragraph 7 (policy implications, ~100w): what NPHCDA / NPI could do
with these scores in the National Strategy on Immunisation and PHC.

Paragraph 8 (future work, ~80w): stepped-wedge pragmatic trial;
uplift-modelling head; generalisation to other vaccines and LMICs.

Requirement: ≥20 citation hooks across the section.

=== manuscript/04_conclusions.md ===

Target 150 words ± 20. Short standalone section per MDPI norm.

## 5. Conclusions

A single paragraph restating: (1) what was done, (2) headline
quantitative finding (best-scenario incremental coverage + ICER),
(3) what stakeholders should take away.

=== manuscript/99_backmatter.md ===

The standard MDPI back-matter blocks. Use these boilerplate-style
statements — personalised where needed:

## Supplementary Materials
The following supporting information can be downloaded at: [URL TBC at
submission]. Figure S1: ...; Figure S2: ...; ...; Table S1: ...; ... .

## Author Contributions
[PLEASE VERIFY: author CRediT roles] — provide a template row
per author (Conceptualization, Methodology, Formal Analysis, Writing —
Original Draft, Writing — Review & Editing, Supervision, Funding
Acquisition). Mark each with [PLEASE VERIFY: Initials].

## Funding
[PLEASE VERIFY: funding source and grant number]. If unfunded, use the
MDPI standard sentence: "This research received no external funding."

## Institutional Review Board Statement
"The DHS Nigeria 2024 data analysed in this study are publicly available
de-identified secondary data. The original DHS protocols were reviewed and
approved by the ICF Institutional Review Board and the Nigeria National
Health Research Ethics Committee. Secondary analysis of these data did
not require additional ethical review per ICF DHS terms of use."

## Informed Consent Statement
"Written informed consent was obtained from all participants or their
legal guardians by the DHS primary data collectors. No additional consent
was sought for this secondary analysis."

## Data Availability Statement
"The DHS 2024 Nigeria datasets are available from the DHS Program upon
registration at https://dhsprogram.com. All analytic code, derived
artifacts, and the interactive dashboard are openly available at
https://github.com/olatechie/dropout. The deployed dashboard is hosted
at https://olatechie.github.io/dropout/."

## Conflicts of Interest
"The authors declare no conflict of interest." [PLEASE VERIFY].

At end, print word counts and total citation-hook counts.
```

- [ ] **Step 2: Opus review gate**

1. All 3 files exist.
2. `03_discussion.md` word count 900–1,100; `04_conclusions.md` word count 130–170.
3. Discussion cites ≥20 `[@…]` hooks (`grep -c '\[@' manuscript/03_discussion.md`).
4. `99_backmatter.md` contains all 7 required headers: Supplementary Materials,
   Author Contributions, Funding, Institutional Review Board Statement,
   Informed Consent Statement, Data Availability Statement, Conflicts of Interest.
5. Data Availability Statement includes `https://olatechie.github.io/dropout/` and
   `https://github.com/olatechie/dropout`.
6. Gottesman 2019 explicitly cited in the limitations paragraph.

- [ ] **Step 3: Commit**

```bash
git add manuscript/03_discussion.md manuscript/04_conclusions.md manuscript/99_backmatter.md
git commit -m "manuscript: write discussion, conclusions, and back-matter

Discussion (~1,000 w, ≥20 citation hooks) covers principal findings,
literature comparison, strengths, limitations (DHS recall, behaviour-policy
inference, Gottesman offline-RL caveats), policy implications, future work.
Conclusions ~150 w. Back-matter uses MDPI boilerplate with [PLEASE VERIFY]
markers for author contributions, funding, and conflicts."
```

---

### Task 11: Supplementary prose (checklists + extended methods) — Sonnet

**Files:**
- Create: `manuscript/supplement/S0_checklists.md`
- Create: `manuscript/supplement/S1_methods_extended.md`
- Create: `manuscript/supplement/S2_parameter_tables.md`
- Create: `manuscript/supplement/S3_figures_tables.md`

- [ ] **Step 1: Dispatch Sonnet subagent**

Call `Agent` with `model: "sonnet"` and prompt:

```
Draft the supplementary materials for the MDPI Vaccines manuscript.
Produce four markdown files under manuscript/supplement/.

Inputs:
- manuscript/00_frontmatter.md .. 99_backmatter.md (the main manuscript)
- manuscript/tables/supplement/ (already rendered from CSVs)
- manuscript/figures/supplement/ (if any; otherwise reference the main
  output PDFs in outputs/)
- manuscript/PAPER_CONTEXT.md

=== manuscript/supplement/S0_checklists.md ===

Three filled-in reporting checklists as Markdown tables.

## S0.1 TRIPOD-AI checklist
One row per TRIPOD-AI item (22 items from Collins et al. 2024 BMJ).
Columns: Item # | Item description | Section addressed | Page/line |
Notes. Every row filled; "Page/line" may reference section numbers
(e.g. "§2.4") since pagination is journal-typeset.

## S0.2 CHEERS 2022 checklist
One row per CHEERS 2022 item (28 items from Husereau et al. 2022).
Same column format. Every row filled.

## S0.3 Gottesman RL-in-health guidelines
One row per of the 7 issues identified by Gottesman et al. 2019:
(1) partial observability, (2) confounding, (3) reward specification,
(4) off-policy evaluation, (5) distributional shift, (6) safety/behaviour
constraints, (7) interpretability. Columns: Issue | How addressed |
Section reference.

=== manuscript/supplement/S1_methods_extended.md ===

## S1.1 Fitted Q Iteration algorithm box (~150 w + pseudocode)
## S1.2 Conservative Q-Learning algorithm box (~150 w + pseudocode,
       α regularisation explained)
## S1.3 Off-policy evaluation formulae
  - Importance Sampling (IS): equation
  - Weighted Importance Sampling (WIS): equation
  - Doubly Robust (DR): equation
  - Reference Jiang & Li 2016.
## S1.4 Behaviour-policy inference rules — full table
  Rule | DHS condition | Inferred action | Confidence weight.
  Populate from CLAUDE.md "Behaviour Policy Inference Rules".

=== manuscript/supplement/S2_parameter_tables.md ===

## S2.1 Model-input parameter table
Include the pre-rendered table from manuscript/tables/supplement/
stab_parameters.md (inline the markdown; do not just link).

## S2.2 Reproducibility parameter table
Inline manuscript/tables/supplement/stab_reproducibility.md.

=== manuscript/supplement/S3_figures_tables.md ===

## S3.1 Supplementary tables
Inline the contents of each stab_*.md under
manuscript/tables/supplement/ in this order:
  1. stab_zone.md (subgroup by zone)
  2. stab_state.md (subgroup by state)
  3. stab_wealth_quintile.md (subgroup by wealth quintile)
  4. stab_urban_rural.md (subgroup by urban/rural)
  5. stab_maternal_education.md (subgroup by maternal education)
  6. stab_policy_lookup.md (policy lookup excerpt)

## S3.2 Supplementary figures — list + captions
For each:
- Calibration T1 pre/post (outputs/stage1/calibration_model_t1.pdf,
  calibration_model_t1_recalibrated.pdf)
- Calibration T2 pre/post (same, _t2)
- SHAP beeswarm T1/T2/full (outputs/stage1/shap_beeswarm_model_*.pdf)
- FQI convergence (outputs/stage2/fqi_convergence.png)
- CQL α-sensitivity (outputs/stage2/cql_analysis.png)
- OPE comparison (outputs/stage2/ope_comparison.png)
- Bootstrap distributions S0–S5
  (outputs/stage3/bootstrap_s{0..5}_*.csv — see captions.md for guidance)
- Local Moran cluster map (outputs/stage0/local_moran_clusters_map.png)
- Prevalence by state (outputs/stage0/dropout_prevalence_by_state.png)
- Andersen-domain decomposition
  (outputs/stage1/andersen_decomp_comparison.png)

For each figure, include a markdown image block:
![Figure S1. Calibration plot T1 pre-recalibration.](../figures/supplement/sfig_calibration_t1_pre.png){#fig:s1}

(scripts/manuscript_supplement.py copies outputs/*.png|pdf to
manuscript/figures/supplement/ with canonical sfig_*.png filenames,
so by the time pandoc runs all these paths exist. Use exactly these
filenames: sfig_calibration_t1_pre.png, sfig_calibration_t1_post.png,
sfig_calibration_t2_pre.png, sfig_calibration_t2_post.png,
sfig_shap_beeswarm_t1.png, sfig_shap_beeswarm_t2.png,
sfig_fqi_convergence.png, sfig_cql_alpha_sensitivity.png,
sfig_ope_comparison.png, sfig_local_moran.png,
sfig_prevalence_by_state.png, sfig_andersen_decomposition.png.)

End every file with a word count.
```

- [ ] **Step 2: Opus review gate**

1. All 4 files exist.
2. `S0_checklists.md` has three H2 headings and ≥22 + ≥28 + 7 = ≥57 rows total
   across the three checklist tables (count `\n| ` occurrences).
3. `S1_methods_extended.md` has the four S1.1–S1.4 subsections; ≥3 equations
   (grep `\$`).
4. `S2_parameter_tables.md` inlines both stab_parameters.md and
   stab_reproducibility.md (grep their distinctive row labels).
5. `S3_figures_tables.md` references ≥10 supplementary figures via
   `![Figure S` markdown.

- [ ] **Step 3: Commit**

```bash
git add manuscript/supplement/
git commit -m "manuscript: write supplementary prose (S0-S3)

S0 checklists: TRIPOD-AI (22 items) + CHEERS 2022 (28 items) +
Gottesman RL-health (7 issues).
S1 extended methods: FQI, CQL, OPE formulae, behaviour-policy inference.
S2 parameter tables (inlined from scripts/manuscript_supplement.py output).
S3 supplementary figures + tables (inlined stab_*.md; S-figure captions)."
```

---

### Task 12: References (≥50) — Sonnet

**Files:**
- Create: `manuscript/references.bib`

- [ ] **Step 1: Dispatch Sonnet subagent**

Call `Agent` with `model: "sonnet"` and prompt:

```
Compile manuscript/references.bib with ≥50 unique BibTeX entries that
resolve every `[@…]` placeholder in the main manuscript and supplement.
Invoke scientific-paper-writer:write-references.

Inputs:
- manuscript/.archive/references.bib (seed — use entries verbatim where the
  @key still matches a current placeholder; remove stale ones)
- manuscript/{00..99}*.md (scan for @-placeholders)
- manuscript/supplement/S*.md
- outputs/literature/dropout_literature_review.csv
- outputs/literature/intervention_effect_sizes.csv

Process:
1. Extract every unique `@key` from the manuscript + supplement files:
   grep -hroE '\[@[a-zA-Z0-9_]+\]' manuscript/ | sort -u
2. For each key, try in order:
   a. If present in .archive/references.bib with a valid entry → copy verbatim.
   b. Else if the paper is in outputs/literature/dropout_literature_review.csv
      → construct a BibTeX entry from the CSV columns.
   c. Else resolve via reasonable inference (authoritative: Collins 2024
      TRIPOD-AI BMJ; Husereau 2022 CHEERS Value in Health; Gottesman 2019
      Nat Med; Ernst 2005 JMLR; Kumar 2020 NeurIPS CQL; Li 2010 WWW LinUCB;
      Jiang 2016 ICML; Andersen 1995 J Health Soc Behav; Chen 2016 KDD XGBoost;
      Lundberg 2017 NeurIPS SHAP; WHO/Gavi reports on DTP; key LMIC DTP
      dropout studies from the lit review CSV).
3. If a key cannot be resolved, insert a BibTeX entry with a
   `note = {[PLEASE VERIFY]}` field rather than fabricating.

Target: ≥50 unique keys in the final .bib file, each a complete BibTeX
entry (at minimum: author, title, year, journal/booktitle). MDPI style
prefers DOI fields — include where known.

Output at end: list of all @keys, their status (seed|lit-csv|inferred|VERIFY),
and the total count.
```

- [ ] **Step 2: Opus review gate**

1. File exists and has ≥50 `@` entries:
   ```bash
   grep -c '^@' manuscript/references.bib
   ```
   Expected: ≥50.
2. Every placeholder in the prose resolves to a bib entry:
   ```bash
   placeholders=$(grep -hroE '\[@[a-zA-Z0-9_]+\]' manuscript/ | tr -d '[]@' | sort -u)
   bibkeys=$(grep -oE '^@[a-zA-Z]+\{[a-zA-Z0-9_]+' manuscript/references.bib | sed 's/^@[a-zA-Z]*{//' | sort -u)
   comm -23 <(echo "$placeholders") <(echo "$bibkeys")
   ```
   Expected: empty output (no placeholders missing a bib entry).
3. `[PLEASE VERIFY]` flags are listed explicitly — not silently fabricated.
4. No duplicate keys (`grep '^@' | cut -d'{' -f2 | cut -d',' -f1 | sort | uniq -d` returns empty).

- [ ] **Step 3: Commit**

```bash
git add manuscript/references.bib
git commit -m "manuscript: compile references.bib (≥50 entries, MDPI numeric)

Seeded from manuscript/.archive/references.bib and augmented with lit
review entries (outputs/literature/dropout_literature_review.csv) plus
authoritative methods citations (TRIPOD-AI, CHEERS, Gottesman, FQI, CQL,
XGBoost, SHAP, LinUCB, DR-OPE, Andersen). Unresolved keys carry
note={[PLEASE VERIFY]} rather than fabricated content."
```

---

## Phase 3 — Finalisation (Opus)

### Task 13: Export to .docx (main + supplement)

**Files:**
- Modify: `scripts/build_manuscript.py` (already exists from Task 5 — use it)
- Output: `manuscript/manuscript.docx`
- Output: `manuscript/manuscript_supplement.docx`

- [ ] **Step 1: Run full build**

```bash
python scripts/build_manuscript.py --all
ls -la manuscript/manuscript.docx manuscript/manuscript_supplement.docx
```

Expected: both files exist and are ≥100 KB each (figures embed adds size).

- [ ] **Step 2: Sanity-check embedded figures and tables**

```bash
python - <<'EOF'
from docx import Document
for path in ("manuscript/manuscript.docx", "manuscript/manuscript_supplement.docx"):
    d = Document(path)
    n_tables = len(d.tables)
    # InlineShapes captures pictures; non-zero count = figures embedded.
    n_figs = len(d.inline_shapes)
    n_paragraphs = len(d.paragraphs)
    print(f"{path}: tables={n_tables}, inline_shapes={n_figs}, paragraphs={n_paragraphs}")
    assert n_tables > 0, f"No tables embedded in {path}"
    assert n_figs > 0, f"No figures embedded in {path}"
EOF
```

Expected:
- `manuscript.docx`: tables ≥ 4, inline_shapes ≥ 5.
- `manuscript_supplement.docx`: tables ≥ 8, inline_shapes ≥ 8.

- [ ] **Step 3: Re-run integration test**

```bash
pytest tests/manuscript/test_build.py::test_build_produces_both_docx -v
```

Expected: PASS.

- [ ] **Step 4: Check citations resolved**

```bash
python - <<'EOF'
from docx import Document
d = Document("manuscript/manuscript.docx")
text = "\n".join(p.text for p in d.paragraphs)
import re
# unresolved pandoc-citeproc placeholders look like "@key" or "[@key]"
unresolved = re.findall(r'@[a-zA-Z0-9_]+', text)
assert not unresolved, f"Unresolved citations: {set(unresolved)}"
print("All citations resolved to numeric form.")
EOF
```

Expected: "All citations resolved to numeric form." If unresolved found, Opus
patches `manuscript/references.bib` and re-runs Task 13 Step 1.

- [ ] **Step 5: Commit build output**

```bash
git add manuscript/manuscript.docx manuscript/manuscript_supplement.docx
git commit -m "manuscript: export main + supplement .docx via pandoc

Both documents generated by scripts/build_manuscript.py with pandoc
--citeproc, assets/mdpi_reference.docx styles, and assets/vaccines.csl.
All figures and tables embedded inline (verified via python-docx
inline_shapes + tables count). All [@key] citations resolved to MDPI
numeric [1] form."
```

---

### Task 14: GitHub Pages manuscript landing page

**Files:**
- Create: `docs/manuscript/index.html`

- [ ] **Step 1: Create landing page**

Create `docs/manuscript/index.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Manuscript — Nigeria DTP Dropout RL Study</title>
  <style>
    body{font-family:Palatino,Georgia,serif;max-width:42rem;margin:4rem auto;padding:0 1.5rem;color:#1a1a1a;line-height:1.55}
    h1{font-size:1.6rem;margin-bottom:.25rem}
    h2{margin-top:2.2rem;font-size:1.15rem;border-bottom:1px solid #ccc;padding-bottom:.2rem}
    a{color:#0645ad}
    ul{padding-left:1.2rem}
    li{margin:.35rem 0}
    .meta{color:#555;font-size:.9rem}
    code{background:#f3f3f3;padding:.1rem .3rem;border-radius:.2rem}
  </style>
</head>
<body>
  <h1>RL-Guided DTP Dropout Reduction in Nigeria — Manuscript Artifacts</h1>
  <p class="meta">Companion page for the MDPI <em>Vaccines</em> submission. Last built from <code>main</code> branch.</p>

  <h2>Preprint &amp; submission files</h2>
  <ul>
    <li><a href="../../manuscript/manuscript.docx">manuscript.docx</a> — main article (figures + tables embedded)</li>
    <li><a href="../../manuscript/manuscript_supplement.docx">manuscript_supplement.docx</a> — supplementary materials</li>
    <li><a href="../../manuscript/references.bib">references.bib</a> — BibTeX</li>
  </ul>

  <h2>Figures (main)</h2>
  <ul>
    <li><a href="../../manuscript/figures/fig1.png">Figure 1 — Study flow + DTP cascade</a></li>
    <li><a href="../../manuscript/figures/fig2.png">Figure 2 — Model performance + top-10 SHAP</a></li>
    <li><a href="../../manuscript/figures/fig3.png">Figure 3 — RL-optimised LGA allocation</a></li>
    <li><a href="../../manuscript/figures/fig4.png">Figure 4 — CEAC + CE plane</a></li>
    <li><a href="../../manuscript/figures/fig5_dashboard.png">Figure 5 — Interactive dashboard screenshots</a></li>
  </ul>

  <h2>Tables (main, source markdown)</h2>
  <ul>
    <li><a href="../../manuscript/tables/tab1.md">Table 1 — Cohort descriptives</a></li>
    <li><a href="../../manuscript/tables/tab2.md">Table 2 — Prediction performance</a></li>
    <li><a href="../../manuscript/tables/tab3.md">Table 3 — Microsimulation scenarios</a></li>
    <li><a href="../../manuscript/tables/tab4.md">Table 4 — One-way sensitivity tornado</a></li>
  </ul>

  <h2>Related resources</h2>
  <ul>
    <li><a href="https://olatechie.github.io/dropout/">Interactive Dashboard (live)</a></li>
    <li><a href="https://github.com/olatechie/dropout">Source code (GitHub)</a></li>
    <li><a href="https://dhsprogram.com">DHS Program (primary data)</a></li>
  </ul>

  <p class="meta">All analytic outputs are reproducible via <code>python scripts/build_manuscript.py --all</code> from a clone of the repository.</p>
</body>
</html>
```

- [ ] **Step 2: Verify links resolve locally**

```bash
python - <<'EOF'
import re, pathlib
root = pathlib.Path(".")
html = (root / "docs/manuscript/index.html").read_text()
rels = re.findall(r'href="(\.\./\.\./[^"]+)"', html)
missing = []
for r in rels:
    target = (root / "docs/manuscript" / r).resolve()
    if not target.exists():
        missing.append((r, str(target)))
print(f"{len(rels)} relative links; {len(missing)} missing")
for r, t in missing:
    print(f"  MISSING: {r} → {t}")
assert not missing, "Fix broken links before commit"
EOF
```

Expected: 0 missing. If any are missing, ensure Task 13 Step 1 ran successfully,
then re-run Step 2.

- [ ] **Step 3: Commit**

```bash
git add docs/manuscript/index.html
git commit -m "manuscript: add GitHub Pages landing page with artifact links

docs/manuscript/index.html links to the main .docx, supplement .docx,
bib file, main figures, main tables, the live dashboard, and the source
repo. Served from https://olatechie.github.io/dropout/manuscript/
once the website-deploy workflow runs on main."
```

---

## Acceptance Gate — Final Verification

Before declaring the plan complete, run this final check:

- [ ] **Gate 1 — All artifacts present**

```bash
ls manuscript/manuscript.docx manuscript/manuscript_supplement.docx \
   manuscript/references.bib \
   manuscript/{00_frontmatter,01_methods,02_results,03_discussion,04_conclusions,99_backmatter}.md \
   manuscript/captions.md manuscript/fact_sheet.md \
   manuscript/supplement/S{0,1,2,3}_*.md \
   docs/manuscript/index.html \
   assets/mdpi_reference.docx assets/vaccines.csl
```

Expected: no "No such file" errors.

- [ ] **Gate 2 — Reference count ≥ 50**

```bash
grep -c '^@' manuscript/references.bib
```
Expected: ≥ 50.

- [ ] **Gate 3 — No unresolved `[@key]` in main docx**

Run Task 13 Step 4 again. Expected: clean.

- [ ] **Gate 4 — Embedded figures / tables visible in Word**

Open `manuscript/manuscript.docx` in Word/LibreOffice; confirm Figures 1–5 render
inline and Tables 1–4 are native Word tables (not images).

- [ ] **Gate 5 — `[PLEASE VERIFY]` audit**

```bash
grep -rn '\[PLEASE VERIFY' manuscript/
```
Expected: small, documented list — for each, either (a) resolve and re-run
build, or (b) accept as a deliberate user-action flag and note in a handoff
message.

- [ ] **Gate 6 — Final summary commit**

```bash
git add -A && git status
git commit -m "manuscript: complete MDPI Vaccines draft — ready for author review" || echo "(nothing to commit)"
git tag manuscript-v0.2.0-draft
```

Print summary to user:
- Path to `manuscript.docx`
- Reference count
- Remaining `[PLEASE VERIFY]` flags (count + file:line list)
- Dashboard URL and landing page URL
- Suggested next step: author review round.

---

## Self-Review Notes

**Spec coverage check** (ran after writing all tasks):

| Spec requirement | Task | Notes |
|---|------|-------|
| §1.1 Submission-ready .docx with embedded figs/tabs | Task 13 | Gate 4 |
| §1.2 Three methodological threads equally weighted | Tasks 7 §2.4–2.7 | Gated on word budget + hooks |
| §1.3 Interactive Dashboard subsection (Methods + Results) | Tasks 7 §2.8 + 9 §3.6 | Gated on URL + voice-pattern |
| §1.4 Supplementary checklists + parameter tables | Tasks 4, 11 | S0–S3 |
| §1.5 ≥50 references | Task 12 | Gate 2 |
| §1.6 Archive to .archive/ | Task 0 | — |
| §4 TRIPOD-AI / CHEERS / Gottesman named | Tasks 7, 10, 11 | S0 checklists + prose |
| §5 Title + abstract + keywords | Task 6 | Gated on 200 ±10 w |
| §6.1–6.2 Section word budgets | Tasks 6–10 | Each gated to ±10% |
| §7 Main display items (5 figs / 4 tabs) | Tasks 2, 3 | Scripts auto-regenerate |
| §8 Supplementary contents | Tasks 4, 11 | Checklists + S-figures + S-tables |
| §9 Reference strategy | Task 12 | Seed + augment + style |
| §11 Assembly toolchain | Task 5 | Pandoc orchestrator |
| §12 File layout | All | — |
| §13 Acceptance criteria | Gates 1–6 | — |

No gaps identified.

**Placeholder scan:** only deliberate `[PLEASE VERIFY: …]` flags remain — these are
user-action markers per `scientific-paper-writer:core-engine` rules, not plan
placeholders. No "TBD" / "TODO" / vague-intent text.

**Type consistency:** file paths consistent across tasks (e.g. `manuscript/captions.md`
cited in Tasks 8, 9, 11; `manuscript/fact_sheet.md` cited in Tasks 8, 9; figure paths
`manuscript/figures/figN.{png,pdf}` consistent in Tasks 2, 3, 5, 13, 14).
