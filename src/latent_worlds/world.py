from __future__ import annotations

from dataclasses import dataclass
import math
import numpy as np

from .agents import ActionKind, Genome, Observation, RandomAgent, ReactiveAgent, ModelBasedAgent, PlannerAgent, RecurrentAgent
from .config import SimulationConfig
from .evolution.reproduction import mutate_genome
from .physics.laws import ClimateLaw, CoupledYieldLaw, RadiationLaw, MultiForcingLaw
from .physics.matter import MatterLaw


@dataclass(slots=True)
class ResourcePatch:
    x: float
    y: float
    richness: float
    capacity: float


@dataclass(slots=True)
class WorldObstacle:
    x: float
    y: float
    radius: float


@dataclass(slots=True)
class EnvironmentalPulse:
    x: float
    y: float
    radius: float
    amplitude: float
    remaining: int


@dataclass(slots=True)
class MatterObject:
    id: int
    x: float
    y: float
    mass: float
    material: tuple[float, float, float]
    holder_id: int | None = None


@dataclass(slots=True)
class BroadcastSignal:
    x: float
    y: float
    payload: tuple[float, ...]
    radius: float
    source_id: int


@dataclass(slots=True)
class CulturalMark:
    x: float
    y: float
    payload: tuple[float, ...]
    strength: float
    decay: float
    source_id: int


class World:
    def __init__(self, config: SimulationConfig | None = None, seed: int = 0):
        self.config = config or SimulationConfig()
        self.rng = np.random.default_rng(seed)
        # Separate observer/intervention RNG: placebo communication must not perturb
        # the stochastic trajectory of physics, reproduction, or agent exploration.
        self.intervention_rng = np.random.default_rng(seed + 10_000_019)
        self.seed = seed
        # Observer-only cache: exact persistent marks visible to each agent at the
        # current observation. Never exposed to controllers or learning.
        self._observer_visible_mark_sources = {}
        # Optional independent population RNG enables causal population/world
        # transplant experiments without changing any agent rule or reward.
        self.agent_rng = self.rng if self.config.agent_seed is None else np.random.default_rng(int(self.config.agent_seed))
        self.time = 0
        self.births = 0
        self.deaths = 0
        self.next_agent_id = 0
        self.signals: list[BroadcastSignal] = []
        self._next_signals: list[BroadcastSignal] = []
        self.marks: list[CulturalMark] = []
        self.communication_log: list[dict] = []
        self.object_log: list[dict] = []
        self.harvest_log: list[dict] = []
        self.social_log: list[dict] = []
        self.visibility_log: list[dict] = []
        self.pulses: list[EnvironmentalPulse] = []

        # A compact hidden physics whose *number of latent causes is itself variable*.
        # Agents are never told how many drivers exist.
        n_sources = int(self.rng.integers(2, 5))
        low = np.linspace(45.0, 115.0, n_sources)
        high = np.linspace(90.0, 280.0, n_sources)
        periods = tuple(float(v) for v in self.rng.uniform(low, high))
        self.forcing_law = MultiForcingLaw(
            amplitudes=tuple(float(v) for v in self.rng.uniform(0.35, 1.05, size=n_sources)),
            periods=periods,
            phases=tuple(float(v) for v in self.rng.uniform(0.0, 2.0 * math.pi, size=n_sources)),
            coupling=float(self.rng.uniform(-0.14, 0.14)),
        )
        self.hidden_source_count = n_sources
        self.climate = ClimateLaw(
            mean=float(self.rng.uniform(9.0, 17.0)),
            gradient_x=float(self.rng.uniform(-0.20, 0.20)),
            gradient_y=float(self.rng.uniform(-0.12, 0.12)),
            forcing_scale=float(self.rng.uniform(3.0, 6.0)),
        )
        self.radiation_law = RadiationLaw(
            baseline=float(self.rng.uniform(0.9, 1.6)),
            gradient_y=float(self.rng.uniform(-0.025, 0.025)),
            forcing_scale=float(self.rng.uniform(0.25, 0.65)),
            thermal_coupling=float(self.rng.uniform(-0.35, 0.35)),
            phase_shift=float(self.rng.uniform(0.0, 2.0 * math.pi)),
        )
        self.yield_law = CoupledYieldLaw(
            optimum_temperature=float(self.rng.uniform(8.0, 22.0)),
            temperature_width=float(self.rng.uniform(4.0, 8.0)),
            optimum_radiation=float(self.rng.uniform(0.5, 2.0)),
            radiation_width=float(self.rng.uniform(0.35, 0.75)),
            interaction=float(self.rng.uniform(-0.7, 0.7)),
        )
        self.matter_law = MatterLaw(
            material_weights=tuple(float(v) for v in self.rng.uniform(-1.15, 1.15, size=3)),
            pair_weights=tuple(float(v) for v in self.rng.uniform(-1.0, 1.0, size=3)),
            field_scale=float(self.rng.uniform(0.14, 0.32)),
            pair_scale=float(self.rng.uniform(0.32, 0.82)),
            interaction_length=float(self.rng.uniform(0.65, 1.5)),
            influence_radius=float(self.rng.uniform(2.2, 3.8)),
        )

        self.obstacles = [self._new_obstacle() for _ in range(self.config.obstacle_count)]
        self.resources = [self._new_patch() for _ in range(self.config.resource_patches)]
        self.objects = [self._new_object(i) for i in range(self.config.object_count)]
        self.initial_object_positions = {o.id: (o.x, o.y) for o in self.objects}
        self.agents = []
        # No science-specific agent is instantiated. Cognitive diversity concerns
        # only generic control architectures.
        # Publication experiments can use a single generic neural substrate.
        # Hand-written architectures remain available only as diagnostic baselines.
        agent_types = [RecurrentAgent] if self.config.generic_population_only else [RandomAgent, ReactiveAgent, ModelBasedAgent, PlannerAgent, RecurrentAgent]
        for i in range(self.config.initial_agents):
            cls = agent_types[i % len(agent_types)]
            self._spawn(cls, None, Genome(
                speed=float(self.agent_rng.uniform(0.8, 1.2)),
                exploration=float(self.agent_rng.uniform(0.12, 0.42)),
                curiosity=0.0,
                memory=float(self.agent_rng.uniform(0.0, 1.0)),
                abstraction=float(self.agent_rng.uniform(0.45, 1.8)),
                signal_range=float(self.agent_rng.uniform(0.0, 1.0)),
                inscription_persistence=float(self.agent_rng.uniform(0.0, 1.0)),
                social_attention=float(self.agent_rng.uniform(0.0, 1.0)),
                plasticity=float(self.agent_rng.uniform(0.0, 0.8)),
            ))

    def _new_obstacle(self) -> WorldObstacle:
        return WorldObstacle(
            x=float(self.rng.uniform(0, self.config.width)),
            y=float(self.rng.uniform(0, self.config.height)),
            radius=float(self.rng.uniform(self.config.obstacle_radius_min, self.config.obstacle_radius_max)),
        )

    def _new_patch(self) -> ResourcePatch:
        capacity = float(self.rng.uniform(2.0, self.config.max_patch_richness))
        return ResourcePatch(
            x=float(self.rng.uniform(0, self.config.width)),
            y=float(self.rng.uniform(0, self.config.height)),
            richness=capacity,
            capacity=capacity,
        )

    def _new_object(self, object_id: int) -> MatterObject:
        # Material coordinates are observable continuous properties. They are not
        # categorical item types and do not imply a predefined use.
        return MatterObject(
            id=object_id,
            x=float(self.rng.uniform(0, self.config.width)),
            y=float(self.rng.uniform(0, self.config.height)),
            mass=float(self.rng.uniform(0.45, 2.6)),
            material=tuple(float(v) for v in self.rng.uniform(-1.0, 1.0, size=3)),
        )

    def _spawn(self, cls, parent, genome: Genome):
        if parent is None:
            x = float(self.agent_rng.uniform(0, self.config.width))
            y = float(self.agent_rng.uniform(0, self.config.height))
            energy = self.config.initial_energy
        else:
            x = min(self.config.width, max(0.0, parent.x + float(self.agent_rng.normal(0, 0.35))))
            y = min(self.config.height, max(0.0, parent.y + float(self.agent_rng.normal(0, 0.35))))
            energy = self.config.reproduction_cost * 0.75
        a = cls(self.next_agent_id, x, y, energy, genome)
        self.next_agent_id += 1
        if parent is not None:
            a.inherit_from(parent, self.agent_rng, self.config.mutation_sigma)
            a.parent_id = parent.id
            a.generation = parent.generation + 1
            parent.children += 1
            self.births += 1
        self.agents.append(a)
        return a

    def forcing(self, t: int | None = None) -> float:
        return self.forcing_law.value(self.time if t is None else t)

    def temperature(self, x: float, y: float) -> float:
        return self.climate.temperature(x, y, self.forcing())

    def radiation(self, x: float, y: float) -> float:
        f = self.forcing()
        temp = self.climate.temperature(x, y, f)
        return self.radiation_law.radiation(x, y, f, temp)

    def _pulse_effect(self, x: float, y: float) -> float:
        effect = 0.0
        for p in self.pulses:
            d = math.hypot(x - p.x, y - p.y)
            if d < p.radius:
                q = 1.0 - d / p.radius
                effect += p.amplitude * q * q
        return effect

    def physical_state(self, x: float, y: float) -> tuple[float, float]:
        f = self.forcing()
        temp = self.climate.temperature(x, y, f)
        rad = self.radiation_law.radiation(x, y, f, temp) + self._pulse_effect(x, y)
        return temp, rad

    @staticmethod
    def _segment_distance_sq(px: float, py: float, ax: float, ay: float, bx: float, by: float) -> float:
        """Squared point-to-segment distance.

        This is mathematically equivalent to the former Euclidean-distance
        helper for all line-of-sight comparisons, but avoids square roots in
        the innermost visibility loop.  It changes no simulation rule.
        """
        abx, aby = bx - ax, by - ay
        denom = abx * abx + aby * aby
        if denom <= 1e-12:
            dx, dy = px - ax, py - ay
            return dx * dx + dy * dy
        t = ((px - ax) * abx + (py - ay) * aby) / denom
        t = min(1.0, max(0.0, t))
        qx, qy = ax + t * abx, ay + t * aby
        dx, dy = px - qx, py - qy
        return dx * dx + dy * dy

    def line_of_sight(self, ax: float, ay: float, bx: float, by: float) -> bool:
        if not self.config.occlusion_enabled:
            return True
        # Exact geometry is unchanged, but reject obstacles whose expanded
        # bounding boxes do not intersect the sight segment before evaluating
        # point-to-segment distance. This is a pure engine optimization: no
        # world law, perception radius or agent information changes.
        minx, maxx = (ax, bx) if ax <= bx else (bx, ax)
        miny, maxy = (ay, by) if ay <= by else (by, ay)
        frac = min(1.0, max(0.0, float(self.config.active_obstacle_fraction)))
        n_active = int(round(frac * len(self.obstacles)))
        for o in self.obstacles[:n_active]:
            r = o.radius
            if o.x < minx - r or o.x > maxx + r or o.y < miny - r or o.y > maxy + r:
                continue
            if self._segment_distance_sq(o.x, o.y, ax, ay, bx, by) < r * r:
                # Do not let an obstacle containing the observer block everything.
                if (ax - o.x) ** 2 + (ay - o.y) ** 2 > (r * 0.95) ** 2:
                    return False
        return True

    def nearby(self, agent):
        r2 = self.config.observation_radius ** 2
        out = []
        for patch in self.resources:
            d2 = (patch.x - agent.x) ** 2 + (patch.y - agent.y) ** 2
            if d2 <= r2 and patch.richness > 0.01 and self.line_of_sight(agent.x, agent.y, patch.x, patch.y):
                out.append((patch.x - agent.x, patch.y - agent.y, patch.richness))
        out.sort(key=lambda q: q[0] * q[0] + q[1] * q[1])
        return out

    def nearby_objects(self, agent):
        r2 = self.config.object_observation_radius ** 2
        out = []
        for obj in self.objects:
            if obj.holder_id is not None:
                continue
            dx, dy = obj.x - agent.x, obj.y - agent.y
            d2 = dx * dx + dy * dy
            if d2 <= r2 and self.line_of_sight(agent.x, agent.y, obj.x, obj.y):
                out.append((obj.id, dx, dy, obj.mass, obj.material))
        out.sort(key=lambda q: q[1] * q[1] + q[2] * q[2])
        return out

    def held_object_observation(self, agent):
        if agent.held_object_id is None:
            return None
        obj = next((o for o in self.objects if o.id == agent.held_object_id), None)
        if obj is None:
            return None
        return (obj.mass, obj.material)

    def nearby_signals(self, agent):
        if not self.config.communication_enabled:
            return []
        out = []
        for s in self.signals:
            if s.source_id == agent.id:
                continue
            dx, dy = s.x - agent.x, s.y - agent.y
            if dx * dx + dy * dy <= s.radius * s.radius and self.line_of_sight(agent.x, agent.y, s.x, s.y):
                out.append((dx, dy, s.payload))
        return out

    def nearby_marks(self, agent):
        if not self.config.marks_enabled:
            self._observer_visible_mark_sources[agent.id] = ()
            return []
        r2 = self.config.mark_radius ** 2
        out = []
        sources = []
        for m in self.marks:
            dx, dy = m.x - agent.x, m.y - agent.y
            if dx * dx + dy * dy <= r2 and self.line_of_sight(agent.x, agent.y, m.x, m.y):
                out.append((dx, dy, m.payload, m.strength))
                sources.append(int(m.source_id))
        self._observer_visible_mark_sources[agent.id] = tuple(sources)
        return out

    def nearby_agents(self, agent):
        r2 = self.config.social_observation_radius ** 2
        out = []
        for other in self.agents:
            if other.id == agent.id or not other.alive:
                continue
            dx, dy = other.x - agent.x, other.y - agent.y
            if dx * dx + dy * dy <= r2 and self.line_of_sight(agent.x, agent.y, other.x, other.y):
                vx = other.x - other.prev_x
                vy = other.y - other.prev_y
                out.append((dx, dy, vx, vy))
        out.sort(key=lambda q: q[0] * q[0] + q[1] * q[1])
        return out

    def observe(self, a) -> Observation:
        temp, rad = self.physical_state(a.x, a.y)
        visible_resources = self.nearby(a)
        visible_agents = self.nearby_agents(a)
        self.visibility_log.append({"time": self.time, "agent_id": a.id, "generation": a.generation, "resources": len(visible_resources), "agents": len(visible_agents), "temperature": temp, "radiation": rad})
        return Observation(
            time=self.time, x=a.x, y=a.y, energy=a.energy,
            temperature=temp, radiation=rad, nearby_resources=visible_resources,
            last_action=a.last_action, last_yield=a.last_yield,
            nearby_signals=self.nearby_signals(a), nearby_marks=self.nearby_marks(a),
            nearby_objects=self.nearby_objects(a), held_object=self.held_object_observation(a),
            nearby_agents=visible_agents,
        )

    def _nearest_harvestable_patch(self, a):
        best = None
        best_d2 = 1.6 ** 2
        for p in self.resources:
            d2 = (p.x-a.x)**2 + (p.y-a.y)**2
            if p.richness > 0.01 and d2 <= best_d2:
                best, best_d2 = p, d2
        return best

    def matter_multiplier(self, x: float, y: float) -> float:
        temp, rad = self.physical_state(x, y)
        return self.matter_law.multiplier(x, y, temp, rad, self.objects)

    def _potential_yield(self, a) -> float:
        temp, rad = self.physical_state(a.x, a.y)
        base = self.yield_law.efficiency(temp, rad)
        return base * self.matter_law.multiplier(a.x, a.y, temp, rad, self.objects)

    def _pickup(self, a) -> bool:
        if a.held_object_id is not None:
            return False
        best = None
        best_d2 = self.config.pickup_radius ** 2
        for obj in self.objects:
            if obj.holder_id is not None:
                continue
            d2 = (obj.x - a.x) ** 2 + (obj.y - a.y) ** 2
            if d2 <= best_d2:
                best, best_d2 = obj, d2
        if best is None:
            return False
        if self.config.object_manipulation_enabled:
            best.holder_id = a.id
            a.held_object_id = best.id
            best.x, best.y = a.x, a.y
            a.objects_picked += 1
            return True
        return False

    def _drop(self, a) -> bool:
        if a.held_object_id is None:
            return False
        obj = next((o for o in self.objects if o.id == a.held_object_id), None)
        if obj is None:
            a.held_object_id = None
            return False
        if self.config.object_manipulation_enabled:
            obj.holder_id = None
            obj.x, obj.y = a.x, a.y
            a.held_object_id = None
            a.objects_dropped += 1
            return True
        return False

    def _apply_action(self, a, action) -> float:
        cfg = self.config
        reward = -cfg.basal_metabolism
        a.energy -= cfg.basal_metabolism
        a.last_yield = None

        if action.kind == ActionKind.MOVE:
            mag = math.hypot(action.dx, action.dy) or 1.0
            step = a.genome.speed
            a.x = min(cfg.width, max(0.0, a.x + step * action.dx / mag))
            a.y = min(cfg.height, max(0.0, a.y + step * action.dy / mag))
            cost = cfg.move_cost * step
            if a.held_object_id is not None:
                obj = next((o for o in self.objects if o.id == a.held_object_id), None)
                if obj is not None:
                    cost += cfg.carry_cost_per_mass * obj.mass * step
                    if cfg.object_manipulation_enabled:
                        obj.x, obj.y = a.x, a.y
            a.energy -= cost
            reward -= cost
        elif action.kind == ActionKind.HARVEST:
            a.energy -= cfg.harvest_cost
            reward -= cfg.harvest_cost
            patch = self._nearest_harvestable_patch(a)
            if patch is not None:
                temp, rad = self.physical_state(a.x, a.y)
                base_efficiency = self.yield_law.efficiency(temp, rad)
                matter_multiplier = self.matter_law.multiplier(a.x, a.y, temp, rad, self.objects)
                efficiency = base_efficiency * matter_multiplier
                amount = min(patch.richness, 1.3 * efficiency)
                patch.richness -= amount
                a.energy += amount
                a.total_harvest += amount
                a.last_yield = amount
                reward += amount
                self.harvest_log.append({
                    "time": self.time, "agent_id": a.id, "generation": a.generation,
                    "amount": amount, "base_efficiency": base_efficiency,
                    "matter_multiplier": matter_multiplier,
                    "held_object": a.held_object_id is not None,
                })
            else:
                a.last_yield = 0.0
        elif action.kind == ActionKind.PROBE:
            a.probes += 1
            a.energy -= cfg.probe_cost
            reward -= cfg.probe_cost
            a.last_yield = self._potential_yield(a)
        elif action.kind == ActionKind.BROADCAST:
            a.energy -= cfg.signal_cost
            reward -= cfg.signal_cost
            radius = cfg.signal_radius_min + a.genome.signal_range * (cfg.signal_radius_max - cfg.signal_radius_min)
            payload = tuple(float(v) for v in action.payload[:cfg.signal_channels])
            if cfg.communication_enabled:
                self._next_signals.append(BroadcastSignal(a.x, a.y, payload, radius, a.id))
            temp, rad = self.physical_state(a.x, a.y)
            near = self.nearby(a)
            self.communication_log.append({
                "time": self.time, "type": "broadcast", "source_id": a.id,
                "generation": a.generation, "payload": payload, "temperature": temp,
                "radiation": rad, "resource_richness": near[0][2] if near else 0.0,
            })
        elif action.kind == ActionKind.INSCRIBE:
            a.energy -= cfg.inscription_cost
            reward -= cfg.inscription_cost
            payload = tuple(float(v) for v in action.payload[:cfg.signal_channels])
            persistence = a.genome.inscription_persistence
            decay = cfg.mark_decay_max - persistence * (cfg.mark_decay_max - cfg.mark_decay_min)
            if cfg.marks_enabled:
                self.marks.append(CulturalMark(a.x, a.y, payload, 1.0, decay, a.id))
            temp, rad = self.physical_state(a.x, a.y)
            near = self.nearby(a)
            self.communication_log.append({
                "time": self.time, "type": "inscription", "source_id": a.id,
                "generation": a.generation, "payload": payload, "temperature": temp,
                "radiation": rad, "resource_richness": near[0][2] if near else 0.0,
            })
            if len(self.marks) > cfg.max_marks:
                self.marks = self.marks[-cfg.max_marks:]
        elif action.kind == ActionKind.PICKUP:
            a.energy -= cfg.manipulation_cost
            reward -= cfg.manipulation_cost
            success = self._pickup(a)
            self.object_log.append({"time": self.time, "type": "pickup", "agent_id": a.id, "generation": a.generation, "success": success})
        elif action.kind == ActionKind.DROP:
            a.energy -= cfg.manipulation_cost
            reward -= cfg.manipulation_cost
            success = self._drop(a)
            self.object_log.append({"time": self.time, "type": "drop", "agent_id": a.id, "generation": a.generation, "success": success})
        elif action.kind == ActionKind.REST:
            pass

        a.last_action = action.kind.value
        a.action_counts[action.kind.value] = a.action_counts.get(action.kind.value, 0) + 1
        return reward

    def step(self):
        self._next_signals = []
        current = [a for a in self.agents if a.alive]
        for a in current:
            a.prev_x, a.prev_y = a.x, a.y
            obs = self.observe(a)
            action = a.act(obs, self.agent_rng)
            reward = self._apply_action(a, action)
            if getattr(a, "kind", "") == "recurrent":
                received = obs.nearby_signals
                if received:
                    payloads = np.asarray([q[2] for q in received], dtype=float)
                    mean_payload = tuple(float(v) for v in np.mean(payloads, axis=0))
                else:
                    mean_payload = ()
                marks = obs.nearby_marks
                if marks:
                    mark_payloads = np.asarray([q[2] for q in marks], dtype=float)
                    mean_mark_payload = tuple(float(v) for v in np.mean(mark_payloads, axis=0))
                    # Observer-only attribution cached while visibility was computed.
                    mark_sources = self._observer_visible_mark_sources.get(a.id, ())
                else:
                    mean_mark_payload = ()
                    mark_sources = ()
                self.social_log.append({
                    "time": self.time, "agent_id": a.id, "generation": a.generation,
                    "received_count": len(received), "mean_payload": mean_payload,
                    "received_mark_count": len(marks), "mean_mark_payload": mean_mark_payload,
                    "mark_source_ids": mark_sources,
                    "conspecifics": len(obs.nearby_agents), "action": action.kind.value,
                    "dx": float(action.dx), "dy": float(action.dy), "reward": float(reward),
                })
            a.learn(obs, action, reward)
            a.age += 1
            if a.energy <= 0:
                if a.held_object_id is not None:
                    obj = next((o for o in self.objects if o.id == a.held_object_id), None)
                    if obj is not None:
                        obj.holder_id = None
                        obj.x, obj.y = a.x, a.y
                    a.held_object_id = None
                a.alive = False
                self.deaths += 1

        living_count = sum(a.alive for a in self.agents)
        for parent in list(self.agents):
            if not parent.alive or living_count >= self.config.max_population:
                continue
            threshold = self.config.reproduction_threshold * parent.genome.reproduction_bias
            if parent.energy >= threshold:
                parent.energy -= self.config.reproduction_cost
                genome = mutate_genome(parent.genome, self.agent_rng, self.config.mutation_sigma)
                self._spawn(type(parent), parent, genome)
                living_count += 1

        for p in self.resources:
            pulse = self._pulse_effect(p.x, p.y)
            growth = self.config.resource_regrowth * max(0.1, 1.0 + 0.45 * pulse)
            p.richness = min(p.capacity, p.richness + growth)

        # Local transient perturbations are world dynamics, not agent tasks.
        if self.rng.random() < self.config.pulse_spawn_rate:
            self.pulses.append(EnvironmentalPulse(
                x=float(self.rng.uniform(0, self.config.width)),
                y=float(self.rng.uniform(0, self.config.height)),
                radius=float(self.rng.uniform(self.config.pulse_radius_min, self.config.pulse_radius_max)),
                amplitude=float(self.rng.uniform(-self.config.pulse_amplitude_max, self.config.pulse_amplitude_max)),
                remaining=int(self.rng.integers(self.config.pulse_lifetime_min, self.config.pulse_lifetime_max + 1)),
            ))
        for pulse in self.pulses:
            pulse.remaining -= 1
        self.pulses = [p for p in self.pulses if p.remaining > 0]

        # Communication has no intrinsic value. Broadcasts live for one step; public
        # traces decay mechanically regardless of whether anyone reads them.
        if self.config.communication_scramble and len(self._next_signals) > 1:
            payloads = [s.payload for s in self._next_signals]
            perm = self.intervention_rng.permutation(len(payloads))
            self.signals = [
                BroadcastSignal(s.x, s.y, payloads[int(j)], s.radius, s.source_id)
                for s, j in zip(self._next_signals, perm)
            ]
        else:
            self.signals = self._next_signals
        for m in self.marks:
            m.strength -= m.decay
        self.marks = [m for m in self.marks if m.strength > 0.0]

        self.time += 1

    def run(self, steps: int):
        for _ in range(steps):
            if not any(a.alive for a in self.agents):
                break
            self.step()
        return self
