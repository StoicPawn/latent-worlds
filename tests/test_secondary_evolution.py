from latent_worlds.secondary_evolution import analyze_secondary_evolution, run_secondary_evolution_probe
from latent_worlds.phase_map import long_horizon_config
from latent_worlds.world import World


def test_secondary_evolution_probe_is_observer_side_and_structured():
    cfg=long_horizon_config(information_level=.35,signal_cost=.03,communication_enabled=True,agent_seed=1)
    w=World(cfg,seed=1).run(80)
    before=[(a.id,a.energy,a.generation,a.total_harvest) for a in w.agents]
    out=analyze_secondary_evolution(w,min_cluster_rows=10,min_emissions_per_variant=2)
    after=[(a.id,a.energy,a.generation,a.total_harvest) for a in w.agents]
    assert before==after
    assert "supported" in out
    assert "clusters" in out


def test_secondary_evolution_runner_returns_identity():
    out=run_secondary_evolution_probe(0,0,steps=30)
    assert out["world_seed"]==0 and out["agent_seed"]==0
    assert out["steps"]<=30


def test_transmission_null_is_reported_when_clusters_exist():
    cfg=long_horizon_config(information_level=.35,signal_cost=.03,communication_enabled=True,agent_seed=0)
    w=World(cfg,seed=0).run(250)
    out=analyze_secondary_evolution(w,min_cluster_rows=10,min_emissions_per_variant=2,permutations=9)
    if out.get('variant_stats'):
        assert 'transmission_null' in out
        assert 0.0 <= out['transmission_null']['p_value'] <= 1.0


def test_inheritance_assay_is_part_of_candidate_when_available():
    cfg=long_horizon_config(information_level=.35,signal_cost=.03,communication_enabled=True,agent_seed=0)
    w=World(cfg,seed=0).run(260)
    out=analyze_secondary_evolution(w,min_cluster_rows=10,min_emissions_per_variant=2,permutations=9)
    if out.get('variant_stats'):
        assert 'inheritance_assay' in out
        ia=out['inheritance_assay']
        assert 'pairs' in ia and 'p_value' in ia


def test_variant_stats_include_propagation_number():
    cfg=long_horizon_config(information_level=.35,signal_cost=.03,communication_enabled=True,agent_seed=0)
    w=World(cfg,seed=0).run(260)
    out=analyze_secondary_evolution(w,min_cluster_rows=10,min_emissions_per_variant=2,permutations=9)
    for v in out.get('variant_stats',[]):
        assert v['propagation_number'] >= 0.0


def test_generational_assays_return_depth_fields():
    from latent_worlds.secondary_evolution import generational_inheritance_assay, generational_propagation_assay
    from latent_worlds.phase_map import long_horizon_config
    from latent_worlds.generational_search import turnover_profile
    from latent_worlds.world import World
    cfg=long_horizon_config(information_level=.35,signal_cost=.03,communication_enabled=True,agent_seed=0)
    for k,v in turnover_profile().items(): setattr(cfg,k,v)
    w=World(cfg,seed=0).run(120)
    a=generational_inheritance_assay(w,permutations=9,min_pairs=5)
    b=generational_propagation_assay(w,min_emissions=1)
    assert "by_generation" in a and "deep_replication" in a
    assert "by_generation" in b and "deep_differential_propagation" in b


def test_transmission_timescale_assay_shape():
    from latent_worlds.secondary_evolution import transmission_timescale_assay
    from latent_worlds.phase_map import long_horizon_config
    from latent_worlds.world import World
    w=World(long_horizon_config(agent_seed=0),seed=0).run(100)
    r=transmission_timescale_assay(w,min_events=3)
    assert "speed_ratio" in r and "by_generation" in r and "faster_than_genes" in r


def test_deep_secondary_evolution_assay_shape():
    from latent_worlds.secondary_evolution import deep_secondary_evolution_assay
    from latent_worlds.phase_map import long_horizon_config
    from latent_worlds.world import World
    w=World(long_horizon_config(agent_seed=0),seed=0).run(100)
    r=deep_secondary_evolution_assay(w,permutations=9,min_pairs=5)
    assert "supported" in r and "criteria" in r and "timescale" in r


def test_information_lineage_reconstruction_is_observer_side_and_structured():
    from latent_worlds.phase_map import long_horizon_config
    from latent_worlds.generational_search import turnover_profile
    from latent_worlds.world import World
    from latent_worlds.information_lineage import reconstruct_information_lineages
    cfg=long_horizon_config(information_level=.35,signal_cost=.03,communication_enabled=True,agent_seed=0)
    for k,v in turnover_profile().items(): setattr(cfg,k,v)
    w=World(cfg,seed=11).run(120)
    before=(w.time,len(w.agents),len(w.communication_log),len(w.social_log))
    r=reconstruct_information_lineages(w,min_cluster_rows=10)
    after=(w.time,len(w.agents),len(w.communication_log),len(w.social_log))
    assert before==after
    assert "edges" in r and "components" in r and "supported" in r


def test_genetic_information_decoupling_returns_bounded_nmi():
    from latent_worlds.phase_map import long_horizon_config
    from latent_worlds.generational_search import turnover_profile
    from latent_worlds.world import World
    from latent_worlds.information_lineage import genetic_information_decoupling
    cfg=long_horizon_config(information_level=.35,signal_cost=.03,communication_enabled=True,agent_seed=0)
    for k,v in turnover_profile().items(): setattr(cfg,k,v)
    w=World(cfg,seed=11).run(140)
    r=genetic_information_decoupling(w,min_cluster_rows=10)
    if r['variant_root_nmi'] is not None:
        assert 0.0 <= r['variant_root_nmi'] <= 1.0 + 1e-9
    assert 'decoupled' in r


def test_genetic_information_decoupling_by_generation_is_bounded():
    from latent_worlds.phase_map import long_horizon_config
    from latent_worlds.generational_search import turnover_profile
    from latent_worlds.world import World
    from latent_worlds.information_lineage import genetic_information_decoupling_by_generation
    cfg=long_horizon_config(information_level=.35,signal_cost=.03,communication_enabled=True,agent_seed=0)
    for k,v in turnover_profile().items(): setattr(cfg,k,v)
    w=World(cfg,seed=11).run(140)
    r=genetic_information_decoupling_by_generation(w,min_cluster_rows=10,min_rows=5)
    for row in r['by_generation'].values():
        if row['variant_root_nmi'] is not None: assert 0 <= row['variant_root_nmi'] <= 1+1e-9


def test_conditional_genetic_inheritance_assay_has_generation_rows():
    from latent_worlds.phase_map import long_horizon_config
    from latent_worlds.generational_search import turnover_profile
    from latent_worlds.world import World
    from latent_worlds.secondary_evolution import conditional_genetic_inheritance_assay
    cfg=long_horizon_config(information_level=.35,signal_cost=.03,communication_enabled=True,agent_seed=0)
    for k,v in turnover_profile().items(): setattr(cfg,k,v)
    w=World(cfg,seed=11).run(150)
    r=conditional_genetic_inheritance_assay(w,min_cluster_rows=10,permutations=19,min_pairs=5)
    assert 'by_generation' in r and 'deep_supported' in r


def test_autonomous_secondary_evolution_requires_genetic_conditioned_inheritance():
    from latent_worlds.phase_map import long_horizon_config
    from latent_worlds.generational_search import turnover_profile
    from latent_worlds.world import World
    from latent_worlds.secondary_evolution import autonomous_secondary_evolution_assay
    cfg=long_horizon_config(information_level=.35,signal_cost=.03,communication_enabled=True,agent_seed=0)
    for k,v in turnover_profile().items(): setattr(cfg,k,v)
    w=World(cfg,seed=11).run(160)
    r=autonomous_secondary_evolution_assay(w,permutations=19,min_pairs=5)
    assert 'inheritance_beyond_genetic_lineage' in r['criteria']
    if r['supported']:
        assert r['criteria']['inheritance_beyond_genetic_lineage']
