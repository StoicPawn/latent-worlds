import argparse, json
from latent_worlds.adaptive_persistence import adaptive_persistence_assay

p=argparse.ArgumentParser()
p.add_argument('--world',type=int,required=True)
p.add_argument('--agents',type=int,required=True)
p.add_argument('--horizons',type=int,nargs='+',default=[500,650,800])
a=p.parse_args()
print(json.dumps(adaptive_persistence_assay(a.world,a.agents,horizons=a.horizons),indent=2))
