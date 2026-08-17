"""Observer-side persistence tests for adaptive content effects.

No agent/world dynamics are changed.  The module asks whether a history that
passes a causal communication assay also beats censorship and payload scrambling
at several preregistered horizons, rather than at a single cherry-picked endpoint.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict

from .replication import fitness_content_controls, standard_turnover_overrides


@dataclass
class HorizonAdaptiveResult:
    steps: int
    harvest_vs_censored: float
    harvest_vs_scrambled: float
    population_vs_censored: int
    population_vs_scrambled: int
    adaptive_supported: bool


def adaptive_persistence_assay(world_seed:int, agent_seed:int, *,
                               horizons=(500,650,800), overrides:dict|None=None,
                               information_level:float=.35, signal_cost:float=.03) -> dict:
    """Require readable content to beat both controls at every fixed horizon."""
    ov=dict(standard_turnover_overrides() if overrides is None else overrides)
    rows=[]
    for h in horizons:
        r=fitness_content_controls(world_seed,agent_seed,steps=int(h),
                                   information_level=information_level,
                                   signal_cost=signal_cost,overrides=ov)
        rows.append(HorizonAdaptiveResult(
            steps=int(h),
            harvest_vs_censored=float(r['harvest_vs_censored']),
            harvest_vs_scrambled=float(r['harvest_vs_scrambled']),
            population_vs_censored=int(r['population_vs_censored']),
            population_vs_scrambled=int(r['population_vs_scrambled']),
            adaptive_supported=bool(r['adaptive_supported']),
        ))
    support=[x.adaptive_supported for x in rows]
    return {
        'world_seed':int(world_seed),'agent_seed':int(agent_seed),
        'horizons':[int(x) for x in horizons],
        'results':[asdict(x) for x in rows],
        'all_horizons_supported':bool(rows and all(support)),
        'supported_fraction':float(sum(support)/len(support)) if support else 0.0,
        'criterion':'readable beats censorship and scrambling on harvest and does not lose population at every preregistered horizon',
    }
