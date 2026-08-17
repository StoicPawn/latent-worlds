from __future__ import annotations

import argparse
import json

from .metrics import snapshot
from .world import World


def main():
    parser = argparse.ArgumentParser(description="Run a Latent Worlds simulation.")
    parser.add_argument("--steps", type=int, default=500)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--reveal-laws", action="store_true", help="Debug only: print hidden ground truth.")
    args = parser.parse_args()

    world = World(seed=args.seed).run(args.steps)
    result = snapshot(world)
    if args.reveal_laws:
        result["hidden_laws"] = {
            "temperature_optimum": world.yield_law.optimum,
            "temperature_width": world.yield_law.width,
            "climate_mean": world.climate.mean,
            "climate_amplitude": world.climate.amplitude,
            "climate_period": world.climate.period,
            "spatial_gradient_x": world.climate.spatial_gradient_x,
        }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
