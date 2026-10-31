"""Unit guards for action-set-matched observer foresight."""
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np

MODULE_DIR = Path(__file__).resolve().parents[1] / "experiments/civitas_zero/synchrony"
sys.path.insert(0, str(MODULE_DIR))
from local_foresight_pilot import world_for, visible_indices, score_action_set


def test_visible_indices_are_exactly_agent_nearby_resource_candidates():
    w = world_for(11, 1.5)
    for position in ((1.0, 1.0), (10.0, 10.0), (25.0, 18.0)):
        indices = visible_indices(w, position)
        agent = SimpleNamespace(x=position[0], y=position[1])
        observed = w.nearby(agent)
        from_patches = [
            (w.resources[i].x - agent.x,
             w.resources[i].y - agent.y,
             w.resources[i].richness)
            for i in indices
        ]
        assert sorted(from_patches) == sorted(observed)


def test_one_visible_option_has_no_forecast_routing_advantage():
    w = world_for(11, 1.5)
    origin = (w.resources[0].x, w.resources[0].y)
    for t in (0, 120, 500, 800):
        r = score_action_set(w, origin, t, [0])
        assert r["advantage"] == 0.0
        assert not r["changed"]


def test_no_visible_options_is_reported_as_unavailable():
    w = world_for(11, 1.5)
    r = score_action_set(w, (2.0, 2.0), 25, [])
    assert r["advantage"] == 0.0
    assert r["n_options"] == 0
    assert r["myopic_realized"] is None


def test_foresight_does_not_lose_with_identical_choice_set():
    w = world_for(21, 1.5)
    for xy in ((5.0, 8.0), (15.0, 15.0), (27.0, 24.0)):
        ids = visible_indices(w, xy)
        for t in (0, 100, 500):
            r = score_action_set(w, xy, t, ids)
            assert r["advantage"] >= -1e-12
            if r["n_options"] > 0:
                assert np.isclose(
                    r["oracle_realized"] - r["myopic_realized"],
                    r["advantage"], atol=1e-10
                )


def test_accessibility_manifest_is_portable_across_machines():
    import json
    from local_foresight_pilot import DATA
    obj = json.loads(DATA.read_text())
    assert obj["source_global"] == "experiments/civitas_zero/data/foresight_pilot/results.json"
    assert len(obj["rows"]) == 6
