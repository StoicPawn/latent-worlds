from __future__ import annotations

import math
import numpy as np

from .base import Action, ActionKind, BaseAgent, Observation


class PlannerAgent(BaseAgent):
    """Instrumental world-model controller.

    It learns local sensory dynamics and harvest outcomes solely to choose actions
    expected to preserve energy. There is no uncertainty bonus, discovery score,
    privileged hypothesis space, probe action, or reward for explanatory accuracy.
    """

    kind = "planner"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.transitions: list[tuple[float, float, float, float]] = []  # dx,dy,dT,dR
        self.outcomes: list[tuple[float, float, float]] = []  # T,R,yield
        self._previous_obs: Observation | None = None
        self._previous_action: Action | None = None

    def _ingest_transition(self, obs: Observation) -> None:
        p, a = self._previous_obs, self._previous_action
        if p is None or a is None or a.kind != ActionKind.MOVE:
            return
        dx, dy = obs.x - p.x, obs.y - p.y
        if abs(dx) + abs(dy) < 0.05:
            return
        self.transitions.append((dx, dy, obs.temperature - p.temperature, obs.radiation - p.radiation))
        cap = int(30 + 170 * self.genome.memory)
        if len(self.transitions) > cap:
            del self.transitions[:-cap]

    def _field_map(self) -> np.ndarray | None:
        if len(self.transitions) < 6:
            return None
        A = np.asarray([[q[0], q[1]] for q in self.transitions], dtype=float)
        B = np.asarray([[q[2], q[3]] for q in self.transitions], dtype=float)
        ridge = 1e-4 * np.eye(2)
        return np.linalg.solve(A.T @ A + ridge, A.T @ B)  # [dx,dy] -> [dT,dR]

    def _harvest_value(self, temp: float, rad: float) -> float:
        if len(self.outcomes) < 5:
            return 0.55
        X = np.asarray([[q[0], q[1]] for q in self.outcomes], dtype=float)
        y = np.asarray([q[2] for q in self.outcomes], dtype=float)
        scale = np.maximum(np.std(X, axis=0), [1.0, 0.15])
        d2 = np.sum(((X - [temp, rad]) / scale) ** 2, axis=1)
        bw = max(0.35, self.genome.abstraction)
        w = np.exp(-0.5 * d2 / bw)
        return float(np.dot(w, y) / w.sum()) if float(w.sum()) > 1e-8 else float(np.mean(y))

    def act(self, obs: Observation, rng) -> Action:
        self._ingest_transition(obs)

        if obs.nearby_resources:
            value = self._harvest_value(obs.temperature, obs.radiation)
            if obs.energy < 8.0 or value > 0.38:
                action = Action(ActionKind.HARVEST)
                self._previous_obs, self._previous_action = obs, action
                return action

        if rng.random() < self.genome.exploration:
            angle = rng.uniform(0.0, 2.0 * math.pi)
            action = Action(ActionKind.MOVE, math.cos(angle), math.sin(angle))
            self._previous_obs, self._previous_action = obs, action
            return action

        J = self._field_map()
        candidates = np.linspace(0.0, 2.0 * math.pi, 12, endpoint=False)
        best = None
        best_score = -1e9
        for angle in candidates:
            move = np.asarray([math.cos(angle), math.sin(angle)]) * self.genome.speed
            t, r = obs.temperature, obs.radiation
            if J is not None:
                delta = move @ J
                t += float(delta[0])
                r += float(delta[1])
            score = self._harvest_value(t, r)
            # Ordinary ecological cue: moving toward visible food is useful.
            if obs.nearby_resources:
                dx, dy, richness = obs.nearby_resources[0]
                norm = math.hypot(dx, dy) or 1.0
                score += 0.22 * richness / 8.0 * float(np.dot(move, [dx / norm, dy / norm]))
            if score > best_score:
                best_score, best = score, move
        action = Action(ActionKind.MOVE, float(best[0]), float(best[1]))
        self._previous_obs, self._previous_action = obs, action
        return action

    def learn(self, obs: Observation, action: Action, reward: float) -> None:
        if action.kind == ActionKind.HARVEST and self.last_yield is not None:
            self.outcomes.append((obs.temperature, obs.radiation, self.last_yield))
            cap = int(30 + 170 * self.genome.memory)
            if len(self.outcomes) > cap:
                del self.outcomes[:-cap]
