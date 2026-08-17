# Experiment v1.8 — Content placebo and population × world transplants

## Principle
Version 1.8 adds no agent objective, semantic prior, action, reward, or physical law. It adds only observer/intervention controls that separate signal content from channel presence and population stochasticity from world stochasticity.

## 1. Signal-content placebo
A new `communication_scramble` intervention preserves signal count, source location, radius, energetic cost, and the marginal payload distribution, but randomly reassigns payloads among simultaneous signals using a separate intervention RNG. Thus world physics, reproduction randomness, and agent exploration RNG are not perturbed by the placebo itself.

The previously unusual coupled seed 11 remained content-sensitive in two of three fragmentation regimes at 2,000 steps:
- q=0.35: readable harvest 3649.0 vs scrambled 2859.6 vs censored 2755.5; populations 29 vs 21 vs 21.
- q=1.65: readable 3407.2 vs scrambled 3242.2 vs censored 2931.1; populations 27 vs 26 vs 22.
- q=1.0 failed the content test at 1,200 steps: scrambled outperformed readable.

These are candidates, not language claims. The strict communication bursts remain early and do not yet fix over many generations.

## 2. Independent population RNG
`SimulationConfig.agent_seed` optionally separates agent-side randomness (initial genomes/controllers, agent exploration, mutation/inheritance) from world-side randomness. This permits population × world transplant experiments without changing agent rules.

A 5×5 transplant matrix at q=0.35 and 600 steps produced strict burst candidates in 7/25 combinations:

- world 0: agent seeds 1, 3, 11
- world 1: agent seeds 1, 3
- world 2: none
- world 7: none
- world 11: agent seeds 0, 14

This sparsity argues against either a universally communicative population or a world that mechanically forces communication. The current pattern is an ecology × population interaction.

## 3. Content placebo on transplanted candidates
Three representative transplant candidates were extended to 1,200 steps:

- world 0 × agent 1: readable beat censored by +134.9 harvest but lost to scrambled by -64.7; not content-sensitive.
- world 11 × agent 14: readable beat censored by +135.0 but lost to scrambled by -148.6; not content-sensitive.
- **world 1 × agent 1**: readable beat censored by +85.1 and scrambled by **+280.1** harvest; population 25 vs 22 vs 22. This is the strongest content-sensitive transplant candidate in v1.8.

## Interpretation
The important emerging pattern is no longer merely 'some signals correlate with the environment'. Rare population–world pairings can produce null-aware cross-generational signalling, and in at least one pairing the intact mapping between sender context and payload materially outperforms both no communication and payload-preserving scrambling.

This still does not establish stable language: generational depth remains shallow and the convention is not yet shown to fix. The next decisive tests are replication of the content-sensitive effect across nearby world/population perturbations and lineage-level analysis of which sender/receiver families carry the effect.
