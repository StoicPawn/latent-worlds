
import numpy as np
from latent_worlds.pretransition_prediction import (
    fit_ridge_logistic,predict_proba,roc_auc,leave_one_out_scores,trajectory_features
)

def test_logistic_learns_simple_separator():
    X=np.asarray([[-2.],[-1.],[1.],[2.]])
    y=np.asarray([0,0,1,1])
    m=fit_ridge_logistic(X,y,l2=.05,steps=1500)
    p=predict_proba(m,X)
    assert p[0] < p[-1]
    assert roc_auc(y,p) == 1.0

def test_loo_has_one_score_per_history():
    rows=[
        {"population":1,"label":0},
        {"population":2,"label":0},
        {"population":9,"label":1},
        {"population":10,"label":1},
    ]
    r=leave_one_out_scores(rows,features=("population",),l2=.05)
    assert len(r["probabilities"]) == 4
    assert 0 <= r["roc_auc"] <= 1

def test_trajectory_features_detect_positive_slope():
    r=trajectory_features([1,2,3,4])
    assert r["slope"] > 0
    assert r["variance"] > 0
