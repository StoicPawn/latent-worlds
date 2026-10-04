# v4.9 — Forecast-pressure factorial experiment

## Motivation

v4.8 showed that the individual predictive-carrier signal discovered in v4.7 is not enriched by the current learning/evolutionary regime relative to a frozen recurrent reservoir.

Across fresh A55–A64 histories:

- mean carrier fraction, full: 0.1242;
- mean carrier fraction, frozen: 0.1221;
- mean difference: +0.0022;
- paired wins: 6/10;
- one-sided sign-test p: 0.377.

Therefore v4.7 does not support selected predictive representation. The current ecology appears to provide too little selective pressure for internal future-world modelling.

The next intervention follows the project's governing rule: **change the world, not the civilisation**.

## Primary question

**If ordinary survival becomes more dependent on anticipating a hidden quasi-periodic resource landscape, does learning/evolution enrich predictive internal representations beyond a frozen recurrent reservoir?**

No reward for prediction, information, truth, model accuracy, curiosity, discovery, or science is introduced.

## World-side intervention

v4.9 introduces an optional hidden spatiotemporal resource-quality field.

The field:

- is generated from the same hidden oscillator family that drives climate;
- gives each resource patch a deterministic spatial phase offset;
- changes the energy yield obtainable from a patch over time;
- remains strictly positive;
- is normalized to mean 1 across all patches at every time step;
- does not change the total nominal resource regrowth process;
- is invisible as a named variable to agents.

The control value is resource-wave strength 0.0, which is an exact no-op.

The treatment value is frozen at **1.5** before observing A65–A72.

Because high-yield regions move in a predictable but multi-periodic way, an agent can in principle benefit by moving toward future opportunities before they become locally obvious. This is an ecological advantage for anticipation, not an epistemic reward.

## Frozen 2x2 design

World seed: **W11**

Fresh population histories: **A65–A72**

Common settings:

- 1200 steps;
- burn-in 200;
- observer stride 2;
- future forcing horizons 10, 35, 70;
- minimum 80 observations per carrier;
- information level 0.35;
- signal cost 0.03;
- active-obstacle fraction 0.75;
- standard turnover profile.

Each population seed is run under four conditions:

1. control ecology + full recurrent learning/inheritance;
2. control ecology + frozen recurrent reservoir;
3. resource-wave ecology + full recurrent learning/inheritance;
4. resource-wave ecology + frozen recurrent reservoir.

The frozen controller condition is exactly the v4.8 null: recurrent hidden dynamics remain active, but lifetime recurrent weight learning and recurrent controller-weight inheritance are disabled.

## Primary endpoint: difference in differences

For each condition:

carrier fraction = carrier candidates / eligible carriers.

Within each ecology:

selection excess = carrier fraction(full) - carrier fraction(frozen).

The primary per-seed causal interaction is:

interaction = selection excess(resource wave) - selection excess(control).

This asks whether the world-side forecast pressure specifically makes learning/inheritance add predictive representation beyond the random-reservoir effect.

## Frozen decision rule

Forecast-pressure support requires both:

1. positive mean interaction across A65–A72; and
2. one-sided paired sign-test p <= 0.05 across non-tied histories.

With eight non-tied histories, 7/8 positive interactions is sufficient for the sign-test threshold; 6/8 is not.

The rule is frozen before observing any A65–A72 result.

## Secondary endpoints

The experiment also reports:

- total-harvest interaction;
- final population;
- births/deaths;
- generation depth;
- maximum and median individual predictive gains.

These are descriptive secondary endpoints and cannot rescue a failed primary endpoint.

## Interpretation

A positive result would support an E1-selection statement:

> A general ecological need for anticipation causally enriches internal predictive state beyond what arises from a fixed random recurrent reservoir.

It would **not** establish:

- collective knowledge;
- non-genetic cumulative inheritance;
- active experimentation;
- causal-law recovery;
- technology;
- spontaneous science;
- Stage-II universality or path dependence.

If the primary result is negative, the intervention is retained as another failed ecological condition rather than tuned post hoc. The next step would be to diagnose whether the failure comes from insufficient forecast value, insufficient travel-time constraint, or insufficient heritable capacity to exploit the opportunity.
