import argparse, json
from latent_worlds.phase_map import phase_grid, causal_information_contrast

p=argparse.ArgumentParser()
p.add_argument('--seeds', type=int, default=4)
p.add_argument('--steps', type=int, default=1200)
p.add_argument('--epoch', type=int, default=100)
p.add_argument('--info', default='0.35,1.0,1.65')
p.add_argument('--costs', default='0.03,0.055,0.09')
p.add_argument('--causal-top', type=int, default=2)
a=p.parse_args()
infos=[float(x) for x in a.info.split(',') if x]
costs=[float(x) for x in a.costs.split(',') if x]
seeds=list(range(a.seeds))
out=phase_grid(infos,costs,seeds,steps=a.steps,epoch=a.epoch)
causal=[]
for cell in out['ranked'][:a.causal_top]:
    candidate_seeds=[r['seed'] for r in cell['rows'] if r['signal_candidates']>0]
    if not candidate_seeds:
        candidate_seeds=seeds[:1]
    for s in candidate_seeds[:2]:
        causal.append(causal_information_contrast(s, information_level=cell['information_level'],
                                                  signal_cost=cell['signal_cost'], steps=a.steps))
out['causal_followups']=causal
print(json.dumps(out, indent=2))
