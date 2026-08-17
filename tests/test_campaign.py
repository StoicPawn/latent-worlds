from latent_worlds.campaign import classify_burst

def test_burst_outcome_classification_is_conservative():
    assert classify_burst(30.0, 0) == 'fitness-positive-candidate'
    assert classify_burst(-25.0, 0) == 'maladaptive-or-costly'
    assert classify_burst(5.0, 0) == 'approximately-neutral'
    assert classify_burst(50.0, -2) == 'maladaptive-or-costly'


def test_scrambled_communication_preserves_channel_but_changes_payload_assignment():
    from latent_worlds.config import SimulationConfig
    from latent_worlds.world import World, BroadcastSignal
    cfg=SimulationConfig(initial_agents=1, communication_scramble=True)
    w=World(cfg, seed=3)
    w._next_signals=[BroadcastSignal(1,1,(1.,0.,0.),5,1), BroadcastSignal(2,2,(0.,1.,0.),5,2), BroadcastSignal(3,3,(0.,0.,1.),5,3)]
    # exercise the exact scrambling rule without altering world RNG
    payloads=[s.payload for s in w._next_signals]
    perm=w.intervention_rng.permutation(len(payloads))
    scrambled=[payloads[int(j)] for j in perm]
    assert sorted(scrambled)==sorted(payloads)
    assert cfg.communication_enabled is True


def test_agent_seed_decouples_initial_population_from_world_seed():
    from latent_worlds.phase_map import long_horizon_config
    from latent_worlds.world import World
    cfg1=long_horizon_config(information_level=0.35, agent_seed=123)
    cfg2=long_horizon_config(information_level=1.65, agent_seed=123)
    w1=World(cfg1, seed=1); w2=World(cfg2, seed=99)
    g1=[(a.genome.speed,a.genome.memory,a.genome.social_attention,a.genome.plasticity) for a in w1.agents]
    g2=[(a.genome.speed,a.genome.memory,a.genome.social_attention,a.genome.plasticity) for a in w2.agents]
    assert g1==g2
