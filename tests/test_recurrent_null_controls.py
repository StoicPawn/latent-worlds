import numpy as np

from latent_worlds.agents import RecurrentAgent
from latent_worlds.config import SimulationConfig
from latent_worlds.world import World


def _cfg(**kwargs):
    base = dict(
        generic_population_only=True,
        initial_agents=1,
        resource_patches=12,
        object_count=4,
        obstacle_count=0,
        pulse_spawn_rate=0.0,
        max_population=10,
    )
    base.update(kwargs)
    return SimulationConfig(**base)


def test_recurrent_learning_null_keeps_controller_weights_fixed():
    world = World(_cfg(recurrent_learning_enabled=False), seed=4)
    agent = world.agents[0]
    world.step()
    assert isinstance(agent, RecurrentAgent)
    assert agent._initialized
    before = agent.W_out.copy()
    for _ in range(20):
        if not agent.alive:
            break
        world.step()
    np.testing.assert_allclose(agent.W_out, before, atol=0.0, rtol=0.0)


def test_recurrent_weight_inheritance_null_starts_child_uninitialized():
    world = World(_cfg(recurrent_weight_inheritance_enabled=False), seed=7)
    parent = world.agents[0]
    world.step()
    assert parent._initialized
    child = world._spawn(RecurrentAgent, parent, parent.genome)
    assert not child._initialized
    assert child.W_in is None
    assert child.W_rec is None
    assert child.W_out is None


def test_default_recurrent_inheritance_preserves_controller_lineage():
    world = World(_cfg(recurrent_weight_inheritance_enabled=True), seed=8)
    parent = world.agents[0]
    world.step()
    assert parent._initialized
    child = world._spawn(RecurrentAgent, parent, parent.genome)
    assert child._initialized
    assert child.W_in is not None
    assert child.W_rec is not None
    assert child.W_out is not None
