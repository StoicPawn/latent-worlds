from __future__ import annotations

import math

from .base import Action, ActionKind, BaseAgent, Observation


class ReactiveAgent(BaseAgent):
    kind = "reactive"

    def act(self, obs: Observation, rng) -> Action:
        if obs.last_yield is not None:
            old = float(self.memory.get("best_yield", -1.0))
            if obs.last_yield > old:
                self.memory["best_yield"] = obs.last_yield
                self.memory["best_temp"] = obs.temperature

        if obs.nearby_resources:
            preferred = self.memory.get("best_temp")
            if preferred is None or abs(obs.temperature - preferred) < 3.5:
                return Action(ActionKind.HARVEST)

        if rng.random() < self.genome.exploration:
            angle = rng.uniform(0.0, 2.0 * math.pi)
        else:
            angle = 0.0 if obs.temperature < self.memory.get("best_temp", obs.temperature) else math.pi
        return Action(ActionKind.MOVE, math.cos(angle), math.sin(angle))
