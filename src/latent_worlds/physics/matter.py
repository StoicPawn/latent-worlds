from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable, Protocol


class MatterLike(Protocol):
    x: float
    y: float
    material: tuple[float, float, float]


@dataclass(frozen=True, slots=True)
class MatterLaw:
    """Continuous law coupling matter arrangements to ambient energy conversion.

    There are no recipes and no named devices. Every object's three observable
    material coordinates enter the same law. Spatial arrangement matters because
    nearby pairs create an additional nonlinear interaction term. The simulator
    can therefore contain useful and harmful configurations without enumerating
    technologies.
    """

    material_weights: tuple[float, float, float]
    pair_weights: tuple[float, float, float]
    field_scale: float
    pair_scale: float
    interaction_length: float
    influence_radius: float

    def activation(self, material: tuple[float, float, float], temperature: float, radiation: float) -> float:
        # Ambient state is deliberately entangled with material properties.
        t = math.tanh((temperature - 14.0) / 8.0)
        r = math.tanh((radiation - 1.2) / 0.8)
        m0, m1, m2 = material
        w0, w1, w2 = self.material_weights
        return math.tanh(w0 * m0 * t + w1 * m1 * r + w2 * m2 * t * r)

    def multiplier(self, x: float, y: float, temperature: float, radiation: float, objects: Iterable[MatterLike]) -> float:
        nearby = []
        for obj in objects:
            dx, dy = obj.x - x, obj.y - y
            d = math.hypot(dx, dy)
            if d <= self.influence_radius:
                nearby.append((obj, d, self.activation(obj.material, temperature, radiation)))

        field = 0.0
        for _, d, a in nearby:
            field += self.field_scale * a * math.exp(-d / max(self.interaction_length, 1e-6))

        pair = 0.0
        for i in range(len(nearby)):
            oi, _, ai = nearby[i]
            for j in range(i + 1, len(nearby)):
                oj, _, aj = nearby[j]
                dij = math.hypot(oi.x - oj.x, oi.y - oj.y)
                if dij > self.influence_radius:
                    continue
                # A continuous bilinear material interaction. Some arrangements
                # amplify ambient conversion and others suppress it.
                c0, c1, c2 = self.pair_weights
                mi, mj = oi.material, oj.material
                compatibility = c0 * mi[0] * mj[1] + c1 * mi[1] * mj[2] + c2 * mi[2] * mj[0]
                pair += self.pair_scale * compatibility * ai * aj * math.exp(-dij / max(self.interaction_length, 1e-6))

        # Smooth bounded transduction. 1.0 means matter has no net effect.
        return float(max(0.20, min(2.75, math.exp(max(-1.6, min(1.0, field + pair))))))
