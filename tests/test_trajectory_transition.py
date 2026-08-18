from latent_worlds.trajectory_transition import (
    featurize_trajectory,
    trajectory_feature_names,
)


def test_featurize_trajectory_has_expected_dynamics():
    run = {
        "world_seed": 1,
        "agent_seed": 2,
        "rows": [
            {"population": 1.0, "births": 0.0},
            {"population": 2.0, "births": 1.0},
            {"population": 3.0, "births": 2.0},
            {"population": 4.0, "births": 3.0},
        ],
    }
    f = featurize_trajectory(run, series=("population", "births"))
    assert f["population__slope"] > 0
    assert f["births__variance"] > 0
    assert f["world_seed"] == 1
    assert f["agent_seed"] == 2


def test_feature_names_are_stable():
    names = trajectory_feature_names(series=("population",))
    assert names == (
        "population__level",
        "population__slope",
        "population__variance",
        "population__lag1_autocorrelation",
    )
