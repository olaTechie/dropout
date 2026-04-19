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
    assert md.count("\n|") >= 10


def test_reproducibility_parameter_table():
    p = SUPP_TAB / "stab_reproducibility.md"
    assert p.exists()
    md = p.read_text()
    for key in ("seed", "Python", "xgboost", "bootstrap"):
        assert key in md, f"missing {key}"


def test_supplementary_figures_copied():
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
