"""v4.0: test whether the v3.9 W11 basin generalises across population seeds.

Consumes the committed v3.9 result and applies a preregistered deterministic
selection rule. No agent/world rule is modified.
"""
from __future__ import annotations

import json
from pathlib import Path

from latent_worlds.causal_transmission import direct_reception_transmission_assay
from latent_worlds.replication import standard_turnover_overrides

RESULT = Path("docs/EXPERIMENT_v3.9_RESULTS.json")
WORLD_SEED = 11
AGENT_SEEDS = (0, 1, 2, 3, 4)
CANONICAL = (1.0, 0.03)
MAX_SUPPORTED = 6
MAX_BOUNDARY_CONTROLS = 4


def _grid_index(values, x):
    return list(values).index(x)


def _manhattan_grid_distance(a, b, occ, costs):
    return abs(_grid_index(occ, a[0]) - _grid_index(occ, b[0])) + abs(_grid_index(costs, a[1]) - _grid_index(costs, b[1]))


def select_cells(data: dict) -> list[dict]:
    occ = list(data["occlusion_values"])
    costs = list(data["signal_cost_values"])
    cells = list(data["cells"])
    supported = [q for q in cells if q.get("supported")]

    def priority(q):
        d = _manhattan_grid_distance((q["active_obstacle_fraction"], q["signal_cost"]), CANONICAL, occ, costs)
        gain = q.get("g2_mean_copy_gain")
        gain = float(gain) if gain is not None else float("-inf")
        return (d, -gain, q["active_obstacle_fraction"], q["signal_cost"])

    chosen_supported = sorted(supported, key=priority)[:MAX_SUPPORTED]
    chosen_keys = {(q["active_obstacle_fraction"], q["signal_cost"]) for q in chosen_supported}

    boundary = []
    for q in cells:
        if q.get("supported"):
            continue
        key = (q["active_obstacle_fraction"], q["signal_cost"])
        if any(_manhattan_grid_distance(key, sk, occ, costs) == 1 for sk in chosen_keys):
            boundary.append(q)
    boundary = sorted(boundary, key=priority)[:MAX_BOUNDARY_CONTROLS]

    out = []
    for q in chosen_supported:
        out.append({**q, "selection_role": "supported"})
    for q in boundary:
        out.append({**q, "selection_role": "boundary_control"})
    return out


def assay(cell: dict, agent_seed: int) -> dict:
    overrides = dict(standard_turnover_overrides())
    overrides["active_obstacle_fraction"] = float(cell["active_obstacle_fraction"])
    r = direct_reception_transmission_assay(
        world_seed=WORLD_SEED,
        agent_seed=int(agent_seed),
        steps=650,
        assay_start=250,
        min_generation=2,
        information_level=.35,
        signal_cost=float(cell["signal_cost"]),
        config_overrides=overrides,
        max_events=300,
        permutations=99,
    )
    g2 = r.get("by_generation", {}).get(2, {})
    return {
        "agent_seed": int(agent_seed),
        "supported": bool(r.get("supported", False)),
        "supported_generations": list(r.get("supported_generations", [])),
        "g2_mean_copy_gain": g2.get("mean_copy_gain"),
        "g2_permutation_p": g2.get("permutation_p"),
        "g2_natural_broadcasts": int(g2.get("natural_broadcasts", 0) or 0),
    }


def main() -> None:
    data = json.loads(RESULT.read_text())
    selected = select_cells(data)
    rows = []
    for cell in selected:
        reps = [assay(cell, a) for a in AGENT_SEEDS]
        independent = [r for r in reps if r["agent_seed"] != 0]
        hits = sum(int(r["supported"]) for r in reps)
        independent_hits = sum(int(r["supported"]) for r in independent)
        rows.append({
            "active_obstacle_fraction": cell["active_obstacle_fraction"],
            "signal_cost": cell["signal_cost"],
            "selection_role": cell["selection_role"],
            "v3_9_supported": bool(cell.get("supported")),
            "population_seed_results": reps,
            "support_fraction_all": hits / len(reps),
            "independent_support_fraction": independent_hits / max(1, len(independent)),
            "extends_beyond_A0": bool(independent_hits > 0),
            "population_robust": bool(independent_hits >= 3),
        })

    supported_rows = [r for r in rows if r["selection_role"] == "supported"]
    controls = [r for r in rows if r["selection_role"] == "boundary_control"]
    print(json.dumps({
        "world_seed": WORLD_SEED,
        "agent_seeds": list(AGENT_SEEDS),
        "selected_supported_cells": len(supported_rows),
        "selected_boundary_controls": len(controls),
        "supported_cells_extending_beyond_A0": sum(int(r["extends_beyond_A0"]) for r in supported_rows),
        "population_robust_supported_cells": sum(int(r["population_robust"]) for r in supported_rows),
        "boundary_controls_with_independent_support": sum(int(r["extends_beyond_A0"]) for r in controls),
        "cells": rows,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
