import numpy as np

from latent_worlds.agents.base import Genome, Observation
from latent_worlds.agents.recurrent import RecurrentAgent
from latent_worlds.config import SimulationConfig
from latent_worlds.world import World


def _observation() -> Observation:
    return Observation(
        time=17,
        x=8.0,
        y=11.0,
        energy=20.0,
        temperature=14.5,
        radiation=1.2,
        nearby_resources=[],
        last_action=None,
        last_yield=0.7,
        nearby_signals=[],
        nearby_marks=[],
        nearby_objects=[],
        held_object=None,
        nearby_agents=[],
        world_width=30.0,
        world_height=30.0,
        context_features_enabled=True,
    )


def _agent(enabled: bool):
    a = RecurrentAgent(
        0, 8.0, 11.0, 20.0,
        Genome(plasticity=1.0, exploration=0.0),
    )
    a.state_plasticity_enabled = enabled
    return a


def test_output_only_plasticity_leaves_internal_weights_fixed():
    rng = np.random.default_rng(4)
    a = _agent(False)
    action = a.act(_observation(), rng)
    win = a.W_in.copy()
    wrec = a.W_rec.copy()
    wout = a.W_out.copy()
    a.learn(_observation(), action, 1.5)

    np.testing.assert_allclose(a.W_in, win, atol=0.0, rtol=0.0)
    np.testing.assert_allclose(a.W_rec, wrec, atol=0.0, rtol=0.0)
    assert not np.allclose(a.W_out, wout)


def test_state_plasticity_updates_input_and_recurrent_weights():
    rng = np.random.default_rng(4)
    a = _agent(True)
    action = a.act(_observation(), rng)
    win = a.W_in.copy()
    wrec = a.W_rec.copy()
    a.learn(_observation(), action, 1.5)

    assert np.max(np.abs(a.W_in - win)) > 0.0
    assert np.max(np.abs(a.W_rec - wrec)) > 0.0


def test_world_wires_state_plasticity_flag_without_changing_default():
    off = World(
        SimulationConfig(
            generic_population_only=True,
            initial_agents=1,
            resource_patches=4,
            object_count=0,
            obstacle_count=0,
            pulse_spawn_rate=0.0,
        ),
        seed=2,
    )
    on = World(
        SimulationConfig(
            generic_population_only=True,
            initial_agents=1,
            resource_patches=4,
            object_count=0,
            obstacle_count=0,
            pulse_spawn_rate=0.0,
            recurrent_state_plasticity_enabled=True,
        ),
        seed=2,
    )
    assert off.agents[0].state_plasticity_enabled is False
    assert on.agents[0].state_plasticity_enabled is True
