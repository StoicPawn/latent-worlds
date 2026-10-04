import numpy as np

from latent_worlds.config import SimulationConfig
from latent_worlds.world import World


def _world(strength: float) -> World:
    return World(
        SimulationConfig(
            generic_population_only=True,
            initial_agents=4,
            resource_patches=40,
            object_count=0,
            obstacle_count=0,
            pulse_spawn_rate=0.0,
            resource_wave_strength=strength,
        ),
        seed=11,
    )


def test_resource_wave_is_exact_noop_at_zero_strength():
    world = _world(0.0)
    assert world._resource_wave_factors() == [1.0] * len(world.resources)


def test_resource_wave_preserves_cross_patch_mean():
    world = _world(1.5)
    factors = np.asarray(world._resource_wave_factors(), dtype=float)
    assert len(factors) == len(world.resources)
    assert np.isclose(np.mean(factors), 1.0, atol=1e-12)
    assert np.std(factors) > 0.1
    assert np.all(factors > 0.0)


def test_resource_wave_moves_with_hidden_dynamics():
    world = _world(1.5)
    a = np.asarray(world._resource_wave_factors(), dtype=float)
    world.time = 37
    b = np.asarray(world._resource_wave_factors(), dtype=float)
    assert np.isclose(np.mean(b), 1.0, atol=1e-12)
    assert not np.allclose(a, b)


def test_step_assigns_wave_to_patches_without_changing_default_regrowth_rule():
    wave = _world(1.5)
    before = [p.richness for p in wave.resources]
    wave.step()
    assert any(abs(p.wave_factor - 1.0) > 1e-6 for p in wave.resources)

    control = _world(0.0)
    control.step()
    assert all(p.wave_factor == 1.0 for p in control.resources)
