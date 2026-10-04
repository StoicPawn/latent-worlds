import numpy as np

from latent_worlds.epistemic_convergence import (
    HistoryTrace,
    _cosine_similarity,
    collect_history_trace,
    compare_histories,
    linear_cka,
    predictive_signature,
)


def _synthetic_trace(seed: int, rotation: np.ndarray | None = None) -> HistoryTrace:
    rng = np.random.default_rng(seed)
    n = 140
    t = np.arange(n)
    z = np.column_stack([
        np.sin(t / 11.0),
        np.cos(t / 17.0),
        np.sin(t / 23.0 + 0.4),
    ])
    base = np.column_stack([z, rng.normal(0, 0.03, size=(n, 3))])
    if rotation is not None:
        hidden = base @ rotation
    else:
        hidden = base
    # Pad to the recurrent controller hidden width.
    hidden = np.pad(hidden, ((0, 0), (0, 12 - hidden.shape[1])))
    collective = np.concatenate([hidden, hidden, hidden, hidden], axis=1)
    raw = rng.normal(size=(n, 6))
    targets = np.column_stack([
        0.7 * z[:, 0] - 0.2 * z[:, 1],
        -0.4 * z[:, 0] + 0.8 * z[:, 2],
    ])
    profile = np.linspace(-0.2, 0.3, 25)
    return HistoryTrace(
        world_seed=7,
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
        successful_drops=5,
        technology_gain=float(profile.mean()),
        technology_strength=float(np.sqrt(np.mean(profile ** 2))),
    )


def test_linear_cka_is_invariant_to_orthogonal_relabelling():
    rng = np.random.default_rng(9)
    X = rng.normal(size=(240, 6))
    q, _ = np.linalg.qr(rng.normal(size=(6, 6)))
    Y = 3.2 * X @ q
    assert linear_cka(X, Y) > 0.999999


def test_predictive_signature_detects_internal_future_signal():
    trace = _synthetic_trace(3)
    result = predictive_signature(trace)
    assert result["collective_nrmse"] < result["raw_nrmse"]
    assert result["predictive_gain_over_raw"] > 0.5
    assert result["predictive_representation_candidate"]


def test_compare_histories_uses_function_not_axis_identity():
    rng = np.random.default_rng(4)
    q, _ = np.linalg.qr(rng.normal(size=(6, 6)))
    a = _synthetic_trace(1)
    b = _synthetic_trace(2, q)
    result = compare_histories(a, b)
    assert result["representation_cka"] > 0.95
    assert result["prediction_agreement"] > 0.9
    assert result["technology_cosine"] > 0.999


def test_cosine_returns_none_for_empty_functional_effect():
    assert _cosine_similarity(np.zeros(5), np.ones(5)) is None


def test_same_world_seed_reproduces_hidden_target_across_population_histories():
    a = collect_history_trace(
        5, 101, steps=120, burn_in=20, stride=5, horizons=(10,)
    )
    b = collect_history_trace(
        5, 102, steps=120, burn_in=20, stride=5, horizons=(10,)
    )
    common, ia, ib = np.intersect1d(
        a.times, b.times, assume_unique=True, return_indices=True
    )
    assert len(common) >= 10
    assert a.physics_signature == b.physics_signature
    np.testing.assert_allclose(a.targets[ia], b.targets[ib], atol=0.0, rtol=0.0)
