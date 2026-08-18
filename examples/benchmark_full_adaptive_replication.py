"""v4.1: search preregistered robust cells for a second full adaptive replication."""
from __future__ import annotations

import json
from pathlib import Path

from latent_worlds.replication import direct_replication_followup, standard_turnover_overrides

V40 = Path("docs/EXPERIMENT_v4.0_RESULTS.json")
OUT = Path("docs/EXPERIMENT_v4.1_RESULTS.json")


def select_candidates(data: dict) -> list[tuple[float, float, int]]:
    cells = []
    for cell in data.get("cells", []):
        reps = int(cell.get("population_replicates", 0) or 0)
        if reps < 2:
            continue
        frac = float(cell["active_obstacle_fraction"])
        cost = float(cell["signal_cost"])
        cells.append((reps, cost, -frac, cell))
    cells.sort(key=lambda x: (-x[0], x[1], x[2]))
    selected = []
    for _, _, _, cell in cells[:3]:
        for seed in cell.get("supported_population_seeds", []):
            seed = int(seed)
            if seed == 0:
                continue
            selected.append((float(cell["active_obstacle_fraction"]), float(cell["signal_cost"]), seed))
    return selected


def run_one(frac: float, cost: float, agent_seed: int) -> dict:
    overrides = dict(standard_turnover_overrides())
    overrides["active_obstacle_fraction"] = frac
    r = direct_replication_followup(
        11,
        agent_seed,
        steps=650,
        assay_start=250,
        min_generation=2,
        overrides=overrides,
        permutations=99,
        information_level=.35,
        signal_cost=cost,
    )
    return {
        "world_seed": 11,
        "agent_seed": agent_seed,
        "active_obstacle_fraction": frac,
        "signal_cost": cost,
        "supported_generations": r.get("supported_generations", []),
        "mechanistic_replication": bool(r.get("mechanistic_replication", False)),
        "adaptive_replication": bool(r.get("adaptive_replication", False)),
        "claim_level": r.get("claim_level"),
        "fitness": r.get("fitness"),
        "transplant_supported_generations": r.get("transplant", {}).get("supported_generations", []),
        "differential_reproduction_supported": r.get("differential_reproduction", {}).get("supported"),
        "scrambled_removal_supported": r.get("scrambled_removal", {}).get("supported"),
        "scrambled_differential_reproduction_supported": r.get("scrambled_differential_reproduction", {}).get("supported"),
    }


def main() -> None:
    data = json.loads(V40.read_text())
    candidates = select_candidates(data)
    runs = [run_one(frac, cost, seed) for frac, cost, seed in candidates]
    positives = [r for r in runs if r["adaptive_replication"]]
    result = {
        "selection_rule_preregistered": True,
        "candidate_count": len(candidates),
        "candidates": [
            {"active_obstacle_fraction": f, "signal_cost": c, "agent_seed": s}
            for f, c, s in candidates
        ],
        "runs": runs,
        "full_adaptive_replications": len(positives),
        "independent_positive_histories": [
            {"world_seed": r["world_seed"], "agent_seed": r["agent_seed"],
             "active_obstacle_fraction": r["active_obstacle_fraction"], "signal_cost": r["signal_cost"]}
            for r in positives
        ],
        "first_strong_target_met": bool(positives),
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
