import argparse,json
from latent_worlds.semantic_autopsy import causal_codebook_assay
p=argparse.ArgumentParser()
p.add_argument('--world-seed',type=int,default=1); p.add_argument('--agent-seed',type=int,default=1)
p.add_argument('--information-level',type=float,default=.35); p.add_argument('--signal-cost',type=float,default=.03)
p.add_argument('--steps',type=int,default=1200); p.add_argument('--scramble',action='store_true')
a=p.parse_args()
print(json.dumps(causal_codebook_assay(a.world_seed,a.agent_seed,information_level=a.information_level,signal_cost=a.signal_cost,steps=a.steps,communication_scramble=a.scramble),indent=2))
