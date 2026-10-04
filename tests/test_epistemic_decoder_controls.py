import numpy as np

from latent_worlds.epistemic_convergence import HistoryTrace
from latent_worlds.epistemic_decoder_controls import (
    DEFAULT_ALPHAS,
    _time_ordered_tuned_decoder,
    capacity_controlled_predictive_signature,
)


def _trace_with_internal_signal(seed: int = 1) -> HistoryTrace:
    rng = np.random.default_rng(seed)
    n = 220
    t = np.arange(n)
    z1 = np.sin(t / 13.0)
    z2 = np.cos(t / 19.0)
    targets = np.column_stack([
        0.8 * z1 - 0.3 * z2,
        -0.2 * z1 + 0.9 * z2,
    ])

    hidden = rng.normal(0, 0.03, size=(n, 12))
    hidden[:, 0] += z1
    hidden[:, 1] += z2
    collective = np.concatenate([hidden, hidden, hidden, hidden], axis=1)
    raw = rng.normal(size=(n, 6))
    profile = np.zeros(25)
    return HistoryTrace(
        world_seed=1,
        agent_seed=seed,
        horizons=(10, 35),
        times=t,
        raw=raw,
        hidden_mean=hidden,
        collective=collective,
        targets=targets,
        populations=np.full(n, 40),
        generations=np.full(n, 3),
        physics_signature={"law": "same"},
        technology_delta_profile=profile,
        successful_drops=0,
        technology_gain=0.0,
        technology_strength=0.0,
    )


def test_tuned_decoder_selects_only_from_preregistered_grid():
    trace = _trace_with_internal_signal()
    result = _time_ordered_tuned_decoder(
        trace.hidden_mean, trace.targets, alphas=DEFAULT_ALPHAS
    )
    assert result is not None
    assert result.alpha in DEFAULT_ALPHAS
    assert np.isfinite(result.nrmse)


def test_capacity_control_detects_low_dimensional_internal_signal():
    trace = _trace_with_internal_signal()
    result = capacity_controlled_predictive_signature(trace)
    assert result["best_internal_representation"] in {"hidden_mean", "collective"}
    assert result["best_internal_nrmse"] < result["raw"]["nrmse"]
    assert result["predictive_gain_over_raw"] > 0.5
    assert result["predictive_representation_candidate"]
    assert result["selection_protocol"]["future_test_used_for_selection"] is False


def test_capacity_control_rejects_internal_noise_when_raw_is_informative():
    rng = np.random.default_rng(8)
    n = 240
    t = np.arange(n)
    z = np.sin(t / 17.0)
    targets = np.column_stack([z, 0.5 * z])
    raw = rng.normal(0, 0.02, size=(n, 6))
    raw[:, 0] += z
    hidden = rng.normal(size=(n, 12))
    collective = np.concatenate([hidden, hidden, hidden, hidden], axis=1)
    trace = HistoryTrace(
        world_seed=2,
        agent_seed=8,
        horizons=(10, 35),
        times=t,
        raw=raw,
        hidden_mean=hidden,
        collective=collective,
        targets=targets,
        populations=np.full(n, 35),
        generations=np.full(n, 2),
        physics_signature={"law": "same"},
        technology_delta_profile=np.zeros(25),
        successful_drops=0,
        technology_gain=0.0,
        technology_strength=0.0,
    )
    result = capacity_controlled_predictive_signature(trace)
    assert result["predictive_gain_over_raw"] < 0.0
    assert not result["predictive_representation_candidate"]
