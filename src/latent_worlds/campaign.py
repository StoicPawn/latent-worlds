"""Observer-side campaign utilities for rare emergent communication events.

No agent or world behaviour is changed here. The module only screens many seeds,
then performs matched readable-vs-censored follow-up on strict burst candidates.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from .phase_map import long_horizon_config
from .longitudinal import run_longitudinal


@dataclass(frozen=True)
class BurstOutcome:
    information_level: float
    seed: int
    readable_population: int
    censored_population: int
    readable_harvest: float
    censored_harvest: float
    delta_population: int
    delta_harvest: float
    max_generation: int
    burst_windows: int
    burst_generations: int
    interpretation: str


def classify_burst(delta_harvest: float, delta_population: int, *, harvest_tol: float = 20.0) -> str:
    """Conservative descriptive label; never exposed to agents or used as reward."""
    if delta_harvest > harvest_tol and delta_population >= 0:
        return "fitness-positive-candidate"
    if delta_harvest < -harvest_tol or delta_population < -1:
        return "maladaptive-or-costly"
    return "approximately-neutral"


def strict_screen(information_levels, seeds, *, signal_cost=0.03, steps=800, epoch=100):
    rows=[]
    for q in information_levels:
        for seed in seeds:
            cfg=long_horizon_config(information_level=float(q), signal_cost=signal_cost)
            run=run_longitudinal(int(seed), steps=steps, epoch=epoch, config=cfg)
            rows.append({
                "information_level": float(q),
                "seed": int(seed),
                "population": int(run["final"]["snapshot"]["population"]),
                "max_generation": int(run["final"]["snapshot"]["max_generation"]),
                "bursts": run.get("transient_communication_bursts", []),
                "extinct": bool(run["extinct"]),
            })
    return rows


def matched_followup(information_level: float, seed: int, *, signal_cost=0.03, steps=1600, epoch=100):
    def run(comm):
        cfg=long_horizon_config(information_level=information_level, signal_cost=signal_cost,
                                communication_enabled=comm)
        return run_longitudinal(seed, steps=steps, epoch=epoch, config=cfg)
    readable=run(True)
    censored=run(False)
    rs=readable["final"]["snapshot"]
    cs=censored["final"]["snapshot"]
    bursts=readable.get("transient_communication_bursts", [])
    windows=max((b["windows"] for b in bursts), default=0)
    generations=max((b["max_active_signal_generations"] for b in bursts), default=0)
    dh=float(rs["total_harvest"]-cs["total_harvest"])
    dp=int(rs["population"]-cs["population"])
    out=BurstOutcome(
        information_level=float(information_level), seed=int(seed),
        readable_population=int(rs["population"]), censored_population=int(cs["population"]),
        readable_harvest=float(rs["total_harvest"]), censored_harvest=float(cs["total_harvest"]),
        delta_population=dp, delta_harvest=dh,
        max_generation=int(rs["max_generation"]), burst_windows=int(windows),
        burst_generations=int(generations), interpretation=classify_burst(dh, dp),
    )
    return asdict(out)


def content_placebo_followup(information_level: float, seed: int, *, signal_cost=0.03, steps=1200, epoch=100, agent_seed: int | None = None):
    """Compare readable content with payload-scrambled and fully censored controls.

    Scrambling preserves message opportunities, locations, ranges, costs, and the
    marginal payload distribution while breaking the sender-state/content pairing.
    A content-sensitive convention should outperform this placebo, not merely censoring.
    """
    def run(mode):
        cfg=long_horizon_config(information_level=information_level, signal_cost=signal_cost,
                                communication_enabled=(mode != "censored"), agent_seed=agent_seed)
        cfg.communication_scramble = (mode == "scrambled")
        return run_longitudinal(seed, steps=steps, epoch=epoch, config=cfg)
    runs={m:run(m) for m in ("readable","scrambled","censored")}
    out={"information_level":float(information_level),"seed":int(seed),"agent_seed":None if agent_seed is None else int(agent_seed)}
    for m,r in runs.items():
        s=r["final"]["snapshot"]
        out[m]={"population":int(s["population"]),"harvest":float(s["total_harvest"]),
                "max_generation":int(s["max_generation"]),
                "bursts":r.get("transient_communication_bursts",[])}
    out["delta_readable_vs_scrambled_harvest"]=out["readable"]["harvest"]-out["scrambled"]["harvest"]
    out["delta_readable_vs_censored_harvest"]=out["readable"]["harvest"]-out["censored"]["harvest"]
    out["delta_readable_vs_scrambled_population"]=out["readable"]["population"]-out["scrambled"]["population"]
    return out


def population_world_transplant(world_seeds, agent_seeds, *, information_level=0.35, signal_cost=0.03, steps=800, epoch=100):
    """Observer-side factorial transplant of population stochasticity across worlds.

    No behaviour is added. `world_seed` controls world physics/dynamics; `agent_seed`
    controls initial genomes/controllers and subsequent agent-side stochasticity.
    This separates population propensity from ecological opportunity.
    """
    rows=[]
    for ws in world_seeds:
        for aseed in agent_seeds:
            cfg=long_horizon_config(information_level=information_level, signal_cost=signal_cost,
                                    communication_enabled=True, agent_seed=int(aseed))
            run=run_longitudinal(int(ws), steps=steps, epoch=epoch, config=cfg)
            fin=run["final"]["snapshot"]
            bursts=run.get("transient_communication_bursts",[])
            rows.append({"world_seed":int(ws),"agent_seed":int(aseed),
                         "population":int(fin["population"]),"max_generation":int(fin["max_generation"]),
                         "bursts":bursts,"strict_candidate":bool(bursts),"extinct":bool(run["extinct"])})
    return rows
