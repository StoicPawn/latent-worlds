from __future__ import annotations

"""Observer-side value-of-foresight assay for world-side forecast pressure.

This module never changes an agent, reward, or simulation trajectory. It asks a
more basic design question before another evolutionary experiment is run:

    if an ideal route chooser knew the future hidden ecology, would that knowledge
    actually improve ordinary energetic return relative to an equally capable
    chooser that knows only the current ecology?

A forecast-pressure intervention should pass this affordance test before it is
used as evidence about learning or evolution.
"""

from contextlib import contextmanager
import math
from typing import Iterable, Sequence

import numpy as np

from .config import SimulationConfig
from .phase_map import long_horizon_config
from .world import World


@contextmanager
def _temporary_time(world: World, t: int):
    old = int(world.time)
    world.time = int(t)
    try:
        yield
    finally:
        world.time = old


def _patch_gross_yield(world: World, patch_index: int, t: int) -> float:
    """One-harvest energetic value at a patch at observer time t."""
    patch = world.resources[int(patch_index)]
    with _temporary_time(world, int(t)):
        factors = world._resource_wave_factors()
        temp, rad = world.physical_state(patch.x, patch.y)
        base = world.yield_law.efficiency(temp, rad)
        matter = world.matter_law.multiplier(
            patch.x, patch.y, temp, rad, world.objects
        )
    efficiency = base * float(factors[int(patch_index)]) * matter
    return float(min(patch.capacity, 1.3 * efficiency))


def _travel_steps(distance: float, speed: float) -> int:
    if speed <= 0:
        raise ValueError("speed must be positive")
    return int(math.ceil(float(distance) / float(speed)))


def _travel_cost(world: World, distance: float, speed: float) -> float:
    steps = _travel_steps(distance, speed)
    return float(
        steps * (world.config.basal_metabolism + world.config.move_cost * speed)
        + world.config.harvest_cost
    )


def _choice_value(
    world: World,
    origin: tuple[float, float],
    patch_index: int,
    decision_time: int,
    *,
    speed: float,
    evaluate_at_arrival: bool,
) -> float:
    patch = world.resources[int(patch_index)]
    distance = math.hypot(patch.x - origin[0], patch.y - origin[1])
    arrival = int(decision_time) + _travel_steps(distance, speed)
    t = arrival if evaluate_at_arrival else int(decision_time)
    return float(
        _patch_gross_yield(world, patch_index, t)
        - _travel_cost(world, distance, speed)
    )


def route_choice(
    world: World,
    origin: tuple[float, float],
    decision_time: int,
    *,
    speed: float = 1.0,
    foresight: bool,
) -> dict:
    """Choose the best patch under current-only or arrival-time information.

    Both choosers see the same complete set of candidate patches and use the
    same energetic travel cost. The only difference is whether patch value is
    evaluated now (myopic) or at the chooser's own arrival time (foresight).
    """
    if not world.resources:
        raise ValueError("world must contain resource patches")
    scores = [
        _choice_value(
            world,
            origin,
            i,
            int(decision_time),
            speed=float(speed),
            evaluate_at_arrival=bool(foresight),
        )
        for i in range(len(world.resources))
    ]
    chosen = int(np.argmax(scores))
    patch = world.resources[chosen]
    distance = float(math.hypot(patch.x - origin[0], patch.y - origin[1]))
    arrival = int(decision_time) + _travel_steps(distance, speed)
    realized = _choice_value(
        world,
        origin,
        chosen,
        int(decision_time),
        speed=float(speed),
        evaluate_at_arrival=True,
    )
    return {
        "patch_index": chosen,
        "decision_score": float(scores[chosen]),
        "realized_value": float(realized),
        "distance": distance,
        "arrival_time": arrival,
    }


def value_of_foresight(
    world_seed: int,
    *,
    wave_strength: float,
    speed: float = 1.0,
    times: Sequence[int] = tuple(range(0, 1201, 20)),
    grid_x: int = 7,
    grid_y: int = 7,
    information_level: float = 0.35,
    signal_cost: float = 0.03,
    config_overrides: dict | None = None,
) -> dict:
    """Canonical observer-side energetic value of perfect ecological foresight."""
    cfg = long_horizon_config(
        information_level=float(information_level),
        signal_cost=float(signal_cost),
        communication_enabled=True,
        agent_seed=0,
    )
    cfg.resource_wave_strength = float(wave_strength)
    for key, value in dict(config_overrides or {}).items():
        if not hasattr(cfg, key):
            raise ValueError(f"unknown SimulationConfig field: {key}")
        setattr(cfg, key, value)

    world = World(cfg, seed=int(world_seed))
    xs = np.linspace(0.0, cfg.width, int(grid_x))
    ys = np.linspace(0.0, cfg.height, int(grid_y))
    origins = [(float(x), float(y)) for x in xs for y in ys]

    advantages = []
    myopic_values = []
    oracle_values = []
    choice_changes = 0
    arrival_leads = []
    for t in tuple(int(v) for v in times):
        for origin in origins:
            myopic = route_choice(
                world, origin, t, speed=float(speed), foresight=False
            )
            oracle = route_choice(
                world, origin, t, speed=float(speed), foresight=True
            )
            advantage = float(oracle["realized_value"] - myopic["realized_value"])
            advantages.append(advantage)
            myopic_values.append(float(myopic["realized_value"]))
            oracle_values.append(float(oracle["realized_value"]))
            choice_changes += int(oracle["patch_index"] != myopic["patch_index"])
            arrival_leads.append(
                abs(int(oracle["arrival_time"]) - int(t))
            )

    a = np.asarray(advantages, dtype=float)
    m = np.asarray(myopic_values, dtype=float)
    o = np.asarray(oracle_values, dtype=float)
    denom = max(abs(float(np.mean(m))), 1e-9)
    return {
        "world_seed": int(world_seed),
        "wave_strength": float(wave_strength),
        "speed": float(speed),
        "samples": int(len(a)),
        "mean_myopic_realized_value": float(np.mean(m)),
        "mean_foresight_realized_value": float(np.mean(o)),
        "mean_foresight_advantage": float(np.mean(a)),
        "median_foresight_advantage": float(np.median(a)),
        "p90_foresight_advantage": float(np.quantile(a, 0.90)),
        "positive_advantage_fraction": float(np.mean(a > 1e-12)),
        "choice_divergence_fraction": float(choice_changes / max(len(a), 1)),
        "relative_mean_advantage": float(np.mean(a) / denom),
        "mean_oracle_travel_horizon": float(np.mean(arrival_leads)),
    }


def forecast_value_grid(
    world_seed: int,
    wave_strengths: Iterable[float],
    speeds: Iterable[float],
    *,
    times: Sequence[int] = tuple(range(0, 1201, 20)),
    config_overrides: dict | None = None,
) -> dict:
    cells = [
        value_of_foresight(
            int(world_seed),
            wave_strength=float(wave),
            speed=float(speed),
            times=times,
            config_overrides=config_overrides,
        )
        for wave in wave_strengths
        for speed in speeds
    ]
    ranked = sorted(
        cells,
        key=lambda c: (
            c["relative_mean_advantage"],
            c["positive_advantage_fraction"],
        ),
        reverse=True,
    )
    return {
        "world_seed": int(world_seed),
        "cells": cells,
        "ranked": ranked,
        "interpretation": (
            "This is an observer-side ecological affordance diagnostic. It does "
            "not measure agent cognition and cannot support an epistemic claim."
        ),
    }
