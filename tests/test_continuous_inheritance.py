from latent_worlds.phase_map import long_horizon_config
from latent_worlds.generational_search import turnover_profile
from latent_worlds.world import World
from latent_worlds.secondary_evolution import continuous_conditional_inheritance_assay

def test_continuous_conditional_inheritance_runs_for_both_existing_carriers():
    cfg=long_horizon_config(information_level=.35,signal_cost=.03,communication_enabled=True,agent_seed=0)
    for k,v in turnover_profile().items(): setattr(cfg,k,v)
    w=World(cfg,seed=0).run(80)
    for carrier in ('broadcast','mark'):
        r=continuous_conditional_inheritance_assay(w,carrier=carrier,permutations=9,min_pairs=5,min_generation=0)
        assert r['carrier']==carrier
        assert 'by_generation' in r

def test_directional_continuous_assay_runs():
    from latent_worlds.secondary_evolution import directional_continuous_transmission_assay
    cfg=long_horizon_config(information_level=.35,signal_cost=.03,communication_enabled=True,agent_seed=0)
    for k,v in turnover_profile().items(): setattr(cfg,k,v)
    w=World(cfg,seed=0).run(80)
    r=directional_continuous_transmission_assay(w,carrier='broadcast',permutations=9,min_pairs=5,min_generation=0)
    assert 'by_generation' in r
