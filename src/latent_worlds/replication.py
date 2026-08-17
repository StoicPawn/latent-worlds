"""Observer-side replication protocol for direct causal transmission.

This module changes no agent or world dynamics.  It separates two claims that
must not be conflated:

1. mechanistic replication: received content causally steers later outgoing
   content and emergent variants have different matched-context reproduction rates;
2. adaptive replication: the readable-content world also outperforms censorship
   and content scrambling on preregistered demographic/fitness outcomes.

A history may replicate the mechanism while failing the adaptive criterion.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict

from .causal_transmission import (
    direct_reception_transmission_assay,
    counterfactual_payload_transplant_assay,
    causal_variant_reproduction_assay,
)
from .generational_search import communication_depth_probe, turnover_profile
from .phase_map import long_horizon_config
from .world import World
from .metrics import snapshot


@dataclass
class FitnessCondition:
    mode: str
    population: int
    max_generation: int
    births: int
    deaths: int
    total_harvest: float


def _run_fitness(world_seed:int, agent_seed:int, *, mode:str, steps:int,
                 information_level:float, signal_cost:float, overrides:dict|None) -> FitnessCondition:
    cfg=long_horizon_config(
        information_level=float(information_level), signal_cost=float(signal_cost),
        communication_enabled=(mode != "censored"), agent_seed=int(agent_seed),
    )
    for k,v in (overrides or {}).items():
        if not hasattr(cfg,k): raise ValueError(f"unknown SimulationConfig field: {k}")
        setattr(cfg,k,v)
    cfg.communication_scramble=(mode == "scrambled")
    w=World(cfg,seed=int(world_seed)).run(int(steps)); s=snapshot(w)
    return FitnessCondition(mode, int(s['population']), int(s['max_generation']),
                            int(w.births), int(w.deaths), float(s['total_harvest']))


def fitness_content_controls(world_seed:int, agent_seed:int, *, steps:int=800,
                             information_level:float=.35, signal_cost:float=.03,
                             overrides:dict|None=None) -> dict:
    rows={m:asdict(_run_fitness(world_seed,agent_seed,mode=m,steps=steps,
                                information_level=information_level,signal_cost=signal_cost,
                                overrides=overrides))
          for m in ('readable','censored','scrambled')}
    r,c,s=rows['readable'],rows['censored'],rows['scrambled']
    return {
        'conditions':rows,
        'harvest_vs_censored':float(r['total_harvest']-c['total_harvest']),
        'harvest_vs_scrambled':float(r['total_harvest']-s['total_harvest']),
        'population_vs_censored':int(r['population']-c['population']),
        'population_vs_scrambled':int(r['population']-s['population']),
        'generation_vs_censored':int(r['max_generation']-c['max_generation']),
        'generation_vs_scrambled':int(r['max_generation']-s['max_generation']),
        # Conservative adaptive criterion: readable must beat both content controls
        # on cumulative harvest and not lose final population to either.
        'adaptive_supported':bool(r['total_harvest']>c['total_harvest'] and
                                  r['total_harvest']>s['total_harvest'] and
                                  r['population']>=c['population'] and
                                  r['population']>=s['population']),
    }


def direct_replication_followup(world_seed:int, agent_seed:int, *, steps:int=800,
                                assay_start:int=500, min_generation:int=2,
                                information_level:float=.35, signal_cost:float=.03,
                                overrides:dict|None=None, permutations:int=99) -> dict:
    """Run the direct causal replication stack on one preregistered history."""
    common=dict(world_seed=int(world_seed),agent_seed=int(agent_seed),steps=int(steps),
                assay_start=int(assay_start),min_generation=int(min_generation),
                information_level=float(information_level),signal_cost=float(signal_cost),
                config_overrides=dict(overrides or {}))
    removal=direct_reception_transmission_assay(max_events=500,permutations=permutations,**common)
    transplant=counterfactual_payload_transplant_assay(max_events=250,permutations=permutations,**common)
    selection=causal_variant_reproduction_assay(max_events=150,**common)
    scr_removal=direct_reception_transmission_assay(max_events=500,permutations=permutations,
                                                    communication_scramble=True,**common)
    scr_selection=causal_variant_reproduction_assay(max_events=150,communication_scramble=True,**common)
    shared=sorted(set(removal.get('supported_generations',[])) &
                  set(transplant.get('supported_generations',[])))
    mechanistic=bool(shared and selection.get('supported') and
                     not scr_removal.get('supported') and not scr_selection.get('supported'))
    fitness=fitness_content_controls(world_seed,agent_seed,steps=steps,
                                     information_level=information_level,signal_cost=signal_cost,
                                     overrides=overrides)
    return {
        'world_seed':int(world_seed),'agent_seed':int(agent_seed),'steps':int(steps),
        'assay_start':int(assay_start),'min_generation':int(min_generation),
        'supported_generations':shared,
        'mechanistic_replication':mechanistic,
        'adaptive_replication':bool(mechanistic and fitness['adaptive_supported']),
        'removal':removal,'transplant':transplant,'differential_reproduction':selection,
        'scrambled_removal':scr_removal,'scrambled_differential_reproduction':scr_selection,
        'fitness':fitness,
        'claim_level':('adaptive direct-causal replication' if mechanistic and fitness['adaptive_supported']
                       else 'mechanistic direct-causal replication' if mechanistic
                       else 'not replicated'),
    }


def screen_for_late_replication(world_seed:int, agent_seed:int, *, steps:int=800,
                                overrides:dict|None=None,
                                min_emissions:int=8,min_receptions:int=20) -> dict:
    """Cheap prerequisite screen before expensive counterfactual assays."""
    return communication_depth_probe(world_seed,agent_seed,steps=steps,overrides=overrides,
                                     min_emissions=min_emissions,min_receptions=min_receptions)


def standard_turnover_overrides() -> dict:
    """Named world-side profile used in the v2.7-v3.1 replication campaign."""
    return turnover_profile()
