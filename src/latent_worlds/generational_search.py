"""Observer-side search for generational depth without cognitive shaping.

The search changes only demographic/ecological parameters of the world and then
asks whether previously observed communication mechanisms survive transfer to a
higher-turnover ecology.  A deeper genealogy is not considered evidence if the
semantic signature disappears or is matched by a scrambled-payload control.
"""
from __future__ import annotations

from .phase_map import long_horizon_config
from .world import World
from .metrics import snapshot
from .semantic_autopsy import counterfactual_content_assay_single_pass


def turnover_profile(*, reproduction_threshold=15.0, reproduction_cost=6.0,
                     resource_regrowth=0.07) -> dict:
    return {
        "reproduction_threshold": float(reproduction_threshold),
        "reproduction_cost": float(reproduction_cost),
        "resource_regrowth": float(resource_regrowth),
    }


def genealogy_probe(world_seed: int, agent_seed: int, *, steps=1200,
                    information_level=.35, signal_cost=.03,
                    overrides: dict | None = None) -> dict:
    cfg=long_horizon_config(information_level=information_level, signal_cost=signal_cost,
                            communication_enabled=True, agent_seed=int(agent_seed))
    for k,v in (overrides or {}).items():
        if not hasattr(cfg,k):
            raise ValueError(f"unknown SimulationConfig field: {k}")
        setattr(cfg,k,v)
    w=World(cfg,seed=int(world_seed)).run(int(steps)); s=snapshot(w)
    return {
        "world_seed":int(world_seed),"agent_seed":int(agent_seed),"steps":int(steps),
        "population":int(s["population"]),"max_generation":int(s["max_generation"]),
        "births":int(w.births),"deaths":int(w.deaths),"total_harvest":float(s["total_harvest"]),
        "overrides":dict(overrides or {}),
    }


def semantic_transfer_probe(world_seed: int, agent_seed: int, *, steps=850,
                            information_level=.35, signal_cost=.03,
                            overrides: dict | None = None, max_events=350,
                            min_generation_events=25) -> dict:
    common=dict(world_seed=int(world_seed),agent_seed=int(agent_seed),steps=int(steps),
                information_level=float(information_level),signal_cost=float(signal_cost),
                max_events=int(max_events),min_generation_events=int(min_generation_events),
                config_overrides=dict(overrides or {}))
    real=counterfactual_content_assay_single_pass(communication_scramble=False,**common)
    scrambled=counterfactual_content_assay_single_pass(communication_scramble=True,**common)
    ra=real.get("intergenerational_amplification")
    sa=scrambled.get("intergenerational_amplification")
    return {
        "world_seed":int(world_seed),"agent_seed":int(agent_seed),"steps":int(steps),
        "overrides":dict(overrides or {}),"real":real,"scrambled":scrambled,
        "amplification_advantage":None if ra is None or sa is None else float(ra-sa),
        # A transfer claim requires *positive* real intergenerational amplification;
        # merely being less negative than the scrambled control is not evidence.
        "transfer_supported":bool(ra is not None and sa is not None and ra>0.0 and ra>sa and real.get("paired_sign_p",1.0)<=.05),
    }


def communication_depth_probe(world_seed: int, agent_seed: int, *, steps=700,
                              information_level=.35, signal_cost=.03,
                              overrides: dict | None = None,
                              min_emissions=8, min_receptions=20) -> dict:
    """Cheap observer-side screen for *communicative* generational depth.

    Genealogical depth alone is not informative if later generations never emit or
    receive signals. This probe runs the ordinary world once and counts broadcast
    emissions and signal-reception decisions by generation. Nothing is exposed to
    agents and no dynamics are changed.
    """
    cfg=long_horizon_config(information_level=information_level, signal_cost=signal_cost,
                            communication_enabled=True, agent_seed=int(agent_seed))
    for k,v in (overrides or {}).items():
        if not hasattr(cfg,k):
            raise ValueError(f"unknown SimulationConfig field: {k}")
        setattr(cfg,k,v)
    w=World(cfg,seed=int(world_seed)).run(int(steps)); s=snapshot(w)
    from collections import Counter
    emissions=Counter(int(e["generation"]) for e in w.communication_log if e["type"]=="broadcast")
    receptions=Counter(int(e["generation"]) for e in w.social_log if e.get("received_count",0)>0)
    gens=sorted(set(emissions)|set(receptions))
    active=[g for g in gens if emissions[g]>=int(min_emissions) and receptions[g]>=int(min_receptions)]
    return {
        "world_seed":int(world_seed), "agent_seed":int(agent_seed), "steps":int(steps),
        "population":int(s["population"]), "max_generation":int(s["max_generation"]),
        "births":int(w.births), "deaths":int(w.deaths),
        "emissions_by_generation":{str(g):int(emissions[g]) for g in gens},
        "receptions_by_generation":{str(g):int(receptions[g]) for g in gens},
        "communication_active_generations":active,
        "max_communication_generation":max(active) if active else None,
        "communication_depth":len(active),
        "late_generation_communication":bool(any(g>=2 for g in active)),
        "overrides":dict(overrides or {}),
    }
