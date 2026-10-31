"""Regression guard for the observer-only ecological opportunity pilot."""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "experiments/civitas_zero/analysis/plot_foresight_pilot.py"
spec = importlib.util.spec_from_file_location("foresight_pilot_plot", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_opportunity_pilot_is_audited_and_reproducible():
    data = json.loads(mod.DATA.read_text())
    rows = mod.audit(data)
    assert len(rows) == 6
    assert all(x["samples"] == 176 for x in rows)
    fig = mod.render(rows)
    assert fig.startswith("<svg ")
    for world in (11, 21, 31):
        assert f"W{world}" in fig
        wave = next(x for x in rows if x["world_seed"] == world and x["wave_strength"] == 1.5)
        off = next(x for x in rows if x["world_seed"] == world and x["wave_strength"] == 0.0)
        assert wave["mean_foresight_advantage"] > off["mean_foresight_advantage"]
    assert "EXPLORATORY_ONLY" in data["status"]


def test_opportunity_missing_cell_fails():
    data = json.loads(mod.DATA.read_text())
    data["rows"] = data["rows"][:-1]
    try:
        mod.audit(data)
    except ValueError as exc:
        assert "Missing world" in str(exc)
    else:
        raise AssertionError("Incomplete pilot data accepted")
