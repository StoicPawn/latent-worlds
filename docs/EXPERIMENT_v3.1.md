# v3.1 — Independent direct-causal replication

## Goal
Replicate the v3.0 within-agent causal mechanism in an independent evolutionary
history without adding any agent capability or reward.

The replication protocol deliberately separates **mechanistic replication** from
**adaptive replication**. A content-transmission mechanism may replicate while
not improving overall harvest relative to every control.

## Independent history
`world_seed=21`, `agent_seed=0`, standard turnover world profile.

At 800 steps the ordinary readable world has communication-active G2, G3 and G4.
The late assay is preregistered to start at step 500 so it tests the later
generations rather than the founder-heavy early period.

### Same-agent removal assay — G3
- receptions: 83 in the 500–800 assay (90 in the 650–950 stability assay)
- natural broadcasts with paired payload counterfactuals: 33
- mean copy gain: ~+0.00724
- positive copy-gain fraction: ~0.909
- permutation p = 0.01

The effect remains numerically identical in a later 650–950 window, so it is not
an early transient.

### Content transplant — G3
- 33 events
- mean steering gain: ~+0.0592
- positive fraction: 1.00
- permutation p = 0.01

Changing only received content steers the same receiver's outgoing content.

### Matched-context variant reproduction — G3
Two naturally discovered signal variants are injected into the same 103 receiver
contexts.

- variant 0 same-variant reproduction rate: 0 / 103 = 0.000
- variant 1 same-variant reproduction rate: 34 / 103 ≈ 0.330
- spread ≈ 0.330; CV = 1.0

Thus content variants have strongly different causal reproduction rates on the
same agents and contexts.

### Scrambled-content control
In the scrambled-evolution world, G3 does not participate in the communication
circuit during the corresponding late window. The removal and matched-context
selection assays therefore have zero eligible G3 events and do not support the
mechanism.

## Fitness controls
At 800 steps:

| mode | harvest | final population | max generation | births |
|---|---:|---:|---:|---:|
| readable | 2095.94 | 33 | 4 | 45 |
| censored | 1940.35 | 30 | 2 | 39 |
| scrambled | 2230.79 | 33 | 2 | 45 |

Readable beats censorship and reaches deeper generations, but scrambled has
higher cumulative harvest. Therefore v3.1 supports **mechanistic replication**,
not yet a general adaptive advantage of correct content.

## Current claim discipline
We now have two independent histories showing a direct within-agent causal content
mechanism beyond G1: the original `W11×A0` candidate in G2 and `W21×A0` in G3.
This is a meaningful replication of the mechanism, but it is not yet sufficient
to claim an autonomous second evolutionary system because:

1. adaptive superiority over both controls is not replicated;
2. fixation over still deeper generations is not established;
3. the frequency of the phenomenon across the world/population ensemble is unknown.

The next preregistered target is replication of **adaptive** direct-causal
transmission, followed by persistence/fixation rather than adding new agent-side
machinery.
