from __future__ import annotations

from dataclasses import replace

from latent_worlds.agents.base import Genome


def mutate_genome(parent: Genome, rng, sigma: float) -> Genome:
    child = replace(parent)
    child.speed = max(0.35, min(2.0, parent.speed + rng.normal(0.0, sigma)))
    child.exploration = max(0.0, min(1.0, parent.exploration + rng.normal(0.0, sigma)))
    child.curiosity = max(0.0, min(1.0, parent.curiosity + rng.normal(0.0, sigma)))
    child.reproduction_bias = max(0.5, min(1.5, parent.reproduction_bias + rng.normal(0.0, sigma)))
    child.memory = max(0.0, min(1.0, parent.memory + rng.normal(0.0, sigma)))
    child.abstraction = max(0.25, min(2.5, parent.abstraction + rng.normal(0.0, sigma)))
    child.signal_range = max(0.0, min(1.0, parent.signal_range + rng.normal(0.0, sigma)))
    child.inscription_persistence = max(0.0, min(1.0, parent.inscription_persistence + rng.normal(0.0, sigma)))
    child.social_attention = max(0.0, min(1.0, parent.social_attention + rng.normal(0.0, sigma)))
    child.plasticity = max(0.0, min(1.0, parent.plasticity + rng.normal(0.0, sigma)))
    return child
