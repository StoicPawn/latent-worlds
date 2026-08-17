# v3.7 — Can the transition be predicted before it happens?

No agent capability, objective, reward, learning rule, physical law or
communication primitive changed.

## Preregistered target

Predict the later direct same-agent causal-copy phenotype from observer-only
measurements collected at t=150, before the late-generation causal assays.

Historical labels were frozen before fitting:
positive direct-removal histories W11, W21, W63, W80 and W187; 21 previously
tested negative histories served as controls.

The feature set was fixed in advance:
population, births, deaths, harvest, broadcast count, signal receptions,
broadcast-environment R2, receiver-action R2, neural signal sensitivity,
signal generational span, private-information index and hidden-source count.

The predictor was deliberately low capacity: standardized L2-regularized logistic
regression with class balancing.

## Result

Leave-one-history-out prediction failed badly:

- ROC-AUC ~ 0.14
- average precision ~ 0.14
- balanced accuracy at 0.5 ~ 0.29

This is not evidence for an inverse biological law.  With only five positive
histories, the correct interpretation is that these coarse t=150 observer
snapshots contain no demonstrated robust predictive signature.

The largest fitted coefficients were not stable enough to support mechanistic
interpretation.  In particular, no single early scalar such as private-information
index, broadcast volume, neural signal sensitivity or early uptake separated
future transition histories.

## Consequence

The simple "critical threshold visible in an early snapshot" hypothesis is
rejected at the present sample size.

Because matched interventions in v3.6 also showed non-monotonic entry and exit
from the causal-copy regime, the next hypothesis is dynamical: transition
histories may be distinguished by *trajectories* rather than levels.

`pretransition_prediction.py` therefore adds preregistered observer-side tools for
low-capacity leave-one-out prediction and for early-warning trajectory features:
level, slope, variance and lag-1 autocorrelation.

A future positive claim requires prospective validation on unseen seeds.  No model
selected after inspecting their late outcomes may count as confirmatory evidence.
