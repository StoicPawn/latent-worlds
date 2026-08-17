# v3.6 — Causal search for transition conditions

No agent capability, objective, reward, learning rule or communication primitive
was added.

## Motivation

The v3.5 campaign established that persistent adaptive direct-causal replication
is rare.  v3.6 asks a different question: what ecological conditions make the
W11 transition possible?

A naive scan of the existing `information_level` parameter is confounded because
changing obstacle count changes how many random draws are consumed during world
initialization, which can indirectly change resource/object realizations.

## Matched ecological intervention

`SimulationConfig.active_obstacle_fraction` now changes only how many already
generated obstacles participate in line-of-sight.  For a fixed world seed all
resources, objects, hidden physics and obstacle coordinates remain identical.
The default is 1.0, so historical simulations are unchanged.

This creates a clean causal intervention on occlusion geometry.

## W11 matched-geometry result

With the same initialized W11 world and A0 population, the direct G2 content-copy
mechanism is not monotonic in active occlusion:

- active obstacle fraction 0.00: supported; G2 copy gain ~ +0.0263, p=.01
- active obstacle fraction 0.33: unsupported; copy gain ~ -0.0057
- active obstacle fraction 0.67: unsupported; no natural G2 rebroadcast in assay
- active obstacle fraction 1.00: supported; G2 copy gain ~ +0.0285, p=.01

Thus "more occlusion produces more cultural copying" is rejected.

## W11 signal-cost result

Holding the ordinary W11 information geometry fixed, direct causal G2 copying was:

- cost 0.000: supported
- cost 0.010: unsupported
- cost 0.020: supported
- cost 0.030: supported
- cost 0.045: unsupported
- cost 0.065: unsupported

Again the relationship is non-monotonic.

A finer information-level scan likewise produced alternating supported and
unsupported regimes.  Because that older knob changes initialization RNG
consumption, those values are retained only as hypothesis-generating evidence,
not causal evidence.

## Interpretation

The current evidence argues against a one-dimensional threshold such as
"communication emerges above enough private information" or "below enough signal
cost".  W11 appears to enter and leave a content-copying regime across nearby
world-side interventions.

The working hypothesis is therefore that the transition is an attractor/basin
phenomenon created by coupled ecology, encounter structure, demographic turnover
and signalling dynamics.  This is not yet a scientific result; it is a more
specific target for the next preregistered experiments.

## Pre-transition profiling

`transition_conditions.py` adds observer-only profiles at early horizons.  These
measure population, turnover, harvest, signal traffic, early encoding/uptake,
signal sensitivity, information asymmetry and hidden-source count without
exposing any metric to agents.

Early W11 signal-cost profiles do not reveal a trivial scalar separator: broadcast
volume, neural signal sensitivity and private-information index do not individually
classify later causal-copy regimes.

This motivates multivariate prediction and matched interventions rather than
single-variable threshold claims.
