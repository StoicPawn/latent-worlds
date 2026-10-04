from __future__ import annotations

"""Observer-side audit for rare individual carriers of predictive information.

Population averaging can erase a representation that exists only in a few long-
lived agents.  This module follows persistent recurrent agents by identity and
asks a conservative conditional question: does adding the agent's hidden state
improve future-physics prediction beyond a contemporaneous baseline containing
the local physical state, position, energy, nearby resource geometry, population
size, and the same hard-coded clock signal available to the controller?

Nothing in this module is visible to agents or enters fitness.
"""

from collections import defaultdict
from dataclasses import dataclass
import math
from typing import Mapping, Sequence

import numpy as np

from .agents.recurrent import RecurrentAgent
from .epistemic_convergence import _normalised_rmse, _ridge_fit_predict, _physics_signature
from .epistemic_decoder_controls import DEFAULT_ALPHAS
from .phase_map import long_horizon_config
from .world import World


@dataclass(slots=True)
class CarrierRows:
    agent_id: int
    generation: int
    times: list[int]
    raw: list[np.ndarray]
    hidden: list[np.ndarray]
    targets: list[np.ndarray]


def _raw_carrier_baseline(world: World, agent: RecurrentAgent) -> np.ndarray:
    temp, rad = world.physical_state(agent.x, agent.y)
    near = world.nearby(agent)
    nearest = near[0] if near else (0.0, 0.0, 0.0)
    living = sum(a.alive for a in world.agents)
    # The controller itself receives sin/cos(0.019*time). Including the same
    # clock in the observer baseline prevents a false "representation" claim
    # caused solely by that hard-coded temporal input.
    return np.asarray([
        temp,
        rad,
        agent.x / max(world.config.width, 1e-9),
        agent.y / max(world.config.height, 1e-9),
        agent.energy / 25.0,
        nearest[0] / 5.0,
        nearest[1] / 5.0,
        nearest[2] / 8.0,
        living / 100.0,
        0.0 if agent.last_yield is None else float(agent.last_yield) / 2.0,
        math.sin(0.019 * world.time),
        math.cos(0.019 * world.time),
    ], dtype=float)


def _nested_predictions(
    X,
    y,
    *,
    alphas: Sequence[float] = DEFAULT_ALPHAS,
    outer_split: float = 0.65,
    inner_split: float = 0.70,
):
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=float)
    n = len(y)
    if X.ndim != 2 or y.ndim != 2 or len(X) != n or n < 60:
        return None

    outer_k = max(35, min(n - 20, int(n * outer_split)))
    inner_k = max(25, min(outer_k - 10, int(outer_k * inner_split)))
    if inner_k >= outer_k:
        return None

    best_alpha = None
    best_score = float("inf")
    for alpha in tuple(float(a) for a in alphas):
        pred = _ridge_fit_predict(
            X[:inner_k], y[:inner_k], X[inner_k:outer_k], alpha=alpha
        )
        score, _ = _normalised_rmse(pred, y[inner_k:outer_k], y[:inner_k])
        if score < best_score - 1e-12 or (
            abs(score - best_score) <= 1e-12
            and (best_alpha is None or alpha > best_alpha)
        ):
            best_score = float(score)
            best_alpha = float(alpha)

    if best_alpha is None:
        return None
    pred = _ridge_fit_predict(
        X[:outer_k], y[:outer_k], X[outer_k:], alpha=best_alpha
    )
    score, per = _normalised_rmse(pred, y[outer_k:], y[:outer_k])
    return {
        "alpha": best_alpha,
        "outer_k": int(outer_k),
        "prediction": np.asarray(pred, dtype=float),
        "truth": np.asarray(y[outer_k:], dtype=float),
        "scale_reference": np.asarray(y[:outer_k], dtype=float),
        "nrmse": float(score),
        "per_horizon_nrmse": list(per),
    }


def _block_bootstrap_lower(
    values,
    *,
    block: int = 8,
    resamples: int = 399,
    seed: int = 0,
    quantile: float = 0.05,
) -> float | None:
    values = np.asarray(values, dtype=float)
    n = len(values)
    if n < max(12, block * 2):
        return None
    block = max(2, min(int(block), n))
    starts = np.arange(0, n - block + 1)
    if len(starts) == 0:
        return None
    rng = np.random.default_rng(int(seed))
    means = []
    blocks_needed = int(np.ceil(n / block))
    for _ in range(int(resamples)):
        picked = rng.choice(starts, size=blocks_needed, replace=True)
        sample = np.concatenate([values[s:s + block] for s in picked])[:n]
        means.append(float(np.mean(sample)))
    return float(np.quantile(means, float(quantile)))


def audit_carrier(rows: CarrierRows, *, min_samples: int = 80) -> dict | None:
    if len(rows.times) < int(min_samples):
        return None
    raw = np.asarray(rows.raw, dtype=float)
    hidden = np.asarray(rows.hidden, dtype=float)
    y = np.asarray(rows.targets, dtype=float)
    augmented = np.column_stack([raw, hidden])

    base = _nested_predictions(raw, y)
    aug = _nested_predictions(augmented, y)
    if base is None or aug is None:
        return None
    if base["outer_k"] != aug["outer_k"]:
        raise AssertionError("paired carrier models must use the same test suffix")

    gain = float((base["nrmse"] - aug["nrmse"]) / max(base["nrmse"], 1e-9))
    scale = np.maximum(np.std(base["scale_reference"], axis=0), 1e-6)
    e0 = ((base["prediction"] - base["truth"]) / scale) ** 2
    e1 = ((aug["prediction"] - aug["truth"]) / scale) ** 2
    improvement = np.mean(e0 - e1, axis=1)
    ci_lower = _block_bootstrap_lower(
        improvement,
        seed=1009 + 17 * int(rows.agent_id) + int(rows.generation),
    )
    return {
        "agent_id": int(rows.agent_id),
        "generation": int(rows.generation),
        "samples": int(len(rows.times)),
        "first_time": int(rows.times[0]),
        "last_time": int(rows.times[-1]),
        "raw_alpha": float(base["alpha"]),
        "augmented_alpha": float(aug["alpha"]),
        "raw_nrmse": float(base["nrmse"]),
        "raw_plus_hidden_nrmse": float(aug["nrmse"]),
        "predictive_gain": gain,
        "paired_error_improvement": float(np.mean(improvement)),
        "bootstrap_lower_95": ci_lower,
        "carrier_candidate": bool(
            gain > 0.03 and ci_lower is not None and ci_lower > 0.0
        ),
    }


def run_individual_carrier_audit(
    world_seed: int,
    agent_seed: int,
    *,
    steps: int = 1200,
    burn_in: int = 200,
    stride: int = 2,
    horizons: Sequence[int] = (10, 35, 70),
    min_samples: int = 80,
    information_level: float = 0.35,
    signal_cost: float = 0.03,
    config_overrides: Mapping[str, object] | None = None,
) -> dict:
    hz = tuple(int(h) for h in horizons)
    cfg = long_horizon_config(
        information_level=float(information_level),
        signal_cost=float(signal_cost),
        communication_enabled=True,
        agent_seed=int(agent_seed),
    )
    for key, value in dict(config_overrides or {}).items():
        if not hasattr(cfg, key):
            raise ValueError(f"unknown SimulationConfig field: {key}")
        setattr(cfg, key, value)

    world = World(cfg, seed=int(world_seed))
    physics = _physics_signature(world)
    by_agent: dict[int, CarrierRows] = {}

    while world.time < int(steps) and any(a.alive for a in world.agents):
        world.step()
        if world.time < int(burn_in) or world.time % int(stride):
            continue
        for agent in world.agents:
            if not (
                isinstance(agent, RecurrentAgent)
                and agent.alive
                and agent._initialized
            ):
                continue
            row = by_agent.get(agent.id)
            if row is None:
                row = CarrierRows(
                    agent_id=int(agent.id),
                    generation=int(agent.generation),
                    times=[],
                    raw=[],
                    hidden=[],
                    targets=[],
                )
                by_agent[agent.id] = row
            row.times.append(int(world.time))
            row.raw.append(_raw_carrier_baseline(world, agent))
            row.hidden.append(np.asarray(agent.hidden, dtype=float).copy())
            row.targets.append(np.asarray([
                float(world.forcing_law.value(world.time + h)) for h in hz
            ], dtype=float))

    audited = []
    for agent_id in sorted(by_agent):
        result = audit_carrier(by_agent[agent_id], min_samples=int(min_samples))
        if result is not None:
            audited.append(result)

    candidates = [r for r in audited if r["carrier_candidate"]]
    gains = [float(r["predictive_gain"]) for r in audited]
    generations = sorted({int(r["generation"]) for r in candidates})
    return {
        "world_seed": int(world_seed),
        "agent_seed": int(agent_seed),
        "steps": int(steps),
        "burn_in": int(burn_in),
        "stride": int(stride),
        "horizons": list(hz),
        "min_samples": int(min_samples),
        "physics_signature": physics,
        "final_population": int(sum(a.alive for a in world.agents)),
        "births": int(world.births),
        "deaths": int(world.deaths),
        "max_generation": int(max((a.generation for a in world.agents), default=0)),
        "total_harvest": float(sum(a.total_harvest for a in world.agents)),
        "eligible_carriers": len(audited),
        "carrier_candidates": len(candidates),
        "candidate_agent_ids": [int(r["agent_id"]) for r in candidates],
        "candidate_generations": generations,
        "max_predictive_gain": max(gains) if gains else None,
        "median_predictive_gain": float(np.median(gains)) if gains else None,
        "carriers": audited,
        "claim_boundary": (
            "A carrier_candidate is a held-out individual-level E1-like diagnostic. "
            "It is not cumulative knowledge or spontaneous science and requires "
            "prospective replication on new histories."
        ),
    }
