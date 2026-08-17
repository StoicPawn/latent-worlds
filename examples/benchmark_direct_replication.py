import argparse, json
from latent_worlds.replication import direct_replication_followup, standard_turnover_overrides

p=argparse.ArgumentParser()
p.add_argument('--world',type=int,required=True)
p.add_argument('--agents',type=int,required=True)
p.add_argument('--steps',type=int,default=800)
p.add_argument('--assay-start',type=int,default=500)
p.add_argument('--min-generation',type=int,default=2)
a=p.parse_args()
r=direct_replication_followup(a.world,a.agents,steps=a.steps,assay_start=a.assay_start,
                              min_generation=a.min_generation,
                              overrides=standard_turnover_overrides())
print(json.dumps(r,indent=2))
