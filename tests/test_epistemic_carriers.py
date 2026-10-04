import numpy as np

from latent_worlds.epistemic_carriers import (
    CarrierRows,
    _block_bootstrap_lower,
    audit_carrier,
)


def _carrier(signal: bool, seed: int = 4) -> CarrierRows:
    rng = np.random.default_rng(seed)
    n = 220
    t = np.arange(n)
    z1 = np.sin(t / 13.0)
    z2 = np.cos(t / 19.0)
    y = np.column_stack([
        0.8 * z1 - 0.3 * z2,
        -0.2 * z1 + 0.9 * z2,
    ])
    raw = rng.normal(size=(n, 11))
    hidden = rng.normal(0, 0.04, size=(n, 12))
    if signal:
        hidden[:, 0] += z1
        hidden[:, 1] += z2
    return CarrierRows(
        agent_id=12,
        generation=2,
        times=list(range(n)),
        raw=[row for row in raw],
        hidden=[row for row in hidden],
        targets=[row for row in y],
    )


def test_block_bootstrap_detects_consistently_positive_improvement():
    values = np.linspace(0.1, 0.5, 80)
    lower = _block_bootstrap_lower(values, block=8, resamples=199, seed=3)
    assert lower is not None
    assert lower > 0.0


def test_carrier_audit_detects_hidden_predictive_value():
    result = audit_carrier(_carrier(True))
    assert result is not None
    assert result["raw_plus_hidden_nrmse"] < result["raw_nrmse"]
    assert result["predictive_gain"] > 0.3
    assert result["bootstrap_lower_95"] > 0.0
    assert result["carrier_candidate"]


def test_carrier_audit_rejects_hidden_noise():
    rows = _carrier(False, seed=11)
    # Make contemporaneous raw state genuinely informative so hidden noise cannot
    # win merely because the baseline is weak.
    targets = np.asarray(rows.targets)
    for i, row in enumerate(rows.raw):
        row[0] = targets[i, 0]
        row[1] = targets[i, 1]
    result = audit_carrier(rows)
    assert result is not None
    assert result["predictive_gain"] < 0.0
    assert not result["carrier_candidate"]
