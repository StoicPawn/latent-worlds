"""Observer-side attrition accounting for staged emergence searches.

This module does not interact with agents or alter world dynamics.  It only
summarizes how many preregistered histories survive progressively stricter
scientific filters.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
import math

def wilson_interval(successes: int, trials: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if trials <= 0:
        return (0.0, 1.0)
    p = successes / trials
    denom = 1.0 + z*z/trials
    center = (p + z*z/(2.0*trials)) / denom
    half = z*math.sqrt((p*(1-p) + z*z/(4.0*trials))/trials) / denom
    return (max(0.0, center-half), min(1.0, center+half))

@dataclass(frozen=True)
class SearchFunnel:
    screened: int
    late_communication: int
    direct_removal: int
    content_specific: int
    mechanistic_replication: int
    persistent_adaptive_replication: int

    def validate(self) -> None:
        vals = [self.screened, self.late_communication, self.direct_removal,
                self.content_specific, self.mechanistic_replication,
                self.persistent_adaptive_replication]
        if any(v < 0 for v in vals):
            raise ValueError("funnel counts must be non-negative")
        if any(b > a for a,b in zip(vals, vals[1:])):
            raise ValueError("funnel counts must be monotonically non-increasing")

    def summary(self) -> dict:
        self.validate()
        names = ["late_communication","direct_removal","content_specific",
                 "mechanistic_replication","persistent_adaptive_replication"]
        out = {"screened": self.screened}
        for name in names:
            k = getattr(self, name)
            lo, hi = wilson_interval(k, self.screened)
            out[name] = {
                "count": k,
                "fraction_of_screened": (k/self.screened if self.screened else 0.0),
                "wilson_95": [lo, hi],
            }
        return out
