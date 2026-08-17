"""Observer-side reconstruction of conservative information lineages.

This module never affects agents or world dynamics.  It reconstructs candidate
transmission edges only when a reception can be attributed to a *unique*
plausible source broadcasting the same emergent variant one step earlier.
The goal is to ask whether information forms lineages that cross genetic roots
and outlive individual carriers, rather than merely correlating with genealogy.
"""
from __future__ import annotations
from collections import defaultdict, deque
import numpy as np

from .semantic_autopsy import discover_signal_clusters, _nearest_center
from .secondary_evolution import _root_map


def reconstruct_information_lineages(world, *, min_cluster_rows: int = 40, max_delay: int = 80):
    clusters = discover_signal_clusters(world, min_rows=min_cluster_rows, max_k=5)
    centers = clusters.get("centers", [])
    if len(centers) < 2:
        return {"clusters": clusters, "edges": [], "components": [], "supported": False}

    emissions=[]
    by_agent=defaultdict(list)
    at_receive_time=defaultdict(list)
    for e in world.communication_log:
        if e.get("type") != "broadcast" or not e.get("payload"):
            continue
        q=dict(e); q["variant"]=_nearest_center(q["payload"], centers)
        emissions.append(q)
        by_agent[int(q["source_id"])].append(q)
        at_receive_time[int(q["time"])+1].append(q)
    for vals in by_agent.values(): vals.sort(key=lambda x:int(x["time"]))

    roots=_root_map(world)
    agents={a.id:a for a in world.agents}
    edges=[]
    for r in world.social_log:
        if int(r.get("received_count",0)) <= 0 or not r.get("mean_payload"):
            continue
        rv=_nearest_center(r["mean_payload"], centers)
        aid=int(r["agent_id"]); t=int(r["time"])
        sources=[e for e in at_receive_time.get(t,[]) if int(e["source_id"])!=aid and int(e["variant"])==rv]
        # Conservative attribution: ambiguous receptions do not create lineage edges.
        if len(sources) != 1:
            continue
        src=sources[0]; sid=int(src["source_id"])
        future=[e for e in by_agent.get(aid,[]) if t < int(e["time"]) <= t+max_delay]
        if not future:
            continue
        out=future[0]
        edges.append({
            "source_id":sid,"receiver_id":aid,"received_variant":int(rv),
            "reemitted_variant":int(out["variant"]),"reception_time":t,"reemission_time":int(out["time"]),
            "delay":int(out["time"])-t,"source_root":roots.get(sid,-1),"receiver_root":roots.get(aid,-2),
            "source_generation":int(src.get("generation", getattr(agents.get(sid),"generation",0))),
            "receiver_generation":int(r.get("generation", getattr(agents.get(aid),"generation",0))),
            "faithful":bool(int(rv)==int(out["variant"])),
            "cross_lineage":bool(roots.get(sid,-1)!=roots.get(aid,-2)),
        })

    # Connected components on the transmission graph (ignoring direction).
    adj=defaultdict(set)
    for e in edges:
        adj[e["source_id"]].add(e["receiver_id"]); adj[e["receiver_id"]].add(e["source_id"])
    seen=set(); comps=[]
    for node in list(adj):
        if node in seen: continue
        q=deque([node]); seen.add(node); nodes=[]
        while q:
            u=q.popleft(); nodes.append(u)
            for v in adj[u]:
                if v not in seen: seen.add(v); q.append(v)
        ce=[e for e in edges if e["source_id"] in nodes and e["receiver_id"] in nodes]
        times=[e["reception_time"] for e in ce] + [e["reemission_time"] for e in ce]
        gr=sorted({roots.get(n,-1) for n in nodes})
        gens=sorted({getattr(agents.get(n),"generation",0) for n in nodes if n in agents})
        faithful=sum(int(e["faithful"]) for e in ce)
        comps.append({
            "nodes":len(nodes),"edges":len(ce),"genetic_roots":len(gr),"generations":gens,
            "generation_span":0 if not gens else int(max(gens)-min(gens)),
            "lifetime":0 if not times else int(max(times)-min(times)),
            "cross_lineage_edges":sum(int(e["cross_lineage"]) for e in ce),
            "faithful_fraction":None if not ce else float(faithful/len(ce)),
        })
    comps.sort(key=lambda c:(c["generation_span"],c["genetic_roots"],c["edges"]), reverse=True)
    cross=sum(int(e["cross_lineage"]) for e in edges)
    deep=[c for c in comps if c["generation_span"]>=2 and c["genetic_roots"]>=2 and c["edges"]>=5]
    return {
        "clusters":clusters,"edges":edges,"components":comps,
        "unique_attributed_edges":len(edges),"cross_lineage_edges":cross,
        "cross_lineage_fraction":None if not edges else float(cross/len(edges)),
        "max_information_generation_span":max((c["generation_span"] for c in comps),default=0),
        "max_genetic_roots_in_component":max((c["genetic_roots"] for c in comps),default=0),
        "deep_components":len(deep),
        "supported":bool(deep),
    }


def genetic_information_decoupling(world, *, min_cluster_rows: int = 40) -> dict:
    """Quantify how strongly emergent signal variants are tied to genetic roots.

    Returns normalized mutual information (NMI) between variant identity and the
    emitter's genetic root, plus the fraction of attributed transmission edges
    crossing roots. Low NMI together with high cross-root transmission is the
    observer-side signature expected from a horizontally transmitted channel.
    """
    lin=reconstruct_information_lineages(world,min_cluster_rows=min_cluster_rows)
    centers=lin.get("clusters",{}).get("centers",[])
    if len(centers)<2:
        return {"n_emissions":0,"variant_root_nmi":None,"cross_lineage_fraction":lin.get("cross_lineage_fraction"),"decoupled":False}
    roots=_root_map(world)
    rows=[]
    for e in world.communication_log:
        if e.get("type")!="broadcast" or not e.get("payload"): continue
        rows.append((_nearest_center(e["payload"],centers), roots.get(int(e["source_id"]),-1)))
    if len(rows)<20:
        return {"n_emissions":len(rows),"variant_root_nmi":None,"cross_lineage_fraction":lin.get("cross_lineage_fraction"),"decoupled":False}
    vs=[v for v,_ in rows]; rs=[r for _,r in rows]
    uv={x:i for i,x in enumerate(sorted(set(vs)))}; ur={x:i for i,x in enumerate(sorted(set(rs)))}
    M=np.zeros((len(uv),len(ur)),dtype=float)
    for v,r in rows: M[uv[v],ur[r]]+=1
    P=M/M.sum(); pv=P.sum(axis=1,keepdims=True); pr=P.sum(axis=0,keepdims=True)
    nz=P>0
    denom=pv@pr
    mi=float(np.sum(P[nz]*np.log(P[nz]/denom[nz])))
    hv=float(-np.sum(pv[pv>0]*np.log(pv[pv>0]))); hr=float(-np.sum(pr[pr>0]*np.log(pr[pr>0])))
    nmi=0.0 if min(hv,hr)<=1e-12 else float(mi/min(hv,hr))
    cross=lin.get("cross_lineage_fraction")
    return {"n_emissions":len(rows),"variant_root_nmi":nmi,"cross_lineage_fraction":cross,
            "decoupled":bool(cross is not None and cross>=0.5 and nmi<=0.25)}


def genetic_information_decoupling_by_generation(world, *, min_cluster_rows: int = 40, min_rows: int = 20) -> dict:
    """Variant/root coupling separately for each emitter generation."""
    lin=reconstruct_information_lineages(world,min_cluster_rows=min_cluster_rows)
    centers=lin.get("clusters",{}).get("centers",[])
    if len(centers)<2: return {"by_generation":{}}
    roots=_root_map(world); rows=defaultdict(list)
    for e in world.communication_log:
        if e.get("type")!="broadcast" or not e.get("payload"): continue
        g=int(e.get("generation",0)); rows[g].append((_nearest_center(e["payload"],centers),roots.get(int(e["source_id"]),-1)))
    out={}
    for g,vals in sorted(rows.items()):
        if len(vals)<min_rows:
            out[str(g)]={"n_emissions":len(vals),"variant_root_nmi":None}; continue
        vs=[v for v,_ in vals]; rs=[r for _,r in vals]
        uv={x:i for i,x in enumerate(sorted(set(vs)))}; ur={x:i for i,x in enumerate(sorted(set(rs)))}
        M=np.zeros((len(uv),len(ur)),dtype=float)
        for v,r in vals: M[uv[v],ur[r]]+=1
        P=M/M.sum(); pv=P.sum(axis=1,keepdims=True); pr=P.sum(axis=0,keepdims=True); D=pv@pr; nz=P>0
        mi=float(np.sum(P[nz]*np.log(P[nz]/D[nz]))); hv=float(-np.sum(pv[pv>0]*np.log(pv[pv>0]))); hr=float(-np.sum(pr[pr>0]*np.log(pr[pr>0])))
        nmi=0.0 if min(hv,hr)<=1e-12 else float(mi/min(hv,hr))
        out[str(g)]={"n_emissions":len(vals),"variant_root_nmi":nmi,"variants":len(uv),"genetic_roots":len(ur)}
    return {"by_generation":out}
