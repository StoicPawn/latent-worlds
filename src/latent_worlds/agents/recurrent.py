from __future__ import annotations

import math
import numpy as np

from .base import Action, ActionKind, BaseAgent, Observation


class RecurrentAgent(BaseAgent):
    """Generic evolvable recurrent controller with no epistemic/social objective.

    Inputs contain bodily/ecological state, anonymous social traces and raw
    material observations. Outputs are primitive motor/manipulation actions.
    Nothing in the controller represents 'tool', 'technology', 'science',
    'message', or a target discovery.
    """

    kind = "recurrent"
    HIDDEN = 12

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hidden = np.zeros(self.HIDDEN, dtype=float)
        self._initialized = False
        self.W_in = None
        self.W_rec = None
        self.W_out = None
        self.emissions = 0
        self.inscriptions = 0
        self._eligibility = None
        self._eligibility_in = None
        self._eligibility_rec = None
        self._last_aug = None
        self._last_row = None
        self._last_x = None
        self._last_hidden_prev = None
        self._state_update_ready = False
        self.state_plasticity_enabled = False
        self._reward_baseline = 0.0

    @staticmethod
    def _aggregate_vectors(items, channels: int) -> np.ndarray:
        if not items:
            return np.zeros(channels, dtype=float)
        vals = []
        for q in items:
            payload = q[2]
            v = np.zeros(channels, dtype=float)
            n = min(channels, len(payload))
            if n:
                v[:n] = payload[:n]
            d = math.hypot(q[0], q[1])
            vals.append(v / (1.0 + d))
        return np.mean(vals, axis=0)

    def _aggregate_social(self, obs: Observation) -> np.ndarray:
        if not obs.nearby_agents:
            return np.zeros(4, dtype=float)
        vals = []
        for dx, dy, vx, vy in obs.nearby_agents:
            d = math.hypot(dx, dy)
            vals.append(np.asarray([dx / 5.0, dy / 5.0, vx, vy], dtype=float) / (1.0 + d))
        # social_attention is not a social objective: it is simply a heritable
        # gain on conspecific sensory input, analogous to any other sensory gain.
        return self.genome.social_attention * np.mean(vals, axis=0)

    def _features(self, obs: Observation, channels: int) -> np.ndarray:
        nearest = obs.nearby_resources[0] if obs.nearby_resources else (0.0, 0.0, 0.0)
        if obs.nearby_objects:
            _, odx, ody, mass, material = obs.nearby_objects[0]
            obj = np.asarray([odx / 5.0, ody / 5.0, mass / 3.0, *material], dtype=float)
        else:
            obj = np.zeros(6, dtype=float)
        if obs.held_object is not None:
            mass, material = obs.held_object
            held = np.asarray([1.0, mass / 3.0, *material], dtype=float)
        else:
            held = np.zeros(5, dtype=float)

        social = self._aggregate_social(obs)
        sig = self._aggregate_vectors(obs.nearby_signals, channels)
        marks = self._aggregate_vectors(obs.nearby_marks, channels)
        base = np.asarray([
            obs.energy / 25.0,
            obs.temperature / 20.0,
            obs.radiation,
            nearest[0] / 5.0,
            nearest[1] / 5.0,
            nearest[2] / 8.0,
            math.sin(0.019 * obs.time),
            math.cos(0.019 * obs.time),
        ], dtype=float)
        if obs.context_features_enabled:
            context = np.asarray([
                obs.x / max(obs.world_width, 1e-9),
                obs.y / max(obs.world_height, 1e-9),
                0.0 if obs.last_yield is None else float(obs.last_yield) / 2.0,
            ], dtype=float)
        else:
            context = np.empty(0, dtype=float)
        # Anonymous social channels remain last; observer-side metrics can locate
        # them without assuming the ecological feature count.
        return np.concatenate([base, context, obj, held, social, sig, marks])

    def _ensure(self, rng, input_dim: int, channels: int) -> None:
        if self._initialized:
            return
        self.W_in = rng.normal(0.0, 0.32, size=(self.HIDDEN, input_dim))
        self.W_rec = rng.normal(0.0, 0.16, size=(self.HIDDEN, self.HIDDEN))
        # outputs: move x/y + harvest/rest/broadcast/inscribe/pickup/drop + payload
        self.W_out = rng.normal(0.0, 0.28, size=(8 + channels, self.HIDDEN + 1))
        self._eligibility = np.zeros_like(self.W_out)
        self._eligibility_in = np.zeros_like(self.W_in)
        self._eligibility_rec = np.zeros_like(self.W_rec)
        self._initialized = True

    def inherit_from(self, parent: BaseAgent, rng, sigma: float) -> None:
        if not isinstance(parent, RecurrentAgent) or not parent._initialized:
            return
        self.W_in = parent.W_in + rng.normal(0.0, sigma * 0.45, size=parent.W_in.shape)
        self.W_rec = parent.W_rec + rng.normal(0.0, sigma * 0.30, size=parent.W_rec.shape)
        self.W_out = parent.W_out + rng.normal(0.0, sigma * 0.45, size=parent.W_out.shape)
        self._eligibility = np.zeros_like(self.W_out)
        self._eligibility_in = np.zeros_like(self.W_in)
        self._eligibility_rec = np.zeros_like(self.W_rec)
        self._initialized = True

    def act(self, obs: Observation, rng) -> Action:
        self._state_update_ready = False
        # Minimal homeostatic reflex only. It prevents arbitrary newborn brains
        # from disappearing before evolution can act, without creating a drive
        # toward objects, communication, prediction or discovery.
        if obs.energy < 4.5 and obs.nearby_resources:
            dx, dy, _ = obs.nearby_resources[0]
            if math.hypot(dx, dy) <= 1.6:
                return Action(ActionKind.HARVEST)
            return Action(ActionKind.MOVE, dx, dy)

        channels = 3
        x = self._features(obs, channels)
        self._ensure(rng, len(x), channels)
        hidden_prev = self.hidden.copy()
        self.hidden = np.tanh(self.W_in @ x + self.W_rec @ hidden_prev)
        aug = np.concatenate([self.hidden, [1.0]])
        z = self.W_out @ aug
        z[:8] += rng.normal(0.0, 0.10 + 0.20 * self.genome.exploration, size=8)
        choice = int(np.argmax(z[2:8]))
        move_strength = float(np.linalg.norm(z[:2]))
        payload = tuple(float(v) for v in np.tanh(z[8:8+channels]))

        if move_strength > float(np.max(z[2:8])):
            dx, dy = float(z[0]), float(z[1])
            if abs(dx) + abs(dy) < 1e-8:
                angle = rng.uniform(0.0, 2.0 * math.pi)
                dx, dy = math.cos(angle), math.sin(angle)
            row = 0 if abs(dx) >= abs(dy) else 1
            action = Action(ActionKind.MOVE, dx, dy)
        elif choice == 0:
            row, action = 2, Action(ActionKind.HARVEST)
        elif choice == 1:
            row, action = 3, Action(ActionKind.REST)
        elif choice == 2:
            self.emissions += 1
            row, action = 4, Action(ActionKind.BROADCAST, payload=payload)
        elif choice == 3:
            self.inscriptions += 1
            row, action = 5, Action(ActionKind.INSCRIBE, payload=payload)
        elif choice == 4:
            row, action = 6, Action(ActionKind.PICKUP)
        else:
            row, action = 7, Action(ActionKind.DROP)

        # Generic reward-modulated synaptic plasticity. The same mechanism acts
        # on movement, feeding, manipulation and signalling; it has no concept
        # of language, imitation, truth or communication success.
        self._last_aug = aug.copy()
        self._last_row = row
        if self._eligibility is None or self._eligibility.shape != self.W_out.shape:
            self._eligibility = np.zeros_like(self.W_out)
        self._eligibility *= 0.92
        self._eligibility[row] += aug

        self._last_x = x.copy()
        self._last_hidden_prev = hidden_prev
        if self.state_plasticity_enabled:
            if self._eligibility_in is None or self._eligibility_in.shape != self.W_in.shape:
                self._eligibility_in = np.zeros_like(self.W_in)
            if self._eligibility_rec is None or self._eligibility_rec.shape != self.W_rec.shape:
                self._eligibility_rec = np.zeros_like(self.W_rec)
            # One-step action-credit eligibility through the recurrent state.
            # This is generic reward-modulated plasticity: no prediction target,
            # hidden-law label or science-specific error signal is supplied.
            credit = self.W_out[row, :self.HIDDEN] * (1.0 - self.hidden ** 2)
            self._eligibility_in *= 0.92
            self._eligibility_rec *= 0.92
            self._eligibility_in += np.outer(credit, x)
            self._eligibility_rec += np.outer(credit, hidden_prev)
            self._state_update_ready = True
        return action

    def learn(self, obs: Observation, action: Action, reward: float) -> None:
        if not self._initialized or self._eligibility is None:
            return
        self._reward_baseline = 0.97 * self._reward_baseline + 0.03 * float(reward)
        advantage = float(np.clip(reward - self._reward_baseline, -2.0, 2.0))
        lr = 0.006 * float(self.genome.plasticity)
        if lr <= 0.0:
            return
        self.W_out += lr * advantage * self._eligibility
        self.W_out *= (1.0 - 0.0005 * self.genome.plasticity)
        np.clip(self.W_out, -4.0, 4.0, out=self.W_out)

        if (
            self.state_plasticity_enabled
            and self._state_update_ready
            and self._eligibility_in is not None
            and self._eligibility_rec is not None
        ):
            state_lr = 0.0015 * float(self.genome.plasticity)
            self.W_in += state_lr * advantage * self._eligibility_in
            self.W_rec += state_lr * advantage * self._eligibility_rec
            decay = 1.0 - 0.0002 * float(self.genome.plasticity)
            self.W_in *= decay
            self.W_rec *= decay
            np.clip(self.W_in, -3.0, 3.0, out=self.W_in)
            np.clip(self.W_rec, -3.0, 3.0, out=self.W_rec)
