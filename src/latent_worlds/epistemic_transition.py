from __future__ import annotations

"""Observer-side assays for spontaneous epistemic transitions.

Nothing here is visible to agents and nothing changes reward or world dynamics.
The assay asks whether survival-driven recurrent populations come to carry
predictive information about a hidden global law, whether that information is
more accessible collectively than individually, and whether social channels
are causally required for the effect.
"""

from dataclasses import dataclass
import numpy as np

from .config import SimulationConfig
from .world import World
from .agents.recurrent import RecurrentAgent


@dataclass(slots=True)
class EpistemicResult:
    samples: int
    horizon: int
    raw_rmse: float
    collective_rmse: float
    individual_rmse: float
    collective_gain_over_raw: float
    collective_gain_over_individual: float
    late_gain_over_early: float
    max_generation: int

    @property
    def candidate(self) -> bool:
        return (
            self.samples >= 80
            and self.collective_gain_over_raw > 0.03
            and self.collective_gain_over_individual > 0.02
            and self.late_gain_over_early > 0.0
        )


def _ridge_fit_predict(Xtr, ytr, Xte, alpha=1e-2):
    Xtr = np.asarray(Xtr, float); Xte = np.asarray(Xte, float)
    ytr = np.asarray(ytr, float)
    mu = Xtr.mean(0); sd = np.maximum(Xtr.std(0), 1e-6)
    A = np.column_stack([np.ones(len(Xtr)), (Xtr-mu)/sd])
    B = np.column_stack([np.ones(len(Xte)), (Xte-mu)/sd])
    reg = alpha*np.eye(A.shape[1]); reg[0,0] = 0.0
    coef = np.linalg.solve(A.T@A + reg, A.T@ytr)
    return B@coef


def _temporal_rmse(X, y, split=0.65):
    n=len(y); k=max(20, min(n-20, int(n*split)))
    pred=_ridge_fit_predict(X[:k], y[:k], X[k:])
    return float(np.sqrt(np.mean((pred-y[k:])**2)))


def _gain(base, model):
    return float((base-model)/max(base, 1e-9))


def _snapshot(world: World):
    agents=[a for a in world.agents if isinstance(a, RecurrentAgent) and a.alive and a._initialized]
    if not agents:
        return None
    H=np.asarray([a.hidden for a in agents], float)
    # Permutation-invariant population representation; no identities or roles.
    collective=np.concatenate([H.mean(0), H.std(0), np.quantile(H, .25, axis=0), np.quantile(H, .75, axis=0)])
    # Best-individual comparison is approximated without privileged identity by
    # selecting the oldest living agent, fixed by a world-side demographic fact.
    focal=max(agents, key=lambda a: a.age)
    individual=focal.hidden.copy()
    # Raw baseline contains only contemporaneous population-level surface evidence.
    phys=np.asarray([world.physical_state(a.x,a.y) for a in agents], float)
    raw=np.concatenate([phys.mean(0), phys.std(0), [len(agents)/100.0]])
    return raw, collective, individual, max(a.generation for a in agents)


def run_epistemic_assay(world_seed:int, agent_seed:int, *, steps:int=1400, horizon:int=35,
                         communication_enabled:bool=True, marks_enabled:bool=True,
                         turnover:bool=False) -> EpistemicResult:
    cfg=SimulationConfig(generic_population_only=True, agent_seed=agent_seed,
                         communication_enabled=communication_enabled, marks_enabled=marks_enabled)
    if turnover:
        cfg.reproduction_threshold=15.0; cfg.reproduction_cost=6.0; cfg.resource_regrowth=0.07
    w=World(cfg, seed=world_seed)
    rows=[]
    # Snapshot after actions. Target is future hidden forcing, never exposed to agents.
    for _ in range(steps):
        w.step()
        s=_snapshot(w)
        if s is not None:
            raw,col,ind,g=s
            target=float(w.forcing_law.value(w.time+horizon))
            rows.append((raw,col,ind,target,g))
        if not w.agents:
            break
    if len(rows)<45:
        inf=float('inf')
        return EpistemicResult(len(rows),horizon,inf,inf,inf,0,0,0,0)
    raw=np.asarray([r[0] for r in rows]); col=np.asarray([r[1] for r in rows]); ind=np.asarray([r[2] for r in rows]); y=np.asarray([r[3] for r in rows])
    rr=_temporal_rmse(raw,y); cr=_temporal_rmse(col,y); ir=_temporal_rmse(ind,y)
    # Emergence-in-time: compare predictive gain in first and second halves with
    # local train/test splits, rather than fitting on the future and testing past.
    mid=len(y)//2
    def local_gain(sl):
        br=_temporal_rmse(raw[sl],y[sl],split=.6); mr=_temporal_rmse(col[sl],y[sl],split=.6)
        return _gain(br,mr)
    early=local_gain(slice(0,mid)); late=local_gain(slice(mid,None))
    return EpistemicResult(len(rows),horizon,rr,cr,ir,_gain(rr,cr),_gain(ir,cr),late-early,max(r[4] for r in rows))


def causal_epistemic_contrast(world_seed:int, agent_seed:int, **kwargs):
    """Readable vs socially censored worlds; same world/population seeds."""
    real=run_epistemic_assay(world_seed,agent_seed,communication_enabled=True,marks_enabled=True,**kwargs)
    censored=run_epistemic_assay(world_seed,agent_seed,communication_enabled=False,marks_enabled=False,**kwargs)
    return {
        'real': real,
        'censored': censored,
        'causal_collective_gain': real.collective_gain_over_raw-censored.collective_gain_over_raw,
        'causal_amplification': real.late_gain_over_early-censored.late_gain_over_early,
    }
