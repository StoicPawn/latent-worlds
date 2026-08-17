"""Observer-side causal tests for emergent behavioural interdependence.

No agent objective or controller is modified during the main simulation.  At an
analysis checkpoint we clone the entire world state, remove a behaviourally
identified subgroup, and compare the subsequent per-capita performance of the
remaining population with matched random removals of the same size.

This distinguishes mere behavioural heterogeneity from functional dependence:
a putative role matters only if other agents systematically do worse when that
role is absent than when an equally large random subset is absent.
"""
from __future__ import annotations

import copy
from collections import defaultdict
import numpy as np

_ACTIONS = ("move", "harvest", "rest", "broadcast", "inscribe", "pickup", "drop")


def action_profile(agent):
    c = np.asarray([agent.action_counts.get(k, 0) for k in _ACTIONS], dtype=float)
    s = float(c.sum())
    return c / s if s > 0 else np.zeros(len(_ACTIONS), dtype=float)


def dominant_role(agent, min_actions: int = 40):
    p = action_profile(agent)
    if p.sum() == 0 or sum(agent.action_counts.values()) < min_actions:
        return None
    return _ACTIONS[int(np.argmax(p))]


def _kill_ids(world, ids):
    ids = set(ids)
    for a in world.agents:
        if a.id in ids and a.alive:
            a.alive = False
            if a.held_object_id is not None:
                obj = next((o for o in world.objects if o.id == a.held_object_id), None)
                if obj is not None:
                    obj.holder_id = None
                    obj.x, obj.y = a.x, a.y
                a.held_object_id = None


def _integrated_population_run(world, horizon: int):
    h0 = float(sum(a.total_harvest for a in world.agents))
    b0 = int(world.births)
    pop_area = 0.0
    for _ in range(horizon):
        living = sum(a.alive for a in world.agents)
        if living <= 0:
            break
        pop_area += living
        world.step()
    h1 = float(sum(a.total_harvest for a in world.agents))
    births = int(world.births) - b0
    final_pop = sum(a.alive for a in world.agents)
    steps = max(1, min(horizon, world.time))
    # Harvest per agent-step is the cleanest productivity quantity available here.
    productivity = (h1 - h0) / max(pop_area, 1.0)
    birth_rate = births / max(pop_area, 1.0)
    return {
        "harvest_delta": h1 - h0,
        "births": births,
        "final_population": final_pop,
        "agent_steps": pop_area,
        "harvest_per_agent_step": productivity,
        "births_per_agent_step": birth_rate,
    }


def _matched_random_ids(living, target_agents, rng):
    """Energy/age-stratified random removal, matched approximately to target role."""
    pool = [a for a in living if a.id not in {t.id for t in target_agents}]
    if len(pool) < len(target_agents):
        pool = list(living)
    chosen=[]
    available=list(pool)
    # Greedy Mahalanobis-lite match on standardized age and energy.
    ages=np.asarray([a.age for a in living],dtype=float)
    ens=np.asarray([a.energy for a in living],dtype=float)
    sa=max(float(np.std(ages)),1.0); se=max(float(np.std(ens)),1.0)
    for t in target_agents:
        if not available:
            break
        d=np.asarray([((a.age-t.age)/sa)**2+((a.energy-t.energy)/se)**2 for a in available],dtype=float)
        m=float(np.min(d))
        candidates=np.flatnonzero(np.isclose(d,m))
        j=int(rng.choice(candidates))
        chosen.append(available.pop(j))
    return [a.id for a in chosen]


def role_interdependence(world, horizon: int = 150, min_role_size: int = 3,
                         min_actions: int = 40, random_controls: int = 8,
                         seed: int = 99173):
    """Causally screen emergent roles at the current world state.

    Returns role-specific effects relative to energy/age-matched random removals.
    Positive `productivity_dependency` means the *remaining* population is less
    productive when that role is removed than under matched random removal.
    """
    living=[a for a in world.agents if a.alive]
    by_role=defaultdict(list)
    for a in living:
        r=dominant_role(a,min_actions=min_actions)
        if r is not None:
            by_role[r].append(a)

    rng=np.random.default_rng(seed + int(world.time))
    results={}
    for role, members in sorted(by_role.items()):
        if len(members) < min_role_size or len(members) >= len(living)-2:
            continue
        branch=copy.deepcopy(world)
        _kill_ids(branch,[a.id for a in members])
        role_out=_integrated_population_run(branch,horizon)

        controls=[]
        for _ in range(random_controls):
            ids=_matched_random_ids(living,members,rng)
            c=copy.deepcopy(world)
            _kill_ids(c,ids)
            controls.append(_integrated_population_run(c,horizon))
        cp=np.asarray([x["harvest_per_agent_step"] for x in controls],dtype=float)
        cb=np.asarray([x["births_per_agent_step"] for x in controls],dtype=float)
        productivity_dependency=float(np.mean(cp)-role_out["harvest_per_agent_step"])
        birth_dependency=float(np.mean(cb)-role_out["births_per_agent_step"])
        # Standardized effect against null spread; finite even for near-zero spread.
        pz=productivity_dependency/max(float(np.std(cp)),1e-6)
        bz=birth_dependency/max(float(np.std(cb)),1e-6)
        results[role]={
            "role_size":len(members),
            "role_fraction":len(members)/max(len(living),1),
            "role_removed":role_out,
            "control_mean_harvest_per_agent_step":float(np.mean(cp)),
            "control_sd_harvest_per_agent_step":float(np.std(cp)),
            "control_mean_births_per_agent_step":float(np.mean(cb)),
            "control_sd_births_per_agent_step":float(np.std(cb)),
            "productivity_dependency":productivity_dependency,
            "birth_dependency":birth_dependency,
            "productivity_z":float(pz),
            "birth_z":float(bz),
            "candidate_interdependence":bool(productivity_dependency>0 and pz>=2.0),
        }
    return {
        "time":int(world.time),
        "living_population":len(living),
        "roles_tested":len(results),
        "roles":results,
        "candidate_roles":[r for r,x in results.items() if x["candidate_interdependence"]],
    }
