from latent_worlds.phase_map import long_horizon_config, screen_cell

def test_phase_world_only_changes():
    low=long_horizon_config(information_level=0.0, signal_cost=0.03)
    high=long_horizon_config(information_level=1.5, signal_cost=0.09)
    assert low.generic_population_only and high.generic_population_only
    assert low.obstacle_count == 0 and high.obstacle_count > 0
    assert low.signal_cost < high.signal_cost
    assert low.initial_agents == high.initial_agents
    assert low.resource_patches == high.resource_patches

def test_tiny_phase_cell_runs():
    out=screen_cell(0.5,0.055,[0],steps=20,epoch=10)
    assert out['worlds']==1
    assert 'candidate_worlds' in out
