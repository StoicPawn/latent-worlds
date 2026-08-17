# Research programme

## Core distinction

A system that merely learns `state -> action` can exploit regularities without representing them. Latent Worlds therefore distinguishes:

1. behavioural success;
2. predictive world-modelling;
3. active experimentation;
4. causal law recovery;
5. construction of useful artefacts from discovered laws;
6. transmission and cumulative improvement of knowledge.

These levels require different metrics and should not be conflated.

## Planned world families

- thermal/resource laws;
- mechanics with hidden mass/friction relations;
- compositional chemistry with conservation constraints;
- waves/signals with hidden propagation laws;
- orbital or multi-source forcing producing irregular environmental regimes;
- worlds with regime switches whose deeper meta-law is itself discoverable.

## Planned agent families

- random baseline;
- reactive/model-free learner;
- predictive world-model agent;
- curiosity-driven agent;
- active causal experimenter;
- symbolic hypothesis agent;
- social learner;
- evolved mixtures of the above.

## Primary benchmark idea

Train/develop on a family of worlds and evaluate on held-out worlds whose parameters and eventually functional forms differ. Metrics should include survival, energetic efficiency, sample efficiency, prediction error, intervention quality, recovered-law error, transfer, emergent tool utility, and cumulative cultural retention.

## Discovery instrumentation (v0.3)

The first world family is deliberately small in state dimension but already has hierarchical hidden structure. Three latent oscillators with independently sampled periods, phases and amplitudes create a quasi-periodic forcing signal. A weak nonlinear coupling means that the forcing cannot be reduced to a single sinusoid. Temperature and radiation are then generated from this forcing through different spatial and cross-field laws. Finally, harvest efficiency depends jointly on temperature and radiation with a hidden interaction.

The important causal graph is therefore approximately:

```text
latent oscillators -> forcing -> temperature ----\
                         \-> radiation ---------> resource yield
                               ^                 /
                               |----------------/
                         thermal coupling
```

Agents are not told this graph. They see local observables and outcomes only.

`ScientistAgent` now fits competing **multivariate** hypotheses: constant, linear, additive quadratic, quadratic-with-interactions and a generic RBF alternative. None is the simulator's actual equation. The agent also estimates, from its own movement history, how spatial interventions tend to move it through observable temperature-radiation space. This gives a primitive form of experimental design without privileged access to gradients.

Evaluator-side metrics now include:

- held-out law-prediction RMSE over reachable spacetime states;
- coverage in both temperature and radiation;
- the model family preferred by each scientist;
- the fraction selecting interaction-capable hypotheses;
- epistemic action counts;
- survival and reproduction separately from epistemic quality.

This creates an important falsifiable distinction. A scientist should receive credit for discovering that two variables interact even if that knowledge does not immediately maximise survival. Conversely, a policy that simply finds a profitable region should not count as understanding the world's structure.

### Next experiments

1. **Structural ablation:** compare a scientist forbidden to use interaction terms with one allowed to discover them. Worlds with interaction near zero serve as negative controls.
2. **Latent-source discovery:** add a temporal model that must infer how many hidden oscillatory sources are needed to explain environmental trajectories, without being told that the answer is three.
3. **Counterfactual intervention:** introduce manipulable objects that locally alter one observable field, allowing agents to distinguish correlation from causal influence.
4. **Held-out law families:** sample qualitatively different yield equations so that success cannot come from memorising the current functional family.
5. **Evolution of cognition:** make memory, probing rate and model complexity heritable costs and test when natural selection favours scientific cognition.

A strong publication claim should require success across held-out worlds and matched-cost ablations, not a visually impressive single run.

## v0.4 principle: no epistemic fitness shaping

From v0.4 onward the mainline experiment forbids direct epistemic incentives. In
particular, default agents receive no reward for model accuracy, uncertainty reduction,
novelty, source recovery, interaction detection, or symbolic correctness. The legacy
`ScientistAgent` is retained only for historical ablation experiments and is not spawned
in the default world.

Observer-side metrics may inspect hidden ground truth, but agents may not. This creates a
clean falsifiable question: if predictive structure, abstraction, social transmission, or
scientific-looking behaviour appears, did it survive because it improved ordinary life?

Negative results are first-class results. Current early runs do not yet show strong
selection for larger memory or abstraction; that absence is preserved rather than tuned
away.

## v0.5 falsifiable culture protocol

The central constraint is now stronger: epistemic and social outcomes are evaluation
variables, never objectives. Agents are selected only by ordinary demographic fitness.

The world exposes anonymous, costly broadcast vectors and persistent public vectors.
A recurrent controller may learn to use them, ignore them, or be selected against. Neural
weights are inherited with mutation; public marks can survive the individual that created
them.

### Hierarchy of evidence

We will not call a phenomenon "communication" merely because emitted vectors correlate
with temperature, radiation or food. Such self-encoding appears in cost-matched censored
controls too. Stronger evidence is ordered as follows:

1. emitted vectors encode external state on held-out episodes;
2. another agent's action distribution changes under signal intervention;
3. that intervention improves demographic fitness;
4. sender/receiver mappings become lineage-stable;
5. mappings transmit beyond genetic parent-child copying via public traces or interaction;
6. records accumulate and later agents exploit information produced before their birth;
7. population-level models predict hidden world structure better than any isolated agent;
8. agents eventually exploit that accumulated structure to create novel physical
   arrangements whose function was never represented as a named technology.

The intended spectacular result is therefore not "an agent fits the hidden equation". It is
an evolutionary transition from purely instrumental behaviour to cumulative externalized
models of a world whose deeper structure was never an objective.

### Required null models

Every claim should be paired with at least one null:

- channel censored but emission cost preserved;
- payloads shuffled between senders/times;
- public marks spatially relocated;
- inheritance broken while ecology is unchanged;
- frozen random recurrent controllers;
- physics held constant versus hidden-source count/regime changes.

These controls are part of the research design, not post-hoc cleanup.


## v0.6 physical technology protocol

Technology is now defined operationally rather than semantically. Matter objects expose
only mass, position and three continuous sensory material coordinates. A world-specific
hidden law maps ambient state plus object arrangement to a multiplicative energy-conversion
effect. No discrete composition rule exists.

This creates a hierarchy of falsifiable tests:

1. **affordance exists**: evaluator-side search confirms some counterfactual arrangements
   materially outperform the neutral field;
2. **manipulation occurs**: agents successfully relocate matter despite energetic cost;
3. **configuration gain**: the actual arrangement becomes better than the exact initial
   layout under the same current environment;
4. **behavioural reuse**: agents revisit, maintain or recreate high-value arrangements;
5. **demographic causality**: manipulation-enabled populations outperform a frozen-object,
   cost-matched paired control;
6. **transmission**: exploitation persists beyond the inventor through genes, signals or
   public traces;
7. **cumulative engineering**: later generations improve a pre-existing configuration.

Current v0.6 runs are deliberately a negative baseline: recurrent agents occasionally
move objects, but there is no systematic demographic advantage yet. This is retained as
an important null rather than tuned away. The next research step is to allow physically
richer long-lived arrangements and measure whether ordinary planning and cultural memory
can make the affordances evolutionarily discoverable without adding an object-oriented
reward.

## v0.7: language must not be a hidden objective

A signal is not language merely because it correlates with temperature, resources or another
world variable. The publication criterion is intentionally stronger. Candidate emergent
communication requires (i) differentiated emission, (ii) receiver sensitivity, (iii) receiver
behavior that depends on the signal, (iv) persistence or recurrence across generations, and
(v) a causal fitness or ecological advantage relative to an otherwise matched world in which
signals are emitted at the same energetic cost but cannot be read. No one of these quantities is
available to the agents.

Conspecific perception is limited to relative position and recent motion. This permits generic
social learning without implementing imitation. Lifetime adaptation is a single generic
reward-modulated plasticity mechanism acting on all primitive actions equally. Thus any stable
communication protocol, convention, imitation-like behavior, teaching-like behavior or cultural
transmission must arise from the same substrate used for ordinary ecological behavior.

## v0.8 — Private information as a world property

The simulator now creates informational asymmetry without any epistemic or social objective in agents.
Opaque geometric obstacles limit line-of-sight to resources, objects, conspecifics, signals and public marks. Local transient physical perturbations alter the radiation field and local resource regrowth. The same global world can therefore produce different evidence at different locations.

This gives communication a possible instrumental role without rewarding communication itself. A publication-grade emergence claim must use factorial controls:

1. private information ON, communication readable;
2. private information ON, communication censored;
3. private information OFF, communication readable;
4. private information OFF, communication censored.

The key interaction is not simply `communication ON > OFF`, but whether communication becomes selectively useful specifically when the world contains substantial information asymmetry.

Observer-only diagnostics quantify visibility asymmetry, local-field dispersion, signal uptake, generational persistence and paired fitness effects. None are visible to agents or enter reproduction.

### Current negative control

A short 4-world x 350-step paired run yielded mean private-information index about 2.27 while readable communication still reduced final population and total harvest relative to the censored control. This is desirable at this stage: the world now supplies a reason for communication to evolve, but no communication solution is hard-coded.

## v0.9 — Minimal-substrate emergence audit

The main publication protocol now uses **one generic recurrent substrate** rather than a menu of hand-authored cognitive roles. Older architectures are retained only as baselines. Behavioural roles must therefore appear as empirical clusters, not Python classes.

The observer applies causal controls before naming phenomena:

- communication: 2x2 private-information × readable-communication design;
- technology: movable-matter vs cost-matched frozen-matter control;
- candidate labels require multiple simultaneous criteria and never enter fitness.

The guiding rule is: *add world structure only when it creates a general ecological opportunity; add observer instrumentation freely; add agent-specific machinery almost never.*

## v1.0 — Longitudinal emergence before new mechanisms

From v1.0 the primary strategy changes from adding capabilities to observing the
existing substrate for long periods.  `latent_worlds.longitudinal` samples the
same evolving world at fixed epochs and detects macroscopic novelty using only
observer-side measurements.  A high novelty score is **not** called emergence:
it must persist into a subsequent epoch in an interpretable channel (behavioural
differentiation, cross-generation signalling, material configuration, or
intergenerational specialization), and any promising candidate must then survive
paired causal controls.

This implements a pre-registered discipline for the project:

1. discover candidate transitions without agent-side shaping;
2. replicate across seeds;
3. ablate the relevant world affordance while keeping costs matched;
4. only then formulate a scientific claim.

The publication-mode population is a single generic recurrent substrate. Named
agent architectures remain diagnostic baselines, not the source of claimed
emergence.

### Anti-false-positive rule: collapse is not emergence

The first long-horizon scan revealed a useful failure mode: novelty scores can spike
while a population is collapsing. v1.0 therefore excludes candidate transitions
once population falls below 20% of the starting population (or four individuals).
This is an observer-side filter only. We also use a slightly more renewable
long-horizon ecology so that evolutionary history is not truncated merely by an
under-supplied world; no agent objective or controller is altered.

## v1.2 — Candidate autopsy before feature growth

The long-horizon campaign now uses a stricter rule: descriptive heterogeneity is not
an emergent social organization. Generation-level specialization is computed only
from living agents, requires at least four profiled individuals per generation, and
requires a chain of three consecutive living generations before being labelled
intergenerational specialization.

A first apparent seed-0 transition failed this stricter audit. The previous signal
was supported by only three generation-1 descendants and was therefore rejected.
The long-horizon ecology was then adjusted only on the world/biology side (renewable
resources, basal dissipation, and reproduction energetics) to permit more genuine
generational turnover without adding any cognitive or epistemic objective.

Under the revised ecology, seed 0 produced a potentially interesting causal pattern:
readable communication improved harvest/births relative to censored communication in
a private-information world, while communication was harmful in the no-private-
information control. However, signal encoding and receiver uptake remained weak and
the effect failed replication in seeds 1 and 2. It is therefore recorded as an
outlier, not evidence of emergent language.

This is the operational publication rule going forward: a candidate must survive
(1) within-run persistence, (2) causal ablation, and (3) across-seed replication
before it is promoted from anomaly to phenomenon.

## v1.3 — Rare-regime search, not feature growth

No new agent capability is added.  The observer now tests recent-window communication
against a shuffled-payload null.  Multi-generation emission alone is rejected: a
candidate signalling transition must show both environment encoding and receiver-action
uptake above permutation baselines in at least two of three consecutive epochs.

A 12-seed screen at 1,200 steps (seeds 0–11; seeds 12–13 were also checked as an
additional extension) produced one communication candidate: seed 0.  Seeds 1 and 3
showed descriptive multi-generation signalling but failed causal replication; seeds
6–13 produced no communication candidates under the stricter null-aware detector.

For seed 0, a long-horizon 2x2 private-information x readable-communication control at
1,200 steps gave an observer-side difference-in-differences of +168.68.  The private-
information readable-vs-censored contrast itself was modestly positive, while readable
communication was substantially harmful when private information was removed.  Seeds 1
and 3 gave negative difference-in-differences (-178.50 and -259.86 respectively).

Interpretation is deliberately narrow: seed 0 is a **rare candidate ecological regime**
in which anonymous signalling may have become instrumentally useful because information
was spatially private.  It is not evidence that language generally emerges.  The next
scientific task is to characterize what is special about this regime and test nearby
world/population perturbations without adding any agent-side mechanism.

## v1.4 — From behavioural diversity to causal interdependence

Behavioural heterogeneity is not division of labour. From v1.4, a role is considered
scientifically interesting only if removing the individuals currently expressing that role
hurts the *remaining population's per-capita productivity* more than removing an equally
large, age/energy-matched random subset. The intervention is observer-side and is performed
only on cloned worlds; it never affects selection in the discovery run.

This provides a stricter hierarchy: diversity -> persistent specialization -> functional
interdependence -> only then a candidate social organization. Harvest-dominant roles are
interpreted cautiously because direct production can mechanically affect totals; the primary
measure is therefore harvest per surviving agent-step relative to matched removals, not raw
harvest.
