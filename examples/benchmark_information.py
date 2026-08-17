from __future__ import annotations

import argparse
import numpy as np

from latent_worlds.config import SimulationConfig
from latent_worlds.metrics import snapshot
from latent_worlds.world import World


def run_pair(seed: int, steps: int):
    common = dict(occlusion_enabled=True, pulse_spawn_rate=0.02)
    on = World(SimulationConfig(communication_enabled=True, marks_enabled=True, **common), seed=seed).run(steps)
    off = World(SimulationConfig(communication_enabled=False, marks_enabled=False, **common), seed=seed).run(steps)
    a, b = snapshot(on), snapshot(off)
    return {
        "seed": seed,
        "private_information_index": a["information_structure"]["private_information_index"],
        "delta_population": a["population"] - b["population"],
        "delta_harvest": a["total_harvest"] - b["total_harvest"],
        "signal_generational_span": a["communication"]["signal_generational_span"],
        "receiver_action_r2": a["communication"]["receiver_action_r2_from_payload"],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--worlds", type=int, default=12)
    ap.add_argument("--steps", type=int, default=700)
    args = ap.parse_args()
    rows = [run_pair(s, args.steps) for s in range(args.worlds)]
    vals = lambda k: [r[k] for r in rows if r[k] is not None]
    print(f"worlds={args.worlds} steps={args.steps}")
    print(f"private_information_index_mean={np.mean(vals('private_information_index')):.4f}")
    print(f"delta_population_mean={np.mean(vals('delta_population')):.4f}")
    print(f"delta_harvest_mean={np.mean(vals('delta_harvest')):.4f}")
    print(f"signal_generational_span_mean={np.mean(vals('signal_generational_span')):.4f}")
    if vals('receiver_action_r2'):
        print(f"receiver_action_r2_mean={np.mean(vals('receiver_action_r2')):.4f}")


if __name__ == "__main__":
    main()
