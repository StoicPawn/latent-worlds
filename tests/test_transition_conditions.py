from latent_worlds.transition_conditions import (
    matched_initialization_signature, matched_world_config, pretransition_profile
)

def test_matched_obstacle_intervention_preserves_initialized_world():
    rows = matched_initialization_signature(11, fractions=(0.0, 0.5, 1.0))
    assert len(rows) == 3
    assert len({r["resource_signature"] for r in rows}) == 1
    assert len({r["object_signature"] for r in rows}) == 1
    assert len({r["forcing_periods"] for r in rows}) == 1
    assert len({r["obstacle_signature"] for r in rows}) == 1

def test_active_obstacle_fraction_is_world_side_only():
    c0 = matched_world_config(active_obstacle_fraction=0.0)
    c1 = matched_world_config(active_obstacle_fraction=1.0)
    assert c0.agent_seed == c1.agent_seed
    assert c0.obstacle_count == c1.obstacle_count
    assert c0.active_obstacle_fraction == 0.0
    assert c1.active_obstacle_fraction == 1.0

def test_pretransition_profile_is_observer_summary():
    row = pretransition_profile(0, steps=5)
    assert row["steps"] == 5
    assert row["population"] > 0
    assert "private_information_index" in row
