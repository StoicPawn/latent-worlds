"""Strict v2.8 assay: can a non-genetic inheritance channel beat genetic-lineage controls?"""
import argparse, json
from latent_worlds.phase_map import long_horizon_config
from latent_worlds.generational_search import turnover_profile
from latent_worlds.world import World
from latent_worlds.secondary_evolution import autonomous_secondary_evolution_assay
from latent_worlds.metrics import snapshot
p=argparse.ArgumentParser(); p.add_argument('--world-seed',type=int,default=11); p.add_argument('--agent-seed',type=int,default=0); p.add_argument('--steps',type=int,default=700); p.add_argument('--scramble',action='store_true')
a=p.parse_args(); cfg=long_horizon_config(information_level=.35,signal_cost=.03,communication_enabled=True,agent_seed=a.agent_seed)
for k,v in turnover_profile().items(): setattr(cfg,k,v)
cfg.communication_scramble=bool(a.scramble); w=World(cfg,seed=a.world_seed).run(a.steps); s=snapshot(w)
r=autonomous_secondary_evolution_assay(w,permutations=199,min_pairs=12)
print(json.dumps({'world_seed':a.world_seed,'agent_seed':a.agent_seed,'steps':a.steps,'scramble':a.scramble,'population':s['population'],'max_generation':s['max_generation'],'births':w.births,'total_harvest':s['total_harvest'],'supported':r['supported'],'qualifying_generations':r['qualifying_generations'],'criteria':r['criteria'],'conditional_by_generation':r['genetic_conditioned_inheritance']['by_generation']},indent=2))
