"""v4.3: full-mechanism follow-up of every prospective v4.2 direct-causal origin."""
from __future__ import annotations

import json
from pathlib import Path

from latent_worlds.replication import direct_replication_followup, standard_turnover_overrides

V42 = Path("docs/EXPERIMENT_v4.2_RESULTS.json")


def candidates(data: dict) -> list[dict]:
    out = []
    for condition in data["conditions"]:
        for run in condition["runs"]:
            seed = int(run["agent_seed"])
            if seed < 5 or seed > 24 or not bool(run["supported"]):
                continue
            out.append({
                "world_seed": int(data["world_seed"]),
                "agent_seed": seed,
                "active_obstacle_fraction": float(condition["active_obstacle_fraction"]),
                "signal_cost": float(condition["signal_cost"]),
                "v4_2_role": condition["role"],
                "v4_2_supported_generations": list(run.get("supported_generations", [])),
            })
    return sorted(out, key=lambda q: (q["active_obstacle_fraction"], q["signal_cost"], q["agent_seed"]))


def assay(q: dict) -> dict:
    overrides = dict(standard_turnover_overrides())
    overrides["active_obstacle_fraction"] = q["active_obstacle_fraction"]
    r = direct_replication_followup(
        q["world_seed"], q["agent_seed"],
        steps=650, assay_start=250, min_generation=2,
        overrides=overrides, permutations=99,
        information_level=.35, signal_cost=q["signal_cost"],
    )
    return {
        **q,
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
    data = json.loads(V42.read_text())
    chosen = candidates(data)
    runs = [assay(q) for q in chosen]
    adaptive = [r for r in runs if r["adaptive_replication"]]
    mechanistic = [r for r in runs if r["mechanistic_replication"]]
    print(json.dumps({
        "preregistered": True,
        "candidate_count": len(chosen),
        "candidate_rule": "all v4.2 A5-A24 histories with prospective direct-removal support",
        "runs": runs,
        "mechanistic_replications": len(mechanistic),
        "full_adaptive_replications": len(adaptive),
        "first_strong_target_met": bool(adaptive),
        "independent_full_positive_histories": [
            {k: r[k] for k in ("world_seed", "agent_seed", "active_obstacle_fraction", "signal_cost", "v4_2_role")}
            for r in adaptive
        ],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
