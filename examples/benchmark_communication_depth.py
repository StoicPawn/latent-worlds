#!/usr/bin/env python3
import argparse, json, itertools, concurrent.futures
from latent_worlds.generational_search import communication_depth_probe

PROFILES={
 'base':{},
 'turnover':{'reproduction_threshold':15.0,'reproduction_cost':6.0,'resource_regrowth':0.07},
}

def one(x):
    w,a,p,steps,me,mr=x
    r=communication_depth_probe(w,a,steps=steps,overrides=PROFILES[p],min_emissions=me,min_receptions=mr)
    r['profile']=p
    r['passes_deep_communication']=bool(r['population']>=8 and r['late_generation_communication'])
    return r

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--worlds',type=int,default=5); ap.add_argument('--agents',type=int,default=5)
    ap.add_argument('--steps',type=int,default=600); ap.add_argument('--workers',type=int,default=8)
    ap.add_argument('--min-emissions',type=int,default=8); ap.add_argument('--min-receptions',type=int,default=20)
    args=ap.parse_args()
    jobs=[(w,a,p,args.steps,args.min_emissions,args.min_receptions) for w,a,p in itertools.product(range(args.worlds),range(args.agents),PROFILES)]
    with concurrent.futures.ProcessPoolExecutor(max_workers=args.workers) as ex: rows=list(ex.map(one,jobs))
    out={'jobs':len(rows),'deep_communication_candidates':sum(r['passes_deep_communication'] for r in rows),'rows':rows}
    print(json.dumps(out,indent=2))
