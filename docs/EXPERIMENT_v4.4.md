# v4.4 — Bottleneck decomposition between mechanism and adaptation

## Motivation

v4.3 prospectively followed every A5–A24 direct-causal origin discovered in v4.2. The preregistered first strong target was not met: 0/11 histories satisfied the existing full adaptive-replication criterion. However, the outcome separated two components that the final claim requires:

- A18 and A20 at W11, active-obstacle fraction 0.75, signal cost 0.03 produced mechanistic direct-causal replication but no adaptive advantage;
- A15 at W11, active-obstacle fraction 1.00, signal cost 0.03 produced adaptive fitness support but did not reproduce the full mechanistic criterion.

The next experiment therefore asks whether the missing coincidence is a narrow ecological bottleneck rather than a need for new agent machinery.

## Frozen design

This experiment is preregistered before its results are observed. No agent capability, reward, learning rule, inheritance mechanism, communication primitive, mutation operator, or world law is added or changed.

Three histories are fixed from v4.3: A18, A20 (mechanism-positive/adaptation-negative) and A15 (adaptation-positive/mechanism-negative). For each history we scan a local world-side neighbourhood only:

- active-obstacle fraction: 0.70, 0.75, 0.80, 0.90, 1.00
- signal cost: 0.020, 0.025, 0.030, 0.035, 0.040

This is 25 conditions per history and 75 total cells. The same full `direct_replication_followup` assay is run in every cell with 650 steps, assay start 250, minimum generation 2, information level 0.35, and 99 permutations.

## Endpoints

For every cell record separately:

1. direct causal support;
2. payload-transplant/content-specific support;
3. differential reproduction;
4. scrambled controls;
5. mechanistic replication;
6. adaptive fitness support;
7. full adaptive replication.

The primary endpoint is at least one full adaptive replication in this frozen 75-cell local neighbourhood.

Secondary endpoint: quantify the overlap geometry between mechanistic-positive and adaptive-positive cells. Even if the primary endpoint is negative, this determines whether the two ingredients approach one another continuously, occupy disjoint regions, or trade off across the ecological surface.

## Claim boundary

A positive cell is a targeted ecological rescue of a prospectively identified independent history; it is not by itself a population-level prevalence estimate. A negative result falsifies the simple local-overlap hypothesis and motivates mechanistic trajectory comparison rather than a wider undirected parameter search.
