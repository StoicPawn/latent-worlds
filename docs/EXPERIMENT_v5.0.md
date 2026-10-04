# v5.0 — Ecological value-of-foresight audit

## Why this experiment exists

v4.9 failed to show that the hidden resource-wave ecology selected predictive internal state beyond the frozen recurrent-reservoir null.

Before changing wave strength, travel speed, or any other ecological parameter, v5.0 asks a prior design question:

**Would perfect knowledge of the future ecology actually improve ordinary energetic return relative to an equally capable planner that only knows the current ecology?**

If the answer is no or only marginally yes, then failure of evolutionary selection is unsurprising and parameter tuning would be poorly motivated.

## Observer-only assay

No agent is simulated for cognition and no simulation rule is changed.

At a canonical set of positions and times, two ideal route choosers consider the same complete set of resource patches and the same movement/metabolic costs.

### Myopic chooser

Ranks patches by their value at the decision time.

### Foresight chooser

Ranks patches by their value at its own arrival time.

Both choices are then scored by the energetic value actually available at arrival.

The foresight chooser therefore differs from the myopic chooser in exactly one respect: access to future ecological state.

## Route value

For each patch, realized route value includes:

- expected one-harvest gross energetic return;
- temperature/radiation yield law;
- material-arrangement multiplier;
- resource-wave multiplier;
- movement cost;
- basal metabolism during travel;
- harvest cost.

The assay does not model competition or resource depletion. It is an affordance upper-bound diagnostic, not a population fitness experiment.

## Exploratory grid

World: W11

Wave strengths:

- 0.0
- 0.75
- 1.5
- 2.5
- 4.0

Representative movement speeds:

- 0.6
- 1.0
- 1.4

Decision times run from 0 to 1200 in steps of 20 over a 7 x 7 canonical origin grid.

The v4.9 treatment corresponds to wave strength 1.5.

## Reported quantities

For every cell:

- mean realized value under myopic choice;
- mean realized value under foresight choice;
- mean and median foresight advantage;
- 90th percentile foresight advantage;
- fraction of decisions with positive foresight value;
- fraction of decisions where foresight chooses a different patch;
- mean relative energetic advantage;
- mean travel horizon of the foresight choice.

## Interpretation

v5.0 is explicitly exploratory.

Its role is to identify whether the current world construction contains a meaningful causal opportunity for anticipation.

A future confirmatory evolutionary experiment must use new population seeds and freeze its ecological parameters before observing those outcomes.

No v5.0 result can support a claim about agent cognition, representation, knowledge, science, or historical contingency.
