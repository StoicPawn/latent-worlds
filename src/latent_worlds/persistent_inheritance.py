"""Observer-side assay for inheritance through persistent environmental marks.

No dynamics are changed.  Agents already can inscribe anonymous numeric marks and
observe nearby marks.  This module asks whether read -> later inscribe relations
carry variant information beyond receiver genetic lineage, and whether mark
variants propagate differentially across unrelated lineages.
"""
from __future__ import annotations
from collections import defaultdict
import numpy as np

from .semantic_autopsy import discover_signal_clusters, _nearest_center
from .secondary_evolution import _root_map


def discover_mark_clusters(world, *, min_rows=40, max_k=5):
    # Reuse the same deterministic clustering logic by temporarily presenting
    # inscription events as the communication corpus expected by the helper.
    class Proxy:
        pass
    p=Proxy(); p.communication_log=[dict(e, type='broadcast') for e in world.communication_log if e.get('type')=='inscription']
    p.seed=world.seed
    return discover_signal_clusters(p,min_rows=min_rows,max_k=max_k)


def _inscriptions(world, centers):
    rows=[]
    for e in world.communication_log:
        if e.get('type')!='inscription' or not e.get('payload'): continue
        q=dict(e); q['variant']=_nearest_center(q['payload'],centers); rows.append(q)
    return rows


def conditional_mark_inheritance_assay(world, *, max_delay=160, min_rows=40,
                                       permutations=199, min_pairs=20,
                                       min_generation=1):
    """Does a read mark predict a later inscription beyond genetic lineage?

    Null permutations occur within receiver genetic root and generation, preserving
    inherited lineage-specific inscription preferences.  A positive excess therefore
    requires information in the *read mark* itself to predict the later inscription.
    """
    clusters=discover_mark_clusters(world,min_rows=min_rows,max_k=5)
    centers=clusters.get('centers',[])
    if len(centers)<2:
        return {'clusters':clusters,'by_generation':{},'deep_supported':False}
    ins=_inscriptions(world,centers); roots=_root_map(world)
    by_agent=defaultdict(list)
    for e in ins: by_agent[int(e['source_id'])].append((int(e['time']),int(e['variant'])))
    for vals in by_agent.values(): vals.sort()
    pairs=defaultdict(list)
    for r in world.social_log:
        if int(r.get('received_mark_count',0))<=0 or not r.get('mean_mark_payload'): continue
        rv=_nearest_center(r['mean_mark_payload'],centers)
        aid=int(r['agent_id']); t=int(r['time']); g=int(r.get('generation',0)); root=roots.get(aid,-1)
        fut=[(tt,v) for tt,v in by_agent.get(aid,[]) if t < tt <= t+max_delay]
        if fut: pairs[g].append((int(rv),int(fut[0][1]),int(root)))
    out={}; rng=np.random.default_rng(int(world.seed)+182731)
    for g,vals in sorted(pairs.items()):
        rec=np.asarray([a for a,_,_ in vals],int); emit=np.asarray([b for _,b,_ in vals],int); root=np.asarray([c for _,_,c in vals],int)
        n=len(vals); fid=float(np.mean(rec==emit)) if n else None
        groups=[np.flatnonzero(root==x) for x in np.unique(root)] if n else []
        informative=sum(len(ix)>=2 and len(np.unique(rec[ix]))>=2 for ix in groups)
        if n<min_pairs or informative<1:
            out[str(g)]={'pairs':n,'fidelity':fid,'conditional_null_fidelity':None,'conditional_excess':None,'p_value':1.0,'informative_roots':informative,'supported':False}
            continue
        null=[]
        for _ in range(int(permutations)):
            rp=rec.copy()
            for ix in groups: rp[ix]=rng.permutation(rp[ix])
            null.append(float(np.mean(rp==emit)))
        null=np.asarray(null,float); ex=float(fid-null.mean()); p=float((1+np.sum(null>=fid))/(1+len(null)))
        mut=float(1-fid)
        out[str(g)]={'pairs':n,'fidelity':fid,'mutation_rate':mut,'conditional_null_fidelity':float(null.mean()),
                     'conditional_excess':ex,'p_value':p,'informative_roots':informative,
                     'supported':bool(ex>=.05 and p<=.05 and .05<=mut<=.90)}
    deep=any(int(g)>=min_generation and v.get('supported') for g,v in out.items())
    return {'clusters':clusters,'by_generation':out,'deep_supported':bool(deep)}


def mark_propagation_assay(world, *, min_rows=40, min_reads=4):
    """Differential cross-lineage exposure per mark author, by mark variant."""
    clusters=discover_mark_clusters(world,min_rows=min_rows,max_k=5); centers=clusters.get('centers',[])
    if len(centers)<2: return {'variant_rows':[],'differential':False}
    ins=_inscriptions(world,centers); roots=_root_map(world)
    # Count observer-side reads whose listed mark sources include an unrelated author.
    reads=defaultdict(set)
    by_source={int(e['source_id']):int(e['variant']) for e in ins}
    for r in world.social_log:
        aid=int(r['agent_id']); rr=roots.get(aid,-1)
        for sid in r.get('mark_source_ids',()):
            if roots.get(int(sid),-2)!=rr and int(sid) in by_source:
                reads[by_source[int(sid)]].add((int(aid),int(r['time'])))
    rows=[]
    for v in sorted(set(e['variant'] for e in ins)):
        authors={int(e['source_id']) for e in ins if int(e['variant'])==v}
        n=len(reads.get(v,set()))
        if authors and n>=min_reads:
            rows.append({'variant':int(v),'authors':len(authors),'cross_lineage_reads':n,'propagation_number':float(n/len(authors))})
    rates=[x['propagation_number'] for x in rows]
    if len(rates)>=2:
        cv=float(np.std(rates)/max(np.mean(rates),1e-12)); spread=float(max(rates)-min(rates)); diff=bool(cv>=.25 and spread>=.5)
    else: cv=spread=0.0; diff=False
    return {'variant_rows':rows,'propagation_cv':cv,'propagation_spread':spread,'differential':diff}


def persistent_secondary_evolution_assay(world, *, min_generation=1, permutations=199):
    inh=conditional_mark_inheritance_assay(world,min_generation=min_generation,permutations=permutations)
    prop=mark_propagation_assay(world)
    qualifying=[int(g) for g,v in inh.get('by_generation',{}).items() if int(g)>=min_generation and v.get('supported')]
    return {'supported':bool(qualifying and prop.get('differential')),
            'qualifying_generations':qualifying,'inheritance':inh,'propagation':prop,
            'criteria':{'inheritance_beyond_genetic_lineage':bool(qualifying),'differential_propagation':bool(prop.get('differential'))}}
