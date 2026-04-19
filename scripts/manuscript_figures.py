#!/usr/bin/env python3
"""Regenerate main manuscript figures 1-4 from outputs/ CSVs and stage PDFs.

Fig 1: Study flow + cascade (2 panels)
Fig 2: Model performance + top-10 SHAP (2x2 panels, T1 and T2)
Fig 3: RL-optimised LGA allocation choropleth
Fig 4: CEAC + CE plane (2 panels)
"""
from __future__ import annotations

import argparse
import re
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
# Use NGA_1 (state-level) for the choropleth — it has exactly 37 rows matching
# DHS sstate codes 1-37.  The LGA-level file (NGA_2) is kept for reference.
SHAPEFILE_STATE = ROOT / "data" / "shapefiles" / "gadm" / "gadm41_NGA_1.shp"


def _save(fig, name: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    # Use 301 dpi to guarantee PIL reads back ≥300 after floating-point rounding
    fig.savefig(OUT / f"{name}.png", dpi=301, bbox_inches="tight")
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
        (axes[0, 0], STAGE1 / "roc_pr_model_t1.png", "A. T1 ROC/PR (DTP1\u2192DTP2)"),
        (axes[0, 1], STAGE1 / "roc_pr_model_t2.png", "B. T2 ROC/PR (DTP2\u2192DTP3)"),
        (axes[1, 0], STAGE1 / "shap_bar_model_t1.pdf", "C. T1 top-10 SHAP"),
        (axes[1, 1], STAGE1 / "shap_bar_model_t2.pdf", "D. T2 top-10 SHAP"),
    ]
    for ax, p, title in pairs:
        if p.suffix == ".pdf":
            import fitz  # PyMuPDF
            doc = fitz.open(str(p))
            page = doc.load_page(0)
            pix = page.get_pixmap(dpi=300)
            import numpy as np
            img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
            doc.close()
            ax.imshow(img)
        else:
            ax.imshow(mpimg.imread(p))
        ax.set_title(title, loc="left", fontsize=12, fontweight="bold")
        ax.axis("off")
    fig.tight_layout()
    _save(fig, "fig2")


def build_fig3() -> None:
    """Fig 3: RL-optimised recommended intervention choropleth (state-level).

    Join strategy:
      - GADM NGA_1 shapefile has exactly 37 rows with GID_1 = 'NGA.N_1'.
      - DHS sstate is an integer 1-37 matching the alphabetical state ordering.
      - Extract the integer N from GID_1 to create sstate_code, then merge.
    """
    try:
        import geopandas as gpd
    except ImportError:
        raise RuntimeError("geopandas required for fig3 — run: pip install geopandas")

    alloc = pd.read_csv(STAGE3 / "lga_allocation.csv")

    # Modal action per state
    state_action = (
        alloc.groupby("sstate")["assigned_action"]
        .agg(lambda s: s.mode().iloc[0])
        .reset_index()
        .rename(columns={"sstate": "sstate_code", "assigned_action": "action"})
    )

    gdf = gpd.read_file(SHAPEFILE_STATE)
    # Extract numeric state index from GID_1 (e.g. 'NGA.1_1' → 1)
    gdf["sstate_code"] = gdf["GID_1"].apply(
        lambda x: int(re.search(r"NGA\.(\d+)_", x).group(1))
    )
    gdf = gdf.merge(state_action, on="sstate_code", how="left")

    action_labels = {
        0: "a0: None",
        1: "a1: SMS",
        2: "a2: CHW",
        3: "a3: Facility recall",
        4: "a4: Incentive",
    }

    # Map integer action codes to readable labels for plotting
    gdf["action_label"] = gdf["action"].map(action_labels).fillna("Unknown")

    fig, ax = plt.subplots(figsize=(10, 10))
    gdf.plot(
        column="action_label",
        ax=ax,
        cmap="tab10",
        legend=True,
        edgecolor="white",
        legend_kwds={"loc": "lower left", "title": "Recommended intervention"},
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
    p.add_argument(
        "--figs",
        default="1,2,3,4",
        help="Comma-sep figure numbers to build (default: 1,2,3,4)",
    )
    args = p.parse_args()
    for n in [int(x) for x in args.figs.split(",") if x.strip()]:
        print(f"Building fig{n}...")
        FIG_BUILDERS[n]()
        print(f"  \u2192 manuscript/figures/fig{n}.png + fig{n}.pdf")


if __name__ == "__main__":
    main()
