"""v3.9: matched causal basin map around W11.

This benchmark changes only world-side occlusion activity and signal cost.  It
uses the same initialized W11 world seed and A0 population seed, then runs the
same direct same-agent removal assay in each ecological cell.
"""
from __future__ import annotations

import json

from latent_worlds.causal_transmission import direct_reception_transmission_assay
from latent_worlds.replication import standard_turnover_overrides

WORLD_SEED = 11
AGENT_SEED = 0
OCCLUSION = (0.0, 0.25, 0.50, 0.75, 1.0)
SIGNAL_COST = (0.0, 0.01, 0.02, 0.03, 0.04, 0.05, 0.065)


def one_cell(frac: float, cost: float) -> dict:
    overrides = dict(standard_turnover_overrides())
    overrides["active_obstacle_fraction"] = float(frac)
    r = direct_reception_transmission_assay(
        world_seed=WORLD_SEED,
        agent_seed=AGENT_SEED,
        steps=650,
        assay_start=250,
        min_generation=2,
        information_level=.35,
        signal_cost=float(cost),
        config_overrides=overrides,
        max_events=300,
        permutations=99,
    )
    g2 = r.get("by_generation", {}).get(2, {})
    return {
        "active_obstacle_fraction": float(frac),
        "signal_cost": float(cost),
        "supported": bool(r.get("supported", False)),
        "supported_generations": list(r.get("supported_generations", [])),
        "g2_natural_broadcasts": int(g2.get("natural_broadcasts", 0) or 0),
        "g2_mean_copy_gain": g2.get("mean_copy_gain"),
        "g2_positive_fraction": g2.get("copy_gain_positive_fraction"),
        "g2_permutation_p": g2.get("permutation_p"),
    }


def main() -> None:
    cells = [one_cell(f, c) for f in OCCLUSION for c in SIGNAL_COST]
    supported = [q for q in cells if q["supported"]]
    # Count local transitions along rows/columns. A large boundary count is a
    # simple observer-side signature of a fragmented/non-monotone basin.
    lookup = {(q["active_obstacle_fraction"], q["signal_cost"]): q["supported"] for q in cells}
    boundary_edges = 0
    for f in OCCLUSION:
        for a, b in zip(SIGNAL_COST, SIGNAL_COST[1:]):
            boundary_edges += int(lookup[(f, a)] != lookup[(f, b)])
    for c in SIGNAL_COST:
        for a, b in zip(OCCLUSION, OCCLUSION[1:]):
            boundary_edges += int(lookup[(a, c)] != lookup[(b, c)])
    print(json.dumps({
        "world_seed": WORLD_SEED,
        "agent_seed": AGENT_SEED,
        "occlusion_values": list(OCCLUSION),
        "signal_cost_values": list(SIGNAL_COST),
        "n_cells": len(cells),
        "supported_cells": len(supported),
        "supported_fraction": len(supported) / len(cells),
        "boundary_edges": boundary_edges,
        "cells": cells,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
