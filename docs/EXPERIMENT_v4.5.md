# v4.5 — Same-physics epistemic contingency diagnostic

## Motivation

The unified North Star now separates two questions:

1. can spontaneous science emerge under ordinary survival/reproduction selection?
2. if it emerges repeatedly under the same physics, how universal is the resulting science?

The second question must not be answered before the first. v4.4 remains negative on the strongest adaptive-replication target: mechanism and adaptive value did not coincide in any of the 75 frozen local cells. Therefore v4.5 does **not** promote the project to Stage II.

Instead, v4.5 builds and prospectively tests the observer-side measurement layer that Stage II will require. The objective is to determine whether independent population histories under one exactly fixed hidden physics produce predictive internal structure that can be compared without assuming common neuron labels, human concepts, named theories, or predefined technologies.

## Primary methodological question

**Can we compare independent epistemic histories under identical physics using representation- and function-level metrics that are invariant to arbitrary internal labels?**

This is a measurement-validation experiment, not an alternative-science claim.

## Frozen design

The experiment is committed before observing A25–A34 outcomes.

- hidden world: **W11**
- population histories: **A25–A34**
- steps: **1200**
- burn-in: **200**
- observer sampling stride: **5**
- future-law horizons: **10, 35, 70**
- information level: **0.35**
- signal cost: **0.03**
- turnover profile: unchanged standard turnover profile
- active-obstacle fraction: **0.75**

A25–A34 were not used in the v4.0–v4.4 discovery/confirmation sequence.

No agent capability, reward, sensor, action, learning rule, mutation operator, inheritance mechanism, communication primitive, object semantics, or physical law is added or modified.

## Fixed-physics verification

Every history is initialized with the same world seed W11 and a different population seed.

The observer records the full hidden-law parameter signature. A campaign aborts if two histories differ in hidden physics.

Future forcing targets are evaluated at matched world times. Pairwise analysis records the maximum absolute target mismatch; under a valid same-physics campaign this should be zero up to numerical identity.

## Epistemic trace

At each observer sample, the evaluator records:

- contemporaneous surface-physics summary;
- mean recurrent hidden state of the living population;
- distributional population hidden-state summary;
- future hidden forcing at the preregistered horizons;
- population size and generation depth.

None of these observer-side diagnostics enter agent observations or fitness.

### Predictive representation

Within each history, a past-only ridge decoder predicts future hidden forcing from:

1. contemporaneous surface observations;
2. collective recurrent population state.

The diagnostic quantity is normalized out-of-sample RMSE and the gain of collective internal state over the raw surface baseline.

A 'predictive_representation_candidate' is a deliberately weak label. It requires at least 80 observer samples and >3% predictive gain over raw observations. It is **not** an E2, E5, E6, or spontaneous-science claim.

## Cross-history representational comparison

Direct neuron-by-neuron comparison is invalid because independently evolved recurrent networks may permute or rotate their hidden coordinates.

v4.5 therefore uses **linear centered-kernel alignment (CKA)** on matched-time population hidden states.

Linear CKA is invariant to orthogonal relabelling and isotropic scale. High CKA therefore means that two histories developed similar representational geometry without requiring their hidden units to have the same identities.

This still does not prove theoretical equivalence; it is an observer-side representation diagnostic.

## Predictive functional equivalence

For each pair of histories, independent decoders are trained on the same early matched-time hidden-physics targets and evaluated on the same later targets.

The evaluator measures the normalized divergence between the two predicted target trajectories and reports prediction agreement as one divided by one plus normalized prediction divergence.

This asks whether two internal systems support similar future-world predictions even if their internal coordinates differ.

## Technology comparison without a technology tree

The final material arrangement in each history is evaluated on a fixed spatial probe grid under the same hidden matter law.

For each probe site the observer computes the effect of the final arrangement minus the effect of the initial arrangement.

The resulting vector is the history's **functional technology profile**.

Pairwise cosine similarity compares what two arrangements do rather than whether they contain the same object identities or shapes. A pair is treated as an active-technology diagnostic only when both histories have at least three successful drops and nontrivial functional effect.

Natural useful arrangements do not count as technology because the profile is measured relative to the exact initial arrangement.

## Stage-II gate

v4.5 intentionally supplies no Stage-II-eligible histories.

The convergence framework accepts a separate q2_eligible_agent_seeds list, but histories may enter it only from external preregistered evidence that they independently satisfy the project's spontaneous-science threshold.

For v4.5 the list is empty and therefore Stage-II inference is disabled.

This prevents a predictive-representation signal from being retrospectively relabelled as "science".

## Outputs

The preregistered output contains:

- per-history predictive representation metrics;
- pairwise representation CKA;
- pairwise predictive agreement;
- per-history functional technology effect;
- pairwise technology-function similarity;
- exact hidden-physics signature;
- explicit Stage-II eligibility state.

## Interpretation

Three outcomes are all useful.

1. **Little predictive structure:** Q1 remains the only relevant frontier; Stage-II instrumentation is validated but dormant.
2. **Predictive structure with strong cross-history convergence:** this identifies a potential world-forced representational attractor at a pre-scientific level.
3. **Predictive structure with cross-history divergence:** this identifies candidate path dependence in representation, but must not be called alternative science unless the histories later satisfy E5–E6 independently.

The experiment therefore prepares the new North Star without weakening the evidentiary standard of the old one.
