"""v4.9: world-side forecast-pressure x recurrent-learning causal interaction."""
from __future__ import annotations

import json
import math

from latent_worlds.epistemic_carriers import run_individual_carrier_audit
from latent_worlds.replication import standard_turnover_overrides


WORLD_SEED = 11
AGENT_SEEDS = tuple(range(65, 73))
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
        "candidate_generations": result["candidate_generations"],
        "max_predictive_gain": result["max_predictive_gain"],
        "median_predictive_gain": result["median_predictive_gain"],
        "final_population": result["final_population"],
        "births": result["births"],
        "deaths": result["deaths"],
        "max_generation": result["max_generation"],
        "total_harvest": result["total_harvest"],
    }


def _run(seed: int, *, wave: float, full: bool):
    overrides = dict(standard_turnover_overrides())
    overrides.update({
        "active_obstacle_fraction": 0.75,
        "resource_wave_strength": float(wave),
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
        control_full = _run(seed, wave=0.0, full=True)
        control_frozen = _run(seed, wave=0.0, full=False)
        wave_full = _run(seed, wave=WAVE_STRENGTH, full=True)
        wave_frozen = _run(seed, wave=WAVE_STRENGTH, full=False)

        selection_control = (
            control_full["candidate_fraction"] - control_frozen["candidate_fraction"]
        )
        selection_wave = (
            wave_full["candidate_fraction"] - wave_frozen["candidate_fraction"]
        )
        interaction = float(selection_wave - selection_control)

        harvest_control = (
            control_full["total_harvest"] - control_frozen["total_harvest"]
        )
        harvest_wave = wave_full["total_harvest"] - wave_frozen["total_harvest"]

        rows.append({
            "agent_seed": int(seed),
            "control_full": control_full,
            "control_frozen": control_frozen,
            "wave_full": wave_full,
            "wave_frozen": wave_frozen,
            "selection_excess_control": float(selection_control),
            "selection_excess_wave": float(selection_wave),
            "carrier_fraction_interaction": interaction,
            "harvest_excess_control": float(harvest_control),
            "harvest_excess_wave": float(harvest_wave),
            "harvest_interaction": float(harvest_wave - harvest_control),
        })

    interactions = [r["carrier_fraction_interaction"] for r in rows]
    sign = _sign_test_one_sided(interactions)
    mean_interaction = float(sum(interactions) / len(interactions))
    support = bool(mean_interaction > 0.0 and sign["p_upper"] <= 0.05)

    harvest_interactions = [r["harvest_interaction"] for r in rows]

    out = {
        "experiment": "v4.9",
        "preregistered": True,
        "world_seed": WORLD_SEED,
        "agent_seeds": list(AGENT_SEEDS),
        "population_seed_status": "A65-A72 unseen before v4.9",
        "resource_wave_strength": WAVE_STRENGTH,
        "design": "2x2 resource-wave (0 vs 1.5) x recurrent full vs frozen",
        "rows": rows,
        "summary": {
            "mean_carrier_fraction_interaction": mean_interaction,
            "carrier_fraction_interaction_sign_test": sign,
            "forecast_pressure_selected_representation_supported": support,
            "mean_harvest_interaction": float(
                sum(harvest_interactions) / len(harvest_interactions)
            ),
            "mean_candidate_fraction_control_full": float(
                sum(r["control_full"]["candidate_fraction"] for r in rows) / len(rows)
            ),
            "mean_candidate_fraction_control_frozen": float(
                sum(r["control_frozen"]["candidate_fraction"] for r in rows) / len(rows)
            ),
            "mean_candidate_fraction_wave_full": float(
                sum(r["wave_full"]["candidate_fraction"] for r in rows) / len(rows)
            ),
            "mean_candidate_fraction_wave_frozen": float(
                sum(r["wave_frozen"]["candidate_fraction"] for r in rows) / len(rows)
            ),
        },
        "decision_rule": (
            "Forecast-pressure support requires a positive mean difference-in-"
            "differences in carrier fraction and a one-sided paired sign-test "
            "p <= 0.05 across non-tied population histories."
        ),
        "claim_boundary": (
            "A positive result would show that a world-side need for anticipation "
            "selectively enriches observer-decodable predictive internal state "
            "beyond a frozen recurrent reservoir. It would be an E1-selection "
            "result, not cumulative knowledge or spontaneous science."
        ),
    }
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
