"""Paired observer-side benchmark for unshaped communication and public memory.

The full and censored worlds share the same seed and physics. In the censored world,
communication/marks still cost energy if attempted but cannot be perceived. Nothing in
this benchmark changes agent reward or selection.
"""
from __future__ import annotations

import argparse
import json
import numpy as np

from latent_worlds.config import SimulationConfig
from latent_worlds.metrics import snapshot
from latent_worlds.world import World


def one(seed: int, steps: int, enabled: bool):
    cfg = SimulationConfig(communication_enabled=enabled, marks_enabled=enabled)
    world = World(cfg, seed=seed).run(steps)
    r = snapshot(world)
    c = r["communication"]
    return {
        "population": r["population"],
        "births": r["births"],
        "max_generation": r["max_generation"],
        "recurrent_alive": c["recurrent_alive"],
        "events": c["events"],
        "signal_r2": c["broadcast_environment_r2"],
        "mark_r2": c["mark_environment_r2"],
        "social_sensitivity": c["mean_social_input_sensitivity"],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--worlds", type=int, default=20)
    ap.add_argument("--steps", type=int, default=700)
    args = ap.parse_args()
    rows = []
    for seed in range(args.worlds):
        full = one(seed, args.steps, True)
        censored = one(seed, args.steps, False)
        rows.append({"seed": seed, "full": full, "censored": censored})

    def mean(key, side):
        vals = [r[side][key] for r in rows if r[side][key] is not None]
        return float(np.mean(vals)) if vals else None

    summary = {
        "worlds": args.worlds,
        "steps": args.steps,
        "full": {k: mean(k, "full") for k in ["population", "births", "max_generation", "recurrent_alive", "events", "signal_r2", "mark_r2", "social_sensitivity"]},
        "censored": {k: mean(k, "censored") for k in ["population", "births", "max_generation", "recurrent_alive", "events", "signal_r2", "mark_r2", "social_sensitivity"]},
    }
    summary["paired_population_delta"] = float(np.mean([r["full"]["population"] - r["censored"]["population"] for r in rows]))
    summary["paired_recurrent_alive_delta"] = float(np.mean([r["full"]["recurrent_alive"] - r["censored"]["recurrent_alive"] for r in rows]))
    print(json.dumps({"summary": summary, "runs": rows}, indent=2))


if __name__ == "__main__":
    main()
