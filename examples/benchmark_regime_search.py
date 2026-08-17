#!/usr/bin/env python3
"""Find rare longitudinal regimes without modifying agent objectives."""
import argparse, json
from latent_worlds.longitudinal import scan

p=argparse.ArgumentParser()
p.add_argument('--worlds',type=int,default=12)
p.add_argument('--steps',type=int,default=1200)
p.add_argument('--epoch',type=int,default=100)
p.add_argument('--seed-start',type=int,default=0)
p.add_argument('--json',action='store_true')
a=p.parse_args()
r=scan(range(a.seed_start,a.seed_start+a.worlds),steps=a.steps,epoch=a.epoch)
rows=[]
for x in r['runs']:
    sig=[c for c in x['transition_candidates'] if 'cross_generation_signalling' in c['persistent_channels']]
    rows.append({
        'seed':x['seed'],'completed_steps':x['completed_steps'],'extinct':x['extinct'],
        'final_population':x['final']['snapshot']['population'],
        'max_generation':x['final']['snapshot']['max_generation'],
        'max_novelty':x['max_novelty_score'],'communication_candidates':sig,
        'all_candidates':x['transition_candidates'],
    })
out={'worlds':len(rows),'communication_candidate_worlds':sum(bool(x['communication_candidates']) for x in rows),'rows':rows}
if a.json: print(json.dumps(out,indent=2))
else:
    print('worlds',out['worlds'])
    print('communication_candidate_worlds',out['communication_candidate_worlds'])
    for x in rows:
        print(f"seed={x['seed']} pop={x['final_population']} gen={x['max_generation']} maxnov={x['max_novelty']:.3f} comm_candidates={x['communication_candidates']}")
