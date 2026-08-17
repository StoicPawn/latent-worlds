#!/usr/bin/env python3
import argparse, json, itertools, concurrent.futures
from latent_worlds.generational_search import genealogy_probe, semantic_transfer_probe

PROFILES={
 'base':{},
 'turnover':{'reproduction_threshold':15.0,'reproduction_cost':6.0,'resource_regrowth':0.07},
}

def one(x):
    w,a,p,steps=x
    r=genealogy_probe(w,a,steps=steps,overrides=PROFILES[p])
    r['profile']=p
    r['passes_genealogy']=bool(r['max_generation']>=2 and r['population']>=8)
    return r

if __name__=='__main__':
 p=argparse.ArgumentParser(); p.add_argument('--worlds',type=int,default=4); p.add_argument('--agents',type=int,default=4); p.add_argument('--steps',type=int,default=1000); p.add_argument('--workers',type=int,default=8); p.add_argument('--semantic-steps',type=int,default=700); p.add_argument('--no-semantic',action='store_true'); p.add_argument('--json',action='store_true'); args=p.parse_args()
 jobs=[(w,a,pr,args.steps) for w,a,pr in itertools.product(range(args.worlds),range(args.agents),PROFILES)]
 with concurrent.futures.ProcessPoolExecutor(max_workers=args.workers) as ex: rows=list(ex.map(one,jobs))
 candidates=[r for r in rows if r['passes_genealogy']]
 sem=[]
 for r in ([] if args.no_semantic else candidates[:8]):
   s=semantic_transfer_probe(r['world_seed'],r['agent_seed'],steps=args.semantic_steps,overrides=PROFILES[r['profile']],max_events=220,min_generation_events=20)
   sem.append({'world_seed':r['world_seed'],'agent_seed':r['agent_seed'],'profile':r['profile'],'max_generation':r['max_generation'],'population':r['population'],'semantic':s})
 out={'jobs':len(rows),'genealogy_candidates':len(candidates),'rows':rows,'semantic_followups':sem}
 print(json.dumps(out,indent=2) if args.json else out)
