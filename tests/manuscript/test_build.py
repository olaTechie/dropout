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
    if not (ROOT / "manuscript" / "00_frontmatter.md").exists():
        pytest.skip("prose markdown not yet written (Sonnet tasks not complete)")
    result = subprocess.run(
        ["python", "scripts/build_manuscript.py", "--all"],
        cwd=ROOT, capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    assert MAIN.exists() and MAIN.stat().st_size > 10_000
    assert SUPP.exists() and SUPP.stat().st_size > 10_000
