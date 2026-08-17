#!/usr/bin/env python
import argparse, json
from latent_worlds.emergence import batch

p=argparse.ArgumentParser(description='Minimal-substrate emergence audit')
p.add_argument('--worlds', type=int, default=12)
p.add_argument('--steps', type=int, default=800)
p.add_argument('--seed', type=int, default=0)
a=p.parse_args()
report=batch(range(a.seed, a.seed+a.worlds), a.steps)
summary={k:v for k,v in report.items() if k not in {'language','technology'}}
print(json.dumps(summary, indent=2))
