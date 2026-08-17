import argparse, json
from latent_worlds.semantic_autopsy import candidate_semantic_autopsy

p=argparse.ArgumentParser()
p.add_argument('--world-seed',type=int,default=1)
p.add_argument('--agent-seed',type=int,default=1)
p.add_argument('--information-level',type=float,default=0.35)
p.add_argument('--signal-cost',type=float,default=0.03)
p.add_argument('--steps',type=int,default=1200)
a=p.parse_args()
print(json.dumps(candidate_semantic_autopsy(a.world_seed,a.agent_seed,information_level=a.information_level,
                                             signal_cost=a.signal_cost,steps=a.steps),indent=2))
