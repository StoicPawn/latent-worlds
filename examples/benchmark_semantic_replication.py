import argparse,json
from latent_worlds.semantic_autopsy import counterfactual_content_assay
p=argparse.ArgumentParser(); p.add_argument('--steps',type=int,default=900)
a=p.parse_args()
pairs=[(0,1),(1,1),(1,3)]
rows=[]
for w,s in pairs:
    real=counterfactual_content_assay(w,s,steps=a.steps,max_events=800,communication_scramble=False)
    scr=counterfactual_content_assay(w,s,steps=a.steps,max_events=800,communication_scramble=True)
    rows.append({'world_seed':w,'agent_seed':s,
                 'real_amplification':real.get('intergenerational_amplification'),
                 'scrambled_amplification':scr.get('intergenerational_amplification'),
                 'amplification_difference':None if real.get('intergenerational_amplification') is None or scr.get('intergenerational_amplification') is None else real['intergenerational_amplification']-scr['intergenerational_amplification'],
                 'real_p':real.get('paired_sign_p'),'scrambled_p':scr.get('paired_sign_p')})
print(json.dumps({'steps':a.steps,'rows':rows},indent=2))
