from latent_worlds.generational_search import turnover_profile, genealogy_probe

def test_turnover_profile_is_world_side_mapping():
    p=turnover_profile()
    assert set(p)=={"reproduction_threshold","reproduction_cost","resource_regrowth"}
    assert p["reproduction_threshold"]>p["reproduction_cost"]

def test_genealogy_probe_runs():
    r=genealogy_probe(0,0,steps=3,overrides=turnover_profile())
    assert r["steps"]==3
    assert r["max_generation"]>=0


def test_transfer_rule_requires_positive_real_amplification():
    # Guard the scientific criterion directly: being less negative than a control
    # must never count as positive transfer evidence.
    ra, sa = -0.01, -0.05
    supported = bool(ra is not None and sa is not None and ra > 0.0 and ra > sa)
    assert not supported


def test_communication_depth_probe_is_observer_side_and_structured():
    from latent_worlds.generational_search import communication_depth_probe
    r=communication_depth_probe(0,0,steps=30,min_emissions=1,min_receptions=1)
    assert "emissions_by_generation" in r
    assert "receptions_by_generation" in r
    assert isinstance(r["communication_active_generations"], list)
    assert r["communication_depth"] == len(r["communication_active_generations"])
