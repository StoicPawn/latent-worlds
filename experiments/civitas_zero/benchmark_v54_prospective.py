"""CIVITAS ZERO / Latent Worlds: preregistered v5.4 E1 replication.

Use inside the root of StoicPawn/latent-worlds (Python >=3.11, numpy>=2).
Prospective run only: parameter selection happened on A89-A92 in v5.3.
This file makes no change to the physics or rewards of Latent Worlds.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from math import comb
from pathlib import Path

# Frozen before the prospective run.
WORLD_SEED = 11
AGENT_SEEDS = tuple(range(93, 109))  # 16 entirely unseen population seeds
RATE = 0.0003  # chosen on v5.3 discovery A89-A92, no retuning permitted
WAVE_STRENGTH = 1.5
MODES = ("frozen", "output_only", "state")


def exact_sign_pvalue(differences: list[float]) -> dict:
    """One-sided exact sign test, ties excluded and fully reported."""
    positives = sum(x > 0.0 for x in differences)
    negatives = sum(x < 0.0 for x in differences)
    ties = len(differences) - positives - negatives
    n = positives + negatives
    p = sum(comb(n, k) for k in range(positives, n + 1)) / (2 ** n) if n else 1.0
    return {"positive": positives, "negative": negatives, "ties": ties, "effective_n": n, "p_one_sided": p}


def run_condition(agent_seed: int, mode: str) -> dict:
    # Lazy import supports pure verification of this runner before installation.
    from latent_worlds.epistemic_carriers import run_individual_carrier_audit
    from latent_worlds.replication import standard_turnover_overrides

    if mode not in MODES:
        raise ValueError(f"Unknown condition: {mode}")
    cfg = dict(standard_turnover_overrides())
    cfg.update(
        active_obstacle_fraction=0.75,
        resource_wave_strength=WAVE_STRENGTH,
        recurrent_context_features_enabled=True,
        recurrent_state_plasticity_rate=RATE,
        recurrent_learning_enabled=(mode != "frozen"),
        recurrent_weight_inheritance_enabled=(mode != "frozen"),
        recurrent_state_plasticity_enabled=(mode == "state"),
    )
    r = run_individual_carrier_audit(
        WORLD_SEED, agent_seed,
        steps=1200, burn_in=200, stride=2, horizons=(10, 35, 70),
        min_samples=80, information_level=0.35, signal_cost=0.03,
        config_overrides=cfg,
    )
    eligible = int(r["eligible_carriers"])
    carriers = int(r["carrier_candidates"])
    # If eligible is zero, the ratio is undefined. Do not silently turn it into 0.
    return {
        "eligible_carriers": eligible,
        "carrier_candidates": carriers,
        "candidate_fraction": carriers / eligible if eligible else None,
        "total_harvest": float(r["total_harvest"]),
        "final_population": int(r["final_population"]),
        "max_generation": int(r["max_generation"]),
    }


def evaluate(rows: list[dict]) -> dict:
    valid = [r for r in rows if all(r["conditions"][m]["candidate_fraction"] is not None for m in MODES)]
    missing = len(rows) - len(valid)
    diffs = {
        baseline: [r["conditions"]["state"]["candidate_fraction"] - r["conditions"][baseline]["candidate_fraction"] for r in valid]
        for baseline in ("frozen", "output_only")
    }
    score = {k: exact_sign_pvalue(v) for k, v in diffs.items()}
    for k, v in diffs.items():
        score[k]["mean_difference"] = sum(v) / len(v) if v else None
    harvest_delta = [r["conditions"]["state"]["total_harvest"] - r["conditions"]["output_only"]["total_harvest"] for r in rows]
    mean_harvest = sum(harvest_delta) / len(harvest_delta) if harvest_delta else None
    # Conservative predeclared gate: no eligible-carrier dropouts, both fraction
    # contrasts positive with exact one-sided sign p <=.05, and no mean fitness loss.
    passed = bool(
        missing == 0 and len(rows) == len(AGENT_SEEDS)
        and all(score[k]["mean_difference"] is not None and score[k]["mean_difference"] > 0
                and score[k]["p_one_sided"] <= 0.05 for k in diffs)
        and mean_harvest is not None and mean_harvest >= 0
    )
    return {"eligible_complete": len(valid), "missing_eligibility": missing,
            "carrier_fraction_tests": score, "mean_harvest_state_minus_output": mean_harvest,
            "gate_passed": passed,
            "interpretation": "E1 candidate requiring independent world holdout; never evidence for civilisation or consciousness"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/v54_prospective"))
    parser.add_argument("--seed", type=int, default=None,
                        help="Run one preregistered seed at a time for resource-limited machines.")
    parser.add_argument("--aggregate-only", action="store_true",
                        help="Read all 16 saved seed files and evaluate the frozen gate without any simulations.")
    args = parser.parse_args()
    if args.aggregate_only and args.seed is not None:
        parser.error("--aggregate-only cannot be combined with --seed")
    seeds = AGENT_SEEDS if args.seed is None else (args.seed,)
    if any(seed not in AGENT_SEEDS for seed in seeds):
        parser.error(f"Allowed preregistered seeds: {AGENT_SEEDS[0]}...{AGENT_SEEDS[-1]}")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {"experiment": "v5.4", "status": "prospective", "rate_frozen": RATE,
                "world_seed": WORLD_SEED, "population_seeds": list(AGENT_SEEDS),
                "conditions": list(MODES), "discovery_population_seeds_excluded": list(range(89, 93)),
                "source": "StoicPawn/latent-worlds v5.3 candidate", "source_code_base_sha": "2cca2dc019541f296285b75daa8e416c7818b15e"}
    mp = args.output_dir / "manifest.json"
    if mp.exists():
        if json.loads(mp.read_text(encoding="utf8")) != manifest:
            raise RuntimeError("Frozen protocol changed; refusing to mix runs")
    else:
        mp.write_text(json.dumps(manifest, indent=2), encoding="utf8")

    if not args.aggregate_only:
        for seed in seeds:
            path = args.output_dir / f"seed_{seed}.json"
            if path.exists():
                print(f"Already saved (no overwrite): {path}")
                continue
            conditions = {mode: run_condition(seed, mode) for mode in MODES}
            record = {"agent_seed": seed, "world_seed": WORLD_SEED, "conditions": conditions}
            path.write_text(json.dumps(record, indent=2), encoding="utf8")
            print(f"Saved: {path}")

    records = []
    for seed in AGENT_SEEDS:
        path = args.output_dir / f"seed_{seed}.json"
        if path.exists():
            record = json.loads(path.read_text(encoding="utf8"))
            if int(record.get("agent_seed", -1)) != seed or int(record.get("world_seed", -1)) != WORLD_SEED:
                raise RuntimeError(f"Mismatched seed or world in {path}")
            records.append(record)
    done = len(records) == len(AGENT_SEEDS)
    summary = {"completed_seeds": [x["agent_seed"] for x in records],
               "n_completed": len(records),
               "evaluation": evaluate(records) if done else "incomplete; preregistered gate not evaluated"}
    if done:
        path = args.output_dir / "summary.json"
        if path.exists() and json.loads(path.read_text(encoding="utf8")) != summary:
            raise RuntimeError("Previously archived summary differs")
        path.write_text(json.dumps(summary, indent=2), encoding="utf8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
