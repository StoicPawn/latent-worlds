# Scientific priority amendment — AI consciousness indicators (2026-10-31)

The completed ecology/predictive-representation work below is a **supporting
methods archive**. It is not the main scientific objective of CIVITAS ZERO.
The current and future study targets theory-derived COMPUTATIONAL INDICATORS
OF AI CONSCIOUSNESS: causal self-world distinction, selective global
availability, recursive self-monitoring. The society is a stress-test ecology.
All consciousness-indicator experiments are currently **UNTESTED**.
See [the current scientific contract](CONSCIOUSNESS_RESEARCH_PROGRAM.md)
and [primary manuscript draft](CONSCIOUSNESS_PAPER_DRAFT.md).

---

# Paper protocol and publication gates

**Status:** publication plan and preregistration candidate; NOT evidence of artificial consciousness.
**Engine:** StoicPawn/latent-worlds; untouched baseline world physics and agent rewards.
**Frozen completed experiment:** W11/A93–A108, state-plasticity rate 0.0003, three controls (v5.4).

## Scientific question

> When does a survival-evolved recurrent population contain *selected, causally used*
> predictive information about hidden physical dynamics, rather than fortuitous
> decodability produced by recurrent memory?

The alternative of publishing a simulated "civilisation" because it looks like one is
scientifically weak. We will only call something knowledge if it survives independent
prediction and intervention gates.

## Explicit claim hierarchy

| Stage | Operational criterion | Must **not** be inferred |
|---|---|---|
| D0: decodability | Hidden state predicts observer-only future variable on time-ordered holdout | Selected knowledge |
| D1: selection | Prediction *increment* beats observation-matched frozen recurrent reservoirs and output-only learners prospectively | Functional use |
| D2: causal use | On same-world matched randomized replays, selective removal of predictive information changes future choices and *external* reward beyond norm-, action-, and compute-matched shams | Self-awareness |
| D3: transfer | D1 and D2 repeat with fresh world laws, population seeds, timescales and unseen perturbations | Universality |
| D4: social accumulation | Information survives replacement of its carriers, crosses genetic lineages and causally raises downstream fitness vs cost-matched censorship and scrambled content | Human-like civilisation |
| D5: discovery | Agents select costly probes which lead to reproducibly better out-of-sample predictions/technology under no epistemic reward | Phenomenal consciousness |

D1 is not yet established. v5.4 fails its preregistered gate even though the
mean effect is positive. D2–D5 are untested within the present programme.

## Novelty required before writing a submission

A paper must make one precise claim *not already demonstrated*, and openly map the
increment relative to reservoir computing, selected cognition, cultural transmission,
and causal probing literature. The present v5.4 negative alone is unlikely sufficient.

Possible manuscript types:

1. **Mechanism paper (preferred):** a new, reproducible dissociation between
   internally decodable forecast information and causal use for survival. Establish
   its ecological boundary conditions by manipulation, not only correlational probes.
2. **Negative measurement / benchmark paper:** show that popular decodability
   diagnostics systematically produce false claims under realistic ecological nulls;
   quantify error with strong, fully powered independent-world experiments.
   Failing to reject zero on W11 does NOT meet this criterion.
3. **Emergence paper:** independently demonstrate socially retained predictive
   information or experimentation without explicitly encoding the target objective,
   across worlds and with transplant/censorship controls.

## Frozen v5.4 audit — completed

- Discovery v5.3: five rates, agent seeds A89–A92, W11; selected rate 0.0003.
- Confirmation v5.4: A93–A108, W11, 1,200 steps per run; frozen, output-only and
  state-plastic treatments; time-ordered observer decoder.
- Paired carrier fraction state-minus-frozen +0.028916, 9/16 wins, exact
  one-sided p=0.401810.
- Paired carrier fraction state-minus-output +0.022856, 10/16 wins, exact
  one-sided p=0.227249.
- State-minus-output harvest +64.581 mean units.
- All 16 pairs eligible; joint gate FAIL. No post-hoc rate adjustment.
- Per-seed JSON files, numerical audit, figure and tests included in this branch.

Do not cite the 16 agents or 16x3 simulator runs as independent physical-world
replications. Only ONE world seed was used. The provided bootstrap CIs condition
on W11 and measure variability of population histories.

## Prospective experimental programme — v5.5 (NOT YET RUN)

The new work tests a stronger null: *a decodable future predictor is not necessarily
an action-used forecast*. Develop assays on separate, explicitly labeled discovery
histories. **Do not tune using A93–A108**, already assigned to the v5.4 evaluation.

A rigorous design should:

1. First demonstrate *forecast opportunity*: an **observer-side** ideal,
   information-advantaged policy can improve future resource harvest under the
   same ecological costs. If not, a null emergence result is uninterpretable.
2. Train readouts on earlier time blocks ONLY. Compare raw present observations,
   frozen reservoir of matching capacity, output-only recurrent agent, state-plastic
   agent, shuffled-memory, shuffled-target and matched random features.
3. Identify a predictive feature/direction on development histories; freeze it.
   For causal tests, clone actual simulator/RNG state before interventions and
   compare blinded matched-replay treatment/sham under the same world shock path.
4. Prevent trivial action-disruption confounds with matched instantaneous
   action-change rates, latent perturbation norms and energy costs, including
   generic (non-predictive) hidden-state ablations.
5. Measure subsequent real task return (harvest, survival, reproduction), not only
   decoder AUROC/NMSE. Keep negative/null interventions and all dropouts.
6. Evaluate after the interventions on at least **three predeclared distinct
   physical-world seeds** and independent agent histories; treat *world* as
   the cluster for between-physics inference. Use additional world configurations
   (hidden oscillator count, amplitude, resource phase topology) for OOD transfer.
7. Match wall time, population, parameter budget and input availability across
   treatments. Baseline superiority must survive causal and environmental controls.

**Numerical design targets, not inferred power:** start with 3 worlds × 16 new
population seeds × primary 3 treatments (144 simulator runs); assess within-world
variance using pilot-only seeds, then freeze power analysis and confirmatory sample
size. No p-value threshold will substitute for a predefined practically important
effect threshold. Re-running the identical W11 cannot establish transfer.

### Preregistered candidate endpoints for v5.5

- Primary mechanistic endpoint: paired relative harvest gain attributable to
  the predictive component vs matched non-predictive intervention, at a
  prespecified replay horizon and cost budget.
- Auxiliary: fraction of individual carriers with held-out decoder advantage
  conditional on all contemporaneous sensors.
- Robustness: cross-world forecast NRMSE and failure under feature-shuffled,
  phase-scrambled and immediate-action-matched controls.

**No v5.5 treatment definitions, numerical thresholds, randomization map or
stopping decisions are frozen yet.** Code and exact criteria must be completed
and reviewed before accessing any v5.5 confirmatory data.

## Paper acceptance standard

A first external submission is justified only after all of the following:

- **Contribution:** a novel, bounded, falsifiable result or a genuinely new,
  broadly reusable evaluation methodology. Explicit closest-paper comparison.
- **Replication:** multiple independent world laws, biological/population seeds
  separated, uncertainty estimates at the true unit of replication.
- **Causality:** complete paired intervention and sham protocol with leakage,
  action-disruption, matched cost and observational-surrogate controls.
- **Reward:** actual external task benefit or a carefully powered negative
  equivalence bound; a high probe AUC alone is insufficient.
- **Transparency:** frozen configs, complete code, raw seed tables, environment
  versions, deterministic reproduction commands, sample exclusion rules,
  null results and generating scripts for every figure.
- **Scientific restraint:** no claim of spontaneous science without D4/D5,
  no claim of consciousness from any of D0–D5.
- **Presentation:** one-page visual overview, clean API, CI tests, fully
  documented reproducibility entrypoint, machine-readable experiment manifest,
  paper draft and references, citable release/DOI when a paper is submitted.

## Proposed figures (minimum)

1. Physical world and agent-observation boundary (observer sees ground truth;
   agent does not).
2. Confirmatory v5.4 paired effects, negative gate and W11-only scope.
3. Forecast opportunity: observer oracle gain under matched energy budget.
4. D0→D1→D2 separation: decoder quality versus causal intervention utility.
5. Independent world-by-world effect distribution and out-of-domain generalization.
6. Intervention ablations / matched cost controls.
7. Optional emergence case study only when supported by D4 or D5 assays.

## Ethical and reporting scope

Artificial societies, collective coordination and functional self-monitoring
do not establish subjective experience. Do not treat arbitrary generative
simulations as empirically validated models of real human civilisation.
No external data or private user files are required.

## Amendment — action-accessibility confound, introduced AFTER v5.4

The original forecast opportunity was computed using global resource patches, not the limited local choice set that actual agents can observe. In the recurrent controller only the nearest patch explicitly enters the current feature vector. The new discovery pilots (W11/W21/W31) show substantial divergence of global versus local-choice-set oracle benefits. The current scientific candidate is a prospectively designed INTERACTION TEST: perceptual rank-invariant candidate access (matched network capacity) × generic recurrent-state plasticity × resource-wave forecast pressure. Primary endpoint: actual survival/harvest world-level interaction; subordinate: individualized forecast prediction beyond synchronized-state controls. All confirmation world seeds, effect thresholds and sampling budgets must be fixed PRIOR to running that experiment. No new claims from existing exploratory seeds.
