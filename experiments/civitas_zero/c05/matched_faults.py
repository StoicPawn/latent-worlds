"""CIVITAS ZERO C0.5 — matched instantaneous internal/external faults.

Purpose: check IDENTIFIABILITY before any AI-consciousness indicator assay.
The internal arm changes the agent's actual recurrent weights; the external
arm perturbs temperature in its input observation. The perturbations are
constructed to produce the SAME first recurrent state, logits and actions.

This is an algebraic positive control, not a learned self-model, consciousness,
or original theorem. It explicitly FAILS full-history input matching because
the external arm observes a different temperature at the intervention step.
Subsequent observations are an OPEN-LOOP replay of a real, unmodified world.
"""
from __future__ import annotations
import argparse
import copy
from dataclasses import replace
import json
from pathlib import Path
from statistics import mean
import numpy as np

from latent_worlds.world import World
from latent_worlds.agents.recurrent import RecurrentAgent
from latent_worlds.phase_map import long_horizon_config
from latent_worlds.replication import standard_turnover_overrides

WORLDS = (11, 21)
AGENT_SEED = 211
WARMUP = 145
REPLAY = 6
DELTA = .25
MAX_AGENTS = 40
RNG_SEED = 51025


def cfg_for(agent_seed=AGENT_SEED):
    cfg = long_horizon_config(information_level=.35, signal_cost=.03,
                               communication_enabled=True, agent_seed=agent_seed)
    for k, v in standard_turnover_overrides().items():
        if not hasattr(cfg, k):
            raise ValueError(k)
        setattr(cfg, k, v)
    cfg.active_obstacle_fraction = .75
    cfg.resource_wave_strength = 1.5
    cfg.recurrent_context_features_enabled = True
    cfg.recurrent_learning_enabled = True
    cfg.recurrent_weight_inheritance_enabled = True
    cfg.recurrent_state_plasticity_enabled = True
    cfg.recurrent_state_plasticity_rate = .0003
    return cfg


def make_pair(agent: RecurrentAgent, first_obs, delta=DELTA):
    """Match recurrent preactivations algebraically, not by fitted labels.

    Agent's x_temperature = obs.temperature/20, feature index 1.
    h=tan h(W_in x+W_rec h_prev). Let ΔW_rec be:
          ΔW_rec = δ W_in[:,1] h_prev^T / (h_prev^T h_prev)
    Then (W_rec + ΔW_rec)h_prev = W_rec h_prev + δ W_in[:,1],
    exactly the same preactivation as increasing x_temperature by δ.

    For t>0, internal lesion persists, while external temperature pulse
    stops, so paths can diverge without refitting the first-step match.
    """
    if not agent._initialized or agent.W_in is None or agent.W_rec is None:
        raise ValueError("Need an initialized recurrent agent")
    if agent.hidden @ agent.hidden < .01:
        raise ValueError("Recurrent history is too small")
    internal = copy.deepcopy(agent)
    external = copy.deepcopy(agent)
    h = np.asarray(agent.hidden, dtype=float)
    internal.W_rec = internal.W_rec + np.outer(
        internal.W_in[:, 1] * delta, h / float(h @ h))
    obs_external = replace(first_obs, temperature=first_obs.temperature + 20 * delta)
    x0 = agent._features(first_obs, 3)
    x1 = external._features(obs_external, 3)
    if not np.isclose(x1[1] - x0[1], delta, atol=1e-14):
        raise AssertionError("Temperature feature unexpectedly changed")
    if not np.allclose(x0[np.arange(len(x0)) != 1],
                       x1[np.arange(len(x1)) != 1], atol=1e-14):
        raise AssertionError("External intervention changed other features")
    z_in = internal.W_in @ x0 + internal.W_rec @ h
    z_ex = external.W_in @ x1 + external.W_rec @ h
    if not np.allclose(z_in, z_ex, atol=1e-12):
        raise AssertionError("Mismatch in the preactivation (incorrect pair)")
    return internal, external, obs_external


def replay_pair(agent, observations, *, delta=DELTA, rng_seed=RNG_SEED, persistent=True) -> dict:
    if len(observations) < REPLAY:
        raise ValueError("Insufficient unmodified-world trajectory")
    a, b, external_obs = make_pair(agent, observations[0], delta)
    rng_a = np.random.default_rng(rng_seed)
    rng_b = np.random.default_rng(rng_seed)
    hidden_diffs, logit_diffs, action_mismatch = [], [], []
    for step, obs in enumerate(observations):
        oa = obs
        ob = external_obs if step == 0 else obs
        ac_a = a.act(oa, rng_a)
        ac_b = b.act(ob, rng_b)
        if not a._initialized or not b._initialized:
            raise AssertionError("Missing real recurrent policy")
        hdiff = float(np.max(np.abs(a.hidden - b.hidden)))
        la = a.W_out @ np.r_[a.hidden, 1.]
        lb = b.W_out @ np.r_[b.hidden, 1.]
        ldiff = float(np.max(np.abs(la - lb)))
        hidden_diffs.append(hdiff)
        logit_diffs.append(ldiff)
        action_mismatch.append(ac_a.kind != ac_b.kind)
        if step == 0 and not persistent:
            # One-step INTERNAL fault is restored after the first action.
            # Both latent trajectories must now remain exactly identical,
            # except for numerical floating-point roundoff.
            a.W_rec = b.W_rec.copy()
    if hidden_diffs[0] > 1e-10 or logit_diffs[0] > 1e-10 or action_mismatch[0]:
        raise AssertionError("First-step state/logits/discrete action were not matched")
    return {
        "first_step_hidden_max_abs_diff": hidden_diffs[0],
        "first_step_logits_max_abs_diff": logit_diffs[0],
        "first_step_action_changed": action_mismatch[0],
        "subsequent_hidden_max_abs_diff": hidden_diffs[1:],
        "subsequent_logits_max_abs_diff": logit_diffs[1:],
        "subsequent_action_kind_mismatch": action_mismatch[1:],
        "internal_recurrent_weights_changed": float(np.linalg.norm(
            a.W_rec - b.W_rec)),
        "external_temperature_pulse": float(external_obs.temperature -
                                           observations[0].temperature),
        "full_observation_histories_matched": False,
        "internal_fault_persists": bool(persistent),
    }


def collect_world(world_seed: int, *, warmup=WARMUP, max_agents=MAX_AGENTS):
    """Collect source states and a real-world 6-step sensory replay.

    The clone policies are NOT inserted into the world. This tests a local
    recurrent observability gate, not survival or adaptive behavior.
    """
    w = World(cfg_for(), seed=world_seed)
    w.run(warmup)
    candidates = {}
    obs_series = {}
    for step in range(REPLAY):
        now = {a.id: a for a in w.agents if a.alive and
               isinstance(a, RecurrentAgent) and a._initialized}
        if step == 0:
            selected = sorted(now, key=int)[:max_agents]
            for i in selected:
                a = now[i]
                if float(a.hidden @ a.hidden) < .01:
                    continue
                candidates[i] = copy.deepcopy(a)
                obs_series[i] = []
        for i in list(candidates):
            if i in now:
                obs_series[i].append(w.observe(now[i]))
        w.step()
    rows = []
    for i, a in candidates.items():
        obs = obs_series.get(i, [])
        if len(obs) != REPLAY:
            continue
        # Homeostatic emergency reflex bypasses the recurrent calculation.
        if any(o.energy < 4.5 for o in obs):
            continue
        result = replay_pair(a, obs, rng_seed=RNG_SEED+i, persistent=True)
        transient = replay_pair(a, obs, rng_seed=RNG_SEED+i, persistent=False)
        if any(z > 1e-10 for z in transient["subsequent_hidden_max_abs_diff"]):
            raise AssertionError("Transient fault was not observationally matched")
        result["transient_pair_max_future_hidden_diff"] = max(
            transient["subsequent_hidden_max_abs_diff"])
        result["transient_pair_max_future_logits_diff"] = max(
            transient["subsequent_logits_max_abs_diff"])
        result["transient_pair_action_kind_mismatches"] = sum(
            transient["subsequent_action_kind_mismatch"])
        result["agent_id"] = i
        rows.append(result)
    if not rows:
        raise RuntimeError("No observable non-reflex recurrent trajectory")
    return {
        "world_seed": world_seed, "agent_seed": AGENT_SEED,
        "warmup": warmup, "steps_replayed": REPLAY,
        "n_eligible_agents": len(rows),
        "n_alive_after": sum(a.alive for a in w.agents),
        "mean_first_step_hidden_diff": mean(x["first_step_hidden_max_abs_diff"] for x in rows),
        "mean_first_step_logits_diff": mean(x["first_step_logits_max_abs_diff"] for x in rows),
        "fraction_diverged_by_second_step": mean(x["subsequent_hidden_max_abs_diff"][0] > 1e-8 for x in rows),
        "max_transient_fault_future_hidden_diff": max(
            x["transient_pair_max_future_hidden_diff"] for x in rows),
        "max_transient_fault_future_logits_diff": max(
            x["transient_pair_max_future_logits_diff"] for x in rows),
        "mean_delayed_hidden_diff_by_step": [
            mean(x["subsequent_hidden_max_abs_diff"][j] for x in rows)
            for j in range(REPLAY-1)
        ],
        "fraction_action_kind_mismatch_by_step": [
            mean(x["subsequent_action_kind_mismatch"][j] for x in rows)
            for j in range(REPLAY-1)
        ],
        "individual": rows,
        "method": "Algebraically matched first-step input-vs-recurrent-weight fault; real policy; open-loop replay of unchanged real world observations",
        "limitations": [
            "Both arms have identical initial hidden state and discrete action BY CONSTRUCTION, not a discovered property.",
            "Observed temperature differs at the intervention instant; a monitor with access to raw sensors could trivially distinguish causes.",
            "Replayed observations do not respond to counterfactual actions; no causal survival effect is estimated.",
            "Lesion ΔW_rec depends on that agent's current hidden state; not a plausible spontaneous fault distribution.",
            "The perfectly matched transient pairs are a deliberately engineered null: this is a demonstration of nonidentifiability from hidden/output alone, not proof of metacognition.",
            "No agent has learned any monitoring or self-modeling mechanism; observer-only calibration/feasibility result.",
            "Agents in same world are correlated; sample size is not independent world-law replication.",
        ],
    }


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--world", type=int, choices=WORLDS, default=11)
    ap.add_argument("--warmup", type=int, default=WARMUP)
    ap.add_argument("--max-agents", type=int, default=MAX_AGENTS)
    ap.add_argument("--output-dir", type=Path,
                    default=Path("experiments/civitas_zero/c05/data"))
    args=ap.parse_args()
    dest=args.output_dir/f"matched_fault_W{args.world}_A{AGENT_SEED}.json"
    if dest.exists():
        raise FileExistsError(f"Pilot result exists; refusing to overwrite {dest}")
    result=collect_world(args.world,warmup=args.warmup,max_agents=args.max_agents)
    args.output_dir.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({
        "file":str(dest),
        "n_eligible_agents":result["n_eligible_agents"],
        "mean_first_step_hidden_diff":result["mean_first_step_hidden_diff"],
        "mean_first_step_logits_diff":result["mean_first_step_logits_diff"],
        "fraction_diverged_by_second_step":result["fraction_diverged_by_second_step"],
        "max_transient_fault_future_hidden_diff":result["max_transient_fault_future_hidden_diff"],
        "mean_delayed_hidden_diff_by_step":result["mean_delayed_hidden_diff_by_step"]
    },indent=2))


if __name__=="__main__":
    main()
