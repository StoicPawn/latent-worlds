"""Observer-only tests for emergence.

Nothing in this module is imported by agent controllers.  It exists to make it
harder for us to fool ourselves: interesting-looking structure must beat null
models and causal controls before it is labelled evidence of emergence.
"""
from __future__ import annotations

from dataclasses import asdict, replace
import math
import numpy as np

from .config import SimulationConfig
from .metrics import snapshot
from .world import World


def _safe(x):
    return float(x) if x is not None and np.isfinite(x) else 0.0


def run_condition(seed: int, steps: int, *, communication=True, manipulation=True,
                  private_information=True, generic_only=True) -> dict:
    cfg = SimulationConfig(
        communication_enabled=communication,
        object_manipulation_enabled=manipulation,
        occlusion_enabled=private_information,
        obstacle_count=18 if private_information else 0,
        pulse_spawn_rate=0.018 if private_information else 0.0,
        generic_population_only=generic_only,
    )
    w = World(cfg, seed=seed).run(steps)
    r = snapshot(w)
    return r


def factorial_emergence(seed: int, steps: int = 800) -> dict:
    """Paired 2x2 causal test for communication under private information.

    Difference-in-differences asks whether readable communication becomes more
    useful specifically when the world distributes information unevenly.
    """
    a = run_condition(seed, steps, communication=True, private_information=True)
    b = run_condition(seed, steps, communication=False, private_information=True)
    c = run_condition(seed, steps, communication=True, private_information=False)
    d = run_condition(seed, steps, communication=False, private_information=False)

    def fitness(r):
        # Observer summary only; agents never optimize this composite.
        return r['total_harvest'] + 2.0*r['births'] + 0.25*r['population']

    did = (fitness(a)-fitness(b)) - (fitness(c)-fitness(d))
    comm = a['communication']
    evidence = {
        'encoding': _safe(comm.get('broadcast_environment_r2')),
        'uptake_action': _safe(comm.get('receiver_action_r2_from_payload')),
        'uptake_motion': _safe(comm.get('receiver_motion_r2_from_payload')),
        'generational_span': int(comm.get('signal_generational_span') or 0),
        'private_information_index': _safe(a['information_structure'].get('private_information_index')),
        'causal_difference_in_differences': float(did),
    }
    # Deliberately conservative: no single correlational statistic can trigger it.
    evidence['candidate_protocol'] = bool(
        evidence['encoding'] > 0.10 and
        max(evidence['uptake_action'], evidence['uptake_motion']) > 0.05 and
        evidence['generational_span'] >= 1 and
        evidence['causal_difference_in_differences'] > 0
    )
    return {'seed': seed, 'A': a, 'B': b, 'C': c, 'D': d, 'evidence': evidence}


def technology_control(seed: int, steps: int = 800) -> dict:
    free = run_condition(seed, steps, manipulation=True)
    frozen = run_condition(seed, steps, manipulation=False)
    tf, tc = free['technology'], frozen['technology']
    delta = free['total_harvest'] - frozen['total_harvest']
    return {
        'seed': seed,
        'harvest_delta_free_minus_frozen': float(delta),
        'configuration_gain': _safe(tf.get('configuration_gain_vs_initial')),
        'successful_drops': int(tf.get('successful_drops') or 0),
        'available_affordance': _safe(tf.get('ground_truth_pair_affordance_max')),
        'candidate_technology': bool(
            delta > 0 and _safe(tf.get('configuration_gain_vs_initial')) > 0.02 and
            int(tf.get('successful_drops') or 0) > 0
        ),
    }


def batch(seeds, steps=800):
    language=[]; tech=[]
    for seed in seeds:
        language.append(factorial_emergence(int(seed), steps))
        tech.append(technology_control(int(seed), steps))
    ev=[x['evidence'] for x in language]
    return {
        'worlds': len(language),
        'steps': steps,
        'language_candidates': sum(e['candidate_protocol'] for e in ev),
        'technology_candidates': sum(t['candidate_technology'] for t in tech),
        'mean_private_information': float(np.mean([e['private_information_index'] for e in ev])) if ev else 0.0,
        'mean_communication_DiD': float(np.mean([e['causal_difference_in_differences'] for e in ev])) if ev else 0.0,
        'mean_technology_harvest_delta': float(np.mean([t['harvest_delta_free_minus_frozen'] for t in tech])) if tech else 0.0,
        'language': language,
        'technology': tech,
    }
