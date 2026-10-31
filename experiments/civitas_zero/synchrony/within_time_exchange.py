"""CIVITAS ZERO — time-matched state-exchange falsification pilot.

Scientific question: since all agents in one simulated world share the same
future-forcing target Y_t, can a decoder's "individual predictive knowledge"
survive exchanging hidden states among individuals at *the same time*?

This is a diagnostic, not an agent intervention or a new claim of knowledge.
Within-time state shuffling is a known class of neural-decoding null models.
All hyperparameters are frozen before the first pilot execution.

Collect complete unmodified trajectories of generic recurrent populations,
then compare observer-only decoders. Strict chronological train/validation/test.
No inference treats agents at the same time as independent world outcomes.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path
import time

import numpy as np

from latent_worlds.agents.recurrent import RecurrentAgent
from latent_worlds.epistemic_carriers import _raw_carrier_baseline
from latent_worlds.phase_map import long_horizon_config
from latent_worlds.replication import standard_turnover_overrides
from latent_worlds.world import World

ALPHAS = (0.1, 1.0, 10.0, 100.0, 1000.0)
HORIZONS = (10, 35, 70)
BURN_IN, STRIDE, STEPS = 80, 3, 500
WORLD_SEEDS = (11, 21)
AGENT_SEEDS = (201, 202)
MODES = ("frozen", "output_only", "state")
RATE = 0.0003
RANDOM_SEED = 26031


def collect(world_seed: int, agent_seed: int, mode: str, *,
            steps: int = STEPS, burn_in: int = BURN_IN,
            stride: int = STRIDE) -> dict:
    if mode not in MODES:
        raise ValueError(mode)
    cfg = long_horizon_config(
        information_level=0.35,
        signal_cost=0.03,
        communication_enabled=True,
        agent_seed=int(agent_seed),
    )
    for k, v in standard_turnover_overrides().items():
        if not hasattr(cfg, k):
            raise ValueError(f"Unknown cfg key: {k}")
        setattr(cfg, k, v)
    cfg.active_obstacle_fraction = 0.75
    cfg.resource_wave_strength = 1.5
    cfg.recurrent_context_features_enabled = True
    cfg.recurrent_learning_enabled = (mode != "frozen")
    cfg.recurrent_weight_inheritance_enabled = (mode != "frozen")
    cfg.recurrent_state_plasticity_enabled = (mode == "state")
    cfg.recurrent_state_plasticity_rate = RATE
    w = World(cfg, seed=int(world_seed))
    xraw, xhidden, targets, times, ids = [], [], [], [], []
    original = int(sum(a.alive for a in w.agents))
    while w.time < steps and any(a.alive for a in w.agents):
        w.step()
        if w.time < burn_in or w.time % stride != 0:
            continue
        future = np.asarray([w.forcing_law.value(w.time + h) for h in HORIZONS], dtype=float)
        for agent in w.agents:
            if not (isinstance(agent, RecurrentAgent) and agent.alive and agent._initialized):
                continue
            xraw.append(_raw_carrier_baseline(w, agent))
            xhidden.append(agent.hidden.copy())
            targets.append(future)
            times.append(w.time)
            ids.append(agent.id)
    if not times:
        raise RuntimeError("No eligible recurrent observations")
    return {
        "world_seed": world_seed, "agent_seed": agent_seed, "mode": mode,
        "times": np.asarray(times, dtype=int),
        "ids": np.asarray(ids, dtype=int),
        "raw": np.asarray(xraw, dtype=float),
        "hidden": np.asarray(xhidden, dtype=float),
        "target": np.asarray(targets, dtype=float),
        "n_initial": original, "n_final": int(sum(a.alive for a in w.agents)),
        "total_harvest": float(sum(a.total_harvest for a in w.agents)),
    }


def time_exchange(hidden: np.ndarray, times: np.ndarray, seed: int) -> np.ndarray:
    """Permute full hidden vectors only within each world-timestamp stratum."""
    out = hidden.copy()
    rng = np.random.default_rng(seed)
    for t in np.unique(times):
        idx = np.flatnonzero(times == t)
        if len(idx) >= 2:
            out[idx] = hidden[rng.permutation(idx)]
    return out


def global_time_mean(hidden: np.ndarray, times: np.ndarray) -> np.ndarray:
    """Global mean state at each t; NO individual pairing remains."""
    out = np.empty_like(hidden)
    for t in np.unique(times):
        idx = np.flatnonzero(times == t)
        out[idx] = hidden[idx].mean(axis=0)
    return out


def lag_misaligned_mean(hidden: np.ndarray, times: np.ndarray) -> np.ndarray:
    """Past-only time-mean surrogate; never access a future hidden state."""
    ts = np.unique(times)
    means = {int(t): hidden[times == t].mean(axis=0) for t in ts}
    out = np.empty_like(hidden)
    shift = max(2, len(ts) // 3)
    for i, t in enumerate(ts):
        # Strict past-only surrogate: never read representations from a later
        # timestamp, including the held-out test suffix. No cyclic wraparound.
        out[times == t] = means[int(ts[max(0, i - shift)])]
    return out


def _predict_ridge(xtrain: np.ndarray, ytrain: np.ndarray,
                   xpred: np.ndarray, alpha: float) -> np.ndarray:
    """No leakage: means/scales fitted only on xtrain, ytrain."""
    mx = xtrain.mean(axis=0)
    sx = np.maximum(xtrain.std(axis=0), 1e-8)
    my = ytrain.mean(axis=0)
    z = (xtrain - mx) / sx
    ztest = (xpred - mx) / sx
    gram = z.T @ z
    gram.flat[::len(gram) + 1] += alpha
    beta = np.linalg.solve(gram, z.T @ (ytrain - my))
    return ztest @ beta + my


def _nrmses(y: np.ndarray, pred: np.ndarray, times: np.ndarray,
            train_reference: np.ndarray) -> list[float]:
    scales = np.maximum(train_reference.std(axis=0), 1e-6)
    vals = []
    for h in range(y.shape[1]):
        # Score timestamp clusters equally, irrespective of fluctuating population.
        err = (pred[:, h] - y[:, h]) ** 2
        per_time = [float(err[times == t].mean()) for t in np.unique(times)]
        vals.append(float(np.sqrt(np.mean(per_time)) / scales[h]))
    return vals


def fit_temporal(x: np.ndarray, y: np.ndarray, times: np.ndarray) -> dict:
    unique = np.unique(times)
    if len(unique) < 35:
        raise ValueError("Insufficient distinct times")
    dev_end = max(20, int(0.70 * len(unique)))
    val_start = max(12, int(0.70 * dev_end))
    dev_times, val_times, test_times = unique[:val_start], unique[val_start:dev_end], unique[dev_end:]
    first, val = np.isin(times, dev_times), np.isin(times, val_times)
    dev, test = times <= unique[dev_end - 1], times >= unique[dev_end]
    scores = []
    for alpha in ALPHAS:
        pred = _predict_ridge(x[first], y[first], x[val], alpha)
        scores.append(float(np.mean(_nrmses(y[val], pred, times[val], y[first]))))
    best = min(zip(scores, ALPHAS))[1]
    pred = _predict_ridge(x[dev], y[dev], x[test], best)
    nrmses = _nrmses(y[test], pred, times[test], y[dev])
    return {
        "mean_nrmse": float(np.mean(nrmses)),
        "per_horizon_nrmse": nrmses,
        "chosen_alpha": best,
        "n_train_times": len(dev_times) + len(val_times),
        "n_test_times": len(test_times),
        "n_train_rows": int(dev.sum()),
        "n_test_rows": int(test.sum()),
    }


def diagnose(sample: dict) -> dict:
    raw, hidden, y, times = (sample[k] for k in ("raw", "hidden", "target", "times"))
    surrogate = time_exchange(hidden, times, RANDOM_SEED + sample["world_seed"] * 1000 + sample["agent_seed"])
    pool = global_time_mean(hidden, times)
    lagged = lag_misaligned_mean(hidden, times)
    variants = {
        "raw_only": raw,
        "individual_hidden": np.column_stack((raw, hidden)),
        "time_matched_exchange": np.column_stack((raw, surrogate)),
        "population_mean_hidden": np.column_stack((raw, pool)),
        "time_misaligned_mean": np.column_stack((raw, lagged)),
    }
    outcomes = {name: fit_temporal(x, y, times) for name, x in variants.items()}
    unique = np.unique(times)
    max_group = max(np.sum(times == t) for t in unique)
    min_group = min(np.sum(times == t) for t in unique)
    return {
        "experiment": "CIVITAS ZERO v5.5 diagnostic/pilot, NOT confirmatory",
        "source_world": sample["world_seed"],
        "agent_seed": sample["agent_seed"],
        "mode": sample["mode"],
        "n_agent_rows": len(times),
        "n_distinct_world_times": len(unique),
        "min_agents_per_time": int(min_group),
        "max_agents_per_time": int(max_group),
        "n_initial": sample["n_initial"],
        "n_final": sample["n_final"],
        "total_harvest": sample["total_harvest"],
        "outcomes": outcomes,
        "shared_target_max_disagreement": float(max(
            np.max(np.ptp(y[times == t], axis=0)) for t in unique
        )),
        "claim_limits": (
            "Same-time exchange is an established style of conditioning/shuffling. "
            "It does not imply that agent memory is useless, nor does a decoder "
            "improvement prove endogenous prediction or causality. "
            "Agent rows are NOT independent: all have identical Y_t at time t."
        ),
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--world", type=int, default=11, choices=WORLD_SEEDS)
    p.add_argument("--agent", type=int, default=201, choices=AGENT_SEEDS)
    p.add_argument("--mode", default="state", choices=MODES)
    p.add_argument("--steps", type=int, default=STEPS)
    p.add_argument("--save-trace", action="store_true", help="Save observer-only raw states for individual audit")
    p.add_argument("--out-dir", type=Path,
                   default=Path("experiments/civitas_zero/data/synchrony_pilot"))
    args = p.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    output = args.out_dir / f"W{args.world}_A{args.agent}_{args.mode}_{args.steps}.json"
    if output.exists():
        raise FileExistsError(f"Do not overwrite a pilot result: {output}")
    start = time.monotonic()
    sample = collect(args.world, args.agent, args.mode, steps=args.steps)
    result = diagnose(sample)
    if args.save_trace:
        trace_path = output.with_suffix(".npz")
        if trace_path.exists():
            raise FileExistsError(f"Do not overwrite trace: {trace_path}")
        np.savez_compressed(trace_path, **{k: sample[k] for k in ("times", "ids", "raw", "hidden", "target")})
        result["trace_path"] = str(trace_path)
    result["steps"] = args.steps
    result["runtime_seconds"] = round(time.monotonic() - start, 2)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "result_file": str(output),
        "runtime_seconds": result["runtime_seconds"],
        "n_times": result["n_distinct_world_times"],
        "mean_nrmse": {k: round(v["mean_nrmse"], 5) for k, v in result["outcomes"].items()},
    }, indent=2))


if __name__ == "__main__":
    main()
