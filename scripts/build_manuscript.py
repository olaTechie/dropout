#!/usr/bin/env python3
"""Build MDPI Vaccines manuscript: main + supplement .docx via pandoc.

Pipeline:
  1. Regenerate main figures  (scripts/manuscript_figures.py)
  2. Capture dashboard shot   (scripts/capture_dashboard.py) — optional
  3. Render main tables       (scripts/manuscript_tables.py)
  4. Render supp tables       (scripts/manuscript_supplement.py)
  5. Concat section markdown  (manuscript/{00..99}_*.md)
  6. Pandoc → manuscript.docx (embedded figs/tabs via reference.docx)
  7. Concat supplement md     (manuscript/supplement/S*.md)
  8. Pandoc → manuscript_supplement.docx

Usage:
  python scripts/build_manuscript.py --dry-run       # show plan, no execution
  python scripts/build_manuscript.py --all           # run steps 1-8
  python scripts/build_manuscript.py --stage docx    # only steps 6+8
"""
from __future__ import annotations

import argparse
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
    "98_figures_tables.md",
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

    if not args.all:
        print("nothing to do; pass --all or --stage or --dry-run")
        return
    for name in ("figures", "tables", "supplement"):
        _run(STEP_SCRIPTS[name])
    _run(STEP_SCRIPTS["dashboard"], allow_fail=True)
    build_main(dry=False)
    build_supplement(dry=False)
    print("✅ Build complete:")
    print(f"   {MAIN_DOCX}")
    print(f"   {SUPP_DOCX}")


if __name__ == "__main__":
    main()
