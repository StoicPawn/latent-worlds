from __future__ import annotations

from collections import Counter, defaultdict
import numpy as np


def _truth_grid(world) -> tuple[np.ndarray, np.ndarray]:
    # Evaluator samples reachable spacetime states. Agents never see this grid.
    rows = []
    truth = []
    xs = np.linspace(0.0, world.config.width, 9)
    ys = np.linspace(0.0, world.config.height, 7)
    times = np.linspace(0, max(1, world.time + 180), 13, dtype=int)
    original_time = world.time
    try:
        for t in times:
            world.time = int(t)
            for x in xs:
                for y in ys:
                    temp, rad = world.physical_state(float(x), float(y))
                    rows.append((temp, rad))
                    truth.append(world.yield_law.efficiency(temp, rad))
    finally:
        world.time = original_time
    return np.asarray(rows, dtype=float), np.asarray(truth, dtype=float)


def _science_metrics(world) -> dict:
    scientists = [a for a in world.agents if hasattr(a, "science")]
    if not scientists:
        return {"scientists": 0, "mean_law_rmse": None, "best_law_rmse": None, "model_counts": {}}

    X, truth = _truth_grid(world)
    rmses = []
    names = Counter()
    temp_spans = []
    radiation_spans = []
    epistemic_actions = 0
    interaction_models = 0
    for a in scientists:
        rmse = a.science.prediction_rmse(X, truth)
        if rmse is not None:
            rmses.append(rmse)
        name = a.science.best_model_name()
        if name:
            names[name] += 1
            if name in {"quadratic_interaction", "rbf"}:
                interaction_models += 1
        spans = a.science.sampled_spans()
        if len(spans) >= 2:
            temp_spans.append(spans[0])
            radiation_spans.append(spans[1])
        epistemic_actions += getattr(a, "epistemic_actions", 0)
    return {
        "scientists": len(scientists),
        "mean_law_rmse": float(np.mean(rmses)) if rmses else None,
        "best_law_rmse": float(np.min(rmses)) if rmses else None,
        "mean_temperature_span": float(np.mean(temp_spans)) if temp_spans else 0.0,
        "mean_radiation_span": float(np.mean(radiation_spans)) if radiation_spans else 0.0,
        "epistemic_actions": epistemic_actions,
        "interaction_capable_fraction": interaction_models / max(len(scientists), 1),
        "model_counts": dict(names),
    }



def _cognition_metrics(world) -> dict:
    cognitive = [a for a in world.agents if getattr(a, "kind", "") in {"model_based", "planner", "recurrent"}]
    living = [a for a in cognitive if a.alive]
    if not cognitive:
        return {"cognitive_agents": 0, "living_cognitive": 0, "hidden_source_count": world.hidden_source_count}
    by_architecture = Counter(a.kind for a in living)
    return {
        "cognitive_agents": len(cognitive),
        "living_cognitive": len(living),
        "living_by_architecture": dict(by_architecture),
        "mean_memory_gene": float(np.mean([a.genome.memory for a in cognitive])),
        "mean_abstraction_gene": float(np.mean([a.genome.abstraction for a in cognitive])),
        "mean_social_attention_gene": float(np.mean([a.genome.social_attention for a in cognitive])),
        "mean_plasticity_gene": float(np.mean([a.genome.plasticity for a in cognitive])),
        "living_mean_memory_gene": float(np.mean([a.genome.memory for a in living])) if living else None,
        "living_mean_abstraction_gene": float(np.mean([a.genome.abstraction for a in living])) if living else None,
        "living_mean_social_attention_gene": float(np.mean([a.genome.social_attention for a in living])) if living else None,
        "living_mean_plasticity_gene": float(np.mean([a.genome.plasticity for a in living])) if living else None,
        "hidden_source_count": world.hidden_source_count,
    }

def snapshot(world) -> dict:
    living = [a for a in world.agents if a.alive]
    kinds = Counter(a.kind for a in living)
    born_by_kind = Counter(a.kind for a in world.agents)
    harvest_by_kind = defaultdict(float)
    ages_by_kind = defaultdict(list)
    for a in world.agents:
        harvest_by_kind[a.kind] += a.total_harvest
        ages_by_kind[a.kind].append(a.age)
    return {
        "time": world.time,
        "population": len(living),
        "births": world.births,
        "deaths": world.deaths,
        "max_generation": max((a.generation for a in world.agents), default=0),
        "mean_energy": sum(a.energy for a in living) / max(1, len(living)),
        "total_harvest": sum(a.total_harvest for a in world.agents),
        "probes": sum(a.probes for a in world.agents),
        "agent_types": dict(kinds),
        "ever_born_by_type": dict(born_by_kind),
        "harvest_by_type": dict(harvest_by_kind),
        "mean_age_by_type": {k: sum(v) / len(v) for k, v in ages_by_kind.items()},
        "science": _science_metrics(world),
        "cognition": _cognition_metrics(world),
        "communication": _communication_metrics(world),
        "technology": _technology_metrics(world),
        "information_structure": _information_structure_metrics(world),
        "behavioral_diversity": _behavioral_diversity_metrics(world),
    }


def _communication_metrics(world) -> dict:
    """Observer-side diagnostics for emergent communication/culture.

    None of these values are exposed to agents or used by evolution.
    Correlation is deliberately reported as evidence, not as 'meaning': random
    controllers can create accidental correlations, so publication-grade claims
    require evolutionary and shuffled baselines.
    """
    recurrent = [a for a in world.agents if getattr(a, "kind", "") == "recurrent"]
    events = world.communication_log
    broadcasts = [e for e in events if e["type"] == "broadcast"]
    inscriptions = [e for e in events if e["type"] == "inscription"]

    def encoding_r2(rows):
        if len(rows) < 12:
            return None
        P = np.asarray([e["payload"] for e in rows], dtype=float)
        if P.ndim != 2 or P.shape[1] == 0 or float(np.std(P)) < 1e-8:
            return None
        Y = np.asarray([[e["temperature"], e["radiation"], e["resource_richness"]] for e in rows], dtype=float)
        X = np.column_stack([np.ones(len(P)), P])
        beta = np.linalg.lstsq(X, Y, rcond=None)[0]
        pred = X @ beta
        denom = np.sum((Y - np.mean(Y, axis=0)) ** 2, axis=0)
        numer = np.sum((Y - pred) ** 2, axis=0)
        valid = denom > 1e-10
        if not np.any(valid):
            return None
        r2 = 1.0 - numer[valid] / denom[valid]
        return float(np.mean(r2))

    # Structural sensitivity of evolved brains to generic conspecific motion,
    # transient signals and persistent public traces. These are substrate
    # diagnostics, not evidence of semantics by themselves.
    sensitivities = []
    body_sensitivities = []
    signal_sensitivities = []
    mark_sensitivities = []
    for a in recurrent:
        if not getattr(a, "_initialized", False):
            continue
        # Input tail = 4 conspecific-motion + 3 signal + 3 mark channels.
        split = a.W_in.shape[1] - 10
        body = float(np.linalg.norm(a.W_in[:, split:split+4]))
        sig = float(np.linalg.norm(a.W_in[:, split+4:split+7]))
        mark = float(np.linalg.norm(a.W_in[:, split+7:split+10]))
        eco = float(np.linalg.norm(a.W_in[:, :split])) + 1e-9
        body_sensitivities.append(body / eco)
        signal_sensitivities.append(sig / eco)
        mark_sensitivities.append(mark / eco)
        sensitivities.append((body + sig + mark) / eco)

    # Receiver uptake: does received payload predict what receivers subsequently do?
    # This remains correlational; causal claims require paired communication-censored runs.
    social_rows = [e for e in world.social_log if e["received_count"] > 0 and e["mean_payload"]]
    action_r2 = None
    motion_r2 = None
    if len(social_rows) >= 20:
        P = np.asarray([e["mean_payload"] for e in social_rows], dtype=float)
        action_names = ["move", "harvest", "rest", "broadcast", "inscribe", "pickup", "drop"]
        Yact = np.asarray([[1.0 if e["action"] == name else 0.0 for name in action_names] for e in social_rows], dtype=float)
        Ymov = np.asarray([[e["dx"], e["dy"]] for e in social_rows], dtype=float)
        X = np.column_stack([np.ones(len(P)), P])
        def multir2(Y):
            beta = np.linalg.lstsq(X, Y, rcond=None)[0]
            pred = X @ beta
            denom = np.sum((Y - np.mean(Y, axis=0)) ** 2, axis=0)
            numer = np.sum((Y - pred) ** 2, axis=0)
            valid = denom > 1e-10
            return float(np.mean(1.0 - numer[valid] / denom[valid])) if np.any(valid) else None
        action_r2 = multir2(Yact)
        motion_r2 = multir2(Ymov)

    generations = sorted({e["generation"] for e in broadcasts})
    signal_generational_span = (max(generations) - min(generations)) if generations else 0

    return {
        "events": len(events),
        "broadcasts": len(broadcasts),
        "inscriptions": len(inscriptions),
        "active_marks": len(world.marks),
        "broadcast_environment_r2": encoding_r2(broadcasts),
        "mark_environment_r2": encoding_r2(inscriptions),
        "mean_social_input_sensitivity": float(np.mean(sensitivities)) if sensitivities else None,
        "mean_body_input_sensitivity": float(np.mean(body_sensitivities)) if body_sensitivities else None,
        "mean_signal_input_sensitivity": float(np.mean(signal_sensitivities)) if signal_sensitivities else None,
        "mean_mark_input_sensitivity": float(np.mean(mark_sensitivities)) if mark_sensitivities else None,
        "receiver_action_r2_from_payload": action_r2,
        "receiver_motion_r2_from_payload": motion_r2,
        "signal_generational_span": signal_generational_span,
        "social_observation_events": len(world.social_log),
        "signal_reception_events": len(social_rows),
        "recurrent_agents_ever_born": len(recurrent),
        "recurrent_alive": sum(a.alive for a in recurrent),
    }


def _technology_metrics(world) -> dict:
    """Observer-only diagnostics for manipulation and configuration effects.

    A high matter multiplier alone is not technology: the world can contain useful
    natural arrangements. Strong evidence requires successful manipulation, a
    causal configuration gain, persistence/reuse, and a paired frozen-object control.
    These diagnostics are never visible to agents.
    """
    from types import SimpleNamespace

    events = world.object_log
    harvest = world.harvest_log
    successful_pickups = sum(e["type"] == "pickup" and e["success"] for e in events)
    successful_drops = sum(e["type"] == "drop" and e["success"] for e in events)
    multipliers = [e["matter_multiplier"] for e in harvest]
    boosted = [m for m in multipliers if m > 1.10]
    moved = []
    for o in world.objects:
        x0, y0 = world.initial_object_positions[o.id]
        moved.append(float(np.hypot(o.x - x0, o.y - y0)))

    # Does this world contain exploitable pair configurations at all? This is a
    # ground-truth affordance diagnostic, not information available to agents.
    sample_sites = [(world.config.width * 0.25, world.config.height * 0.25),
                    (world.config.width * 0.50, world.config.height * 0.50),
                    (world.config.width * 0.75, world.config.height * 0.75)]
    pair_max = 1.0
    pair_min = 1.0
    for x, y in sample_sites:
        temp, rad = world.physical_state(x, y)
        for i in range(len(world.objects)):
            for j in range(i + 1, len(world.objects)):
                oi, oj = world.objects[i], world.objects[j]
                pair = [SimpleNamespace(x=x, y=y, material=oi.material),
                        SimpleNamespace(x=x, y=y, material=oj.material)]
                m = world.matter_law.multiplier(x, y, temp, rad, pair)
                pair_max = max(pair_max, m)
                pair_min = min(pair_min, m)

    # Counterfactual effect of the current arrangement relative to the exact
    # initial object layout, evaluated at the same current physical state.
    initial_objects = [SimpleNamespace(
        x=world.initial_object_positions[o.id][0],
        y=world.initial_object_positions[o.id][1],
        material=o.material,
    ) for o in world.objects]
    current_vals = []
    initial_vals = []
    for p in world.resources:
        temp, rad = world.physical_state(p.x, p.y)
        current_vals.append(world.matter_law.multiplier(p.x, p.y, temp, rad, world.objects))
        initial_vals.append(world.matter_law.multiplier(p.x, p.y, temp, rad, initial_objects))
    config_shift = float(np.mean(current_vals) - np.mean(initial_vals)) if current_vals else 0.0

    return {
        "objects": len(world.objects),
        "manipulation_events": len(events),
        "successful_pickups": successful_pickups,
        "successful_drops": successful_drops,
        "max_harvest_matter_multiplier": float(max(multipliers)) if multipliers else None,
        "mean_harvest_matter_multiplier": float(np.mean(multipliers)) if multipliers else None,
        "boosted_harvest_fraction": len(boosted) / len(multipliers) if multipliers else 0.0,
        "mean_object_displacement": float(np.mean(moved)) if moved else 0.0,
        "max_object_displacement": float(max(moved)) if moved else 0.0,
        "ground_truth_pair_affordance_max": float(pair_max),
        "ground_truth_pair_affordance_min": float(pair_min),
        "configuration_gain_vs_initial": config_shift,
    }


def _information_structure_metrics(world) -> dict:
    """Observer-side diagnostics for private information created by world geometry.

    These quantities never enter agent observations or fitness. They quantify whether
    different individuals actually possess different local evidence, a prerequisite
    for nontrivial communication to become instrumentally useful.
    """
    rows = world.visibility_log
    if not rows:
        return {"visibility_events": 0, "private_information_index": None}
    by_time = defaultdict(list)
    for r in rows:
        by_time[r["time"]].append(r)
    asym = []
    field_spread = []
    for group in by_time.values():
        if len(group) < 2:
            continue
        resource_counts = np.asarray([g["resources"] for g in group], dtype=float)
        agent_counts = np.asarray([g["agents"] for g in group], dtype=float)
        rad = np.asarray([g["radiation"] for g in group], dtype=float)
        asym.append(float(np.std(resource_counts) + 0.5 * np.std(agent_counts)))
        field_spread.append(float(np.std(rad)))
    private_index = None
    if asym:
        private_index = float(np.mean(asym) + np.mean(field_spread))
    return {
        "visibility_events": len(rows),
        "obstacles": len(world.obstacles),
        "active_local_perturbations": len(world.pulses),
        "mean_visible_resources": float(np.mean([r["resources"] for r in rows])),
        "mean_visible_conspecifics": float(np.mean([r["agents"] for r in rows])),
        "mean_cross_agent_visibility_asymmetry": float(np.mean(asym)) if asym else None,
        "mean_cross_agent_local_field_spread": float(np.mean(field_spread)) if field_spread else None,
        "private_information_index": private_index,
    }


def _behavioral_diversity_metrics(world) -> dict:
    """Observer-only measure of spontaneous role differentiation.

    No role labels are supplied. We compare normalized action profiles between
    individuals; high pairwise distance means behavioural specialization has
    appeared from one generic substrate.
    """
    actions = ["move", "harvest", "rest", "broadcast", "inscribe", "pickup", "drop"]
    agents = [a for a in world.agents if sum(getattr(a, "action_counts", {}).values()) >= 20]
    if len(agents) < 2:
        return {"agents_profiled": len(agents), "mean_pairwise_action_distance": None, "profile_entropy": None}
    P=[]
    for a in agents:
        c=getattr(a, "action_counts", {})
        v=np.asarray([c.get(k,0) for k in actions], dtype=float)
        v=v/max(v.sum(),1.0)
        P.append(v)
    P=np.asarray(P)
    ds=[]
    for i in range(len(P)):
        for j in range(i+1,len(P)):
            ds.append(float(np.linalg.norm(P[i]-P[j])))
    mean_profile=np.mean(P, axis=0)
    nz=mean_profile[mean_profile>1e-12]
    entropy=float(-np.sum(nz*np.log(nz))/np.log(len(actions))) if len(nz) else 0.0
    # Dominant-action diversity is deliberately descriptive, not a named-role classifier.
    dom=[actions[int(np.argmax(v))] for v in P]
    return {
        "agents_profiled": len(agents),
        "mean_pairwise_action_distance": float(np.mean(ds)) if ds else 0.0,
        "max_pairwise_action_distance": float(np.max(ds)) if ds else 0.0,
        "profile_entropy": entropy,
        "distinct_dominant_actions": len(set(dom)),
        "dominant_action_counts": dict(Counter(dom)),
    }
