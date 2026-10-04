from __future__ import annotations

"""Observer-side tools for comparing independent epistemic histories.

The module never changes an agent objective, reward, sensor, action, inheritance
mechanism, or world law.  It exists to support the second Latent Worlds North
Star only after emergence evidence exists: hold physics fixed, vary population
history, and compare what is represented and built without comparing arbitrary
neuron labels directly.

Until a history independently satisfies the project's spontaneous-science
criteria, outputs from this module are diagnostics of predictive representation
and technological configuration, not evidence of an alternative science.
"""

from dataclasses import asdict, dataclass, is_dataclass
from itertools import combinations
from types import SimpleNamespace
from typing import Iterable, Mapping, Sequence

import numpy as np

from .agents.recurrent import RecurrentAgent
from .phase_map import long_horizon_config
from .world import World


@dataclass(slots=True)
class HistoryTrace:
    world_seed: int
    agent_seed: int
    horizons: tuple[int, ...]
    times: np.ndarray
    raw: np.ndarray
    hidden_mean: np.ndarray
    collective: np.ndarray
    targets: np.ndarray
    populations: np.ndarray
    generations: np.ndarray
    physics_signature: dict
    technology_delta_profile: np.ndarray
    successful_drops: int
    technology_gain: float
    technology_strength: float


def _serialise_dataclass(obj):
    if is_dataclass(obj):
        return asdict(obj)
    return {
        key: value
        for key, value in vars(obj).items()
        if isinstance(value, (int, float, str, bool, tuple, list))
    }


def _physics_signature(world: World) -> dict:
    """Exact observer-side record of the hidden law held fixed across histories."""
    return {
        "hidden_source_count": int(world.hidden_source_count),
        "forcing": _serialise_dataclass(world.forcing_law),
        "climate": _serialise_dataclass(world.climate),
        "radiation": _serialise_dataclass(world.radiation_law),
        "yield": _serialise_dataclass(world.yield_law),
        "matter": _serialise_dataclass(world.matter_law),
    }


def _population_state(world: World):
    agents = [
        a for a in world.agents
        if isinstance(a, RecurrentAgent) and a.alive and a._initialized
    ]
    if not agents:
        return None

    H = np.asarray([a.hidden for a in agents], dtype=float)
    phys = np.asarray([world.physical_state(a.x, a.y) for a in agents], dtype=float)
    raw = np.concatenate([
        phys.mean(axis=0),
        phys.std(axis=0),
        np.asarray([
            len(agents) / 100.0,
            np.mean([a.energy for a in agents]) / 25.0,
        ], dtype=float),
    ])

    # The within-history decoder may use distributional population information.
    # Cross-history geometry is compared only through hidden_mean because linear
    # CKA on this matrix is invariant to an orthogonal relabelling of hidden axes.
    collective = np.concatenate([
        H.mean(axis=0),
        H.std(axis=0),
        np.quantile(H, 0.25, axis=0),
        np.quantile(H, 0.75, axis=0),
    ])
    return raw, H.mean(axis=0), collective, max(a.generation for a in agents)


def _technology_profile(world: World, grid_size: int = 5):
    """Functional effect of the final material arrangement relative to its start.

    This compares technologies by what their arrangements *do* on a canonical
    evaluator grid, not by object identity or by a hand-authored device label.
    """
    initial_objects = [
        SimpleNamespace(
            x=world.initial_object_positions[o.id][0],
            y=world.initial_object_positions[o.id][1],
            material=o.material,
        )
        for o in world.objects
    ]
    xs = np.linspace(0.0, world.config.width, int(grid_size))
    ys = np.linspace(0.0, world.config.height, int(grid_size))
    delta = []
    for x in xs:
        for y in ys:
            temp, rad = world.physical_state(float(x), float(y))
            current = world.matter_law.multiplier(
                float(x), float(y), temp, rad, world.objects
            )
            baseline = world.matter_law.multiplier(
                float(x), float(y), temp, rad, initial_objects
            )
            delta.append(float(current - baseline))
    profile = np.asarray(delta, dtype=float)
    successful_drops = sum(
        int(e.get("success", False))
        for e in world.object_log
        if e.get("type") == "drop"
    )
    gain = float(np.mean(profile)) if len(profile) else 0.0
    strength = float(np.sqrt(np.mean(profile ** 2))) if len(profile) else 0.0
    return profile, int(successful_drops), gain, strength


def collect_history_trace(
    world_seed: int,
    agent_seed: int,
    *,
    steps: int = 1200,
    burn_in: int = 200,
    stride: int = 5,
    horizons: Sequence[int] = (10, 35, 70),
    information_level: float = 0.35,
    signal_cost: float = 0.03,
    config_overrides: Mapping[str, object] | None = None,
) -> HistoryTrace:
    """Run one population history while keeping the hidden world law explicit."""
    if steps <= 0 or stride <= 0 or burn_in < 0:
        raise ValueError("steps/stride must be positive and burn_in non-negative")
    hz = tuple(int(h) for h in horizons)
    if not hz or any(h <= 0 for h in hz):
        raise ValueError("horizons must contain positive integers")

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

    times = []
    raw_rows = []
    hidden_rows = []
    collective_rows = []
    target_rows = []
    populations = []
    generations = []

    while world.time < int(steps) and any(a.alive for a in world.agents):
        world.step()
        if world.time < int(burn_in) or world.time % int(stride):
            continue
        state = _population_state(world)
        if state is None:
            continue
        raw, hidden_mean, collective, max_generation = state
        times.append(int(world.time))
        raw_rows.append(raw)
        hidden_rows.append(hidden_mean)
        collective_rows.append(collective)
        target_rows.append([
            float(world.forcing_law.value(world.time + h)) for h in hz
        ])
        populations.append(sum(a.alive for a in world.agents))
        generations.append(int(max_generation))

    profile, drops, tech_gain, tech_strength = _technology_profile(world)

    def arr(rows, width):
        if rows:
            return np.asarray(rows, dtype=float)
        return np.empty((0, int(width)), dtype=float)

    return HistoryTrace(
        world_seed=int(world_seed),
        agent_seed=int(agent_seed),
        horizons=hz,
        times=np.asarray(times, dtype=int),
        raw=arr(raw_rows, 6),
        hidden_mean=arr(hidden_rows, RecurrentAgent.HIDDEN),
        collective=arr(collective_rows, 4 * RecurrentAgent.HIDDEN),
        targets=arr(target_rows, len(hz)),
        populations=np.asarray(populations, dtype=int),
        generations=np.asarray(generations, dtype=int),
        physics_signature=physics,
        technology_delta_profile=profile,
        successful_drops=drops,
        technology_gain=tech_gain,
        technology_strength=tech_strength,
    )


def _ridge_fit_predict(Xtr, ytr, Xte, alpha: float = 1e-2):
    Xtr = np.asarray(Xtr, dtype=float)
    Xte = np.asarray(Xte, dtype=float)
    ytr = np.asarray(ytr, dtype=float)
    mu = Xtr.mean(axis=0)
    sd = np.maximum(Xtr.std(axis=0), 1e-6)
    A = np.column_stack([np.ones(len(Xtr)), (Xtr - mu) / sd])
    B = np.column_stack([np.ones(len(Xte)), (Xte - mu) / sd])
    reg = float(alpha) * np.eye(A.shape[1])
    reg[0, 0] = 0.0
    coef = np.linalg.solve(A.T @ A + reg, A.T @ ytr)
    return B @ coef


def _normalised_rmse(pred, truth, scale_reference):
    pred = np.asarray(pred, dtype=float)
    truth = np.asarray(truth, dtype=float)
    ref = np.asarray(scale_reference, dtype=float)
    scale = np.maximum(np.std(ref, axis=0), 1e-6)
    per_target = np.sqrt(np.mean((pred - truth) ** 2, axis=0)) / scale
    return float(np.mean(per_target)), [float(v) for v in per_target]


def predictive_signature(trace: HistoryTrace, split: float = 0.65) -> dict:
    n = len(trace.times)
    if n < 40:
        return {
            "samples": n,
            "raw_nrmse": None,
            "collective_nrmse": None,
            "predictive_gain_over_raw": None,
            "per_horizon_raw_nrmse": [],
            "per_horizon_collective_nrmse": [],
            "predictive_representation_candidate": False,
        }
    k = max(20, min(n - 15, int(n * float(split))))
    ytr, yte = trace.targets[:k], trace.targets[k:]
    raw_pred = _ridge_fit_predict(trace.raw[:k], ytr, trace.raw[k:])
    col_pred = _ridge_fit_predict(trace.collective[:k], ytr, trace.collective[k:])
    raw_rmse, raw_per = _normalised_rmse(raw_pred, yte, ytr)
    col_rmse, col_per = _normalised_rmse(col_pred, yte, ytr)
    gain = float((raw_rmse - col_rmse) / max(raw_rmse, 1e-9))
    return {
        "samples": n,
        "raw_nrmse": raw_rmse,
        "collective_nrmse": col_rmse,
        "predictive_gain_over_raw": gain,
        "per_horizon_raw_nrmse": raw_per,
        "per_horizon_collective_nrmse": col_per,
        # Deliberately weaker than an E2/E5/E6 claim: this is only an observer
        # diagnostic that population internal state contains useful future signal.
        "predictive_representation_candidate": bool(n >= 80 and gain > 0.03),
    }


def linear_cka(X, Y) -> float | None:
    """Linear centered-kernel alignment, invariant to orthogonal axis relabelling."""
    X = np.asarray(X, dtype=float)
    Y = np.asarray(Y, dtype=float)
    if X.ndim != 2 or Y.ndim != 2 or len(X) != len(Y) or len(X) < 3:
        return None
    X = X - X.mean(axis=0, keepdims=True)
    Y = Y - Y.mean(axis=0, keepdims=True)
    cross = Y.T @ X
    denom = np.linalg.norm(X.T @ X, ord="fro") * np.linalg.norm(Y.T @ Y, ord="fro")
    if denom <= 1e-12:
        return None
    return float((np.linalg.norm(cross, ord="fro") ** 2) / denom)


def _cosine_similarity(a, b) -> float | None:
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    denom = float(np.linalg.norm(a) * np.linalg.norm(b))
    if denom <= 1e-12:
        return None
    return float(np.dot(a, b) / denom)


def compare_histories(a: HistoryTrace, b: HistoryTrace, split: float = 0.65) -> dict:
    if a.world_seed != b.world_seed:
        raise ValueError("history comparison requires identical world_seed")
    if a.physics_signature != b.physics_signature:
        raise ValueError("history comparison requires identical hidden physics")
    if a.horizons != b.horizons:
        raise ValueError("history comparison requires identical prediction horizons")

    common, ia, ib = np.intersect1d(
        a.times, b.times, assume_unique=True, return_indices=True
    )
    out = {
        "world_seed": int(a.world_seed),
        "agent_seed_a": int(a.agent_seed),
        "agent_seed_b": int(b.agent_seed),
        "matched_samples": int(len(common)),
        "representation_cka": None,
        "prediction_agreement": None,
        "prediction_divergence_nrmse": None,
        "target_match_max_abs": None,
        "technology_cosine": _cosine_similarity(
            a.technology_delta_profile, b.technology_delta_profile
        ),
        "technology_active_pair": bool(
            a.successful_drops >= 3
            and b.successful_drops >= 3
            and a.technology_strength >= 0.01
            and b.technology_strength >= 0.01
        ),
    }
    if len(common) < 40:
        return out

    Xa = a.hidden_mean[ia]
    Xb = b.hidden_mean[ib]
    out["representation_cka"] = linear_cka(Xa, Xb)

    ya = a.targets[ia]
    yb = b.targets[ib]
    out["target_match_max_abs"] = float(np.max(np.abs(ya - yb)))
    # Same hidden physics and matched times should make these targets identical.
    y = 0.5 * (ya + yb)
    n = len(common)
    k = max(20, min(n - 15, int(n * float(split))))
    pa = _ridge_fit_predict(a.collective[ia][:k], y[:k], a.collective[ia][k:])
    pb = _ridge_fit_predict(b.collective[ib][:k], y[:k], b.collective[ib][k:])
    divergence, _ = _normalised_rmse(pa, pb, y[:k])
    out["prediction_divergence_nrmse"] = divergence
    out["prediction_agreement"] = float(1.0 / (1.0 + divergence))
    return out


def _mean_finite(values: Iterable[float | None]) -> float | None:
    vals = [float(v) for v in values if v is not None and np.isfinite(v)]
    return float(np.mean(vals)) if vals else None


def history_summary(trace: HistoryTrace) -> dict:
    pred = predictive_signature(trace)
    return {
        "world_seed": int(trace.world_seed),
        "agent_seed": int(trace.agent_seed),
        "samples": int(len(trace.times)),
        "completed_time": int(trace.times[-1]) if len(trace.times) else 0,
        "final_population": int(trace.populations[-1]) if len(trace.populations) else 0,
        "max_generation": int(np.max(trace.generations)) if len(trace.generations) else 0,
        "horizons": list(trace.horizons),
        "prediction": pred,
        "technology": {
            "successful_drops": int(trace.successful_drops),
            "functional_gain": float(trace.technology_gain),
            "functional_strength": float(trace.technology_strength),
            "active_candidate": bool(
                trace.successful_drops >= 3 and trace.technology_strength >= 0.01
            ),
        },
    }


def same_physics_campaign(
    world_seed: int,
    agent_seeds: Sequence[int],
    *,
    steps: int = 1200,
    burn_in: int = 200,
    stride: int = 5,
    horizons: Sequence[int] = (10, 35, 70),
    information_level: float = 0.35,
    signal_cost: float = 0.03,
    config_overrides: Mapping[str, object] | None = None,
    q2_eligible_agent_seeds: Sequence[int] = (),
) -> dict:
    """Compare independent histories under one exact hidden-physics realization.

    q2_eligible_agent_seeds must be supplied only from external, preregistered
    evidence that those histories have already met the spontaneous-science
    threshold.  The campaign never promotes histories by its own Q2 metrics.
    """
    seeds = tuple(int(s) for s in agent_seeds)
    if len(set(seeds)) != len(seeds):
        raise ValueError("agent_seeds must be unique")
    traces = [
        collect_history_trace(
            int(world_seed), seed, steps=int(steps), burn_in=int(burn_in),
            stride=int(stride), horizons=horizons,
            information_level=float(information_level), signal_cost=float(signal_cost),
            config_overrides=config_overrides,
        )
        for seed in seeds
    ]

    if traces and any(t.physics_signature != traces[0].physics_signature for t in traces[1:]):
        raise AssertionError("same-physics campaign generated inconsistent hidden laws")

    summaries = [history_summary(t) for t in traces]
    pairs = [compare_histories(a, b) for a, b in combinations(traces, 2)]

    predictive = {
        s["agent_seed"]
        for s in summaries
        if s["prediction"]["predictive_representation_candidate"]
    }
    predictive_pairs = [
        p for p in pairs
        if p["agent_seed_a"] in predictive and p["agent_seed_b"] in predictive
    ]
    active_tech_pairs = [p for p in pairs if p["technology_active_pair"]]

    externally_eligible = set(int(s) for s in q2_eligible_agent_seeds)
    unknown = externally_eligible - set(seeds)
    if unknown:
        raise ValueError(f"q2 eligible seeds not present in campaign: {sorted(unknown)}")
    q2_pairs = [
        p for p in pairs
        if p["agent_seed_a"] in externally_eligible
        and p["agent_seed_b"] in externally_eligible
    ]

    return {
        "world_seed": int(world_seed),
        "agent_seeds": list(seeds),
        "steps": int(steps),
        "burn_in": int(burn_in),
        "stride": int(stride),
        "horizons": [int(h) for h in horizons],
        "physics_signature": traces[0].physics_signature if traces else {},
        "histories": summaries,
        "pairwise": pairs,
        "diagnostic_summary": {
            "histories": len(summaries),
            "predictive_representation_candidates": len(predictive),
            "mean_pairwise_representation_cka_all": _mean_finite(
                p["representation_cka"] for p in pairs
            ),
            "mean_pairwise_prediction_agreement_all": _mean_finite(
                p["prediction_agreement"] for p in pairs
            ),
            "mean_pairwise_representation_cka_predictive": _mean_finite(
                p["representation_cka"] for p in predictive_pairs
            ),
            "mean_pairwise_prediction_agreement_predictive": _mean_finite(
                p["prediction_agreement"] for p in predictive_pairs
            ),
            "active_technology_histories": sum(
                int(s["technology"]["active_candidate"]) for s in summaries
            ),
            "mean_active_technology_cosine": _mean_finite(
                p["technology_cosine"] for p in active_tech_pairs
            ),
        },
        "north_star_stage_ii": {
            "externally_science_qualified_histories": sorted(externally_eligible),
            "eligible_pair_count": len(q2_pairs),
            "inference_allowed": bool(len(externally_eligible) >= 3),
            "mean_eligible_representation_cka": _mean_finite(
                p["representation_cka"] for p in q2_pairs
            ),
            "mean_eligible_prediction_agreement": _mean_finite(
                p["prediction_agreement"] for p in q2_pairs
            ),
            "claim_boundary": (
                "Stage-II universality/contingency inference is disabled unless "
                "at least three histories are supplied as independently qualified "
                "by the Stage-I spontaneous-science protocol."
            ),
        },
    }
