from latent_worlds.world import World


def test_seed_is_reproducible():
    a = World(seed=11)
    b = World(seed=11)
    assert a.yield_law == b.yield_law
    assert a.climate == b.climate
    assert a.forcing_law == b.forcing_law
    assert a.radiation_law == b.radiation_law
    assert a.hidden_source_count == b.hidden_source_count


def test_agents_do_not_receive_law_parameters():
    world = World(seed=3)
    obs = world.observe(world.agents[0])
    assert hasattr(obs, "temperature")
    assert hasattr(obs, "radiation")
    assert not hasattr(obs, "optimum_temperature")
    assert not hasattr(obs, "interaction")
    assert not hasattr(obs, "source_count")


def test_simulation_advances():
    world = World(seed=5)
    world.run(10)
    assert world.time == 10 or not any(a.alive for a in world.agents)


def test_default_population_has_no_science_specific_agent():
    world = World(seed=21)
    assert all(a.kind != "scientist" for a in world.agents)
    assert all(a.kind != "curious" for a in world.agents)


def test_hidden_number_of_sources_varies_across_worlds():
    counts = {World(seed=s).hidden_source_count for s in range(12)}
    assert counts.issubset({2, 3, 4})
    assert len(counts) >= 2


def test_model_based_agent_has_no_discovery_reward_or_probe_policy():
    from latent_worlds.agents import ModelBasedAgent
    world = World(seed=22)
    agents = [a for a in world.agents if isinstance(a, ModelBasedAgent)]
    assert agents
    a = agents[0]
    assert not hasattr(a, "science")
    assert not hasattr(a, "epistemic_actions")
    world.run(80)
    assert a.probes == 0


def test_model_based_agent_accumulates_only_ordinary_experience():
    from latent_worlds.agents import ModelBasedAgent
    world = World(seed=12).run(100)
    agents = [a for a in world.agents if isinstance(a, ModelBasedAgent)]
    assert agents
    assert max(len(a.experiences) for a in agents) > 0


def test_cognition_metrics_are_observer_side():
    from latent_worlds.metrics import snapshot
    world = World(seed=13).run(120)
    report = snapshot(world)
    assert "cognition" in report
    assert report["cognition"]["hidden_source_count"] == world.hidden_source_count
    assert "mean_memory_gene" in report["cognition"]


def test_hidden_forcing_is_nontrivial():
    world = World(seed=4)
    values = [world.forcing_law.value(t) for t in range(0, 250, 10)]
    assert max(values) - min(values) > 1.0


def test_generation_is_inherited_and_incremented():
    world = World(seed=0)
    world.run(500)
    children = [a for a in world.agents if a.parent_id is not None]
    if children:
        assert all(a.generation >= 1 for a in children)


def test_default_world_has_anonymous_costly_channels_but_no_semantics():
    from latent_worlds.agents import RecurrentAgent
    world = World(seed=31)
    recurrent = [a for a in world.agents if isinstance(a, RecurrentAgent)]
    assert recurrent
    obs = world.observe(recurrent[0])
    assert hasattr(obs, "nearby_signals") and hasattr(obs, "nearby_marks")
    assert not hasattr(obs, "message_meaning")
    assert not hasattr(obs, "teacher")
    assert not hasattr(recurrent[0], "communication_reward")


def test_broadcast_costs_energy_without_reward_bonus():
    from latent_worlds.agents import Action, ActionKind
    world = World(seed=32)
    a = world.agents[0]
    before = a.energy
    reward = world._apply_action(a, Action(ActionKind.BROADCAST, payload=(0.1, -0.2, 0.3)))
    expected = world.config.basal_metabolism + world.config.signal_cost
    assert abs((before - a.energy) - expected) < 1e-9
    assert reward < 0.0
    assert len(world._next_signals) == 1


def test_inscriptions_persist_mechanically_and_decay():
    from latent_worlds.agents import Action, ActionKind
    world = World(seed=33)
    a = world.agents[0]
    world._apply_action(a, Action(ActionKind.INSCRIBE, payload=(0.4, 0.0, -0.1)))
    assert len(world.marks) == 1
    strength = world.marks[0].strength
    world.step()
    if world.marks:
        assert world.marks[0].strength < strength


def test_communication_metrics_are_observer_only():
    from latent_worlds.metrics import snapshot
    world = World(seed=34).run(60)
    report = snapshot(world)
    assert "communication" in report
    assert "broadcast_environment_r2" in report["communication"]
    assert all(not hasattr(a, "broadcast_environment_r2") for a in world.agents)


def test_world_has_continuous_matter_without_named_recipes():
    world = World(seed=41)
    assert world.objects
    assert hasattr(world, "matter_law")
    assert not hasattr(world, "recipes")
    assert not hasattr(world, "tech_tree")
    assert all(len(o.material) == 3 for o in world.objects)


def test_object_parameters_are_observed_but_matter_law_is_hidden():
    world = World(seed=42)
    a = world.agents[-1]
    obs = world.observe(a)
    assert hasattr(obs, "nearby_objects")
    assert not hasattr(obs, "material_weights")
    assert not hasattr(obs, "pair_weights")
    assert not hasattr(obs, "matter_law")


def test_manipulation_cost_is_paid_even_when_manipulation_is_censored():
    from latent_worlds.agents import Action, ActionKind
    from latent_worlds.config import SimulationConfig
    cfg = SimulationConfig(object_manipulation_enabled=False)
    world = World(config=cfg, seed=43)
    a = world.agents[0]
    before = a.energy
    reward = world._apply_action(a, Action(ActionKind.PICKUP))
    expected = cfg.basal_metabolism + cfg.manipulation_cost
    assert abs((before - a.energy) - expected) < 1e-9
    assert reward < 0.0
    assert a.held_object_id is None


def test_arrangement_changes_physical_conversion_without_device_labels():
    world = World(seed=44)
    x, y = 10.0, 10.0
    # Put two arbitrary continuous-material objects at the same evaluation site,
    # then separate one. The law may amplify or suppress; it must depend on layout.
    o1, o2 = world.objects[:2]
    o1.x = o2.x = x
    o1.y = o2.y = y
    together = world.matter_multiplier(x, y)
    o2.x, o2.y = world.config.width, world.config.height
    apart = world.matter_multiplier(x, y)
    assert abs(together - apart) > 1e-8


def test_technology_metrics_are_observer_side():
    from latent_worlds.metrics import snapshot
    world = World(seed=45).run(40)
    report = snapshot(world)
    assert "technology" in report
    assert "successful_pickups" in report["technology"]
    assert all(not hasattr(a, "boosted_harvest_fraction") for a in world.agents)


def test_agents_can_observe_conspecific_motion_without_social_semantics():
    world = World(seed=51)
    a = world.agents[-1]
    obs = world.observe(a)
    assert hasattr(obs, "nearby_agents")
    assert not hasattr(obs, "imitate")
    assert not hasattr(obs, "social_reward")
    if obs.nearby_agents:
        assert len(obs.nearby_agents[0]) == 4


def test_recurrent_plasticity_is_generic_and_heritable_gene():
    from latent_worlds.agents import RecurrentAgent
    world = World(seed=52)
    agents = [a for a in world.agents if isinstance(a, RecurrentAgent)]
    assert agents
    a = agents[0]
    assert 0.0 <= a.genome.plasticity <= 1.0
    assert 0.0 <= a.genome.social_attention <= 1.0
    assert not hasattr(a, "language_reward")
    assert not hasattr(a, "meaning")


def test_language_diagnostics_are_observer_side_only():
    from latent_worlds.metrics import snapshot
    world = World(seed=53).run(80)
    c = snapshot(world)["communication"]
    assert "receiver_action_r2_from_payload" in c
    assert "signal_generational_span" in c
    assert all(not hasattr(a, "receiver_action_r2_from_payload") for a in world.agents)


def test_world_creates_private_information_without_agent_semantics():
    world = World(seed=61)
    assert world.obstacles
    assert not hasattr(world.agents[0], "private_information_reward")
    a = world.agents[0]
    obs = world.observe(a)
    assert not hasattr(obs, "occlusion_map")
    assert not hasattr(obs, "information_value")


def test_occlusion_changes_visibility_but_not_world_existence():
    from latent_worlds.config import SimulationConfig
    a = World(config=SimulationConfig(occlusion_enabled=True), seed=62)
    b = World(config=SimulationConfig(occlusion_enabled=False), seed=62)
    assert len(a.resources) == len(b.resources)
    # Across all agents at least one visibility count should differ for this fixed world.
    va = [len(a.nearby(x)) for x in a.agents]
    vb = [len(b.nearby(x)) for x in b.agents]
    assert any(x != y for x, y in zip(va, vb))


def test_local_perturbations_are_world_dynamics_not_tasks():
    from latent_worlds.config import SimulationConfig
    cfg = SimulationConfig(pulse_spawn_rate=1.0)
    world = World(config=cfg, seed=63)
    world.step()
    assert world.pulses
    assert all(not hasattr(a, "pulse_reward") for a in world.agents)
    assert all(not hasattr(a, "seek_pulse") for a in world.agents)


def test_information_structure_metrics_are_observer_side():
    from latent_worlds.metrics import snapshot
    world = World(seed=64).run(30)
    info = snapshot(world)["information_structure"]
    assert "private_information_index" in info
    assert all(not hasattr(a, "private_information_index") for a in world.agents)


def test_publication_mode_uses_one_generic_agent_substrate():
    from latent_worlds.config import SimulationConfig
    world = World(SimulationConfig(generic_population_only=True), seed=71)
    assert {a.kind for a in world.agents} == {"recurrent"}
    # Roles are not named into the population by the world.
    assert all(not hasattr(a, "role") for a in world.agents)


def test_emergence_audit_is_observer_side_and_conservative():
    from latent_worlds.emergence import factorial_emergence
    r = factorial_emergence(seed=72, steps=25)
    assert "candidate_protocol" in r["evidence"]
    assert all(not hasattr(a, "candidate_protocol") for a in World(seed=72).agents)


def test_behavioral_roles_are_measured_not_assigned():
    from latent_worlds.config import SimulationConfig
    from latent_worlds.metrics import snapshot
    world = World(SimulationConfig(generic_population_only=True), seed=73).run(60)
    d = snapshot(world)["behavioral_diversity"]
    assert "mean_pairwise_action_distance" in d
    assert all(not hasattr(a, "behavioral_role") for a in world.agents)


def test_longitudinal_detector_is_observer_only():
    from latent_worlds.longitudinal import run_longitudinal
    r = run_longitudinal(seed=81, steps=80, epoch=20)
    assert "transition_candidates" in r
    assert len(r["epochs"]) >= 2
    assert all(not hasattr(a, "novelty_score") for a in World(seed=81).agents)


def test_publication_longitudinal_run_uses_generic_substrate():
    from latent_worlds.longitudinal import run_longitudinal
    r = run_longitudinal(seed=82, steps=40, epoch=20)
    kinds = r["final"]["snapshot"]["ever_born_by_type"]
    assert set(kinds) == {"recurrent"}


def test_longitudinal_recent_activity_does_not_treat_old_signals_as_current():
    from latent_worlds.longitudinal import run_longitudinal
    r = run_longitudinal(seed=83, steps=60, epoch=20)
    assert "recent" in r["epochs"][-1]
    assert "signal_generation_count" in r["epochs"][-1]["recent"]
