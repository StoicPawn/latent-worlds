import numpy as np
from latent_worlds.epistemic_transition import _ridge_fit_predict, _gain, run_epistemic_assay

def test_ridge_decoder_recovers_linear_relation():
    x=np.linspace(-2,2,100)[:,None]; y=1.5+2*x[:,0]
    p=_ridge_fit_predict(x[:70],y[:70],x[70:])
    assert np.sqrt(np.mean((p-y[70:])**2)) < .02

def test_gain_direction():
    assert _gain(2.0,1.0)==.5
    assert _gain(1.0,2.0)==-1.0

def test_epistemic_assay_smoke():
    r=run_epistemic_assay(0,0,steps=90,horizon=10)
    assert r.samples > 20
    assert r.horizon==10
