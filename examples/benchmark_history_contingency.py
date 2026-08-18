"""v4.2 preregistered expansion across new population histories A5-A24."""
from __future__ import annotations
import json
from latent_worlds.causal_transmission import direct_reception_transmission_assay
from latent_worlds.replication import standard_turnover_overrides

WORLD_SEED = 11
AGENT_SEEDS = tuple(range(5, 25))
CONDITIONS = (
    (0.50, 0.03, "A2_discovery_condition"),
    (1.00, 0.03, "canonical_A0_positive"),
    (0.75, 0.03, "negative_boundary_control_1"),
    (1.00, 0.04, "negative_boundary_control_2"),
)


def assay(frac: float, cost: float, seed: int) -> dict:
    overrides = dict(standard_turnover_overrides())
    overrides["active_obstacle_fraction"] = frac
    r = direct_reception_transmission_assay(
        world_seed=WORLD_SEED, agent_seed=seed, steps=650, assay_start=250,
        min_generation=2, information_level=.35, signal_cost=cost,
        config_overrides=overrides, max_events=300, permutations=99,
    )
    return {"agent_seed": seed, "supported": bool(r.get("supported", False)),
            "supported_generations": list(r.get("supported_generations", []))}


def main() -> None:
    rows = []
    for frac, cost, role in CONDITIONS:
        runs = [assay(frac, cost, seed) for seed in AGENT_SEEDS]
        hits = sum(int(r["supported"]) for r in runs)
        rows.append({"active_obstacle_fraction": frac, "signal_cost": cost,
                     "role": role, "new_population_seeds": list(AGENT_SEEDS),
                     "hits": hits, "origin_rate": hits / len(runs),
                     "history_reproducible": hits >= 3,
                     "positive_seeds": [r["agent_seed"] for r in runs if r["supported"]],
                     "runs": runs})
    discovery = rows[0]
    controls = rows[2:]
    print(json.dumps({"world_seed": WORLD_SEED, "preregistered": True,
                      "history_reproducible_threshold": 3,
                      "conditions": rows,
                      "primary_target_met": bool(discovery["history_reproducible"]),
                      "discovery_origin_rate": discovery["origin_rate"],
                      "negative_control_origin_rates": [r["origin_rate"] for r in controls]},
                     indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
