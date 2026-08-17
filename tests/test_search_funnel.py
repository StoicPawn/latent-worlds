import pytest
from latent_worlds.search_funnel import SearchFunnel, wilson_interval

def test_wilson_bounds_are_valid():
    lo, hi = wilson_interval(1, 10)
    assert 0 <= lo <= 0.1 <= hi <= 1

def test_funnel_requires_monotonic_counts():
    with pytest.raises(ValueError):
        SearchFunnel(10, 5, 6, 2, 1, 0).summary()

def test_funnel_summary():
    s = SearchFunnel(64, 7, 1, 0, 0, 0).summary()
    assert s["late_communication"]["count"] == 7
    assert s["direct_removal"]["fraction_of_screened"] == pytest.approx(1/64)
