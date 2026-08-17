# Experiment v2.7 — Deep secondary evolution

## Preregistered target

Find a non-genetic information channel that satisfies Darwinian signatures **inside generation G2 or later**, not merely in aggregate:

1. replication fidelity above a within-generation permutation null;
2. non-zero imperfect copying (variation/mutation);
3. differential cross-lineage propagation among variants in the same generation;
4. transmission faster than genetic generational turnover;
5. disappearance of the deep inheritance/selection signature under payload scrambling;
6. fitness advantage of readable content over both scrambled and censored controls.

No agent capability, reward, or hidden law was added for this experiment.

## First strict candidate

The adaptive search identified `world_seed=11, agent_seed=0` under the pre-existing turnover ecology.
At 500 steps, generation G2 is communication-active and contains 234 receive→later-emission pairs.

G2 replication assay (real channel):

- fidelity ≈ 0.855
- permutation-null fidelity ≈ 0.582
- fidelity excess ≈ +0.272
- p = 0.005 (199 permutations)
- mutation rate ≈ 0.145

G2 differential propagation (cross-lineage adoptions per G2 emitter):

- variant 0: 27.5
- variant 1: 3.0
- variant 2: 10.67
- CV ≈ 0.746
- spread = 24.5

Thus variation, replication and differential propagation are simultaneously observed in G2.

The receive→same-variant re-emission median delay is 6 simulation steps versus an estimated genetic generation timescale of 250 steps (speed ratio ≈ 41.7×). In G2 specifically, the median delay is 5 steps.

## Payload-scramble control

Same world and initial population, with payload/context association destroyed during evolution:

- G2 fidelity excess ≈ +0.046
- p = 0.21
- G2 differential propagation criterion fails

Therefore the G2 Darwinian signature is not reproduced by the mere existence of a numeric communication channel.

## Fitness controls

At 500 steps:

| condition | total harvest | final population | births |
|---|---:|---:|---:|
| readable | 1835.71 | 51 | 48 |
| censored | 1759.51 | 50 | 44 |
| scrambled | 1661.38 | 43 | 46 |

Readable content therefore outperforms both controls in this candidate. This is still **one candidate**, not a general result.

## Replication status

Two additional G2-active histories tested (`W9×A0`, `W11×A2`) do not reproduce the full G2 signature. Another (`W0×A0`) shows strong G2 replication with variation but not differential propagation. Therefore v2.7 establishes a strict mechanistic candidate, not yet a replicated discovery.

## Next falsification target

Replicate the full G2 triad in independent world×population combinations and test whether the same informational variants persist into G3. Only after replication should the claim be upgraded from *candidate second evolutionary channel* toward *spontaneously emerged non-genetic evolutionary process*.
