"""Direct observer-side causal assay for reception -> transmission.

The assay changes no agent objective or world dynamics.  At naturally occurring
reception events, it asks a counterfactual question about the *same receiver at
the same instant*: what would this receiver output if the transient social signal
were removed, while every other observation and the RNG state were held fixed?

For events where the receiver naturally broadcasts, this gives a direct causal
estimate of whether received content changes outgoing content.  Because the
comparison is within-agent and within-instant, genetic lineage, environmental
state and slow neural-state autocorrelation are exactly matched.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from dataclasses import replace
import numpy as np

from .phase_map import long_horizon_config
from .semantic_autopsy import _apply_config_overrides, _counterfactual_act_inplace
from .world import World
from .agents import ActionKind


@dataclass
class GenerationCausalTransmission:
    generation: int
    receptions: int
    natural_broadcasts: int
    cf_broadcasts_without_signal: int
    action_changed_without_signal: int
    payload_effect_events: int
    mean_payload_effect: float | None
    median_payload_effect: float | None
    mean_copy_gain: float | None
    copy_gain_positive_fraction: float | None
    permutation_p: float


def _mean_signal_payload(obs) -> np.ndarray | None:
    if not obs.nearby_signals:
        return None
    return np.mean(np.asarray([q[2] for q in obs.nearby_signals], dtype=float), axis=0)


def _payload(action) -> np.ndarray | None:
    if action.kind != ActionKind.BROADCAST or not action.payload:
        return None
    return np.asarray(action.payload, dtype=float)


def _summarize_generation(rows: list[dict], generation: int, *, permutations: int, rng) -> GenerationCausalTransmission:
    receptions=len(rows)
    natural=[r for r in rows if r["real_kind"] == "broadcast"]
    natural_broadcasts=len(natural)
    cf_bcasts=sum(r["nosig_kind"] == "broadcast" for r in natural)
    action_changed=sum(r["real_kind"] != r["nosig_kind"] for r in rows)
    eff=[r["payload_effect"] for r in natural if r["payload_effect"] is not None]
    gains=[r["copy_gain"] for r in natural if r["copy_gain"] is not None]
    if len(gains) >= 12:
        # Within-event null: preserve the receiver's real/no-signal outputs but
        # randomly reassign which received payload each event is paired with.
        real=np.asarray([r["real_payload"] for r in natural if r["copy_gain"] is not None],float)
        no=np.asarray([r["nosig_payload"] for r in natural if r["copy_gain"] is not None],float)
        x=np.asarray([r["received_payload"] for r in natural if r["copy_gain"] is not None],float)
        obs=float(np.mean(np.linalg.norm(no-x,axis=1)-np.linalg.norm(real-x,axis=1)))
        null=[]
        for _ in range(int(permutations)):
            xp=x[rng.permutation(len(x))]
            null.append(float(np.mean(np.linalg.norm(no-xp,axis=1)-np.linalg.norm(real-xp,axis=1))))
        null=np.asarray(null,float)
        p=float((1+np.sum(null>=obs))/(1+len(null)))
    else:
        p=1.0
    return GenerationCausalTransmission(
        generation=int(generation), receptions=int(receptions), natural_broadcasts=int(natural_broadcasts),
        cf_broadcasts_without_signal=int(cf_bcasts), action_changed_without_signal=int(action_changed),
        payload_effect_events=len(eff), mean_payload_effect=None if not eff else float(np.mean(eff)),
        median_payload_effect=None if not eff else float(np.median(eff)),
        mean_copy_gain=None if not gains else float(np.mean(gains)),
        copy_gain_positive_fraction=None if not gains else float(np.mean(np.asarray(gains)>0)),
        permutation_p=p,
    )


def direct_reception_transmission_assay(
    world_seed: int,
    agent_seed: int,
    *,
    information_level: float = 0.35,
    signal_cost: float = 0.03,
    steps: int = 800,
    assay_start: int = 50,
    assay_end: int | None = None,
    max_events: int = 3000,
    min_generation: int = 0,
    communication_scramble: bool = False,
    config_overrides: dict | None = None,
    permutations: int = 199,
    seed: int = 0,
) -> dict:
    """Causal within-instant reception->outgoing-signal assay.

    ``copy_gain`` is positive when the naturally emitted payload is closer to the
    actually received payload than the payload the *same agent* would emit if the
    received social signal were removed.  Positive copy gain therefore measures a
    causal pull of received content on outgoing content, not mere similarity.
    """
    cfg=long_horizon_config(information_level=information_level, signal_cost=signal_cost,
                            communication_enabled=True, agent_seed=int(agent_seed))
    cfg=_apply_config_overrides(cfg, config_overrides)
    cfg.communication_scramble=bool(communication_scramble)
    w=World(cfg,seed=int(world_seed))
    end=int(steps if assay_end is None else min(steps,assay_end))
    rows=[]
    tested=0
    for _ in range(int(steps)):
        if assay_start <= w.time < end and tested < max_events:
            for a in [q for q in w.agents if q.alive and getattr(q,"kind","")=="recurrent"]:
                if tested>=max_events: break
                if int(a.generation) < int(min_generation):
                    continue
                obs=w.observe(a)
                x=_mean_signal_payload(obs)
                if x is None: continue
                noobs=replace(obs,nearby_signals=[])
                real=_counterfactual_act_inplace(a,obs,w.agent_rng)
                nosig=_counterfactual_act_inplace(a,noobs,w.agent_rng)
                rp=_payload(real); npay=_payload(nosig)
                effect=None; gain=None
                if rp is not None and npay is not None:
                    effect=float(np.linalg.norm(rp-npay))
                    gain=float(np.linalg.norm(npay-x)-np.linalg.norm(rp-x))
                rows.append({
                    "time":int(w.time),"agent_id":int(a.id),"generation":int(a.generation),
                    "received_payload":x.tolist(),"real_kind":real.kind.value,"nosig_kind":nosig.kind.value,
                    "real_payload":None if rp is None else rp.tolist(),"nosig_payload":None if npay is None else npay.tolist(),
                    "payload_effect":effect,"copy_gain":gain,
                })
                tested+=1
        if not any(a.alive for a in w.agents): break
        w.step()
    bygen={}
    rng=np.random.default_rng(int(seed)+int(world_seed)*1009+int(agent_seed)*9176+(991 if communication_scramble else 0))
    for g in sorted({r["generation"] for r in rows}):
        bygen[str(g)]=asdict(_summarize_generation([r for r in rows if r["generation"]==g],g,permutations=permutations,rng=rng))
    deep=[]
    for gs,d in bygen.items():
        if int(gs)>=1 and d["natural_broadcasts"]>=12 and d["mean_copy_gain"] is not None and d["mean_copy_gain"]>0 and d["permutation_p"]<=0.05:
            deep.append(int(gs))
    return {
        "world_seed":int(world_seed),"agent_seed":int(agent_seed),"steps":int(steps),"min_generation":int(min_generation),
        "communication_scramble":bool(communication_scramble),"events":len(rows),"by_generation":bygen,
        "supported_generations":deep,"supported":bool(deep),
        "criterion":"same-agent same-instant received content causally pulls outgoing payload toward received payload",
    }


def counterfactual_payload_transplant_assay(
    world_seed: int,
    agent_seed: int,
    *,
    steps: int = 800,
    assay_start: int = 100,
    min_generation: int = 1,
    max_events: int = 500,
    information_level: float = 0.35,
    signal_cost: float = 0.03,
    communication_scramble: bool = False,
    config_overrides: dict | None = None,
    permutations: int = 199,
    seed: int = 0,
) -> dict:
    """Inject donor signal content into the same receiver at the same instant.

    For naturally broadcasting receivers, replace every received payload by a
    payload sampled from another real reception event.  ``steering_gain`` is
    positive when the counterfactual emitted payload moves closer to the injected
    donor content than the natural emitted payload was.  This is a direct causal
    content-steering test, with agent, world state and RNG fixed.
    """
    cfg=long_horizon_config(information_level=information_level, signal_cost=signal_cost,
                            communication_enabled=True, agent_seed=int(agent_seed))
    cfg=_apply_config_overrides(cfg,config_overrides)
    cfg.communication_scramble=bool(communication_scramble)
    # First collect a donor pool from the same realized history.
    ref=World(cfg,seed=int(world_seed)).run(int(steps))
    donor=[]
    for r in ref.social_log:
        if int(r.get('generation',0)) < int(min_generation): continue
        if int(r.get('received_count',0))>0 and r.get('mean_payload'):
            donor.append(np.asarray(r['mean_payload'],float))
    if len(donor)<12:
        return {'events':0,'supported':False,'reason':'insufficient_donor_payloads'}
    donor=np.asarray(donor,float)

    w=World(cfg,seed=int(world_seed)); rng=np.random.default_rng(int(seed)+world_seed*1117+agent_seed*2017)
    rows=[]
    for _ in range(int(steps)):
        if w.time>=assay_start and len(rows)<max_events:
            for a in [q for q in w.agents if q.alive and getattr(q,'kind','')=='recurrent' and int(q.generation)>=int(min_generation)]:
                if len(rows)>=max_events: break
                obs=w.observe(a); x=_mean_signal_payload(obs)
                if x is None: continue
                real=_counterfactual_act_inplace(a,obs,w.agent_rng); rp=_payload(real)
                if rp is None: continue
                # Pick a donor deliberately separated from the observed payload
                # when possible, but from the empirical payload distribution.
                dists=np.linalg.norm(donor-x[None,:],axis=1)
                candidates=np.flatnonzero(dists>=np.quantile(dists,0.65))
                j=int(rng.choice(candidates if len(candidates) else np.arange(len(donor))))
                y=donor[j]
                ytuple=tuple(float(v) for v in y)
                cfobs=replace(obs,nearby_signals=[(dx,dy,ytuple) for dx,dy,_ in obs.nearby_signals])
                cf=_counterfactual_act_inplace(a,cfobs,w.agent_rng); cp=_payload(cf)
                if cp is None: continue
                gain=float(np.linalg.norm(rp-y)-np.linalg.norm(cp-y))
                rows.append({'generation':int(a.generation),'gain':gain,'real':rp,'cf':cp,'donor':y})
        if not any(a.alive for a in w.agents): break
        w.step()
    bygen={}
    for g in sorted({r['generation'] for r in rows}):
        vals=[r for r in rows if r['generation']==g]; gains=np.asarray([r['gain'] for r in vals],float)
        if len(vals)>=12:
            # Null donor reassignment, preserving natural/counterfactual outputs.
            R=np.asarray([r['real'] for r in vals],float); C=np.asarray([r['cf'] for r in vals],float); D=np.asarray([r['donor'] for r in vals],float)
            obs=float(np.mean(gains)); null=[]
            for _ in range(int(permutations)):
                dp=D[rng.permutation(len(D))]
                null.append(float(np.mean(np.linalg.norm(R-dp,axis=1)-np.linalg.norm(C-dp,axis=1))))
            null=np.asarray(null,float); p=float((1+np.sum(null>=obs))/(1+len(null)))
        else: p=1.0
        bygen[str(g)]={'events':len(vals),'mean_steering_gain':None if not len(vals) else float(np.mean(gains)),
                      'positive_fraction':None if not len(vals) else float(np.mean(gains>0)),'permutation_p':p,
                      'supported':bool(len(vals)>=12 and float(np.mean(gains))>0 and p<=.05)}
    supported=[int(g) for g,d in bygen.items() if d['supported']]
    return {'world_seed':int(world_seed),'agent_seed':int(agent_seed),'communication_scramble':bool(communication_scramble),
            'events':len(rows),'by_generation':bygen,'supported_generations':supported,'supported':bool(supported)}


def causal_variant_reproduction_assay(
    world_seed: int,
    agent_seed: int,
    *,
    steps: int = 600,
    assay_start: int = 150,
    min_generation: int = 2,
    max_events: int = 250,
    information_level: float = .35,
    signal_cost: float = .03,
    communication_scramble: bool = False,
    config_overrides: dict | None = None,
    min_cluster_rows: int = 40,
) -> dict:
    """Matched-receiver causal reproduction rates for emergent signal variants.

    Every naturally receiving agent/context is exposed counterfactually to every
    naturally discovered signal centroid.  A variant 'reproduces' on an event when
    the receiver broadcasts and its outgoing payload is classified back into the
    injected variant.  All variants are therefore evaluated on the exact same
    receiver/context set, removing genetic and ecological composition confounds.
    """
    from .semantic_autopsy import discover_signal_clusters, _nearest_center
    cfg=long_horizon_config(information_level=information_level, signal_cost=signal_cost,
                            communication_enabled=True, agent_seed=int(agent_seed))
    cfg=_apply_config_overrides(cfg,config_overrides); cfg.communication_scramble=bool(communication_scramble)
    ref=World(cfg,seed=int(world_seed)).run(int(steps)); clusters=discover_signal_clusters(ref,min_rows=min_cluster_rows,max_k=5)
    centers=clusters.get('centers',[])
    if len(centers)<2: return {'supported':False,'events':0,'clusters':clusters,'reason':'insufficient_variants'}
    w=World(cfg,seed=int(world_seed)); k=len(centers); M=np.zeros((k,k),int); exposures=np.zeros(k,int); events=0
    for _ in range(int(steps)):
        if w.time>=assay_start and events<max_events:
            for a in [q for q in w.agents if q.alive and getattr(q,'kind','')=='recurrent' and int(q.generation)>=int(min_generation)]:
                if events>=max_events: break
                obs=w.observe(a)
                if not obs.nearby_signals: continue
                events+=1
                for i,c in enumerate(centers):
                    payload=tuple(float(v) for v in c); cfobs=replace(obs,nearby_signals=[(dx,dy,payload) for dx,dy,_ in obs.nearby_signals])
                    act=_counterfactual_act_inplace(a,cfobs,w.agent_rng); exposures[i]+=1
                    op=_payload(act)
                    if op is not None:
                        j=_nearest_center(op,centers); M[i,j]+=1
        if not any(a.alive for a in w.agents): break
        w.step()
    rows=[]
    for i in range(k):
        same=int(M[i,i]); exp=int(exposures[i]); bcasts=int(M[i].sum())
        rows.append({'variant':i,'exposures':exp,'broadcasts':bcasts,'same_variant_offspring':same,
                     'reproduction_rate':None if exp==0 else float(same/exp),
                     'broadcast_rate':None if exp==0 else float(bcasts/exp)})
    rates=np.asarray([r['reproduction_rate'] for r in rows if r['reproduction_rate'] is not None],float)
    spread=float(np.max(rates)-np.min(rates)) if len(rates)>=2 else 0.0
    cv=float(np.std(rates)/max(np.mean(rates),1e-12)) if len(rates)>=2 else 0.0
    # Matched contexts make any nontrivial spread causal with respect to injected content;
    # a conservative magnitude threshold prevents calling tiny numerical differences selection.
    supported=bool(events>=20 and len(rates)>=2 and spread>=.08 and cv>=.20)
    return {'world_seed':int(world_seed),'agent_seed':int(agent_seed),'communication_scramble':bool(communication_scramble),
            'events':int(events),'clusters':clusters,'matrix':M.tolist(),'variants':rows,'reproduction_spread':spread,
            'reproduction_cv':cv,'differential_reproduction':supported,'supported':supported}


def direct_secondary_evolution_assay(world_seed:int, agent_seed:int, *, steps:int=600,
                                     min_generation:int=2, assay_start:int=180,
                                     config_overrides:dict|None=None, permutations:int=99) -> dict:
    """Strict direct-causal candidate assay for a secondary inheritance process.

    This combines three within-agent/context tests: removal, content transplant and
    matched-context differential variant reproduction.  It deliberately does not
    call a candidate replicated; replication across independent histories remains
    an external requirement.
    """
    real_copy=direct_reception_transmission_assay(world_seed,agent_seed,steps=steps,assay_start=assay_start,
        min_generation=min_generation,max_events=700,config_overrides=config_overrides,permutations=permutations)
    real_trans=counterfactual_payload_transplant_assay(world_seed,agent_seed,steps=steps,assay_start=assay_start,
        min_generation=min_generation,max_events=300,config_overrides=config_overrides,permutations=permutations)
    real_sel=causal_variant_reproduction_assay(world_seed,agent_seed,steps=steps,assay_start=assay_start,
        min_generation=min_generation,max_events=180,config_overrides=config_overrides)
    scr_copy=direct_reception_transmission_assay(world_seed,agent_seed,steps=steps,assay_start=assay_start,
        min_generation=min_generation,max_events=700,communication_scramble=True,config_overrides=config_overrides,permutations=permutations)
    scr_sel=causal_variant_reproduction_assay(world_seed,agent_seed,steps=steps,assay_start=assay_start,
        min_generation=min_generation,max_events=180,communication_scramble=True,config_overrides=config_overrides)
    qualifying=sorted(set(real_copy.get('supported_generations',[])) & set(real_trans.get('supported_generations',[])))
    supported=bool(qualifying and real_sel.get('supported') and not scr_copy.get('supported') and not scr_sel.get('supported'))
    return {'world_seed':int(world_seed),'agent_seed':int(agent_seed),'min_generation':int(min_generation),
            'supported_generations':qualifying,'supported':supported,
            'real':{'copy':real_copy,'transplant':real_trans,'differential_reproduction':real_sel},
            'scrambled':{'copy':scr_copy,'differential_reproduction':scr_sel},
            'replication_status':'unreplicated_single-history candidate' if supported else 'not supported'}
