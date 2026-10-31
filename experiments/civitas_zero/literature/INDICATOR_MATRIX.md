# Theory-derived indicators relevant to AI consciousness

**Literature verified through 2026-10-31.**
Canonical IDs come from Butlin et al. (2023, 2026), not CIVITAS ZERO.
The following are engineering **paraphrases** and example falsifying
countermodels, not validated sufficient conditions for experience.

All indicators are **NOT ASSESSED**. C1, C2 and C3 are our own experimental
assay groupings; they are *not* Butlin's official indicator categories.
Indicators overlap and can have dependencies; summing passes would be misleading.

Main source: [Butlin et al. 2026](https://doi.org/10.1016/j.tics.2025.10.011)

## Recurrent Processing (RPT)

| ID | Engineering interpretation | Naive false-positive mechanism | Proposed assay | Status |
|:--|:--|:--|:--|:--|
| **RPT-1** | Local, functionally relevant recurrent computation inside input/perceptual modules | A recurrent hidden state that never changes perceptual representations | C2 | NOT_ASSESSED |
| **RPT-2** | Structured integration of perceptual information within input processing | A simple concatenation of independent sensory channels | C2 | NOT_ASSESSED |

## Global Workspace (GWT)

| ID | Engineering interpretation | Naive false-positive mechanism | Proposed assay | Status |
|:--|:--|:--|:--|:--|
| **GWT-1** | Parallel operation of multiple genuinely specialized processing subsystems | A stack of nominal modules all computing the same fixed feature | C2 | NOT_ASSESSED |
| **GWT-2** | Selective bottleneck or finite-capacity shared workspace | A fixed one-slot tensor whose content is always the same winner | C2 | NOT_ASSESSED |
| **GWT-3** | Workspace content made functionally available across specialized modules | A broadcast operation that no downstream module actually uses | C2 | NOT_ASSESSED |
| **GWT-4** | Attention contingent on internal state and serial querying of specialist modules | An unchanging round-robin scheduler or constant attention bids | C2 | NOT_ASSESSED |

## Higher-Order / Metacognitive (HOT)

| ID | Engineering interpretation | Naive false-positive mechanism | Proposed assay | Status |
|:--|:--|:--|:--|:--|
| **HOT-1** | Perceptual representation with generative, top-down or uncertainty-sensitive processing | A noisy sensor followed by a feedforward classifier | C1 | NOT_ASSESSED |
| **HOT-2** | Metacognitive discrimination of reliable perception from unreliable signals | A post-hoc output confidence value entirely explained by logits | C1, C3 | NOT_ASSESSED |
| **HOT-3** | Belief and action updates that causally depend on metacognitive monitoring | A label-reading monitor disconnected from actual decisions | C1, C3 | NOT_ASSESSED |
| **HOT-4** | Representations with structured sparse and continuous quality-like dimensions | A sparse vector renamed 'qualia' without tested quality-space structure | No experiment proposed | NOT_ASSESSED |

## Attention Schema (AST)

| ID | Engineering interpretation | Naive false-positive mechanism | Proposed assay | Status |
|:--|:--|:--|:--|:--|
| **AST-1** | An internal predictive model of attentional state that actively controls attention | A self-state monitor with no access to attention allocation | C3 | NOT_ASSESSED |

## Predictive Processing (PP)

| ID | Engineering interpretation | Naive false-positive mechanism | Proposed assay | Status |
|:--|:--|:--|:--|:--|
| **PP-1** | Perception based on internal predictive-coding dynamics | A predictor trained on future reward without error-driven perceptual updating | C3 | NOT_ASSESSED |

## Agency / Embodiment (AE)

| ID | Engineering interpretation | Naive false-positive mechanism | Proposed assay | Status |
|:--|:--|:--|:--|:--|
| **AE-1** | Feedback-driven agency flexible across multiple competing goals | A fixed hard-coded success policy in a single task | C1 | NOT_ASSESSED |
| **AE-2** | Model of sensorimotor action-to-observation contingencies used for control | A map of world state that never predicts effects of the agent's own actions | C1 | NOT_ASSESSED |

## Theory-to-engineering dependencies (caution, not a proof)

Butlin et al. describe overlapping conditions (including GWT-3/4 and
RPT-1); dependencies are not statistically independent 'votes'.

- **GWT-2**: consider GWT-1.
- **GWT-3**: consider GWT-1, GWT-2, RPT-1.
- **GWT-4**: consider GWT-1, GWT-2, GWT-3, RPT-1.
- **HOT-2**: consider HOT-1.
- **HOT-3**: consider HOT-1, HOT-2, AE-1.
- **PP-1**: consider RPT-1, HOT-1.

## Methods and interpretation

See [critical review](REVIEW_2026-10-31.md),
[adversarial predictions](THEORY_ADJUDICATION.md) and
[source ledger](SOURCES.json). Functional computation may shift
credences under a theory but cannot establish substrate-independent
phenomenal consciousness or justify a numeric 'proto-consciousness score'.

**No C1/C2/C3 experiments have been run.** Historical population and
foraging results are *not* consciousness-indicator evidence.
