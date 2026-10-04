# v5.2 — Recurrent-state plasticity under forecast pressure

## Motivation

v5.0 established that the resource-wave ecology contains a large energetic value of foresight. At the v4.9 treatment (wave strength 1.5, speed 1.0), perfect foresight improves mean route value by about 65% and changes the preferred patch in about 78% of decisions.

v5.1 then tested whether the failure to select predictive representation was caused simply by missing generic context. Adding normalized x/y position and previous harvest/probe yield did **not** improve the selected-representation excess:

- mean carrier-fraction interaction: -0.0413;
- paired wins: 4/8;
- one-sided sign-test p: 0.637.

The remaining architectural bottleneck is explicit in the current recurrent controller: lifetime reward-modulated learning changes `W_out`, but the input and recurrent weights that generate hidden state do not learn during the organism's lifetime.

v5.2 tests a generic state-plasticity mechanism without supplying any prediction target, hidden-law label, truth signal, or science-specific objective.

## Intervention

A new default-off switch is added:

`recurrent_state_plasticity_enabled`

When disabled, the historical controller is unchanged.

When enabled, the recurrent controller maintains action-credit eligibility traces for `W_in` and `W_rec`. The trace is computed through the selected output row and the derivative of the current recurrent state. The same scalar reward advantage already used for output plasticity modulates these traces.

The mechanism is therefore generic reward-modulated recurrent plasticity. It can in principle shape memory for locomotion, feeding, manipulation, communication, or any other rewarded behaviour. It has no concept of forecasting or science.

## Frozen design

World: **W11**

Fresh population histories: **A81–A88**

Common settings:

- resource-wave strength 1.5;
- generic context features enabled;
- 1200 steps;
- burn-in 200;
- observer stride 2;
- future forcing horizons 10, 35, 70;
- minimum 80 observations per carrier;
- information level 0.35;
- signal cost 0.03;
- active-obstacle fraction 0.75;
- standard turnover profile.

Each seed is run in three conditions.

### Frozen reservoir

- lifetime recurrent learning OFF;
- recurrent weight inheritance OFF;
- state plasticity OFF.

### Output-only learning

- historical lifetime `W_out` plasticity ON;
- recurrent weight inheritance ON;
- state plasticity OFF.

### State-plastic learning

- output plasticity ON;
- recurrent weight inheritance ON;
- reward-modulated `W_in` and `W_rec` plasticity ON.

All three conditions receive the same generic context inputs.

## Primary endpoints

Two preregistered paired contrasts are required:

1. carrier fraction(state-plastic) - carrier fraction(output-only);
2. carrier fraction(state-plastic) - carrier fraction(frozen).

## Frozen decision rule

Support for **selected state plasticity** requires all four conditions:

- positive mean state-minus-output carrier-fraction difference;
- one-sided paired sign-test p <= 0.05 for state vs output-only;
- positive mean state-minus-frozen carrier-fraction difference;
- one-sided paired sign-test p <= 0.05 for state vs frozen.

With eight non-tied histories, 7/8 positive differences are sufficient for each sign-test threshold; 6/8 are not.

This intentionally prevents a result from being called positive merely because state plasticity beats one weak comparator.

## Secondary endpoints

Reported descriptively:

- harvest difference vs output-only;
- harvest difference vs frozen;
- population;
- generation depth;
- maximum/median predictive gain.

They cannot rescue a failed primary endpoint.

## Claim boundary

A positive v5.2 result would show that generic reward-modulated recurrent plasticity can causally enrich future-physics representation beyond both the historical output-only learner and a frozen recurrent reservoir.

It would be a discovery-level E1 mechanism result only. Independent prospective replication would still be required before claiming E1, and E2–E6 would remain open.
