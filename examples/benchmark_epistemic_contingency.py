"""v4.5: prospective same-physics epistemic-contingency diagnostic.

This is deliberately a pre-Q2 instrument validation, not a claim that spontaneous
science has already emerged.  It uses previously untested population seeds A25-A34
under one fixed W11 physics realization and quantifies predictive representation,
representation geometry, and functional material-configuration similarity.
"""
from __future__ import annotations

import json

from latent_worlds.epistemic_convergence import same_physics_campaign
from latent_worlds.replication import standard_turnover_overrides


WORLD_SEED = 11
AGENT_SEEDS = tuple(range(25, 35))
STEPS = 1200
BURN_IN = 200
STRIDE = 5
HORIZONS = (10, 35, 70)


def main() -> None:
    overrides = dict(standard_turnover_overrides())
    # v4.4 found mechanistic candidates around this W11 ecological neighbourhood.
    # This remains a diagnostic context; no v4.5 result can promote a Stage-II claim.
    overrides["active_obstacle_fraction"] = 0.75

    result = same_physics_campaign(
        WORLD_SEED,
        AGENT_SEEDS,
        steps=STEPS,
        burn_in=BURN_IN,
        stride=STRIDE,
        horizons=HORIZONS,
        information_level=0.35,
        signal_cost=0.03,
        config_overrides=overrides,
        q2_eligible_agent_seeds=(),
    )
    result["experiment"] = "v4.5"
    result["preregistered"] = True
    result["interpretation_scope"] = "pre-Q2 diagnostic only"
    result["population_seed_status"] = "A25-A34 not used in v4.0-v4.4 discovery/confirmation"
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
