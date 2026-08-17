"""Observer-side semantic autopsy for emergent signalling candidates.

This module adds no agent objective, reward, sensor, action or world law.  It
re-runs an already identified candidate and asks whether signal *content* has a
causal effect on a receiver while holding the receiver, world and local context
fixed.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
import math
import numpy as np

from .phase_map import long_horizon_config
from .world import World
from .agents import ActionKind


def _apply_config_overrides(cfg, overrides):
    if not overrides:
        return cfg
    for key, value in overrides.items():
        if not hasattr(cfg, key):
            raise ValueError(f"unknown SimulationConfig field: {key}")
        setattr(cfg, key, value)
    return cfg


def _kmeans(x: np.ndarray, k: int, seed: int = 0, iters: int = 80):
    if len(x) < k:
        raise ValueError("not enough rows")
    rng = np.random.default_rng(seed)
    # kmeans++-like deterministic-enough seeding
    centers = [x[int(rng.integers(len(x)))]]
    for _ in range(1, k):
        d2 = np.min(np.sum((x[:, None, :] - np.asarray(centers)[None, :, :]) ** 2, axis=2), axis=1)
        if float(np.sum(d2)) <= 1e-12:
            centers.append(x[int(rng.integers(len(x)))])
        else:
            centers.append(x[int(rng.choice(len(x), p=d2 / np.sum(d2)))])
    centers = np.asarray(centers, dtype=float)
    labels = np.zeros(len(x), dtype=int)
    for _ in range(iters):
        dist = np.sum((x[:, None, :] - centers[None, :, :]) ** 2, axis=2)
        new = np.argmin(dist, axis=1)
        if np.array_equal(new, labels) and _ > 0:
            break
        labels = new
        for j in range(k):
            rows = x[labels == j]
            if len(rows):
                centers[j] = np.mean(rows, axis=0)
    return labels, centers


def _silhouette(x: np.ndarray, labels: np.ndarray) -> float:
    if len(x) < 3 or len(np.unique(labels)) < 2:
        return -1.0
    out=[]
    for i in range(len(x)):
        own = labels == labels[i]
        own[i] = False
        a = float(np.mean(np.linalg.norm(x[own] - x[i], axis=1))) if np.any(own) else 0.0
        bs=[]
        for lab in np.unique(labels):
            if lab == labels[i]:
                continue
            q = labels == lab
            if np.any(q):
                bs.append(float(np.mean(np.linalg.norm(x[q] - x[i], axis=1))))
        b=min(bs) if bs else a
        den=max(a,b,1e-12)
        out.append((b-a)/den)
    return float(np.mean(out))


def discover_signal_clusters(world: World, *, min_rows: int = 30, max_k: int = 5) -> dict:
    rows=[e for e in world.communication_log if e.get("type") == "broadcast" and e.get("payload")]
    if len(rows) < min_rows:
        return {"rows":len(rows),"k":0,"silhouette":None,"centers":[],"cluster_contexts":[]}
    P=np.asarray([e["payload"] for e in rows], dtype=float)
    best=None
    for k in range(2, min(max_k, len(P)-1)+1):
        labels,centers=_kmeans(P,k,seed=world.seed+7919*k)
        sil=_silhouette(P,labels)
        if best is None or sil > best[0]:
            best=(sil,labels,centers)
    sil,labels,centers=best
    contexts=[]
    for j in range(len(centers)):
        ix=np.where(labels==j)[0]
        ctx={"cluster":int(j),"n":int(len(ix))}
        for key in ("temperature","radiation","resource_richness"):
            vals=np.asarray([rows[i][key] for i in ix],dtype=float)
            ctx[key]=float(np.mean(vals)) if len(vals) else None
            ctx[key+"_sd"]=float(np.std(vals)) if len(vals) else None
        gens=sorted({int(rows[i]["generation"]) for i in ix})
        ctx["generations"]=gens
        contexts.append(ctx)
    # observer-side context separability: between-cluster variance / total variance
    context_r2={}
    for key in ("temperature","radiation","resource_richness"):
        y=np.asarray([e[key] for e in rows],dtype=float)
        mu=float(np.mean(y)); total=float(np.sum((y-mu)**2))
        within=0.0
        for j in range(len(centers)):
            v=y[labels==j]
            if len(v): within += float(np.sum((v-np.mean(v))**2))
        context_r2[key]=0.0 if total<=1e-12 else float(max(0.0,1.0-within/total))
    return {"rows":len(rows),"k":int(len(centers)),"silhouette":float(sil),
            "centers":[list(map(float,c)) for c in centers],
            "cluster_contexts":contexts,"context_r2":context_r2}


def _nearest_center(payload, centers):
    p=np.asarray(payload,dtype=float)
    c=np.asarray(centers,dtype=float)
    return int(np.argmin(np.sum((c-p[None,:])**2,axis=1)))


def _own_center(payload, centers):
    p=np.asarray(payload,dtype=float); c=np.asarray(centers,dtype=float)
    d=np.sum((c-p[None,:])**2,axis=1)
    return tuple(float(v) for v in c[int(np.argmin(d))])

def _farthest_other_center(payload, centers):
    p=np.asarray(payload,dtype=float); c=np.asarray(centers,dtype=float)
    d=np.sum((c-p[None,:])**2,axis=1)
    own=int(np.argmin(d)); d[own]=-1.0
    return tuple(float(v) for v in c[int(np.argmax(d))])


def _action_signature(action):
    if action.kind.value == "move":
        n=math.hypot(action.dx,action.dy)
        return (action.kind.value, 0.0 if n==0 else action.dx/n, 0.0 if n==0 else action.dy/n)
    return (action.kind.value,0.0,0.0)


def _paired_sign_p(cross_only: int, within_only: int) -> float:
    """Two-sided exact sign-test p-value on discordant paired events."""
    n=int(cross_only+within_only)
    if n<=0: return 1.0
    k=min(int(cross_only),int(within_only))
    tail=sum(math.comb(n,i) for i in range(k+1))/(2.0**n)
    return float(min(1.0,2.0*tail))




def _counterfactual_act_inplace(agent, obs, rng):
    """Evaluate ``agent.act`` without changing agent or RNG state.

    This is observer-side acceleration only.  The original assay deep-copied the
    whole recurrent controller (including weight matrices) for every
    counterfactual.  Here we snapshot only mutable runtime state, call the exact
    same ``act`` method, then restore both agent and RNG.  The simulation itself
    is untouched.
    """
    rng_state = deepcopy(rng.bit_generator.state)
    state = {
        "hidden": agent.hidden.copy() if getattr(agent, "hidden", None) is not None else None,
        "initialized": getattr(agent, "_initialized", None),
        "eligibility": None if getattr(agent, "_eligibility", None) is None else agent._eligibility.copy(),
        "last_aug": None if getattr(agent, "_last_aug", None) is None else agent._last_aug.copy(),
        "last_row": getattr(agent, "_last_row", None),
        "emissions": getattr(agent, "emissions", None),
        "inscriptions": getattr(agent, "inscriptions", None),
    }
    # ``act`` only lazily initializes weights.  Assayed recurrent agents in a live
    # replay are normally initialized already, but preserve refs in the rare case
    # this is the first action.
    weight_state = None
    if not bool(getattr(agent, "_initialized", False)):
        weight_state = (getattr(agent, "W_in", None), getattr(agent, "W_rec", None), getattr(agent, "W_out", None))
    try:
        return agent.act(obs, rng)
    finally:
        rng.bit_generator.state = rng_state
        if state["hidden"] is not None:
            agent.hidden = state["hidden"]
        agent._initialized = state["initialized"]
        agent._eligibility = state["eligibility"]
        agent._last_aug = state["last_aug"]
        agent._last_row = state["last_row"]
        if state["emissions"] is not None:
            agent.emissions = state["emissions"]
        if state["inscriptions"] is not None:
            agent.inscriptions = state["inscriptions"]
        if weight_state is not None:
            agent.W_in, agent.W_rec, agent.W_out = weight_state

def counterfactual_content_assay(world_seed: int, agent_seed: int, *, information_level: float = 0.35,
                                 signal_cost: float = 0.03, steps: int = 1200,
                                 assay_start: int = 100, assay_end: int | None = None,
                                 max_events: int = 1000, communication_scramble: bool = False,
                                 min_generation_events: int = 50, config_overrides: dict | None = None) -> dict:
    """Within-receiver causal content substitution assay.

    For every sampled reception event, three cloned receivers see the exact same
    non-signal observation and RNG state: (i) the real payload, (ii) its own signal
    cluster centroid, and (iii) the farthest other cluster centroid.  The difference
    between cross-cluster and within-cluster action changes is the key observer-side
    semantic contrast.  None of these counterfactual actions affects the real run.
    """
    cfg=long_horizon_config(information_level=information_level, signal_cost=signal_cost,
                            communication_enabled=True, agent_seed=int(agent_seed))
    cfg=_apply_config_overrides(cfg, config_overrides)
    cfg.communication_scramble = bool(communication_scramble)
    ref=World(cfg, seed=int(world_seed)).run(int(steps))
    clusters=discover_signal_clusters(ref)
    centers=clusters.get("centers",[])
    if len(centers)<2:
        return {"world_seed":world_seed,"agent_seed":agent_seed,"clusters":clusters,"events":0}

    replay=World(cfg, seed=int(world_seed))
    end=steps if assay_end is None else min(steps,int(assay_end))
    tested=0
    within_kind_changed=cross_kind_changed=0
    within_any_changed=cross_any_changed=0
    cross_only=within_only=0
    by_generation={}
    by_lineage_relation={"same":{"events":0,"cross_only":0,"within_only":0},"cross":{"events":0,"cross_only":0,"within_only":0}}
    examples=[]
    for _ in range(int(steps)):
        if replay.time >= assay_start and replay.time < end and tested < max_events:
            for a in [q for q in replay.agents if q.alive and getattr(q,"kind","")=="recurrent"]:
                if tested >= max_events: break
                obs=replay.observe(a)
                if not obs.nearby_signals:
                    continue
                mean=np.mean(np.asarray([sig[2] for sig in obs.nearby_signals],dtype=float),axis=0)
                own=_own_center(mean, centers)
                other=_farthest_other_center(mean, centers)
                obs_own=replace(obs, nearby_signals=[(dx,dy,own) for dx,dy,_ in obs.nearby_signals])
                obs_other=replace(obs, nearby_signals=[(dx,dy,other) for dx,dy,_ in obs.nearby_signals])
                real=_counterfactual_act_inplace(a, obs, replay.agent_rng)
                same=_counterfactual_act_inplace(a, obs_own, replay.agent_rng)
                cross=_counterfactual_act_inplace(a, obs_other, replay.agent_rng)
                sr,ss,sc=map(_action_signature,(real,same,cross))
                w_any=sr!=ss; c_any=sr!=sc
                w_kind=sr[0]!=ss[0]; c_kind=sr[0]!=sc[0]
                tested+=1
                within_any_changed+=int(w_any); cross_any_changed+=int(c_any)
                within_kind_changed+=int(w_kind); cross_kind_changed+=int(c_kind)
                g=int(a.generation)
                d=by_generation.setdefault(g,{"events":0,"within_kind_changed":0,"cross_kind_changed":0,"cross_only":0,"within_only":0})
                d["events"]+=1; d["within_kind_changed"]+=int(w_kind); d["cross_kind_changed"]+=int(c_kind)
                co=bool(c_kind and not w_kind); wo=bool(w_kind and not c_kind)
                cross_only+=int(co); within_only+=int(wo); d["cross_only"]+=int(co); d["within_only"]+=int(wo)
                # Genealogical relation is observer-side: recover current visible signal sources.
                def root_id(agent_id):
                    lookup={q.id:q for q in replay.agents}
                    cur=lookup.get(agent_id); seen=set()
                    while cur is not None and cur.parent_id is not None and cur.id not in seen:
                        seen.add(cur.id); cur=lookup.get(cur.parent_id)
                    return None if cur is None else int(cur.id)
                receiver_root=root_id(a.id)
                source_ids=[]
                for sig in replay.signals:
                    if sig.source_id==a.id: continue
                    dx,dy=sig.x-a.x,sig.y-a.y
                    if dx*dx+dy*dy <= sig.radius*sig.radius and replay.line_of_sight(a.x,a.y,sig.x,sig.y):
                        source_ids.append(sig.source_id)
                relation="cross" if any(root_id(sid)!=receiver_root for sid in source_ids if root_id(sid) is not None) else "same"
                lr=by_lineage_relation[relation]; lr["events"]+=1; lr["cross_only"]+=int(co); lr["within_only"]+=int(wo)
                if len(examples)<12 and c_kind and not w_kind:
                    examples.append({"time":int(replay.time),"agent_id":int(a.id),"generation":g,
                                     "real_payload":list(map(float,mean)),"own_centroid":list(map(float,own)),
                                     "other_centroid":list(map(float,other)),"real_action":sr[0],
                                     "within_action":ss[0],"cross_action":sc[0]})
        if not any(a.alive for a in replay.agents): break
        replay.step()
    def rate(x): return None if tested==0 else float(x/tested)
    for d in by_generation.values():
        n=d["events"]
        d["within_kind_change_rate"]=float(d["within_kind_changed"]/n) if n else None
        d["cross_kind_change_rate"]=float(d["cross_kind_changed"]/n) if n else None
        d["semantic_excess_kind_rate"]=(d["cross_kind_change_rate"]-d["within_kind_change_rate"]) if n else None
        d["paired_sign_p"]=_paired_sign_p(d["cross_only"],d["within_only"])
    g0=by_generation.get(0,{}).get("semantic_excess_kind_rate")
    later=[d.get("semantic_excess_kind_rate") for g,d in by_generation.items() if int(g)>0 and d.get("semantic_excess_kind_rate") is not None and int(d.get("events",0)) >= int(min_generation_events)]
    intergenerational_amplification=None if g0 is None or int(by_generation.get(0,{}).get("events",0)) < int(min_generation_events) or not later else float(max(later)-g0)
    for d in by_lineage_relation.values():
        n=d["events"]
        d["semantic_excess_kind_rate"]=None if n==0 else float((d["cross_only"]-d["within_only"])/n)
        d["paired_sign_p"]=_paired_sign_p(d["cross_only"],d["within_only"])
    return {
        "world_seed":int(world_seed),"agent_seed":int(agent_seed),"steps":int(steps),"communication_scramble":bool(communication_scramble),"clusters":clusters,"events":int(tested),
        "within_cluster_action_change_rate":rate(within_any_changed),"cross_cluster_action_change_rate":rate(cross_any_changed),
        "within_cluster_kind_change_rate":rate(within_kind_changed),"cross_cluster_kind_change_rate":rate(cross_kind_changed),
        "semantic_excess_kind_rate":None if tested==0 else float((cross_kind_changed-within_kind_changed)/tested),
        "cross_only":int(cross_only),"within_only":int(within_only),"paired_sign_p":_paired_sign_p(cross_only,within_only),
        "intergenerational_amplification":intergenerational_amplification,"by_generation":by_generation,"by_lineage_relation":by_lineage_relation,"examples":examples,
    }

def candidate_semantic_autopsy(world_seed: int = 1, agent_seed: int = 1, *, information_level: float = 0.35,
                                signal_cost: float = 0.03, steps: int = 1200) -> dict:
    return counterfactual_content_assay(world_seed, agent_seed, information_level=information_level,
                                        signal_cost=signal_cost, steps=steps)


def _tv(p, q):
    p=np.asarray(p,dtype=float); q=np.asarray(q,dtype=float)
    return float(0.5*np.sum(np.abs(p-q)))


def causal_codebook_assay(world_seed: int, agent_seed: int, *, information_level: float = 0.35,
                           signal_cost: float = 0.03, steps: int = 1200,
                           assay_start: int = 100, assay_end: int | None = None,
                           max_events: int = 1200, communication_scramble: bool = False,
                           config_overrides: dict | None = None) -> dict:
    """Observer-side causal codebook assay.

    For each reception event, clones the *same receiver* and injects each naturally
    discovered signal-cluster centroid in turn while holding all other sensory input
    and RNG state fixed.  It then estimates P(action | injected cluster, generation).

    A codebook is interesting only when distinct signal classes causally induce
    distinct action distributions, and when that mapping is retained/amplified in
    descendants.  The assay never changes the real evolutionary trajectory.
    """
    cfg=long_horizon_config(information_level=information_level, signal_cost=signal_cost,
                            communication_enabled=True, agent_seed=int(agent_seed))
    cfg=_apply_config_overrides(cfg, config_overrides)
    cfg.communication_scramble=bool(communication_scramble)
    ref=World(cfg, seed=int(world_seed)).run(int(steps))
    clusters=discover_signal_clusters(ref)
    centers=clusters.get("centers",[])
    if len(centers)<2:
        return {"world_seed":world_seed,"agent_seed":agent_seed,"clusters":clusters,"events":0}

    replay=World(cfg, seed=int(world_seed))
    end=steps if assay_end is None else min(int(steps),int(assay_end))
    actions=[k.value for k in ActionKind]
    ai={a:i for i,a in enumerate(actions)}
    counts={}
    tested=0
    for _ in range(int(steps)):
        if assay_start <= replay.time < end and tested < max_events:
            for a in [q for q in replay.agents if q.alive and getattr(q,"kind","")=="recurrent"]:
                if tested>=max_events: break
                obs=replay.observe(a)
                if not obs.nearby_signals: continue
                g=int(a.generation)
                gd=counts.setdefault(g,np.zeros((len(centers),len(actions)),dtype=int))
                for ci,c in enumerate(centers):
                    payload=tuple(float(v) for v in c)
                    cf=replace(obs, nearby_signals=[(dx,dy,payload) for dx,dy,_ in obs.nearby_signals])
                    act=_counterfactual_act_inplace(a, cf, replay.agent_rng)
                    gd[ci,ai[act.kind.value]]+=1
                tested+=1
        if not any(a.alive for a in replay.agents): break
        replay.step()

    by_generation={}
    for g,arr in counts.items():
        probs=[]
        for row in arr:
            s=int(np.sum(row)); probs.append((row/max(s,1)).astype(float))
        probs=np.asarray(probs)
        pair=[]
        for i in range(len(probs)):
            for j in range(i+1,len(probs)):
                pair.append(_tv(probs[i],probs[j]))
        # entropy of each cluster-induced action distribution, normalized by log |A|
        ents=[]
        for p in probs:
            q=p[p>0]; h=-float(np.sum(q*np.log(q))) if len(q) else 0.0
            ents.append(h/max(math.log(len(actions)),1e-12))
        dominant=[actions[int(np.argmax(p))] for p in probs]
        by_generation[int(g)]={
            "events":int(np.sum(arr[0])) if len(arr) else 0,
            "causal_differentiation":float(np.mean(pair)) if pair else 0.0,
            "max_pairwise_tv":float(max(pair)) if pair else 0.0,
            "mean_action_entropy":float(np.mean(ents)) if ents else None,
            "dominant_actions":dominant,
            "action_probabilities":[{actions[i]:float(p[i]) for i in range(len(actions))} for p in probs],
        }

    generations=sorted(by_generation)
    retention={}
    for g0,g1 in zip(generations,generations[1:]):
        p0=by_generation[g0]["action_probabilities"]
        p1=by_generation[g1]["action_probabilities"]
        tvs=[]
        for a0,a1 in zip(p0,p1):
            v0=[a0[x] for x in actions]; v1=[a1[x] for x in actions]
            tvs.append(_tv(v0,v1))
        retention[f"{g0}->{g1}"]={
            "mean_codebook_tv":float(np.mean(tvs)) if tvs else None,
            "codebook_retention":float(1.0-np.mean(tvs)) if tvs else None,
        }
    g0=by_generation.get(0,{}).get("causal_differentiation")
    later=[d["causal_differentiation"] for g,d in by_generation.items() if g>0]
    amplification=None if g0 is None or not later else float(max(later)-g0)
    return {
        "world_seed":int(world_seed),"agent_seed":int(agent_seed),"steps":int(steps),
        "communication_scramble":bool(communication_scramble),"events":int(tested),
        "clusters":clusters,"actions":actions,"by_generation":by_generation,
        "intergenerational_codebook_amplification":amplification,
        "retention":retention,
    }


def directional_substitution_assay(world_seed: int, agent_seed: int, *, information_level: float=.35,
                                    signal_cost: float=.03, steps: int=1200,
                                    assay_start: int=100, assay_end: int|None=None,
                                    max_events: int=1400, communication_scramble: bool=False,
                                    min_pair_events: int=25, config_overrides: dict | None = None) -> dict:
    """Directional cluster-to-cluster counterfactual substitution.

    For each reception, identifies the nearest naturally-emerged signal cluster and
    compares the receiver's action under that cluster centroid with every *other*
    centroid. Records which substitutions cause which action-kind transitions.
    This asks whether specific signal categories have reproducibly different causal
    effects, without assigning any human semantic label to a category.
    """
    cfg=long_horizon_config(information_level=information_level,signal_cost=signal_cost,
                            communication_enabled=True,agent_seed=int(agent_seed))
    cfg=_apply_config_overrides(cfg, config_overrides)
    cfg.communication_scramble=bool(communication_scramble)
    ref=World(cfg,seed=int(world_seed)).run(int(steps))
    clusters=discover_signal_clusters(ref); centers=clusters.get('centers',[])
    if len(centers)<2:
        return {'world_seed':world_seed,'agent_seed':agent_seed,'clusters':clusters,'events':0,'pairs':{}}
    replay=World(cfg,seed=int(world_seed)); end=steps if assay_end is None else min(steps,int(assay_end))
    raw={}; tested=0
    for _ in range(int(steps)):
        if assay_start <= replay.time < end and tested < max_events:
            for a in [q for q in replay.agents if q.alive and getattr(q,'kind','')=='recurrent']:
                if tested>=max_events: break
                obs=replay.observe(a)
                if not obs.nearby_signals: continue
                mean=np.mean(np.asarray([sig[2] for sig in obs.nearby_signals],dtype=float),axis=0)
                own=_nearest_center(mean,centers); own_payload=tuple(map(float,centers[own]))
                base_obs=replace(obs,nearby_signals=[(dx,dy,own_payload) for dx,dy,_ in obs.nearby_signals])
                base=_counterfactual_act_inplace(a, base_obs, replay.agent_rng); bkind=base.kind.value
                g=int(a.generation)
                for j,c in enumerate(centers):
                    if j==own: continue
                    payload=tuple(map(float,c)); cf=replace(obs,nearby_signals=[(dx,dy,payload) for dx,dy,_ in obs.nearby_signals])
                    alt=_counterfactual_act_inplace(a, cf, replay.agent_rng); akind=alt.kind.value
                    key=(g,own,j); d=raw.setdefault(key,{'n':0,'changed':0,'transitions':{}})
                    d['n']+=1; d['changed']+=int(akind!=bkind)
                    if akind!=bkind:
                        tr=f'{bkind}->{akind}'; d['transitions'][tr]=d['transitions'].get(tr,0)+1
                tested+=1
        if not any(a.alive for a in replay.agents): break
        replay.step()
    pairs={}
    for (g,i,j),d in raw.items():
        if d['n']<min_pair_events: continue
        trans=sorted(d['transitions'].items(),key=lambda z:z[1],reverse=True)
        pairs[f'g{g}:{i}->{j}']={'generation':g,'from_cluster':i,'to_cluster':j,'n':d['n'],
                                'change_rate':float(d['changed']/d['n']),
                                'top_transitions':[{'transition':t,'n':int(n),'rate':float(n/d['n'])} for t,n in trans[:5]]}
    # For each generation: how heterogeneous are pair-specific causal change rates?
    by_generation={}
    for g in sorted({v['generation'] for v in pairs.values()}):
        vals=[v['change_rate'] for v in pairs.values() if v['generation']==g]
        by_generation[g]={'pairs':len(vals),'mean_change_rate':float(np.mean(vals)) if vals else None,
                          'sd_pair_change_rate':float(np.std(vals)) if vals else None,
                          'max_change_rate':float(max(vals)) if vals else None}
    return {'world_seed':int(world_seed),'agent_seed':int(agent_seed),'steps':int(steps),
            'communication_scramble':bool(communication_scramble),'events':int(tested),
            'clusters':clusters,'pairs':pairs,'by_generation':by_generation}


def counterfactual_content_assay_single_pass(world_seed: int, agent_seed: int, *, information_level: float = 0.35,
                                              signal_cost: float = 0.03, steps: int = 1200,
                                              assay_start: int = 100, assay_end: int | None = None,
                                              max_events: int = 1000, communication_scramble: bool = False,
                                              min_generation_events: int = 50,
                                              max_events_per_generation: int | None = None,
                                              config_overrides: dict | None = None) -> dict:
    """Single-simulation equivalent of :func:`counterfactual_content_assay`.

    The legacy assay first simulated the candidate to discover signal clusters and
    then replayed the entire world to recover reception events.  This observer-only
    implementation captures compact receiver decision snapshots during that first
    run, discovers clusters afterwards, and evaluates the same counterfactuals
    offline.  It changes neither the world trajectory nor the agent objective.
    """
    cfg=long_horizon_config(information_level=information_level, signal_cost=signal_cost,
                            communication_enabled=True, agent_seed=int(agent_seed))
    cfg=_apply_config_overrides(cfg, config_overrides)
    cfg.communication_scramble = bool(communication_scramble)
    world=World(cfg, seed=int(world_seed))
    end=steps if assay_end is None else min(steps,int(assay_end))
    captured=[]
    captured_by_generation={}
    seen_by_generation={}
    observer_rng=np.random.default_rng(104729 + 1009*int(world_seed) + 9176*int(agent_seed))

    def root_id(agent_id):
        lookup={q.id:q for q in world.agents}
        cur=lookup.get(agent_id); seen=set()
        while cur is not None and cur.parent_id is not None and cur.id not in seen:
            seen.add(cur.id); cur=lookup.get(cur.parent_id)
        return None if cur is None else int(cur.id)

    for _ in range(int(steps)):
        total_captured = (sum(len(v) for v in captured_by_generation.values()) if max_events_per_generation is not None else len(captured))
        if assay_start <= world.time < end and (max_events_per_generation is not None or total_captured < max_events):
            for a in [q for q in world.agents if q.alive and getattr(q,"kind","")=="recurrent"]:
                if max_events_per_generation is None and len(captured)>=max_events: break
                obs=world.observe(a)
                if not obs.nearby_signals:
                    continue
                g=int(a.generation)
                # Observer-side reservoir sampling prevents abundant early generations
                # from consuming the whole assay budget.  The observer RNG is separate
                # from world/agent RNGs and cannot affect evolution.
                slot=None
                if max_events_per_generation is not None:
                    seen=seen_by_generation.get(g,0)+1; seen_by_generation[g]=seen
                    bucket=captured_by_generation.setdefault(g,[])
                    if len(bucket) < int(max_events_per_generation):
                        slot=len(bucket)
                    else:
                        j=int(observer_rng.integers(seen))
                        if j < int(max_events_per_generation): slot=j
                        else: continue
                receiver_root=root_id(a.id)
                source_ids=[]
                for sig in world.signals:
                    if sig.source_id==a.id: continue
                    dx,dy=sig.x-a.x,sig.y-a.y
                    if dx*dx+dy*dy <= sig.radius*sig.radius and world.line_of_sight(a.x,a.y,sig.x,sig.y):
                        source_ids.append(sig.source_id)
                relation="cross" if any(root_id(sid)!=receiver_root for sid in source_ids if root_id(sid) is not None) else "same"
                item={
                    "time":int(world.time), "agent":deepcopy(a), "obs":deepcopy(obs),
                    "rng_state":deepcopy(world.agent_rng.bit_generator.state),
                    "relation":relation,
                }
                if max_events_per_generation is None:
                    captured.append(item)
                else:
                    bucket=captured_by_generation[g]
                    if slot==len(bucket): bucket.append(item)
                    else: bucket[slot]=item
        if not any(a.alive for a in world.agents): break
        world.step()

    if max_events_per_generation is not None:
        captured=[item for g in sorted(captured_by_generation) for item in sorted(captured_by_generation[g], key=lambda z:z["time"])]
    clusters=discover_signal_clusters(world)
    centers=clusters.get("centers",[])
    if len(centers)<2:
        return {"world_seed":world_seed,"agent_seed":agent_seed,"clusters":clusters,"events":0}

    tested=0
    within_kind_changed=cross_kind_changed=0
    within_any_changed=cross_any_changed=0
    cross_only=within_only=0
    by_generation={}
    by_lineage_relation={"same":{"events":0,"cross_only":0,"within_only":0},"cross":{"events":0,"cross_only":0,"within_only":0}}
    examples=[]
    for item in captured:
        a=item["agent"]; obs=item["obs"]
        mean=np.mean(np.asarray([sig[2] for sig in obs.nearby_signals],dtype=float),axis=0)
        own=_own_center(mean, centers); other=_farthest_other_center(mean, centers)
        obs_own=replace(obs, nearby_signals=[(dx,dy,own) for dx,dy,_ in obs.nearby_signals])
        obs_other=replace(obs, nearby_signals=[(dx,dy,other) for dx,dy,_ in obs.nearby_signals])
        # Recreate a local RNG at the exact state captured before the event.
        local_rng=np.random.default_rng(); local_rng.bit_generator.state=deepcopy(item["rng_state"])
        real=_counterfactual_act_inplace(a, obs, local_rng)
        same=_counterfactual_act_inplace(a, obs_own, local_rng)
        cross=_counterfactual_act_inplace(a, obs_other, local_rng)
        sr,ss,sc=map(_action_signature,(real,same,cross))
        w_any=sr!=ss; c_any=sr!=sc; w_kind=sr[0]!=ss[0]; c_kind=sr[0]!=sc[0]
        tested+=1; within_any_changed+=int(w_any); cross_any_changed+=int(c_any)
        within_kind_changed+=int(w_kind); cross_kind_changed+=int(c_kind)
        g=int(a.generation)
        d=by_generation.setdefault(g,{"events":0,"within_kind_changed":0,"cross_kind_changed":0,"cross_only":0,"within_only":0})
        d["events"]+=1; d["within_kind_changed"]+=int(w_kind); d["cross_kind_changed"]+=int(c_kind)
        co=bool(c_kind and not w_kind); wo=bool(w_kind and not c_kind)
        cross_only+=int(co); within_only+=int(wo); d["cross_only"]+=int(co); d["within_only"]+=int(wo)
        lr=by_lineage_relation[item["relation"]]; lr["events"]+=1; lr["cross_only"]+=int(co); lr["within_only"]+=int(wo)
        if len(examples)<12 and c_kind and not w_kind:
            examples.append({"time":item["time"],"agent_id":int(a.id),"generation":g,
                             "real_payload":list(map(float,mean)),"own_centroid":list(map(float,own)),
                             "other_centroid":list(map(float,other)),"real_action":sr[0],
                             "within_action":ss[0],"cross_action":sc[0]})
    def rate(x): return None if tested==0 else float(x/tested)
    for d in by_generation.values():
        n=d["events"]
        d["within_kind_change_rate"]=float(d["within_kind_changed"]/n) if n else None
        d["cross_kind_change_rate"]=float(d["cross_kind_changed"]/n) if n else None
        d["semantic_excess_kind_rate"]=(d["cross_kind_change_rate"]-d["within_kind_change_rate"]) if n else None
        d["paired_sign_p"]=_paired_sign_p(d["cross_only"],d["within_only"])
    g0=by_generation.get(0,{}).get("semantic_excess_kind_rate")
    later=[d.get("semantic_excess_kind_rate") for g,d in by_generation.items() if int(g)>0 and d.get("semantic_excess_kind_rate") is not None and int(d.get("events",0)) >= int(min_generation_events)]
    intergenerational_amplification=None if g0 is None or int(by_generation.get(0,{}).get("events",0)) < int(min_generation_events) or not later else float(max(later)-g0)
    for d in by_lineage_relation.values():
        n=d["events"]
        d["semantic_excess_kind_rate"]=None if n==0 else float((d["cross_only"]-d["within_only"])/n)
        d["paired_sign_p"]=_paired_sign_p(d["cross_only"],d["within_only"])
    return {
        "world_seed":int(world_seed),"agent_seed":int(agent_seed),"steps":int(steps),"communication_scramble":bool(communication_scramble),"clusters":clusters,"events":int(tested),
        "within_cluster_action_change_rate":rate(within_any_changed),"cross_cluster_action_change_rate":rate(cross_any_changed),
        "within_cluster_kind_change_rate":rate(within_kind_changed),"cross_cluster_kind_change_rate":rate(cross_kind_changed),
        "semantic_excess_kind_rate":None if tested==0 else float((cross_kind_changed-within_kind_changed)/tested),
        "cross_only":int(cross_only),"within_only":int(within_only),"paired_sign_p":_paired_sign_p(cross_only,within_only),
        "intergenerational_amplification":intergenerational_amplification,"by_generation":by_generation,"by_lineage_relation":by_lineage_relation,"examples":examples,
        "single_pass":True,
    }
