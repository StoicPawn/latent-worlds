from __future__ import annotations

"""Capacity-controlled observer decoders for epistemic-history diagnostics.

v4.5 used one fixed ridge penalty for a 6-dimensional raw baseline and a
48-dimensional collective-state decoder.  That is a valid frozen result, but a
negative collective result can be confounded by unequal decoder capacity.

This module adds a new, prospective control: each representation receives its
own ridge penalty selected only on an earlier temporal validation window.  The
chosen model is then refit on the complete development prefix and evaluated on
a later untouched test suffix.  No future rows participate in model selection.
"""

from dataclasses import dataclass
from typing import Mapping, Sequence

import numpy as np

from .epistemic_convergence import (
    HistoryTrace,
    _normalised_rmse,
    _ridge_fit_predict,
    collect_history_trace,
)


DEFAULT_ALPHAS = (1e-4, 1e-3, 1e-2, 1e-1, 1.0, 10.0, 100.0)


@dataclass(slots=True)
class TunedDecoderResult:
    alpha: float
    nrmse: float
    per_horizon_nrmse: list[float]


def _time_ordered_tuned_decoder(
    X,
    y,
    *,
    outer_split: float = 0.65,
    inner_split: float = 0.70,
    alphas: Sequence[float] = DEFAULT_ALPHAS,
) -> TunedDecoderResult | None:
    """Nested past-only ridge selection with a final untouched future suffix."""
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=float)
    n = len(y)
    if X.ndim != 2 or y.ndim != 2 or len(X) != n or n < 60:
        return None

    outer_k = max(35, min(n - 20, int(n * float(outer_split))))
    inner_k = max(25, min(outer_k - 10, int(outer_k * float(inner_split))))
    if inner_k >= outer_k:
        return None

    best_alpha = None
    best_score = float("inf")
    for alpha in tuple(float(a) for a in alphas):
        pred = _ridge_fit_predict(
            X[:inner_k], y[:inner_k], X[inner_k:outer_k], alpha=alpha
        )
        score, _ = _normalised_rmse(
            pred, y[inner_k:outer_k], y[:inner_k]
        )
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
    return TunedDecoderResult(
        alpha=best_alpha,
        nrmse=float(score),
        per_horizon_nrmse=list(per),
    )


def capacity_controlled_predictive_signature(
    trace: HistoryTrace,
    *,
    alphas: Sequence[float] = DEFAULT_ALPHAS,
) -> dict:
    """Compare raw, hidden-mean and collective predictors under equal protocol."""
    reps = {
        "raw": trace.raw,
        "hidden_mean": trace.hidden_mean,
        "collective": trace.collective,
    }
    fitted = {
        name: _time_ordered_tuned_decoder(X, trace.targets, alphas=alphas)
        for name, X in reps.items()
    }

    def pack(result):
        if result is None:
            return {
                "alpha": None,
                "nrmse": None,
                "per_horizon_nrmse": [],
            }
        return {
            "alpha": float(result.alpha),
            "nrmse": float(result.nrmse),
            "per_horizon_nrmse": list(result.per_horizon_nrmse),
        }

    raw = fitted["raw"]
    internal = [
        (name, result)
        for name, result in fitted.items()
        if name != "raw" and result is not None
    ]
    best_name = None
    best = None
    if internal:
        best_name, best = min(internal, key=lambda item: item[1].nrmse)

    gain = None
    if raw is not None and best is not None:
        gain = float((raw.nrmse - best.nrmse) / max(raw.nrmse, 1e-9))

    return {
        "samples": int(len(trace.times)),
        "raw": pack(raw),
        "hidden_mean": pack(fitted["hidden_mean"]),
        "collective": pack(fitted["collective"]),
        "best_internal_representation": best_name,
        "best_internal_nrmse": None if best is None else float(best.nrmse),
        "predictive_gain_over_raw": gain,
        "predictive_representation_candidate": bool(
            len(trace.times) >= 80 and gain is not None and gain > 0.03
        ),
        "selection_protocol": {
            "outer_split": 0.65,
            "inner_split_within_development": 0.70,
            "alphas": [float(a) for a in alphas],
            "future_test_used_for_selection": False,
        },
    }


def capacity_controlled_same_physics_campaign(
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
) -> dict:
    seeds = tuple(int(s) for s in agent_seeds)
    if len(set(seeds)) != len(seeds):
        raise ValueError("agent_seeds must be unique")

    traces = [
        collect_history_trace(
            int(world_seed),
            seed,
            steps=int(steps),
            burn_in=int(burn_in),
            stride=int(stride),
            horizons=horizons,
            information_level=float(information_level),
            signal_cost=float(signal_cost),
            config_overrides=config_overrides,
        )
        for seed in seeds
    ]
    if traces and any(
        t.physics_signature != traces[0].physics_signature for t in traces[1:]
    ):
        raise AssertionError("same-physics campaign generated inconsistent hidden laws")

    rows = []
    for trace in traces:
        signature = capacity_controlled_predictive_signature(trace)
        rows.append({
            "world_seed": int(trace.world_seed),
            "agent_seed": int(trace.agent_seed),
            "samples": int(len(trace.times)),
            "completed_time": int(trace.times[-1]) if len(trace.times) else 0,
            "final_population": int(trace.populations[-1]) if len(trace.populations) else 0,
            "max_generation": int(np.max(trace.generations)) if len(trace.generations) else 0,
            "prediction": signature,
            "technology": {
                "successful_drops": int(trace.successful_drops),
                "functional_gain": float(trace.technology_gain),
                "functional_strength": float(trace.technology_strength),
            },
        })

    gains = [
        float(r["prediction"]["predictive_gain_over_raw"])
        for r in rows
        if r["prediction"]["predictive_gain_over_raw"] is not None
    ]
    candidates = [
        r["agent_seed"]
        for r in rows
        if r["prediction"]["predictive_representation_candidate"]
    ]
    representation_counts = {
        name: sum(
            r["prediction"]["best_internal_representation"] == name
            for r in rows
        )
        for name in ("hidden_mean", "collective")
    }
    return {
        "world_seed": int(world_seed),
        "agent_seeds": list(seeds),
        "steps": int(steps),
        "burn_in": int(burn_in),
        "stride": int(stride),
        "horizons": [int(h) for h in horizons],
        "physics_signature": traces[0].physics_signature if traces else {},
        "histories": rows,
        "summary": {
            "histories": len(rows),
            "predictive_representation_candidates": len(candidates),
            "candidate_agent_seeds": candidates,
            "mean_predictive_gain_over_raw": (
                float(np.mean(gains)) if gains else None
            ),
            "max_predictive_gain_over_raw": (
                float(np.max(gains)) if gains else None
            ),
            "best_representation_counts": representation_counts,
        },
        "claim_boundary": (
            "This capacity-control experiment can validate or reject an E1-like "
            "predictive-representation diagnostic. It cannot establish E2-E6 or "
            "Stage-II scientific universality/contingency."
        ),
    }
