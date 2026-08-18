# v4.0 — Ecology versus population contingency

## Question

If v3.9 identifies ecological cells in which `W11 × A0` enters direct causal G2+ information transmission, is that regime a property of the **world-side ecological basin**, or is it contingent on the exact initial population history `A0`?

This distinction is essential. A transition that reappears across independently initialized populations in the same matched world is qualitatively stronger than one restricted to a single population realization.

## No agent-side changes

v4.0 adds no capability, objective, reward, sensor, action, inheritance mechanism, communication primitive, or physical law. It is an observer-side replication experiment only.

## Preregistered cell selection

The experiment consumes `docs/EXPERIMENT_v3.9_RESULTS.json` after v3.9 is complete.

Before seeing the v3.9 outcome, the selection rule is fixed as follows:

1. take at most six v3.9 **supported** cells;
2. prioritize supported cells by proximity to the canonical W11 condition `(active_obstacle_fraction=1.0, signal_cost=0.03)`, breaking ties by larger G2 mean copy gain;
3. add at most four **unsupported boundary controls** that are Manhattan-adjacent on the v3.9 grid to at least one selected supported cell;
4. evaluate every selected cell under population seeds `A0, A1, A2, A3, A4` with the same W11 world seed and the same direct causal removal assay.

The selection rule is deterministic and encoded in `examples/benchmark_population_contingency.py`.

## Primary quantities

For each ecological cell:

- fraction of population seeds supporting direct causal transmission;
- supported generations by population seed;
- G2 mean copy gain and permutation p-value;
- whether support extends beyond the discovery population `A0`.

We summarize three regimes:

- **history-contingent:** support is restricted to A0;
- **partially reproducible:** at least one independent population seed supports the cell;
- **population-robust:** a majority of tested independent population seeds support the cell.

These are descriptive operational labels, not claims of universality.

## Interpretation

A reproducible ecological basin would support the view that world-side conditions create a genuine opportunity for a secondary information process. Strong A0-specificity would instead imply that the phenomenon is dominated by evolutionary historical contingency, even within a fixed world.

Either outcome is scientifically useful and will determine whether the next step should refine ecological phase structure or characterize path dependence and historical lock-in.
