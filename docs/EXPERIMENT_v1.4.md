# v1.4 screening note — causal interdependence and longer-history scan

No new agent capability or objective was introduced. v1.4 adds only observer-side causal
role ablation plus a pure line-of-sight engine optimization.

## Engine acceleration

The exact line-of-sight geometry now uses a bounding-box rejection before the same exact
point-to-segment calculation. In a 120-step profile, runtime fell from ~3.95 s to ~1.55 s
(~2.5x), allowing more evolutionary history without changing world laws or agent inputs.

## Functional role ablation

Five worlds were screened at step 900. Behaviourally identified roles were removed only in
cloned analysis branches and compared with age/energy-matched random removals. No candidate
functional interdependence survived. Where a large role existed it was usually harvest-dominant;
removing it did not reduce the remaining population's per-agent-step productivity beyond the
matched null. Therefore current behavioural diversity is not evidence of division of labour.

## Longer longitudinal scan

Three worlds were run for 1800 steps with the permutation-null signalling criterion.
Seeds 0 and 1 produced windows labelled `cross_generation_signalling` together with persistent
behavioural differentiation; seed 2 did not produce a communication candidate and declined to
population 3.

These labels remain candidate discovery only.

## 2x2 causal communication autopsy

For seeds 0 and 1, at 800 steps, the same initial seed was rerun under private-information
ON/OFF x readable-communication ON/OFF with signal costs preserved when censored.

Harvest difference-in-differences:

- seed 0: +21.32
- seed 1: +34.11

Population DiD was 0 for both seeds. Birth DiD was +2 for seed 0 and 0 for seed 1.

This is directionally interesting: readable communication appears less harmful / more useful
when information is spatially private. However, receiver-action uptake did not persist in the
final 100-step window (seed 0 showed negative excess over the shuffled-payload null; seed 1 had
insufficient receiver rows). Therefore v1.4 does **not** claim emergent language.

The correct interpretation is a reproducible-looking ecological interaction worth larger-seed
replication, while the mechanistic criterion for language remains unmet.
