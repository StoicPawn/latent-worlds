"""No-world-rollout tests for the time-synchrony diagnostic."""
import importlib.util
from pathlib import Path
import numpy as np

SOURCE = Path(__file__).resolve().parents[1] / "experiments/civitas_zero/synchrony/within_time_exchange.py"
spec = importlib.util.spec_from_file_location("syn", SOURCE)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def test_same_time_exchange_preserves_full_time_group_distribution():
    time = np.repeat(np.arange(60), 4)
    h = np.arange(240 * 3, dtype=float).reshape(240, 3)
    exchanged = m.time_exchange(h, time, 4812)
    assert np.any(exchanged != h)
    for t in np.unique(time):
        assert sorted(map(tuple, exchanged[time == t])) == sorted(map(tuple, h[time == t]))


def test_time_mean_has_no_agent_identity():
    ts = np.repeat(np.arange(40), 3)
    h = np.arange(len(ts) * 2, dtype=float).reshape(-1, 2)
    result = m.global_time_mean(h, ts)
    for t in np.unique(ts):
        assert np.allclose(result[ts == t], np.mean(h[ts == t], axis=0))


def test_decoder_is_chronological_and_numerically_consistent():
    ts = np.repeat(np.arange(100), 4)
    phase = np.arange(100, dtype=float)
    y = np.repeat(np.column_stack([np.sin(phase / 17), np.cos(phase / 21), np.sin(phase / 7)]), 4, axis=0)
    x = np.column_stack([np.sin(ts / 17), np.cos(ts / 21), np.sin(ts / 7)])
    outcome = m.fit_temporal(x, y, ts)
    assert outcome["n_train_times"] == 70
    assert outcome["n_test_times"] == 30
    assert outcome["n_test_rows"] == 120
    assert np.isfinite(outcome["mean_nrmse"])


def test_truth_per_time_is_the_same_for_all_individuals():
    ts = np.repeat(np.arange(41), 5)
    y = np.repeat(np.arange(41, dtype=float), 5).reshape(-1, 1)
    assert all(np.ptp(y[ts == t]) == 0 for t in np.unique(ts))


def test_time_shift_breaks_shared_timing_in_nonconstant_fixture():
    ts = np.repeat(np.arange(80), 5)
    h = np.column_stack([np.sin(ts / 8), np.cos(ts / 8)])
    shifted = m.lag_misaligned_mean(h, ts)
    assert np.mean((shifted - h) ** 2) > 0.1


def test_lagged_null_never_uses_a_future_state():
    times = np.repeat(np.arange(100), 3)
    hidden = np.column_stack((times.astype(float), np.zeros(len(times))))
    lag = m.lag_misaligned_mean(hidden, times)
    assert np.all(lag[:, 0] <= times)
    assert np.all(lag[times >= 40, 0] < times[times >= 40])
