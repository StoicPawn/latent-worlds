from latent_worlds.replication import fitness_content_controls, standard_turnover_overrides


def test_fitness_controls_have_three_modes():
    r=fitness_content_controls(0,0,steps=10,overrides=standard_turnover_overrides())
    assert set(r['conditions']) == {'readable','censored','scrambled'}
    assert isinstance(r['adaptive_supported'], bool)


def test_standard_turnover_is_world_side_only():
    r=standard_turnover_overrides()
    assert set(r) == {'reproduction_threshold','reproduction_cost','resource_regrowth'}
