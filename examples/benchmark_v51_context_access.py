"""v5.1: generic recurrent context-access ablation under forecast pressure."""
from __future__ import annotations

import json
import math

from latent_worlds.epistemic_carriers import run_individual_carrier_audit
from latent_worlds.replication import standard_turnover_overrides


WORLD_SEED = 11
AGENT_SEEDS = tuple(range(73, 81))
WAVE_STRENGTH = 1.5


def _sign_test_one_sided(values):
    nonzero = [float(v) for v in values if abs(float(v)) > 1e-12]
    wins = sum(v > 0 for v in nonzero)
    n = len(nonzero)
    if n == 0:
        return {"wins": 0, "non_ties": 0, "p_upper": 1.0}
    p = sum(math.comb(n, k) for k in range(wins, n + 1)) / (2 ** n)
    return {"wins": int(wins), "non_ties": int(n), "p_upper": float(p)}


def _compact(result):
    eligible = int(result["eligible_carriers"])
    candidates = int(result["carrier_candidates"])
    return {
        "eligible_carriers": eligible,
        "carrier_candidates": candidates,
        "candidate_fraction": float(candidates / eligible) if eligible else 0.0,
        "max_predictive_gain": result["max_predictive_gain"],
        "median_predictive_gain": result["median_predictive_gain"],
        "final_population": result["final_population"],
        "births": result["births"],
        "deaths": result["deaths"],
        "max_generation": result["max_generation"],
        "total_harvest": result["total_harvest"],
    }


def _run(seed: int, *, context: bool, full: bool):
    overrides = dict(standard_turnover_overrides())
    overrides.update({
        "active_obstacle_fraction": 0.75,
        "resource_wave_strength": WAVE_STRENGTH,
        "recurrent_context_features_enabled": bool(context),
        "recurrent_learning_enabled": bool(full),
        "recurrent_weight_inheritance_enabled": bool(full),
    })
    return _compact(run_individual_carrier_audit(
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
    ))


def main() -> None:
    rows = []
    for seed in AGENT_SEEDS:
        legacy_full = _run(seed, context=False, full=True)
        legacy_frozen = _run(seed, context=False, full=False)
        context_full = _run(seed, context=True, full=True)
        context_frozen = _run(seed, context=True, full=False)

        legacy_excess = (
            legacy_full["candidate_fraction"] - legacy_frozen["candidate_fraction"]
        )
        context_excess = (
            context_full["candidate_fraction"] - context_frozen["candidate_fraction"]
        )
        interaction = float(context_excess - legacy_excess)

        harvest_legacy = (
            legacy_full["total_harvest"] - legacy_frozen["total_harvest"]
        )
        harvest_context = (
            context_full["total_harvest"] - context_frozen["total_harvest"]
        )

        rows.append({
            "agent_seed": int(seed),
            "legacy_full": legacy_full,
            "legacy_frozen": legacy_frozen,
            "context_full": context_full,
            "context_frozen": context_frozen,
            "selection_excess_legacy": float(legacy_excess),
            "selection_excess_context": float(context_excess),
            "carrier_fraction_interaction": interaction,
            "harvest_excess_legacy": float(harvest_legacy),
            "harvest_excess_context": float(harvest_context),
            "harvest_interaction": float(harvest_context - harvest_legacy),
        })

    interactions = [r["carrier_fraction_interaction"] for r in rows]
    sign = _sign_test_one_sided(interactions)
    mean_interaction = float(sum(interactions) / len(interactions))
    support = bool(mean_interaction > 0.0 and sign["p_upper"] <= 0.05)

    harvest_interactions = [r["harvest_interaction"] for r in rows]
    out = {
        "experiment": "v5.1",
        "preregistered": True,
        "world_seed": WORLD_SEED,
        "agent_seeds": list(AGENT_SEEDS),
        "population_seed_status": "A73-A80 unseen before v5.1",
        "resource_wave_strength": WAVE_STRENGTH,
        "context_features": [
            "normalized absolute x",
            "normalized absolute y",
            "previous harvest/probe yield",
        ],
        "rows": rows,
        "summary": {
            "mean_carrier_fraction_interaction": mean_interaction,
            "carrier_fraction_interaction_sign_test": sign,
            "generic_context_enrichment_supported": support,
            "mean_harvest_interaction": float(
                sum(harvest_interactions) / len(harvest_interactions)
            ),
            "mean_candidate_fraction_legacy_full": float(
                sum(r["legacy_full"]["candidate_fraction"] for r in rows) / len(rows)
            ),
            "mean_candidate_fraction_legacy_frozen": float(
                sum(r["legacy_frozen"]["candidate_fraction"] for r in rows) / len(rows)
            ),
            "mean_candidate_fraction_context_full": float(
                sum(r["context_full"]["candidate_fraction"] for r in rows) / len(rows)
            ),
            "mean_candidate_fraction_context_frozen": float(
                sum(r["context_frozen"]["candidate_fraction"] for r in rows) / len(rows)
            ),
        },
        "decision_rule": (
            "Generic context enrichment is supported only if its full-minus-frozen "
            "carrier-fraction excess exceeds the legacy full-minus-frozen excess "
            "on average and the one-sided paired sign-test is <= 0.05."
        ),
        "claim_boundary": (
            "A positive result would identify generic spatial/outcome observability "
            "as a causal bottleneck for selected predictive representation. It "
            "would not establish cumulative knowledge or spontaneous science."
        ),
    }
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
