
"""Observer-side pre-transition prediction utilities.

No function in this module is imported by agent controllers.  The purpose is to
test whether a later direct-causal communication transition can be forecast from
measurements collected before the transition.

The default model is deliberately simple: standardized L2-regularized logistic
regression fit by deterministic gradient descent.  This avoids opaque model
capacity when sample sizes are small.
"""
from __future__ import annotations
import math
import numpy as np

DEFAULT_FEATURES = (
    "population", "births", "deaths", "total_harvest", "broadcasts",
    "signal_receptions", "broadcast_environment_r2", "receiver_action_r2",
    "mean_signal_input_sensitivity", "signal_generational_span",
    "private_information_index", "hidden_source_count",
)

def matrix(rows, features=DEFAULT_FEATURES):
    X=np.asarray([[0.0 if r.get(k) is None else float(r.get(k,0.0)) for k in features] for r in rows],dtype=float)
    y=np.asarray([int(r["label"]) for r in rows],dtype=int)
    return X,y

def _standardize_fit(X):
    mu=X.mean(axis=0)
    sd=X.std(axis=0)
    sd=np.where(sd<1e-12,1.0,sd)
    return (X-mu)/sd,mu,sd

def fit_ridge_logistic(X,y,l2=.35,steps=2500,lr=.04):
    X=np.asarray(X,dtype=float); y=np.asarray(y,dtype=float)
    Z,mu,sd=_standardize_fit(X)
    # Intercept is not penalized.
    w=np.zeros(Z.shape[1],dtype=float)
    b=0.0
    # Class balancing is fixed in advance because positive transitions are rare.
    n1=max(1.0,float((y==1).sum())); n0=max(1.0,float((y==0).sum()))
    sw=np.where(y==1,0.5/n1,0.5/n0)
    for _ in range(int(steps)):
        z=Z@w+b
        p=1.0/(1.0+np.exp(-np.clip(z,-40,40)))
        err=(p-y)*sw
        gw=Z.T@err + float(l2)*w/max(1,len(y))
        gb=float(err.sum())
        w-=float(lr)*gw
        b-=float(lr)*gb
    return {"w":w,"b":b,"mu":mu,"sd":sd}

def predict_proba(model,X):
    X=np.asarray(X,dtype=float)
    Z=(X-model["mu"])/model["sd"]
    z=Z@model["w"]+model["b"]
    return 1.0/(1.0+np.exp(-np.clip(z,-40,40)))

def roc_auc(y,score):
    """Tie-aware Mann-Whitney ROC AUC without sklearn."""
    y=np.asarray(y,dtype=int); score=np.asarray(score,dtype=float)
    pos=score[y==1]; neg=score[y==0]
    if len(pos)==0 or len(neg)==0: return None
    wins=0.0
    for a in pos:
        wins += float(np.sum(a>neg)) + 0.5*float(np.sum(a==neg))
    return wins/(len(pos)*len(neg))

def leave_one_out_scores(rows,features=DEFAULT_FEATURES,l2=.35):
    X,y=matrix(rows,features)
    out=np.zeros(len(rows),dtype=float)
    for i in range(len(rows)):
        mask=np.ones(len(rows),dtype=bool); mask[i]=False
        m=fit_ridge_logistic(X[mask],y[mask],l2=l2)
        out[i]=predict_proba(m,X[i:i+1])[0]
    return {
        "probabilities":out.tolist(),
        "roc_auc":roc_auc(y,out),
        "labels":y.tolist(),
        "features":list(features),
    }

def trajectory_features(series):
    """Simple early-warning features from a scalar observer time series.

    Useful for testing attractor-transition hypotheses: level, slope, variance,
    and lag-1 autocorrelation.  Agents never receive these quantities.
    """
    x=np.asarray(list(series),dtype=float)
    if len(x)==0:
        return {"level":0.0,"slope":0.0,"variance":0.0,"lag1_autocorrelation":0.0}
    t=np.arange(len(x),dtype=float)
    slope=0.0 if len(x)<2 else float(np.polyfit(t,x,1)[0])
    var=float(np.var(x))
    ac=0.0
    if len(x)>=3 and np.std(x[:-1])>1e-12 and np.std(x[1:])>1e-12:
        ac=float(np.corrcoef(x[:-1],x[1:])[0,1])
    return {"level":float(x[-1]),"slope":slope,"variance":var,"lag1_autocorrelation":ac}
