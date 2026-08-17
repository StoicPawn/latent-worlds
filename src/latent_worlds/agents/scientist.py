from __future__ import annotations

import math
import numpy as np

from .base import Action, ActionKind, BaseAgent, Observation
from latent_worlds.science_hypotheses import HypothesisEnsemble


class ScientistAgent(BaseAgent):
    """Agent that competes multivariate hypotheses and seeks informative states."""

    kind = "scientist"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.science = HypothesisEnsemble()
        self.epistemic_actions = 0
        self._history: list[tuple[float, float, float, float]] = []  # x,y,T,R

    def learn(self, obs: Observation, action: Action, reward: float) -> None:
        if action.kind in {ActionKind.HARVEST, ActionKind.PROBE} and self.last_yield is not None:
            self.science.add((obs.temperature, obs.radiation), self.last_yield)
        self._history.append((obs.x, obs.y, obs.temperature, obs.radiation))
        if len(self._history) > 40:
            del self._history[:-40]

    def _environment_jacobian(self) -> np.ndarray | None:
        """Infer how movement changes observed fields from the agent's own history."""
        if len(self._history) < 8:
            return None
        rows = []
        targets = []
        for a, b in zip(self._history[:-1], self._history[1:]):
            dx, dy = b[0] - a[0], b[1] - a[1]
            if abs(dx) + abs(dy) < 0.1:
                continue
            rows.append([dx, dy])
            targets.append([b[2] - a[2], b[3] - a[3]])
        if len(rows) < 5:
            return None
        A = np.asarray(rows, dtype=float)
        B = np.asarray(targets, dtype=float)
        coef, *_ = np.linalg.lstsq(A, B, rcond=None)
        # coef maps [dx,dy] -> [dT,dR]
        return coef

    def _seek_novel_environment(self, obs: Observation, rng) -> Action:
        if not self.science.samples:
            angle = rng.uniform(0.0, 2.0 * math.pi)
            return Action(ActionKind.MOVE, math.cos(angle), math.sin(angle))
        X = np.asarray([s[0] for s in self.science.samples], dtype=float)
        current = np.asarray([obs.temperature, obs.radiation], dtype=float)
        centre = np.mean(X, axis=0)
        scale = np.maximum(np.std(X, axis=0), 0.5)
        # Seek away from already sampled regions in observable-state space.
        desired = (current - centre) / scale
        if float(np.linalg.norm(desired)) < 0.4:
            desired = rng.normal(0.0, 1.0, size=2)
        J = self._environment_jacobian()
        if J is None:
            angle = rng.uniform(0.0, 2.0 * math.pi)
            return Action(ActionKind.MOVE, math.cos(angle), math.sin(angle))
        move, *_ = np.linalg.lstsq(J.T, desired, rcond=None)
        if not np.all(np.isfinite(move)) or float(np.linalg.norm(move)) < 1e-6:
            angle = rng.uniform(0.0, 2.0 * math.pi)
            return Action(ActionKind.MOVE, math.cos(angle), math.sin(angle))
        return Action(ActionKind.MOVE, float(move[0]), float(move[1]))

    def act(self, obs: Observation, rng) -> Action:
        features = (obs.temperature, obs.radiation)
        pred, uncertainty = self.science.predict(features)
        n = len(self.science.samples)

        # Explicit, costly experiment. The decision depends on epistemic
        # uncertainty rather than on privileged knowledge of the true equation.
        probe_pressure = min(1.0, uncertainty) * (0.30 + self.genome.curiosity)
        if (n < 8 or rng.random() < probe_pressure * 0.28) and obs.energy > 4.5:
            self.epistemic_actions += 1
            return Action(ActionKind.PROBE)

        if obs.nearby_resources and (n < 6 or pred > 0.28 or obs.energy < 12.0):
            return Action(ActionKind.HARVEST)

        if n >= 5 and obs.energy > 8.0 and rng.random() < 0.50:
            self.epistemic_actions += 1
            return self._seek_novel_environment(obs, rng)

        angle = rng.uniform(0.0, 2.0 * math.pi)
        return Action(ActionKind.MOVE, math.cos(angle), math.sin(angle))
