#!/usr/bin/env python3
"""Render supplementary tables for the MDPI Vaccines manuscript.

Produces (in manuscript/tables/supplement/):
- stab_{zone,state,wealth_quintile,urban_rural,maternal_education}.md : subgroup perf
- stab_policy_lookup.md : state→action Q-value lookup
- stab_parameters.md : model-input parameters (effect sizes, costs, PSA priors)
- stab_reproducibility.md : seeds, hyperparams, software versions

And copies supplementary figures to manuscript/figures/supplement/ with
canonical sfig_*.png filenames for pandoc embedding.
"""
from __future__ import annotations

import platform
import shutil
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "manuscript" / "tables" / "supplement"
VAL = ROOT / "outputs" / "validation"
STAGE0 = ROOT / "outputs" / "stage0"
STAGE1 = ROOT / "outputs" / "stage1"
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
    df = pd.read_csv(csv).head(50)
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
    versions = {"Python": platform.python_version()}
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
            {"Component": "bootstrap iterations", "Value": "1,000"},
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

    PyMuPDF (fitz) rasterises PDFs to 300 DPI PNG when a PNG doesn't exist.
    """
    dest = ROOT / "manuscript" / "figures" / "supplement"
    dest.mkdir(parents=True, exist_ok=True)

    def _png_for(stem: Path) -> Path | None:
        """Return a PNG path for `stem` (no extension).

        Prefer existing PNG. If only PDF exists, rasterise with fitz
        to a temporary PNG next to the PDF and return that.
        """
        png = stem.with_suffix(".png")
        pdf = stem.with_suffix(".pdf")
        if png.exists():
            return png
        if pdf.exists():
            try:
                import fitz
                doc = fitz.open(str(pdf))
                page = doc.load_page(0)
                pix = page.get_pixmap(dpi=300)
                tmp = stem.with_suffix(".rendered.png")
                pix.save(str(tmp))
                doc.close()
                return tmp
            except Exception as exc:
                print(f"  (fitz failed on {pdf}: {exc})")
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
        src = _png_for(src_stem)
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
