from latent_worlds.phase_map import long_horizon_config
from latent_worlds.generational_search import turnover_profile
from latent_worlds.world import World
from latent_worlds.persistent_inheritance import conditional_mark_inheritance_assay, persistent_secondary_evolution_assay

def test_mark_reads_are_observer_logged_without_new_agent_input():
    cfg=long_horizon_config(information_level=.35,signal_cost=.03,communication_enabled=True,agent_seed=0)
    for k,v in turnover_profile().items(): setattr(cfg,k,v)
    w=World(cfg,seed=0).run(80)
    assert all('received_mark_count' in r and 'mean_mark_payload' in r for r in w.social_log)

def test_persistent_inheritance_assay_runs():
    cfg=long_horizon_config(information_level=.35,signal_cost=.03,communication_enabled=True,agent_seed=0)
    for k,v in turnover_profile().items(): setattr(cfg,k,v)
    w=World(cfg,seed=0).run(100)
    r=conditional_mark_inheritance_assay(w,permutations=9,min_pairs=5,min_generation=0,min_rows=10)
    assert 'by_generation' in r
    z=persistent_secondary_evolution_assay(w,permutations=9,min_generation=0)
    assert 'criteria' in z
