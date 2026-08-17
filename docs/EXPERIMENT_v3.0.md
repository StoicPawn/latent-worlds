# v3.0 — Direct causal transmission

## Question
Can a non-genetic information carrier show direct causal replication, variation and differential reproduction inside later generations, after the apparent v2.7 signal was shown to be confounded by genetic lineage?

## Methodological change
No agent or world capability was added. Instead, reception-to-transmission is tested within the **same agent, same instant, same world state and same RNG state**.

Three counterfactual observer-side assays are used:

1. **Signal removal:** compare the naturally emitted payload with the payload the same receiver would emit if its received transient signals were removed. A positive `copy_gain` means the received payload causally pulls the outgoing payload toward itself.
2. **Payload transplant:** replace the received content with an empirically observed donor payload while keeping the receiver and context fixed. A positive steering gain means outgoing content is causally steered toward the transplanted content.
3. **Matched-context variant reproduction:** inject each naturally discovered variant into the exact same receiver/context set and measure the probability that the outgoing signal is classified as the injected variant. Differences are therefore causal effects of variant content rather than population composition.

## Primary candidate: W11 × A0, turnover ecology
The pre-existing turnover profile is used (`reproduction_threshold=15`, `reproduction_cost=6`, `resource_regrowth=0.07`).

### G2 direct removal assay
At 600 steps, G2 has 218 natural reception events and 76 natural broadcasts suitable for payload comparison.

- mean payload effect when signals are removed: ~0.0438
- mean copy gain: ~+0.0270
- positive copy-gain fraction: ~0.724
- permutation p = 0.01

The effect remains later in history (450–900-step window): mean copy gain ~+0.0114, positive fraction ~0.726, p=0.01.

In the payload-scrambled evolutionary control, G2 receives signals but produces no natural broadcasts in the matched assay window; the direct-copy criterion is not supported.

### G2 content-transplant assay
77 G2 natural-broadcast events were counterfactually exposed to donor payloads drawn from other real receptions:

- mean steering gain ~+0.0397
- 97.4% of events positive
- permutation p=0.01

The scrambled evolutionary control has only one eligible G2 event and does not support the assay.

### G2 causal differential reproduction
Each of two emergent signal variants was injected into the **same 180 receiver/context events**.

Real evolutionary history:

- variant 0 reproduction rate: 8/180 = 0.0444
- variant 1 reproduction rate: 42/180 = 0.2333
- spread = 0.1889
- CV = 0.68

Scrambled evolutionary control:

- rates ≈0.0056 and 0.0
- spread ≈0.0056
- criterion fails

Thus the earlier differential-propagation signal is no longer attributable merely to different genetic families occupying different contexts: the same receivers and contexts reproduce different injected variants at substantially different rates.

## Replication search
Independent deep-genealogy histories W3×A0, W3×A2, W0×A3, W0×A4, W11×A1, W11×A2, W12×A0 and W13×A0 do not replicate the direct G2 effect at the tested horizons. Most later-generation agents receive but do not naturally broadcast enough for the assay.

## Current interpretation
W11×A0 is the first candidate in the project with **direct within-agent causal content transmission in G2**, causal content steering, and matched-context differential variant reproduction, all absent/collapsed under payload scrambling. This repairs the genetic-lineage confound that invalidated the v2.7 interpretation.

It is **not yet a discovery of an autonomous second evolutionary system** because independent replication is missing. The next preregistered requirement is at least one independent world×population history showing the same direct G2+ signature.
