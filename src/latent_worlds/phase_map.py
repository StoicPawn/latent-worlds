"""Observer-side phase mapping for emergent communication.

This module changes no agent objective or controller. It varies only world-side
information geometry and the physical energetic cost of signalling, then asks
whether null-aware, cross-generational communication candidates concentrate in
specific ecological regimes.
"""
from __future__ import annotations

from dataclasses import replace
from collections import defaultdict
import numpy as np

from .config import SimulationConfig
from .longitudinal import run_longitudinal
from .metrics import snapshot
from .world import World


def long_horizon_config(*, information_level: float = 1.0, signal_cost: float = 0.055,
                        communication_enabled: bool = True, agent_seed: int | None = None) -> SimulationConfig:
    """Build a publication-oriented world config without changing agent faculties."""
    q = max(0.0, float(information_level))
    return SimulationConfig(
        generic_population_only=True,
        initial_agents=36,
        resource_patches=84,
        resource_regrowth=0.062,
        basal_metabolism=0.034,
        initial_energy=20.0,
        reproduction_threshold=20.0,
        reproduction_cost=8.5,
        max_population=300,
        signal_cost=float(signal_cost),
        communication_enabled=bool(communication_enabled),
        agent_seed=agent_seed,
        occlusion_enabled=q > 0,
        obstacle_count=int(round(18 * q)) if q > 0 else 0,
        pulse_spawn_rate=0.018 * q,
    )


def _candidate_signal_count(run: dict) -> int:
    return sum(
        "cross_generation_signalling" in c.get("persistent_channels", [])
        for c in run.get("transition_candidates", [])
    )


def screen_cell(information_level: float, signal_cost: float, seeds, *, steps=1200, epoch=100) -> dict:
    rows=[]
    for seed in seeds:
        cfg=long_horizon_config(information_level=information_level, signal_cost=signal_cost)
        run=run_longitudinal(int(seed), steps=steps, epoch=epoch, config=cfg)
        fin=run["final"]["snapshot"]
        rec=run["final"].get("recent_signal_evidence", {})
        rows.append({
            "seed": int(seed),
            "extinct": bool(run["extinct"]),
            "completed_steps": int(run["completed_steps"]),
            "population": int(fin["population"]),
            "max_generation": int(fin["max_generation"]),
            "private_information_index": fin["information_structure"].get("private_information_index"),
            "signal_candidates": _candidate_signal_count(run),
            "encoding_excess": (rec.get("encoding") or {}).get("excess"),
            "uptake_excess": (rec.get("uptake_action") or {}).get("excess"),
            "receiver_rows": rec.get("receiver_rows", 0),
            "broadcast_rows": rec.get("broadcast_rows", 0),
        })
    def vals(key):
        return [float(r[key]) for r in rows if r.get(key) is not None and np.isfinite(r[key])]
    return {
        "information_level": float(information_level),
        "signal_cost": float(signal_cost),
        "worlds": len(rows),
        "extinctions": sum(r["extinct"] for r in rows),
        "candidate_worlds": sum(r["signal_candidates"] > 0 for r in rows),
        "candidate_events": sum(r["signal_candidates"] for r in rows),
        "mean_population": float(np.mean(vals("population"))) if vals("population") else 0.0,
        "mean_max_generation": float(np.mean(vals("max_generation"))) if vals("max_generation") else 0.0,
        "mean_private_information": float(np.mean(vals("private_information_index"))) if vals("private_information_index") else 0.0,
        "mean_encoding_excess": float(np.mean(vals("encoding_excess"))) if vals("encoding_excess") else None,
        "mean_uptake_excess": float(np.mean(vals("uptake_excess"))) if vals("uptake_excess") else None,
        "rows": rows,
    }


def phase_grid(information_levels, signal_costs, seeds, *, steps=1200, epoch=100) -> dict:
    cells=[]
    for q in information_levels:
        for cost in signal_costs:
            cells.append(screen_cell(float(q), float(cost), seeds, steps=steps, epoch=epoch))
    # Rank descriptively; this does not create a claim. Candidate count dominates,
    # then null-aware uptake/encoding evidence. Causal confirmation is separate.
    def score(c):
        return (
            c["candidate_worlds"],
            c["mean_uptake_excess"] if c["mean_uptake_excess"] is not None else -1e9,
            c["mean_encoding_excess"] if c["mean_encoding_excess"] is not None else -1e9,
        )
    ranked=sorted(cells, key=score, reverse=True)
    return {"steps": steps, "epoch": epoch, "seeds": list(map(int,seeds)), "cells": cells, "ranked": ranked}


def causal_information_contrast(seed: int, *, information_level: float, signal_cost: float,
                                steps: int = 1200) -> dict:
    """Matched 2x2 contrast at a fixed ecological regime.

    Fragmentation-enhanced worlds use the requested intensity. The baseline removes
    occlusion/pulses but retains unavoidable locality from finite sensory range. Emission cost is identical in readable and censored worlds.
    """
    def run(q, comm):
        cfg=long_horizon_config(information_level=q, signal_cost=signal_cost,
                                communication_enabled=comm)
        w=World(cfg, seed=int(seed)).run(int(steps))
        return snapshot(w)
    a=run(information_level, True)
    b=run(information_level, False)
    c=run(0.0, True)
    d=run(0.0, False)
    def harvest(x): return float(x["total_harvest"])
    did=(harvest(a)-harvest(b))-(harvest(c)-harvest(d))
    return {
        "seed": int(seed), "information_level": float(information_level),
        "signal_cost": float(signal_cost), "steps": int(steps),
        "harvest_fragmentation_interaction": float(did),
        "population_DiD": float((a["population"]-b["population"])-(c["population"]-d["population"])),
        "A": a, "B": b, "C": c, "D": d,
    }
