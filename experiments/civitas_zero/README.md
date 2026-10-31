# CIVITAS ZERO / Latent Worlds — prospective v5.4

This is an **independent preregistered research extension**, not a new world simulator.
Parent source commit: `2cca2dc019541f296285b75daa8e416c7818b15e` (unchanged world/agents).
The v5.3 discovery grid used W11/A89–A92 and selected state-plasticity rate 0.0003; none of these seed results count as confirmatory evidence.

Frozen v5.4: W11, agent seeds A93–A108 inclusive; three matched conditions
`frozen`, `output_only`, `state` with rate 0.0003. Each runs 1200 world steps,
burn-in=200, stride=2, prediction horizons (10,35,70) and carrier min_samples=80.

Primary gate: full eligibility, positive paired mean carrier fraction improvement over BOTH baselines,
exact one-sided sign p <= 0.05 for BOTH; no mean harvest loss vs output_only.
This is a within-world research gate, not E1 certification. No civiliation/consciousness claim.

To run (use the repository virtualenv, do not install global packages):

```bash
PYTHONPATH=src OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python experiments/civitas_zero/benchmark_v54_prospective.py --seed 93 --output-dir artifacts/v54_prospective
PYTHONPATH=src OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python experiments/civitas_zero/benchmark_v54_prospective.py --aggregate-only --output-dir artifacts/v54_prospective
```

Repeat for 93..108; do not retune using confirmation seeds. Script refuses to overwrite prior seed outputs. The exact run manifest records immutable source commit. Results stay local until reviewed and independently archived.
Follow-up if the gate passes: preregister W21 transfer with new population seeds, not just more W11 seeds.
