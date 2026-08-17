from __future__ import annotations

import math

from .base import Action, ActionKind, BaseAgent, Observation


class RandomAgent(BaseAgent):
    kind = "random"

    def act(self, obs: Observation, rng) -> Action:
        if obs.nearby_resources and rng.random() < 0.45:
            return Action(ActionKind.HARVEST)
        angle = rng.uniform(0.0, 2.0 * math.pi)
        return Action(ActionKind.MOVE, math.cos(angle), math.sin(angle))
