# v4.3 — Prospective full-mechanism follow-up of independent origins

## Motivation

v4.2 prospectively evaluated population seeds A5–A24 in four preregistered W11 conditions. The originally designated A2-discovery condition did not meet its preregistered >=3/20 history-reproducible threshold (2/20), so that primary v4.2 target is negative. However, independent direct-causal origins occurred in all four tested conditions, including preregistered negative boundary controls. Two boundary controls reached the descriptive >=3/20 threshold.

This result does not justify redefining the v4.2 primary endpoint. Instead it motivates a new, explicitly separate follow-up: test whether any of the *prospectively observed independent direct-causal origins* satisfy the stronger mechanism chain.

## Frozen candidate rule

This document is committed before the v4.3 full-mechanism results are observed.

Candidates are read directly from `docs/EXPERIMENT_v4.2_RESULTS.json`. Every A5–A24 history with `supported=true` is eligible. No candidate may be added or removed based on v4.3 outcomes.

This yields the prospective candidate set discovered by v4.2, including candidates from discovery, canonical, and boundary-control conditions. Their v4.2 roles remain labels only and are retained in the output.

## Strong mechanism assay

For every eligible history, run the existing `direct_replication_followup` under the exact W11 ecological condition in which the direct causal origin was observed.

The follow-up records:

1. direct causal replication;
2. real-payload transplant/content-specific steering;
3. matched-context differential reproduction;
4. scrambled-removal control;
5. scrambled differential-reproduction control;
6. readable-vs-censorship and readable-vs-scrambling fitness evidence exposed by the existing replication assay;
7. the assay's `adaptive_replication` and `claim_level` outputs.

No agent capability, reward, learning rule, inheritance mechanism, communication primitive, or world law is changed.

## Claim boundary

The primary v4.3 endpoint is whether at least one A5–A24 candidate satisfies the existing full adaptive-replication criterion. A positive result would constitute a second independent origin of the complete mechanism under a prospectively generated candidate set.

A negative result would imply that direct causal copying is substantially easier to originate than the full persistent-adaptive inheritance mechanism. In that case the next research question becomes identifying which mechanistic step is the dominant bottleneck rather than continuing undirected seed search.
