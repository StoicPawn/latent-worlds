"""Individual-agent replication of time-synchrony surrogate audit.

Inputs: observer-only trajectory NPZ from within_time_exchange.py.
No world simulation and no reward modification. Reports *descriptive*
agent-conditional results; agents in one world are correlated.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import mean, median

import numpy as np

from within_time_exchange import fit_temporal, lag_misaligned_mean


def other_agent_exchange(hidden: np.ndarray, times: np.ndarray,
                         seed: int = 41021) -> np.ndarray:
    """Within-time derangement: each row gets a DIFFERENT agent's state."""
    rng = np.random.default_rng(seed)
    out = np.empty_like(hidden)
    for t in np.unique(times):
        idx = np.flatnonzero(times == t)
        if len(idx) < 2:
            out[idx] = 0.0  # not scored in the individual assay
        else:
            perm = np.roll(idx, int(rng.integers(1, len(idx))))
            out[idx] = hidden[perm]
    return out


def leave_one_out_mean(hidden: np.ndarray, times: np.ndarray) -> np.ndarray:
    """At t, average states of *other* living agents only."""
    out = np.empty_like(hidden)
    for t in np.unique(times):
        idx = np.flatnonzero(times == t)
        n = len(idx)
        if n < 2:
            out[idx] = 0.0  # not scored in the individual assay
            continue
        total = hidden[idx].sum(axis=0)
        out[idx] = (total - hidden[idx]) / (n - 1)
    return out


def run_audit(path: Path, min_times: int = 80) -> dict:
    with np.load(path, allow_pickle=False) as a:
        times, ids, raw, hidden, y = [a[k] for k in
                                     ("times", "ids", "raw", "hidden", "target")]
    if not (len(times) == len(ids) == len(raw) == len(hidden) == len(y)):
        raise ValueError("Trace arrays are not aligned")
    if not np.all(np.isfinite(y)) or not np.all(np.isfinite(hidden)):
        raise ValueError("Nonfinite trace")
    options = {
        "individual_hidden": hidden,
        "different_agent_hidden": other_agent_exchange(hidden, times),
        "leave_one_out_mean": leave_one_out_mean(hidden, times),
        "time_shifted_mean": lag_misaligned_mean(hidden, times),
    }
    rows = []
    for agent in sorted(np.unique(ids)):
        idx = np.flatnonzero(ids == agent)
        if len(idx) < min_times:
            continue
        # Reject times when there is no other agent to exchange with.
        ntimes = {int(t): int(np.sum(times == t)) for t in times[idx]}
        idx = np.asarray([i for i in idx if ntimes[int(times[i])] >= 2])
        if len(idx) < min_times:
            continue
        x0 = raw[idx]
        scores = {"raw_only": fit_temporal(x0, y[idx], times[idx])}
        for name, h in options.items():
            scores[name] = fit_temporal(
                np.column_stack((x0, h[idx])), y[idx], times[idx]
            )
        baseline = scores["raw_only"]["mean_nrmse"]
        real = scores["individual_hidden"]["mean_nrmse"]
        exchange = scores["different_agent_hidden"]["mean_nrmse"]
        population = scores["leave_one_out_mean"]["mean_nrmse"]
        rows.append({
            "agent_id": int(agent),
            "n_times": len(idx),
            "scores": {k: float(v["mean_nrmse"]) for k, v in scores.items()},
            "gain_vs_raw": float(baseline - real),
            "gain_vs_exchanged": float(exchange - real),
            "gain_vs_population_mean": float(population - real),
        })
    if not rows:
        raise RuntimeError("No eligible individual carriers")
    return {
        "source_trace": path.name,
        "n_eligible_agents": len(rows),
        "n_total_agent_rows": len(times),
        "metric": "time-ordered NRMSE; lower is better",
        "summary": {
            "mean_gain_vs_raw": mean(r["gain_vs_raw"] for r in rows),
            "mean_gain_vs_exchanged": mean(r["gain_vs_exchanged"] for r in rows),
            "mean_gain_vs_population_mean": mean(r["gain_vs_population_mean"] for r in rows),
            "median_gain_vs_exchanged": median(r["gain_vs_exchanged"] for r in rows),
            "fraction_individual_better_than_raw":
                mean(r["gain_vs_raw"] > 0 for r in rows),
            "fraction_individual_better_than_exchange":
                mean(r["gain_vs_exchanged"] > 0 for r in rows),
        },
        "agents": rows,
        "claim_boundary": (
            "Exploratory individual-decoder audit. Same-world agents share the "
            "future forcing target, correlated selection and environment. "
            "Agent count is NOT an independent physics replication sample. "
            "Decodability does not prove causal use, selected knowledge, "
            "culture, subjective experience or publishability."
        ),
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("trace", type=Path)
    p.add_argument("--min-times", type=int, default=80)
    args = p.parse_args()
    dest = args.trace.with_name(args.trace.stem + "_individual_audit.json")
    if dest.exists():
        raise FileExistsError(dest)
    result = run_audit(args.trace, args.min_times)
    dest.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({
        "saved": str(dest),
        "n_eligible_agents": result["n_eligible_agents"],
        "summary": result["summary"],
    }, indent=2))


if __name__ == "__main__":
    main()
