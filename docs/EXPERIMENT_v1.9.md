# Experiment v1.9 — Counterfactual semantic autopsy

## Principle
No agent faculty, reward, sensor, action, or world law is added in v1.9.  The
release adds observer-side interventions for an already identified candidate
population/world pair (`world_seed=1`, `agent_seed=1`).

The central question is narrower than "has language emerged?":

> Does changing only the received signal content, while holding receiver state,
> local world state, and stochastic draw fixed, causally change receiver action?

## Payload clusters
Broadcast payloads in the reference trajectory are clustered using only their
3-dimensional signal vectors.  The candidate produced four payload clusters
(best silhouette about 0.44).  Cluster membership has modest but non-zero
observer-side association with environmental context, strongest for local
resource richness (R² about 0.20).

## Within-receiver counterfactual assay
For every sampled reception event, three deep-copied receivers see exactly the
same non-signal observation and RNG state:

1. the real payload;
2. the centroid of the payload's own cluster (within-cluster placebo);
3. the centroid of the farthest other signal cluster (cross-cluster substitution).

Counterfactual decisions never alter the live simulation trajectory.

### Candidate, t=250..700
899 reception events were assayed.

- founders (generation 0): cross-vs-within excess action-kind change ≈ +0.028,
  paired exact p ≈ 0.0018;
- descendants (generation 1): excess ≈ +0.083,
  paired exact p ≈ 3.6e-12;
- intergenerational amplification ≈ +0.055.

At later windows, generation-1 excess remains large:

- t=400..900: ≈ +0.088 (p ≈ 1.2e-7);
- t=600..1100: ≈ +0.11 (p ≈ 0.0034).

Almost all sampled receptions are cross-lineage, so this is not merely a
within-family code.

## Training-placebo control
The exact same world/population was re-run with signal payloads scrambled during
evolution.  Message opportunities, locations, ranges, costs, and marginal
payload distribution remain; only sender-state/content pairing is broken.

For t=250..700:

- readable trajectory: overall semantic excess ≈ +0.057, paired p ≈ 1.2e-14,
  intergenerational amplification ≈ +0.055;
- scrambled trajectory: overall semantic excess ≈ +0.008, paired p = 0.125,
  intergenerational amplification ≈ +0.002.

Thus the descendant amplification largely disappears when meaningful
sender-state/content structure is destroyed during evolution.

## Interpretation
This is not sufficient to claim language, compositionality, symbolic reference,
or stable cultural fixation.  It is, however, a stronger mechanistic candidate
than earlier correlational burst evidence:

- signal content matters causally for receiver action;
- the effect is stronger in descendants than founders;
- the amplification is absent under a payload-scrambled evolutionary placebo;
- the interaction is mostly across genealogical lineages.

The next falsification targets are replication across independently emerging
candidate pairs, persistence across deeper generations, and testing whether
specific signal clusters produce reproducible action/context substitutions.
