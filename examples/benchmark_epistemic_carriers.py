"""v4.7: prospective individual predictive-carrier audit on A45-A54."""
from __future__ import annotations

import json

from latent_worlds.epistemic_carriers import run_individual_carrier_audit
from latent_worlds.replication import standard_turnover_overrides


WORLD_SEED = 11
AGENT_SEEDS = tuple(range(45, 55))


def main() -> None:
    overrides = dict(standard_turnover_overrides())
    overrides["active_obstacle_fraction"] = 0.75
    histories = [
        run_individual_carrier_audit(
            WORLD_SEED,
            seed,
            steps=1200,
            burn_in=200,
            stride=2,
            horizons=(10, 35, 70),
            min_samples=80,
            information_level=0.35,
            signal_cost=0.03,
            config_overrides=overrides,
        )
        for seed in AGENT_SEEDS
    ]
    candidates = [h for h in histories if h["carrier_candidates"] > 0]
    out = {
        "experiment": "v4.7",
        "preregistered": True,
        "world_seed": WORLD_SEED,
        "agent_seeds": list(AGENT_SEEDS),
        "population_seed_status": "A45-A54 unseen before v4.7",
        "histories": histories,
        "summary": {
            "histories": len(histories),
            "histories_with_carrier_candidates": len(candidates),
            "candidate_history_seeds": [h["agent_seed"] for h in candidates],
            "eligible_carriers_total": sum(h["eligible_carriers"] for h in histories),
            "carrier_candidates_total": sum(h["carrier_candidates"] for h in histories),
            "max_gain_across_histories": max(
                (h["max_predictive_gain"] for h in histories if h["max_predictive_gain"] is not None),
                default=None,
            ),
        },
        "interpretation_scope": "individual E1-like carrier diagnostic only",
    }
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
