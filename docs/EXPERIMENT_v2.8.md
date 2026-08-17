# Experiment v2.8 — Genetic-conditioned falsification

## Question
Can the apparent non-genetic inheritance detected in v2.7 be explained by genetically inherited family-specific signal preferences?

## Why v2.7 was not enough
The v2.7 permutation null globally shuffled received variant labels. A lineage whose neural controller is genetically predisposed to receive and emit the same variant can therefore look like information copying even when the received payload has no independent hereditary effect.

## New preregistered requirement
For each receiver generation, received variant labels are permuted **within receiver genetic root**. Receiver lineage, generation, emission timing and emitted variant are preserved. A candidate autonomous inheritance channel must still show excess receive→reemission fidelity under this conditional null.

## Main falsification result
The strongest previous candidate, `world_seed=11, agent_seed=0`, fails the new test. At 700 steps:

- G0 fidelity ≈ 0.766; lineage-conditioned null ≈ 0.767; excess ≈ -0.001; p ≈ 0.92.
- G1 fidelity ≈ 0.569; conditioned null ≈ 0.576; excess ≈ -0.007; p = 1.0.
- G2 fidelity ≈ 0.858; conditioned null ≈ 0.860; excess ≈ -0.003; p = 1.0.

Thus the v2.7 replication signal is compatible with inherited lineage-specific signalling preferences rather than an autonomous second inheritance process.

The other two G2 candidates rechecked (`W0×A0`, `W0×A1`) also fail: G2 either has too few within-root informative pairs or no variation within a root.

## Information-lineage reconstruction
A conservative unique-source graph nevertheless shows substantial horizontal traffic in `W11×A0`: at 800 steps, 625 uniquely attributable transmission edges, ~67% cross genetic roots, and a large component spanning G0–G2. However, a scrambled control also forms a large interaction graph. Graph connectivity alone is therefore not evidence of inheritance.

## Interpretation
This is a deliberate falsification of the strongest v2.7 claim. The project has evidence for structured, cross-lineage communication and lineage-specific signal traditions, but **not yet for a second evolutionary system autonomous from genetic inheritance**.

The new North-Star stepping-stone criterion is therefore stricter:

1. replication with nonzero variation;
2. differential propagation;
3. G2+ depth;
4. faster-than-gene transmission;
5. fitness/content controls;
6. **received information predicts re-emission beyond genetic-root predisposition**.

Only worlds satisfying all six advance as candidates for “evolution inventing a faster evolution.”
