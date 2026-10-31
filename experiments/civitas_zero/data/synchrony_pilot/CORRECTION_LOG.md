# Correction of a secondary pilot negative control

Before the manuscript branch was published, code review found that
the circular time-shift of population-mean hidden states could access
later timestamps, including the held-out future test segment.
This is lookahead and is not a valid negative control.

The corrected surrogate uses ONLY past timestamps, without wraparound.
The original same-time exchange and individual-state comparisons
are unchanged to numerical precision. Raw trajectories are immutable.

| World | Mode | Old leaky lag NRMSE | New past-only lag NRMSE |
|:--|:--|--:|--:|
| W11 | state | 1.59639 | 1.79693 |
| W11 | frozen | 1.44577 | 1.92867 |
| W21 | state | 1.31203 | 2.12186 |
| W21 | frozen | 1.04915 | 1.39344 |

Only derived, never raw, observer-side outputs were recomputed.
All original/within-time-exchange comparisons stayed exactly fixed.
No claim of artificial consciousness, selected prediction or causality.
