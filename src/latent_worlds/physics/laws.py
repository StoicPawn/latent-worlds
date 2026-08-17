from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass(frozen=True, slots=True)
class MultiForcingLaw:
    """Quasi-periodic forcing produced by three latent oscillators.

    The source periods, phases and amplitudes are ground-truth world
    parameters. Agents never receive them directly. The construction is a small
    artificial analogue of a world driven by several interacting celestial
    cycles: simple equations can generate an environment that is hard to infer
    from short trajectories.
    """

    amplitudes: tuple[float, ...]
    periods: tuple[float, ...]
    phases: tuple[float, ...]
    coupling: float

    def components(self, t: int | float) -> tuple[float, ...]:
        return tuple(
            a * math.sin(2.0 * math.pi * float(t) / p + ph)
            for a, p, ph in zip(self.amplitudes, self.periods, self.phases)
        )

    def value(self, t: int | float) -> float:
        components = self.components(t)
        total = sum(components)
        # Pairwise nonlinear resonances create apparently irregular regimes while
        # keeping an exactly known generator for evaluator-side analysis.
        pairwise = 0.0
        for i in range(len(components)):
            for j in range(i + 1, len(components)):
                pairwise += components[i] * components[j]
        return total + self.coupling * pairwise


@dataclass(frozen=True, slots=True)
class ClimateLaw:
    mean: float
    gradient_x: float
    gradient_y: float
    forcing_scale: float

    def temperature(self, x: float, y: float, forcing: float) -> float:
        return (
            self.mean
            + self.gradient_x * x
            + self.gradient_y * y
            + self.forcing_scale * forcing
        )


@dataclass(frozen=True, slots=True)
class RadiationLaw:
    baseline: float
    gradient_y: float
    forcing_scale: float
    thermal_coupling: float
    phase_shift: float

    def radiation(self, x: float, y: float, forcing: float, temperature: float) -> float:
        # Radiation is coupled to both the latent forcing and the temperature,
        # so observing one field alone does not identify the full world state.
        thermal = self.thermal_coupling * math.tanh((temperature - 12.0) / 8.0)
        spatial = self.gradient_y * y + 0.08 * math.sin(0.22 * x + self.phase_shift)
        return self.baseline + self.forcing_scale * forcing + thermal + spatial


@dataclass(frozen=True, slots=True)
class CoupledYieldLaw:
    """Hidden resource law depending on two observable physical variables.

    The law has a temperature optimum, a radiation optimum and a genuine
    interaction term. A one-dimensional policy can therefore perform well in
    some regions while still misunderstanding the causal structure.
    """

    optimum_temperature: float
    temperature_width: float
    optimum_radiation: float
    radiation_width: float
    interaction: float

    def efficiency(self, temperature: float, radiation: float) -> float:
        zt = (temperature - self.optimum_temperature) / self.temperature_width
        zr = (radiation - self.optimum_radiation) / self.radiation_width
        exponent = -(zt * zt + zr * zr) + self.interaction * zt * zr
        # Clamp only for numerical safety; the sampled interaction keeps the
        # quadratic form well behaved in normal operation.
        return float(min(1.5, max(0.0, math.exp(max(-30.0, min(1.0, exponent))))))


# Backward-compatible alias for old experiments.
TripleForcingLaw = MultiForcingLaw
