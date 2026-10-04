# v4.8 — Frozen recurrent reservoir control

## Motivation

v4.7 produced the first strong positive signal in the new North-Star programme:

- all 10 fresh W11 histories A45–A54 contained at least one individual predictive carrier;
- 89 of 562 eligible long-lived recurrent agents passed the frozen carrier criterion;
- the largest held-out predictive gain from adding hidden state was about 69.8%.

This is retained as a positive individual E1-like result.

It is not yet evidence that selection discovered a predictive representation. A fixed random recurrent network can act as a reservoir: recurrence plus nonlinear transformations of ordinary sensory and clock inputs may create a rich temporal basis from which an external observer can decode future forcing even when the controller never learned or inherited that structure.

v4.8 is the preregistered causal control for that alternative explanation.

## Primary question

**Does the predictive-carrier signal exceed what is produced by a matched frozen random recurrent reservoir?**

## Frozen design

- hidden world: W11
- fresh population histories: A55–A64
- 1200 steps
- burn-in 200
- observer stride 2
- future forcing horizons 10, 35, 70
- minimum 80 observations per individual carrier
- information level 0.35
- signal cost 0.03
- active-obstacle fraction 0.75
- standard turnover profile

A55–A64 are unseen before v4.8.

Each population seed is run under two matched conditions.

### Full condition

- recurrent lifetime reward-modulated weight learning: ON
- recurrent controller-weight inheritance with mutation: ON

This is the unchanged publication mainline.

### Frozen-reservoir condition

- recurrent lifetime weight learning: OFF
- recurrent controller-weight inheritance: OFF

The recurrent state remains recurrent. Agents still receive the same sensory inputs, including the same clock channels, and fixed random recurrent weights can still transform and retain temporal information. Children receive fresh random recurrent controllers instead of inherited ones.

Everything else remains unchanged: physics, resources, actions, metabolism, reproduction, genome inheritance, sensory inputs, communication affordances, object manipulation, recurrent state update, and demographic selection.

The two switches default to ON, so prior experiments and the mainline are unchanged.

## Endpoint

The individual carrier assay is exactly the v4.7 assay.

For each history and condition we compute the carrier fraction as carrier candidates divided by eligible carriers.

The primary paired statistic is the full-condition carrier fraction minus the frozen-condition carrier fraction for each of the ten matched population seeds.

A one-sided paired sign test is computed over non-tied histories.

## Frozen decision rule

Evidence for **selected-representation excess** requires both:

1. positive mean carrier-fraction excess in the full condition; and
2. one-sided paired sign-test p <= 0.05.

With ten non-tied pairs, this requires at least 9/10 positive paired differences.

The maximum predictive-gain difference is reported descriptively but is not part of the primary decision rule.

## Interpretation

Three outcomes are possible.

1. **Frozen approximately equals full.**  
   The v4.7 signal is explainable by generic recurrent reservoir dynamics. It remains an interesting representation property but not evidence that evolution or lifetime learning constructed predictive knowledge.

2. **Full exceeds frozen under the frozen decision rule.**  
   Learning and/or inherited controller dynamics causally contribute to the E1-like signal beyond the random-reservoir null. A subsequent factorial experiment should separate lifetime learning from inherited evolution.

3. **Frozen exceeds full.**  
   Selection is suppressing rather than enriching the observer-decodable future signal under the current ecology. This would strengthen the case that predictive representation is not currently adaptive.

No v4.8 outcome by itself establishes cumulative knowledge, experimentation, law generalisation, spontaneous science, or Stage-II convergence.
