from __future__ import annotations

import math
import numpy as np

from .base import Action, ActionKind, BaseAgent, Observation


class ModelBasedAgent(BaseAgent):
    """Generic predictive controller, not a scientist.

    It receives no reward for prediction accuracy, novelty, uncertainty reduction,
    model complexity, or discovery. It simply learns correlations between its
    sensory state, actions and subsequent energetic consequences, then uses those
    predictions instrumentally when choosing what to do.
    """

    kind = "model_based"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.experiences: list[tuple[np.ndarray, str, float]] = []
        self._pending: tuple[np.ndarray, str] | None = None

    @staticmethod
    def _features(obs: Observation) -> np.ndarray:
        nearest = obs.nearby_resources[0] if obs.nearby_resources else (0.0, 0.0, 0.0)
        dist = math.hypot(nearest[0], nearest[1]) if obs.nearby_resources else 8.0
        return np.asarray([
            1.0,
            obs.energy / 25.0,
            obs.temperature / 20.0,
            obs.radiation,
            min(dist, 8.0) / 8.0,
            min(nearest[2], 8.0) / 8.0,
            math.sin(0.031 * obs.time),
            math.cos(0.031 * obs.time),
        ], dtype=float)

    def learn(self, obs: Observation, action: Action, reward: float) -> None:
        x = self._features(obs)
        self.experiences.append((x, action.kind.value, float(reward)))
        cap = int(max(20, min(240, round(40 + 180 * self.genome.memory))))
        if len(self.experiences) > cap:
            del self.experiences[:-cap]

    def _estimate(self, x: np.ndarray, action: str) -> tuple[float, int]:
        rows = [(xx, r) for xx, a, r in self.experiences if a == action]
        if len(rows) < 5:
            return 0.0, len(rows)
        X = np.vstack([q[0] for q in rows])
        y = np.asarray([q[1] for q in rows], dtype=float)
        # Generic local kernel predictor. No model family corresponds to a world law.
        scale = np.maximum(np.std(X, axis=0), 0.15)
        d2 = np.sum(((X - x) / scale) ** 2, axis=1)
        k = np.exp(-0.5 * d2 / max(0.35, self.genome.abstraction))
        if float(k.sum()) < 1e-8:
            return float(np.mean(y)), len(rows)
        return float(np.dot(k, y) / k.sum()), len(rows)

    def act(self, obs: Observation, rng) -> Action:
        # Hard survival reflex only when energy is critically low. Everything else
        # is selected from generic learned energetic consequences.
        if obs.energy < 4.0 and obs.nearby_resources:
            return Action(ActionKind.HARVEST)

        x = self._features(obs)
        actions = [ActionKind.HARVEST, ActionKind.REST, ActionKind.MOVE]
        estimates = []
        for a in actions:
            pred, n = self._estimate(x, a.value)
            # optimistic defaults are NOT tied to uncertainty/discovery; they merely
            # prevent a newborn controller from freezing before it has experience.
            if n < 5:
                pred += 0.015 * (5 - n)
            estimates.append(pred)

        if rng.random() < self.genome.exploration:
            chosen = actions[int(rng.integers(0, len(actions)))]
        else:
            chosen = actions[int(np.argmax(estimates))]

        if chosen == ActionKind.HARVEST:
            return Action(chosen)
        if chosen == ActionKind.REST:
            return Action(chosen)

        if obs.nearby_resources and rng.random() > self.genome.exploration:
            dx, dy, _ = obs.nearby_resources[0]
            return Action(ActionKind.MOVE, dx, dy)
        angle = rng.uniform(0.0, 2.0 * math.pi)
        return Action(ActionKind.MOVE, math.cos(angle), math.sin(angle))
