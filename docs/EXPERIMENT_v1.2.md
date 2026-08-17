# v1.2 screening note

Protocol: single generic recurrent substrate; no epistemic or social reward; long-horizon
world-side ecology only. Screening horizon: 900 steps.

## Longitudinal screen (seeds 0–3)

- No complete extinctions by step 900, but final populations were 24, 26, 10 in the tuned
  ecology for seeds 0–2 during the focused run.
- Seed 0 reached generation 2 with 9 births; seed 1 generation 1 with 4 births; seed 2 had
  no births by 900.
- The earlier intergenerational-specialization candidate vanished after requiring living
  agents, >=4 profiled agents per generation, and three consecutive living generations.

## Communication autopsy

Seed 0, private-information world, communication readable vs censored:

- harvest: 1404.20 vs 1369.13
- births: 9 vs 6
- final population: 24 vs 24
- signal-environment R^2: 0.0318
- receiver-action R^2 from payload: 0.0273
- signal generational span: 2

In the no-private-information paired control, readable communication was substantially
more harmful; the resulting seed-0 difference-in-differences was +161.41 under the
observer fitness summary. This looked promising but did not replicate.

Seed 1 readable vs censored (private information):

- harvest delta: -95.05
- births delta: +1
- population delta: -3

Seed 2 readable vs censored (private information):

- harvest delta: -159.39
- births delta: 0
- population delta: -4

Conclusion: seed 0 is an anomaly worth retaining for later mechanistic inspection, but
there is no robust evidence of emergent language or a stable communication advantage.
