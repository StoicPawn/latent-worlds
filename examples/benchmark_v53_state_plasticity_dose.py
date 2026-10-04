"""v5.3: exploratory dose-response of generic recurrent state plasticity."""
from __future__ import annotations

import json

from latent_worlds.epistemic_carriers import run_individual_carrier_audit
from latent_worlds.replication import standard_turnover_overrides


WORLD_SEED = 11
AGENT_SEEDS = tuple(range(89, 93))
WAVE_STRENGTH = 1.5
RATES = (0.0001, 0.0003, 0.0007, 0.0015, 0.0030)


def _compact(result):
    eligible = int(result["eligible_carriers"])
    candidates = int(result["carrier_candidates"])
    return {
        "eligible_carriers": eligible,
        "carrier_candidates": candidates,
        "candidate_fraction": float(candidates / eligible) if eligible else 0.0,
        "total_harvest": float(result["total_harvest"]),
        "final_population": int(result["final_population"]),
        "max_generation": int(result["max_generation"]),
        "max_predictive_gain": result["max_predictive_gain"],
        "median_predictive_gain": result["median_predictive_gain"],
    }


def _run(seed: int, *, mode: str, rate: float = 0.0015):
    overrides = dict(standard_turnover_overrides())
    overrides.update({
        "active_obstacle_fraction": 0.75,
        "resource_wave_strength": WAVE_STRENGTH,
        "recurrent_context_features_enabled": True,
        "recurrent_state_plasticity_rate": float(rate),
    })
    if mode == "frozen":
        overrides.update({
            "recurrent_learning_enabled": False,
            "recurrent_weight_inheritance_enabled": False,
            "recurrent_state_plasticity_enabled": False,
        })
    elif mode == "output_only":
        overrides.update({
            "recurrent_learning_enabled": True,
            "recurrent_weight_inheritance_enabled": True,
            "recurrent_state_plasticity_enabled": False,
        })
    elif mode == "state":
        overrides.update({
            "recurrent_learning_enabled": True,
            "recurrent_weight_inheritance_enabled": True,
            "recurrent_state_plasticity_enabled": True,
        })
    else:
        raise ValueError(mode)

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


def _mean(rows, key):
    return float(sum(float(r[key]) for r in rows) / len(rows))


def _pareto_front(points):
    front = []
    for p in points:
        dominated = False
        for q in points:
            if q is p:
                continue
            if (
                q["mean_candidate_fraction"] >= p["mean_candidate_fraction"]
                and q["mean_total_harvest"] >= p["mean_total_harvest"]
                and (
                    q["mean_candidate_fraction"] > p["mean_candidate_fraction"]
                    or q["mean_total_harvest"] > p["mean_total_harvest"]
                )
            ):
                dominated = True
                break
        if not dominated:
            front.append(p["rate"])
    return sorted(front)


def main() -> None:
    frozen_rows = [_run(seed, mode="frozen") for seed in AGENT_SEEDS]
    output_rows = [_run(seed, mode="output_only") for seed in AGENT_SEEDS]

    frozen = {
        "mean_candidate_fraction": _mean(frozen_rows, "candidate_fraction"),
        "mean_total_harvest": _mean(frozen_rows, "total_harvest"),
        "rows": frozen_rows,
    }
    output = {
        "mean_candidate_fraction": _mean(output_rows, "candidate_fraction"),
        "mean_total_harvest": _mean(output_rows, "total_harvest"),
        "rows": output_rows,
    }

    rate_results = []
    for rate in RATES:
        rows = [_run(seed, mode="state", rate=rate) for seed in AGENT_SEEDS]
        rate_results.append({
            "rate": float(rate),
            "mean_candidate_fraction": _mean(rows, "candidate_fraction"),
            "mean_total_harvest": _mean(rows, "total_harvest"),
            "mean_final_population": _mean(rows, "final_population"),
            "mean_max_generation": _mean(rows, "max_generation"),
            "carrier_excess_vs_frozen": float(
                _mean(rows, "candidate_fraction") - frozen["mean_candidate_fraction"]
            ),
            "carrier_excess_vs_output": float(
                _mean(rows, "candidate_fraction") - output["mean_candidate_fraction"]
            ),
            "harvest_excess_vs_frozen": float(
                _mean(rows, "total_harvest") - frozen["mean_total_harvest"]
            ),
            "harvest_excess_vs_output": float(
                _mean(rows, "total_harvest") - output["mean_total_harvest"]
            ),
            "rows": rows,
        })

    admissible = [
        r for r in rate_results
        if r["mean_candidate_fraction"] > max(
            frozen["mean_candidate_fraction"], output["mean_candidate_fraction"]
        )
        and r["mean_total_harvest"] >= output["mean_total_harvest"]
    ]
    candidate_rate = min((r["rate"] for r in admissible), default=None)

    out = {
        "experiment": "v5.3",
        "analysis_type": "exploratory dose-response",
        "world_seed": WORLD_SEED,
        "agent_seeds": list(AGENT_SEEDS),
        "population_seed_status": "A89-A92 reserved for v5.3 discovery only",
        "resource_wave_strength": WAVE_STRENGTH,
        "context_features_enabled": True,
        "rates": list(RATES),
        "frozen": frozen,
        "output_only": output,
        "rate_results": rate_results,
        "pareto_front_rates": _pareto_front(rate_results),
        "admissible_rates": [r["rate"] for r in admissible],
        "candidate_rate_for_prospective_replication": candidate_rate,
        "selection_rule": (
            "A discovery rate is admissible only if mean carrier fraction exceeds "
            "both output-only and frozen controls while mean harvest is at least "
            "the output-only mean. If multiple rates qualify, choose the smallest."
        ),
        "claim_boundary": (
            "v5.3 is parameter discovery only. No rate selected here can support "
            "E1 until frozen and prospectively replicated on unseen population seeds."
        ),
    }
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
