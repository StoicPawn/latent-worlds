import numpy as np

from latent_worlds.agents import RecurrentAgent
from latent_worlds.config import SimulationConfig
from latent_worlds.world import World


def _cfg(enabled: bool):
    return SimulationConfig(
        generic_population_only=True,
        initial_agents=1,
        resource_patches=8,
        object_count=2,
        obstacle_count=0,
        pulse_spawn_rate=0.0,
        recurrent_context_features_enabled=enabled,
    )


def test_context_feature_flag_changes_only_recurrent_input_width():
    legacy = World(_cfg(False), seed=3)
    enriched = World(_cfg(True), seed=3)

    a0 = legacy.agents[0]
    a1 = enriched.agents[0]
    o0 = legacy.observe(a0)
    o1 = enriched.observe(a1)

    x0 = a0._features(o0, 3)
    x1 = a1._features(o1, 3)

    assert len(x1) == len(x0) + 3
    np.testing.assert_allclose(x1[:8], x0[:8], atol=0.0, rtol=0.0)
    assert o0.context_features_enabled is False
    assert o1.context_features_enabled is True


def test_context_contains_normalized_position_and_last_yield():
    world = World(_cfg(True), seed=5)
    agent = world.agents[0]
    agent.last_yield = 1.6
    obs = world.observe(agent)
    x = agent._features(obs, 3)

    # base is 8 dims; optional context follows it.
    np.testing.assert_allclose(
        x[8:11],
        np.asarray([
            agent.x / world.config.width,
            agent.y / world.config.height,
            0.8,
        ]),
        atol=1e-12,
        rtol=0.0,
    )
