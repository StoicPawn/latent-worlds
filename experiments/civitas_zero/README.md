# CIVITAS ZERO

**From a decodable state to knowledge that changes survival.**

CIVITAS ZERO is an open, experiment-first artificial-life research programme built on [Latent Worlds](../../README.md). The physical laws, reproduction, energy budget, and agent reward **do not contain** a prescribed language, civilisation, science, or curiosity objective.

[![CIVITAS ZERO CI](https://github.com/StoicPawn/latent-worlds/actions/workflows/civitas-zero.yml/badge.svg)](https://github.com/StoicPawn/latent-worlds/actions/workflows/civitas-zero.yml)

![Frozen prospective result](figures/v54_effects.svg)

### The world contains a genuine forecasting opportunity

![Observer-only forecasting opportunity](figures/foresight_opportunity.svg)

Three *exploratory* independent world laws (W11, W21, W31) were tested with the original observer-side ideal foresight comparator. A resource wave of strength 1.5 creates substantial energetic value for future-informed route selection; no agent receives that knowledge. See [pilot table](figures/FORESIGHT_RESULTS.md). This is a physical affordance check, **not a claim of learning**.


## At a glance

| Milestone | Question | Evidence status |
|:--|:--|:--|
| v3–v4 | Does semantically empty information transmission support cumulative adaptation? | Rare mechanisms; strong adaptive replication not established |
| v5.3 | Does recurrent-state plasticity create excess predictive carriers? | **Exploratory**; selected rate 0.0003 from 5 candidates |
| v5.4 | Does that rate survive 16 *new* population seeds? | **Failed preregistered joint gate** |
| Next | Are decoded hidden features causally used for decisions, and does the effect transfer across independent physical worlds? | **Unrun hypothesis** |

The latest archived result is a **negative** replication, not a discovery of cognition.

### Reproduce every figure and number

The 16 seed-level observations, frozen manifest and original summary live in [data/v54](data/v54).
No simulation is required to regenerate the result:

~~~bash
python experiments/civitas_zero/analysis/analyze_v54.py
python experiments/civitas_zero/analysis/plot_foresight_pilot.py
python -m pytest -q tests/test_civitas_analysis.py tests/test_civitas_v54.py
~~~

Outputs:

- [Scientifically audited table](figures/V54_RESULTS.md)
- [Full numerical reanalysis](figures/v54_audit.json)
- [Vector figure suitable for manuscripts](figures/v54_effects.svg)
- [Observer-side opportunity pilot data](data/foresight_pilot/results.json)

To rerun the **expensive original experiment**, use the existing [v5.4 prospective runner](benchmark_v54_prospective.py), Python >= 3.11 and the project's environment. The 16 population histories share world W11; they are not 16 independent world laws. Replaying all three treatments for all seeds is time-consuming. Existing archived seed records are never silently overwritten.

## Proposed paper

**Working title:** *The Decodability–Selection Gap: Prospective Tests of Predictive State in Survival-Driven Artificial Life.*

- [Manuscript skeleton](paper/MANUSCRIPT.md)
- [Publication-grade acceptance criteria and next experiment](paper/PROTOCOL.md)
- [Novelty audit and competing work](paper/PRIOR_ART.md)

A successful **mechanism** paper must demonstrate predictive information that is causally needed for useful action, with matched controls and independent world generalization. Alternatively, a strong **negative benchmark** paper must establish practically meaningful failure, with sufficient precision to distinguish absence of an effect from an underpowered experiment. Nonsignificant p-values alone support neither route.

## Scientific guardrails

1. Do **not** add a "discovery" bonus, explicit truth labels, a science agent or a technology tree.
2. Observer-only decoders never feed hidden law parameters back to the agents.
3. Distinguish *decodable information*, *selection by survival*, *causal behavioral use*, and *socially inherited knowledge*.
4. Keep pre-registered results even when they fail.
5. Never infer phenomenal consciousness from a simulated society or an introspection metric.

## Repository design

- Python source and tests remain small, readable, and deterministic.
- Data provenance is immutable: world seeds, population seeds and the fixed treatment appear in each artifact.
- Plots use a pure-standard-library SVG generator, so the paper figure does not require notebook state or a proprietary dashboard.
- Work is isolated on a research branch; the publication baseline remains untouched.

Source: [Latent Worlds](https://github.com/StoicPawn/latent-worlds). See [project-wide methods](paper/PROTOCOL.md).
