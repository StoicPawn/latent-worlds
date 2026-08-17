"""Observer-side tools for causal ecological transition studies.

These helpers do not modify agent objectives or controllers.  They make world-side
interventions while preserving the underlying initialized world wherever possible,
so that emergence hypotheses are not confounded by unrelated RNG changes.
"""
from __future__ import annotations

from .phase_map import long_horizon_config
from .replication import standard_turnover_overrides
from .world import World
from .metrics import snapshot


def matched_world_config(*, agent_seed: int = 0, signal_cost: float = .03,
                         information_level: float = .35,
                         active_obstacle_fraction: float = 1.0):
    """Config for matched occlusion interventions.

    `information_level` fixes the number and coordinates of initialized obstacles.
    `active_obstacle_fraction` changes only which prefix of that already-generated
    obstacle set participates in line-of-sight.  Resource/object initialization is
    therefore identical across fractions for a fixed seed.
    """
    cfg = long_horizon_config(
        information_level=float(information_level),
        signal_cost=float(signal_cost),
        communication_enabled=True,
        agent_seed=int(agent_seed),
    )
    for k, v in standard_turnover_overrides().items():
        setattr(cfg, k, v)
    cfg.active_obstacle_fraction = float(active_obstacle_fraction)
    return cfg


def pretransition_profile(world_seed: int, agent_seed: int = 0, *, steps: int = 150,
                          signal_cost: float = .03, information_level: float = .35,
                          active_obstacle_fraction: float = 1.0) -> dict:
    """Collect observer-only features before the late-generation causal assay."""
    cfg = matched_world_config(
        agent_seed=agent_seed, signal_cost=signal_cost,
        information_level=information_level,
        active_obstacle_fraction=active_obstacle_fraction,
    )
    w = World(cfg, seed=int(world_seed)).run(int(steps))
    s = snapshot(w)
    c = s["communication"]
    info = s["information_structure"]
    return {
        "world_seed": int(world_seed),
        "agent_seed": int(agent_seed),
        "steps": int(steps),
        "signal_cost": float(signal_cost),
        "active_obstacle_fraction": float(active_obstacle_fraction),
        "population": int(s["population"]),
        "births": int(w.births),
        "deaths": int(w.deaths),
        "total_harvest": float(s["total_harvest"]),
        "broadcasts": int(c.get("broadcasts", 0)),
        "signal_receptions": int(c.get("signal_reception_events", 0)),
        "broadcast_environment_r2": c.get("broadcast_environment_r2"),
        "receiver_action_r2": c.get("receiver_action_r2_from_payload"),
        "mean_signal_input_sensitivity": c.get("mean_signal_input_sensitivity"),
        "signal_generational_span": int(c.get("signal_generational_span") or 0),
        "private_information_index": info.get("private_information_index"),
        "hidden_source_count": int(w.hidden_source_count),
    }


def matched_initialization_signature(world_seed: int, *, agent_seed: int = 0,
                                     signal_cost: float = .03,
                                     information_level: float = .35,
                                     fractions=(0.0, .33, .67, 1.0)) -> list[dict]:
    """Prove that matched obstacle-fraction interventions preserve non-occlusion state."""
    rows = []
    for frac in fractions:
        cfg = matched_world_config(
            agent_seed=agent_seed, signal_cost=signal_cost,
            information_level=information_level,
            active_obstacle_fraction=float(frac),
        )
        w = World(cfg, seed=int(world_seed))
        rows.append({
            "fraction": float(frac),
            "resource_signature": tuple((round(r.x, 12), round(r.y, 12), round(r.capacity, 12))
                                        for r in w.resources),
            "object_signature": tuple((round(o.x, 12), round(o.y, 12), round(o.mass, 12))
                                      for o in w.objects),
            "forcing_periods": tuple(round(x, 12) for x in w.forcing_law.periods),
            "obstacle_signature": tuple((round(o.x, 12), round(o.y, 12), round(o.radius, 12))
                                        for o in w.obstacles),
        })
    return rows
