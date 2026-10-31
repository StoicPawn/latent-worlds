"""Scientific guardrails for individual matched-time exchange controls."""
import sys
from pathlib import Path
import numpy as np

MODULE_DIR = Path(__file__).resolve().parents[1] / "experiments/civitas_zero/synchrony"
sys.path.insert(0, str(MODULE_DIR))
from individual_audit import other_agent_exchange, leave_one_out_mean


def test_other_agent_hidden_is_never_the_own_hidden_when_group_size_two():
    times = np.repeat(np.arange(25), 2)
    h = np.arange(len(times) * 3, dtype=float).reshape(-1, 3)
    swapped = other_agent_exchange(h, times)
    assert np.array_equal(swapped[0], h[1])
    assert np.array_equal(swapped[1], h[0])
    for t in np.unique(times):
        idx = np.flatnonzero(times == t)
        assert not np.array_equal(swapped[idx[0]], h[idx[0]])
        assert sorted(map(tuple, swapped[idx])) == sorted(map(tuple, h[idx]))


def test_leave_one_out_mean_excludes_self_and_preserves_time():
    t = np.repeat(np.arange(30), 3)
    h = np.arange(len(t), dtype=float).reshape(-1, 1)
    m = leave_one_out_mean(h, t)
    assert m[0, 0] == (h[1, 0] + h[2, 0]) / 2
    assert m[1, 0] == (h[0, 0] + h[2, 0]) / 2
    for q in np.unique(t):
        idx = np.flatnonzero(t == q)
        for i in idx:
            other = [j for j in idx if j != i]
            assert np.isclose(m[i, 0], h[other, 0].mean())


def test_only_one_survivor_cannot_be_claimed_a_cross_individual_control():
    t = np.arange(10)
    h = np.ones((10, 2), dtype=float)
    assert np.all(other_agent_exchange(h, t) == 0)
    assert np.all(leave_one_out_mean(h, t) == 0)
