#!/usr/bin/env python3
"""Search for functional dependence on emergent behavioural roles."""
import argparse, json
from latent_worlds.config import SimulationConfig
from latent_worlds.world import World
from latent_worlds.role_ablation import role_interdependence

p=argparse.ArgumentParser()
p.add_argument('--worlds',type=int,default=8)
p.add_argument('--checkpoint',type=int,default=900)
p.add_argument('--horizon',type=int,default=150)
p.add_argument('--controls',type=int,default=8)
p.add_argument('--seed-start',type=int,default=0)
p.add_argument('--json',action='store_true')
a=p.parse_args()
cfg=SimulationConfig(generic_population_only=True,initial_agents=36,resource_patches=84,
    resource_regrowth=0.062,basal_metabolism=0.034,initial_energy=20.0,
    reproduction_threshold=20.0,reproduction_cost=8.5,max_population=300)
rows=[]
for seed in range(a.seed_start,a.seed_start+a.worlds):
    w=World(cfg,seed=seed); w.run(a.checkpoint)
    r=role_interdependence(w,horizon=a.horizon,random_controls=a.controls)
    rows.append({'seed':seed,'population':sum(x.alive for x in w.agents),'births':w.births,
                 'max_generation':max((x.generation for x in w.agents),default=0),**r})
out={'worlds':len(rows),'worlds_with_candidate_roles':sum(bool(x['candidate_roles']) for x in rows),'rows':rows}
if a.json: print(json.dumps(out,indent=2))
else:
    print('worlds',out['worlds'],'candidate_worlds',out['worlds_with_candidate_roles'])
    for x in rows:
        print('seed',x['seed'],'pop',x['population'],'gen',x['max_generation'],'candidates',x['candidate_roles'])
        for role,v in x['roles'].items():
            print(' ',role,'n=',v['role_size'],'dep=',round(v['productivity_dependency'],6),'z=',round(v['productivity_z'],2))
