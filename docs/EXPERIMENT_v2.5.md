# v2.5 — North Star branch: spontaneous epistemic transition

## Target
Can a population that is selected only for survival spontaneously become a system that discovers and accumulates true predictive knowledge about hidden laws of its universe?

This branch deliberately does **not** add scientist agents, epistemic rewards, hypothesis tokens, truth labels, experiment objectives, or privileged law access.

## Pre-registered epistemic ladder
A claim advances only if all earlier levels are passed.

- **E0 — exploitation:** behaviour covaries with hidden physics and improves fitness.
- **E1 — representation:** internal state predicts held-out future latent physics beyond contemporaneous surface observations.
- **E2 — collective excess:** population state predicts latent physics better than any individual representation under matched information budgets.
- **E3 — causal dependence:** censoring naturally available social/external-memory channels removes the collective excess while preserving their energetic costs where possible.
- **E4 — cumulative epistemic inheritance:** predictive structure survives replacement of its original carriers and improves across generations.
- **E5 — spontaneous experimentation:** interventions that are not intrinsically rewarded become systematically selected because their downstream information changes later action and fitness; this must be established observer-side by counterfactual controls.
- **E6 — law generalisation:** the acquired structure transfers to held-out spatial/temporal regimes or related worlds in ways incompatible with memorised local policy.

The headline 'spontaneous science' is reserved for a system reaching at least E5–E6 with replication and ablations.

## New observer-side assay
`epistemic_transition.py` decodes the world's future latent forcing at horizon h from:

1. current surface observations (raw baseline),
2. one recurrent agent's internal state,
3. a permutation-invariant summary of the whole population's recurrent states.

Evaluation is temporally held out. The target is the simulator's hidden forcing and is never exposed to agents.

A paired causal assay reruns the same world/population seeds with readable social traces versus communication+marks censored.

## Pilot (6 independent world/population pairs, 700 steps, h=35)
No E2 candidate survived the strict criterion. Several worlds showed that recurrent state contains information about future forcing beyond a raw instantaneous baseline, but the population summary did not consistently beat the individual representation. Therefore there is **no current evidence for collective knowledge**.

This negative result is useful: the North Star branch begins with a falsifiable baseline rather than defining collective knowledge after observing a suggestive run.

## Next
Improve the *observer*, not the agents: test information-budget-matched, permutation-invariant decoders and cross-world held-out evaluation. Only after E2 appears reproducibly should E3–E6 be run.
