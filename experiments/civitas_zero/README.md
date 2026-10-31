# CIVITAS ZERO

**Primary objective: falsifiable research on functional indicators of AI consciousness.**

**Theory-first gate C0 (mandatory before designing new agent experiments):**
[critical literature review, cutoff 31 October 2026](literature/REVIEW_2026-10-31.md)
· [14 canonical theory-derived indicators](literature/INDICATOR_MATRIX.md)
· [adversarial theory-specific predictions](literature/THEORY_ADJUDICATION.md)
· [peer-reviewed/preprint source ledger](literature/SOURCES.json).
· [literature-first research decision / paper gate](literature/RESEARCH_DECISION.md).
**The three C1–C3 labels are our ASSAY GROUPS, not canonical indicators.**
Some theories explicitly allow minimal awareness without an explicit self-model;
none of these computations is a validated sufficient test of experience.


**Can an AI agent develop a causally useful model of its OWN computation, distinguish
internal damage from environmental difficulty, and selectively use that information?**
The world and any civilisation that emerges are experimental tools, NOT evidence
of consciousness. This programme does not claim to prove phenomenal experience.

[**Consciousness programme and preregistration roadmap**](paper/CONSCIOUSNESS_RESEARCH_PROGRAM.md)
· [**AI-consciousness working manuscript**](paper/CONSCIOUSNESS_PAPER_DRAFT.md)
· [**Machine-readable indicator matrix**](paper/INDICATOR_MATRIX.json)

**C1 self/world causal attribution**, **C2 global access**, **C3 recursive
monitoring**: all **UNTESTED**. The archived v5.4/v5.5 observations are
methodological controls and feasibility results, never consciousness data.


CIVITAS ZERO is an open, experiment-first artificial-life research programme built on [Latent Worlds](../../README.md). The physical laws, reproduction, energy budget, and agent reward **do not contain** a prescribed language, civilisation, science, or curiosity objective.

[![CIVITAS ZERO CI](https://github.com/StoicPawn/latent-worlds/actions/workflows/civitas-zero.yml/badge.svg)](https://github.com/StoicPawn/latent-worlds/actions/workflows/civitas-zero.yml)

![Frozen prospective result](figures/v54_effects.svg)

### A strong-looking forecasting opportunity — but whose actions are available?

![Observer-only forecasting opportunity](figures/foresight_opportunity.svg)

Three *exploratory* independent world laws (W11, W21, W31) were tested with the original observer-side ideal foresight comparator. A resource wave of strength 1.5 creates substantial energetic value for future-informed route selection; no agent receives that knowledge. See [pilot table](figures/FORESIGHT_RESULTS.md). The original oracle chooses globally among all resource patches, whereas simulated agents perceive only local patches. This is a *privileged upper-context comparison*, not proof that the agent can realize its value.

### A new experimental falsification: perception versus theoretical information value

![Global versus locally visible choice sets](figures/accessibility_foresight_pilot.svg)

In three PILOT worlds with resource waves, the global-choice extra value (1.126, 0.671, 0.163) drops to 0.015, 0.017, 0.008 when **both** forecasters can choose only among resources presently visible under the world's exact observation radius and obstacle occlusion. This comparison of incremental values is DESCRIPTIVE: shrinking the set of actions is not generally monotone in value-of-information gain, and agents may explore to reveal new patches. See [full accessibility audit](figures/ACCESSIBILITY_PILOT.md).

A separate source-level test establishes that the generic recurrent controller explicitly encodes only the **nearest** resource, despite the observation API returning multiple visible patches. This is a specific architecture bottleneck worth testing causally; it is not a general impossibility result.

### Could synchronized world time masquerade as individual knowledge?

![Individual synchrony audit](figures/synchrony_learning_modes.svg)

The new two-world PILOT exchanges complete hidden states among agents at *the same world timestamp* and trains time-ordered observer decoders with identical raw cues. In both worlds, most individual hidden states fail to beat a different agent's matched-time state. [Detailed methods, all frozen controls, negative findings and preregistration candidate](synchrony/RESULTS_AND_NEXT.md). The negative result is not yet a causal claim. A discovered lookahead bug in a secondary negative control was corrected *before publishing*; raw trajectories and [the correction log](data/synchrony_pilot/CORRECTION_LOG.md) are retained.




### C0.5: matched internal and external faults — actual trained-agent feasibility pilot

![Matched counterfactual faults](c05/figures/matched_faults.svg)

The first experiment on **real evolved recurrent agents** (W11/W21, 33 eligible agents) uses a constructed pair of internal-weight and external temperature perturbations with **exactly matched first-step latent state and action**. Persistent internal faults cause later trajectory differences; transient matched faults remain identical within floating-point precision. **This is algebraically guaranteed**, not discovered awareness. Because the raw temperature observation differs, the experiment is **NOT** a matched-information test for endogenous self/world discrimination, and not a consciousness indicator. [Read the full protocol and scope](c05/PROTOCOL.md), [reproducible negative-results report](c05/figures/C05_RESULTS.md) and [directly relevant Phua 2025 prior art](https://arxiv.org/abs/2512.19155).

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
- [Local access pilot](data/local_foresight_pilot/results.json)
- [Matched-time exchange trace and statistical controls](synchrony/PROTOCOL.md)

To rerun the **expensive original experiment**, use the existing [v5.4 prospective runner](benchmark_v54_prospective.py), Python >= 3.11 and the project's environment. The 16 population histories share world W11; they are not 16 independent world laws. Replaying all three treatments for all seeds is time-consuming. Existing archived seed records are never silently overwritten.

## Publication objective

**Primary working title:** *Can Survival-Evolved AI Agents Acquire Causally Useful Self-Models?*
A theory-guided experimental study of computational indicators of artificial
consciousness. **Results do not exist yet.**

The older ecology-focused manuscript below is kept only as a transparent
methods/negative-results record, not as the primary paper.


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
