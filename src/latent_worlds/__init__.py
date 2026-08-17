"""Latent Worlds: artificial universes with discoverable hidden laws."""

from .config import SimulationConfig
from .world import World

__all__ = ["SimulationConfig", "World"]

from .semantic_autopsy import candidate_semantic_autopsy, counterfactual_content_assay, causal_codebook_assay, directional_substitution_assay

__version__ = "3.2.0"
