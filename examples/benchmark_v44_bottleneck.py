"""v4.4: frozen local ecological scan around mechanism/adaptation split histories."""
from __future__ import annotations

import json

from latent_worlds.replication import direct_replication_followup, standard_turnover_overrides

WORLD_SEED = 11
HISTORIES = [
    {"agent_seed": 18, "v4_3_class": "mechanism_positive_adaptation_negative"},
    {"agent_seed": 20, "v4_3_class": "mechanism_positive_adaptation_negative"},
    {"agent_seed": 15, "v4_3_class": "adaptation_positive_mechanism_negative"},
]
OBSTACLES = [0.70, 0.75, 0.80, 0.90, 1.00]
COSTS = [0.020, 0.025, 0.030, 0.035, 0.040]


def run_cell(history: dict, obstacle: float, cost: float) -> dict:
    overrides = dict(standard_turnover_overrides())
    overrides["active_obstacle_fraction"] = obstacle
    r = direct_replication_followup(
        WORLD_SEED, history["agent_seed"], steps=650, assay_start=250,
        min_generation=2, overrides=overrides, permutations=99,
        information_level=.35, signal_cost=cost,
    )
    fitness = r.get("fitness") or {}
    return {
        **history,
        "world_seed": WORLD_SEED,
        "active_obstacle_fraction": obstacle,
        "signal_cost": cost,
        "supported_generations": r.get("supported_generations", []),
        "transplant_supported_generations": (r.get("transplant") or {}).get("supported_generations", []),
        "differential_reproduction_supported": (r.get("differential_reproduction") or {}).get("supported"),
        "scrambled_removal_supported": (r.get("scrambled_removal") or {}).get("supported"),
        "scrambled_differential_reproduction_supported": (r.get("scrambled_differential_reproduction") or {}).get("supported"),
        "mechanistic_replication": bool(r.get("mechanistic_replication", False)),
        "adaptive_supported": bool(fitness.get("adaptive_supported", False)),
        "adaptive_replication": bool(r.get("adaptive_replication", False)),
        "claim_level": r.get("claim_level"),
        "fitness": fitness,
    }


def main() -> None:
    runs = [run_cell(h, o, c) for h in HISTORIES for o in OBSTACLES for c in COSTS]
    mech = [r for r in runs if r["mechanistic_replication"]]
    adapt = [r for r in runs if r["adaptive_supported"]]
    full = [r for r in runs if r["adaptive_replication"]]
    both_raw = [r for r in runs if r["mechanistic_replication"] and r["adaptive_supported"]]
    out = {
        "preregistered": True,
        "world_seed": WORLD_SEED,
        "histories": HISTORIES,
        "obstacle_grid": OBSTACLES,
        "signal_cost_grid": COSTS,
        "cell_count": len(runs),
        "runs": runs,
        "mechanistic_positive_cells": len(mech),
        "adaptive_positive_cells": len(adapt),
        "raw_overlap_cells": len(both_raw),
        "full_adaptive_replications": len(full),
        "primary_target_met": bool(full),
        "full_positive_cells": [
            {k: r[k] for k in ("agent_seed", "active_obstacle_fraction", "signal_cost", "v4_3_class", "claim_level")}
            for r in full
        ],
    }
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
