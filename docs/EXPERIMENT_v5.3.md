# v5.3 — Exploratory dose-response for recurrent-state plasticity

## Motivation

v5.2 produced a mixed but informative result.

State-plastic agents exceeded the frozen recurrent-reservoir carrier fraction in all 8/8 fresh histories:

- mean carrier excess vs frozen: +0.0562;
- one-sided paired sign-test p = 0.0039.

However, the preregistered experiment remained negative because state plasticity beat the historical output-only learner in only 3/8 histories, and mean harvest was substantially lower:

- mean carrier excess vs output-only: +0.0296, but p = 0.855;
- mean harvest difference vs output-only: -199;
- mean harvest difference vs frozen: -443.

The interpretation is not E1. The fixed state-plasticity rate can generate additional observer-decodable predictive structure, but that structure is not reliably superior to the existing learner and is maladaptive at the tested rate.

The next step is therefore a **parameter-discovery experiment**, not another claim experiment.

## Frozen exploratory grid

World: W11

Discovery population histories: A89–A92

All conditions use:

- resource-wave strength 1.5;
- generic context features enabled;
- 1200 steps;
- burn-in 200;
- observer stride 2;
- future forcing horizons 10, 35, 70;
- active-obstacle fraction 0.75;
- standard turnover profile.

Controls:

- frozen recurrent reservoir;
- historical output-only learner.

State-plasticity rates:

- 0.0001
- 0.0003
- 0.0007
- 0.0015
- 0.0030

The v5.2 rate is 0.0015.

## Discovery outputs

For every rate:

- mean carrier fraction;
- mean total harvest;
- mean final population;
- mean generation depth;
- carrier excess vs frozen;
- carrier excess vs output-only;
- harvest excess vs frozen;
- harvest excess vs output-only.

The representation/fitness Pareto front is also reported.

## Rate-selection rule

A rate is **admissible for later prospective replication** only if:

1. its mean carrier fraction exceeds both the frozen and output-only means; and
2. its mean harvest is at least the output-only mean.

If multiple rates satisfy both constraints, select the **smallest** rate.

This rule is frozen before observing A89–A92 and prevents selecting a high-plasticity setting merely because it maximises one attractive metric while damaging ordinary fitness.

## Claim boundary

v5.3 is exploratory parameter discovery.

No p-value from this grid, no Pareto-front membership, and no selected rate can establish E1. Any selected rate must be frozen and tested prospectively on population seeds not used in v5.3.
