## v3.7 — pre-transition prediction

No agent/world dynamics changed.  A low-capacity leave-one-history-out model using
t=150 observer snapshots failed to predict the later direct-causal communication
transition (ROC-AUC ~0.14 on the frozen historical set).  Coarse early-state
thresholds are therefore not supported.  The next preregistered target is
trajectory-based early-warning structure, followed by prospective unseen-seed
validation.  See `docs/EXPERIMENT_v3.7.md`.

# Latent Worlds

A minimal artificial-life laboratory for studying whether complex informational, cultural, technological, and eventually epistemic processes can emerge from generic agents interacting with a world whose rules are fixed independently of their objectives.

The core design principle is strict separation between **world structure** and **agent incentives**. The world may contain hidden regularities, resources, spatial geometry, matter, and communication affordances; the agents are selected for survival and reproduction, not for discovering physics, communicating, teaching, or doing science. Any such behaviour must emerge indirectly.

## North Star

The long-run research question is:

> **Can science emerge without being selected for?**

A more operational formulation is:

> Can a population of evolving agents, selected only for survival and reproduction, spontaneously develop a cumulative process for discovering, testing, transmitting, and generalizing true regularities about hidden laws of its universe, without any epistemic objective being specified?

The current branch studies an intermediate transition:

> **Can evolution spontaneously invent a faster form of evolution?**

That is, can a non-genetic information carrier acquire causal replication, variation, differential reproduction, and persistence on a timescale faster than genetic turnover, without an explicit cultural-learning mechanism?

## Current scientific status

The project does **not** currently claim that a second evolutionary system or proto-science has been discovered.

The strongest current result is a small set of rare histories in which received signal content causally changes the content subsequently emitted by the same agent under same-state counterfactual intervention, and where different emergent signal variants show different causal reproduction rates. One history (`W11 × A0`) additionally shows a persistent fitness advantage of readable content over censorship and scrambling across multiple horizons. Independent histories (`W21 × A0`, `W63 × A0`) replicate the mechanistic causal effect but not the full persistent adaptive advantage.

A 64-world independent search in v3.5 found no second persistent adaptive replication, suggesting that the phenomenon is rare under the current protocol. v3.6 rejected simple one-dimensional ecological threshold explanations. v3.7 tested whether coarse early observer snapshots predict the later direct-causal transition; they did not.

## Methodological principle

Interesting-looking correlations are not treated as evidence of emergence. The project progressively introduced stronger controls, including:

- readable vs censored communication;
- payload scrambling during evolution;
- generation-stratified sampling;
- genetic-lineage-conditioned null models;
- continuous payload assays;
- temporal directionality controls;
- same-agent same-instant counterfactual signal removal;
- content transplantation;
- matched-context differential reproduction of signal variants;
- adaptive persistence across multiple horizons;
- preregistered staged search funnels;
- matched world-side ecological interventions.

Several earlier apparent positive results were deliberately rejected after stronger controls showed that they could be explained by genetic predispositions, persistent state, environmental autocorrelation, or scrambled-channel dynamics.

## Repository layout

- `src/latent_worlds/` — simulation engine and observer-side scientific assays.
- `tests/` — regression and methodological tests.
- `examples/` — reproducible benchmark and search scripts.
- `docs/` — experiment reports by version and methodological notes.
- `pyproject.toml` — package metadata and dependencies.

## Installation

```bash
python -m pip install -e .
```

For development/testing:

```bash
python -m pip install -e ".[dev]"
pytest -q
```

## Example

A basic world run:

```bash
PYTHONPATH=src python examples/run_world.py
```

The repository contains specialized benchmark scripts for communication depth, causal transmission, semantic autopsy, secondary-evolution search, adaptive persistence, and transition-condition analysis.

## Scientific caution

This repository is an evolving research codebase. Versioned experiment documents record both positive and negative findings. Results from individual seeds are candidates until they survive independent replication and the relevant causal controls. The project intentionally prefers falsifying an attractive interpretation over preserving it.

## License

See `LICENSE`.
