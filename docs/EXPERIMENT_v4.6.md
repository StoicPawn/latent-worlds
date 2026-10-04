# v4.6 — Decoder-capacity control for predictive representation

## Motivation

v4.5 prospectively tested A25–A34 under one fixed W11 physics realization. The result was uniformly negative for the preregistered predictive-representation criterion: 0/10 histories beat the contemporaneous raw-physics baseline.

That result is retained unchanged.

However, v4.5 compared a 6-dimensional raw decoder with a 48-dimensional collective-state decoder under one fixed ridge penalty. The negative result could therefore be partly attributable to unequal effective decoder capacity or overfitting.

v4.6 is a new prospective experiment that removes this ambiguity without modifying agents or world dynamics.

## Primary question

**Does any independent population history contain future-physics information beyond the raw observable baseline after decoder complexity is controlled using past-only model selection?**

## Frozen population set

- world: W11
- new population histories: A35–A44
- steps: 1200
- burn-in: 200
- observer stride: 5
- future forcing horizons: 10, 35, 70
- information level: 0.35
- signal cost: 0.03
- active-obstacle fraction: 0.75
- standard turnover profile

A35–A44 are not used in v4.5.

## Three representations

Each history is evaluated using exactly three observer-side feature sets:

1. raw contemporaneous surface summary — 6 dimensions;
2. population mean recurrent hidden state — 12 dimensions;
3. population distributional recurrent summary — 48 dimensions.

The hidden-mean representation is added because it reduces the dimensionality imbalance while remaining a direct internal-state diagnostic.

## Nested temporal ridge protocol

For each representation independently, ridge alpha is selected from the frozen grid:

- 0.0001
- 0.001
- 0.01
- 0.1
- 1
- 10
- 100

Selection uses only the past.

The first 65% of the time series is the development prefix. Within that prefix, the first 70% is used to fit candidate penalties and the remaining 30% to choose alpha.

After selection, the chosen decoder is refit on the entire 65% development prefix and evaluated once on the untouched final 35%.

The final test suffix is never used for alpha selection.

## Endpoint

For each history:

- report raw normalized RMSE;
- report hidden-mean normalized RMSE;
- report collective normalized RMSE;
- select the better of the two internal representations;
- compute predictive gain over raw.

A history is a weak 'predictive representation candidate' only if:

- at least 80 observer samples are available; and
- the best internal representation improves normalized RMSE over raw by more than 3%.

This remains an E1-like diagnostic only. It does not establish collective excess, causal social dependence, cumulative epistemic inheritance, experimentation, law generalisation, spontaneous science, or Stage-II convergence.

## Decision rule

If v4.6 remains 0/10, the working conclusion is that the present recurrent substrate/ecology does not yet produce detectable future-law representation under this assay. The next work should return to Stage-I mechanism/ecology rather than expanding Stage-II comparisons.

If one or more candidates appear, they are discovery candidates only. A separate prospective replication on new population seeds is required before any stronger epistemic claim.
