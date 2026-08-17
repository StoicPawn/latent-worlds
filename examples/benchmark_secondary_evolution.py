import argparse, json
from latent_worlds.secondary_evolution import run_secondary_evolution_probe

p=argparse.ArgumentParser()
p.add_argument('--worlds',type=int,default=8); p.add_argument('--steps',type=int,default=900)
a=p.parse_args()
rows=[]
for seed in range(a.worlds):
    r=run_secondary_evolution_probe(seed,seed,steps=a.steps)
    rows.append(r)
    print(json.dumps({k:r.get(k) for k in ('world_seed','max_generation','population','supported','cross_lineage_adoptions','information_faster_than_genes')}))
print('candidates',sum(bool(r.get('supported')) for r in rows),'/',len(rows))
