#!/usr/bin/env python3
import argparse, json
from latent_worlds.longitudinal import scan

p = argparse.ArgumentParser(description="Long-horizon observer-only emergence scan")
p.add_argument("--worlds", type=int, default=12)
p.add_argument("--steps", type=int, default=5000)
p.add_argument("--epoch", type=int, default=100)
p.add_argument("--seed-start", type=int, default=0)
p.add_argument("--json", action="store_true")
a = p.parse_args()
r = scan(range(a.seed_start, a.seed_start+a.worlds), steps=a.steps, epoch=a.epoch)
if a.json:
    print(json.dumps(r, indent=2))
else:
    print("worlds", r["worlds"])
    print("steps", r["steps"])
    print("extinctions", r["extinctions"])
    print("runs_with_transition_candidates", r["runs_with_transition_candidates"])
    print("candidate_count", r["candidate_count"])
    print("max_novelty", round(r["max_novelty"], 3))
    for x in r["runs"]:
        cs = x["transition_candidates"]
        print(f"seed={x['seed']} t={x['completed_steps']} extinct={x['extinct']} max_novelty={x['max_novelty_score']:.3f} candidates={cs}")
