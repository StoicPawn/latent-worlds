"""Structural sensory bottleneck audit, with exact reproducible fixture."""
from dataclasses import replace
import numpy as np

from latent_worlds.agents.base import Genome, Observation
from latent_worlds.agents.recurrent import RecurrentAgent


def _obs(resources):
    return Observation(
        time=100, x=8.0, y=8.0, energy=20.0,
        temperature=12.0, radiation=0.5,
        nearby_resources=resources,
        last_action=None, last_yield=0.0,
        nearby_signals=[], nearby_marks=[],
        nearby_objects=[], held_object=None,
        nearby_agents=[],
        world_width=30.0, world_height=30.0,
        context_features_enabled=True,
    )


def test_recurrent_controller_explicitly_encodes_only_nearest_resource():
    """Changing any second/third resource cannot change CURRENT neural features."""
    agent = RecurrentAgent(0, 8.0, 8.0, 20.0, Genome())
    base = _obs([(1.0, 0.0, 4.0), (2.0, 1.0, 5.0)])
    new_far = replace(base, nearby_resources=[
        (1.0, 0.0, 4.0), (-3.0, -2.0, 1000.0), (4.0, 0.0, 500.0)])
    assert np.array_equal(agent._features(base, 3), agent._features(new_far, 3))

    new_nearest = replace(base, nearby_resources=[
        (1.5, 0.0, 4.0), (2.0, 1.0, 5.0)])
    assert not np.array_equal(agent._features(base, 3), agent._features(new_nearest, 3))


def test_empty_resource_observation_is_distinct():
    agent = RecurrentAgent(1, 8.0, 8.0, 20.0, Genome())
    assert not np.array_equal(
        agent._features(_obs([]), 3),
        agent._features(_obs([(1.0, 0.0, 1.0)]), 3),
    )



def test_immediate_recurrent_action_is_invariant_to_non_nearest_resources():
    import copy
    original = RecurrentAgent(7, 8.0, 8.0, 20.0, Genome())
    a = copy.deepcopy(original)
    b = copy.deepcopy(original)
    first = _obs([(1.0, 0.0, 4.0), (2.0, 1.0, 5.0)])
    other = replace(first, nearby_resources=[
        (1.0, 0.0, 4.0), (-2.0, 1.0, 999.0),
        (3.0, -1.0, 5.0)])
    action_a = a.act(first, np.random.default_rng(2026))
    action_b = b.act(other, np.random.default_rng(2026))
    assert action_a == action_b
    assert np.array_equal(a.hidden, b.hidden)
    assert np.array_equal(a.W_out, b.W_out)
