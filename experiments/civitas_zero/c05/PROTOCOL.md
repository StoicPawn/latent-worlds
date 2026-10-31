# C0.5 — Before measuring introspection, can we identify its cause?

**Status:** completed first pilot on two pre-existing exploratory world laws
(W11/W21); publication-level result NOT achieved.

### Theory motivation

HOT-2/3-like and broader metacognitive theories often require
more than accurate reports of task uncertainty. We want to test
whether a system can build and CAUSALLY USE information that
differentiates changes in its own inference mechanism from changes
outside it. That does NOT, on its own, prove phenomenal consciousness.

The closest prior art is stronger than a simple lesion demo:
Phua (arXiv:2512.19155, 2025) already reported selective
metacognitive deficits under self-model lesions with preserved
first-order competence; Kumaran (Nat Mach Intell 2026) causally
linked confidence to abstention; Tang (arXiv:2610.38911, 2026)
studied interventional introspection and causal bypass.
**The C0.5 algebra below is classical and is not a novel self-model.**

### Exact intervention

An existing, ecologically evolved recurrent controller has
\`h_{t+1}=tanh(W_in x_t + W_rec h_t)\` with 12D internal state. Its
temperature feature is \`x_t[1]=temperature/20\`.

Given \`h_t≠0\`, set
\`ΔW_rec=δ W_in[:,1] h_t^T/(h_t^T h_t)\` with \`δ=.25\`.

In the **internal** arm, use unchanged \`x_t\` but
\`W_rec+ΔW_rec\`. In the **external** arm, preserve \`W_rec\` but
replace temperature by temperature+5, so the temperature feature
changes by \`δ\`. Exact preactivations at the first step:
\`(W_rec+ΔW_rec)h_t + W_in x_t
 = W_rec h_t + W_in(x_t+δ e_temperature)\`.

They therefore produce the same h, W_out logits and action for a
fixed random-number stream at t+1, BY CONSTRUCTION. Two variants:

- **Persistent internal lesion:** leave W_rec changed after first step,
  but remove the transient external sensor perturbation.
- **Transient internal lesion:** restore W_rec after first step.
  Under identical following observations the two latent, logit and
  action trajectories must remain identical (control).

### Scope and controls

- Real Latent Worlds organisms from W11 and W21, population seed A211,
  warmup=145 steps, next 6 observations from unchanged world.
- No change to world code, reward rules or baseline experiments.
- Exact numerical equality checks for first-step preactivation,
  hidden vector, logits and action category. Test transient replay
  for the expected numerical null.
- The subsequent input stream is an OPEN-LOOP observational replay
  of the actual unmodified world. It is not a branch of a fully
  counterfactual ecological simulation.
- Critically, **raw sensory observations are NOT identical** at the
  intervention step: the external temperature is different. A
  temperature-monitoring comparator with access to the unperturbed
  baseline trivially detects the cause. We therefore have NOT
  controlled the full agent-accessible history, and have not built
  a valid self/world metacognitive identification benchmark.
- The perturbation is tuned algebraically to the agent's current
  hidden state; it is an intentionally constructed fixture, not a
  plausible distribution of natural faults.
- Agents share a world and cannot be counted as independent
  physical-law replicates.
- No agent has learned a causal self-model or a fault-adaptive
  decision rule in this experiment.

### Prospective C1 gate: not started

To support a publishable **functional-indicator specificity** result,
we must first define internal-vs-external faults that have matched
agent-accessible information, early task difficulty and action damage,
without disclosing fault cause in raw observations. Test whether an
appropriate response is possible under the available information;
compare external-only, confidence-only, time-yoked peer, equal-budget
sham and internal self-state routes. Train only with ecological
survival reward and show actual paired external task benefit on
independent new world laws and held-out fault types.

If the same information available to a rival policy suffices, or
the intervention type is directly encoded in the input, a
HOT-aligned endogenous self-model interpretation is NO-GO. If
there is no ecological value of different responses, it is also
NO-GO. Passing future C1 would still not demonstrate phenomenal
consciousness.

### Reproduction

From repo root with project's environment:

    PYTHONPATH=src:. python experiments/civitas_zero/c05/matched_faults.py --world 11 --output-dir /tmp/c05_replay
    PYTHONPATH=src:. python experiments/civitas_zero/c05/matched_faults.py --world 21 --output-dir /tmp/c05_replay
    PYTHONPATH=src:. python experiments/civitas_zero/c05/summarize.py
    PYTHONPATH=src:. pytest -q tests/test_civitas_c05_identifiability.py

Data directory \`data/\`: original persistent-only pilot outputs retained;
\`data_transient/\`: subsequent independently rerun paired
persistent/transient controls. Neither is a confirmatory experiment.

**Literature:** Butlin et al. (2026) DOI
10.1016/j.tics.2025.10.011; Phua (2025) arXiv:2512.19155;
Butlin et al. (2026) DOI 10.1016/j.tics.2026.04.006;
Kumaran et al. (2026) DOI 10.1038/s42256-026-01293-x;
Tang et al. (2026) arXiv:2610.38911.
