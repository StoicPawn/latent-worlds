# v5.1 — Generic context-access ablation under forecast pressure

## Motivation

v4.9 showed no enrichment of selected predictive representation under the hidden resource-wave ecology.

A subsequent observer-side value-of-foresight audit indicates that the v4.9 ecology can, in principle, make future information energetically valuable. This shifts attention to the generic recurrent substrate.

Inspection of the publication mainline identified a concrete accessibility bottleneck: `Observation` already contains absolute position and the previous harvest/probe yield, but the `RecurrentAgent` historically discards both when constructing its recurrent input.

The v4.9 resource-wave depends jointly on time and spatial phase. Therefore a controller lacking absolute position and direct outcome feedback may be unable to learn the relevant regularity even though the world makes anticipation valuable.

v5.1 tests this bottleneck without introducing any science-specific objective or representation.

## Intervention

A new configuration switch is added:

`recurrent_context_features_enabled`

Its default is **false**, preserving all prior experiments.

When enabled, the recurrent input receives three additional generic channels:

1. normalized absolute x position;
2. normalized absolute y position;
3. previous harvest/probe yield.

No label for resource-wave phase, future reward, hidden forcing, prediction error, truth, model quality, discovery, or science is provided.

The controller architecture, hidden-state width, action space, reward, reproduction rule, world physics, communication substrate, and learning algorithm remain unchanged.

## Frozen design

World: **W11**

Fresh population histories: **A73–A80**

Resource-wave strength: **1.5**

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

Each seed is run in four conditions:

1. legacy recurrent input + full learning/inheritance;
2. legacy recurrent input + frozen recurrent reservoir;
3. enriched generic context + full learning/inheritance;
4. enriched generic context + frozen recurrent reservoir.

The carrier audit now conditions its observer baseline on current outcome feedback as well as current position, local physics, resource geometry, population, energy, and clock. Therefore hidden state cannot receive E1 credit merely for copying the newly exposed contemporaneous channels.

## Primary endpoint

Within each input condition:

selection excess = carrier fraction(full) - carrier fraction(frozen).

Per-seed interaction:

interaction = selection excess(context) - selection excess(legacy).

## Frozen decision rule

Support for **generic context enrichment** requires:

1. positive mean interaction across A73–A80; and
2. one-sided paired sign-test p <= 0.05 across non-tied histories.

With eight non-tied histories, 7/8 positive interactions is sufficient; 6/8 is not.

## Secondary endpoints

Reported descriptively:

- total-harvest interaction;
- population;
- births/deaths;
- generation depth;
- maximum and median predictive gain.

These cannot rescue a failed primary endpoint.

## Claim boundary

A positive result would identify missing generic spatial/outcome observability as a causal bottleneck for selected predictive representation.

It would not establish collective knowledge, cumulative cultural inheritance, experimentation, law discovery, technology, spontaneous science, or Stage-II historical contingency.
