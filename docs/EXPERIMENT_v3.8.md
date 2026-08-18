# v3.8 — Prospective trajectory prediction

No agent capability, objective, reward, learning rule, physical law or communication primitive changed.

## Question
Can a future direct-causal non-genetic information-transmission transition be predicted from early observer-side dynamics rather than a single early snapshot?

## Protocol
The historical training set was frozen before the prospective test: 26 previously assayed histories, including 5 direct-removal positives. Early trajectories were sampled before the late-generation causal assay and converted into transparent dynamical features (level, slope, variance, lag-1 autocorrelation) over preregistered observer variables.

The model then ranked previously unseen world seeds W202–W225. Only after ranking were the 6 highest-scored and 6 lowest-scored seeds subjected to the expensive direct same-agent causal-removal assay.

## Result
Historical leave-one-history-out ROC-AUC was approximately 0.457, i.e. no useful retrospective discrimination.

Prospectively:

- top-ranked tested seeds: W215, W216, W209, W206, W204, W211;
- bottom-ranked tested seeds: W203, W223, W205, W202, W210, W219;
- direct-removal hits in top group: 0/6;
- direct-removal hits in bottom group: 0/6.

Therefore there was no prospective enrichment.

## Interpretation
The trajectory-based early-warning hypothesis, as operationalised here, is not supported. This is not evidence that the transition is fundamentally unpredictable. It does show that coarse population-level trajectories over the tested early window are insufficient for a useful predictor.

Combined with v3.6, the project now has two negative results against simple observational precursors:

1. coarse early snapshots do not predict the transition;
2. coarse early trajectories do not predict the transition.

The next step should therefore become causal rather than predictive: map the local basin around the canonical W11 history using matched world-side interventions that preserve initialized physics/resources wherever possible.

The machine-readable result is retained in `docs/EXPERIMENT_v3.8_RESULTS.json`.
