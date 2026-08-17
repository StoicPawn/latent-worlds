"""Observer-side benchmark for spontaneous selection of generic cognition.

No agent is rewarded for prediction, discovery, novelty or explanatory accuracy.
The benchmark merely records what evolution leaves behind.
"""
from __future__ import annotations

import argparse
import json
import numpy as np

from latent_worlds.metrics import snapshot
from latent_worlds.world import World


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--worlds", type=int, default=20)
    ap.add_argument("--steps", type=int, default=800)
    args = ap.parse_args()

    rows = []
    for seed in range(args.worlds):
        w = World(seed=seed)
        initial_model = [a for a in w.agents if a.kind in {"model_based", "planner"}]
        initial_memory = float(np.mean([a.genome.memory for a in initial_model]))
        initial_abstraction = float(np.mean([a.genome.abstraction for a in initial_model]))
        w.run(args.steps)
        s = snapshot(w)
        c = s["cognition"]
        rows.append({
            "seed": seed,
            "hidden_sources": w.hidden_source_count,
            "population": s["population"],
            "max_generation": s["max_generation"],
            "cognitive_living": c["living_cognitive"],
            "initial_memory": initial_memory,
            "living_memory": c.get("living_mean_memory_gene"),
            "initial_abstraction": initial_abstraction,
            "living_abstraction": c.get("living_mean_abstraction_gene"),
        })

    valid_mem = [r["living_memory"] - r["initial_memory"] for r in rows if r["living_memory"] is not None]
    valid_abs = [r["living_abstraction"] - r["initial_abstraction"] for r in rows if r["living_abstraction"] is not None]
    summary = {
        "worlds": len(rows),
        "extinctions": sum(r["population"] == 0 for r in rows),
        "mean_final_population": float(np.mean([r["population"] for r in rows])),
        "mean_max_generation": float(np.mean([r["max_generation"] for r in rows])),
        "mean_memory_selection_delta": float(np.mean(valid_mem)) if valid_mem else None,
        "mean_abstraction_selection_delta": float(np.mean(valid_abs)) if valid_abs else None,
        "rows": rows,
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
