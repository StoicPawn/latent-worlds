"""Exploratory ecological opportunity screen across independent world laws.

Not an agent-cognition experiment. The observer-only ideal foresight chooser
knows future physical conditions; no agent receives this privileged knowledge.
Pilot world seeds must NOT be reused as confirmatory held-out worlds.
"""
from __future__ import annotations

import json
from pathlib import Path
from time import perf_counter

from latent_worlds.forecast_value import value_of_foresight
from latent_worlds.replication import standard_turnover_overrides

WORLDS = (11, 21, 31)
WAVES = (0.0, 1.5)
TIMES = tuple(range(0, 1201, 120))
GRID = 4
SPEED = 1.0


def main() -> None:
    folder = Path("experiments/civitas_zero/data/foresight_pilot")
    folder.mkdir(parents=True, exist_ok=True)
    overrides = dict(standard_turnover_overrides())
    overrides["active_obstacle_fraction"] = 0.75
    t0 = perf_counter()
    entries = []
    for world in WORLDS:
        for wave in WAVES:
            outcome = value_of_foresight(
                world, wave_strength=wave, speed=SPEED,
                times=TIMES, grid_x=GRID, grid_y=GRID,
                config_overrides=overrides,
            )
            entries.append(outcome)
            print(json.dumps({
                "world": world, "wave": wave,
                "mean_advantage": outcome["mean_foresight_advantage"],
                "relative_advantage": outcome["relative_mean_advantage"],
                "samples": outcome["samples"],
            }), flush=True)
    result = {
        "status": "EXPLORATORY_ONLY",
        "worlds": WORLDS,
        "waves": WAVES,
        "times": TIMES,
        "grid": GRID,
        "speed": SPEED,
        "rows": entries,
        "elapsed_seconds": round(perf_counter() - t0, 2),
        "claim_boundary": (
            "Observer-side perfect ecological foresight opportunity only; "
            "NOT evidence that any agent can learn, use, or represent it. "
            "No world-level significance can be inferred from three pilot worlds."
        ),
    }
    (folder / "results.json").write_text(json.dumps(result, indent=2) + "\n")
    print("Saved:", folder / "results.json")


if __name__ == "__main__":
    main()
