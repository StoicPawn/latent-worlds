"""Observer-side search for an emergent non-genetic inheritance system.

Nothing in this module is visible to agents.  It analyses already existing
broadcasts, receptions, genealogies and fitness outcomes and asks whether
information begins to satisfy Darwinian criteria independently of genes:
variation, transmission, differential persistence and cross-lineage adoption.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, asdict
import math
import numpy as np

from .phase_map import long_horizon_config
from .semantic_autopsy import discover_signal_clusters, _nearest_center
from .world import World


@dataclass
class VariantStats:
    variant: int
    emissions: int
    emitters: int
    generations: tuple[int, ...]
    first_time: int
    last_time: int
    lifetime: int
    cross_lineage_adoptions: int
    same_lineage_adoptions: int
    adopter_fitness_mean: float | None
    nonadopter_fitness_mean: float | None
    propagation_number: float


def _root_map(world: World) -> dict[int, int]:
    agents = {a.id: a for a in world.agents}
    roots: dict[int, int] = {}
    for aid in agents:
        cur = agents[aid]
        seen = set()
        while cur.parent_id is not None and cur.id not in seen and cur.parent_id in agents:
            seen.add(cur.id)
            cur = agents[cur.parent_id]
        roots[aid] = cur.id
    return roots


def _assign_emissions(world: World, centers) -> list[dict]:
    out=[]
    for e in world.communication_log:
        if e.get("type") != "broadcast" or not e.get("payload"):
            continue
        q=dict(e)
        q["variant"]=_nearest_center(q["payload"], centers)
        out.append(q)
    return out


def _received_variant(row: dict, centers) -> int | None:
    payload=row.get("mean_payload", ())
    if not payload or int(row.get("received_count",0)) <= 0:
        return None
    return _nearest_center(payload, centers)


def _adoption_events(world: World, emissions: list[dict], centers, *, max_delay: int = 80) -> list[dict]:
    """Find receive -> later emit-same-variant events.

    This does not assert imitation.  It is a deliberately conservative
    observer-side operational definition of candidate transmission: an agent
    receives a variant and subsequently emits that same variant within a finite
    window.  Cross-lineage events are especially informative because genetic
    inheritance cannot directly explain them.
    """
    by_agent=defaultdict(list)
    for e in emissions:
        by_agent[int(e["source_id"])].append(e)
    for vals in by_agent.values():
        vals.sort(key=lambda z:int(z["time"]))
    roots=_root_map(world)
    source_at_time=defaultdict(list)
    # Broadcasts live one step. Reception at t sees signals emitted at t-1.
    for e in emissions:
        source_at_time[int(e["time"])+1].append(e)

    events=[]
    for r in world.social_log:
        v=_received_variant(r, centers)
        if v is None:
            continue
        aid=int(r["agent_id"]); t=int(r["time"])
        later=[e for e in by_agent.get(aid,[]) if t < int(e["time"]) <= t+max_delay and int(e["variant"])==v]
        if not later:
            continue
        first=later[0]
        possible_sources=[e for e in source_at_time.get(t,[]) if int(e["variant"])==v]
        # If geometry produced multiple sources we classify as cross-lineage only
        # when at least one plausible source is from another root and none is the
        # receiver itself. This is conservative, not a proof of causal copying.
        source_roots={roots.get(int(e["source_id"]),-1) for e in possible_sources if int(e["source_id"])!=aid}
        rr=roots.get(aid,-2)
        cross=bool(source_roots and any(sr != rr for sr in source_roots))
        same=bool(source_roots and any(sr == rr for sr in source_roots))
        events.append({
            "receiver_id":aid,"generation":int(r["generation"]),"received_time":t,
            "reemission_time":int(first["time"]),"delay":int(first["time"])-t,
            "variant":int(v),"cross_lineage":cross,"same_lineage":same,
        })
    return events



def _transmission_matrix_assay(world: World, emissions: list[dict], centers, *, max_delay: int = 80,
                               permutations: int = 99, seed: int = 0) -> dict:
    """Estimate replication fidelity and mutation among information variants.

    Each reception is paired with the receiver's first later broadcast within
    ``max_delay``. The observed received->emitted variant matrix is compared with
    a null that permutes received labels while preserving emitters, timing and
    emitted variants.
    """
    k=len(centers)
    by_agent=defaultdict(list)
    for e in emissions:
        by_agent[int(e["source_id"])].append((int(e["time"]),int(e["variant"])))
    for vals in by_agent.values(): vals.sort()
    pairs=[]
    for r in world.social_log:
        rv=_received_variant(r,centers)
        if rv is None: continue
        aid=int(r["agent_id"]); t=int(r["time"])
        fut=[(tt,vv) for tt,vv in by_agent.get(aid,[]) if t < tt <= t+max_delay]
        if fut:
            pairs.append((int(rv),int(fut[0][1])))
    if len(pairs)<25:
        return {"pairs":len(pairs),"fidelity":None,"mutation_rate":None,"null_fidelity":None,"p_value":1.0,"matrix":[]}
    rec=np.asarray([a for a,_ in pairs],dtype=int); out=np.asarray([b for _,b in pairs],dtype=int)
    M=np.zeros((k,k),dtype=int)
    for a,b in pairs: M[a,b]+=1
    fidelity=float(np.mean(rec==out)); mutation=float(1.0-fidelity)
    rng=np.random.default_rng(seed)
    null=np.asarray([np.mean(rng.permutation(rec)==out) for _ in range(int(permutations))],dtype=float)
    p=float((1+np.sum(null>=fidelity))/(1+len(null)))
    return {"pairs":len(pairs),"fidelity":fidelity,"mutation_rate":mutation,
            "null_fidelity":float(np.mean(null)),"null_sd":float(np.std(null)),"p_value":p,
            "fidelity_excess":float(fidelity-np.mean(null)),"matrix":M.tolist()}


def _genetic_turnover_timescale(world: World) -> float | None:
    """Approximate genetic-change timescale from generation intervals.

    Uses age at reproduction when reconstructable from parent/child generations.
    Since exact birth timestamps are not stored, generation depth over elapsed
    simulation time gives a conservative population-level timescale.
    """
    maxg=max((a.generation for a in world.agents), default=0)
    if maxg <= 0:
        return None
    return float(world.time/maxg)


def _variant_turnover_timescale(emissions: list[dict], n_variants: int, *, bin_width: int = 50) -> float | None:
    if not emissions or n_variants < 2:
        return None
    bins=defaultdict(lambda:np.zeros(n_variants,dtype=float))
    for e in emissions:
        bins[int(e["time"])//bin_width][int(e["variant"])]+=1.0
    keys=sorted(bins)
    dominant=[]
    for k in keys:
        if bins[k].sum() > 0:
            dominant.append((k,int(np.argmax(bins[k]))))
    changes=[]
    for (b0,v0),(b1,v1) in zip(dominant,dominant[1:]):
        if v0 != v1:
            changes.append((b1-b0)*bin_width)
    if not changes:
        return None
    return float(np.median(changes))



def _transmission_null(world: World, emissions: list[dict], centers, *, max_delay: int = 80, permutations: int = 99, seed: int = 0) -> dict:
    """Permutation null for receive -> later emit-same-variant transmission.

    Receiver identities, reception times, future emissions and genealogy stay fixed;
    only labels of received variants are permuted. Precomputation keeps this cheap.
    """
    by_agent=defaultdict(list)
    for e in emissions:
        by_agent[int(e["source_id"])].append((int(e["time"]),int(e["variant"])))
    for vals in by_agent.values(): vals.sort()
    roots=_root_map(world)
    # earliest time each variant was emitted by each genetic root
    earliest=defaultdict(lambda: math.inf)
    for e in emissions:
        key=(int(e["variant"]),roots.get(int(e["source_id"]),-1))
        earliest[key]=min(earliest[key],int(e["time"]))
    receptions=[]; eligible=[]
    k=len(centers)
    for r in world.social_log:
        v=_received_variant(r, centers)
        if v is None: continue
        aid=int(r["agent_id"]); t=int(r["time"]); rr=roots.get(aid,-2)
        possible=set(vv for tt,vv in by_agent.get(aid,[]) if t < tt <= t+max_delay)
        ok=np.zeros(k,dtype=bool)
        for vv in possible:
            # some other root must already have emitted vv by reception time
            if any(root!=rr and et<=t for (var,root),et in earliest.items() if var==vv):
                ok[vv]=True
        receptions.append(int(v)); eligible.append(ok)
    if len(receptions)<20:
        return {"observed":0,"null_mean":0.0,"null_sd":0.0,"p_value":1.0,"excess":0.0,"n_receptions":len(receptions)}
    labels=np.asarray(receptions,dtype=int); E=np.asarray(eligible,dtype=bool)
    idx=np.arange(len(labels))
    def score(lab): return int(np.sum(E[idx,lab]))
    observed=score(labels)
    rng=np.random.default_rng(seed)
    null=np.asarray([score(rng.permutation(labels)) for _ in range(int(permutations))],dtype=float)
    p=float((1+np.sum(null>=observed))/(1+len(null)))
    return {"observed":int(observed),"null_mean":float(np.mean(null)),"null_sd":float(np.std(null)),
            "p_value":p,"excess":float(observed-np.mean(null)),"n_receptions":len(receptions)}

def analyze_secondary_evolution(world: World, *, min_cluster_rows: int = 40,
                                max_delay: int = 80, min_emissions_per_variant: int = 8, permutations: int = 99) -> dict:
    clusters=discover_signal_clusters(world,min_rows=min_cluster_rows,max_k=5)
    centers=clusters.get("centers",[])
    if len(centers)<2:
        return {"supported":False,"reason":"insufficient_signal_variation","clusters":clusters}
    emissions=_assign_emissions(world,centers)
    adoptions=_adoption_events(world,emissions,centers,max_delay=max_delay)
    roots=_root_map(world)
    agents={a.id:a for a in world.agents}
    variants=[]
    for v in range(len(centers)):
        ev=[e for e in emissions if int(e["variant"])==v]
        if len(ev)<min_emissions_per_variant:
            continue
        emitter_ids={int(e["source_id"]) for e in ev}
        av=[a for a in adoptions if int(a["variant"])==v]
        adopter_ids={int(a["receiver_id"]) for a in av}
        nonadopter_ids=set(agents)-adopter_ids
        adopter_fit=[agents[i].total_harvest for i in adopter_ids if i in agents]
        nonadopter_fit=[agents[i].total_harvest for i in nonadopter_ids if i in agents]
        variants.append(VariantStats(
            variant=v,
            emissions=len(ev),emitters=len(emitter_ids),
            generations=tuple(sorted({int(e["generation"]) for e in ev})),
            first_time=min(int(e["time"]) for e in ev),last_time=max(int(e["time"]) for e in ev),
            lifetime=max(int(e["time"]) for e in ev)-min(int(e["time"]) for e in ev),
            cross_lineage_adoptions=sum(int(a["cross_lineage"]) for a in av),
            same_lineage_adoptions=sum(int(a["same_lineage"]) for a in av),
            adopter_fitness_mean=None if not adopter_fit else float(np.mean(adopter_fit)),
            nonadopter_fitness_mean=None if not nonadopter_fit else float(np.mean(nonadopter_fit)),
            propagation_number=float(sum(int(a["cross_lineage"]) for a in av)/max(1,len(emitter_ids))),
        ))
    transmission_null=_transmission_null(world,emissions,centers,max_delay=max_delay,permutations=permutations,seed=world.seed+44021)
    inheritance=_transmission_matrix_assay(world,emissions,centers,max_delay=max_delay,permutations=permutations,seed=world.seed+55109)
    genetic_tau=_genetic_turnover_timescale(world)
    cultural_tau=_variant_turnover_timescale(emissions,len(centers))
    cross=sum(v.cross_lineage_adoptions for v in variants)
    multi_gen=sum(len(v.generations)>=2 for v in variants)
    # Selection-like dynamics in the information channel itself: variants must
    # have measurably different propagation numbers (cross-lineage adoptions per
    # emitter). This is more relevant than merely correlating a signal with host
    # harvest, which can be confounded by host quality.
    propagation=[v.propagation_number for v in variants if v.emissions>=min_emissions_per_variant]
    if len(propagation)>=2:
        pm=float(np.mean(propagation)); ps=float(np.std(propagation))
        propagation_cv=float(ps/max(pm,1e-12))
        differential=bool(propagation_cv>=0.25 and (max(propagation)-min(propagation))>=0.5)
    else:
        propagation_cv=0.0; differential=False
    faster=bool(cultural_tau is not None and genetic_tau is not None and cultural_tau < genetic_tau)
    # Candidate only: these are necessary observational signatures, not proof of
    # a second evolutionary system. Causal scramble/censorship assays remain next.
    transmission_supported=bool(transmission_null["observed"]>=5 and transmission_null["excess"]>=3.0 and transmission_null["p_value"]<=0.05)
    inheritance_supported=bool(inheritance.get("fidelity") is not None and inheritance["pairs"]>=25 and inheritance["fidelity_excess"]>=0.05 and inheritance["p_value"]<=0.05 and 0.05 <= inheritance["mutation_rate"] <= 0.90)
    supported=bool(len(variants)>=2 and transmission_supported and inheritance_supported and multi_gen>=1 and differential and faster)
    return {
        "supported":supported,
        "clusters":clusters,
        "variant_stats":[asdict(v) for v in variants],
        "adoption_events":len(adoptions),
        "cross_lineage_adoptions":cross,
        "transmission_null":transmission_null,
        "inheritance_assay":inheritance,
        "multi_generation_variants":multi_gen,
        "genetic_timescale":genetic_tau,
        "information_variant_timescale":cultural_tau,
        "information_faster_than_genes":faster,
        "differential_persistence_or_fitness":differential,
        "propagation_cv":propagation_cv,
        "criteria":{
            "variation":len(variants)>=2,
            "cross_lineage_transmission":transmission_supported,
            "replication_with_variation":inheritance_supported,
            "multi_generation_persistence":multi_gen>=1,
            "differential_dynamics":differential,
            "faster_than_genetic_turnover":faster,
        },
    }


def run_secondary_evolution_probe(world_seed:int, agent_seed:int, *, steps:int=900,
                                  information_level:float=0.35, signal_cost:float=0.03,
                                  config_overrides:dict|None=None) -> dict:
    cfg=long_horizon_config(information_level=information_level,signal_cost=signal_cost,
                            communication_enabled=True,agent_seed=int(agent_seed))
    if config_overrides:
        for k,v in config_overrides.items(): setattr(cfg,k,v)
    w=World(cfg,seed=int(world_seed)).run(int(steps))
    out=analyze_secondary_evolution(w)
    out.update({"world_seed":int(world_seed),"agent_seed":int(agent_seed),"steps":int(w.time),
                "population":sum(a.alive for a in w.agents),"max_generation":max((a.generation for a in w.agents),default=0)})
    return out


def generational_inheritance_assay(world: World, *, min_cluster_rows: int = 40,
                                  max_delay: int = 80, permutations: int = 199,
                                  min_pairs: int = 12) -> dict:
    """Resolve information replication/mutation by receiver generation.

    This is observer-side only.  For each reception, pair the received variant
    with the receiver's first later emission within ``max_delay`` and test whether
    received and emitted variant agree more often than under a within-generation
    permutation null.  Reporting by generation prevents abundant G0/G1 traffic
    from masquerading as deep cultural inheritance.
    """
    clusters=discover_signal_clusters(world,min_rows=min_cluster_rows,max_k=5)
    centers=clusters.get("centers",[])
    if len(centers)<2:
        return {"clusters":clusters,"by_generation":{},"max_supported_generation":None}
    emissions=_assign_emissions(world,centers)
    by_agent=defaultdict(list)
    for e in emissions:
        by_agent[int(e["source_id"])].append((int(e["time"]),int(e["variant"])))
    for vals in by_agent.values(): vals.sort()
    pairs=defaultdict(list)
    for r in world.social_log:
        rv=_received_variant(r,centers)
        if rv is None: continue
        aid=int(r["agent_id"]); t=int(r["time"]); g=int(r.get("generation",0))
        fut=[(tt,vv) for tt,vv in by_agent.get(aid,[]) if t < tt <= t+max_delay]
        if fut: pairs[g].append((int(rv),int(fut[0][1])))
    out={}
    for g,vals in sorted(pairs.items()):
        n=len(vals); rec=np.asarray([a for a,_ in vals],dtype=int); emit=np.asarray([b for _,b in vals],dtype=int)
        fid=float(np.mean(rec==emit)) if n else None
        mut=None if fid is None else float(1.0-fid)
        if n < int(min_pairs):
            out[str(g)]={"pairs":n,"fidelity":fid,"mutation_rate":mut,"null_fidelity":None,
                         "fidelity_excess":None,"p_value":1.0,"supported":False}
            continue
        rng=np.random.default_rng(int(world.seed)+73001+997*g)
        null=np.asarray([np.mean(rng.permutation(rec)==emit) for _ in range(int(permutations))],dtype=float)
        excess=float(fid-np.mean(null)); p=float((1+np.sum(null>=fid))/(1+len(null)))
        out[str(g)]={"pairs":n,"fidelity":fid,"mutation_rate":mut,"null_fidelity":float(np.mean(null)),
                     "null_sd":float(np.std(null)),"fidelity_excess":excess,"p_value":p,
                     "supported":bool(excess>=0.05 and p<=0.05 and 0.05<=mut<=0.90)}
    supported=[int(g) for g,v in out.items() if v.get("supported")]
    return {"clusters":clusters,"by_generation":out,
            "max_supported_generation":max(supported) if supported else None,
            "deep_replication":bool(any(g>=2 for g in supported))}


def generational_propagation_assay(world: World, *, min_cluster_rows: int = 40,
                                   max_delay: int = 80, min_emissions: int = 3) -> dict:
    """Measure differential propagation of variants separately by adopter generation."""
    clusters=discover_signal_clusters(world,min_rows=min_cluster_rows,max_k=5)
    centers=clusters.get("centers",[])
    if len(centers)<2:
        return {"clusters":clusters,"by_generation":{},"max_differential_generation":None}
    emissions=_assign_emissions(world,centers)
    adoptions=_adoption_events(world,emissions,centers,max_delay=max_delay)
    bygen={}
    gens=sorted(set(int(a["generation"]) for a in adoptions))
    for g in gens:
        ag=[a for a in adoptions if int(a["generation"])==g and a.get("cross_lineage")]
        rates=[]; rows=[]
        for v in range(len(centers)):
            emitters={int(e["source_id"]) for e in emissions if int(e["variant"])==v and int(e.get("generation",-1))==g}
            vg=[a for a in ag if int(a["variant"])==v]
            if len(emitters)>=1 and len(vg)>=int(min_emissions):
                rate=float(len(vg)/len(emitters)); rates.append(rate)
                rows.append({"variant":v,"cross_lineage_adoptions":len(vg),"emitters":len(emitters),"propagation_number":rate})
        if len(rates)>=2:
            mean=float(np.mean(rates)); cv=float(np.std(rates)/max(mean,1e-12)); spread=float(max(rates)-min(rates))
            differential=bool(cv>=0.25 and spread>=0.5)
        else:
            cv=0.0; spread=0.0; differential=False
        bygen[str(g)]={"variant_rows":rows,"propagation_cv":cv,"propagation_spread":spread,
                       "differential":differential,"cross_lineage_adoptions":len(ag)}
    supported=[int(g) for g,v in bygen.items() if v.get("differential")]
    return {"clusters":clusters,"by_generation":bygen,
            "max_differential_generation":max(supported) if supported else None,
            "deep_differential_propagation":bool(any(g>=2 for g in supported))}


def transmission_timescale_assay(world: World, *, min_cluster_rows: int = 40,
                                 max_delay: int = 80, min_events: int = 12) -> dict:
    """Compare information-transmission delay with genetic-generation timescale.

    The informational timescale is the median receive->same-variant re-emission
    delay among cross-lineage candidate transmissions. This is a direct timescale
    for the putative non-genetic channel and does not require the population's
    dominant variant to switch identity.
    """
    clusters=discover_signal_clusters(world,min_rows=min_cluster_rows,max_k=5)
    centers=clusters.get("centers",[])
    if len(centers)<2:
        return {"events":0,"median_delay":None,"genetic_timescale":_genetic_turnover_timescale(world),
                "speed_ratio":None,"faster_than_genes":False,"by_generation":{}}
    emissions=_assign_emissions(world,centers)
    events=[e for e in _adoption_events(world,emissions,centers,max_delay=max_delay) if e.get("cross_lineage")]
    genetic=_genetic_turnover_timescale(world)
    def summary(vals):
        if len(vals)<int(min_events): return {"events":len(vals),"median_delay":None,"mean_delay":None}
        arr=np.asarray([int(e["delay"]) for e in vals],dtype=float)
        return {"events":len(vals),"median_delay":float(np.median(arr)),"mean_delay":float(np.mean(arr))}
    overall=summary(events)
    by={}
    for g in sorted(set(int(e["generation"]) for e in events)):
        by[str(g)]=summary([e for e in events if int(e["generation"])==g])
    med=overall.get("median_delay")
    ratio=None if med is None or genetic is None or med<=0 else float(genetic/med)
    return {"events":overall["events"],"median_delay":med,"mean_delay":overall.get("mean_delay"),
            "genetic_timescale":genetic,"speed_ratio":ratio,
            "faster_than_genes":bool(ratio is not None and ratio>1.0),"by_generation":by}


def deep_secondary_evolution_assay(world: World, *, min_generation: int = 2,
                                   permutations: int = 199, min_pairs: int = 12) -> dict:
    """Strict observer-side candidate test for a deep non-genetic evolutionary channel.

    A generation g qualifies only if it independently shows (i) replication with
    non-zero variation above a permutation null and (ii) differential propagation
    among at least two variants. The channel must also operate faster than genetic
    generational turnover. Scramble/censorship controls are intentionally external:
    a real-world candidate is not a claim until those controls fail.
    """
    inh=generational_inheritance_assay(world,permutations=permutations,min_pairs=min_pairs)
    prop=generational_propagation_assay(world,min_emissions=3)
    speed=transmission_timescale_assay(world,min_events=min_pairs)
    qualifying=[]
    gens=sorted(set(inh.get("by_generation",{})) | set(prop.get("by_generation",{})), key=int)
    for gs in gens:
        g=int(gs); iv=inh.get("by_generation",{}).get(gs,{})
        pv=prop.get("by_generation",{}).get(gs,{})
        if g>=int(min_generation) and iv.get("supported") and pv.get("differential"):
            qualifying.append(g)
    supported=bool(qualifying and speed.get("faster_than_genes"))
    return {"supported":supported,"qualifying_generations":qualifying,
            "max_qualifying_generation":max(qualifying) if qualifying else None,
            "inheritance":inh,"propagation":prop,"timescale":speed,
            "criteria":{"deep_replication_with_variation":bool(qualifying),
                        "differential_propagation_same_generation":bool(qualifying),
                        "faster_than_genes":bool(speed.get("faster_than_genes"))}}


def conditional_genetic_inheritance_assay(world: World, *, min_cluster_rows: int = 40,
                                           max_delay: int = 80, permutations: int = 199,
                                           min_pairs: int = 20, min_generation: int = 2) -> dict:
    """Test information inheritance beyond genetic-lineage predispositions.

    Received labels are permuted *within receiver genetic root and generation*.
    This preserves lineage-specific signal preferences and generation effects.
    Excess fidelity therefore asks whether the actually received information
    predicts later emission beyond what the receiver's genetic lineage explains.
    """
    clusters=discover_signal_clusters(world,min_rows=min_cluster_rows,max_k=5)
    centers=clusters.get("centers",[])
    if len(centers)<2: return {"by_generation":{},"deep_supported":False}
    emissions=_assign_emissions(world,centers); roots=_root_map(world)
    by_agent=defaultdict(list)
    for e in emissions: by_agent[int(e['source_id'])].append((int(e['time']),int(e['variant'])))
    for vals in by_agent.values(): vals.sort()
    pairs=defaultdict(list)
    for r in world.social_log:
        rv=_received_variant(r,centers)
        if rv is None: continue
        aid=int(r['agent_id']); t=int(r['time']); g=int(r.get('generation',0)); root=roots.get(aid,-1)
        fut=[(tt,vv) for tt,vv in by_agent.get(aid,[]) if t < tt <= t+max_delay]
        if fut: pairs[g].append((int(rv),int(fut[0][1]),int(root)))
    out={}; rng=np.random.default_rng(int(world.seed)+99173)
    for g,vals in sorted(pairs.items()):
        n=len(vals); rec=np.array([a for a,_,_ in vals],int); emit=np.array([b for _,b,_ in vals],int); root=np.array([c for _,_,c in vals],int)
        fid=float(np.mean(rec==emit)) if n else None
        groups=[np.flatnonzero(root==r) for r in np.unique(root)]
        informative_groups=sum(len(ix)>=2 and len(np.unique(rec[ix]))>=2 for ix in groups)
        if n<min_pairs or informative_groups<1:
            out[str(g)]={'pairs':n,'fidelity':fid,'conditional_null_fidelity':None,'conditional_excess':None,'p_value':1.0,'informative_roots':informative_groups,'supported':False}; continue
        null=[]
        for _ in range(int(permutations)):
            rp=rec.copy()
            for ix in groups: rp[ix]=rng.permutation(rp[ix])
            null.append(np.mean(rp==emit))
        null=np.asarray(null,float); ex=float(fid-null.mean()); p=float((1+np.sum(null>=fid))/(1+len(null)))
        out[str(g)]={'pairs':n,'fidelity':fid,'conditional_null_fidelity':float(null.mean()),'conditional_null_sd':float(null.std()),'conditional_excess':ex,'p_value':p,'informative_roots':informative_groups,'supported':bool(ex>=.05 and p<=.05)}
    deep=any(int(g)>=int(min_generation) and v.get('supported') for g,v in out.items())
    return {'by_generation':out,'deep_supported':bool(deep)}


def autonomous_secondary_evolution_assay(world: World, *, min_generation: int = 2,
                                          permutations: int = 199, min_pairs: int = 12) -> dict:
    """Stricter candidate assay for a genuinely non-genetic evolutionary channel.

    In addition to the v2.7 deep Darwinian signatures, information inheritance
    must survive a null that conditions on receiver genetic root and generation.
    This rules out apparent copying caused by lineage-specific inherited signal
    preferences.  This is still a candidate criterion, not a claim of culture.
    """
    deep=deep_secondary_evolution_assay(world,min_generation=min_generation,
                                        permutations=permutations,min_pairs=min_pairs)
    cond=conditional_genetic_inheritance_assay(world,min_generation=min_generation,
                                               permutations=permutations,min_pairs=min_pairs)
    q=[]
    for g in deep.get('qualifying_generations',[]):
        row=cond.get('by_generation',{}).get(str(g),{})
        if row.get('supported'): q.append(int(g))
    return {
        'supported':bool(deep.get('supported') and q),
        'qualifying_generations':q,
        'deep_darwinian':deep,
        'genetic_conditioned_inheritance':cond,
        'criteria':{
            'replication_with_variation_and_selection':bool(deep.get('supported')),
            'inheritance_beyond_genetic_lineage':bool(q),
            'faster_than_genes':bool(deep.get('timescale',{}).get('faster_than_genes')),
        },
    }


def continuous_conditional_inheritance_assay(world: World, *, carrier: str = "broadcast",
                                              max_delay: int = 80, min_pairs: int = 40,
                                              permutations: int = 199,
                                              min_generation: int = 1) -> dict:
    """Cluster-free inheritance test conditional on genetic lineage.

    Tests whether a received continuous payload predicts the receiver's later emitted
    payload after removing receiver-root × generation means.  The statistic is a
    normalized residual cross-covariance (multivariate RV-like coefficient).  The
    null permutes received residual vectors within genetic root and generation, so
    lineage-specific signal biases and generation effects are preserved.

    ``carrier='broadcast'`` pairs mean received transient signal -> later broadcast.
    ``carrier='mark'`` pairs mean read persistent mark -> later inscription.
    """
    if carrier not in {"broadcast", "mark"}:
        raise ValueError("carrier must be 'broadcast' or 'mark'")
    roots=_root_map(world)
    out_field='mean_payload' if carrier=='broadcast' else 'mean_mark_payload'
    count_field='received_count' if carrier=='broadcast' else 'received_mark_count'
    emit_type='broadcast' if carrier=='broadcast' else 'inscription'
    emissions=defaultdict(list)
    for e in world.communication_log:
        if e.get('type')!=emit_type or not e.get('payload'): continue
        emissions[int(e['source_id'])].append((int(e['time']),np.asarray(e['payload'],float)))
    for vals in emissions.values(): vals.sort(key=lambda z:z[0])
    pairs=defaultdict(list)
    for r in world.social_log:
        if int(r.get(count_field,0))<=0 or not r.get(out_field): continue
        aid=int(r['agent_id']); t=int(r['time']); g=int(r.get('generation',0)); root=roots.get(aid,-1)
        fut=[(tt,p) for tt,p in emissions.get(aid,[]) if t < tt <= t+max_delay]
        if fut:
            x=np.asarray(r[out_field],float); y=np.asarray(fut[0][1],float)
            d=min(len(x),len(y))
            if d: pairs[g].append((x[:d],y[:d],int(root)))
    rng=np.random.default_rng(int(world.seed)+2718281+(0 if carrier=='broadcast' else 314159))
    results={}
    for g,vals in sorted(pairs.items()):
        n=len(vals)
        if n<min_pairs:
            results[str(g)]={'pairs':n,'statistic':None,'null_mean':None,'excess':None,'p_value':1.0,'informative_roots':0,'supported':False}; continue
        X=np.stack([v[0] for v in vals]); Y=np.stack([v[1] for v in vals]); R=np.asarray([v[2] for v in vals],int)
        groups=[np.flatnonzero(R==r) for r in np.unique(R)]
        informative=sum(len(ix)>=3 for ix in groups)
        if informative<1:
            results[str(g)]={'pairs':n,'statistic':None,'null_mean':None,'excess':None,'p_value':1.0,'informative_roots':informative,'supported':False}; continue
        # Residualize both payloads within genetic roots. Generation is already fixed.
        Xr=X.copy(); Yr=Y.copy()
        for ix in groups:
            Xr[ix]-=Xr[ix].mean(axis=0,keepdims=True); Yr[ix]-=Yr[ix].mean(axis=0,keepdims=True)
        def stat(A,B):
            C=A.T@B
            den=float(np.sqrt(np.sum((A.T@A)**2)*np.sum((B.T@B)**2)))+1e-12
            return float(np.sum(C*C)/den)
        obs=stat(Xr,Yr)
        null=[]
        for _ in range(int(permutations)):
            Xp=Xr.copy()
            for ix in groups: Xp[ix]=Xp[rng.permutation(ix)]
            null.append(stat(Xp,Yr))
        null=np.asarray(null,float); ex=float(obs-null.mean()); p=float((1+np.sum(null>=obs))/(1+len(null)))
        results[str(g)]={'pairs':n,'statistic':obs,'null_mean':float(null.mean()),'null_sd':float(null.std()),
                         'excess':ex,'p_value':p,'informative_roots':informative,
                         'supported':bool(ex>=.02 and p<=.05)}
    deep=any(int(g)>=min_generation and v.get('supported') for g,v in results.items())
    return {'carrier':carrier,'by_generation':results,'deep_supported':bool(deep)}


def directional_continuous_transmission_assay(world: World, *, carrier: str = "broadcast",
                                               max_delay: int = 80, min_pairs: int = 40,
                                               permutations: int = 199,
                                               min_generation: int = 1) -> dict:
    """Temporal-direction control for continuous information transmission.

    For each reception/read with both a prior and a later emission by the same
    receiver within ``max_delay``, compare dependence of the received payload on
    the *later* payload versus the *prior* payload.  The permutation null swaps
    prior/later outcomes within each event.  Agent identity, local history and the
    received payload are therefore held fixed. A positive effect is a necessary
    signature for information flowing reception -> later emission rather than a
    static lineage or shared-context correlation.
    """
    if carrier not in {"broadcast", "mark"}:
        raise ValueError("carrier must be 'broadcast' or 'mark'")
    recv_field='mean_payload' if carrier=='broadcast' else 'mean_mark_payload'
    count_field='received_count' if carrier=='broadcast' else 'received_mark_count'
    emit_type='broadcast' if carrier=='broadcast' else 'inscription'
    emissions=defaultdict(list)
    for e in world.communication_log:
        if e.get('type')==emit_type and e.get('payload'):
            emissions[int(e['source_id'])].append((int(e['time']),np.asarray(e['payload'],float)))
    for vals in emissions.values(): vals.sort(key=lambda z:z[0])
    triples=defaultdict(list)
    for r in world.social_log:
        if int(r.get(count_field,0))<=0 or not r.get(recv_field): continue
        aid=int(r['agent_id']); t=int(r['time']); g=int(r.get('generation',0)); x=np.asarray(r[recv_field],float)
        pre=[(tt,p) for tt,p in emissions.get(aid,[]) if t-max_delay <= tt < t]
        post=[(tt,p) for tt,p in emissions.get(aid,[]) if t < tt <= t+max_delay]
        if not pre or not post: continue
        y0=pre[-1][1]; y1=post[0][1]; d=min(len(x),len(y0),len(y1))
        if d: triples[g].append((x[:d],y0[:d],y1[:d]))
    rng=np.random.default_rng(int(world.seed)+1618033+(0 if carrier=='broadcast' else 271828))
    out={}
    def dep(A,B):
        # Center globally within generation; prior/later swap null preserves all marginals.
        A=A-A.mean(axis=0,keepdims=True); B=B-B.mean(axis=0,keepdims=True)
        C=A.T@B; den=float(np.sqrt(np.sum((A.T@A)**2)*np.sum((B.T@B)**2)))+1e-12
        return float(np.sum(C*C)/den)
    for g,vals in sorted(triples.items()):
        n=len(vals)
        if n<min_pairs:
            out[str(g)]={'pairs':n,'after_dependence':None,'before_dependence':None,'directional_excess':None,'p_value':1.0,'supported':False}; continue
        X=np.stack([v[0] for v in vals]); Y0=np.stack([v[1] for v in vals]); Y1=np.stack([v[2] for v in vals])
        before=dep(X,Y0); after=dep(X,Y1); diff=float(after-before)
        null=[]
        for _ in range(int(permutations)):
            swap=rng.random(n)<.5
            A=Y0.copy(); B=Y1.copy(); A[swap],B[swap]=Y1[swap],Y0[swap]
            null.append(dep(X,B)-dep(X,A))
        null=np.asarray(null,float); p=float((1+np.sum(null>=diff))/(1+len(null)))
        out[str(g)]={'pairs':n,'after_dependence':after,'before_dependence':before,'directional_excess':diff,
                     'null_mean':float(null.mean()),'null_sd':float(null.std()),'p_value':p,
                     'supported':bool(diff>=.02 and p<=.05)}
    deep=any(int(g)>=min_generation and v.get('supported') for g,v in out.items())
    return {'carrier':carrier,'by_generation':out,'deep_supported':bool(deep)}
