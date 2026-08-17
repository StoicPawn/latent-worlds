import argparse, json
from latent_worlds.campaign import strict_screen, matched_followup

p=argparse.ArgumentParser()
p.add_argument('--seeds', type=int, default=8)
p.add_argument('--screen-steps', type=int, default=800)
p.add_argument('--follow-steps', type=int, default=1600)
p.add_argument('--epoch', type=int, default=100)
p.add_argument('--info', default='0.35,1.0,1.65')
p.add_argument('--signal-cost', type=float, default=0.03)
a=p.parse_args()
infos=[float(x) for x in a.info.split(',') if x]
rows=strict_screen(infos, range(a.seeds), signal_cost=a.signal_cost,
                   steps=a.screen_steps, epoch=a.epoch)
candidates=[r for r in rows if r['bursts']]
follow=[matched_followup(r['information_level'], r['seed'], signal_cost=a.signal_cost,
                         steps=a.follow_steps, epoch=a.epoch) for r in candidates]
print(json.dumps({'screen': rows, 'candidate_count': len(candidates), 'followup': follow}, indent=2))
