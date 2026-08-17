"""Observer-only longitudinal emergence analysis.

This module adds no agent capability and no fitness signal.  It watches a world
through time and asks a stricter question than a final snapshot: did a new
population-level organization appear abruptly, persist, and survive null-like
fluctuations?
"""
from __future__ import annotations

from dataclasses import dataclass
from collections import Counter, defaultdict
import math
import numpy as np

from .config import SimulationConfig
from .metrics import snapshot
from .world import World


def _f(x, default=0.0):
    try:
        x = float(x)
        return x if np.isfinite(x) else default
    except (TypeError, ValueError):
        return default


def _action_profile(agent):
    names = ("move", "harvest", "rest", "broadcast", "inscribe", "pickup", "drop")
    c = np.asarray([agent.action_counts.get(k, 0) for k in names], dtype=float)
    s = c.sum()
    return c / s if s > 0 else np.zeros(len(names), dtype=float)


def _lineage_metrics(world):
    by_id = {a.id: a for a in world.agents}
    distances = []
    same_dominant = []
    cross_generation_pairs = 0
    for child in world.agents:
        if child.parent_id is None or child.parent_id not in by_id:
            continue
        parent = by_id[child.parent_id]
        p, q = _action_profile(parent), _action_profile(child)
        if p.sum() == 0 or q.sum() == 0:
            continue
        distances.append(float(np.abs(p-q).sum()/2.0))
        same_dominant.append(int(np.argmax(p) == np.argmax(q)))
        cross_generation_pairs += 1
    return {
        "parent_child_pairs": cross_generation_pairs,
        "mean_parent_child_action_distance": float(np.mean(distances)) if distances else None,
        "dominant_action_inheritance": float(np.mean(same_dominant)) if same_dominant else None,
    }


def _generation_specialization(world):
    """Observer-only evidence for stable behavioural niches across generations."""
    by_gen = defaultdict(list)
    # Only currently living agents can constitute a present population-level niche.
    # Dead ancestors remain available through lineage logs but must not inflate
    # contemporary specialization.
    for a in world.agents:
        if a.alive and sum(a.action_counts.values()) >= 20:
            by_gen[a.generation].append(_action_profile(a))
    summaries = {}
    for g, rows in by_gen.items():
        # Tiny descendant samples are descriptive anecdotes, not population niches.
        if len(rows) < 4:
            continue
        A = np.asarray(rows)
        dom = Counter(np.argmax(A, axis=1).tolist())
        diversity = len(dom)
        # Mean distance from population centroid: specialization without naming roles.
        centroid = A.mean(axis=0)
        dispersion = float(np.mean(np.abs(A-centroid).sum(axis=1)/2.0))
        summaries[int(g)] = (diversity, dispersion, len(rows))
    eligible = sorted(summaries)
    persistent = 0
    # Require a chain of three consecutive living generations. Two generations
    # can be produced by a handful of lucky births and is too weak for a claim
    # about intergenerational organization.
    if len(eligible) >= 3:
        for g0, g1, g2 in zip(eligible[:-2], eligible[1:-1], eligible[2:]):
            if g1 == g0 + 1 and g2 == g1 + 1:
                triples = (summaries[g0], summaries[g1], summaries[g2])
                if all(v[0] >= 2 and v[2] >= 4 and v[1] >= 0.12 for v in triples):
                    persistent += 1
    return {
        "generations_with_profiles": len(eligible),
        "persistent_specialization_transitions": persistent,
        "living_generation_depth": (max(eligible)-min(eligible)+1) if eligible else 0,
        "generation_summaries": {str(k): {"dominant_action_count": v[0], "dispersion": v[1], "agents": v[2]} for k,v in summaries.items()},
    }



def _recent_activity(world, window: int):
    start = max(0, world.time - window)
    broadcasts = [e for e in world.communication_log if e["type"] == "broadcast" and e["time"] >= start]
    inscriptions = [e for e in world.communication_log if e["type"] == "inscription" and e["time"] >= start]
    gens = sorted({e["generation"] for e in broadcasts})
    drops = [e for e in world.object_log if e["type"] == "drop" and e["time"] >= start and e.get("success")]
    return {
        "broadcasts": len(broadcasts),
        "inscriptions": len(inscriptions),
        "signal_generation_count": len(gens),
        "signal_generational_span": (max(gens)-min(gens)) if gens else 0,
        "successful_drops": len(drops),
    }



def _multir2(P, Y):
    if len(P) < 20:
        return None
    P = np.asarray(P, dtype=float)
    Y = np.asarray(Y, dtype=float)
    if P.ndim != 2 or Y.ndim != 2 or P.shape[0] != Y.shape[0] or float(np.std(P)) < 1e-10:
        return None
    X = np.column_stack([np.ones(len(P)), P])
    beta = np.linalg.lstsq(X, Y, rcond=None)[0]
    pred = X @ beta
    denom = np.sum((Y - np.mean(Y, axis=0)) ** 2, axis=0)
    numer = np.sum((Y - pred) ** 2, axis=0)
    valid = denom > 1e-10
    if not np.any(valid):
        return None
    return float(np.mean(1.0 - numer[valid] / denom[valid]))


def _permutation_excess(P, Y, permutations=32):
    """Observer-side excess predictive structure over a shuffled-payload null.

    This is deliberately not exposed to agents.  It rejects a common false positive:
    low but non-zero R^2 created solely by finite samples or action imbalance.
    """
    obs = _multir2(P, Y)
    if obs is None:
        return {"observed": None, "null_mean": None, "excess": None, "p_upper": None}
    P = np.asarray(P, dtype=float)
    Y = np.asarray(Y, dtype=float)
    rng = np.random.default_rng(1729 + len(P))
    null=[]
    for _ in range(permutations):
        q = P[rng.permutation(len(P))]
        r = _multir2(q, Y)
        if r is not None:
            null.append(r)
    if not null:
        return {"observed": obs, "null_mean": None, "excess": None, "p_upper": None}
    null=np.asarray(null, dtype=float)
    p=(1.0 + float(np.sum(null >= obs))) / (len(null)+1.0)
    return {"observed": obs, "null_mean": float(np.mean(null)),
            "excess": float(obs-np.mean(null)), "p_upper": float(p)}


def _recent_signal_evidence(world, window: int):
    start=max(0, world.time-window)
    b=[e for e in world.communication_log if e["type"]=="broadcast" and e["time"]>=start]
    enc={"observed": None, "null_mean": None, "excess": None, "p_upper": None}
    if len(b)>=20:
        P=np.asarray([e["payload"] for e in b], dtype=float)
        Y=np.asarray([[e["temperature"],e["radiation"],e["resource_richness"]] for e in b], dtype=float)
        enc=_permutation_excess(P,Y)
    sr=[e for e in world.social_log if e["time"]>=start and e["received_count"]>0 and e["mean_payload"]]
    uptake={"observed": None, "null_mean": None, "excess": None, "p_upper": None}
    if len(sr)>=20:
        P=np.asarray([e["mean_payload"] for e in sr], dtype=float)
        names=["move","harvest","rest","broadcast","inscribe","pickup","drop"]
        Y=np.asarray([[1.0 if e["action"]==n else 0.0 for n in names] for e in sr], dtype=float)
        uptake=_permutation_excess(P,Y)
    return {"encoding":enc, "uptake_action":uptake, "receiver_rows":len(sr), "broadcast_rows":len(b)}

def observer_state(world, window: int = 100):
    s = snapshot(world)
    c = s["communication"]
    t = s["technology"]
    b = s["behavioral_diversity"]
    cog = s["cognition"]
    info = s["information_structure"]
    lineage = _lineage_metrics(world)
    specialization = _generation_specialization(world)
    # A compact vector used only to detect unexpected macroscopic changes.
    vec = np.asarray([
        _f(s["population"]),
        _f(s["max_generation"]),
        _f(b.get("mean_pairwise_action_distance")),
        _f(c.get("broadcast_environment_r2")),
        _f(c.get("receiver_action_r2_from_payload")),
        _f(c.get("receiver_motion_r2_from_payload")),
        _f(c.get("mean_signal_input_sensitivity")),
        _f(c.get("mean_mark_input_sensitivity")),
        _f(c.get("signal_generational_span")),
        _f(t.get("configuration_gain_vs_initial")),
        _f(t.get("successful_drops")),
        _f(info.get("private_information_index")),
        _f(cog.get("living_mean_memory_gene")),
        _f(cog.get("living_mean_plasticity_gene")),
        _f(cog.get("living_mean_social_attention_gene")),
        _f(specialization.get("persistent_specialization_transitions")),
    ], dtype=float)
    return {"time": world.time, "snapshot": s, "lineage": lineage,
            "specialization": specialization, "recent": _recent_activity(world, window),
            "recent_signal_evidence": _recent_signal_evidence(world, window), "vector": vec}


def _novelty_scores(vectors):
    """Past-only standardized innovation score; no future leakage."""
    scores = [0.0] * len(vectors)
    if len(vectors) < 4:
        return scores
    X = np.asarray(vectors, dtype=float)
    for i in range(3, len(X)):
        hist = X[:i]
        center = np.median(hist, axis=0)
        scale = np.median(np.abs(hist-center), axis=0) * 1.4826
        # Avoid tiny-variance channels becoming automatic discoveries.
        floor = np.maximum(np.std(hist, axis=0)*0.25, 0.05)
        scale = np.maximum(scale, floor)
        z = np.abs((X[i]-center)/scale)
        # Require breadth: average only the strongest 1/3 of coordinates.
        k = max(3, len(z)//3)
        scores[i] = float(np.mean(np.sort(z)[-k:]))
    return scores




def _transient_communication_bursts(epochs):
    """Detect null-aware communication bursts without calling them language.

    A burst requires at least two consecutive non-initial windows in which both
    environmental encoding and receiver-action uptake beat the shuffled-payload
    null. Persistence across generations is deliberately *not* required here: the
    point is to detect failed/ephemeral informational innovations for later causal
    autopsy. This observer-only label never affects fitness or behaviour.
    """
    good=[]
    for i,e in enumerate(epochs):
        ev=e.get("recent_signal_evidence", {})
        enc,up=ev.get("encoding",{}),ev.get("uptake_action",{})
        ok=(enc.get("excess") is not None and up.get("excess") is not None
            and enc.get("excess",0.0)>0.10 and up.get("excess",0.0)>0.05
            and enc.get("p_upper",1.0)<=0.05 and up.get("p_upper",1.0)<=0.05
            and ev.get("receiver_rows",0)>=20 and ev.get("broadcast_rows",0)>=20)
        good.append(bool(ok))
    bursts=[]
    i=1
    while i < len(good):
        if not good[i]:
            i+=1; continue
        j=i
        while j+1 < len(good) and good[j+1]: j+=1
        if j-i+1>=3:
            gens=max(epochs[k]["recent"].get("signal_generation_count",0) for k in range(i,j+1))
            if gens>=2:
                bursts.append({
                    "start_time": epochs[i]["time"], "end_time": epochs[j]["time"],
                    "windows": j-i+1, "max_active_signal_generations": int(gens),
                    "cross_generational": True,
                })
        i=j+1
    return bursts


def run_longitudinal(seed: int, steps: int = 5000, epoch: int = 100,
                     config: SimulationConfig | None = None) -> dict:
    cfg = config or SimulationConfig(
        generic_population_only=True,
        # World-side long-horizon ecology: more renewable matter and lower basal
        # dissipation, without changing controller objectives or adding behaviours.
        initial_agents=36, resource_patches=84, resource_regrowth=0.062,
        basal_metabolism=0.034, initial_energy=20.0,
        reproduction_threshold=20.0, reproduction_cost=8.5, max_population=300,
    )
    world = World(cfg, seed=seed)
    epochs = [observer_state(world, epoch)]
    while world.time < steps and any(a.alive for a in world.agents):
        world.run(min(epoch, steps-world.time))
        epochs.append(observer_state(world, epoch))
    scores = _novelty_scores([e["vector"] for e in epochs])
    for e, score in zip(epochs, scores):
        e["novelty_score"] = score
        e.pop("vector", None)

    # A transition is only a candidate if novelty is large and at least one
    # interpretable population-level feature remains elevated at the next epoch.
    candidates = []
    for i in range(3, len(epochs)-2):
        if scores[i] < 3.0:
            continue
        cur, nxt, nxt2 = epochs[i], epochs[i+1], epochs[i+2]
        # Demographic collapse is not counted as interesting emergence. A candidate
        # must live inside a viable population for at least two later epochs.
        healthy_floor = max(6, int(0.25 * cfg.initial_agents))
        if min(cur["snapshot"]["population"], nxt["snapshot"]["population"], nxt2["snapshot"]["population"]) < healthy_floor:
            continue
        # A collapse trajectory is not a phase transition worth publishing.
        prev_pop = epochs[i-1]["snapshot"]["population"]
        if cur["snapshot"]["population"] < 0.85 * max(prev_pop, 1):
            continue
        sc, sn, sn2 = cur["snapshot"], nxt["snapshot"], nxt2["snapshot"]
        cc, cn = sc["communication"], sn["communication"]
        tc, tn = sc["technology"], sn["technology"]
        bc, bn = sc["behavioral_diversity"], sn["behavioral_diversity"]
        persistent_channels = []
        # Use recent-window events, not cumulative logs: stale signals cannot
        # masquerade as a persistent convention. Require at least two generations
        # actively emitting in consecutive windows.
        if (cur["recent"]["signal_generation_count"] >= 2 and nxt["recent"]["signal_generation_count"] >= 2
                and nxt2["recent"]["signal_generation_count"] >= 2):
            # Mere multi-generation emission is not language.  Require recent-window
            # payload structure to beat a shuffled-payload null in at least two of
            # the three consecutive epochs, both for environmental encoding and
            # receiver action uptake.
            sig_epochs=(cur,nxt,nxt2)
            evidential=0
            for ee in sig_epochs:
                ev=ee["recent_signal_evidence"]
                enc,up=ev["encoding"],ev["uptake_action"]
                if (enc.get("excess") is not None and up.get("excess") is not None
                        and enc["excess"] > 0.015 and up["excess"] > 0.015
                        and enc.get("p_upper",1.0) <= 0.10 and up.get("p_upper",1.0) <= 0.10):
                    evidential += 1
            if evidential >= 2:
                persistent_channels.append("cross_generation_signalling")
        if (_f(tc.get("configuration_gain_vs_initial")) > 0.02 and _f(tn.get("configuration_gain_vs_initial")) > 0.02
                and _f(sn2["technology"].get("configuration_gain_vs_initial")) > 0.02):
            persistent_channels.append("material_configuration")
        if (_f(bc.get("mean_pairwise_action_distance")) > 0.35 and _f(bn.get("mean_pairwise_action_distance")) > 0.35
                and _f(sn2["behavioral_diversity"].get("mean_pairwise_action_distance")) > 0.35):
            persistent_channels.append("behavioural_differentiation")
        if (cur["specialization"]["persistent_specialization_transitions"] > 0
                and nxt["specialization"]["persistent_specialization_transitions"] > 0
                and nxt2["specialization"]["persistent_specialization_transitions"] > 0):
            persistent_channels.append("intergenerational_specialization")
        if persistent_channels:
            candidates.append({"time": cur["time"], "novelty_score": scores[i], "persistent_channels": persistent_channels})

    # Interesting final claims remain deliberately weak: this is candidate discovery,
    # not proof. Causal controls are run separately after candidates are found.
    return {
        "seed": seed, "requested_steps": steps, "completed_steps": world.time,
        "extinct": not any(a.alive for a in world.agents),
        "epochs": epochs,
        "transition_candidates": candidates,
        "transient_communication_bursts": _transient_communication_bursts(epochs),
        "max_novelty_score": max(scores) if scores else 0.0,
        "final": epochs[-1],
    }


def scan(seeds, steps=5000, epoch=100):
    runs = [run_longitudinal(int(s), steps=steps, epoch=epoch) for s in seeds]
    return {
        "worlds": len(runs), "steps": steps, "epoch": epoch,
        "extinctions": sum(r["extinct"] for r in runs),
        "runs_with_transition_candidates": sum(bool(r["transition_candidates"]) for r in runs),
        "candidate_count": sum(len(r["transition_candidates"]) for r in runs),
        "max_novelty": max((r["max_novelty_score"] for r in runs), default=0.0),
        "runs": runs,
    }
