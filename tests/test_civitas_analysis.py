"""Fast scientific-regression tests; no expensive world rollout."""
import importlib.util
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "experiments/civitas_zero/analysis/analyze_v54.py"
DATA = ROOT / "experiments/civitas_zero/data/v54"
spec = importlib.util.spec_from_file_location("civitas_analysis", SCRIPT)
analysis = importlib.util.module_from_spec(spec)
spec.loader.exec_module(analysis)


def test_sign_test_is_exact_and_ties_are_reported():
    test = analysis.sign_test([1.0] * 10 + [-1.0] * 6)
    assert math.isclose(test["p"], 14893 / 65536)
    assert test["positive"] == 10 and test["negative"] == 6
    assert analysis.sign_test([0.0, 0.0])["p"] == 1.0
    assert analysis.sign_test([0.0, 0.0])["ties"] == 2


def test_bootstrap_is_reproducible_and_resamples_seed_level():
    xs = [-1.0, 0.2, 0.8, 1.0]
    assert analysis.paired_interval(xs, n_draws=1000) == analysis.paired_interval(xs, n_draws=1000)
    assert analysis.paired_interval([3.0] * 16, n_draws=100) == (3.0, 3.0)


def test_prospective_frozen_gate_reconstructed_independently():
    manifest, rows = analysis.load_rows(DATA)
    report = analysis.audit(rows)
    original = json.loads((DATA / "summary.json").read_text())
    assert manifest["source_code_base_sha"] == "2cca2dc019541f296285b75daa8e416c7818b15e"
    assert report["n_population_seeds"] == 16
    assert not report["preregistered_gate_passed"]
    assert report["preregistered_gate_passed"] == original["evaluation"]["gate_passed"]
    for baseline in ("frozen", "output_only"):
        got = report["paired_fraction_effects"][baseline]
        old = original["evaluation"]["carrier_fraction_tests"][baseline]
        assert math.isclose(got["difference"], old["mean_difference"], abs_tol=1e-12)
        assert math.isclose(got["p"], old["p_one_sided"], abs_tol=1e-12)


def test_corrupted_fraction_is_rejected(tmp_path):
    manifest, rows = analysis.load_rows(DATA)
    src = DATA / "seed_93.json"
    dst = tmp_path / "manifest.json"
    dst.write_text(json.dumps(manifest))
    for seed in analysis.SEEDS:
        row = json.loads((DATA / f"seed_{seed}.json").read_text())
        if seed == 93:
            row["conditions"]["frozen"]["candidate_fraction"] = 0.999
        (tmp_path / f"seed_{seed}.json").write_text(json.dumps(row))
    try:
        analysis.load_rows(tmp_path)
    except ValueError as exc:
        assert "Fraction inconsistent" in str(exc)
    else:
        raise AssertionError("Audit accepted a deliberately corrupt carrier fraction")


def test_svg_is_static_and_carries_frozen_result():
    _, rows = analysis.load_rows(DATA)
    svg = analysis._svg(analysis.audit(rows))
    assert svg.startswith("<svg ")
    assert "p=0.402" in svg
    assert "p=0.227" in svg
    assert "no confirmation of E1" in svg
