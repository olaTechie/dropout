#!/usr/bin/env python3
"""Render main manuscript tables 1-4 from outputs/ CSVs to Markdown pipe-tables.

Tab 1: Cohort descriptives by T1/T2 dropout status
Tab 2: Prediction-model performance (AUROC/AUPRC/Brier/ECE, 95% CI)
Tab 3: Microsimulation scenarios S0-S5 with PSA CIs and ICER
Tab 4: Tornado (one-way sensitivity top parameters)
"""
from __future__ import annotations

import json
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
    """Prediction performance from xgb_results_summary.json."""
    summary_path = STAGE1 / "xgb_results_summary.json"
    d = json.loads(summary_path.read_text())

    rows = []
    for tkey, tlabel in [("t1", "T1 (DTP1→DTP2)"), ("t2", "T2 (DTP2→DTP3)")]:
        m = d[tkey]["metrics"]
        auc_roc = m["auc_roc"]
        auc_roc_ci = m["auc_roc_ci"]
        auc_pr = m["auc_pr"]
        auc_pr_ci = m["auc_pr_ci"]
        brier_recal = m["brier"]["brier"]
        brier_orig = m["brier_original"]["brier"]
        cal_orig_slope = m.get("calibration_original", {}).get("slope")
        cal_recal_slope = m.get("calibration", {}).get("slope")
        rows.append({
            "Transition": tlabel,
            "N": d[tkey]["n"],
            "Prevalence": f"{d[tkey]['prevalence']:.4f}",
            "AUROC (95% CI)": f"{auc_roc:.3f} ({auc_roc_ci[0]:.3f}–{auc_roc_ci[1]:.3f})",
            "AUPRC (95% CI)": f"{auc_pr:.3f} ({auc_pr_ci[0]:.3f}–{auc_pr_ci[1]:.3f})",
            "Brier (orig. → recal.)": f"{brier_orig:.4f} → {brier_recal:.4f}",
            "Cal. slope (orig. → recal.)":
                f"{cal_orig_slope:.3f} → {cal_recal_slope:.3f}"
                if cal_orig_slope is not None and cal_recal_slope is not None
                else "—",
        })
    df = pd.DataFrame(rows)
    body = df.to_markdown(index=False)
    _write(
        "tab2",
        "Prediction-model discrimination and calibration for DTP1→DTP2 (T1) "
        "and DTP2→DTP3 (T2) transitions, with 95 % confidence intervals from "
        "1,000-sample bootstrap. Brier score and calibration slope reported "
        "pre- and post-isotonic recalibration.",
        body,
        "AUROC = area under receiver-operating-characteristic curve; "
        "AUPRC = area under precision-recall curve.",
    )


def render_tab3() -> None:
    """Microsim scenarios: coverage, cost, ICER vs S0."""
    df = pd.read_csv(STAGE3V2 / "microsim_results.csv")
    s0 = df[df["scenario"].str.startswith("S0")].iloc[0]

    def _icer(r):
        if r.scenario == s0.scenario:
            return "—"
        dcov = (r.dtp3_mean - s0.dtp3_mean) * 100
        if abs(dcov) < 1e-6:
            return "dominated / equivalent"
        return f"{(r.cost_per_child_mean - s0.cost_per_child_mean) / dcov:,.0f}"

    out = pd.DataFrame({
        "Scenario": df["scenario"],
        "DTP3 coverage mean (95% CI)": df.apply(
            lambda r: f"{r.dtp3_mean:.3f} ({r.dtp3_ci_low:.3f}–{r.dtp3_ci_high:.3f})",
            axis=1
        ),
        "Cost per child (₦) mean (95% CI)": df.apply(
            lambda r: f"{r.cost_per_child_mean:.0f} ({r.cost_per_child_ci_low:.0f}–{r.cost_per_child_ci_high:.0f})",
            axis=1,
        ),
        "ICER vs S0 (₦ per % coverage)": df.apply(_icer, axis=1),
    })
    body = out.to_markdown(index=False)
    _write(
        "tab3",
        "Microsimulation results for scenarios S0–S5 with 1,000-iteration "
        "probabilistic sensitivity analysis. DTP3 coverage and cost per child "
        "reported as mean with 95 % bootstrap CI.",
        body,
        "ICER = incremental cost-effectiveness ratio. Cost-effectiveness "
        "probability at willingness-to-pay λ = ₦50,000 per additional child "
        "fully vaccinated shown in Figure 4 (CEAC).",
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
