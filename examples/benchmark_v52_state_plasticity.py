"""v5.2: prospective recurrent-state plasticity test under forecast pressure."""
from __future__ import annotations

import json
import math

from latent_worlds.epistemic_carriers import run_individual_carrier_audit
from latent_worlds.replication import standard_turnover_overrides


WORLD_SEED = 11
AGENT_SEEDS = tuple(range(81, 89))
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


def _run(seed: int, *, learning: bool, inheritance: bool, state_plasticity: bool):
    overrides = dict(standard_turnover_overrides())
    overrides.update({
        "active_obstacle_fraction": 0.75,
        "resource_wave_strength": WAVE_STRENGTH,
        "recurrent_context_features_enabled": True,
        "recurrent_learning_enabled": bool(learning),
        "recurrent_weight_inheritance_enabled": bool(inheritance),
        "recurrent_state_plasticity_enabled": bool(state_plasticity),
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
        frozen = _run(
            seed, learning=False, inheritance=False, state_plasticity=False
        )
        output_only = _run(
            seed, learning=True, inheritance=True, state_plasticity=False
        )
        state_plastic = _run(
            seed, learning=True, inheritance=True, state_plasticity=True
        )

        state_minus_output = float(
            state_plastic["candidate_fraction"] - output_only["candidate_fraction"]
        )
        state_minus_frozen = float(
            state_plastic["candidate_fraction"] - frozen["candidate_fraction"]
        )
        output_minus_frozen = float(
            output_only["candidate_fraction"] - frozen["candidate_fraction"]
        )

        rows.append({
            "agent_seed": int(seed),
            "frozen": frozen,
            "output_only": output_only,
            "state_plastic": state_plastic,
            "state_minus_output_carrier_fraction": state_minus_output,
            "state_minus_frozen_carrier_fraction": state_minus_frozen,
            "output_minus_frozen_carrier_fraction": output_minus_frozen,
            "state_minus_output_harvest": float(
                state_plastic["total_harvest"] - output_only["total_harvest"]
            ),
            "state_minus_frozen_harvest": float(
                state_plastic["total_harvest"] - frozen["total_harvest"]
            ),
        })

    d_output = [r["state_minus_output_carrier_fraction"] for r in rows]
    d_frozen = [r["state_minus_frozen_carrier_fraction"] for r in rows]
    sign_output = _sign_test_one_sided(d_output)
    sign_frozen = _sign_test_one_sided(d_frozen)
    mean_output = float(sum(d_output) / len(d_output))
    mean_frozen = float(sum(d_frozen) / len(d_frozen))

    support = bool(
        mean_output > 0.0
        and mean_frozen > 0.0
        and sign_output["p_upper"] <= 0.05
        and sign_frozen["p_upper"] <= 0.05
    )

    out = {
        "experiment": "v5.2",
        "preregistered": True,
        "world_seed": WORLD_SEED,
        "agent_seeds": list(AGENT_SEEDS),
        "population_seed_status": "A81-A88 unseen before v5.2",
        "resource_wave_strength": WAVE_STRENGTH,
        "context_features_enabled": True,
        "state_plasticity": (
            "reward-modulated eligibility through recurrent hidden state; "
            "no prediction target or hidden-law supervision"
        ),
        "rows": rows,
        "summary": {
            "mean_state_minus_output_carrier_fraction": mean_output,
            "state_minus_output_sign_test": sign_output,
            "mean_state_minus_frozen_carrier_fraction": mean_frozen,
            "state_minus_frozen_sign_test": sign_frozen,
            "selected_state_plasticity_supported": support,
            "mean_state_minus_output_harvest": float(
                sum(r["state_minus_output_harvest"] for r in rows) / len(rows)
            ),
            "mean_state_minus_frozen_harvest": float(
                sum(r["state_minus_frozen_harvest"] for r in rows) / len(rows)
            ),
            "mean_candidate_fraction_frozen": float(
                sum(r["frozen"]["candidate_fraction"] for r in rows) / len(rows)
            ),
            "mean_candidate_fraction_output_only": float(
                sum(r["output_only"]["candidate_fraction"] for r in rows) / len(rows)
            ),
            "mean_candidate_fraction_state_plastic": float(
                sum(r["state_plastic"]["candidate_fraction"] for r in rows) / len(rows)
            ),
        },
        "decision_rule": (
            "State-plasticity support requires positive mean carrier-fraction "
            "advantages over both output-only learning and the frozen reservoir, "
            "with one-sided paired sign-test p <= 0.05 for both comparisons."
        ),
        "claim_boundary": (
            "A positive v5.2 result would establish a generic mechanism capable "
            "of selecting observer-decodable predictive internal state under "
            "ordinary reward. It would support E1 only after independent "
            "prospective replication, and would not imply cumulative knowledge "
            "or spontaneous science."
        ),
    }
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
