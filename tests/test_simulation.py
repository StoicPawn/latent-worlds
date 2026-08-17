

def test_specialization_ignores_dead_and_tiny_descendant_samples():
    from latent_worlds.longitudinal import _generation_specialization
    from latent_worlds.config import SimulationConfig
    from latent_worlds.world import World
    w = World(SimulationConfig(generic_population_only=True, initial_agents=8), seed=777)
    # Give founders enough activity, but leave at most two fabricated descendants.
    for a in w.agents:
        a.action_counts['move'] = 30
    # Dead agents must not create current niches.
    for a in w.agents[:4]:
        a.alive = False
    out = _generation_specialization(w)
    assert out['persistent_specialization_transitions'] == 0


def test_permutation_excess_detects_real_payload_structure():
    import numpy as np
    from latent_worlds.longitudinal import _permutation_excess
    x=np.linspace(-1,1,80)[:,None]
    P=np.column_stack([x[:,0],x[:,0]**2, np.sin(3*x[:,0])])
    Y=np.column_stack([2*P[:,0]-P[:,1], P[:,2]])
    r=_permutation_excess(P,Y,permutations=24)
    assert r["excess"] is not None and r["excess"] > 0.5
    assert r["p_upper"] <= 0.08


def test_permutation_excess_does_not_reward_constant_payload():
    import numpy as np
    from latent_worlds.longitudinal import _permutation_excess
    P=np.ones((40,3)); Y=np.arange(80,dtype=float).reshape(40,2)
    r=_permutation_excess(P,Y,permutations=8)
    assert r["observed"] is None


def test_role_interdependence_is_observer_side_and_returns_structured_result():
    from latent_worlds.config import SimulationConfig
    from latent_worlds.world import World
    from latent_worlds.role_ablation import role_interdependence
    cfg=SimulationConfig(generic_population_only=True, initial_agents=16, resource_patches=36,
                         resource_regrowth=0.07, basal_metabolism=0.03, initial_energy=20.0,
                         reproduction_threshold=20.0, reproduction_cost=8.5)
    w=World(cfg,seed=31); w.run(120)
    before=(w.time, [(a.id,a.alive,a.energy) for a in w.agents])
    r=role_interdependence(w,horizon=10,min_role_size=2,min_actions=10,random_controls=2)
    after=(w.time, [(a.id,a.alive,a.energy) for a in w.agents])
    assert before == after
    assert r['time']==120 and 'roles' in r and 'candidate_roles' in r
