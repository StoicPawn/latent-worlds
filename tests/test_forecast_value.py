import numpy as np

from latent_worlds.forecast_value import (
    route_choice,
    value_of_foresight,
)
from latent_worlds.phase_map import long_horizon_config
from latent_worlds.world import World


def _world(strength: float) -> World:
    cfg = long_horizon_config(
        information_level=0.35,
        signal_cost=0.03,
        communication_enabled=True,
        agent_seed=0,
    )
    cfg.resource_wave_strength = strength
    cfg.active_obstacle_fraction = 0.75
    return World(cfg, seed=11)


def test_oracle_choice_never_underperforms_myopic_realized_choice():
    world = _world(1.5)
    for t in (0, 73, 251, 719):
        for origin in ((2.0, 2.0), (15.0, 15.0), (28.0, 8.0)):
            myopic = route_choice(world, origin, t, speed=1.0, foresight=False)
            oracle = route_choice(world, origin, t, speed=1.0, foresight=True)
            assert oracle["realized_value"] + 1e-12 >= myopic["realized_value"]


def test_value_of_foresight_reports_nonnegative_mean_advantage():
    result = value_of_foresight(
        11,
        wave_strength=1.5,
        speed=1.0,
        times=(0, 100, 200),
        grid_x=3,
        grid_y=3,
        config_overrides={"active_obstacle_fraction": 0.75},
    )
    assert result["samples"] == 27
    assert result["mean_foresight_advantage"] >= -1e-12
    assert 0.0 <= result["positive_advantage_fraction"] <= 1.0
    assert 0.0 <= result["choice_divergence_fraction"] <= 1.0


def test_forecast_value_changes_with_wave_strength():
    a = value_of_foresight(
        11,
        wave_strength=0.0,
        speed=1.0,
        times=(0, 80, 160, 240),
        grid_x=3,
        grid_y=3,
        config_overrides={"active_obstacle_fraction": 0.75},
    )
    b = value_of_foresight(
        11,
        wave_strength=2.5,
        speed=1.0,
        times=(0, 80, 160, 240),
        grid_x=3,
        grid_y=3,
        config_overrides={"active_obstacle_fraction": 0.75},
    )
    assert not np.isclose(
        a["mean_foresight_advantage"],
        b["mean_foresight_advantage"],
        atol=1e-8,
    )
