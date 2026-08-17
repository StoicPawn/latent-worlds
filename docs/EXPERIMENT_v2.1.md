# Experiment v2.1 — Generational depth without semantic shaping

## Question
Can we obtain deeper genealogies by changing only demographic/ecological world parameters, while preserving the content-sensitive communication signature discovered in v1.9–v2.0?

## Constraint
No new sensors, actions, rewards, objectives, communication mechanisms, learning rules, or agent classes are introduced. The pilot changes only reproduction threshold/cost and resource regrowth.

## Pilot ecology
A high-turnover profile used `reproduction_threshold=15`, `reproduction_cost=6`, and `resource_regrowth=0.07`. In W1×A1 it reached generation 2 by 1200 steps, whereas the standard long-horizon candidate had remained at generation 1 even at 3000 steps.

## Semantic transfer test
The same within-receiver counterfactual assay was then run at 850 steps with 350 sampled reception events.

Readable channel:
- G0: n=171, semantic excess ≈ 0.0117, paired p=0.625
- G1: n=179, semantic excess ≈ 0.0335, paired p≈0.0703
- intergenerational amplification ≈ +0.0218

Scrambled-payload evolution:
- G0: n=159, semantic excess ≈ 0.0126, paired p=0.5
- G1: n=191, semantic excess ≈ 0.0576, paired p≈0.00098
- intergenerational amplification ≈ +0.0450

## Interpretation
The deeper-turnover ecology does **not** preserve the candidate semantic mechanism. The scrambled control is stronger at this horizon. Therefore increasing generational depth by ecological tuning cannot be used as a shortcut to claim cultural fixation.

This is evidence that the candidate mechanism is contingent on an ecology × population × history interaction. Future searches must optimize for the joint occurrence of (i) natural generational depth and (ii) real-over-scrambled semantic advantage, rather than depth alone.
