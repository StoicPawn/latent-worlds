from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class ActionKind(str, Enum):
    MOVE = "move"
    HARVEST = "harvest"
    REST = "rest"
    PROBE = "probe"
    BROADCAST = "broadcast"
    INSCRIBE = "inscribe"
    PICKUP = "pickup"
    DROP = "drop"


@dataclass(slots=True)
class Action:
    kind: ActionKind
    dx: float = 0.0
    dy: float = 0.0
    payload: tuple[float, ...] = ()


@dataclass(slots=True)
class Genome:
    speed: float = 1.0
    exploration: float = 0.25
    curiosity: float = 0.25
    reproduction_bias: float = 1.0
    memory: float = 0.5
    abstraction: float = 1.0
    signal_range: float = 0.5
    inscription_persistence: float = 0.5
    social_attention: float = 0.5
    plasticity: float = 0.2


@dataclass(slots=True)
class Observation:
    time: int
    x: float
    y: float
    energy: float
    temperature: float
    radiation: float
    nearby_resources: list[tuple[float, float, float]]
    last_action: str | None
    last_yield: float | None
    nearby_signals: list[tuple[float, float, tuple[float, ...]]]
    nearby_marks: list[tuple[float, float, tuple[float, ...], float]]
    nearby_objects: list[tuple[int, float, float, float, tuple[float, float, float]]]
    held_object: tuple[float, tuple[float, float, float]] | None
    nearby_agents: list[tuple[float, float, float, float]]


class BaseAgent:
    kind = "base"

    def __init__(self, agent_id: int, x: float, y: float, energy: float, genome: Genome):
        self.id = agent_id
        self.x = x
        self.y = y
        self.energy = energy
        self.genome = genome
        self.age = 0
        self.alive = True
        self.parent_id: int | None = None
        self.children = 0
        self.generation = 0
        self.last_action: str | None = None
        self.last_yield: float | None = None
        self.probes = 0
        self.total_harvest = 0.0
        self.held_object_id: int | None = None
        self.objects_picked = 0
        self.objects_dropped = 0
        self.memory: dict[str, Any] = {}
        self.prev_x = x
        self.prev_y = y
        self.action_counts: dict[str, int] = {}

    def act(self, obs: Observation, rng) -> Action:
        raise NotImplementedError

    def learn(self, obs: Observation, action: Action, reward: float) -> None:
        pass

    def inherit_from(self, parent: "BaseAgent", rng, sigma: float) -> None:
        """Optional architecture-specific inheritance hook.

        The world does not know what is inherited beyond the generic genome.
        """
        return None
