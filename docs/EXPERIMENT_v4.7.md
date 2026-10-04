# v4.7 — Individual predictive-carrier audit

## Motivation

v4.5 found 0/10 population-level predictive-representation candidates. v4.6 retained the negative result after controlling decoder capacity on a fresh A35–A44 cohort: 0/10 candidates, maximum gain -2.8%, mean gain -15.0%.

Before modifying the ecology or recurrent substrate, one remaining observer-side ambiguity must be tested: population aggregation may erase predictive structure carried by a minority of persistent individuals.

v4.7 therefore searches for individual carriers without changing any agent or world rule.

## Primary question

**Does any sufficiently observed individual recurrent agent carry future-law information beyond what is already available in its contemporaneous observable state?**

## Frozen design

- world: W11
- new histories: A45–A54
- steps: 1200
- burn-in: 200
- observer stride: 2
- horizons: 10, 35, 70
- minimum samples per carrier: 80
- information level: 0.35
- signal cost: 0.03
- active-obstacle fraction: 0.75
- standard turnover profile

A45–A54 are unseen before v4.7.

## Identity-preserving traces

Each recurrent agent is tracked by its simulator identity. Only rows from the same individual are used in that carrier's decoder.

The observer baseline contains:

- current local temperature and radiation;
- normalized position;
- energy;
- nearest visible resource displacement and richness;
- current population size;
- the exact sin/cos clock signal that the recurrent controller itself receives.

Including the clock is essential: a future-law signal cannot be credited to hidden state merely because the controller was given an explicit temporal cue.

## Conditional hidden-state test

Two models are compared for every eligible carrier:

1. contemporaneous raw baseline;
2. the same raw baseline plus the agent's recurrent hidden state.

Both models use independent past-only nested ridge selection over the preregistered alpha grid from v4.6. They share the same untouched future test suffix.

The endpoint is the normalized RMSE gain from adding hidden state.

## Paired held-out stability

For the final test suffix, v4.7 computes the per-time improvement in normalized squared prediction error produced by adding hidden state.

A moving-block bootstrap preserves local temporal dependence. The lower 5% bootstrap quantile is reported.

An individual is called a weak carrier candidate only if:

- at least 80 samples are available;
- raw+hidden improves normalized RMSE by more than 3%; and
- the 95% lower bootstrap bound on paired error improvement is positive.

This is stronger than selecting the best-looking individual by point estimate alone.

## Claim boundary

A carrier candidate is only an individual-level E1-like diagnostic.

It is not evidence of:

- collective excess;
- social dependence;
- intergenerational knowledge;
- experimentation;
- law generalisation;
- spontaneous science;
- Stage-II convergence or historical contingency.

Any v4.7 positive history must be replicated prospectively on new population seeds before its mechanism is interpreted.

## Decision rule

If v4.7 finds no carrier candidates across A45–A54, the combined v4.5–v4.7 evidence supports a Stage-I bottleneck interpretation: under the current ecology/substrate, predictive representation of future hidden physics is not detectably selected even at the individual level.

The next intervention should then be world-side only and should create an ordinary survival advantage for anticipation, without rewarding prediction, truth, discovery, or science directly.
