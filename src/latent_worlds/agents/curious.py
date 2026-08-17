from __future__ import annotations

import math
import numpy as np

from .base import Action, ActionKind, BaseAgent, Observation


class CuriousAgent(BaseAgent):
    """Learns a single flexible predictor without explicit model competition."""

    kind = "curious"

    def _samples(self) -> list[tuple[float, float, float]]:
        return self.memory.setdefault("samples", [])

    def learn(self, obs: Observation, action: Action, reward: float) -> None:
        if action.kind in {ActionKind.HARVEST, ActionKind.PROBE} and self.last_yield is not None:
            samples = self._samples()
            samples.append((obs.temperature, obs.radiation, self.last_yield))
            if len(samples) > 100:
                del samples[:-100]

    def _predict(self, temperature: float, radiation: float) -> tuple[float, float]:
        samples = self._samples()
        if len(samples) < 7:
            return 0.0, 1.0
        X0 = np.asarray([[s[0], s[1]] for s in samples], dtype=float)
        y = np.asarray([s[2] for s in samples], dtype=float)
        mu = X0.mean(axis=0)
        sc = np.maximum(X0.std(axis=0), 0.5)
        z = (X0 - mu) / sc
        X = np.column_stack([np.ones(len(z)), z[:, 0], z[:, 1], z[:, 0]**2, z[:, 1]**2, z[:, 0]*z[:, 1]])
        coef, *_ = np.linalg.lstsq(X, y, rcond=None)
        zz = (np.asarray([temperature, radiation]) - mu) / sc
        row = np.asarray([1.0, zz[0], zz[1], zz[0]**2, zz[1]**2, zz[0]*zz[1]])
        pred = float(row @ coef)
        residual = y - X @ coef
        uncertainty = float(np.std(residual)) + 1.0 / math.sqrt(len(samples))
        return pred, uncertainty

    def act(self, obs: Observation, rng) -> Action:
        samples = self._samples()
        pred, uncertainty = self._predict(obs.temperature, obs.radiation)
        if rng.random() < self.genome.curiosity * min(1.0, uncertainty) and len(samples) < 45:
            return Action(ActionKind.PROBE)
        if obs.nearby_resources and (len(samples) < 7 or pred > 0.58):
            return Action(ActionKind.HARVEST)
        angle = rng.uniform(0.0, 2.0 * math.pi)
        return Action(ActionKind.MOVE, math.cos(angle), math.sin(angle))
