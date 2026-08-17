"""v2.9 carrier-agnostic falsification scan.

Audits the two already-existing non-genetic carriers (transient broadcasts and
persistent marks) without adding agent capabilities. Reports genetic-conditioned
categorical inheritance, cluster-free continuous dependence, and a temporal
directionality control (received payload must predict later output better than
prior output).
"""
import argparse, json
from latent_worlds.phase_map import long_horizon_config
from latent_worlds.generational_search import turnover_profile
from latent_worlds.world import World
from latent_worlds.secondary_evolution import (
    conditional_genetic_inheritance_assay,
    continuous_conditional_inheritance_assay,
    directional_continuous_transmission_assay,
)
from latent_worlds.persistent_inheritance import persistent_secondary_evolution_assay

p=argparse.ArgumentParser(); p.add_argument('--world-seed',type=int,default=11); p.add_argument('--agent-seed',type=int,default=0); p.add_argument('--steps',type=int,default=500); p.add_argument('--size',type=float,default=30.0)
a=p.parse_args()
cfg=long_horizon_config(information_level=.35,signal_cost=.03,communication_enabled=True,agent_seed=a.agent_seed)
for k,v in turnover_profile().items(): setattr(cfg,k,v)
cfg.width=cfg.height=float(a.size)
w=World(cfg,seed=a.world_seed).run(a.steps)
out={
 'world_seed':a.world_seed,'agent_seed':a.agent_seed,'steps':w.time,'size':a.size,
 'max_generation':max((x.generation for x in w.agents),default=0),
 'broadcast_categorical':conditional_genetic_inheritance_assay(w,permutations=99,min_pairs=12,min_generation=2),
 'broadcast_continuous':continuous_conditional_inheritance_assay(w,carrier='broadcast',permutations=99,min_pairs=20,min_generation=1),
 'broadcast_directional':directional_continuous_transmission_assay(w,carrier='broadcast',permutations=99,min_pairs=30,min_generation=1),
 'persistent_marks':persistent_secondary_evolution_assay(w,permutations=99,min_generation=1),
 'mark_continuous':continuous_conditional_inheritance_assay(w,carrier='mark',permutations=99,min_pairs=20,min_generation=1),
 'mark_directional':directional_continuous_transmission_assay(w,carrier='mark',permutations=99,min_pairs=30,min_generation=1),
}
print(json.dumps(out,indent=2))
