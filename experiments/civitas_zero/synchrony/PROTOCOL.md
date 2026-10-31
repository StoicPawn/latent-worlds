# SYNCHRONY AUDIT — can shared time mimic individual knowledge?

Status: exploratory, not a discovery or a preregistered confirmatory result.

## Question
The existing individual-carrier diagnostic attempts to decode future world
forcing from each agent's recurrent state. At any fixed time, that future
forcing is EXACTLY THE SAME for every agent. A decoder could therefore pick
up an exchangeable common-phase signal rather than individual-specific
functional knowledge. A temporal train/test split alone does not exclude
this explanation.

## Five frozen variants
1. raw_only: contemporaneous observer-side sensor cues, position, agent
energy, clock signals.
2. individual_hidden: raw plus the actual agent's 12D hidden state.
3. time_matched_exchange: raw plus a different individual's complete hidden
vector chosen from the SAME world timestamp. Target remains identical.
4. population_mean_hidden: raw plus population-average memory at that time.
5. time_misaligned_mean: raw plus a population mean from a different time.

A feature-selected ridge uses a strictly early validation window and an
untouched late test suffix. All treatments share identical target and
evaluation splits. Scores are averaged by UNIQUE WORLD TIMESTAMP, not by
agent row. Within-time permutation preserves group distribution while
destroying individual matching.

## Frozen pilot
W11, A201, state plasticity at 0.0003, 500 steps, burn-in 80, stride 3,
horizons 10/35/70. Future exploratory expansion: W11/W21 and A201/A202,
three learning modes, WITHOUT retuning on held-out worlds.

## Interpretation
If individual_hidden is no better than time_matched_exchange or
population_mean_hidden, a POOLED decoder has not isolated private
individual knowledge. This does not falsify all per-agent representation.
If individual_hidden wins, that is an observational signal, not proof of
causal behavioral use, fitness selection, or consciousness.

## Publication requirements
G1: real individual-memory signals beat contemporaneous-sensor,
time-exchanged, population-average, rich-clock and capacity-matched
controls on entirely new world laws.
G2: blinded paired replay shows selective removal reduces genuine
external survival/harvest beyond norm- and initial-action-matched shams.
G3: G2 replicates across independently varying physical laws and
survival-selected controllers, not just a fixed reservoir.
A strong NEGATIVE benchmark would also require calibrated error rates
and narrow equivalence intervals across independent world clusters.

## Prior art: NOT a new mathematical trick
- Elsayed & Cunningham (2017), Structure in neural population recordings:
  an expected byproduct of simpler phenomena? Nat Neurosci, DOI 10.1038/nn.4617.
  Provides surrogate population nulls preserving simple structure.
- Tiwari et al. (2026), Decodability is Not Causality, arXiv:2609.18080.
- Tolle et al. (2026), Evolving reservoir computers reveal bidirectional
  coupling between predictive power and emergent dynamics, Patterns,
  DOI 10.1016/j.patter.2025.101457.
- Trial-balanced neural decoding within-condition shuffles,
  Nature Human Behaviour 2026 DOI 10.1038/s41562-026-02537-x.

The potential contribution is a tightly delimited ecological empirical
result, not the shuffle method itself. No finding or novelty is claimed yet.
