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
