"""Observer-side trajectory features for pre-emergence transition prediction.

Nothing in this module is visible to agents and nothing changes fitness, physics,
or the controller substrate.  It records preregistered population-level metrics
at early checkpoints and converts each scalar trajectory into simple dynamical
features: level, slope, variance, and lag-1 autocorrelation.
"""
from __future__ import annotations

from collections import defaultdict
import numpy as np

from .metrics import snapshot
from .phase_map import long_horizon_config
from .pretransition_prediction import trajectory_features
from .replication import standard_turnover_overrides
from .world import World

DEFAULT_SERIES = (
    "population",
    "births",
    "deaths",
    "total_harvest",
    "broadcasts",
    "signal_receptions",
    "broadcast_environment_r2",
    "receiver_action_r2",
    "mean_signal_input_sensitivity",
    "signal_generational_span",
    "private_information_index",
)


def _observer_row(world: World) -> dict:
    s = snapshot(world)
    c = s.get("communication", {})
    info = s.get("information_structure", {})
    return {
        "population": float(s.get("population", 0.0)),
        "births": float(world.births),
        "deaths": float(world.deaths),
        "total_harvest": float(s.get("total_harvest", 0.0)),
        "broadcasts": float(c.get("broadcasts", 0.0)),
        "signal_receptions": float(c.get("signal_reception_events", c.get("receiver_events", 0.0))),
        "broadcast_environment_r2": float(c.get("broadcast_environment_r2") or 0.0),
        "receiver_action_r2": float(c.get("receiver_action_r2_from_payload") or 0.0),
        "mean_signal_input_sensitivity": float(c.get("mean_signal_input_sensitivity") or 0.0),
        "signal_generational_span": float(c.get("signal_generational_span") or 0.0),
        "private_information_index": float(info.get("private_information_index") or 0.0),
    }


def early_trajectory(world_seed: int, agent_seed: int = 0, *,
                     start: int = 50, stop: int = 250, interval: int = 25,
                     information_level: float = .35, signal_cost: float = .03,
                     overrides: dict | None = None) -> dict:
    """Run one early history and return observer-only metric trajectories."""
    cfg = long_horizon_config(
        information_level=information_level,
        signal_cost=signal_cost,
        communication_enabled=True,
        agent_seed=agent_seed,
    )
    for k, v in (standard_turnover_overrides() if overrides is None else overrides).items():
        setattr(cfg, k, v)
    w = World(cfg, seed=world_seed)
    checkpoints = set(range(int(start), int(stop) + 1, int(interval)))
    rows = []
    for _ in range(int(stop)):
        w.step()
        if w.time in checkpoints:
            rows.append({"time": int(w.time), **_observer_row(w)})
        if not any(a.alive for a in w.agents):
            break
    return {
        "world_seed": int(world_seed),
        "agent_seed": int(agent_seed),
        "start": int(start),
        "stop": int(stop),
        "interval": int(interval),
        "rows": rows,
    }


def featurize_trajectory(run: dict, series=DEFAULT_SERIES) -> dict:
    """Convert one early trajectory into a flat, transparent feature vector."""
    rows = list(run.get("rows", ()))
    out = {
        "world_seed": int(run.get("world_seed", -1)),
        "agent_seed": int(run.get("agent_seed", -1)),
        "n_checkpoints": len(rows),
    }
    for key in series:
        vals = [float(r.get(key, 0.0) or 0.0) for r in rows]
        f = trajectory_features(vals)
        for stat, value in f.items():
            out[f"{key}__{stat}"] = float(value)
    return out


def trajectory_feature_names(series=DEFAULT_SERIES) -> tuple[str, ...]:
    stats = ("level", "slope", "variance", "lag1_autocorrelation")
    return tuple(f"{key}__{stat}" for key in series for stat in stats)
