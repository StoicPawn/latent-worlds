"""v5.0: observer-side ecological value-of-foresight audit."""
from __future__ import annotations

import json

from latent_worlds.forecast_value import forecast_value_grid
from latent_worlds.replication import standard_turnover_overrides


WORLD_SEED = 11
WAVE_STRENGTHS = (0.0, 0.75, 1.5, 2.5, 4.0)
SPEEDS = (0.6, 1.0, 1.4)


def main() -> None:
    overrides = dict(standard_turnover_overrides())
    overrides["active_obstacle_fraction"] = 0.75
    result = forecast_value_grid(
        WORLD_SEED,
        WAVE_STRENGTHS,
        SPEEDS,
        times=tuple(range(0, 1201, 20)),
        config_overrides=overrides,
    )
    result["experiment"] = "v5.0"
    result["analysis_type"] = "exploratory ecological affordance audit"
    result["wave_strengths"] = list(WAVE_STRENGTHS)
    result["speeds"] = list(SPEEDS)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
