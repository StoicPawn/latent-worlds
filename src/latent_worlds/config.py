from dataclasses import dataclass


@dataclass(slots=True)
class SimulationConfig:
    width: float = 30.0
    height: float = 30.0
    initial_agents: int = 24
    resource_patches: int = 45
    initial_energy: float = 18.0
    basal_metabolism: float = 0.045
    move_cost: float = 0.035
    probe_cost: float = 0.10
    harvest_cost: float = 0.03
    reproduction_threshold: float = 23.0
    reproduction_cost: float = 10.0
    resource_regrowth: float = 0.04
    max_patch_richness: float = 8.0
    observation_radius: float = 4.5
    mutation_sigma: float = 0.10
    max_population: int = 250
    signal_channels: int = 3
    signal_cost: float = 0.055
    inscription_cost: float = 0.11
    signal_radius_min: float = 2.0
    signal_radius_max: float = 7.0
    mark_radius: float = 4.5
    mark_decay_min: float = 0.002
    mark_decay_max: float = 0.02
    max_marks: int = 600
    communication_enabled: bool = True
    communication_scramble: bool = False
    marks_enabled: bool = True
    object_count: int = 36
    object_observation_radius: float = 4.5
    pickup_radius: float = 1.35
    manipulation_cost: float = 0.055
    carry_cost_per_mass: float = 0.010
    object_manipulation_enabled: bool = True
    social_observation_radius: float = 5.5
    plasticity_rate: float = 0.004
    plasticity_decay: float = 0.002
    obstacle_count: int = 18
    active_obstacle_fraction: float = 1.0
    obstacle_radius_min: float = 0.7
    obstacle_radius_max: float = 2.0
    pulse_spawn_rate: float = 0.018
    pulse_radius_min: float = 2.0
    pulse_radius_max: float = 5.0
    pulse_lifetime_min: int = 25
    pulse_lifetime_max: int = 90
    pulse_amplitude_max: float = 0.65
    occlusion_enabled: bool = True
    generic_population_only: bool = False
    agent_seed: int | None = None

