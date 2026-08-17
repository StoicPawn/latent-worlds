"""Paired observer-side benchmark for emergent signalling.

No term reported here is used by agents or by selection. A communication claim
requires a difference between matched worlds where signals are readable and
where they are physically censored while emission remains equally costly.
"""
from __future__ import annotations
import argparse
import json
import numpy as np
from latent_worlds.config import SimulationConfig
from latent_worlds.metrics import snapshot
from latent_worlds.world import World


def run(seed: int, steps: int, enabled: bool):
    cfg = SimulationConfig(communication_enabled=enabled)
    w = World(cfg, seed=seed).run(steps)
    return snapshot(w)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--worlds", type=int, default=20)
    ap.add_argument("--steps", type=int, default=900)
    args = ap.parse_args()
    rows = []
    for seed in range(args.worlds):
        on, off = run(seed, args.steps, True), run(seed, args.steps, False)
        rows.append({
            "seed": seed,
            "population_delta": on["population"] - off["population"],
            "harvest_delta": on["total_harvest"] - off["total_harvest"],
            "birth_delta": on["births"] - off["births"],
            "broadcast_r2": on["communication"]["broadcast_environment_r2"],
            "receiver_action_r2": on["communication"]["receiver_action_r2_from_payload"],
            "signal_generational_span": on["communication"]["signal_generational_span"],
            "signal_sensitivity": on["communication"]["mean_signal_input_sensitivity"],
        })
    def mean(key):
        v=[r[key] for r in rows if r[key] is not None]
        return float(np.mean(v)) if v else None
    print(json.dumps({
        "worlds": args.worlds, "steps": args.steps,
        "mean_population_delta_on_minus_censored": mean("population_delta"),
        "mean_harvest_delta_on_minus_censored": mean("harvest_delta"),
        "mean_birth_delta_on_minus_censored": mean("birth_delta"),
        "mean_receiver_action_r2": mean("receiver_action_r2"),
        "mean_signal_sensitivity": mean("signal_sensitivity"),
        "max_signal_generational_span": max((r["signal_generational_span"] for r in rows), default=0),
        "runs": rows,
    }, indent=2))

if __name__ == "__main__":
    main()
