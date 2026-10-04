"""v4.6: decoder-capacity control on new same-physics histories A35-A44."""
from __future__ import annotations

import json

from latent_worlds.epistemic_decoder_controls import (
    capacity_controlled_same_physics_campaign,
)
from latent_worlds.replication import standard_turnover_overrides


WORLD_SEED = 11
AGENT_SEEDS = tuple(range(35, 45))


def main() -> None:
    overrides = dict(standard_turnover_overrides())
    overrides["active_obstacle_fraction"] = 0.75
    result = capacity_controlled_same_physics_campaign(
        WORLD_SEED,
        AGENT_SEEDS,
        steps=1200,
        burn_in=200,
        stride=5,
        horizons=(10, 35, 70),
        information_level=0.35,
        signal_cost=0.03,
        config_overrides=overrides,
    )
    result["experiment"] = "v4.6"
    result["preregistered"] = True
    result["population_seed_status"] = "A35-A44 unseen before v4.6"
    result["interpretation_scope"] = "capacity-control E1-like diagnostic only"
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
