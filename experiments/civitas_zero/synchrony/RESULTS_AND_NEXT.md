# CIVITAS ZERO — v5.5 exploratory falsification dossier

**Status: exploratory research; NOT a publishable mechanism, NOT evidence of consciousness.**
Source: StoicPawn/latent-worlds on branch research/civitas-synchrony-pilot.
Mainline engine, rewards and existing v5.4 results unchanged.

## Motivation: two hidden assumptions in the original research framing

1. The observer-only forecast target is the same physical forcing for every
   agent in a world at time t. State decodability might represent a common
   environmental clock rather than privately selected agent knowledge.
2. The old perfect-foresight route chooser has access to every patch worldwide,
   whereas physical agents perceive only nearby unoccluded patches. In the
   generic recurrent controller, ONLY THE NEAREST patch is explicitly encoded
   among potentially several visible patches. The original oracle opportunity
   cannot be equated with action-accessible opportunity for this controller.

## Pilot 1: exchangeability of "individual" representation

All runs use 500 simulator steps, burn-in 80, stride 3, future forcing
horizons 10/35/70, common population seed A201, and independent physical
world seeds W11 and W21. Modes: frozen recurrent reservoir, state-plastic
at the v5.3 discovery rate 0.0003. Only observer-side linear decoders
are fitted; no learning signal or label is fed to agents.

| World | Learning | Eligible individuals | Fraction own memory beats time-matched foreign memory | Mean NRMSE benefit of own memory |
|:--|:--|--:|--:|--:|
| W11 | frozen | 65 | 18.5% | -0.0902 |
| W11 | state plastic | 61 | 11.5% | -0.1108 |
| W21 | frozen | 47 | 19.1% | -0.0519 |
| W21 | state plastic | 36 | 30.6% | -0.0585 |

Benefit = NRMSE using another agent's hidden vector at the SAME timestamp
minus NRMSE using the agent's own vector. Positive is better for the
individual. Negative population means show that this untrained
time-order decoder does not establish private predictive representation.
The agents are correlated, so agent rows are NOT independent replications.

Pooled observer decoders additionally failed to improve over the raw
sensor/time baseline using individual hidden state on W11 and W21.
This does NOT falsify all per-agent representations or prove a lack of
functional knowledge, especially because the controllers have distinct
weights/codebooks and sample sizes.

Important audit: the first version of a secondary *cyclic* time-shifted
mean control inadvertently read future states. Corrected it to a
STRICT PAST-ONLY surrogate before any research-branch publication.
The main comparisons above are provably unchanged. Read
data/synchrony_pilot/CORRECTION_LOG.md; all raw NPZ trajectories are retained.

## Pilot 2: do agents have a chance to use forecasts?

The historical v5.0 and CIVITAS foresight benchmark gives a "myopic" and
perfect-foresight observer privileged access to ALL global resource patches.
We repeated the SAME 176 decision samples per world-condition, but limited
both choosers to the patches currently visible with the exact simulator
radius and obstacle line-of-sight rule. Both observers still know the
yield law; actual agents do not.

| World | Oscillation | Global extra value | Visible-patch-set extra value |
|:--|--:|--:|--:|
| W11 | 1.5 | 1.12594 | 0.01502 |
| W21 | 1.5 | 0.67128 | 0.01684 |
| W31 | 1.5 | 0.16314 | 0.00795 |

These are mean energetic units per decision. The restricted-set
incremental advantage is 95–99% numerically smaller for these pilot
cases. The RATIO is NOT a proof that this fraction of "knowledge" is
inaccessible: incremental value of extra information is not monotone
under changing action sets, and exploration could reveal new patches
at later times. This observer remains privileged about yield-law values.

A source-level test shows the generic recurrent feature map uses only
the first element of the visible resource list. Changing the second
or later visible resources does not change the CURRENT neural input.
This is a concrete perception-to-action bottleneck to investigate, not
proof that an organism can never discover an unseen resource.

## Why these are NOT yet original publication claims

- Conditional neural-population surrogate shuffles are established
  (Elsayed & Cunningham, Nat Neurosci 2017).
- Decodability-versus-causality dissociations are established
  (Tiwari et al., 2026).
- Reservoir performance/emergence relationships are established
  (Tolle et al., Patterns 2026).
- Neural bottlenecks in the evolution of learning rules for foraging agents
  are already studied (Giannakakis et al., Artificial Life 2025,
  DOI 10.1162/artl_a_00458).
- Partial-observability value-of-information and controllability
  constraints are established in reinforcement-learning theory.

The candidate new empirical question is narrower:

> Does action-conditioned perceptual access, rather than forecast
> decodability alone, cause the selection and future behavioral use of
> hidden physical law representations under pure survival rewards?

## Minimum prospective next experiment

**Do not** redesign the rules after seeing results from confirmation worlds.

A factorial study on an independent set of physical worlds should
randomize and compare:

A. Perceptual budget: the current nearest-only resource feature map,
   versus a rank-invariant feature summary of K visible patches;
   match total input dimension, parameter count, interaction costs and
   local environmental sensing radius. A control receives shuffled
   non-nearest resource information at equal capacity.

B. Plasticity: frozen reservoir, output-only, generic recurrent
   state plasticity (rate frozen before outcome access).

C. Ecological forecast opportunity: no resource waves versus an
   ex ante chosen wave strength.

Primary question: whether the incremental fitness effect of state
plasticity depends on *actionable access to resource alternatives*
and changes under genuine temporal forecast pressure. The primary
outcome must be actual harvest/survival under the identical physical
law and energy budget, not decoder NRMSE.

Secondary preregistered measurements:
- Individual state NRMSE beyond raw+clock and foreign/mean hidden,
  evaluated on chronological holdouts.
- Causal use under paired stochastic-replay interventions with
  matched initial action changes and perturbation energy.
- World-seed-level effect heterogeneity; cross-law transfer to
  physics drawn from heldout families.

A statistically persuasive study requires an independently designed
sample size, confidence interval at world-cluster level, meaningful
effect bound and no new tuning on confirmatory worlds. Three pilot
world laws and one agent seed are insufficient.

## Reproducibility

Run from repository root with its environment:

    PYTHONPATH=src OPENBLAS_NUM_THREADS=1 python experiments/civitas_zero/synchrony/local_foresight_pilot.py
    PYTHONPATH=src OPENBLAS_NUM_THREADS=1 python experiments/civitas_zero/synchrony/summarize_pilot.py
    PYTHONPATH=src OPENBLAS_NUM_THREADS=1 python experiments/civitas_zero/synchrony/summarize_modes.py
    PYTHONPATH=src OPENBLAS_NUM_THREADS=1 python experiments/civitas_zero/synchrony/recompute_from_traces.py --check

The full simulator runs that created the NPZ arrays take longer; raw
traces, per-agent outputs and all scripts are archived with this branch.

## Decision

**GO for prospectively testing the affordance/access × plasticity
interaction. NO-GO for claiming current evidence of selected knowledge,
novel mathematics, spontaneously evolved science or consciousness.**
