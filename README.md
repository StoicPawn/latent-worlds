# Latent Worlds

**Latent Worlds** is an artificial-life research laboratory for studying whether survival-driven evolution can spontaneously create new mechanisms for inheriting information and, ultimately, cumulative scientific knowledge — **without communication, culture, truth, discovery, or science being explicit objectives**.

The governing design rule is:

> **Build the world, not the civilisation.**

The simulator defines physics, resources, energetic constraints, reproduction, matter, geometry, and semantically empty interaction channels. Agents are not given a technology tree, language, teaching mechanism, scientific objective, truth signal, or reward for understanding the world.

## North Star

> **Can science emerge spontaneously, and if it does, how universal is the science that emerges?**

More precisely:

> **Can populations selected only for ordinary survival and reproduction spontaneously discover, preserve, improve, and generalise true predictive knowledge about hidden laws — and, across independent histories governed by the same physics, do they converge on the same representations, laws, experiments, and technologies, or can contingent discoveries produce different but equally effective sciences?**

Latent Worlds therefore has a two-stage North Star.

### Stage I — Emergence

The first question is the project's current experimental core:

> **Can science emerge without being selected for?**

A population must progress from ordinary adaptation to cumulative predictive knowledge, causal experimentation, law generalisation, and technology without receiving any reward for truth, discovery, communication, culture, or science.

### Stage II — Universality and contingency

Only after spontaneous science is demonstrated reproducibly does the second question become experimentally meaningful:

> **Which parts of science are properties of the universe, and which are properties of the history of those who study it?**

Hold the hidden physics fixed and run many independent evolutionary histories. Compare the resulting epistemic systems at several levels:

1. **predictive convergence** — do populations make the same successful predictions?
2. **causal convergence** — do they identify equivalent intervention structure?
3. **representational convergence** — do internal abstractions encode the same latent regularities?
4. **theoretical convergence** — do independently accumulated models become equivalent up to transformation?
5. **technological convergence** — do populations exploit the same physical affordances, or construct different technological lineages?
6. **historical contingency** — do small early differences or controlled early discoveries causally redirect later science and technology?

The objective is **not** to test whether artificial populations rediscover human scientific vocabulary. Agents are never rewarded for reproducing our concepts. The target is to distinguish functional or structural invariants forced by the world from conventions and trajectories selected by history.

The full long-run programme is therefore:

```text
survival
  ↓
behavioural adaptation
  ↓
non-genetic information inheritance
  ↓
cumulative information
  ↓
predictive knowledge about hidden physics
  ↓
causal models and experimentation
  ↓
cumulative technology / externalised knowledge
  ↓
spontaneous science
  ↓
independent scientific histories under identical physics
  ↓
measure convergence, equivalence and divergence
  ↓
controlled counterfactual perturbations of discovery history
  ↓
epistemic invariants vs historical contingencies
```

A successful programme would therefore answer two distinct causal questions:

```text
Can science emerge?
        ↓
If it emerges repeatedly, must it take the same form?
```

The project deliberately distinguishes behavioural success from genuine epistemic structure, and genuine epistemic structure from historical convergence. A population that merely learns profitable state → action mappings has not necessarily discovered anything about the underlying world; two populations that discover equally predictive models have not necessarily developed the same science.

## Current bridge question

The nearer-term research branch asks:

> **Can evolution spontaneously invent a faster form of evolution?**

Genetic evolution already transfers information across generations. Latent Worlds asks whether populations can spontaneously create a second, non-genetic information process using only already-available anonymous signals or persistent environmental traces.

A serious candidate must show more than repeated signalling. It must exhibit evidence consistent with:

1. **variation** — multiple information variants exist;
2. **causal transmission** — received content directly changes subsequently produced content;
3. **replication with variation** — information is reproduced imperfectly rather than merely correlated with lineage;
4. **differential reproduction** — variants propagate at different rates under matched receiver/context interventions;
5. **cross-lineage persistence** — transmission cannot be reduced to genetic inheritance;
6. **multi-generation persistence** — the process survives beyond its original carriers;
7. **adaptive value** — readable content beats cost-matched censorship and payload scrambling;
8. **faster turnover than genes** — the informational dynamics operate on a shorter timescale than genealogical replacement.

If such a process becomes stable, the next question is not merely whether it exists, but **what it accumulates**. Only if it begins accumulating predictive and causal information about hidden world laws does the project advance toward the North Star.

## Current frontier — v5.1

The current frontier is now the first rung of the epistemic ladder:

> **Can ordinary survival pressure select internal predictive representations that exceed a matched frozen recurrent-reservoir null?**

Three recent results define the problem.

- **v4.7:** individual hidden states were strongly decodable for future latent forcing in all 10 fresh histories (89/562 eligible carriers), but this alone was only an E1-like signal.
- **v4.8:** the signal was not enriched by learning/evolution relative to frozen random recurrent reservoirs (mean carrier fraction 0.1242 vs 0.1221; paired sign-test p = 0.377). The v4.7 result is therefore treated as reservoir decodability, not selected knowledge.
- **v4.9:** adding a hidden quasi-periodic resource-quality field did not create selected-representation excess (mean difference-in-differences -0.0150; 4/8 paired wins; p = 0.637), and the harvest interaction was also negative.

The active diagnosis is now causal rather than cosmetic: either the world does not make anticipation valuable enough, or the generic recurrent substrate cannot access/learn the relevant structure.

v5.0 therefore measures the **observer-side value of perfect foresight** in the resource-wave ecology, while v5.1 prospectively tests a minimal generic input-access ablation: the recurrent controller may optionally receive normalized absolute position and the previous harvest/probe yield, both already present in `Observation`.

No epistemic reward, prediction target, truth signal, science objective, technology tree, or hand-authored theory is introduced.

## Current evidence

The strongest causal histories are:

- **`W11 × A0`** — direct same-agent causal content transmission in G2, real-payload steering, matched-context differential reproduction, specificity against scrambled-content evolution, and persistent adaptive superiority across preregistered horizons.
- **`W21 × A0`** — independent direct-causal mechanistic replication, reaching G3, but not full adaptive replication.
- **`W63 × A0`** — independent content-specific mechanistic replication in G2, but readable content still loses to censorship despite beating scrambling.

The project therefore **does not currently claim discovery of a stable autonomous second evolutionary system**. The strongest missing result is a second independent history satisfying the complete persistent-adaptive criterion.

A 64-world independent campaign in v3.5 found:

- 7/64 histories with late-generation communication;
- 1/64 with a direct causal-removal candidate;
- 0/64 new content-specific mechanistic replications;
- 0/64 new persistent adaptive replications.

This supports the interpretation that the target transition is rare and strongly selective rather than a generic property of the architecture.

## Scientific discipline

Latent Worlds is designed around **falsification before spectacle**.

Patterns are not named “language”, “culture”, “technology”, “knowledge”, or “science” because they look suggestive. Candidate phenomena must survive observer-side null models and causal controls.

Core controls include:

- readable communication vs cost-matched censorship;
- real payloads vs payload scrambling;
- world seed separated from population seed;
- genetic-root conditioning;
- temporal-direction controls;
- same-agent, same-state signal removal;
- donor-payload transplantation;
- matched-context variant reproduction;
- persistent fitness tests across several horizons;
- matched world-side ecological interventions;
- preregistered staged search funnels;
- negative results retained rather than hidden.

Observer instrumentation may inspect simulator ground truth. **Agents may not.**

## The world

The current simulator is a continuous 2D artificial universe with renewable resources and hidden multi-level physics.

### Hidden dynamics

Each world samples **2–4 latent dynamical sources** with unknown periods, phases, amplitudes, and nonlinear coupling. Their combined forcing influences observable temperature and radiation fields. Resource yield depends jointly on those fields through a hidden nonlinear interaction law.

Conceptually:

```text
latent oscillators
      ↓
 hidden forcing
   ↙       ↘
temperature  radiation
      ↘     ↙
    resource yield
```

The number and parameters of the latent sources are never exposed to agents.

### Private information

Opaque obstacles impose line-of-sight constraints. Local transient environmental perturbations alter radiation and resource dynamics. Two agents in the same universe can therefore possess genuinely different evidence about the world:

```text
I_A(t) ≠ I_B(t)
```

This creates a possible ecological reason for communication without rewarding communication itself.

### Matter without a technology tree

The world contains manipulable objects with continuous material coordinates, mass, and position. A hidden `MatterLaw` maps ambient conditions and object arrangements to physical effects.

There are no named object classes such as `battery`, `hammer`, or `generator`, and no recipe table. Useful configurations count as candidate technology only if their value emerges from the underlying physics and survives causal controls.

## Agents

The repository retains several historical/diagnostic agent architectures, including random, reactive, model-based, planner, recurrent, curious, and scientist baselines.

The **publication-oriented mainline**, however, uses a single generic evolvable recurrent substrate via `generic_population_only=True`.

`RecurrentAgent` contains no concept of:

- language;
- message meaning;
- technology;
- science;
- truth;
- teaching;
- imitation;
- target discovery.

Its inputs are ordinary sensory variables plus anonymous signals, public marks, local matter, and conspecific motion. Its outputs are primitive actions.

### Primitive actions

```text
MOVE
HARVEST
REST
PROBE
BROADCAST
INSCRIBE
PICKUP
DROP
```

`BROADCAST` and `INSCRIBE` carry semantically empty numerical vectors. `PICKUP` and `DROP` only manipulate ordinary matter.

### Evolution and lifetime learning

Agents reproduce genetically with mutation. Recurrent-controller weights are inherited with mutation. The generic recurrent substrate also has reward-modulated lifetime plasticity, but this same mechanism applies to locomotion, feeding, manipulation, signalling, and inscription; it has no communication- or science-specific objective.

The evolutionary currency remains ordinary demographic success.

## Epistemic North-Star ladder

The project reserves strong epistemic claims for a preregistered hierarchy:

- **E0 — exploitation:** behaviour covaries with hidden physics and improves fitness;
- **E1 — selected representation:** internal state predicts future latent physics beyond contemporaneous observations **and exceeds matched frozen recurrent/reservoir controls**;
- **E2 — collective excess:** population state predicts latent physics better than individual representations under matched information budgets;
- **E3 — causal social dependence:** censoring social/external-memory channels removes that collective excess;
- **E4 — cumulative epistemic inheritance:** predictive structure survives replacement of its original carriers and improves across generations;
- **E5 — spontaneous experimentation:** unrewarded interventions are selected because the information they generate changes later action and fitness;
- **E6 — law generalisation:** acquired structure transfers to held-out regimes or related worlds in ways incompatible with memorised local policy.

The phrase **spontaneous science** is reserved for replicated systems reaching at least E5–E6 with appropriate causal ablations.

The current epistemic programme has **not yet established E1** under the reservoir-null criterion, and therefore does not yet proceed to E2.

## Repository structure

```text
src/latent_worlds/
  world.py                    world state, ecology, perception, actions
  config.py                   simulation configuration
  metrics.py                  observer-side measurements

  agents/                     agent substrates and diagnostic baselines
  evolution/                  genetic inheritance and mutation
  physics/                    hidden dynamical and matter laws

  emergence.py                candidate-transition detection
  longitudinal.py             long-run observer
  role_ablation.py            causal functional-role tests
  semantic_autopsy.py         content/receiver semantic controls
  information_lineage.py      information lineage analysis
  persistent_inheritance.py   persistent-carrier assays
  secondary_evolution.py      non-genetic Darwinian-process analysis
  causal_transmission.py      same-agent counterfactual transmission assays
  replication.py              independent mechanistic/adaptive replication
  adaptive_search.py          staged replication funnel
  adaptive_persistence.py     multi-horizon adaptive persistence
  phase_map.py                ecological parameter mapping
  transition_conditions.py    matched causal ecology interventions
  pretransition_prediction.py early-warning prediction tools
  epistemic_transition.py     North-Star epistemic assays
  epistemic_convergence.py    same-physics Stage-II comparison tools
  epistemic_decoder_controls.py capacity-controlled predictive decoders
  epistemic_carriers.py       individual predictive-carrier audits
  forecast_value.py           observer-side value-of-foresight assay
  search_funnel.py            attrition/statistical accounting

docs/
  RESEARCH.md                 research programme
  EXPERIMENT_v*.md            chronological experimental record

examples/
  benchmark_*.py              reproducible experiment entrypoints

tests/
  test_*.py                   simulation and scientific-assay tests
```

## Reproducibility

World and population randomness can be separated. Experimental histories are seedable, controls are explicit, and the project keeps negative results as part of the scientific record.

Install and run:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
latent-worlds --steps 1000 --seed 7
```

Example research entrypoints include:

```bash
PYTHONPATH=src python examples/benchmark_secondary_evolution.py
PYTHONPATH=src python examples/benchmark_direct_replication.py
PYTHONPATH=src python examples/benchmark_adaptive_persistence.py
```

## Research principles

1. **Minimum agent-side hard-coding.** Add generic substrate only when necessary; do not encode desired discoveries.
2. **World laws, not technology trees.** Opportunities arise from physics rather than named recipes.
3. **Epistemic outcomes are measurements, never objectives.**
4. **One generic publication substrate.** Hand-designed agents remain baselines, not explanations of civilisation.
5. **Causal tests before labels.** Correlation is not communication, culture, technology, or knowledge.
6. **Held-out worlds and prospective validation.** Avoid defining success after inspecting outcomes.
7. **Negative results are first-class results.** Do not weaken criteria to rescue attractive histories.
8. **Observer complexity is cheap; agent-specific structure is expensive.** Improve measurement and causal inference before adding faculties.
9. **Reproducibility.** Every scientific claim must be tied to explicit seeds, controls, horizons, and criteria.

## Status

**Research prototype, current frontier: v5.1.**

The current scientific task is to establish or falsify **E1 selected representation** under matched recurrent-reservoir controls before attempting stronger claims about collective or cumulative knowledge. In parallel, the earlier direct-causal communication programme remains evidence about a possible non-genetic inheritance substrate, but it is not being conflated with epistemic success. The longer programme remains directed toward spontaneous cumulative knowledge and ultimately the North Star:

> **Can science emerge without being selected for?**

For the complete chronological research record, including failed hypotheses and falsified candidates, see [`docs/RESEARCH.md`](docs/RESEARCH.md) and the versioned experiment reports in [`docs/`](docs/).
