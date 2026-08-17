"""Run a small reproducible discovery benchmark across held-out world seeds."""
from __future__ import annotations

import argparse
import json
from statistics import mean

from latent_worlds.metrics import snapshot
from latent_worlds.world import World


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--worlds", type=int, default=20)
    parser.add_argument("--steps", type=int, default=500)
    parser.add_argument("--seed-start", type=int, default=0)
    args = parser.parse_args()

    rows = []
    for seed in range(args.seed_start, args.seed_start + args.worlds):
        world = World(seed=seed).run(args.steps)
        report = snapshot(world)
        rows.append({
            "seed": seed,
            "population": report["population"],
            "births": report["births"],
            "living_types": report["agent_types"],
            **report["science"],
        })

    rmses = [r["best_law_rmse"] for r in rows if r["best_law_rmse"] is not None]
    spans = [r["mean_temperature_span"] for r in rows]
    radiation_spans = [r["mean_radiation_span"] for r in rows]
    interaction_fractions = [r["interaction_capable_fraction"] for r in rows]
    scientists_surviving = sum(r["living_types"].get("scientist", 0) for r in rows)
    result = {
        "config": vars(args),
        "summary": {
            "worlds_completed": len(rows),
            "mean_best_law_rmse": mean(rmses) if rmses else None,
            "mean_temperature_span": mean(spans) if spans else 0.0,
            "mean_radiation_span": mean(radiation_spans) if radiation_spans else 0.0,
            "mean_interaction_capable_fraction": mean(interaction_fractions) if interaction_fractions else 0.0,
            "scientists_surviving_across_final_states": scientists_surviving,
        },
        "worlds": rows,
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
