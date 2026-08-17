"""Observer-side staged search for adaptive replication candidates.

No agent or world dynamics are modified. The purpose of this module is purely
computational and methodological: reject non-specific late-generation signal
phenomena before paying for expensive fitness and persistence controls.
"""
from __future__ import annotations

from .replication import screen_for_late_replication, standard_turnover_overrides
from .causal_transmission import (
    direct_reception_transmission_assay,
    counterfactual_payload_transplant_assay,
    causal_variant_reproduction_assay,
)


def staged_mechanistic_screen(world_seed:int, agent_seed:int=0, *, steps:int=800,
                              assay_start:int=450, min_generation:int=2,
                              overrides:dict|None=None, permutations:int=99) -> dict:
    """Pre-registered staged screen for content-specific causal replication.

    Stages are intentionally ordered from cheap to expensive:
    communicative depth -> removal -> transplant -> differential reproduction ->
    scrambled removal.  Fitness is deliberately *not* evaluated here.
    """
    ov=dict(overrides or standard_turnover_overrides())
    depth=screen_for_late_replication(world_seed,agent_seed,steps=steps,
                                      overrides=ov,min_emissions=8,min_receptions=20)
    if not depth.get('late_generation_communication'):
        return {'world_seed':world_seed,'agent_seed':agent_seed,'stage':'depth',
                'mechanistic_candidate':False,'depth':depth}
    common=dict(world_seed=world_seed,agent_seed=agent_seed,steps=steps,
                assay_start=assay_start,min_generation=min_generation,
                config_overrides=ov)
    removal=direct_reception_transmission_assay(max_events=500,permutations=permutations,**common)
    if not removal.get('supported'):
        return {'world_seed':world_seed,'agent_seed':agent_seed,'stage':'removal',
                'mechanistic_candidate':False,'depth':depth,'removal':removal}
    transplant=counterfactual_payload_transplant_assay(max_events=250,permutations=permutations,**common)
    if not transplant.get('supported'):
        return {'world_seed':world_seed,'agent_seed':agent_seed,'stage':'transplant',
                'mechanistic_candidate':False,'depth':depth,'removal':removal,'transplant':transplant}
    selection=causal_variant_reproduction_assay(max_events=150,**common)
    if not selection.get('supported'):
        return {'world_seed':world_seed,'agent_seed':agent_seed,'stage':'selection',
                'mechanistic_candidate':False,'depth':depth,'removal':removal,
                'transplant':transplant,'selection':selection}
    scrambled=direct_reception_transmission_assay(max_events=500,permutations=permutations,
                                                   communication_scramble=True,**common)
    specific=not scrambled.get('supported')
    return {'world_seed':world_seed,'agent_seed':agent_seed,
            'stage':'passed' if specific else 'scrambled_specificity',
            'mechanistic_candidate':bool(specific),'depth':depth,'removal':removal,
            'transplant':transplant,'selection':selection,'scrambled_removal':scrambled}
