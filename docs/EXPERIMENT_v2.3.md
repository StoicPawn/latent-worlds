# Experiment v2.3 — Deep-generation semantic search

## Constraint
No agent capability, reward, sensor, action, or physical law was added. This release improves only observer-side inference throughput and generational sampling.

## Single-pass semantic autopsy
The previous content assay simulated a candidate once to discover spontaneous signal clusters and then replayed the same world to recover reception events. v2.3 captures compact decision snapshots during the first run and evaluates counterfactual payload substitutions offline. On the canonical short assay, output statistics were identical while runtime fell from about 5.0 s to 2.75 s (~1.8x faster).

## Generation-stratified sampling
A global event cap was biased toward G0/G1 because early generations dominate reception counts. v2.3 adds an observer-only reservoir sampler with an independent RNG and a per-generation quota. This allows equal-depth interrogation of G0, G1, G2, and G3 without changing evolution.

## Corrected transfer criterion
A candidate is no longer called transfer-supported merely because real amplification is less negative than scrambled amplification. Real intergenerational amplification must itself be positive before any transfer claim is possible.

## G3 search
Genealogical screening found three independent G3 histories under the same world-side turnover profile:
- W0 × A3
- W3 × A0
- W3 × A2

Generation-stratified real-vs-scrambled autopsy rejected all three as deep semantic-culture candidates. W0×A3 showed real semantic excess through G3, but scrambled amplification was stronger. W3×A0 had weak/non-significant real effects. W3×A2 had a significant aggregate real content effect, but scrambled amplification again exceeded the real condition.

## Interpretation
The simulator can now produce G3 histories, but genealogical depth and semantic persistence remain distinct. No current G3 history passes the preregistered deep-culture criterion. This negative result narrows the search rather than motivating additional agent-side shaping.
