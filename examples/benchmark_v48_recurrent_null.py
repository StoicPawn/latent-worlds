"""v4.8: prospective full-vs-frozen recurrent representation control."""
from __future__ import annotations

import json
import math

from latent_worlds.epistemic_carriers import run_individual_carrier_audit
from latent_worlds.replication import standard_turnover_overrides


WORLD_SEED = 11
AGENT_SEEDS = tuple(range(55, 65))


def _sign_test_one_sided(deltas):
    nonzero = [float(d) for d in deltas if abs(float(d)) > 1e-12]
    wins = sum(d > 0 for d in nonzero)
    n = len(nonzero)
    if n == 0:
        return {"wins": 0, "non_ties": 0, "p_upper": 1.0}
    p = sum(math.comb(n, k) for k in range(wins, n + 1)) / (2 ** n)
    return {"wins": int(wins), "non_ties": int(n), "p_upper": float(p)}


def _fraction(result):
    n = int(result["eligible_carriers"])
    return float(result["carrier_candidates"] / n) if n else 0.0


def main() -> None:
    base = dict(standard_turnover_overrides())
    base["active_obstacle_fraction"] = 0.75

    rows = []
    for seed in AGENT_SEEDS:
        full_overrides = {
            **base,
            "recurrent_learning_enabled": True,
            "recurrent_weight_inheritance_enabled": True,
        }
        frozen_overrides = {
            **base,
            "recurrent_learning_enabled": False,
            "recurrent_weight_inheritance_enabled": False,
        }
        full = run_individual_carrier_audit(
            WORLD_SEED, seed, steps=1200, burn_in=200, stride=2,
            horizons=(10, 35, 70), min_samples=80,
            information_level=0.35, signal_cost=0.03,
            config_overrides=full_overrides,
        )
        frozen = run_individual_carrier_audit(
            WORLD_SEED, seed, steps=1200, burn_in=200, stride=2,
            horizons=(10, 35, 70), min_samples=80,
            information_level=0.35, signal_cost=0.03,
            config_overrides=frozen_overrides,
        )
        full_fraction = _fraction(full)
        frozen_fraction = _fraction(frozen)
        rows.append({
            "agent_seed": int(seed),
            "full": full,
            "frozen": frozen,
            "candidate_fraction_full": full_fraction,
            "candidate_fraction_frozen": frozen_fraction,
            "candidate_fraction_delta": float(full_fraction - frozen_fraction),
            "max_gain_full": full["max_predictive_gain"],
            "max_gain_frozen": frozen["max_predictive_gain"],
            "max_gain_delta": (
                None
                if full["max_predictive_gain"] is None or frozen["max_predictive_gain"] is None
                else float(full["max_predictive_gain"] - frozen["max_predictive_gain"])
            ),
        })

    fraction_deltas = [r["candidate_fraction_delta"] for r in rows]
    sign = _sign_test_one_sided(fraction_deltas)
    gain_deltas = [
        r["max_gain_delta"] for r in rows if r["max_gain_delta"] is not None
    ]
    mean_fraction_delta = float(sum(fraction_deltas) / len(fraction_deltas))
    support = bool(mean_fraction_delta > 0.0 and sign["p_upper"] <= 0.05)

    out = {
        "experiment": "v4.8",
        "preregistered": True,
        "world_seed": WORLD_SEED,
        "agent_seeds": list(AGENT_SEEDS),
        "population_seed_status": "A55-A64 unseen before v4.8",
        "conditions": {
            "full": {
                "recurrent_learning_enabled": True,
                "recurrent_weight_inheritance_enabled": True,
            },
            "frozen": {
                "recurrent_learning_enabled": False,
                "recurrent_weight_inheritance_enabled": False,
            },
        },
        "rows": rows,
        "summary": {
            "mean_candidate_fraction_full": float(sum(r["candidate_fraction_full"] for r in rows) / len(rows)),
            "mean_candidate_fraction_frozen": float(sum(r["candidate_fraction_frozen"] for r in rows) / len(rows)),
            "mean_candidate_fraction_delta": mean_fraction_delta,
            "candidate_fraction_sign_test": sign,
            "mean_max_gain_delta": (
                float(sum(gain_deltas) / len(gain_deltas)) if gain_deltas else None
            ),
            "selected_representation_excess_supported": support,
        },
        "decision_rule": (
            "Selected-representation excess is supported only if the full condition "
            "has positive mean carrier-fraction excess and the paired one-sided sign "
            "test across non-tied histories is <= 0.05."
        ),
        "claim_boundary": (
            "A positive v4.8 result would show that learning/inherited controller "
            "dynamics contribute to the v4.7 E1-like signal beyond a frozen random "
            "recurrent reservoir. It would still not establish cumulative knowledge "
            "or spontaneous science."
        ),
    }
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
