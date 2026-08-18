from __future__ import annotations

import json
import numpy as np

from latent_worlds.causal_transmission import direct_reception_transmission_assay
from latent_worlds.pretransition_prediction import fit_ridge_logistic, predict_proba, roc_auc
from latent_worlds.replication import standard_turnover_overrides
from latent_worlds.trajectory_transition import early_trajectory, featurize_trajectory, trajectory_feature_names

# Historical labels are frozen from the v3.0-v3.7 record before this benchmark.
HISTORICAL_POSITIVES = (11, 21, 63, 80, 187)
HISTORICAL_NEGATIVES = (42, 56, 65, 70, 72, 78, 90, 104, 109, 114, 115, 117, 118, 123, 135, 143, 156, 176, 186, 192, 196)
PROSPECTIVE_SEEDS = tuple(range(202, 226))


def _rows(seeds, label=None):
    rows = []
    for seed in seeds:
        f = featurize_trajectory(early_trajectory(seed, 0))
        if label is not None:
            f["label"] = int(label)
        rows.append(f)
    return rows


def _matrix(rows, features):
    X = np.asarray([[float(r.get(k, 0.0)) for k in features] for r in rows], dtype=float)
    y = np.asarray([int(r["label"]) for r in rows], dtype=int)
    return X, y


def _loo(rows, features):
    X, y = _matrix(rows, features)
    score = np.zeros(len(rows), dtype=float)
    for i in range(len(rows)):
        keep = np.ones(len(rows), dtype=bool)
        keep[i] = False
        m = fit_ridge_logistic(X[keep], y[keep], l2=.35)
        score[i] = predict_proba(m, X[i:i+1])[0]
    return score, roc_auc(y, score)


def _direct_label(seed):
    r = direct_reception_transmission_assay(
        world_seed=int(seed), agent_seed=0, steps=650, assay_start=250,
        min_generation=2, information_level=.35, signal_cost=.03,
        config_overrides=standard_turnover_overrides(), max_events=300,
        permutations=99,
    )
    return {
        "seed": int(seed),
        "supported": bool(r.get("supported")),
        "supported_generations": list(r.get("supported_generations", ())),
    }


def main():
    features = trajectory_feature_names()
    historical = _rows(HISTORICAL_POSITIVES, 1) + _rows(HISTORICAL_NEGATIVES, 0)
    loo_score, loo_auc = _loo(historical, features)
    X, y = _matrix(historical, features)
    model = fit_ridge_logistic(X, y, l2=.35)

    prospective = _rows(PROSPECTIVE_SEEDS)
    Xp = np.asarray([[float(r.get(k, 0.0)) for k in features] for r in prospective], dtype=float)
    pp = predict_proba(model, Xp)
    ranked = sorted(
        [{"seed": int(r["world_seed"]), "score": float(p)} for r, p in zip(prospective, pp)],
        key=lambda z: z["score"], reverse=True,
    )

    # Prospective validation set is fixed from predictions alone, before outcomes.
    selected = [r["seed"] for r in ranked[:6]] + [r["seed"] for r in ranked[-6:]]
    outcomes = [_direct_label(seed) for seed in selected]
    outcome_map = {r["seed"]: r for r in outcomes}
    for r in ranked:
        if r["seed"] in outcome_map:
            r.update(outcome_map[r["seed"]])

    top = ranked[:6]
    bottom = ranked[-6:]
    top_hits = sum(bool(r.get("supported")) for r in top)
    bottom_hits = sum(bool(r.get("supported")) for r in bottom)

    result = {
        "historical_n": len(historical),
        "historical_positives": int(y.sum()),
        "historical_trajectory_loo_auc": None if loo_auc is None else float(loo_auc),
        "prospective_seed_range": [min(PROSPECTIVE_SEEDS), max(PROSPECTIVE_SEEDS)],
        "prospective_tested_top": [r["seed"] for r in top],
        "prospective_tested_bottom": [r["seed"] for r in bottom],
        "prospective_top_hits": int(top_hits),
        "prospective_bottom_hits": int(bottom_hits),
        "prospective_enrichment": float((top_hits + .5) / (bottom_hits + .5)),
        "ranked": ranked,
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
