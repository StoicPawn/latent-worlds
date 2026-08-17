from __future__ import annotations

import argparse
import copy
import statistics

from latent_worlds.config import SimulationConfig
from latent_worlds.metrics import snapshot
from latent_worlds.world import World


def run_pair(seed: int, steps: int):
    active_cfg = SimulationConfig(object_manipulation_enabled=True)
    frozen_cfg = copy.deepcopy(active_cfg)
    frozen_cfg.object_manipulation_enabled = False

    active = World(config=active_cfg, seed=seed).run(steps)
    frozen = World(config=frozen_cfg, seed=seed).run(steps)
    return snapshot(active), snapshot(frozen)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--worlds", type=int, default=12)
    ap.add_argument("--steps", type=int, default=700)
    args = ap.parse_args()

    rows = []
    for seed in range(args.worlds):
        a, f = run_pair(seed, args.steps)
        rows.append({
            "seed": seed,
            "population_delta": a["population"] - f["population"],
            "birth_delta": a["births"] - f["births"],
            "harvest_delta": a["total_harvest"] - f["total_harvest"],
            "pickups": a["technology"]["successful_pickups"],
            "drops": a["technology"]["successful_drops"],
            "object_displacement": a["technology"]["mean_object_displacement"],
            "boosted_fraction": a["technology"]["boosted_harvest_fraction"],
        })

    print("paired manipulation vs frozen-object control")
    for r in rows:
        print(r)
    print("summary")
    for key in ["population_delta", "birth_delta", "harvest_delta", "pickups", "drops", "object_displacement", "boosted_fraction"]:
        print(key, statistics.mean(r[key] for r in rows))


if __name__ == "__main__":
    main()
