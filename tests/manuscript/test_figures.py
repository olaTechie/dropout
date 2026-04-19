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
